import pytest
from lib.common_tools.sqlite_client import SQLiteClient


@pytest.fixture
def db(tmp_path):
    """Create a fresh test database."""
    client = SQLiteClient(str(tmp_path / "test.db"))
    client.conn.execute("""
        CREATE TABLE executions (
            id TEXT PRIMARY KEY,
            workflow_id TEXT,
            status TEXT
        )
    """)
    return client


def test_insert_and_query(db):
    db.table("executions").insert({
        "id": "test_123",
        "workflow_id": "test_workflow",
        "status": "running"
    }).execute()

    result = db.table("executions").select("*").eq("id", "test_123").execute()
    assert len(result) == 1
    assert result[0]["status"] == "running"


def test_update(db):
    db.table("executions").insert({
        "id": "test_456",
        "workflow_id": "test_workflow",
        "status": "running"
    }).execute()

    db.table("executions").update({"status": "completed"}).eq("id", "test_456").execute()
    result = db.table("executions").select("*").eq("id", "test_456").execute()
    assert result[0]["status"] == "completed"


def test_delete(db):
    db.table("executions").insert({
        "id": "test_789",
        "workflow_id": "test_workflow",
        "status": "failed"
    }).execute()

    db.table("executions").delete().eq("id", "test_789").execute()
    result = db.table("executions").select("*").eq("id", "test_789").execute()
    assert len(result) == 0


def test_filter_by_workflow(db):
    db.table("executions").insert({"id": "a", "workflow_id": "wf1", "status": "completed"}).execute()
    db.table("executions").insert({"id": "b", "workflow_id": "wf2", "status": "completed"}).execute()
    db.table("executions").insert({"id": "c", "workflow_id": "wf1", "status": "failed"}).execute()

    result = db.table("executions").select("*").eq("workflow_id", "wf1").execute()
    assert len(result) == 2


def test_empty_query_returns_empty_list(db):
    result = db.table("executions").select("*").eq("id", "nonexistent").execute()
    assert result == []
