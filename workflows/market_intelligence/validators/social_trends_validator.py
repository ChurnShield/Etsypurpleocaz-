# =============================================================================
# workflows/market_intelligence/validators/social_trends_validator.py
# =============================================================================

import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(_here)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_validator import BaseValidator


class SocialTrendsValidator(BaseValidator):
    """Validate that Phase 1 produced usable trend signals."""

    def validate(self, data, context=None):
        issues = []

        if not isinstance(data, dict):
            return {
                "passed": False,
                "issues": [f"Expected dict, got {type(data).__name__}"],
                "needs_more": False,
                "validator_name": self.get_name(),
                "metadata": {},
            }

        signals = data.get("trend_signals", [])
        if not signals:
            issues.append("No trend signals collected from any source")

        sources = data.get("sources_summary", {})
        google_count = sources.get("google_trends", 0)
        reddit_count = sources.get("reddit", 0)

        if google_count == 0 and reddit_count == 0:
            issues.append("Both Google Trends and Reddit returned zero signals")

        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "needs_more": len(issues) > 0,
            "validator_name": self.get_name(),
            "metadata": {
                "signal_count": len(signals),
                "google_count": google_count,
                "reddit_count": reddit_count,
            },
        }
