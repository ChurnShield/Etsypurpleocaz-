import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(_here)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_validator import BaseValidator


class ResearchEnrichedValidator(BaseValidator):
    """Validates that opportunities were enriched with NotebookLM research.

    Allows pass-through when NotebookLM is unavailable (graceful degradation).
    """

    def validate(self, data, context=None):
        issues = []

        # Data should be a list of opportunities
        if not isinstance(data, list):
            return {
                "passed": False,
                "issues": ["Expected a list of opportunities"],
                "needs_more": False,
                "validator_name": self.get_name(),
                "metadata": {},
            }

        if not data:
            issues.append("No opportunities in research output")
            return {
                "passed": False,
                "issues": issues,
                "needs_more": False,
                "validator_name": self.get_name(),
                "metadata": {"total": 0},
            }

        # Count enriched opportunities
        enriched = sum(1 for opp in data if opp.get("research_context"))
        total = len(data)
        rate = enriched / total if total > 0 else 0

        min_rate = (context or {}).get("min_enrichment_rate", 0.0)

        # If no enrichment happened at all, that's okay (graceful degradation)
        # The tool metadata will indicate why (no CLI, no notebook, etc.)
        if enriched == 0:
            return {
                "passed": True,
                "issues": ["No opportunities enriched (NotebookLM may be unavailable)"],
                "needs_more": False,
                "validator_name": self.get_name(),
                "metadata": {"enriched": 0, "total": total, "rate": 0.0},
            }

        # If some enrichment happened, check quality
        if min_rate > 0 and rate < min_rate:
            issues.append(
                f"Enrichment rate {rate:.0%} below minimum {min_rate:.0%}"
            )

        # Check that enriched opportunities have valid research_context
        for opp in data:
            rc = opp.get("research_context")
            if rc and not rc.get("insights"):
                issues.append(
                    f"Empty insights for: {opp.get('product_title', 'unknown')[:40]}"
                )

        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "needs_more": len(issues) > 0 and rate > 0,
            "validator_name": self.get_name(),
            "metadata": {"enriched": enriched, "total": total, "rate": rate},
        }
