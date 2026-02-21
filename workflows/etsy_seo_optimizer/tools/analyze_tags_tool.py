# =============================================================================
# workflows/etsy_seo_optimizer/tools/analyze_tags_tool.py
#
# Phase 1: Fetches all listings from Etsy and analyzes tag health.
# Identifies: overused tags, under-tagged listings, tag cannibalization,
# and calculates an SEO score per listing.
# =============================================================================

import json
import time
import urllib.request
import sys
import os
from collections import Counter

_here = os.path.dirname(os.path.abspath(__file__))
_workflow = os.path.dirname(_here)
_project_root = os.path.dirname(os.path.dirname(_workflow))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_tool import BaseTool

ETSY_BASE_URL = "https://openapi.etsy.com/v3/application"


class AnalyzeTagsTool(BaseTool):
    """Fetch all listings and analyze tag health across the shop."""

    def execute(self, **kwargs) -> dict:
        api_key             = kwargs.get("api_key", "")
        shop_id             = kwargs.get("shop_id", "")
        page_limit          = kwargs.get("page_limit", 100)
        overused_threshold  = kwargs.get("overused_threshold", 50)
        focus_niche         = kwargs.get("focus_niche", "tattoo")
        max_listings        = kwargs.get("max_listings", 50)

        if not api_key or not shop_id:
            return {
                "success": False, "data": None,
                "error": "api_key and shop_id required",
                "tool_name": self.get_name(), "metadata": {},
            }

        try:
            # -- Fetch all active listings --
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
                    page = json.loads(resp.read().decode("utf-8"))

                results = page.get("results", [])
                if not results:
                    break
                all_listings.extend(results)
                offset += len(results)
                if offset >= page.get("count", 0):
                    break
                time.sleep(0.3)

            # -- Build global tag frequency map --
            global_tag_freq = Counter()
            for l in all_listings:
                for tag in l.get("tags", []):
                    global_tag_freq[tag.lower()] += 1

            overused_tags = {
                tag for tag, count in global_tag_freq.items()
                if count >= overused_threshold
            }

            # -- Score and analyze each listing --
            analyzed = []
            for l in all_listings:
                tags = [t.lower() for t in l.get("tags", [])]
                title = l.get("title", "")
                price_data = l.get("price", {})
                price = price_data.get("amount", 0) / price_data.get("divisor", 1) if price_data else 0

                # Count overused tags in this listing
                overused_count = sum(1 for t in tags if t in overused_tags)
                unique_count = sum(1 for t in tags if global_tag_freq.get(t, 0) < overused_threshold)
                tag_count = len(tags)

                # SEO Score (0-100)
                score = 0
                # +30 for having 13 tags
                score += min(30, int(tag_count / 13 * 30))
                # +40 for unique (non-overused) tags
                if tag_count > 0:
                    score += int((unique_count / tag_count) * 40)
                # +15 for having views (indicates some discoverability)
                views = l.get("views", 0)
                if views > 100:
                    score += 15
                elif views > 20:
                    score += 10
                elif views > 0:
                    score += 5
                # +15 for having favourites (indicates relevance)
                favs = l.get("num_favorers", 0)
                if favs > 10:
                    score += 15
                elif favs > 3:
                    score += 10
                elif favs > 0:
                    score += 5

                issues = []
                if tag_count < 13:
                    issues.append(f"Only {tag_count}/13 tags")
                if overused_count > 5:
                    issues.append(f"{overused_count} generic/overused tags")
                if overused_count == tag_count and tag_count > 0:
                    issues.append("ALL tags are overused across shop")

                analyzed.append({
                    "listing_id":     l.get("listing_id"),
                    "title":          title,
                    "price":          round(price, 2),
                    "views":          views,
                    "num_favorers":   favs,
                    "current_tags":   tags,
                    "tag_count":      tag_count,
                    "overused_count": overused_count,
                    "unique_count":   unique_count,
                    "seo_score":      score,
                    "issues":         issues,
                    "url":            l.get("url", ""),
                })

            # -- Prioritize: focus niche first, then worst SEO scores --
            niche_listings = [
                a for a in analyzed
                if focus_niche.lower() in a["title"].lower()
                or any(focus_niche.lower() in t for t in a["current_tags"])
            ]
            other_listings = [a for a in analyzed if a not in niche_listings]

            # Sort each group by SEO score ascending (worst first)
            niche_listings.sort(key=lambda x: x["seo_score"])
            other_listings.sort(key=lambda x: x["seo_score"])

            # Build priority list: niche first, then others
            priority_list = niche_listings + other_listings

            # Limit to max_listings for optimization
            to_optimize = priority_list[:max_listings] if max_listings > 0 else priority_list

            # -- Overview stats --
            avg_score = round(sum(a["seo_score"] for a in analyzed) / len(analyzed), 1)
            under_tagged = sum(1 for a in analyzed if a["tag_count"] < 13)
            heavily_overused = sum(1 for a in analyzed if a["overused_count"] > 5)

            overused_summary = sorted(
                [(tag, count) for tag, count in global_tag_freq.most_common(30)],
                key=lambda x: -x[1]
            )

            return {
                "success": True,
                "data": {
                    "to_optimize":     to_optimize,
                    "all_analyzed":    analyzed,
                    "overused_tags":   list(overused_tags),
                    "overused_summary": overused_summary,
                    "overview": {
                        "total_listings":   len(analyzed),
                        "avg_seo_score":    avg_score,
                        "under_tagged":     under_tagged,
                        "heavily_overused":  heavily_overused,
                        "niche_count":      len(niche_listings),
                        "unique_tags_total": len(global_tag_freq),
                        "overused_tag_count": len(overused_tags),
                    },
                },
                "error": None,
                "tool_name": self.get_name(),
                "metadata": {
                    "total_listings":  len(analyzed),
                    "to_optimize":     len(to_optimize),
                    "avg_seo_score":   avg_score,
                    "niche_count":     len(niche_listings),
                },
            }

        except Exception as e:
            return {
                "success": False, "data": None,
                "error": str(e),
                "tool_name": self.get_name(),
                "metadata": {"exception_type": type(e).__name__},
            }
