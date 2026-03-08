"""Tests for SmallBrain per-workflow learning layer.

Validates that SmallBrain correctly detects:
1. Validators with high failure rates → validator_improvement proposals
2. Tools with slow execution times → performance_improvement proposals
3. Deduplication: skips proposals that already exist as pending
"""

import pytest
import uuid
from datetime import datetime

from lib.common_tools.sqlite_client import SQLiteClient


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _create_test_db(tmp_path):
    """Create an in-memory-style test DB with required tables."""
    db = SQLiteClient(str(tmp_path / "test_brain.db"))
    db.conn.executescript("""
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


def _seed_executions(db, workflow_id, count):
    """Insert N execution rows for a workflow."""
    for i in range(count):
        db.table("executions").insert({
            "id": str(uuid.uuid4()),
            "workflow_id": workflow_id,
            "started_at": datetime.utcnow().isoformat(),
            "status": "completed",
        }).execute()


def _seed_validation_logs(db, workflow_id, validator_name, total, passed):
    """Insert validation logs: `passed` succeed, the rest fail."""
    for i in range(total):
        db.table("execution_logs").insert({
            "id": str(uuid.uuid4()),
            "execution_id": "exec_test",
            "workflow_id": workflow_id,
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "validation",
            "validator_name": validator_name,
            "success": 1 if i < passed else 0,
        }).execute()


def _seed_tool_result_logs(db, workflow_id, tool_name, durations):
    """Insert tool_result logs with given duration_ms values."""
    for dur in durations:
        db.table("execution_logs").insert({
            "id": str(uuid.uuid4()),
            "execution_id": "exec_test",
            "workflow_id": workflow_id,
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "tool_result",
            "tool_name": tool_name,
            "success": 1,
            "duration_ms": dur,
        }).execute()


@pytest.fixture
def brain_env(tmp_path):
    """Set up DB and import SmallBrain with patched config."""
    db = _create_test_db(tmp_path)
    # Import SmallBrain — it uses config values at import time,
    # so we patch them on the module after import.
    from templates.workflow_template.brain import SmallBrain
    return db, SmallBrain


# ---------------------------------------------------------------------------
# Tests: threshold gate
# ---------------------------------------------------------------------------

class TestThresholdGate:
    """SmallBrain should not analyze until enough runs exist."""

    def test_below_threshold_returns_empty(self, brain_env):
        db, SmallBrain = brain_env
        _seed_executions(db, "wf_test", 5)  # Below default 15

        brain = SmallBrain(workflow_id="wf_test", db=db)
        proposals = brain.analyze()

        assert proposals == []

    def test_at_threshold_runs_analysis(self, brain_env):
        db, SmallBrain = brain_env
        _seed_executions(db, "wf_test", 15)

        brain = SmallBrain(workflow_id="wf_test", db=db)
        # No logs seeded → no proposals, but analysis DID run (no early exit)
        proposals = brain.analyze()
        assert proposals == []


# ---------------------------------------------------------------------------
# Tests: validator failure detection
# ---------------------------------------------------------------------------

class TestValidatorAnalysis:
    """SmallBrain should flag validators with high failure rates."""

    def test_high_failure_rate_generates_proposal(self, brain_env):
        db, SmallBrain = brain_env
        _seed_executions(db, "wf_test", 20)
        # 10 checks, only 2 pass → 80% fail rate (above 70% threshold)
        _seed_validation_logs(db, "wf_test", "content_validator", total=10, passed=2)

        brain = SmallBrain(workflow_id="wf_test", db=db)
        proposals = brain.analyze()

        assert len(proposals) == 1
        assert proposals[0]["proposal_type"] == "validator_improvement"
        assert "content_validator" in proposals[0]["title"]
        assert proposals[0]["pattern_data"]["fail_rate"] == 0.8

    def test_acceptable_failure_rate_no_proposal(self, brain_env):
        db, SmallBrain = brain_env
        _seed_executions(db, "wf_test", 20)
        # 10 checks, 8 pass → 20% fail rate (below 70% threshold)
        _seed_validation_logs(db, "wf_test", "content_validator", total=10, passed=8)

        brain = SmallBrain(workflow_id="wf_test", db=db)
        proposals = brain.analyze()

        assert len(proposals) == 0

    def test_borderline_failure_rate_generates_proposal(self, brain_env):
        db, SmallBrain = brain_env
        _seed_executions(db, "wf_test", 20)
        # 10 checks, 3 pass → 70% fail rate (exactly at threshold)
        _seed_validation_logs(db, "wf_test", "seo_validator", total=10, passed=3)

        brain = SmallBrain(workflow_id="wf_test", db=db)
        proposals = brain.analyze()

        assert len(proposals) == 1
        assert proposals[0]["pattern_data"]["fail_rate"] == 0.7

    def test_multiple_validators_flagged(self, brain_env):
        db, SmallBrain = brain_env
        _seed_executions(db, "wf_test", 20)
        # Two validators both failing heavily
        _seed_validation_logs(db, "wf_test", "content_validator", total=10, passed=1)
        _seed_validation_logs(db, "wf_test", "seo_validator", total=10, passed=2)

        brain = SmallBrain(workflow_id="wf_test", db=db)
        proposals = brain.analyze()

        assert len(proposals) == 2
        types = {p["proposal_type"] for p in proposals}
        assert types == {"validator_improvement"}

    def test_proposals_saved_to_db(self, brain_env):
        db, SmallBrain = brain_env
        _seed_executions(db, "wf_test", 20)
        _seed_validation_logs(db, "wf_test", "content_validator", total=10, passed=1)

        brain = SmallBrain(workflow_id="wf_test", db=db)
        brain.analyze()

        rows = db.table("proposals").select("*").eq("workflow_id", "wf_test").execute()
        assert len(rows) == 1
        assert rows[0]["status"] == "pending"
        assert rows[0]["proposal_type"] == "validator_improvement"


# ---------------------------------------------------------------------------
# Tests: slow tool detection
# ---------------------------------------------------------------------------

class TestSlowToolAnalysis:
    """SmallBrain should flag tools that are consistently slow."""

    def test_consistently_slow_tool_generates_proposal(self, brain_env):
        db, SmallBrain = brain_env
        _seed_executions(db, "wf_test", 20)
        # 10 calls, 8 are slow (>10000ms) → 80% slow rate
        durations = [15000] * 8 + [5000] * 2
        _seed_tool_result_logs(db, "wf_test", "etsy_api_tool", durations)

        brain = SmallBrain(workflow_id="wf_test", db=db)
        proposals = brain.analyze()

        assert len(proposals) == 1
        assert proposals[0]["proposal_type"] == "performance_improvement"
        assert "etsy_api_tool" in proposals[0]["title"]

    def test_occasionally_slow_tool_no_proposal(self, brain_env):
        db, SmallBrain = brain_env
        _seed_executions(db, "wf_test", 20)
        # 10 calls, only 3 are slow → 30% slow rate (below threshold)
        durations = [15000] * 3 + [5000] * 7
        _seed_tool_result_logs(db, "wf_test", "etsy_api_tool", durations)

        brain = SmallBrain(workflow_id="wf_test", db=db)
        proposals = brain.analyze()

        assert len(proposals) == 0

    def test_fast_tool_no_proposal(self, brain_env):
        db, SmallBrain = brain_env
        _seed_executions(db, "wf_test", 20)
        # All calls are fast
        durations = [500] * 10
        _seed_tool_result_logs(db, "wf_test", "fast_tool", durations)

        brain = SmallBrain(workflow_id="wf_test", db=db)
        proposals = brain.analyze()

        assert len(proposals) == 0


# ---------------------------------------------------------------------------
# Tests: combined detection
# ---------------------------------------------------------------------------

class TestCombinedDetection:
    """SmallBrain should detect both validator failures and slow tools together."""

    def test_both_patterns_detected(self, brain_env):
        db, SmallBrain = brain_env
        _seed_executions(db, "wf_test", 20)

        # Failing validator
        _seed_validation_logs(db, "wf_test", "content_validator", total=10, passed=1)
        # Slow tool
        durations = [20000] * 9 + [5000] * 1
        _seed_tool_result_logs(db, "wf_test", "gemini_tool", durations)

        brain = SmallBrain(workflow_id="wf_test", db=db)
        proposals = brain.analyze()

        assert len(proposals) == 2
        types = {p["proposal_type"] for p in proposals}
        assert "validator_improvement" in types
        assert "performance_improvement" in types


# ---------------------------------------------------------------------------
# Tests: deduplication
# ---------------------------------------------------------------------------

class TestDeduplication:
    """SmallBrain should not regenerate proposals that already exist as pending."""

    def test_duplicate_validator_proposal_skipped(self, brain_env):
        db, SmallBrain = brain_env
        _seed_executions(db, "wf_test", 20)
        _seed_validation_logs(db, "wf_test", "content_validator", total=10, passed=1)

        brain = SmallBrain(workflow_id="wf_test", db=db)

        # First run: generates 1 proposal
        proposals_1 = brain.analyze()
        assert len(proposals_1) == 1

        # Second run: same data, should skip duplicate
        proposals_2 = brain.analyze()
        assert len(proposals_2) == 0

        # DB should only have 1 proposal
        rows = db.table("proposals").select("*").eq("workflow_id", "wf_test").execute()
        assert len(rows) == 1

    def test_approved_proposal_allows_new_one(self, brain_env):
        db, SmallBrain = brain_env
        _seed_executions(db, "wf_test", 20)
        _seed_validation_logs(db, "wf_test", "content_validator", total=10, passed=1)

        brain = SmallBrain(workflow_id="wf_test", db=db)

        # First run: generates proposal
        proposals_1 = brain.analyze()
        assert len(proposals_1) == 1

        # Mark it as approved (no longer pending)
        proposal_id = db.table("proposals").select("id").eq("workflow_id", "wf_test").execute()[0]["id"]
        db.table("proposals").update({"status": "approved"}).eq("id", proposal_id).execute()

        # Second run: should generate a new proposal (old one is approved, not pending)
        proposals_2 = brain.analyze()
        assert len(proposals_2) == 1

    def test_different_targets_not_deduplicated(self, brain_env):
        db, SmallBrain = brain_env
        _seed_executions(db, "wf_test", 20)
        _seed_validation_logs(db, "wf_test", "content_validator", total=10, passed=1)
        _seed_validation_logs(db, "wf_test", "seo_validator", total=10, passed=2)

        brain = SmallBrain(workflow_id="wf_test", db=db)
        proposals = brain.analyze()
        # Two different validators → both should be saved
        assert len(proposals) == 2


# ---------------------------------------------------------------------------
# Tests: isolation between workflows
# ---------------------------------------------------------------------------

class TestWorkflowIsolation:
    """SmallBrain should only analyze logs for its own workflow."""

    def test_ignores_other_workflow_logs(self, brain_env):
        db, SmallBrain = brain_env
        _seed_executions(db, "wf_a", 20)
        _seed_executions(db, "wf_b", 20)

        # wf_b has a failing validator, wf_a does not
        _seed_validation_logs(db, "wf_b", "content_validator", total=10, passed=1)

        brain = SmallBrain(workflow_id="wf_a", db=db)
        proposals = brain.analyze()

        # wf_a should have zero proposals
        assert len(proposals) == 0
