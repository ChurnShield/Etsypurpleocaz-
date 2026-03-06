# =============================================================================
# workflows/market_intelligence/tools/enrich_competitor_data_tool.py
#
# Phase 2: For each trend signal from Phase 1, queries the official Etsy API
# (findAllListingsActive) to enrich with competitor pricing, views, favorites,
# and tag data. Data is ephemeral -- used for scoring only, not stored long-term.
#
# Pattern source: fetch_trends_tool.py _fetch_etsy_search (lines 204-272)
# =============================================================================

import json
import time
import urllib.request
import urllib.error
import urllib.parse
import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
_workflow = os.path.dirname(_here)
_project_root = os.path.dirname(os.path.dirname(_workflow))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_tool import BaseTool

ETSY_BASE_URL = "https://openapi.etsy.com/v3/application"


class EnrichCompetitorDataTool(BaseTool):
    """Enrich trend signals with Etsy competitor data (official API)."""

    def execute(self, **kwargs) -> dict:
        trend_signals      = kwargs.get("trend_signals", [])
        api_key            = kwargs.get("api_key", "")
        page_limit         = kwargs.get("page_limit", 25)
        max_signals        = kwargs.get("max_signals_to_enrich", 30)

        if not api_key:
            return {
                "success": False, "data": None,
                "error": "api_key required for Etsy enrichment",
                "tool_name": self.get_name(), "metadata": {},
            }

        if not trend_signals:
            return {
                "success": False, "data": None,
                "error": "No trend signals to enrich",
                "tool_name": self.get_name(), "metadata": {},
            }

        try:
            enriched = []
            skipped = 0
            errors = 0

            # Only enrich the top N signals to stay within API limits
            to_enrich = trend_signals[:max_signals]
            to_skip = trend_signals[max_signals:]

            print(f"     Enriching top {len(to_enrich)} signals "
                  f"(skipping {len(to_skip)} lower-scored)...", flush=True)

            for i, signal in enumerate(to_enrich):
                keyword = signal.get("keyword", "")
                if not keyword:
                    enriched.append({**signal, "enrichment_status": "no_keyword"})
                    continue

                try:
                    competitor_data = self._fetch_competitor_data(
                        keyword, api_key, page_limit
                    )
                    enriched.append({
                        **signal,
                        **competitor_data,
                        "enrichment_status": "enriched",
                    })
                except Exception as e:
                    enriched.append({
                        **signal,
                        "enrichment_status": f"error: {str(e)[:60]}",
                        "avg_competitor_price": 0,
                        "avg_competitor_views": 0,
                        "avg_competitor_favs": 0,
                        "competition_level": "unknown",
                        "top_competitor_tags": [],
                        "total_results": 0,
                    })
                    errors += 1

                # Progress indicator
                if (i + 1) % 10 == 0:
                    print(f"          {i + 1}/{len(to_enrich)} enriched...", flush=True)

                time.sleep(0.5)  # Rate limit for Etsy API

            # Mark skipped signals
            for signal in to_skip:
                enriched.append({
                    **signal,
                    "enrichment_status": "skipped",
                    "avg_competitor_price": 0,
                    "avg_competitor_views": 0,
                    "avg_competitor_favs": 0,
                    "competition_level": "unknown",
                    "top_competitor_tags": [],
                    "total_results": 0,
                })
                skipped += 1

            return {
                "success": True,
                "data": {
                    "enriched_signals": enriched,
                    "enrichment_stats": {
                        "enriched": len(to_enrich) - errors,
                        "skipped": skipped,
                        "errors": errors,
                        "total": len(enriched),
                    },
                },
                "error": None,
                "tool_name": self.get_name(),
                "metadata": {
                    "enriched": len(to_enrich) - errors,
                    "skipped": skipped,
                    "errors": errors,
                },
            }

        except Exception as e:
            return {
                "success": False, "data": None,
                "error": str(e),
                "tool_name": self.get_name(),
                "metadata": {"exception_type": type(e).__name__},
            }

    def _fetch_competitor_data(self, keyword, api_key, page_limit):
        """Query Etsy findAllListingsActive for a keyword and extract stats.

        Same pattern as fetch_trends_tool.py _fetch_etsy_search.
        """
        url = (
            f"{ETSY_BASE_URL}/listings/active"
            f"?keywords={urllib.parse.quote(keyword)}"
            f"&limit={page_limit}&sort_on=score"
        )
        req = urllib.request.Request(url)
        req.add_header("x-api-key", api_key)
        req.add_header("Accept", "application/json")

        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        listings = data.get("results", [])
        total = data.get("count", 0)

        if not listings:
            return {
                "avg_competitor_price": 0,
                "avg_competitor_views": 0,
                "avg_competitor_favs": 0,
                "competition_level": "none",
                "top_competitor_tags": [],
                "total_results": total,
            }

        # Extract pricing, views, favorites
        prices = []
        views_list = []
        favs_list = []
        tag_freq = {}

        for listing in listings:
            price = listing.get("price", {})
            amt = price.get("amount", 0) / price.get("divisor", 1) if price else 0
            prices.append(amt)
            views_list.append(listing.get("views", 0))
            favs_list.append(listing.get("num_favorers", 0))

            for tag in listing.get("tags", []):
                tag_lower = tag.lower()
                tag_freq[tag_lower] = tag_freq.get(tag_lower, 0) + 1

        top_tags = sorted(tag_freq.items(), key=lambda x: x[1], reverse=True)[:10]

        # Classify competition level
        if total < 200:
            level = "low"
        elif total < 2000:
            level = "medium"
        elif total < 10000:
            level = "high"
        else:
            level = "saturated"

        return {
            "avg_competitor_price": round(sum(prices) / len(prices), 2) if prices else 0,
            "avg_competitor_views": round(sum(views_list) / len(views_list), 1) if views_list else 0,
            "avg_competitor_favs": round(sum(favs_list) / len(favs_list), 1) if favs_list else 0,
            "competition_level": level,
            "top_competitor_tags": [t[0] for t in top_tags],
            "total_results": total,
        }
