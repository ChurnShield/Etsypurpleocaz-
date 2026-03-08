"""Tests for ProposalFeedbackTracker — the self-improvement learning loop.

Validates:
1. Before/after metric snapshots are captured correctly
2. Outcome recording works with auto-scoring
3. Effectiveness stats aggregate properly
4. Target history lookups find the right proposals
5. Success rate queries work per proposal type
"""

import pytest
import uuid
import json
from datetime import datetime

from lib.common_tools.sqlite_client import SQLiteClient


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _create_test_db(tmp_path):
    """Create a test DB with required tables + feedback columns."""
    db = SQLiteClient(str(tmp_path / "test_feedback.db"))
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
            applied_by TEXT,
            outcome TEXT,
            outcome_notes TEXT,
            metric_before TEXT,
            metric_after TEXT,
            resolved_at DATETIME,
            feedback_score REAL
        );
    """)
    return db


def _insert_proposal(db, proposal_id=None, workflow_id="wf_test",
                      proposal_type="validator_improvement", target="content_validator",
                      status="pending", outcome=None, feedback_score=None,
                      metric_before=None, metric_after=None):
    """Insert a proposal for testing."""
    pid = proposal_id or str(uuid.uuid4())
    db.table("proposals").insert({
        "id": pid,
        "workflow_id": workflow_id,
        "generated_at": datetime.utcnow().isoformat(),
        "status": status,
        "proposal_type": proposal_type,
        "title": f"Test proposal for {target}",
        "description": f"Testing {target}",
        "pattern_data": json.dumps({"target": target}),
        "proposed_changes": json.dumps({"action": "review", "target": target}),
        "outcome": outcome,
        "feedback_score": feedback_score,
        "metric_before": json.dumps(metric_before) if metric_before else None,
        "metric_after": json.dumps(metric_after) if metric_after else None,
    }).execute()
    return pid


def _seed_validation_logs(db, workflow_id, validator_name, total, passed):
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


def _seed_tool_logs(db, workflow_id, tool_name, durations):
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
def tracker_env(tmp_path):
    db = _create_test_db(tmp_path)
    from lib.big_brain.feedback_tracker import ProposalFeedbackTracker
    tracker = ProposalFeedbackTracker(db=db)
    return tracker, db


# ---------------------------------------------------------------------------
# Tests: metric snapshots
# ---------------------------------------------------------------------------

class TestMetricSnapshots:

    def test_snapshot_before_validator(self, tracker_env):
        tracker, db = tracker_env
        pid = _insert_proposal(db, proposal_type="validator_improvement",
                                target="content_validator")
        _seed_validation_logs(db, "wf_test", "content_validator", total=10, passed=3)

        metrics = tracker.snapshot_before(pid, "wf_test")

        assert metrics["validator_name"] == "content_validator"
        assert metrics["total_checks"] == 10
        assert metrics["pass_rate"] == 0.3
        assert metrics["fail_rate"] == 0.7

        # Verify saved to DB
        row = db.table("proposals").select("metric_before").eq("id", pid).execute()[0]
        saved = json.loads(row["metric_before"])
        assert saved["fail_rate"] == 0.7

    def test_snapshot_before_performance(self, tracker_env):
        tracker, db = tracker_env
        pid = _insert_proposal(db, proposal_type="performance_improvement",
                                target="etsy_api_tool")
        _seed_tool_logs(db, "wf_test", "etsy_api_tool", [15000, 12000, 18000])

        metrics = tracker.snapshot_before(pid, "wf_test")

        assert metrics["tool_name"] == "etsy_api_tool"
        assert metrics["total_calls"] == 3
        assert metrics["avg_duration_ms"] == 15000

    def test_snapshot_after_captures_improvement(self, tracker_env):
        tracker, db = tracker_env
        pid = _insert_proposal(db, proposal_type="validator_improvement",
                                target="content_validator")
        _seed_validation_logs(db, "wf_test", "content_validator", total=10, passed=8)

        metrics = tracker.snapshot_after(pid, "wf_test")

        assert metrics["pass_rate"] == 0.8
        row = db.table("proposals").select("metric_after").eq("id", pid).execute()[0]
        saved = json.loads(row["metric_after"])
        assert saved["pass_rate"] == 0.8

    def test_snapshot_nonexistent_proposal(self, tracker_env):
        tracker, db = tracker_env
        result = tracker.snapshot_before("nonexistent_id")
        assert result == {"error": "proposal_not_found"}


# ---------------------------------------------------------------------------
# Tests: outcome recording
# ---------------------------------------------------------------------------

class TestOutcomeRecording:

    def test_record_improved_outcome(self, tracker_env):
        tracker, db = tracker_env
        pid = _insert_proposal(db)

        result = tracker.record_outcome(pid, outcome="improved", notes="Fixed it!")

        assert result["outcome"] == "improved"
        assert result["outcome_notes"] == "Fixed it!"
        assert result["resolved_at"] is not None

        row = db.table("proposals").select("outcome, outcome_notes").eq("id", pid).execute()[0]
        assert row["outcome"] == "improved"

    def test_record_with_custom_score(self, tracker_env):
        tracker, db = tracker_env
        pid = _insert_proposal(db)

        result = tracker.record_outcome(pid, outcome="improved", feedback_score=0.9)

        assert result["feedback_score"] == 0.9
        row = db.table("proposals").select("feedback_score").eq("id", pid).execute()[0]
        assert row["feedback_score"] == 0.9

    def test_auto_score_from_before_after(self, tracker_env):
        tracker, db = tracker_env
        pid = _insert_proposal(
            db,
            proposal_type="validator_improvement",
            target="content_validator",
            metric_before={"fail_rate": 0.8, "pass_rate": 0.2},
            metric_after={"fail_rate": 0.2, "pass_rate": 0.8},
        )

        result = tracker.record_outcome(pid, outcome="improved")

        # 75% improvement in fail_rate → should auto-score 1.0
        assert result["feedback_score"] == 1.0

    def test_auto_score_worsened(self, tracker_env):
        tracker, db = tracker_env
        pid = _insert_proposal(
            db,
            proposal_type="validator_improvement",
            target="content_validator",
            metric_before={"fail_rate": 0.3, "pass_rate": 0.7},
            metric_after={"fail_rate": 0.6, "pass_rate": 0.4},
        )

        result = tracker.record_outcome(pid, outcome="worsened")

        # Fail rate doubled → should auto-score -1.0
        assert result["feedback_score"] == -1.0


# ---------------------------------------------------------------------------
# Tests: effectiveness stats
# ---------------------------------------------------------------------------

class TestEffectivenessStats:

    def test_empty_stats(self, tracker_env):
        tracker, db = tracker_env
        stats = tracker.get_effectiveness_stats()
        assert stats["total_resolved"] == 0

    def test_aggregate_stats(self, tracker_env):
        tracker, db = tracker_env
        _insert_proposal(db, outcome="improved", feedback_score=0.8)
        _insert_proposal(db, outcome="improved", feedback_score=1.0)
        _insert_proposal(db, outcome="no_change", feedback_score=0.0)
        _insert_proposal(db, outcome="worsened", feedback_score=-0.5)

        stats = tracker.get_effectiveness_stats()

        assert stats["total_resolved"] == 4
        assert stats["improved"] == 2
        assert stats["no_change"] == 1
        assert stats["worsened"] == 1
        assert stats["avg_feedback_score"] == 0.325  # (0.8+1.0+0.0-0.5)/4

    def test_stats_by_type(self, tracker_env):
        tracker, db = tracker_env
        _insert_proposal(db, proposal_type="validator_improvement",
                          outcome="improved", feedback_score=1.0)
        _insert_proposal(db, proposal_type="performance_improvement",
                          outcome="no_change", feedback_score=0.0)

        stats = tracker.get_effectiveness_stats()

        assert "validator_improvement" in stats["by_type"]
        assert stats["by_type"]["validator_improvement"]["improved"] == 1
        assert stats["by_type"]["validator_improvement"]["avg_score"] == 1.0


# ---------------------------------------------------------------------------
# Tests: target history
# ---------------------------------------------------------------------------

class TestTargetHistory:

    def test_find_history_for_target(self, tracker_env):
        tracker, db = tracker_env
        _insert_proposal(db, target="content_validator", outcome="improved")
        _insert_proposal(db, target="content_validator", outcome="no_change")
        _insert_proposal(db, target="seo_validator", outcome="improved")

        history = tracker.get_history_for_target("content_validator")

        assert len(history) == 2
        outcomes = [h["outcome"] for h in history]
        assert "improved" in outcomes
        assert "no_change" in outcomes

    def test_no_history_for_unknown_target(self, tracker_env):
        tracker, db = tracker_env
        history = tracker.get_history_for_target("nonexistent_tool")
        assert len(history) == 0


# ---------------------------------------------------------------------------
# Tests: success rate queries
# ---------------------------------------------------------------------------

class TestSuccessRate:

    def test_success_rate_for_type(self, tracker_env):
        tracker, db = tracker_env
        _insert_proposal(db, proposal_type="validator_improvement", outcome="improved")
        _insert_proposal(db, proposal_type="validator_improvement", outcome="improved")
        _insert_proposal(db, proposal_type="validator_improvement", outcome="no_change")

        rate = tracker.get_success_rate_for_type("validator_improvement")
        assert rate == 0.667  # 2/3

    def test_zero_success_rate(self, tracker_env):
        tracker, db = tracker_env
        _insert_proposal(db, proposal_type="performance_improvement", outcome="worsened")

        rate = tracker.get_success_rate_for_type("performance_improvement")
        assert rate == 0.0

    def test_no_resolved_proposals(self, tracker_env):
        tracker, db = tracker_env
        rate = tracker.get_success_rate_for_type("validator_improvement")
        assert rate == 0.0
