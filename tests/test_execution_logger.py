import pytest
from lib.orchestrator.execution_logger import ExecutionLogger
from lib.common_tools.sqlite_client import SQLiteClient


@pytest.fixture
def setup(tmp_path):
    """Create test database with execution_logs table."""
    db = SQLiteClient(str(tmp_path / "test.db"))
    db.conn.executescript("""
        CREATE TABLE execution_logs (
            id TEXT PRIMARY KEY,
            execution_id TEXT,
            workflow_id TEXT,
            timestamp TEXT,
            phase TEXT,
            event_type TEXT,
            tool_name TEXT,
            validator_name TEXT,
            success BOOLEAN,
            duration_ms INTEGER,
            metadata TEXT,
            error_message TEXT
        );
    """)
    logger = ExecutionLogger("exec_001", "wf_001", db)
    return logger, db


def test_phase_logging(setup):
    logger, db = setup
    logger.phase_start("Phase 1")
    logger.phase_end("Phase 1", success=True)
    logger.flush()

    logs = db.table("execution_logs").select("*").eq("execution_id", "exec_001").execute()
    assert len(logs) == 2
    assert logs[0]["event_type"] == "phase_start"
    assert logs[1]["event_type"] == "phase_end"


def test_tool_logging(setup):
    logger, db = setup
    logger.tool_call("my_tool", {"param": "value"})
    logger.tool_result("my_tool", {"data": "result"}, success=True, duration_ms=150)
    logger.flush()

    logs = db.table("execution_logs").select("*").eq("tool_name", "my_tool").execute()
    assert len(logs) == 2
    assert logs[0]["event_type"] == "tool_call"
    assert logs[1]["event_type"] == "tool_result"


def test_validation_logging(setup):
    logger, db = setup
    logger.validation_event("my_validator", passed=True, issues=[])
    logger.flush()

    logs = db.table("execution_logs").select("*").eq("validator_name", "my_validator").execute()
    assert len(logs) == 1
    assert logs[0]["event_type"] == "validation"
    assert logs[0]["success"] == 1  # SQLite stores booleans as integers


def test_error_logging(setup):
    logger, db = setup
    logger.error("Something went wrong", {"context": "data"})
    logger.flush()

    logs = db.table("execution_logs").select("*").eq("event_type", "error").execute()
    assert len(logs) == 1
    assert logs[0]["success"] == 0  # SQLite stores booleans as integers
    assert logs[0]["error_message"] == "Something went wrong"
