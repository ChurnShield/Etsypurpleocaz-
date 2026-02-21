# =============================================================================
# workflows/etsy_analytics/tools/triage_listings_tool.py
#
# Scores every listing on a 0-100 scale and sorts into A/B/C tiers:
#
#   A-tier (70+)  : Keep & promote   - strong performers
#   B-tier (35-69): Optimize         - has potential, needs work
#   C-tier (0-34) : Deactivate       - dead weight hurting shop quality
#
# Scoring breakdown (100 total):
#   Views           0-25  (traffic signal)
#   Sales/Revenue   0-25  (actual conversions)
#   Favourites      0-15  (buyer interest)
#   Engagement      0-10  (fav/view ratio quality)
#   Tag health      0-10  (SEO readiness)
#   Age efficiency  0-10  (performance vs age)
#   Niche bonus     0-5   (tattoo niche priority)
# =============================================================================

import sys
import os
import time
from datetime import datetime, timezone

_here = os.path.dirname(os.path.abspath(__file__))
_workflow = os.path.dirname(_here)
_project_root = os.path.dirname(os.path.dirname(_workflow))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_tool import BaseTool


class TriageListingsTool(BaseTool):
    """Score and categorize every listing into A/B/C tiers."""

    def execute(self, **kwargs) -> dict:
        listings    = kwargs.get("listings", [])
        focus_niche = kwargs.get("focus_niche", "tattoo")

        if not listings:
            return {
                "success": False, "data": None,
                "error": "No listings to triage",
                "tool_name": self.get_name(), "metadata": {},
            }

        try:
            now = time.time()

            # -- Pre-compute percentile boundaries --
            views_list = sorted(l["views"] for l in listings)
            favs_list  = sorted(l["num_favorers"] for l in listings)
            sales_list = sorted(l.get("sales", 0) for l in listings)
            rev_list   = sorted(l.get("revenue", 0) for l in listings)

            scored = []
            for l in listings:
                score, breakdown = self._score_listing(
                    l, views_list, favs_list, sales_list, rev_list,
                    now, focus_niche,
                )
                tier = "A" if score >= 70 else ("B" if score >= 35 else "C")
                recommendation = self._recommend(tier, l, breakdown)

                scored.append({
                    "listing_id":     l["listing_id"],
                    "title":          l["title"],
                    "price":          l.get("price", 0),
                    "currency":       l.get("currency", ""),
                    "views":          l["views"],
                    "num_favorers":   l["num_favorers"],
                    "sales":          l.get("sales", 0),
                    "revenue":        round(l.get("revenue", 0), 2),
                    "tag_count":      l.get("tag_count", len(l.get("tags", []))),
                    "score":          score,
                    "tier":           tier,
                    "breakdown":      breakdown,
                    "recommendation": recommendation,
                    "url":            l.get("url", ""),
                    "created":        l.get("created", 0),
                    "is_niche":       self._is_niche(l, focus_niche),
                })

            # Sort: A first, then B, then C; within each tier, best score first
            tier_order = {"A": 0, "B": 1, "C": 2}
            scored.sort(key=lambda x: (tier_order[x["tier"]], -x["score"]))

            # -- Summary stats --
            a_count = sum(1 for s in scored if s["tier"] == "A")
            b_count = sum(1 for s in scored if s["tier"] == "B")
            c_count = sum(1 for s in scored if s["tier"] == "C")

            a_views = sum(s["views"] for s in scored if s["tier"] == "A")
            b_views = sum(s["views"] for s in scored if s["tier"] == "B")
            c_views = sum(s["views"] for s in scored if s["tier"] == "C")
            total_views = a_views + b_views + c_views

            a_sales = sum(s["sales"] for s in scored if s["tier"] == "A")
            b_sales = sum(s["sales"] for s in scored if s["tier"] == "B")
            c_sales = sum(s["sales"] for s in scored if s["tier"] == "C")

            a_revenue = round(sum(s["revenue"] for s in scored if s["tier"] == "A"), 2)
            b_revenue = round(sum(s["revenue"] for s in scored if s["tier"] == "B"), 2)
            c_revenue = round(sum(s["revenue"] for s in scored if s["tier"] == "C"), 2)

            niche_a = sum(1 for s in scored if s["tier"] == "A" and s["is_niche"])
            niche_b = sum(1 for s in scored if s["tier"] == "B" and s["is_niche"])
            niche_c = sum(1 for s in scored if s["tier"] == "C" and s["is_niche"])

            summary = {
                "total_listings":  len(scored),
                "a_tier": {"count": a_count, "views": a_views, "sales": a_sales,
                           "revenue": a_revenue, "niche": niche_a},
                "b_tier": {"count": b_count, "views": b_views, "sales": b_sales,
                           "revenue": b_revenue, "niche": niche_b},
                "c_tier": {"count": c_count, "views": c_views, "sales": c_sales,
                           "revenue": c_revenue, "niche": niche_c},
                "view_share": {
                    "a_pct": round(a_views / total_views * 100, 1) if total_views else 0,
                    "b_pct": round(b_views / total_views * 100, 1) if total_views else 0,
                    "c_pct": round(c_views / total_views * 100, 1) if total_views else 0,
                },
                "avg_score": round(sum(s["score"] for s in scored) / len(scored), 1),
                "focus_niche": focus_niche,
                "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            }

            return {
                "success": True,
                "data": {
                    "scored_listings": scored,
                    "summary": summary,
                },
                "error": None,
                "tool_name": self.get_name(),
                "metadata": {
                    "total": len(scored),
                    "a_count": a_count,
                    "b_count": b_count,
                    "c_count": c_count,
                    "avg_score": summary["avg_score"],
                },
            }

        except Exception as e:
            return {
                "success": False, "data": None,
                "error": str(e),
                "tool_name": self.get_name(),
                "metadata": {"exception_type": type(e).__name__},
            }

    # -------------------------------------------------------------------------
    # Scoring
    # -------------------------------------------------------------------------

    def _percentile_rank(self, value, sorted_list):
        """Return 0.0-1.0 percentile rank of value in a sorted list."""
        if not sorted_list:
            return 0.0
        count_below = 0
        for v in sorted_list:
            if v < value:
                count_below += 1
            else:
                break
        return count_below / len(sorted_list)

    def _score_listing(self, l, views_list, favs_list, sales_list, rev_list,
                       now_ts, focus_niche):
        """Score a single listing (0-100). Returns (score, breakdown_dict)."""

        # 1. Views score (0-25)
        views = l["views"]
        views_pct = self._percentile_rank(views, views_list)
        views_score = round(views_pct * 25, 1)

        # 2. Sales/Revenue score (0-25)
        sales = l.get("sales", 0)
        revenue = l.get("revenue", 0)
        sales_pct = self._percentile_rank(sales, sales_list)
        rev_pct   = self._percentile_rank(revenue, rev_list)
        # Weight revenue slightly more than count
        sales_score = round((sales_pct * 0.4 + rev_pct * 0.6) * 25, 1)

        # 3. Favourites score (0-15)
        favs = l["num_favorers"]
        favs_pct = self._percentile_rank(favs, favs_list)
        favs_score = round(favs_pct * 15, 1)

        # 4. Engagement score (0-10) — fav/view ratio for listings with 10+ views
        if views >= 10:
            fav_rate = favs / views
            # A 5%+ fav rate is excellent on Etsy
            eng_score = min(10, round(fav_rate * 200, 1))
        else:
            eng_score = 0.0

        # 5. Tag health score (0-10)
        tag_count = l.get("tag_count", len(l.get("tags", [])))
        tag_score = round((tag_count / 13) * 10, 1)
        tag_score = min(10, tag_score)

        # 6. Age efficiency (0-10) — performance relative to how long listed
        created = l.get("created", 0)
        if created > 0:
            age_days = max(1, (now_ts - created) / 86400)
            # Views per day, normalised: 1+ view/day = full score
            views_per_day = views / age_days
            age_score = min(10, round(views_per_day * 10, 1))
        else:
            age_score = 5.0  # Unknown age, give neutral score

        # 7. Niche bonus (0-5)
        niche_score = 5.0 if self._is_niche(l, focus_niche) else 0.0

        total = round(views_score + sales_score + favs_score + eng_score +
                      tag_score + age_score + niche_score, 1)
        total = min(100, total)

        breakdown = {
            "views": views_score,
            "sales": sales_score,
            "favs": favs_score,
            "engagement": eng_score,
            "tags": tag_score,
            "age_efficiency": age_score,
            "niche_bonus": niche_score,
        }

        return total, breakdown

    def _is_niche(self, l, focus_niche):
        """Check if listing belongs to the focus niche."""
        niche_lower = focus_niche.lower()
        if niche_lower in l.get("title", "").lower():
            return True
        for tag in l.get("tags", []):
            if niche_lower in tag.lower():
                return True
        return False

    def _recommend(self, tier, l, breakdown):
        """Generate a short recommendation string based on tier and scores."""
        if tier == "A":
            parts = ["KEEP"]
            if breakdown["tags"] < 8:
                parts.append("top up tags to 13")
            if breakdown["engagement"] >= 7:
                parts.append("high engagement - consider raising price")
            return " | ".join(parts)

        elif tier == "B":
            parts = ["OPTIMIZE"]
            if breakdown["views"] < 10:
                parts.append("needs more traffic - improve SEO")
            if breakdown["tags"] < 8:
                parts.append("add more tags (aim for 13)")
            if breakdown["engagement"] < 3 and l["views"] >= 10:
                parts.append("low engagement - update title/thumbnail")
            if breakdown["sales"] < 5 and l["views"] >= 50:
                parts.append("views but no sales - check pricing/photos")
            return " | ".join(parts)

        else:  # C
            parts = ["DEACTIVATE"]
            if l["views"] == 0:
                parts.append("zero views - invisible to buyers")
            elif l["views"] < 5:
                parts.append("near-zero traffic")
            if l.get("sales", 0) == 0:
                parts.append("never sold")
            if breakdown["tags"] < 5:
                parts.append("severely under-tagged")
            return " | ".join(parts)
