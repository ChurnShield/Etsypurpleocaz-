# =============================================================================
# workflows/etsy_analytics/tools/analyze_performance_tool.py
#
# Phase 2: Analyzes listing performance — identifies top performers,
# underperformers, and calculates shop-level metrics.
# No external dependencies.
# =============================================================================

import sys
import os
from datetime import datetime

_here = os.path.dirname(os.path.abspath(__file__))
_workflow = os.path.dirname(_here)
_project_root = os.path.dirname(os.path.dirname(_workflow))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_tool import BaseTool


class AnalyzePerformanceTool(BaseTool):
    """Analyze Etsy listing data and produce actionable insights."""

    def execute(self, **kwargs) -> dict:
        shop     = kwargs.get("shop", {})
        listings = kwargs.get("listings", [])

        if not listings:
            return {
                "success":   False,
                "data":      None,
                "error":     "No listings to analyze",
                "tool_name": self.get_name(),
                "metadata":  {},
            }

        try:
            now_ts = datetime.utcnow().isoformat()

            # -- Basic stats --
            total_views     = sum(l["views"] for l in listings)
            total_favs      = sum(l["num_favorers"] for l in listings)
            total_sales     = sum(l.get("sales", 0) for l in listings)
            total_revenue   = round(sum(l.get("revenue", 0) for l in listings), 2)
            avg_views       = round(total_views / len(listings), 1)
            avg_favs        = round(total_favs / len(listings), 1)
            avg_price       = round(sum(l["price"] for l in listings) / len(listings), 2)

            # -- Price distribution --
            prices = [l["price"] for l in listings]
            prices.sort()
            min_price = prices[0]
            max_price = prices[-1]
            median_price = prices[len(prices) // 2]

            # -- Top performers by views --
            by_views = sorted(listings, key=lambda x: x["views"], reverse=True)
            top_by_views = by_views[:20]

            # -- Top performers by favourites --
            by_favs = sorted(listings, key=lambda x: x["num_favorers"], reverse=True)
            top_by_favs = by_favs[:20]

            # -- Top performers by revenue (if sales data available) --
            by_revenue = sorted(listings, key=lambda x: x.get("revenue", 0), reverse=True)
            top_by_revenue = [l for l in by_revenue[:20] if l.get("revenue", 0) > 0]

            # -- Top performers by sales count --
            by_sales = sorted(listings, key=lambda x: x.get("sales", 0), reverse=True)
            top_by_sales = [l for l in by_sales[:20] if l.get("sales", 0) > 0]

            # -- Fav-to-view ratio (engagement rate) for listings with 10+ views --
            for l in listings:
                if l["views"] >= 10:
                    l["fav_rate"] = round(l["num_favorers"] / l["views"] * 100, 2)
                else:
                    l["fav_rate"] = 0.0

            by_engagement = sorted(
                [l for l in listings if l["views"] >= 10],
                key=lambda x: x["fav_rate"],
                reverse=True,
            )
            top_engagement = by_engagement[:20]

            # -- Zero-view listings (need attention) --
            zero_views = [l for l in listings if l["views"] == 0]

            # -- Low-view listings (< 5 views, likely need SEO help) --
            low_views = [l for l in listings if 0 < l["views"] < 5]

            # -- Tag analysis --
            all_tags = {}
            for l in listings:
                for tag in l.get("tags", []):
                    tag_lower = tag.lower()
                    all_tags[tag_lower] = all_tags.get(tag_lower, 0) + 1
            # Most reused tags (potential cannibalization)
            overused_tags = sorted(all_tags.items(), key=lambda x: x[1], reverse=True)[:20]

            # Listings with fewer than 13 tags (missing SEO opportunity)
            under_tagged = [l for l in listings if l["tag_count"] < 13]

            # -- Tattoo niche analysis --
            tattoo_listings = [
                l for l in listings
                if "tattoo" in l["title"].lower()
                or any("tattoo" in t.lower() for t in l.get("tags", []))
            ]
            tattoo_views   = sum(l["views"] for l in tattoo_listings) if tattoo_listings else 0
            tattoo_favs    = sum(l["num_favorers"] for l in tattoo_listings) if tattoo_listings else 0
            tattoo_sales   = sum(l.get("sales", 0) for l in tattoo_listings) if tattoo_listings else 0
            tattoo_revenue = round(sum(l.get("revenue", 0) for l in tattoo_listings), 2) if tattoo_listings else 0

            # -- Daily snapshot row --
            snapshot = {
                "date":             now_ts[:10],
                "total_sales":      shop.get("total_sales", 0),
                "active_listings":  len(listings),
                "shop_favorers":    shop.get("num_favorers", 0),
                "review_average":   shop.get("review_average", 0),
                "review_count":     shop.get("review_count", 0),
                "total_views":      total_views,
                "total_favs":       total_favs,
                "avg_views":        avg_views,
                "avg_favs":         avg_favs,
                "avg_price":        avg_price,
                "median_price":     median_price,
                "min_price":        min_price,
                "max_price":        max_price,
                "zero_view_count":  len(zero_views),
                "low_view_count":   len(low_views),
                "under_tagged":     len(under_tagged),
                "tattoo_listings":  len(tattoo_listings),
                "tattoo_views":     tattoo_views,
                "tattoo_favs":      tattoo_favs,
                "total_item_sales": total_sales,
                "total_revenue":    total_revenue,
                "tattoo_sales":     tattoo_sales,
                "tattoo_revenue":   tattoo_revenue,
            }

            return {
                "success": True,
                "data": {
                    "snapshot":        snapshot,
                    "listings":        listings,
                    "top_by_views":    top_by_views,
                    "top_by_favs":     top_by_favs,
                    "top_by_revenue":  top_by_revenue,
                    "top_by_sales":    top_by_sales,
                    "top_engagement":  top_engagement,
                    "zero_views":      zero_views[:50],
                    "overused_tags":   overused_tags,
                    "tattoo_listings": len(tattoo_listings),
                },
                "error":     None,
                "tool_name": self.get_name(),
                "metadata": {
                    "total_listings":    len(listings),
                    "total_views":       total_views,
                    "total_favs":        total_favs,
                    "zero_view_count":   len(zero_views),
                    "tattoo_count":      len(tattoo_listings),
                    "overused_tag_top":  overused_tags[0] if overused_tags else None,
                },
            }

        except Exception as e:
            return {
                "success":   False,
                "data":      None,
                "error":     str(e),
                "tool_name": self.get_name(),
                "metadata":  {"exception_type": type(e).__name__},
            }
