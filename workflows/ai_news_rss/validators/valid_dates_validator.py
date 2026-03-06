# =============================================================================
# workflows/ai_news_rss/validators/valid_dates_validator.py
#
# ValidDatesValidator — validates Phase 2 (FilterRecentTool) output.
#
# What it checks
# --------------
# 1. The tool produced a valid data structure (has "articles" key).
# 2. An empty articles list IS valid — it simply means no new content
#    today, which is normal and not worth retrying.
#
# What it does NOT check
# ----------------------
# It does not require at least one article — that would cause the
# workflow to fail on quiet news days.  run.py handles the "nothing
# to save" case gracefully by skipping Phase 3.
#
# needs_more = False — retrying the filter with the same articles
# would produce the same result.
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


class ValidDatesValidator(BaseValidator):
    """
    Validates that FilterRecentTool produced a well-formed output.

    Passes even when zero articles remain after filtering —
    that just means nothing was published in the lookback window today.
    """

    def validate(self, data: dict, context: dict = None) -> dict:
        """
        Parameters
        ----------
        data : dict   result["data"] from FilterRecentTool.
                      Expected shape: {"articles": [...], "total_input": int, ...}
        """
        issues = []

        if data is None:
            issues.append(
                "FilterRecentTool returned no data at all — "
                "the tool may have crashed silently."
            )
            return {
                "passed":         False,
                "issues":         issues,
                "needs_more":     False,
                "validator_name": self.get_name(),
                "metadata":       {},
            }

        articles = data.get("articles")

        if articles is None:
            issues.append(
                "FilterRecentTool output is missing the 'articles' key."
            )
        elif not isinstance(articles, list):
            issues.append(
                f"'articles' should be a list, got {type(articles).__name__}."
            )

        passed        = len(issues) == 0
        recent_count  = len(articles) if isinstance(articles, list) else 0

        return {
            "passed":         passed,
            "issues":         issues,
            "needs_more":     not passed,
            "validator_name": self.get_name(),
            "metadata": {
                "recent_count":   recent_count,
                "total_input":    data.get("total_input",    0),
                "skipped_old":    data.get("skipped_old",    0),
                "skipped_no_date":data.get("skipped_no_date",0),
            },
        }
