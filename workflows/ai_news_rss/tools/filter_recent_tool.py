# =============================================================================
# workflows/ai_news_rss/tools/filter_recent_tool.py
#
# FilterRecentTool — Phase 2
#
# Takes the full article list from FetchRSSTool and keeps only the articles
# published within the last N hours.
#
# Why this is a separate tool (not just code inside FetchRSSTool):
#   - ExecutionLogger records it as its own event → SmallBrain can see
#     how often filtering removes ALL articles (possible signal to widen
#     the lookback window).
#   - Easier to test in isolation.
#   - Swap the filtering logic without touching the fetch logic.
#
# Output format (stored in result["data"]):
#   {
#       "articles":      list,   # Articles that passed the date filter
#       "total_input":   int,    # How many articles came in
#       "filtered_count":int,    # How many passed (= len(articles))
#       "skipped_old":   int,    # Too old
#       "skipped_no_date":int,   # Could not parse the date string
#       "cutoff_utc":    str,    # ISO 8601 timestamp of the cutoff
#   }
# =============================================================================

import sys
import os
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

# ---------------------------------------------------------------------------
# Path setup  (same pattern as fetch_rss_tool.py)
# ---------------------------------------------------------------------------
_here = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(_here)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_tool import BaseTool


class FilterRecentTool(BaseTool):
    """
    Keeps only articles published within the last `hours` hours.

    Date parsing strategy
    ---------------------
    RSS 2.0 feeds use RFC 2822 format:  "Wed, 19 Feb 2026 12:00:00 +0000"
    Some feeds use ISO 8601:            "2026-02-19T12:00:00Z"
    We try RFC 2822 first, then fall back to ISO 8601.
    Articles with unparseable dates are skipped (logged in skipped_no_date).
    """

    def execute(self, **kwargs) -> dict:
        """
        Parameters
        ----------
        articles : list   Output of FetchRSSTool — list of article dicts.
        hours    : int    Keep articles published within this many hours (default 24).

        Returns
        -------
        Standard tool dict.  result["data"]["articles"] is the filtered list.
        """
        articles = kwargs.get("articles", [])
        hours    = int(kwargs.get("hours", 24))

        try:
            cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

            recent          = []
            skipped_old     = 0
            skipped_no_date = 0

            for article in articles:
                pub_dt = self._parse_date(article.get("pub_date", ""))

                if pub_dt is None:
                    # Can't determine when this was published — skip it.
                    skipped_no_date += 1
                    continue

                if pub_dt >= cutoff:
                    # Copy the article and add a clean ISO date for Airtable.
                    enriched = dict(article)
                    enriched["pub_date_iso"] = pub_dt.isoformat()
                    recent.append(enriched)
                else:
                    skipped_old += 1

            return {
                "success": True,
                "data": {
                    "articles":       recent,
                    "total_input":    len(articles),
                    "filtered_count": len(recent),
                    "skipped_old":    skipped_old,
                    "skipped_no_date": skipped_no_date,
                    "cutoff_utc":     cutoff.isoformat(),
                },
                "error": None,
                "tool_name": self.get_name(),
                "metadata": {
                    "total_input":    len(articles),
                    "recent_count":   len(recent),
                    "lookback_hours": hours,
                },
            }

        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": str(e),
                "tool_name": self.get_name(),
                "metadata": {"exception_type": type(e).__name__},
            }

    # -------------------------------------------------------------------------
    # Private helpers
    # -------------------------------------------------------------------------

    def _parse_date(self, date_str: str):
        """
        Return a timezone-aware datetime, or None if parsing fails.

        Tries RFC 2822 first (standard RSS 2.0 format), then ISO 8601.
        """
        if not date_str:
            return None

        # --- RFC 2822 (RSS 2.0): "Wed, 19 Feb 2026 12:00:00 +0000" ----------
        try:
            return parsedate_to_datetime(date_str)
        except Exception:
            pass

        # --- ISO 8601: "2026-02-19T12:00:00Z" or "2026-02-19T12:00:00+00:00" -
        try:
            normalized = date_str.replace("Z", "+00:00")
            dt = datetime.fromisoformat(normalized)
            # Attach UTC if the string had no timezone info.
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except Exception:
            pass

        return None   # Give up — date format is not recognised
