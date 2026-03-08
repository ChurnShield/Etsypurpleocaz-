"""Tests for BigBrain system-wide health monitoring.

Validates that BigBrain correctly detects:
1. System-wide failure rates (critical / degraded / healthy)
2. Recurring errors across workflows
3. API key / authentication failures
4. Security events (unauthorized access, data corruption, crashes)
5. Cross-workflow patterns
6. Caching behaviour
"""

import pytest
import uuid
import time
from datetime import datetime, timedelta
from unittest.mock import patch

from lib.common_tools.sqlite_client import SQLiteClient


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _create_test_db(tmp_path):
    """Create a test DB with all required tables."""
    db = SQLiteClient(str(tmp_path / "test_big_brain.db"))
    db.conn.executescript("""
        CREATE TABLE IF NOT EXISTS workflows (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            domain TEXT,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            total_runs INTEGER DEFAULT 0,
            successful_runs INTEGER DEFAULT 0,
            failed_runs INTEGER DEFAULT 0,
            avg_duration_ms INTEGER,
            last_run_at DATETIME
        );

        CREATE TABLE IF NOT EXISTS executions (
            id TEXT PRIMARY KEY,
            workflow_id TEXT NOT NULL,
            started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            completed_at DATETIME,
            status TEXT,
            outcome_quality FLOAT,
            input_summary TEXT,
            output_summary TEXT,
            error_message TEXT,
            metadata TEXT
        );

        CREATE TABLE IF NOT EXISTS execution_logs (
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

        CREATE TABLE IF NOT EXISTS proposals (
            id TEXT PRIMARY KEY,
            workflow_id TEXT,
            generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT,
            proposal_type TEXT,
            title TEXT,
            description TEXT,
            pattern_data TEXT,
            proposed_changes TEXT,
            applied_at DATETIME,
            applied_by TEXT
        );
    """)
    return db


def _now_iso():
    return datetime.utcnow().isoformat()


def _seed_execution(db, workflow_id, status="completed", error_message=None):
    """Insert one execution row."""
    db.table("executions").insert({
        "id": str(uuid.uuid4()),
        "workflow_id": workflow_id,
        "started_at": _now_iso(),
        "status": status,
        "error_message": error_message,
    }).execute()


def _seed_error_log(db, workflow_id, error_message):
    """Insert an error event into execution_logs."""
    db.table("execution_logs").insert({
        "id": str(uuid.uuid4()),
        "execution_id": "exec_test",
        "workflow_id": workflow_id,
        "timestamp": _now_iso(),
        "event_type": "error",
        "error_message": error_message,
        "success": 0,
    }).execute()


def _create_workflow_dirs(tmp_path, workflow_names):
    """Create minimal workflow directories with run.py files."""
    workflows_dir = tmp_path / "workflows"
    workflows_dir.mkdir(exist_ok=True)
    for name in workflow_names:
        wf_dir = workflows_dir / name
        wf_dir.mkdir(exist_ok=True)
        (wf_dir / "run.py").write_text("# workflow\n")
    return str(workflows_dir)


@pytest.fixture
def brain_setup(tmp_path):
    """Create DB, workflow dirs, and return a BigBrain constructor."""
    db = _create_test_db(tmp_path)
    workflows_dir = _create_workflow_dirs(tmp_path, ["wf_a", "wf_b", "wf_c"])

    from lib.big_brain.brain import BigBrain
    brain = BigBrain(workflows_dir=workflows_dir, db_client=db)
    # Override the workflows_dir since BigBrain prepends project root
    brain.workflows_dir = workflows_dir
    brain._workflows = brain.discover_workflows()
    return brain, db


# ---------------------------------------------------------------------------
# Tests: healthy system
# ---------------------------------------------------------------------------

class TestHealthySystem:

    def test_no_executions_is_healthy(self, brain_setup):
        brain, db = brain_setup
        health = brain.analyze_system_health()
        assert health.status == "healthy"
        assert health.total_executions_24h == 0
        assert health.problems == []

    def test_all_successful_is_healthy(self, brain_setup):
        brain, db = brain_setup
        for _ in range(10):
            _seed_execution(db, "wf_a", status="completed")
        health = brain.analyze_system_health()
        assert health.status == "healthy"
        assert health.system_failure_rate == 0.0


# ---------------------------------------------------------------------------
# Tests: failure rate detection
# ---------------------------------------------------------------------------

class TestFailureRateDetection:

    def test_critical_failure_rate(self, brain_setup):
        brain, db = brain_setup
        # 10 executions, 6 failed → 60% (above 50% critical threshold)
        for _ in range(4):
            _seed_execution(db, "wf_a", status="completed")
        for _ in range(6):
            _seed_execution(db, "wf_a", status="failed")

        health = brain.analyze_system_health()
        assert health.status == "critical"
        assert health.system_failure_rate == 0.6
        critical_problems = [
            p for p in health.problems
            if p["category"] == "system_failure_rate" and p["severity"] == "critical"
        ]
        assert len(critical_problems) == 1

    def test_degraded_failure_rate(self, brain_setup):
        brain, db = brain_setup
        # 10 executions, 3 failed → 30% (above 25% degraded, below 50% critical)
        for _ in range(7):
            _seed_execution(db, "wf_a", status="completed")
        for _ in range(3):
            _seed_execution(db, "wf_a", status="failed")

        health = brain.analyze_system_health()
        assert health.status == "degraded"
        assert health.system_failure_rate == 0.3


# ---------------------------------------------------------------------------
# Tests: recurring error detection
# ---------------------------------------------------------------------------

class TestRecurringErrors:

    def test_recurring_error_detected(self, brain_setup):
        brain, db = brain_setup
        # Same error 12 times (threshold is 10)
        for _ in range(12):
            _seed_error_log(db, "wf_a", "ConnectionError: Etsy API timeout")

        health = brain.analyze_system_health()
        recurring = [
            p for p in health.problems if p["category"] == "recurring_error"
        ]
        assert len(recurring) == 1
        assert recurring[0]["severity"] == "high"

    def test_below_threshold_not_flagged(self, brain_setup):
        brain, db = brain_setup
        # Same error 5 times (below threshold of 10)
        for _ in range(5):
            _seed_error_log(db, "wf_a", "ConnectionError: timeout")

        health = brain.analyze_system_health()
        recurring = [
            p for p in health.problems if p["category"] == "recurring_error"
        ]
        assert len(recurring) == 0


# ---------------------------------------------------------------------------
# Tests: security event detection
# ---------------------------------------------------------------------------

class TestSecurityEvents:

    def test_api_auth_failures_detected(self, brain_setup):
        brain, db = brain_setup
        for _ in range(5):
            _seed_error_log(db, "wf_a", "401 Unauthorized: invalid API key")

        health = brain.analyze_system_health()
        api_problems = [
            p for p in health.problems if p["category"] == "api_key_failure"
        ]
        assert len(api_problems) == 1

    def test_unauthorized_access_detected(self, brain_setup):
        brain, db = brain_setup
        _seed_error_log(db, "wf_b", "unauthorized access attempt from unknown IP")

        health = brain.analyze_system_health()
        security = [
            p for p in health.problems if p["category"] == "unauthorized_access"
        ]
        assert len(security) == 1
        assert security[0]["severity"] == "critical"

    def test_data_corruption_detected(self, brain_setup):
        brain, db = brain_setup
        _seed_error_log(db, "wf_a", "database disk image is malformed")

        health = brain.analyze_system_health()
        corruption = [
            p for p in health.problems if p["category"] == "data_corruption"
        ]
        assert len(corruption) == 1
        assert corruption[0]["severity"] == "critical"

    def test_crash_detected(self, brain_setup):
        brain, db = brain_setup
        _seed_error_log(db, "wf_a", "fatal: unhandled exception in main loop")

        health = brain.analyze_system_health()
        crashes = [
            p for p in health.problems if p["category"] == "system_crash"
        ]
        assert len(crashes) == 1
        assert crashes[0]["severity"] == "critical"


# ---------------------------------------------------------------------------
# Tests: caching
# ---------------------------------------------------------------------------

class TestCaching:

    def test_cache_returns_same_result(self, brain_setup):
        brain, db = brain_setup
        health1 = brain.analyze_system_health()
        health2 = brain.analyze_system_health()
        # Should be the exact same object (cached)
        assert health1 is health2

    def test_cache_expires(self, brain_setup):
        brain, db = brain_setup
        # Set cache TTL to 0 to force expiry
        brain._cache._ttl = 0
        health1 = brain.analyze_system_health()
        time.sleep(0.1)
        health2 = brain.analyze_system_health()
        # Different objects (cache expired)
        assert health1 is not health2


# ---------------------------------------------------------------------------
# Tests: workflow stats
# ---------------------------------------------------------------------------

class TestWorkflowStats:

    def test_per_workflow_stats_computed(self, brain_setup):
        brain, db = brain_setup
        for _ in range(5):
            _seed_execution(db, "wf_a", status="completed")
        for _ in range(3):
            _seed_execution(db, "wf_b", status="failed")

        health = brain.analyze_system_health()
        assert "wf_a" in health.workflow_stats
        assert "wf_b" in health.workflow_stats
        assert health.workflow_stats["wf_a"]["failed"] == 0
        assert health.workflow_stats["wf_b"]["failed"] == 3


# ---------------------------------------------------------------------------
# Tests: timeout detection
# ---------------------------------------------------------------------------

class TestTimeoutDetection:

    def test_timeout_pattern_detected(self, brain_setup):
        brain, db = brain_setup
        for _ in range(6):
            _seed_error_log(db, "wf_a", "TimeoutError: operation timed out after 120s")

        health = brain.analyze_system_health()
        timeouts = [
            p for p in health.problems if p["category"] == "timeout_pattern"
        ]
        assert len(timeouts) == 1
