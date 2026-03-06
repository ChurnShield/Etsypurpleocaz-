# =============================================================================
# lib/big_brain/system_proposer.py
#
# SystemProposer -- generates system-wide improvement proposals from
# BigBrain health monitoring results.
#
# What it does
# ------------
# Takes the output of BigBrain.analyze_system_health() and converts detected
# problems into actionable proposals.  Each proposal is:
#   1. Saved to the proposals table (workflow_id = NULL for system-wide)
#   2. Written as a markdown file to proposals/system/
#
# What it does NOT do
# -------------------
# It never re-analyses raw logs (that is BigBrain's job).
# It only transforms already-detected problems into proposals.
# =============================================================================

import os
import sys
import uuid
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_here = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(_here))

if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.common_tools.sqlite_client import get_client


# ---------------------------------------------------------------------------
# Problem category -> proposal type mapping
# ---------------------------------------------------------------------------
_CATEGORY_TO_PROPOSAL_TYPE = {
    "system_failure_rate":          "platform_optimization",
    "multiple_workflow_failures":   "cross_workflow_fix",
    "performance_degradation":      "platform_optimization",
    "recurring_error":              "cross_workflow_fix",
    "database_size":                "resource_management",
    "api_key_failure":              "security_hardening",
    "unauthorized_access":          "security_hardening",
    "data_corruption":              "infrastructure_upgrade",
    "memory_usage":                 "resource_management",
    "disk_space":                   "resource_management",
    "database_connection":          "infrastructure_upgrade",
    "system_crash":                 "infrastructure_upgrade",
    "data_loss":                    "infrastructure_upgrade",
    "validation_trend":             "platform_optimization",
    "timeout_pattern":              "infrastructure_upgrade",
}


# =============================================================================
# SystemProposer
# =============================================================================

class SystemProposer:
    """
    Converts BigBrain health monitoring results into system-wide proposals.

    Usage
    -----
    from lib.big_brain.system_proposer import SystemProposer
    from lib.common_tools.sqlite_client import get_client

    proposer = SystemProposer(db_client=get_client())
    health = brain.analyze_system_health()
    proposals = proposer.generate_proposals_from_health(asdict(health))
    """

    def __init__(self, db_client=None, proposals_dir: str = None):
        self.db = db_client or get_client()
        if proposals_dir:
            self._proposals_dir = Path(proposals_dir)
        else:
            self._proposals_dir = Path(_project_root) / "proposals" / "system"

    # -------------------------------------------------------------------------
    # Main entry point
    # -------------------------------------------------------------------------

    def generate_proposals_from_health(self, health: Dict[str, Any]) -> List[Dict]:
        """
        Generate proposals from system health analysis.

        Args:
            health: System health dict (from asdict(SystemHealth) or similar).
                    Expected keys: status, problems, system_failure_rate.

        Returns:
            List of proposal dicts that were saved.
        """
        proposals = []

        status = health.get("status", "unknown")
        if status == "healthy":
            print("SystemProposer: System healthy -- no proposals needed")
            return proposals

        problems = health.get("problems", [])

        for problem in problems:
            proposal = self._create_proposal_from_problem(problem, health)
            if proposal:
                proposals.append(proposal)

        for proposal in proposals:
            self._save_system_proposal(proposal)

        print(f"SystemProposer: Generated {len(proposals)} system proposals")
        return proposals

    # -------------------------------------------------------------------------
    # Problem -> Proposal conversion
    # -------------------------------------------------------------------------

    def _create_proposal_from_problem(
        self, problem: Dict, health: Dict
    ) -> Optional[Dict]:
        """
        Create a proposal dict from a detected problem.

        Returns None if the problem category is not mapped to a proposal type.
        """
        category = problem.get("category", "")
        severity = problem.get("severity", "medium")
        description = problem.get("description", "")
        details = problem.get("details", {})

        proposal_type = _CATEGORY_TO_PROPOSAL_TYPE.get(category)
        if not proposal_type:
            return None

        title = self._generate_title(category, details, health)
        affected = self._extract_affected_workflows(details)

        return {
            "proposal_type": proposal_type,
            "severity": severity,
            "title": title,
            "description": description,
            "pattern_data": details,
            "affected_workflows": affected,
            "proposed_changes": self._generate_changes_checklist(proposal_type),
        }

    # -------------------------------------------------------------------------
    # Title generation
    # -------------------------------------------------------------------------

    def _generate_title(self, category: str, details: Dict, health: Dict) -> str:
        """Generate a human-readable title for the proposal."""
        titles = {
            "system_failure_rate": lambda: (
                f"System Failure Rate Critical: "
                f"{health.get('system_failure_rate', 0) * 100:.0f}%"
            ),
            "multiple_workflow_failures": lambda: (
                f"{len(details.get('workflows', []))} Workflows Failing"
            ),
            "performance_degradation": lambda: (
                f"Performance Degraded: {details.get('workflow_id', 'system')} "
                f"{details.get('factor', '?')}x slower"
            ),
            "recurring_error": lambda: (
                f"Recurring Error: "
                f"{details.get('error_message', 'Unknown')[:60]}"
            ),
            "database_size": lambda: (
                f"Database Approaching Capacity: "
                f"{details.get('size_mb', '?')}MB / "
                f"{details.get('limit_mb', '?')}MB"
            ),
            "api_key_failure": lambda: (
                f"API Authentication Failures: "
                f"{details.get('count', '?')} in 24h"
            ),
            "unauthorized_access": lambda: "Unauthorized Access Detected",
            "data_corruption": lambda: "Possible Data Corruption Detected",
            "memory_usage": lambda: (
                f"Memory Usage Critical: "
                f"{details.get('usage_pct', '?')}%"
            ),
            "disk_space": lambda: (
                f"Disk Space Critical: "
                f"{details.get('usage_pct', '?')}% full"
            ),
            "database_connection": lambda: "Database Connection Error",
            "system_crash": lambda: "System Crash Detected",
            "data_loss": lambda: "Possible Data Loss Detected",
            "validation_trend": lambda: "Validation Failures Increasing",
            "timeout_pattern": lambda: (
                f"Timeout Pattern: "
                f"{details.get('count', '?')} timeouts in 24h"
            ),
        }
        gen = titles.get(category)
        if gen:
            try:
                return gen()
            except Exception:
                pass
        return f"System Issue: {category.replace('_', ' ').title()}"

    # -------------------------------------------------------------------------
    # Affected workflows
    # -------------------------------------------------------------------------

    def _extract_affected_workflows(self, details: Dict) -> List[str]:
        """Extract affected workflow IDs from problem details."""
        if "workflows" in details:
            return details["workflows"]
        if "workflow_id" in details and details["workflow_id"]:
            return [details["workflow_id"]]
        return ["all"]

    # -------------------------------------------------------------------------
    # Save proposal (DB + markdown file)
    # -------------------------------------------------------------------------

    def _save_system_proposal(self, proposal: Dict):
        """Save proposal to database and write a markdown file."""
        proposal_id = str(uuid.uuid4())
        now = datetime.utcnow()

        # -- Database --
        self.db.table("proposals").insert({
            "id": proposal_id,
            "workflow_id": None,
            "generated_at": now.isoformat(),
            "status": "pending",
            "proposal_type": proposal["proposal_type"],
            "title": proposal["title"],
            "description": proposal["description"],
            "pattern_data": json.dumps(proposal["pattern_data"]),
            "proposed_changes": json.dumps(proposal["proposed_changes"]),
            "applied_at": None,
            "applied_by": None,
        }).execute()

        # -- Markdown file --
        self._proposals_dir.mkdir(parents=True, exist_ok=True)
        filename = (
            f"proposal_{now.strftime('%Y%m%d_%H%M%S')}_{proposal_id[:8]}.md"
        )
        filepath = self._proposals_dir / filename
        markdown = self._generate_markdown(proposal, proposal_id)
        filepath.write_text(markdown, encoding="utf-8")

        print(f"SystemProposer: Saved -> {filepath.name}")

    # -------------------------------------------------------------------------
    # Markdown generation
    # -------------------------------------------------------------------------

    def _generate_markdown(self, proposal: Dict, proposal_id: str) -> str:
        """Generate full markdown content for a system proposal."""
        now = datetime.utcnow()

        # Format pattern data as bullet list
        pattern_lines = []
        for key, value in proposal["pattern_data"].items():
            formatted_key = key.replace("_", " ").title()
            pattern_lines.append(f"- **{formatted_key}**: {value}")
        pattern_formatted = (
            "\n".join(pattern_lines) if pattern_lines else "No additional data"
        )

        # Format affected workflows
        affected = proposal.get("affected_workflows", ["all"])
        if isinstance(affected, list):
            affected_str = ", ".join(str(w) for w in affected)
        else:
            affected_str = str(affected)

        # Format proposed changes checklist
        changes = proposal.get("proposed_changes", [])
        if isinstance(changes, list):
            changes_str = "\n".join(changes)
        else:
            changes_str = str(changes)

        recommendation = self._get_recommendation(proposal["proposal_type"])

        return (
            f"# System Proposal: {proposal['title']}\n"
            f"\n"
            f"**ID**: {proposal_id}  \n"
            f"**Generated**: {now.strftime('%Y-%m-%d %H:%M:%S')}  \n"
            f"**Type**: {proposal['proposal_type']}  \n"
            f"**Scope**: System-wide  \n"
            f"**Severity**: {proposal['severity'].upper()}  \n"
            f"**Status**: pending\n"
            f"\n"
            f"---\n"
            f"\n"
            f"## System Issue Detected\n"
            f"\n"
            f"{proposal['description']}\n"
            f"\n"
            f"**Affected Workflows**: {affected_str}\n"
            f"\n"
            f"---\n"
            f"\n"
            f"## Evidence\n"
            f"\n"
            f"{pattern_formatted}\n"
            f"\n"
            f"---\n"
            f"\n"
            f"## Recommendation\n"
            f"\n"
            f"{recommendation}\n"
            f"\n"
            f"---\n"
            f"\n"
            f"## Proposed Changes\n"
            f"\n"
            f"{changes_str}\n"
            f"\n"
            f"---\n"
            f"\n"
            f"## Expected Impact\n"
            f"\n"
            f"**If Applied:**\n"
            f"- Improved system stability\n"
            f"- Reduced failure rates across affected workflows\n"
            f"- Better resource utilization\n"
            f"\n"
            f"**If Ignored:**\n"
            f"- System issues may worsen\n"
            f"- More workflows may be affected\n"
            f"- Potential system downtime\n"
            f"\n"
            f"---\n"
            f"\n"
            f"## Review Instructions\n"
            f"\n"
            f"1. Review the system issue and evidence\n"
            f"2. Check boxes `[x]` for changes you want to apply\n"
            f"3. Rename file to `*_APPROVED.md` to mark as approved\n"
            f"4. OR rename to `*_REJECTED.md` if not applicable\n"
            f"\n"
            f"---\n"
            f"\n"
            f"*Generated by BigBrain system-wide health analysis.*\n"
        )

    # -------------------------------------------------------------------------
    # Changes checklist per proposal type
    # -------------------------------------------------------------------------

    def _generate_changes_checklist(self, proposal_type: str) -> List[str]:
        """Return a checklist of proposed changes for the given proposal type."""
        changes_map = {
            "platform_optimization": [
                "- [ ] Optimize database queries (add indexes)",
                "- [ ] Increase ExecutionLogger buffer size",
                "- [ ] Add connection pooling for database",
                "- [ ] Review slow tool implementations",
            ],
            "resource_management": [
                "- [ ] Archive old execution logs (>30 days)",
                "- [ ] Clean up backup files",
                "- [ ] Increase resource limits in config",
                "- [ ] Monitor growth rate and plan capacity",
            ],
            "security_hardening": [
                "- [ ] Rotate API keys and OAuth tokens",
                "- [ ] Add authentication retry logic with backoff",
                "- [ ] Mask sensitive data in logs",
                "- [ ] Review access permissions",
            ],
            "cross_workflow_fix": [
                "- [ ] Investigate common error across workflows",
                "- [ ] Add system-wide retry mechanism",
                "- [ ] Update shared infrastructure",
                "- [ ] Stagger workflow execution times",
            ],
            "infrastructure_upgrade": [
                "- [ ] Upgrade database capacity",
                "- [ ] Improve network stability",
                "- [ ] Add health check endpoint",
                "- [ ] Review system resource allocation",
            ],
        }
        return changes_map.get(
            proposal_type, ["- [ ] Investigate and resolve issue"]
        )

    # -------------------------------------------------------------------------
    # Recommendation text per proposal type
    # -------------------------------------------------------------------------

    def _get_recommendation(self, proposal_type: str) -> str:
        """Return recommendation text for the given proposal type."""
        recommendations = {
            "platform_optimization": (
                "Optimize core system components to improve performance "
                "across all workflows. Focus on the slowest operations first."
            ),
            "resource_management": (
                "Clean up resources and manage capacity to prevent hitting "
                "system limits. Archive old data and monitor growth trends."
            ),
            "security_hardening": (
                "Implement security improvements to protect the system. "
                "Rotate credentials and review access patterns."
            ),
            "cross_workflow_fix": (
                "Fix infrastructure issues affecting multiple workflows. "
                "Start with the most common error across workflows."
            ),
            "infrastructure_upgrade": (
                "Upgrade system infrastructure to handle current demands. "
                "Prioritize stability over new features."
            ),
        }
        return recommendations.get(
            proposal_type, "Address the detected system issue."
        )
