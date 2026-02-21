# =============================================================================
# workflows/ai_news_rss/validators/google_sheets_save_validator.py
#
# GoogleSheetsSaveValidator — validates Phase 3 (SaveToGoogleSheetsTool) output.
#
# What it checks
# --------------
# 1. saved_count > 0  (unless total_input was 0 — nothing to save is fine).
# 2. saved_count == total_input  (no silent partial failures).
#
# Why needs_more = False
# ----------------------
# Retrying would DUPLICATE rows in the sheet.  Better to fail loudly so
# the operator can check the sheet and fix credentials / permissions.
# =============================================================================

import sys
import os

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_here = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(_here)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_validator import BaseValidator


class GoogleSheetsSaveValidator(BaseValidator):
    """
    Confirms that SaveToGoogleSheetsTool appended all articles successfully.

    Passes immediately when total_input is 0 — nothing to save is fine.
    Fails if saved_count does not match total_input.
    """

    def validate(self, data: dict, context: dict = None) -> dict:
        """
        Parameters
        ----------
        data : dict   result["data"] from SaveToGoogleSheetsTool.
                      Expected shape: {"saved_count": int, "total_input": int}
        """
        issues = []

        if data is None:
            issues.append(
                "SaveToGoogleSheetsTool returned no data — "
                "the tool may have crashed silently."
            )
            return {
                "passed":         False,
                "issues":         issues,
                "needs_more":     False,
                "validator_name": self.get_name(),
                "metadata":       {},
            }

        saved_count = data.get("saved_count", 0)
        total_input = data.get("total_input", 0)

        # "Nothing to save" is always a valid outcome — not a failure.
        if total_input == 0:
            return {
                "passed":         True,
                "issues":         [],
                "needs_more":     False,
                "validator_name": self.get_name(),
                "metadata":       {"note": "No articles to save — skipped."},
            }

        if saved_count == 0:
            issues.append(
                "Google Sheets reported 0 rows saved. "
                "Check that: (1) GOOGLE_CREDENTIALS_FILE is correct, "
                "(2) GOOGLE_SPREADSHEET_ID is correct, "
                "(3) the Sheet is shared with your service account email."
            )
        elif saved_count < total_input:
            issues.append(
                f"Partial save: {saved_count} of {total_input} rows were written. "
                "Check the Sheets API quota and the tool error logs."
            )

        passed = len(issues) == 0

        return {
            "passed":         passed,
            "issues":         issues,
            # Never retry — would create duplicate rows in the sheet.
            "needs_more":     False,
            "validator_name": self.get_name(),
            "metadata": {
                "saved_count": saved_count,
                "total_input": total_input,
            },
        }
