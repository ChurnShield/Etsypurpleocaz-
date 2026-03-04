"""ObsidianSyncTool — syncs system knowledge into an Obsidian vault.

Reads workflows, executions, proposals, and logs from the database
and writes structured, cross-linked Markdown notes into the vault.

Usage in a workflow:
    tool = ObsidianSyncTool(vault_path=OBSIDIAN_VAULT_PATH)
    result = tool.execute(db_client=db, sync_scope="full")
"""

import json
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from lib.obsidian.vault_manager import ObsidianVaultManager
from lib.orchestrator.base_tool import BaseTool


class ObsidianSyncTool(BaseTool):
    """Syncs database knowledge into an Obsidian vault.

    Extends BaseTool — returns standard {success, data, error, tool_name, metadata}.
    """

    def __init__(self, vault_path: str):
        self._vault_path = vault_path
        self._vault = ObsidianVaultManager(vault_path)

    def execute(self, **kwargs) -> Dict[str, Any]:
        """Sync system data to the Obsidian vault.

        Keyword Args:
            db_client: SQLiteClient instance for reading data.
            sync_scope: "full" | "recent" | "proposals_only" (default: "recent").
            since_hours: For "recent" scope, how far back to look (default: 24).

        Returns:
            Standard tool result dict.
        """
        start_ms = time.time()

        try:
            db = kwargs.get("db_client")
            if db is None:
                return self._error_result("db_client is required")

            sync_scope = kwargs.get("sync_scope", "recent")
            since_hours = kwargs.get("since_hours", 24)

            # Initialize vault structure
            init_result = self._vault.init_vault()

            stats = {
                "workflows_synced": 0,
                "executions_synced": 0,
                "proposals_synced": 0,
                "daily_notes_created": 0,
                "analytics_updated": False,
                "vault_path": self._vault_path,
                "sync_scope": sync_scope,
            }

            # Sync workflows (always — they're lightweight)
            workflows = self._fetch_workflows(db)
            for wf in workflows:
                self._vault.write_workflow_note(wf)
                stats["workflows_synced"] += 1

            # Sync proposals
            proposals = self._fetch_proposals(db, sync_scope, since_hours)
            proposal_filenames = []
            for prop in proposals:
                path = self._vault.write_proposal_note(prop)
                proposal_filenames.append(_filename_from_path(path))
                stats["proposals_synced"] += 1

            if sync_scope != "proposals_only":
                # Sync executions
                executions = self._fetch_executions(db, sync_scope, since_hours)
                execution_filenames = []
                for exc in executions:
                    logs = self._fetch_execution_logs(db, exc["id"])
                    path = self._vault.write_execution_note(exc, logs)
                    execution_filenames.append(_filename_from_path(path))
                    stats["executions_synced"] += 1

                # Create daily note for today
                today = datetime.utcnow().strftime("%Y-%m-%d")
                summary = self._build_daily_summary(workflows, executions, proposals)
                self._vault.write_daily_note(
                    date=today,
                    summary=summary,
                    executions=execution_filenames,
                    proposals=proposal_filenames,
                )
                stats["daily_notes_created"] = 1

                # Update analytics dashboard
                self._write_analytics_dashboard(db, workflows)
                stats["analytics_updated"] = True

            duration_ms = int((time.time() - start_ms) * 1000)

            return {
                "success": True,
                "data": stats,
                "error": None,
                "tool_name": self.get_name(),
                "metadata": {
                    "duration_ms": duration_ms,
                    "vault_initialized": bool(init_result.get("folders_created")),
                },
            }

        except Exception as e:
            duration_ms = int((time.time() - start_ms) * 1000)
            return {
                "success": False,
                "data": None,
                "error": str(e),
                "tool_name": self.get_name(),
                "metadata": {"duration_ms": duration_ms},
            }

    # ── Data fetching ────────────────────────────────────────────

    def _fetch_workflows(self, db) -> List[Dict[str, Any]]:
        result = db.table("workflows").select("*").execute()
        return result.get("data", []) if isinstance(result, dict) else []

    def _fetch_executions(
        self, db, scope: str, since_hours: int
    ) -> List[Dict[str, Any]]:
        query = db.table("executions").select("*")
        if scope == "recent":
            cutoff = (
                datetime.utcnow() - timedelta(hours=since_hours)
            ).isoformat()
            query = query.gte("started_at", cutoff)
        result = query.execute()
        return result.get("data", []) if isinstance(result, dict) else []

    def _fetch_execution_logs(
        self, db, execution_id: str
    ) -> List[Dict[str, Any]]:
        result = (
            db.table("execution_logs")
            .select("*")
            .eq("execution_id", execution_id)
            .execute()
        )
        return result.get("data", []) if isinstance(result, dict) else []

    def _fetch_proposals(
        self, db, scope: str, since_hours: int
    ) -> List[Dict[str, Any]]:
        query = db.table("proposals").select("*")
        if scope == "recent":
            cutoff = (
                datetime.utcnow() - timedelta(hours=since_hours)
            ).isoformat()
            query = query.gte("created_at", cutoff)
        result = query.execute()
        return result.get("data", []) if isinstance(result, dict) else []

    # ── Helpers ──────────────────────────────────────────────────

    def _build_daily_summary(
        self,
        workflows: List[Dict],
        executions: List[Dict],
        proposals: List[Dict],
    ) -> str:
        total_exec = len(executions)
        successful = sum(
            1 for e in executions if e.get("status") == "success"
        )
        failed = total_exec - successful
        pending_proposals = sum(
            1 for p in proposals if p.get("status") == "pending"
        )

        lines = [
            f"- **{total_exec}** workflow runs ({successful} succeeded, {failed} failed)",
            f"- **{len(workflows)}** active workflows",
            f"- **{len(proposals)}** proposals synced ({pending_proposals} pending review)",
        ]
        return "\n".join(lines)

    def _write_analytics_dashboard(
        self, db, workflows: List[Dict]
    ) -> None:
        sections = {}

        # Workflow health table
        rows = ["| Workflow | Runs | Success Rate |", "|---------|------|-------------|"]
        for wf in workflows:
            name = wf.get("name", wf.get("id", "?"))
            total = wf.get("total_runs", 0)
            success = wf.get("successful_runs", 0)
            rate = f"{round(success / total * 100, 1)}%" if total > 0 else "N/A"
            rows.append(f"| {name} | {total} | {rate} |")
        sections["Workflow Health"] = "\n".join(rows)

        # Pending proposals count
        result = (
            db.table("proposals")
            .select("*")
            .eq("status", "pending")
            .execute()
        )
        pending = result.get("data", []) if isinstance(result, dict) else []
        sections["Pending Proposals"] = (
            f"**{len(pending)}** proposals awaiting review.\n\n"
            "```dataview\n"
            'LIST FROM "Proposals" WHERE status = "pending"\n'
            "SORT created DESC\n"
            "```"
        )

        self._vault.write_analytics_note("System Dashboard", sections)

    def _error_result(self, message: str) -> Dict[str, Any]:
        return {
            "success": False,
            "data": None,
            "error": message,
            "tool_name": self.get_name(),
            "metadata": {},
        }


def _filename_from_path(path: str) -> str:
    """Extract filename without extension for Obsidian wikilinks."""
    import os
    return os.path.splitext(os.path.basename(path))[0]
