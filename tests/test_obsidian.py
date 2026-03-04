import os
import json
import pytest
import tempfile
import shutil

from lib.obsidian.vault_manager import ObsidianVaultManager, ALL_FOLDERS
from lib.obsidian.sync_tool import ObsidianSyncTool


@pytest.fixture
def vault_dir():
    """Create a temporary vault directory for each test."""
    tmpdir = tempfile.mkdtemp(prefix="obsidian_test_")
    yield tmpdir
    shutil.rmtree(tmpdir, ignore_errors=True)


# ── VaultManager tests ──────────────────────────────────────


class TestObsidianVaultManager:
    def test_init_vault_creates_folders(self, vault_dir):
        mgr = ObsidianVaultManager(vault_dir)
        result = mgr.init_vault()

        assert result["vault_path"] == vault_dir
        assert len(result["folders_created"]) == len(ALL_FOLDERS)

        for folder in ALL_FOLDERS:
            assert os.path.isdir(os.path.join(vault_dir, folder))

    def test_init_vault_is_idempotent(self, vault_dir):
        mgr = ObsidianVaultManager(vault_dir)
        mgr.init_vault()
        result = mgr.init_vault()

        # Second call creates nothing new
        assert result["folders_created"] == []

    def test_seed_templates_created(self, vault_dir):
        mgr = ObsidianVaultManager(vault_dir)
        mgr.init_vault()

        templates_dir = os.path.join(vault_dir, "Templates")
        assert os.path.isfile(os.path.join(templates_dir, "execution_template.md"))
        assert os.path.isfile(os.path.join(templates_dir, "proposal_template.md"))

    def test_write_workflow_note(self, vault_dir):
        mgr = ObsidianVaultManager(vault_dir)
        mgr.init_vault()

        path = mgr.write_workflow_note({
            "id": "market_intelligence",
            "name": "Market Intelligence",
            "total_runs": 20,
            "successful_runs": 18,
        })

        assert os.path.isfile(path)
        content = open(path).read()
        assert "Market Intelligence" in content
        assert "90.0%" in content
        assert "workflow_id: market_intelligence" in content

    def test_write_execution_note(self, vault_dir):
        mgr = ObsidianVaultManager(vault_dir)
        mgr.init_vault()

        path = mgr.write_execution_note(
            execution={
                "id": "abc12345-def6-7890",
                "workflow_id": "ai_news_rss",
                "status": "success",
                "started_at": "2026-03-04T10:00:00",
                "ended_at": "2026-03-04T10:01:30",
            },
            log_events=[
                {
                    "event_type": "phase_start",
                    "phase": "Fetch RSS",
                    "success": True,
                    "timestamp": "2026-03-04T10:00:01",
                },
                {
                    "event_type": "tool_result",
                    "tool_name": "FetchRSSTool",
                    "success": True,
                    "duration_ms": 1500,
                    "timestamp": "2026-03-04T10:00:03",
                },
            ],
        )

        assert os.path.isfile(path)
        content = open(path).read()
        assert "abc12345" in content
        assert "success" in content
        assert "FetchRSSTool" in content

    def test_write_proposal_note(self, vault_dir):
        mgr = ObsidianVaultManager(vault_dir)
        mgr.init_vault()

        path = mgr.write_proposal_note({
            "id": "prop-0001-abcdef",
            "workflow_id": "etsy_analytics",
            "type": "validator_improvement",
            "status": "pending",
            "description": "PerformanceValidator fails 80% of runs.",
            "evidence": "8 out of 10 recent runs failed validation.",
            "created_at": "2026-03-04T12:00:00",
        })

        assert os.path.isfile(path)
        content = open(path).read()
        assert "validator_improvement" in content
        assert "pending" in content
        assert "80%" in content

    def test_write_daily_note(self, vault_dir):
        mgr = ObsidianVaultManager(vault_dir)
        mgr.init_vault()

        path = mgr.write_daily_note(
            date="2026-03-04",
            summary="3 runs today, all passed.",
            executions=["abc12345_2026-03-04", "def67890_2026-03-04"],
            proposals=["prop-0001_validator_improvement"],
        )

        assert os.path.isfile(path)
        content = open(path).read()
        assert "2026-03-04" in content
        assert "[[abc12345_2026-03-04]]" in content
        assert "[[prop-0001_validator_improvement]]" in content

    def test_write_analytics_note(self, vault_dir):
        mgr = ObsidianVaultManager(vault_dir)
        mgr.init_vault()

        path = mgr.write_analytics_note("System Dashboard", {
            "Workflow Health": "All systems operational.",
            "Pending Proposals": "2 proposals awaiting review.",
        })

        assert os.path.isfile(path)
        content = open(path).read()
        assert "System Dashboard" in content
        assert "All systems operational" in content

    def test_empty_log_events(self, vault_dir):
        mgr = ObsidianVaultManager(vault_dir)
        mgr.init_vault()

        path = mgr.write_execution_note(
            execution={"id": "empty-run", "workflow_id": "test", "status": "success"},
            log_events=[],
        )

        content = open(path).read()
        assert "No log events recorded" in content


# ── SyncTool tests ──────────────────────────────────────────


class FakeDBResult:
    """Minimal mock for SQLiteClient chained queries."""

    def __init__(self, data=None):
        self._data = data or []

    def table(self, name):
        return self

    def select(self, cols):
        return self

    def eq(self, col, val):
        return self

    def gte(self, col, val):
        return self

    def execute(self):
        return {"data": self._data}


class TestObsidianSyncTool:
    def test_extends_base_tool(self, vault_dir):
        from lib.orchestrator.base_tool import BaseTool
        tool = ObsidianSyncTool(vault_path=vault_dir)
        assert isinstance(tool, BaseTool)

    def test_returns_standard_result_format(self, vault_dir):
        tool = ObsidianSyncTool(vault_path=vault_dir)
        db = FakeDBResult()
        result = tool.execute(db_client=db, sync_scope="full")

        assert "success" in result
        assert "data" in result
        assert "error" in result
        assert "tool_name" in result
        assert "metadata" in result

    def test_sync_full_with_empty_db(self, vault_dir):
        tool = ObsidianSyncTool(vault_path=vault_dir)
        db = FakeDBResult()
        result = tool.execute(db_client=db, sync_scope="full")

        assert result["success"] is True
        assert result["data"]["workflows_synced"] == 0
        assert result["data"]["executions_synced"] == 0
        assert result["data"]["proposals_synced"] == 0
        assert result["data"]["daily_notes_created"] == 1
        assert result["data"]["analytics_updated"] is True

    def test_sync_proposals_only(self, vault_dir):
        tool = ObsidianSyncTool(vault_path=vault_dir)
        db = FakeDBResult()
        result = tool.execute(db_client=db, sync_scope="proposals_only")

        assert result["success"] is True
        assert result["data"]["daily_notes_created"] == 0
        assert result["data"]["analytics_updated"] is False

    def test_missing_db_client_returns_error(self, vault_dir):
        tool = ObsidianSyncTool(vault_path=vault_dir)
        result = tool.execute()

        assert result["success"] is False
        assert "db_client is required" in result["error"]

    def test_tool_name(self, vault_dir):
        tool = ObsidianSyncTool(vault_path=vault_dir)
        assert tool.get_name() == "ObsidianSyncTool"

    def test_sync_with_workflow_data(self, vault_dir):
        workflows = [
            {"id": "wf1", "name": "Test Workflow", "total_runs": 5, "successful_runs": 4},
        ]
        db = FakeDBResult(data=workflows)
        tool = ObsidianSyncTool(vault_path=vault_dir)
        result = tool.execute(db_client=db, sync_scope="full")

        assert result["success"] is True
        assert result["data"]["workflows_synced"] == 1

        # Verify file was actually created
        wf_note = os.path.join(vault_dir, "Workflows", "test-workflow.md")
        assert os.path.isfile(wf_note)

    def test_duration_ms_in_metadata(self, vault_dir):
        tool = ObsidianSyncTool(vault_path=vault_dir)
        db = FakeDBResult()
        result = tool.execute(db_client=db, sync_scope="recent")

        assert "duration_ms" in result["metadata"]
        assert isinstance(result["metadata"]["duration_ms"], int)
