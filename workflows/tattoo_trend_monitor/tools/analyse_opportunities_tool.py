# =============================================================================
# workflows/tattoo_trend_monitor/tools/analyse_opportunities_tool.py
#
# Phase 2: Combines Google Trends + Etsy competitor data + your listings
# to identify gaps and opportunities in the tattoo niche.
#
# Uses Claude to generate actionable product ideas based on the data.
# =============================================================================

import json
import urllib.request
import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
_workflow = os.path.dirname(_here)
_project_root = os.path.dirname(os.path.dirname(_workflow))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_tool import BaseTool

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"


class AnalyseOpportunitiesTool(BaseTool):
    """Analyse trends data and identify tattoo niche opportunities."""

    def execute(self, **kwargs) -> dict:
        trends           = kwargs.get("trends", [])
        competitor_search = kwargs.get("competitor_search", [])
        my_listings      = kwargs.get("my_tattoo_listings", [])
        api_key          = kwargs.get("anthropic_api_key", "")
        model            = kwargs.get("model", "claude-sonnet-4-20250514")

        try:
            # ---- Step 1: Trend scoring ----
            print("     [2a] Scoring trend keywords...", flush=True)
            scored_trends = self._score_trends(trends)

            # ---- Step 2: Gap analysis ----
            print("     [2b] Running gap analysis vs your inventory...", flush=True)
            gaps = self._find_gaps(competitor_search, my_listings)

            # ---- Step 3: Market sizing ----
            print("     [2c] Sizing market opportunities...", flush=True)
            market_data = self._size_markets(competitor_search)

            # ---- Step 4: AI opportunity ranking ----
            print("     [2d] Generating AI opportunity analysis...", flush=True)
            if api_key:
                ai_opportunities = self._ai_analyse(
                    scored_trends, gaps, market_data, my_listings,
                    api_key, model,
                )
            else:
                ai_opportunities = []
                print("          Skipped (no ANTHROPIC_API_KEY)", flush=True)

            # ---- Compile results ----
            opportunities = []
            for trend in scored_trends:
                kw = trend["keyword"]
                gap_info = next((g for g in gaps if g["query_keyword"] == kw), None)
                market = next((m for m in market_data if m["keyword"] == kw), None)

                opportunities.append({
                    "keyword": kw,
                    "trend_score": trend["trend_score"],
                    "trend_direction": trend["trend_direction"],
                    "growth_pct": trend["growth_pct"],
                    "current_interest": trend["current_interest"],
                    "you_have_listings": gap_info["you_have"] if gap_info else 0,
                    "gap_status": gap_info["gap_status"] if gap_info else "unknown",
                    "competitor_count": market["total_competitors"] if market else 0,
                    "avg_competitor_price": market["avg_price"] if market else 0,
                    "avg_competitor_views": market["avg_views"] if market else 0,
                    "opportunity_score": self._calc_opportunity_score(trend, gap_info, market),
                })

            # Sort by opportunity score
            opportunities.sort(key=lambda x: x["opportunity_score"], reverse=True)

            # Summary stats
            rising = [t for t in scored_trends if t["trend_direction"] == "rising"]
            total_gaps = sum(1 for g in gaps if g["gap_status"] == "GAP")
            weak_coverage = sum(1 for g in gaps if g["gap_status"] == "WEAK")

            summary = {
                "total_keywords_tracked": len(scored_trends),
                "rising_trends": len(rising),
                "declining_trends": sum(1 for t in scored_trends if t["trend_direction"] == "declining"),
                "stable_trends": sum(1 for t in scored_trends if t["trend_direction"] == "stable"),
                "total_gaps": total_gaps,
                "weak_coverage": weak_coverage,
                "your_tattoo_listings": len(my_listings),
                "top_opportunity": opportunities[0]["keyword"] if opportunities else "",
            }

            return {
                "success": True,
                "data": {
                    "opportunities": opportunities,
                    "ai_opportunities": ai_opportunities,
                    "scored_trends": scored_trends,
                    "gaps": gaps,
                    "market_data": market_data,
                    "summary": summary,
                },
                "error": None,
                "tool_name": self.get_name(),
                "metadata": {
                    "opportunities": len(opportunities),
                    "rising_trends": len(rising),
                    "gaps_found": total_gaps,
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
    # Step 1: Score trends
    # -------------------------------------------------------------------------

    def _score_trends(self, trends):
        """Score each trend keyword 0-100 based on interest + direction."""
        scored = []
        for t in trends:
            interest = t.get("current_interest", 0)
            growth = t.get("growth_pct", 0)
            peak = t.get("peak_interest", 0)

            # Interest score (0-50): current interest relative to 100 scale
            interest_score = min(50, interest * 0.5)

            # Growth score (0-30): positive growth is good
            if growth > 50:
                growth_score = 30
            elif growth > 20:
                growth_score = 20
            elif growth > 0:
                growth_score = 10
            elif growth > -15:
                growth_score = 5
            else:
                growth_score = 0

            # Consistency score (0-20): current vs peak
            if peak > 0:
                consistency = interest / peak
                consistency_score = round(consistency * 20, 1)
            else:
                consistency_score = 0

            total = round(interest_score + growth_score + consistency_score, 1)

            scored.append({
                **t,
                "trend_score": min(100, total),
            })

        scored.sort(key=lambda x: x["trend_score"], reverse=True)
        return scored

    # -------------------------------------------------------------------------
    # Step 2: Gap analysis
    # -------------------------------------------------------------------------

    def _find_gaps(self, competitor_search, my_listings):
        """Compare competitor queries against your inventory."""
        my_titles = " ".join(l["title"].lower() for l in my_listings)
        my_tags = set()
        for l in my_listings:
            for t in l.get("tags", []):
                my_tags.add(t.lower())

        gaps = []
        for comp in competitor_search:
            query = comp.get("query", "")
            query_words = query.lower().split()

            # Check if you have listings matching this query
            matches = 0
            for l in my_listings:
                title_lower = l["title"].lower()
                tag_lower = [t.lower() for t in l.get("tags", [])]
                # Count how many query words appear in title or tags
                word_hits = sum(
                    1 for w in query_words
                    if w in title_lower or any(w in t for t in tag_lower)
                )
                if word_hits >= len(query_words) * 0.6:
                    matches += 1

            if matches == 0:
                gap_status = "GAP"
            elif matches <= 2:
                gap_status = "WEAK"
            else:
                gap_status = "COVERED"

            # Extract the core keyword from the query
            core_kw = query.replace("template", "").replace("canva", "").replace("editable", "").replace("digital", "").replace("printable", "").strip()

            gaps.append({
                "query": query,
                "query_keyword": core_kw,
                "you_have": matches,
                "gap_status": gap_status,
                "competitor_count": comp.get("total_results", 0),
                "competitor_avg_price": comp.get("top_25_avg_price", 0),
            })

        return gaps

    # -------------------------------------------------------------------------
    # Step 3: Market sizing
    # -------------------------------------------------------------------------

    def _size_markets(self, competitor_search):
        """Extract market metrics from competitor search data."""
        markets = []
        for comp in competitor_search:
            query = comp.get("query", "")
            core_kw = query.replace("template", "").replace("canva", "").replace("editable", "").replace("digital", "").replace("printable", "").strip()

            markets.append({
                "keyword": core_kw,
                "query": query,
                "total_competitors": comp.get("total_results", 0),
                "avg_price": comp.get("top_25_avg_price", 0),
                "avg_views": comp.get("top_25_avg_views", 0),
                "avg_favs": comp.get("top_25_avg_favs", 0),
                "max_views": comp.get("top_25_max_views", 0),
                "max_favs": comp.get("top_25_max_favs", 0),
                "top_tags": [t[0] for t in comp.get("competitor_tags", [])[:5]],
            })

        return markets

    # -------------------------------------------------------------------------
    # Opportunity score
    # -------------------------------------------------------------------------

    def _calc_opportunity_score(self, trend, gap, market):
        """Calculate a combined opportunity score (0-100)."""
        score = 0

        # Trend strength (0-30)
        score += min(30, trend.get("trend_score", 0) * 0.3)

        # Gap bonus (0-30): bigger gap = bigger opportunity
        if gap:
            if gap["gap_status"] == "GAP":
                score += 30
            elif gap["gap_status"] == "WEAK":
                score += 15

        # Market demand (0-20): more competitors = proven demand
        if market:
            competitors = market.get("total_competitors", 0)
            if competitors > 5000:
                score += 20
            elif competitors > 1000:
                score += 15
            elif competitors > 200:
                score += 10
            elif competitors > 50:
                score += 5

        # Growth bonus (0-20): rising trends are more valuable
        growth = trend.get("growth_pct", 0)
        if growth > 30:
            score += 20
        elif growth > 10:
            score += 15
        elif growth > 0:
            score += 10

        return round(min(100, score), 1)

    # -------------------------------------------------------------------------
    # AI analysis
    # -------------------------------------------------------------------------

    def _ai_analyse(self, trends, gaps, markets, my_listings, api_key, model):
        """Use Claude to generate specific product opportunity recommendations."""
        # Build context for Claude
        rising_trends = [t for t in trends if t["trend_direction"] == "rising"][:10]
        gap_keywords = [g for g in gaps if g["gap_status"] in ("GAP", "WEAK")][:10]
        top_markets = sorted(markets, key=lambda m: m.get("total_competitors", 0), reverse=True)[:10]

        my_titles = [l["title"] for l in my_listings[:30]]

        prompt = f"""You are an Etsy product strategist specializing in digital templates for the tattoo industry.

CONTEXT: I sell digital Canva templates on Etsy (gift certificates, consent forms, aftercare cards, flash sheets, etc.) targeting tattoo shops and artists. I currently have {len(my_listings)} tattoo-related listings.

RISING GOOGLE TRENDS (tattoo niche):
{json.dumps(rising_trends, indent=2)}

GAPS IN MY INVENTORY (products competitors sell that I don't have or barely cover):
{json.dumps(gap_keywords, indent=2)}

TOP COMPETITIVE MARKETS (by number of sellers):
{json.dumps(top_markets, indent=2)}

MY CURRENT TATTOO LISTINGS (sample):
{json.dumps(my_titles, indent=2)}

TASK: Give me exactly 10 specific product opportunities ranked by potential. For each one:
1. Product name (specific Etsy listing title I could use)
2. Why it's an opportunity (trend + gap + demand data)
3. Suggested price point (based on competitor pricing)
4. Priority (HIGH / MEDIUM / LOW)
5. Estimated effort to create in Canva (quick / moderate / complex)

RESPOND IN JSON FORMAT:
[
  {{
    "rank": 1,
    "product_title": "Specific listing title",
    "why": "Brief explanation",
    "suggested_price": 4.99,
    "priority": "HIGH",
    "effort": "quick",
    "target_keywords": ["tag1", "tag2", "tag3"]
  }}
]"""

        try:
            payload = json.dumps({
                "model": model,
                "max_tokens": 4096,
                "messages": [{"role": "user", "content": prompt}],
            }).encode("utf-8")

            req = urllib.request.Request(ANTHROPIC_API_URL, data=payload, method="POST")
            req.add_header("x-api-key", api_key)
            req.add_header("anthropic-version", "2023-06-01")
            req.add_header("Content-Type", "application/json")

            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            text = ""
            for block in data.get("content", []):
                if block.get("type") == "text":
                    text = block.get("text", "")
                    break

            # Parse JSON from response
            text = text.strip()
            if text.startswith("```"):
                lines = text.split("\n")
                text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
                text = text.strip()

            try:
                return json.loads(text)
            except json.JSONDecodeError:
                start = text.find("[")
                end = text.rfind("]") + 1
                if start >= 0 and end > start:
                    return json.loads(text[start:end])
                return []

        except Exception as e:
            print(f"          AI analysis error: {e}", flush=True)
            return []
