# =============================================================================
# workflows/tattoo_trend_monitor/tools/fetch_trends_tool.py
#
# Phase 1: Fetches data from 3 sources:
#   a) Google Trends - search interest for tattoo keywords over time
#   b) Etsy Search API - competitor listings for tattoo queries
#   c) Your own listings - current tattoo inventory from your shop
# =============================================================================

import json
import time
import urllib.request
import urllib.error
import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
_workflow = os.path.dirname(_here)
_project_root = os.path.dirname(os.path.dirname(_workflow))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_tool import BaseTool

ETSY_BASE_URL = "https://openapi.etsy.com/v3/application"


class FetchTrendsTool(BaseTool):
    """Fetch Google Trends + Etsy competitor data for tattoo niche."""

    def execute(self, **kwargs) -> dict:
        trend_keywords    = kwargs.get("trend_keywords", [])
        etsy_queries      = kwargs.get("etsy_search_queries", [])
        api_key           = kwargs.get("api_key", "")
        shop_id           = kwargs.get("shop_id", "")
        page_limit        = kwargs.get("page_limit", 100)
        trends_geo        = kwargs.get("trends_geo", "")
        trends_timeframe  = kwargs.get("trends_timeframe", "today 12-m")

        if not api_key or not shop_id:
            return {
                "success": False, "data": None,
                "error": "api_key and shop_id required",
                "tool_name": self.get_name(), "metadata": {},
            }

        try:
            # ---- A) Google Trends ----
            print("     [1a] Fetching Google Trends data...", flush=True)
            trends_data = self._fetch_google_trends(
                trend_keywords, trends_geo, trends_timeframe
            )
            print(f"          {len(trends_data)} keyword groups analysed", flush=True)

            # ---- B) Etsy competitor search ----
            print("     [1b] Scanning Etsy competitor listings...", flush=True)
            etsy_search_results = self._fetch_etsy_search(
                etsy_queries, api_key, page_limit
            )
            print(f"          {len(etsy_search_results)} queries scanned", flush=True)

            # ---- C) Your own tattoo listings ----
            print("     [1c] Fetching your tattoo listings...", flush=True)
            my_listings = self._fetch_my_tattoo_listings(
                api_key, shop_id, page_limit
            )
            print(f"          {len(my_listings)} tattoo listings in your shop", flush=True)

            return {
                "success": True,
                "data": {
                    "trends": trends_data,
                    "competitor_search": etsy_search_results,
                    "my_tattoo_listings": my_listings,
                },
                "error": None,
                "tool_name": self.get_name(),
                "metadata": {
                    "trend_keywords": len(trend_keywords),
                    "etsy_queries": len(etsy_search_results),
                    "my_listings": len(my_listings),
                },
            }

        except Exception as e:
            return {
                "success": False, "data": None,
                "error": str(e),
                "tool_name": self.get_name(),
                "metadata": {"exception_type": type(e).__name__},
            }

    # =========================================================================
    # A) Google Trends
    # =========================================================================

    def _fetch_google_trends(self, keywords, geo, timeframe):
        """Fetch Google Trends interest data for keyword groups.

        pytrends limits to 5 keywords per request, so we batch them.
        Returns list of dicts with trend scores and direction.
        """
        try:
            from pytrends.request import TrendReq
        except ImportError:
            print("          WARNING: pytrends not installed, skipping Google Trends",
                  flush=True)
            return []

        results = []
        pytrends = TrendReq(hl="en-US", tz=0)

        # Process in groups of 5 (pytrends limit)
        for i in range(0, len(keywords), 5):
            group = keywords[i:i + 5]
            try:
                pytrends.build_payload(group, timeframe=timeframe, geo=geo)
                interest = pytrends.interest_over_time()

                if interest.empty:
                    for kw in group:
                        results.append({
                            "keyword": kw,
                            "current_interest": 0,
                            "avg_interest": 0,
                            "peak_interest": 0,
                            "trend_direction": "no data",
                            "growth_pct": 0,
                        })
                    continue

                for kw in group:
                    if kw not in interest.columns:
                        results.append({
                            "keyword": kw,
                            "current_interest": 0,
                            "avg_interest": 0,
                            "peak_interest": 0,
                            "trend_direction": "no data",
                            "growth_pct": 0,
                        })
                        continue

                    series = interest[kw]
                    current = int(series.iloc[-1]) if len(series) > 0 else 0
                    avg_val = round(float(series.mean()), 1)
                    peak = int(series.max())

                    # Compare last 3 months vs first 3 months for direction
                    if len(series) >= 12:
                        recent = float(series.iloc[-13:].mean())
                        earlier = float(series.iloc[:13].mean())
                    elif len(series) >= 4:
                        mid = len(series) // 2
                        recent = float(series.iloc[mid:].mean())
                        earlier = float(series.iloc[:mid].mean())
                    else:
                        recent = current
                        earlier = avg_val

                    if earlier > 0:
                        growth = round((recent - earlier) / earlier * 100, 1)
                    else:
                        growth = 100.0 if recent > 0 else 0.0

                    if growth > 15:
                        direction = "rising"
                    elif growth < -15:
                        direction = "declining"
                    else:
                        direction = "stable"

                    results.append({
                        "keyword": kw,
                        "current_interest": current,
                        "avg_interest": avg_val,
                        "peak_interest": peak,
                        "trend_direction": direction,
                        "growth_pct": growth,
                    })

                time.sleep(2)  # Rate limit for Google

            except Exception as e:
                # Don't fail the whole run for one group
                for kw in group:
                    results.append({
                        "keyword": kw,
                        "current_interest": 0,
                        "avg_interest": 0,
                        "peak_interest": 0,
                        "trend_direction": f"error: {str(e)[:50]}",
                        "growth_pct": 0,
                    })
                time.sleep(5)

        return results

    # =========================================================================
    # B) Etsy search - competitor landscape
    # =========================================================================

    def _fetch_etsy_search(self, queries, api_key, page_limit):
        """Search Etsy for each query and analyse competitor listings."""
        results = []

        for query in queries:
            try:
                url = (
                    f"{ETSY_BASE_URL}/listings/active"
                    f"?keywords={urllib.parse.quote(query)}"
                    f"&limit=25&sort_on=score"
                )
                req = urllib.request.Request(url)
                req.add_header("x-api-key", api_key)
                req.add_header("Accept", "application/json")

                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode("utf-8"))

                listings = data.get("results", [])
                total = data.get("count", 0)

                # Analyse the top results
                prices = []
                views_list = []
                favs_list = []
                tag_sets = []

                for l in listings:
                    price = l.get("price", {})
                    amt = price.get("amount", 0) / price.get("divisor", 1) if price else 0
                    prices.append(amt)
                    views_list.append(l.get("views", 0))
                    favs_list.append(l.get("num_favorers", 0))
                    tag_sets.append(l.get("tags", []))

                # Common tags used by competitors
                tag_freq = {}
                for tags in tag_sets:
                    for t in tags:
                        tag_freq[t.lower()] = tag_freq.get(t.lower(), 0) + 1
                top_competitor_tags = sorted(tag_freq.items(), key=lambda x: x[1], reverse=True)[:10]

                results.append({
                    "query": query,
                    "total_results": total,
                    "top_25_avg_price": round(sum(prices) / len(prices), 2) if prices else 0,
                    "top_25_avg_views": round(sum(views_list) / len(views_list), 1) if views_list else 0,
                    "top_25_avg_favs": round(sum(favs_list) / len(favs_list), 1) if favs_list else 0,
                    "top_25_max_views": max(views_list) if views_list else 0,
                    "top_25_max_favs": max(favs_list) if favs_list else 0,
                    "competitor_tags": top_competitor_tags,
                })

                time.sleep(0.5)

            except Exception as e:
                results.append({
                    "query": query,
                    "total_results": 0,
                    "error": str(e)[:100],
                    "top_25_avg_price": 0,
                    "top_25_avg_views": 0,
                    "top_25_avg_favs": 0,
                    "top_25_max_views": 0,
                    "top_25_max_favs": 0,
                    "competitor_tags": [],
                })

        return results

    # =========================================================================
    # C) Your own tattoo listings
    # =========================================================================

    def _fetch_my_tattoo_listings(self, api_key, shop_id, page_limit):
        """Fetch all your listings and filter to tattoo niche."""
        all_listings = []
        offset = 0

        while True:
            url = (
                f"{ETSY_BASE_URL}/shops/{shop_id}/listings/active"
                f"?limit={page_limit}&offset={offset}"
            )
            req = urllib.request.Request(url)
            req.add_header("x-api-key", api_key)
            req.add_header("Accept", "application/json")

            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            results = data.get("results", [])
            total = data.get("count", 0)

            if not results:
                break

            all_listings.extend(results)
            offset += len(results)
            if offset >= total:
                break
            time.sleep(0.3)

        # Filter to tattoo niche
        tattoo_listings = []
        for l in all_listings:
            title = l.get("title", "").lower()
            tags = [t.lower() for t in l.get("tags", [])]
            if "tattoo" in title or any("tattoo" in t for t in tags):
                price = l.get("price", {})
                amt = price.get("amount", 0) / price.get("divisor", 1) if price else 0
                tattoo_listings.append({
                    "listing_id": l.get("listing_id"),
                    "title": l.get("title", ""),
                    "price": round(amt, 2),
                    "views": l.get("views", 0),
                    "num_favorers": l.get("num_favorers", 0),
                    "tags": l.get("tags", []),
                    "url": l.get("url", ""),
                })

        return tattoo_listings
