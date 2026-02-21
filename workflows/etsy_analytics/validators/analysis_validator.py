# =============================================================================
# workflows/etsy_analytics/validators/analysis_validator.py
#
# Validates Phase 2 output — checks that analysis produced a snapshot
# and meaningful data.
# =============================================================================

import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
_workflow = os.path.dirname(_here)
_project_root = os.path.dirname(os.path.dirname(_workflow))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_validator import BaseValidator


class AnalysisValidator(BaseValidator):

    def validate(self, data, context=None):
        issues = []

        if not isinstance(data, dict):
            return {
                "passed": False,
                "issues": ["Data is not a dict"],
                "needs_more": False,
                "validator_name": self.get_name(),
                "metadata": {},
            }

        snapshot = data.get("snapshot", {})
        if not snapshot:
            issues.append("No snapshot data produced")

        if not snapshot.get("date"):
            issues.append("Snapshot missing date")

        listings = data.get("listings", [])
        if not listings:
            issues.append("No listing data in analysis")

        passed = len(issues) == 0

        return {
            "passed":         passed,
            "issues":         issues,
            "needs_more":     False,
            "validator_name": self.get_name(),
            "metadata": {
                "has_snapshot":    bool(snapshot),
                "listing_count":   len(listings),
                "top_views_count": len(data.get("top_by_views", [])),
            },
        }
