# =============================================================================
# workflows/market_intelligence/validators/enrichment_validator.py
# =============================================================================

import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(_here)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_validator import BaseValidator


class EnrichmentValidator(BaseValidator):
    """Validate that Phase 2 enriched signals with competitor data."""

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

        enriched = data.get("enriched_signals", [])
        if not enriched:
            issues.append("No enriched signals returned")
        else:
            # Check at least some have actual pricing data
            has_pricing = sum(
                1 for s in enriched
                if s.get("avg_competitor_price", 0) > 0
            )
            if has_pricing == 0:
                issues.append("No competitor pricing data found for any signal")

        stats = data.get("enrichment_stats", {})
        error_count = stats.get("errors", 0)
        enriched_count = stats.get("enriched", 0)

        if enriched_count > 0 and error_count > enriched_count:
            issues.append(
                f"More errors ({error_count}) than successful enrichments ({enriched_count})"
            )

        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "needs_more": False,  # No retry -- API data is what it is
            "validator_name": self.get_name(),
            "metadata": {
                "enriched_count": len(enriched),
                "has_pricing": has_pricing if enriched else 0,
                "error_count": error_count,
            },
        }
