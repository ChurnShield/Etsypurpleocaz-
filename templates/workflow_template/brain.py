# =============================================================================
# templates/workflow_template/brain.py
#
# SmallBrain — the per-workflow learning layer.
#
# What it does
# ------------
# After enough executions have accumulated, SmallBrain reads execution_logs
# and looks for two patterns:
#
#   1. Validators that fail too often  → proposal to review the validator
#      or the tool it checks.
#
#   2. Tools that run too slowly       → proposal to optimise or cache that tool.
#
# When it finds a pattern it saves a proposal row to the proposals table.
# A human must approve proposals before anything is changed (human-in-the-loop).
#
# What it does NOT do
# -------------------
# It never modifies workflows automatically.
# It only reads logs and writes proposals.
# =============================================================================

import sys
import os
import uuid
import json
from collections import defaultdict
from datetime import datetime

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_here = os.path.dirname(os.path.abspath(__file__))
# brain.py is at: templates/workflow_template/brain.py
#   dirname(_here) → templates/
#   dirname(dirname(_here)) → project root  ✅
_project_root = os.path.dirname(os.path.dirname(_here))

# _here (template dir) inserted first so 'from config import ...' finds the
# TEMPLATE config.py, not the root-level config.py.
if _here not in sys.path:
    sys.path.insert(0, _here)
if _project_root not in sys.path:
    sys.path.insert(1, _project_root)

from lib.common_tools.sqlite_client import SQLiteClient
from config import (
    PROPOSAL_THRESHOLD_RUNS,
    MIN_PATTERN_CONFIDENCE,
    SLOW_TOOL_THRESHOLD_MS,
)


class SmallBrain:
    """
    Analyses execution logs for ONE workflow and saves improvement proposals.

    Usage
    -----
    brain = SmallBrain(workflow_id="example_workflow", db=db)
    proposals = brain.analyze()
    print(f"Generated {len(proposals)} proposals")
    """

    def __init__(self, workflow_id: str, db):
        self.workflow_id = workflow_id
        self.db = db

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def analyze(self) -> list:
        """
        Run analysis and return a list of proposal dicts that were saved.

        Returns an empty list (and prints a message) if there are not yet
        enough runs to spot reliable patterns.
        """
        run_count = self._count_runs()

        if run_count < PROPOSAL_THRESHOLD_RUNS:
            print(
                f"SmallBrain: {run_count}/{PROPOSAL_THRESHOLD_RUNS} runs "
                f"collected for '{self.workflow_id}'. "
                f"Need {PROPOSAL_THRESHOLD_RUNS - run_count} more before analysis."
            )
            return []

        print(f"SmallBrain: Analysing {run_count} runs for '{self.workflow_id}'...")

        proposals = []
        proposals.extend(self._analyze_validators())
        proposals.extend(self._analyze_slow_tools())

        for proposal in proposals:
            self._save_proposal(proposal)

        print(f"SmallBrain: {len(proposals)} proposal(s) generated.")
        return proposals

    # -------------------------------------------------------------------------
    # Analysis helpers
    # -------------------------------------------------------------------------

    def _count_runs(self) -> int:
        """How many executions exist for this workflow?"""
        rows = (
            self.db.table("executions")
            .select("id")
            .eq("workflow_id", self.workflow_id)
            .execute()
        )
        return len(rows)

    def _analyze_validators(self) -> list:
        """
        Find validators whose failure rate meets or exceeds MIN_PATTERN_CONFIDENCE.

        How the maths works
        -------------------
        If MIN_PATTERN_CONFIDENCE = 0.7, a validator that fails 70 %+ of the
        time is flagged. That means the pattern is consistent enough to act on.
        """
        logs = (
            self.db.table("execution_logs")
            .select("validator_name, success")
            .eq("workflow_id", self.workflow_id)
            .eq("event_type", "validation")
            .execute()
        )

        if not logs:
            return []

        # Group results by validator name
        stats = defaultdict(lambda: {"total": 0, "passed": 0})
        for log in logs:
            name = log.get("validator_name")
            if not name:
                continue
            stats[name]["total"] += 1
            if log.get("success"):
                stats[name]["passed"] += 1

        proposals = []
        for validator_name, counts in stats.items():
            if counts["total"] == 0:
                continue

            pass_rate = counts["passed"] / counts["total"]
            fail_rate = 1.0 - pass_rate

            # Only propose when failure is consistent enough to trust the signal
            if fail_rate >= MIN_PATTERN_CONFIDENCE:
                proposals.append({
                    "proposal_type": "validator_improvement",
                    "title": f"High failure rate in {validator_name}",
                    "description": (
                        f"{validator_name} fails {fail_rate:.0%} of the time "
                        f"({counts['total'] - counts['passed']} of "
                        f"{counts['total']} checks). "
                        f"Consider relaxing validation rules or improving the "
                        f"upstream tool."
                    ),
                    "pattern_data": {
                        "validator_name": validator_name,
                        "pass_rate": pass_rate,
                        "fail_rate": fail_rate,
                        "total_checks": counts["total"],
                    },
                    "proposed_changes": {
                        "action": "review_validator",
                        "target": validator_name,
                        "suggestion": (
                            "Review validation thresholds or improve "
                            "the quality of the tool it checks."
                        ),
                    },
                })

        return proposals

    def _analyze_slow_tools(self) -> list:
        """
        Find tools whose calls exceed SLOW_TOOL_THRESHOLD_MS frequently.

        Only tool_result events have a duration_ms value, so we filter for
        those specifically.
        """
        logs = (
            self.db.table("execution_logs")
            .select("tool_name, duration_ms")
            .eq("workflow_id", self.workflow_id)
            .eq("event_type", "tool_result")
            .execute()
        )

        if not logs:
            return []

        # Group durations by tool name
        stats = defaultdict(lambda: {"total": 0, "slow_count": 0, "total_ms": 0})
        for log in logs:
            name = log.get("tool_name")
            duration = log.get("duration_ms")
            if not name or duration is None:
                continue
            stats[name]["total"] += 1
            stats[name]["total_ms"] += duration
            if duration > SLOW_TOOL_THRESHOLD_MS:
                stats[name]["slow_count"] += 1

        proposals = []
        for tool_name, counts in stats.items():
            if counts["total"] == 0:
                continue

            slow_rate = counts["slow_count"] / counts["total"]
            avg_ms = counts["total_ms"] / counts["total"]

            if slow_rate >= MIN_PATTERN_CONFIDENCE:
                proposals.append({
                    "proposal_type": "performance_improvement",
                    "title": f"Slow execution detected in {tool_name}",
                    "description": (
                        f"{tool_name} exceeds {SLOW_TOOL_THRESHOLD_MS} ms "
                        f"{slow_rate:.0%} of the time (avg: {avg_ms:.0f} ms). "
                        f"Consider caching results or reducing external calls."
                    ),
                    "pattern_data": {
                        "tool_name": tool_name,
                        "avg_duration_ms": avg_ms,
                        "slow_rate": slow_rate,
                        "threshold_ms": SLOW_TOOL_THRESHOLD_MS,
                    },
                    "proposed_changes": {
                        "action": "optimise_tool",
                        "target": tool_name,
                        "suggestion": (
                            "Add caching, reduce API round-trips, "
                            "or run slow operations in parallel."
                        ),
                    },
                })

        return proposals

    # -------------------------------------------------------------------------
    # Database write
    # -------------------------------------------------------------------------

    def _save_proposal(self, proposal: dict):
        """
        Write one proposal to the proposals table.

        pattern_data and proposed_changes are stored as JSON strings so they
        can hold arbitrary structured data without needing extra columns.
        """
        self.db.table("proposals").insert({
            "id": str(uuid.uuid4()),
            "workflow_id": self.workflow_id,
            "generated_at": datetime.utcnow().isoformat(),
            "status": "pending",            # Human must change this to 'approved'
            "proposal_type": proposal["proposal_type"],
            "title": proposal["title"],
            "description": proposal["description"],
            "pattern_data": json.dumps(proposal["pattern_data"]),
            "proposed_changes": json.dumps(proposal["proposed_changes"]),
            "applied_at": None,
            "applied_by": None,
        }).execute()
