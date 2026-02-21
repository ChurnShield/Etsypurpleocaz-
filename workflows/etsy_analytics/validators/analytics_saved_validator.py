# =============================================================================
# workflows/etsy_analytics/validators/analytics_saved_validator.py
#
# Validates Phase 3 output — checks that data was written to Google Sheets.
# needs_more = False: retrying would create duplicate snapshot rows.
# =============================================================================

import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
_workflow = os.path.dirname(_here)
_project_root = os.path.dirname(os.path.dirname(_workflow))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_validator import BaseValidator


class AnalyticsSavedValidator(BaseValidator):

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

        listings_saved = data.get("listings_saved", 0)
        if listings_saved == 0:
            issues.append("No listings written to sheet")

        passed = len(issues) == 0

        return {
            "passed":         passed,
            "issues":         issues,
            "needs_more":     False,
            "validator_name": self.get_name(),
            "metadata": {
                "snapshot_added":  data.get("snapshot_added", False),
                "listings_saved":  listings_saved,
                "top_rows_saved":  data.get("top_rows_saved", 0),
            },
        }
