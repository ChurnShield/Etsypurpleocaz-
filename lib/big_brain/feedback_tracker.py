# =============================================================================
# lib/big_brain/feedback_tracker.py
#
# ProposalFeedbackTracker — closes the self-improvement loop.
#
# What it does
# ------------
# 1. Records before/after metrics when a proposal is applied
# 2. Evaluates whether the proposal improved the target metric
# 3. Builds a knowledge base of "what worked" for future proposals
# 4. Provides effectiveness stats to SmallBrain/BigBrain for better proposals
#
# What it does NOT do
# -------------------
# It never auto-applies proposals (human-in-the-loop required).
# It only reads and writes the proposals table.
# =============================================================================

import os
import sys
import json
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Optional, Any

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_here = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(_here))

if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.common_tools.sqlite_client import get_client


class ProposalFeedbackTracker:
    """
    Tracks proposal outcomes and builds learning memory.

    Usage
    -----
    tracker = ProposalFeedbackTracker(db=db)

    # Before applying a proposal, snapshot current metrics
    tracker.snapshot_before(proposal_id, workflow_id="my_workflow")

    # After applying and running a few times, snapshot again
    tracker.snapshot_after(proposal_id, workflow_id="my_workflow")

    # Record the outcome
    tracker.record_outcome(proposal_id, outcome="improved", notes="Failure rate dropped")

    # Query effectiveness for future decision-making
    stats = tracker.get_effectiveness_stats()
    history = tracker.get_history_for_target("content_validator")
    """

    def __init__(self, db=None):
        self.db = db or get_client()

    # -------------------------------------------------------------------------
    # Metric snapshots
    # -------------------------------------------------------------------------

    def snapshot_before(self, proposal_id: str, workflow_id: str = None) -> Dict:
        """
        Capture current metrics for a proposal's target before applying it.

        Reads execution_logs for the last 24h and computes:
        - Failure rate for the target validator (if validator_improvement)
        - Avg duration for the target tool (if performance_improvement)
        - Overall workflow success rate

        Returns the snapshot dict and saves it to metric_before.
        """
        proposal = self._get_proposal(proposal_id)
        if not proposal:
            return {"error": "proposal_not_found"}

        wf_id = workflow_id or proposal.get("workflow_id")
        metrics = self._compute_metrics(proposal, wf_id)

        self.db.table("proposals").update({
            "metric_before": json.dumps(metrics),
        }).eq("id", proposal_id).execute()

        return metrics

    def snapshot_after(self, proposal_id: str, workflow_id: str = None) -> Dict:
        """
        Capture metrics after a proposal has been applied and enough runs have occurred.

        Same metrics as snapshot_before — the difference reveals impact.
        """
        proposal = self._get_proposal(proposal_id)
        if not proposal:
            return {"error": "proposal_not_found"}

        wf_id = workflow_id or proposal.get("workflow_id")
        metrics = self._compute_metrics(proposal, wf_id)

        self.db.table("proposals").update({
            "metric_after": json.dumps(metrics),
        }).eq("id", proposal_id).execute()

        return metrics

    # -------------------------------------------------------------------------
    # Outcome recording
    # -------------------------------------------------------------------------

    def record_outcome(
        self,
        proposal_id: str,
        outcome: str,
        notes: str = "",
        feedback_score: float = None,
    ) -> Dict:
        """
        Record the outcome of an applied proposal.

        Args:
            proposal_id: The proposal to update.
            outcome: One of 'improved', 'no_change', 'worsened'.
            notes: Human notes about what happened.
            feedback_score: Optional -1.0 to +1.0 score.
                           If not provided, auto-computed from before/after.

        Returns:
            Updated proposal dict.
        """
        proposal = self._get_proposal(proposal_id)
        if not proposal:
            return {"error": "proposal_not_found"}

        if feedback_score is None:
            feedback_score = self._auto_score(proposal, outcome)

        update = {
            "outcome": outcome,
            "outcome_notes": notes,
            "resolved_at": datetime.utcnow().isoformat(),
            "feedback_score": feedback_score,
        }

        self.db.table("proposals").update(update).eq("id", proposal_id).execute()

        return {**update, "proposal_id": proposal_id}

    # -------------------------------------------------------------------------
    # Learning queries
    # -------------------------------------------------------------------------

    def get_effectiveness_stats(self) -> Dict:
        """
        Get aggregate effectiveness stats across all resolved proposals.

        Returns:
            {
                total_resolved: int,
                improved: int,
                no_change: int,
                worsened: int,
                avg_feedback_score: float,
                by_type: {proposal_type: {improved, no_change, worsened, avg_score}}
            }
        """
        all_proposals = (
            self.db.table("proposals")
            .select("proposal_type, outcome, feedback_score")
            .execute()
        )

        resolved = [p for p in all_proposals if p.get("outcome")]

        stats = {
            "total_resolved": len(resolved),
            "improved": 0,
            "no_change": 0,
            "worsened": 0,
            "avg_feedback_score": 0.0,
            "by_type": {},
        }

        if not resolved:
            return stats

        scores = []
        by_type = defaultdict(lambda: {
            "improved": 0, "no_change": 0, "worsened": 0, "scores": []
        })

        for p in resolved:
            outcome = p.get("outcome", "no_change")
            ptype = p.get("proposal_type", "unknown")
            score = p.get("feedback_score")

            if outcome in stats:
                stats[outcome] += 1
            by_type[ptype][outcome] = by_type[ptype].get(outcome, 0) + 1

            if score is not None:
                scores.append(score)
                by_type[ptype]["scores"].append(score)

        stats["avg_feedback_score"] = (
            round(sum(scores) / len(scores), 3) if scores else 0.0
        )

        for ptype, data in by_type.items():
            type_scores = data.pop("scores", [])
            data["avg_score"] = (
                round(sum(type_scores) / len(type_scores), 3) if type_scores else 0.0
            )

        stats["by_type"] = dict(by_type)
        return stats

    def get_history_for_target(self, target_name: str) -> List[Dict]:
        """
        Get all past proposals targeting a specific validator or tool.

        Useful for: "Has fixing content_validator worked before?"
        """
        all_proposals = (
            self.db.table("proposals")
            .select("id, proposal_type, title, outcome, feedback_score, "
                    "metric_before, metric_after, resolved_at, proposed_changes")
            .execute()
        )

        matching = []
        for p in all_proposals:
            try:
                changes = json.loads(p.get("proposed_changes", "{}"))
            except (json.JSONDecodeError, TypeError):
                changes = {}
            if changes.get("target") == target_name:
                matching.append(p)

        return matching

    def get_success_rate_for_type(self, proposal_type: str) -> float:
        """
        What percentage of proposals of this type led to improvement?

        Returns 0.0 if no resolved proposals of this type exist.
        """
        proposals = (
            self.db.table("proposals")
            .select("outcome")
            .eq("proposal_type", proposal_type)
            .execute()
        )

        resolved = [p for p in proposals if p.get("outcome")]
        if not resolved:
            return 0.0

        improved = len([p for p in resolved if p["outcome"] == "improved"])
        return round(improved / len(resolved), 3)

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _get_proposal(self, proposal_id: str) -> Optional[Dict]:
        rows = (
            self.db.table("proposals")
            .select("*")
            .eq("id", proposal_id)
            .execute()
        )
        return rows[0] if rows else None

    def _compute_metrics(self, proposal: Dict, workflow_id: str) -> Dict:
        """Compute relevant metrics based on proposal type."""
        cutoff = (datetime.utcnow() - timedelta(hours=24)).isoformat()
        metrics = {"snapshot_at": datetime.utcnow().isoformat()}

        try:
            changes = json.loads(proposal.get("proposed_changes", "{}"))
        except (json.JSONDecodeError, TypeError):
            changes = {}

        target = changes.get("target", "")
        ptype = proposal.get("proposal_type", "")

        if ptype == "validator_improvement" and target:
            logs = (
                self.db.table("execution_logs")
                .select("success")
                .eq("workflow_id", workflow_id)
                .eq("event_type", "validation")
                .eq("validator_name", target)
                .gte("timestamp", cutoff)
                .execute()
            )
            total = len(logs)
            passed = len([l for l in logs if l.get("success")])
            metrics["validator_name"] = target
            metrics["total_checks"] = total
            metrics["pass_rate"] = round(passed / total, 3) if total else 0.0
            metrics["fail_rate"] = round(1 - (passed / total), 3) if total else 0.0

        elif ptype == "performance_improvement" and target:
            logs = (
                self.db.table("execution_logs")
                .select("duration_ms")
                .eq("workflow_id", workflow_id)
                .eq("event_type", "tool_result")
                .eq("tool_name", target)
                .gte("timestamp", cutoff)
                .execute()
            )
            durations = [l["duration_ms"] for l in logs if l.get("duration_ms")]
            metrics["tool_name"] = target
            metrics["total_calls"] = len(durations)
            metrics["avg_duration_ms"] = (
                round(sum(durations) / len(durations)) if durations else 0
            )

        # Overall workflow success rate
        executions = (
            self.db.table("executions")
            .select("status")
            .eq("workflow_id", workflow_id)
            .gte("started_at", cutoff)
            .execute()
        )
        total_exec = len(executions)
        success_exec = len([e for e in executions if e.get("status") == "completed"])
        metrics["workflow_success_rate"] = (
            round(success_exec / total_exec, 3) if total_exec else 0.0
        )

        return metrics

    def _auto_score(self, proposal: Dict, outcome: str) -> float:
        """
        Auto-compute a feedback score from before/after metrics.

        Returns:
            +1.0 for clear improvement
            +0.5 for moderate improvement
             0.0 for no change
            -0.5 for moderate worsening
            -1.0 for clear worsening
        """
        if outcome == "improved":
            base = 0.5
        elif outcome == "worsened":
            base = -0.5
        else:
            base = 0.0

        try:
            before = json.loads(proposal.get("metric_before") or "{}")
            after = json.loads(proposal.get("metric_after") or "{}")
        except (json.JSONDecodeError, TypeError):
            return base

        ptype = proposal.get("proposal_type", "")

        if ptype == "validator_improvement":
            before_rate = before.get("fail_rate", 0)
            after_rate = after.get("fail_rate", 0)
            if before_rate > 0:
                improvement = (before_rate - after_rate) / before_rate
                if improvement > 0.5:
                    return 1.0
                elif improvement > 0.2:
                    return 0.5
                elif improvement < -0.5:
                    return -1.0
                elif improvement < -0.2:
                    return -0.5

        elif ptype == "performance_improvement":
            before_ms = before.get("avg_duration_ms", 0)
            after_ms = after.get("avg_duration_ms", 0)
            if before_ms > 0:
                improvement = (before_ms - after_ms) / before_ms
                if improvement > 0.5:
                    return 1.0
                elif improvement > 0.2:
                    return 0.5
                elif improvement < -0.5:
                    return -1.0
                elif improvement < -0.2:
                    return -0.5

        return base
