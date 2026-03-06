# =============================================================================
# workflows/market_intelligence/tools/score_opportunities_tool.py
#
# Phase 3: Uses Claude AI to analyze enriched signals and produce scored,
# ranked product opportunities with actionable recommendations.
#
# Pattern source: analyse_opportunities_tool.py _ai_analyse (lines 292-376)
# =============================================================================

import json
import time
import urllib.request
import urllib.error
import sys
import os
from datetime import datetime, timezone

_here = os.path.dirname(os.path.abspath(__file__))
_workflow = os.path.dirname(_here)
_project_root = os.path.dirname(os.path.dirname(_workflow))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_tool import BaseTool

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"


class ScoreOpportunitiesTool(BaseTool):
    """Score and rank opportunities using Claude AI analysis."""

    def execute(self, **kwargs) -> dict:
        enriched_signals = kwargs.get("enriched_signals", [])
        api_key          = kwargs.get("anthropic_api_key", "")
        model            = kwargs.get("model", "claude-sonnet-4-20250514")
        focus_niche      = kwargs.get("focus_niche", "tattoo")
        min_score        = kwargs.get("min_score", 30)
        max_opportunities = kwargs.get("max_opportunities", 20)

        if not api_key:
            return {
                "success": False, "data": None,
                "error": "anthropic_api_key required",
                "tool_name": self.get_name(), "metadata": {},
            }

        if not enriched_signals:
            return {
                "success": False, "data": None,
                "error": "No enriched signals to score",
                "tool_name": self.get_name(), "metadata": {},
            }

        try:
            # Filter to actually enriched signals for the prompt
            scoreable = [
                s for s in enriched_signals
                if s.get("enrichment_status") == "enriched"
            ]
            if not scoreable:
                scoreable = enriched_signals[:max_opportunities]

            print(f"     Scoring {len(scoreable)} signals with Claude...", flush=True)

            opportunities = self._ai_score(
                scoreable, api_key, model, focus_niche
            )

            if not opportunities:
                return {
                    "success": False, "data": None,
                    "error": "Claude returned no opportunities",
                    "tool_name": self.get_name(), "metadata": {},
                }

            # Post-processing
            now = datetime.now(timezone.utc).isoformat()
            filtered = []
            for opp in opportunities:
                score = opp.get("opportunity_score", 0)
                if not isinstance(score, (int, float)):
                    continue
                if score < min_score:
                    continue
                opp["scored_at"] = now
                filtered.append(opp)

            filtered.sort(key=lambda o: o.get("opportunity_score", 0), reverse=True)
            filtered = filtered[:max_opportunities]

            # Re-rank
            for i, opp in enumerate(filtered):
                opp["rank"] = i + 1

            print(f"     {len(filtered)} opportunities scored above threshold ({min_score})",
                  flush=True)

            return {
                "success": True,
                "data": {
                    "scored_opportunities": filtered,
                    "scoring_stats": {
                        "input_signals": len(scoreable),
                        "raw_from_claude": len(opportunities),
                        "after_filter": len(filtered),
                        "model": model,
                    },
                },
                "error": None,
                "tool_name": self.get_name(),
                "metadata": {
                    "opportunities": len(filtered),
                    "model": model,
                },
            }

        except Exception as e:
            return {
                "success": False, "data": None,
                "error": str(e),
                "tool_name": self.get_name(),
                "metadata": {"exception_type": type(e).__name__},
            }

    def _ai_score(self, signals, api_key, model, focus_niche):
        """Call Claude to score and rank market signals into opportunities."""
        # Build a compact summary for the prompt
        signal_summary = []
        for s in signals[:30]:
            signal_summary.append({
                "keyword": s.get("keyword", ""),
                "source": s.get("source", ""),
                "signal_score": s.get("signal_score", 0),
                "direction": s.get("direction", ""),
                "context": s.get("context", ""),
                "avg_competitor_price": s.get("avg_competitor_price", 0),
                "competition_level": s.get("competition_level", ""),
                "total_results": s.get("total_results", 0),
                "top_competitor_tags": s.get("top_competitor_tags", [])[:5],
            })

        prompt = f"""You are an Etsy digital product strategist for the {focus_niche} niche.

Analyze these market signals (from Google Trends + Reddit + Etsy competitor data) and identify the best product opportunities for digital templates on Etsy.

MARKET SIGNALS:
{json.dumps(signal_summary, indent=2)}

For each viable opportunity, provide:
1. opportunity_score (0-100): Higher = better opportunity
2. product_suggestion: Specific Etsy listing title (max 140 chars)
3. product_type: e.g. "gift certificate", "consent form", "social media kit"
4. recommended_price: Based on competitor pricing data
5. recommended_tags: Exactly 13 tags, each max 20 chars
6. reasoning: Why this is an opportunity (1-2 sentences)
7. competition_assessment: "low" | "medium" | "high" | "saturated"
8. urgency: "immediate" | "this_week" | "this_month" | "backlog"
9. source_signals: Which signals contributed

SCORING GUIDELINES:
- Rising trends with low competition = 80-100
- Rising trends with medium competition = 60-80
- Stable trends with low competition = 50-70
- Rising trends with high competition = 30-50
- Declining trends = 10-30

RESPOND IN JSON ARRAY FORMAT ONLY (no markdown, no explanation):
[
  {{
    "rank": 1,
    "opportunity_score": 85,
    "product_suggestion": "Specific Listing Title Here",
    "product_type": "gift certificate",
    "recommended_price": 4.99,
    "recommended_tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8", "tag9", "tag10", "tag11", "tag12", "tag13"],
    "reasoning": "Brief explanation...",
    "competition_assessment": "medium",
    "urgency": "immediate",
    "source_signals": ["google_trends: keyword", "reddit: context"]
  }}
]"""

        from config import MAX_RETRIES

        max_attempts = MAX_RETRIES + 1
        for attempt in range(1, max_attempts + 1):
            try:
                payload = json.dumps({
                    "model": model,
                    "max_tokens": 4096,
                    "messages": [{"role": "user", "content": prompt}],
                }).encode("utf-8")

                req = urllib.request.Request(
                    ANTHROPIC_API_URL, data=payload, method="POST"
                )
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

                return self._parse_json_response(text)

            except urllib.error.HTTPError as e:
                if e.code == 529 and attempt < max_attempts:
                    wait = 10 * attempt
                    print(f"       API overloaded (529), waiting {wait}s...", flush=True)
                    time.sleep(wait)
                    continue
                raise

        return []

    def _parse_json_response(self, text):
        """Parse JSON array from Claude response, handling code fences."""
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(
                lines[1:-1] if lines[-1].strip() == "```" else lines[1:]
            )
            text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("[")
            end = text.rfind("]") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
            return []
