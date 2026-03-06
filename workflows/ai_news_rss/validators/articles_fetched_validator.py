# =============================================================================
# workflows/ai_news_rss/validators/articles_fetched_validator.py
#
# ArticlesFetchedValidator — validates Phase 1 (FetchRSSTool) output.
#
# What it checks
# --------------
# 1. The "articles" key exists in the tool's data dict.
# 2. At least one article was returned.
#
# When it would fail
# ------------------
# - The RSS feed returned an empty channel (no <item> elements).
# - The feed URL was wrong and returned an error page instead of XML.
# - All items were missing both a title and a URL (filtered out by the tool).
#
# needs_more = False because retrying will just hit the same feed again.
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


class ArticlesFetchedValidator(BaseValidator):
    """
    Confirms that FetchRSSTool returned at least one article.

    An empty feed is treated as a failure because the workflow has
    nothing to filter or save — it's worth alerting on this.
    """

    def validate(self, data: dict, context: dict = None) -> dict:
        """
        Parameters
        ----------
        data : dict   result["data"] from FetchRSSTool.
                      Expected shape: {"articles": [...]}
        """
        issues   = []
        articles = (data or {}).get("articles", [])

        if not isinstance(articles, list):
            issues.append(
                "'articles' is not a list — "
                "FetchRSSTool may have returned an unexpected format."
            )
        elif len(articles) == 0:
            issues.append(
                "No articles were fetched. "
                "The RSS feed may be empty, unreachable, or using "
                "a format the tool does not support."
            )

        article_count = len(articles) if isinstance(articles, list) else 0
        passed = len(issues) == 0

        return {
            "passed":         passed,
            "issues":         issues,
            # Retrying the fetch won't help if the feed is genuinely empty.
            "needs_more":     False,
            "validator_name": self.get_name(),
            "metadata":       {"article_count": article_count},
        }
