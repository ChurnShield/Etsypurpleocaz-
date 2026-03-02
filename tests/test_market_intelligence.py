# =============================================================================
# tests/test_market_intelligence.py
# =============================================================================

import sys
import os
import pytest

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _project_root)
sys.path.insert(0, os.path.join(_project_root, "workflows", "market_intelligence"))

from workflows.market_intelligence.validators.social_trends_validator import SocialTrendsValidator
from workflows.market_intelligence.validators.enrichment_validator import EnrichmentValidator
from workflows.market_intelligence.validators.scoring_validator import ScoringValidator
from workflows.market_intelligence.validators.report_saved_validator import ReportSavedValidator


# ── SocialTrendsValidator ──────────────────────────────────────────────────

class TestSocialTrendsValidator:
    def setup_method(self):
        self.v = SocialTrendsValidator()

    def test_passes_with_signals(self):
        data = {
            "trend_signals": [{"keyword": "tattoo gift", "signal_score": 80}],
            "sources_summary": {"google_trends": 1, "reddit": 0},
        }
        result = self.v.validate(data)
        assert result["passed"] is True
        assert result["issues"] == []

    def test_fails_empty_signals(self):
        data = {"trend_signals": [], "sources_summary": {"google_trends": 0, "reddit": 0}}
        result = self.v.validate(data)
        assert result["passed"] is False
        assert len(result["issues"]) > 0

    def test_fails_not_dict(self):
        result = self.v.validate("bad")
        assert result["passed"] is False

    def test_return_format(self):
        result = self.v.validate({})
        for key in ("passed", "issues", "needs_more", "validator_name", "metadata"):
            assert key in result


# ── EnrichmentValidator ────────────────────────────────────────────────────

class TestEnrichmentValidator:
    def setup_method(self):
        self.v = EnrichmentValidator()

    def test_passes_with_pricing(self):
        data = {
            "enriched_signals": [{"avg_competitor_price": 5.99}],
            "enrichment_stats": {"enriched": 1, "errors": 0},
        }
        result = self.v.validate(data)
        assert result["passed"] is True

    def test_fails_no_pricing(self):
        data = {
            "enriched_signals": [{"avg_competitor_price": 0}],
            "enrichment_stats": {"enriched": 1, "errors": 0},
        }
        result = self.v.validate(data)
        assert result["passed"] is False

    def test_no_retry(self):
        result = self.v.validate({"enriched_signals": [], "enrichment_stats": {}})
        assert result["needs_more"] is False


# ── ScoringValidator ───────────────────────────────────────────────────────

class TestScoringValidator:
    def setup_method(self):
        self.v = ScoringValidator()

    def test_passes_with_scores(self):
        data = {
            "scored_opportunities": [
                {"opportunity_score": 85, "product_suggestion": "Test Title"},
            ],
        }
        result = self.v.validate(data)
        assert result["passed"] is True

    def test_fails_empty(self):
        result = self.v.validate({"scored_opportunities": []})
        assert result["passed"] is False

    def test_fails_missing_scores(self):
        data = {
            "scored_opportunities": [
                {"product_suggestion": "No score here"},
                {"product_suggestion": "Also no score"},
            ],
        }
        result = self.v.validate(data)
        assert result["passed"] is False

    def test_retry_on_malformed(self):
        result = self.v.validate({"scored_opportunities": []})
        assert result["needs_more"] is True


# ── ReportSavedValidator ──────────────────────────────────────────────────

class TestReportSavedValidator:
    def setup_method(self):
        self.v = ReportSavedValidator()

    def test_passes_with_rows(self):
        result = self.v.validate({"rows_written": 10})
        assert result["passed"] is True

    def test_fails_zero_rows(self):
        result = self.v.validate({"rows_written": 0})
        assert result["passed"] is False

    def test_no_retry(self):
        result = self.v.validate({"rows_written": 0})
        assert result["needs_more"] is False
