# =============================================================================
# workflows/market_intelligence/validators/scoring_validator.py
# =============================================================================

import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(_here)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_validator import BaseValidator


class ScoringValidator(BaseValidator):
    """Validate that Phase 3 produced scored opportunities."""

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

        opportunities = data.get("scored_opportunities", [])
        if not opportunities:
            issues.append("No scored opportunities produced")
        else:
            scored = [
                o for o in opportunities
                if isinstance(o.get("opportunity_score"), (int, float))
            ]
            if len(scored) < len(opportunities) * 0.5:
                issues.append(
                    f"Only {len(scored)}/{len(opportunities)} have valid scores"
                )

            titled = [o for o in opportunities if o.get("product_suggestion")]
            if len(titled) < len(opportunities) * 0.5:
                issues.append(
                    f"Only {len(titled)}/{len(opportunities)} have product suggestions"
                )

        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "needs_more": len(issues) > 0,  # Retry if Claude output malformed
            "validator_name": self.get_name(),
            "metadata": {"opportunity_count": len(opportunities)},
        }
