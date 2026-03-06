# =============================================================================
# workflows/market_intelligence/validators/report_saved_validator.py
# =============================================================================

import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(_here)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_validator import BaseValidator


class ReportSavedValidator(BaseValidator):
    """Validate that Phase 4 saved data to Sheets."""

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

        if data.get("rows_written", 0) == 0:
            issues.append("No rows written to Market Intelligence sheet")

        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "needs_more": False,  # No retry for sheet save
            "validator_name": self.get_name(),
            "metadata": {"rows_written": data.get("rows_written", 0)},
        }
