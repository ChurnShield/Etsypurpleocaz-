"""Obsidian Vault Manager — creates and maintains a structured knowledge vault.

Vault structure:
    vault_root/
    ├── Workflows/           # One note per workflow with run history
    ├── Executions/          # One note per execution run
    ├── Proposals/           # Brain-generated improvement proposals
    ├── Analytics/           # Performance dashboards and trends
    ├── Daily Notes/         # Daily summaries auto-linked
    └── Templates/           # Note templates (managed by this module)
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


# ── Vault folder names ──
FOLDER_WORKFLOWS = "Workflows"
FOLDER_EXECUTIONS = "Executions"
FOLDER_PROPOSALS = "Proposals"
FOLDER_ANALYTICS = "Analytics"
FOLDER_DAILY = "Daily Notes"
FOLDER_TEMPLATES = "Templates"

ALL_FOLDERS = [
    FOLDER_WORKFLOWS,
    FOLDER_EXECUTIONS,
    FOLDER_PROPOSALS,
    FOLDER_ANALYTICS,
    FOLDER_DAILY,
    FOLDER_TEMPLATES,
]


class ObsidianVaultManager:
    """Manages the Obsidian vault directory structure, note creation, and linking."""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)

    # ── Vault setup ──────────────────────────────────────────────

    def init_vault(self) -> Dict[str, Any]:
        """Create vault folder structure and seed templates. Idempotent."""
        created = []
        for folder in ALL_FOLDERS:
            folder_path = self.vault_path / folder
            if not folder_path.exists():
                folder_path.mkdir(parents=True, exist_ok=True)
                created.append(folder)

        self._seed_templates()
        return {"vault_path": str(self.vault_path), "folders_created": created}

    # ── Note creation ────────────────────────────────────────────

    def write_workflow_note(self, workflow: Dict[str, Any]) -> str:
        """Create or update a Workflow note with run stats and links."""
        workflow_id = workflow.get("id", "unknown")
        name = workflow.get("name", workflow_id)
        total_runs = workflow.get("total_runs", 0)
        successful_runs = workflow.get("successful_runs", 0)
        success_rate = (
            round(successful_runs / total_runs * 100, 1) if total_runs > 0 else 0
        )

        content = (
            f"---\n"
            f"tags: [workflow, {_slug(name)}]\n"
            f"workflow_id: {workflow_id}\n"
            f"updated: {_now_iso()}\n"
            f"---\n\n"
            f"# {name}\n\n"
            f"## Stats\n"
            f"| Metric | Value |\n"
            f"|--------|-------|\n"
            f"| Total runs | {total_runs} |\n"
            f"| Successful | {successful_runs} |\n"
            f"| Success rate | {success_rate}% |\n\n"
            f"## Recent Executions\n"
            f"```dataview\n"
            f'LIST FROM "Executions" WHERE workflow_id = "{workflow_id}"\n'
            f"SORT timestamp DESC\n"
            f"LIMIT 20\n"
            f"```\n\n"
            f"## Proposals\n"
            f"```dataview\n"
            f'LIST FROM "Proposals" WHERE workflow_id = "{workflow_id}"\n'
            f"SORT created DESC\n"
            f"```\n"
        )

        return self._write_note(FOLDER_WORKFLOWS, f"{_slug(name)}.md", content)

    def write_execution_note(
        self, execution: Dict[str, Any], log_events: List[Dict[str, Any]]
    ) -> str:
        """Create a note for a single workflow execution run."""
        exec_id = execution.get("id", "unknown")
        workflow_id = execution.get("workflow_id", "unknown")
        status = execution.get("status", "unknown")
        started = execution.get("started_at", "")
        ended = execution.get("ended_at", "")

        phases_md = self._format_log_events(log_events)

        content = (
            f"---\n"
            f"tags: [execution, {status}]\n"
            f"execution_id: {exec_id}\n"
            f"workflow_id: {workflow_id}\n"
            f"status: {status}\n"
            f"timestamp: {started}\n"
            f"---\n\n"
            f"# Execution {exec_id[:8]}\n\n"
            f"**Workflow**: [[{_slug(workflow_id)}]]\n"
            f"**Status**: {status}\n"
            f"**Started**: {started}\n"
            f"**Ended**: {ended}\n\n"
            f"## Phase Log\n\n"
            f"{phases_md}\n"
        )

        filename = f"{exec_id[:8]}_{_date_slug(started)}.md"
        return self._write_note(FOLDER_EXECUTIONS, filename, content)

    def write_proposal_note(self, proposal: Dict[str, Any]) -> str:
        """Create a note for a Brain proposal."""
        proposal_id = proposal.get("id", "unknown")
        workflow_id = proposal.get("workflow_id", "system-wide")
        proposal_type = proposal.get("type", "improvement")
        status = proposal.get("status", "pending")
        description = proposal.get("description", "")
        evidence = proposal.get("evidence", "")
        created = proposal.get("created_at", _now_iso())

        content = (
            f"---\n"
            f"tags: [proposal, {status}, {proposal_type}]\n"
            f"proposal_id: {proposal_id}\n"
            f"workflow_id: {workflow_id}\n"
            f"status: {status}\n"
            f"created: {created}\n"
            f"---\n\n"
            f"# Proposal: {proposal_type}\n\n"
            f"**Workflow**: [[{_slug(str(workflow_id))}]]\n"
            f"**Status**: `{status}`\n"
            f"**Created**: {created}\n\n"
            f"## Description\n\n"
            f"{description}\n\n"
            f"## Evidence\n\n"
            f"{evidence}\n\n"
            f"## Decision\n\n"
            f"- [ ] Approved\n"
            f"- [ ] Rejected\n"
            f"- Notes: \n"
        )

        filename = f"{proposal_id[:8]}_{proposal_type}.md"
        return self._write_note(FOLDER_PROPOSALS, filename, content)

    def write_analytics_note(self, title: str, sections: Dict[str, str]) -> str:
        """Create an analytics/dashboard note with arbitrary sections."""
        tags_str = "analytics, dashboard"
        body = ""
        for heading, text in sections.items():
            body += f"## {heading}\n\n{text}\n\n"

        content = (
            f"---\n"
            f"tags: [{tags_str}]\n"
            f"updated: {_now_iso()}\n"
            f"---\n\n"
            f"# {title}\n\n"
            f"{body}"
        )

        return self._write_note(FOLDER_ANALYTICS, f"{_slug(title)}.md", content)

    def write_daily_note(
        self,
        date: str,
        summary: str,
        executions: List[str],
        proposals: List[str],
    ) -> str:
        """Create or update a daily note with links to the day's activity."""
        exec_links = "\n".join(f"- [[{e}]]" for e in executions) or "- None"
        proposal_links = "\n".join(f"- [[{p}]]" for p in proposals) or "- None"

        content = (
            f"---\n"
            f"tags: [daily-note]\n"
            f"date: {date}\n"
            f"---\n\n"
            f"# {date}\n\n"
            f"## Summary\n\n"
            f"{summary}\n\n"
            f"## Executions\n\n"
            f"{exec_links}\n\n"
            f"## Proposals\n\n"
            f"{proposal_links}\n"
        )

        return self._write_note(FOLDER_DAILY, f"{date}.md", content)

    # ── Internal helpers ─────────────────────────────────────────

    def _write_note(self, folder: str, filename: str, content: str) -> str:
        """Write a note to the vault. Returns the file path."""
        folder_path = self.vault_path / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        note_path = folder_path / filename
        note_path.write_text(content, encoding="utf-8")
        return str(note_path)

    def _format_log_events(self, events: List[Dict[str, Any]]) -> str:
        """Format execution log events into readable markdown."""
        if not events:
            return "_No log events recorded._"

        lines = []
        for event in events:
            event_type = event.get("event_type", "unknown")
            phase = event.get("phase", "")
            success = event.get("success")
            tool = event.get("tool_name", "")
            validator = event.get("validator_name", "")
            duration = event.get("duration_ms")
            error = event.get("error_message", "")
            timestamp = event.get("timestamp", "")

            icon = "+" if success else "-"
            actor = tool or validator or phase or event_type

            line = f"  {icon} **{event_type}** — {actor}"
            if duration:
                line += f" ({duration}ms)"
            if error:
                line += f" — `{error}`"
            if timestamp:
                line += f"  _({timestamp})_"
            lines.append(line)

        return "\n".join(lines)

    def _seed_templates(self):
        """Write starter templates into the Templates folder."""
        templates_dir = self.vault_path / FOLDER_TEMPLATES
        templates_dir.mkdir(parents=True, exist_ok=True)

        # Execution template
        exec_template = (
            "---\n"
            "tags: [execution]\n"
            "execution_id: \n"
            "workflow_id: \n"
            "status: \n"
            "---\n\n"
            "# Execution {{execution_id}}\n\n"
            "**Workflow**: [[{{workflow_id}}]]\n"
            "**Status**: {{status}}\n\n"
            "## Phase Log\n\n"
        )
        (templates_dir / "execution_template.md").write_text(
            exec_template, encoding="utf-8"
        )

        # Proposal template
        proposal_template = (
            "---\n"
            "tags: [proposal, pending]\n"
            "proposal_id: \n"
            "workflow_id: \n"
            "---\n\n"
            "# Proposal: {{type}}\n\n"
            "**Workflow**: [[{{workflow_id}}]]\n\n"
            "## Description\n\n"
            "## Evidence\n\n"
            "## Decision\n\n"
            "- [ ] Approved\n"
            "- [ ] Rejected\n"
        )
        (templates_dir / "proposal_template.md").write_text(
            proposal_template, encoding="utf-8"
        )


# ── Module-level helpers ─────────────────────────────────────

def _slug(text: str) -> str:
    """Convert text to a safe filename slug."""
    return text.lower().replace(" ", "-").replace("_", "-")


def _now_iso() -> str:
    return datetime.utcnow().isoformat()


def _date_slug(iso_timestamp: str) -> str:
    """Extract YYYY-MM-DD from an ISO timestamp, or use today."""
    try:
        return iso_timestamp[:10]
    except (TypeError, IndexError):
        return datetime.utcnow().strftime("%Y-%m-%d")
