# =============================================================================
# workflows/auto_listing_creator/tools/notebooklm_research_tool.py
#
# Phase 1.5: Enriches product opportunities with grounded research from
# NotebookLM notebooks via the notebooklm-mcp-cli MCP server.
#
# Queries niche-specific notebooks for:
#   - Market positioning insights
#   - Keyword gap analysis
#   - Buyer psychology and purchase triggers
#   - Citation-backed niche expertise
#
# Graceful degradation: if NotebookLM is unavailable, opportunities pass
# through unchanged so the pipeline continues without research enrichment.
# =============================================================================

import json
import subprocess
import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
_workflow = os.path.dirname(_here)
_project_root = os.path.dirname(os.path.dirname(_workflow))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_tool import BaseTool


class NotebookLmResearchTool(BaseTool):
    """Enriches opportunities with grounded NotebookLM research.

    Uses the notebooklm-mcp-cli `nlm` CLI to query niche notebooks
    and attach citation-backed insights to each opportunity before
    Claude generates listing content.
    """

    def execute(self, **kwargs) -> dict:
        opportunities = kwargs.get("opportunities", [])
        notebook_ids = kwargs.get("notebook_ids", {})
        focus_niche = kwargs.get("focus_niche", "tattoo")
        enable_research = kwargs.get("enable_research", True)

        if not enable_research:
            return {
                "success": True,
                "data": opportunities,
                "error": None,
                "tool_name": self.get_name(),
                "metadata": {"skipped": True, "reason": "research disabled"},
            }

        if not opportunities:
            return {
                "success": False,
                "data": None,
                "error": "No opportunities to enrich",
                "tool_name": self.get_name(),
                "metadata": {},
            }

        try:
            # Check if nlm CLI is available
            if not self._check_nlm_available():
                print("     NotebookLM CLI not available, passing through unchanged")
                return {
                    "success": True,
                    "data": opportunities,
                    "error": None,
                    "tool_name": self.get_name(),
                    "metadata": {
                        "skipped": True,
                        "reason": "nlm CLI not installed or not authenticated",
                        "enriched_count": 0,
                        "total": len(opportunities),
                    },
                }

            notebook_id = notebook_ids.get(focus_niche, "")
            if not notebook_id:
                print(f"     No notebook ID configured for niche '{focus_niche}', passing through")
                return {
                    "success": True,
                    "data": opportunities,
                    "error": None,
                    "tool_name": self.get_name(),
                    "metadata": {
                        "skipped": True,
                        "reason": f"no notebook_id for niche '{focus_niche}'",
                        "enriched_count": 0,
                        "total": len(opportunities),
                    },
                }

            enriched = []
            enriched_count = 0

            for i, opp in enumerate(opportunities, 1):
                title = opp.get("product_title", "")
                keywords = opp.get("target_keywords", [])
                why = opp.get("why", "")

                print(f"     Researching {i}/{len(opportunities)}: {title[:50]}...",
                      flush=True)

                query = self._build_research_query(title, keywords, why, focus_niche)
                research = self._query_notebook(notebook_id, query)

                enriched_opp = dict(opp)
                if research:
                    enriched_opp["research_context"] = research
                    enriched_count += 1
                    print(f"       -> Enriched with {len(research.get('insights', ''))} char insights",
                          flush=True)
                else:
                    print(f"       -> No research returned", flush=True)

                enriched.append(enriched_opp)

            return {
                "success": True,
                "data": enriched,
                "error": None,
                "tool_name": self.get_name(),
                "metadata": {
                    "enriched_count": enriched_count,
                    "total": len(opportunities),
                    "enrichment_rate": enriched_count / len(opportunities) if opportunities else 0,
                    "notebook_id": notebook_id,
                    "niche": focus_niche,
                },
            }

        except Exception as e:
            # Graceful degradation: return original opportunities on any error
            return {
                "success": True,
                "data": opportunities,
                "error": None,
                "tool_name": self.get_name(),
                "metadata": {
                    "skipped": True,
                    "reason": f"error during research: {str(e)}",
                    "exception_type": type(e).__name__,
                    "enriched_count": 0,
                    "total": len(opportunities),
                },
            }

    def _check_nlm_available(self):
        """Check if the nlm CLI is installed and authenticated."""
        try:
            result = subprocess.run(
                ["nlm", "login", "--check"],
                capture_output=True, text=True, timeout=10,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _build_research_query(self, title, keywords, why, niche):
        """Build a research query for NotebookLM."""
        kw_str = ", ".join(keywords[:5]) if keywords else ""
        return (
            f"I'm creating a digital template product for {niche} businesses: "
            f'"{title}". '
            f"Keywords: {kw_str}. "
            f"Context: {why}. "
            f"Please provide: "
            f"1) Key market insights about this product type in the {niche} industry. "
            f"2) What language and terms do {niche} business owners use when searching for this? "
            f"3) What are the top pain points this product solves? "
            f"4) Any keyword gaps or positioning opportunities?"
        )

    def _query_notebook(self, notebook_id, query):
        """Query a NotebookLM notebook via the nlm CLI.

        Returns a research_context dict or None on failure.
        """
        try:
            result = subprocess.run(
                ["nlm", "query", notebook_id, query, "--format", "json"],
                capture_output=True, text=True, timeout=60,
            )

            if result.returncode != 0:
                return None

            response = json.loads(result.stdout)

            # Extract structured research from the response
            answer = response.get("answer", response.get("text", ""))
            citations = response.get("citations", [])

            if not answer:
                return None

            # Parse insights into structured format
            return {
                "insights": answer,
                "keywords": self._extract_keywords_from_insights(answer),
                "positioning": self._extract_positioning(answer),
                "citations": [c.get("source", "") for c in citations[:5]],
            }

        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
            return None

    def _extract_keywords_from_insights(self, insights):
        """Extract keyword suggestions from research insights."""
        keywords = []
        lower = insights.lower()
        # Look for keyword-related sections in the response
        for marker in ["keyword", "search term", "phrase", "tag"]:
            if marker in lower:
                # Find the sentence containing the marker
                for sentence in insights.split("."):
                    if marker in sentence.lower():
                        # Extract quoted terms
                        import re
                        quoted = re.findall(r'"([^"]+)"', sentence)
                        keywords.extend(quoted)
        return keywords[:10]

    def _extract_positioning(self, insights):
        """Extract positioning advice from research insights."""
        lower = insights.lower()
        for marker in ["position", "differentiat", "stand out", "unique", "competitive"]:
            if marker in lower:
                for sentence in insights.split("."):
                    if marker in sentence.lower():
                        return sentence.strip()
        return ""
