# =============================================================================
# workflows/auto_listing_creator/tools/generate_listing_content_tool.py
#
# Phase 2: Uses Claude to generate complete Etsy listing content for each
# product opportunity:
#   - Optimised title (max 140 chars, SEO-friendly)
#   - Full description (Etsy-formatted, with sections)
#   - 13 unique tags (max 20 chars each, long-tail)
#   - Suggested price
# =============================================================================

import json
import time
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


class GenerateListingContentTool(BaseTool):
    """Use Claude to generate complete Etsy listing content."""

    def execute(self, **kwargs) -> dict:
        opportunities = kwargs.get("opportunities", [])
        api_key       = kwargs.get("anthropic_api_key", "")
        model         = kwargs.get("model", "claude-sonnet-4-20250514")
        focus_niche   = kwargs.get("focus_niche", "tattoo")
        currency      = kwargs.get("currency", "GBP")

        if not api_key:
            return {
                "success": False, "data": None,
                "error": "anthropic_api_key required",
                "tool_name": self.get_name(), "metadata": {},
            }

        if not opportunities:
            return {
                "success": False, "data": None,
                "error": "No opportunities to generate listings for",
                "tool_name": self.get_name(), "metadata": {},
            }

        try:
            all_listings = []

            # Process each opportunity individually for best quality
            for i, opp in enumerate(opportunities, 1):
                print(f"     Generating listing {i}/{len(opportunities)}: "
                      f"{opp.get('product_title', '')[:50]}...", flush=True)

                prompt = self._build_prompt(opp, focus_niche, currency)
                response = self._call_claude(api_key, model, prompt)
                listing = self._parse_response(response, opp)

                if listing:
                    all_listings.append(listing)
                    print(f"       -> Generated ({len(listing.get('tags', []))} tags)", flush=True)
                else:
                    print(f"       -> FAILED to parse", flush=True)

                # Rate limit
                if i < len(opportunities):
                    time.sleep(1)

            return {
                "success": True,
                "data": {
                    "generated_listings": all_listings,
                    "stats": {
                        "total_opportunities": len(opportunities),
                        "listings_generated": len(all_listings),
                        "failed": len(opportunities) - len(all_listings),
                    },
                },
                "error": None,
                "tool_name": self.get_name(),
                "metadata": {
                    "generated": len(all_listings),
                    "total": len(opportunities),
                },
            }

        except Exception as e:
            return {
                "success": False, "data": None,
                "error": str(e),
                "tool_name": self.get_name(),
                "metadata": {"exception_type": type(e).__name__},
            }

    def _build_prompt(self, opportunity, focus_niche, currency):
        """Build a Claude prompt for generating a complete Etsy listing."""
        target_kws = ", ".join(opportunity.get("target_keywords", []))

        return f"""You are an expert Etsy seller specializing in digital Canva templates for the {focus_niche} industry. You have a shop called "PurpleOcaz" that sells editable templates.

PRODUCT IDEA:
  Title suggestion: {opportunity.get('product_title', '')}
  Why this is an opportunity: {opportunity.get('why', '')}
  Suggested price: {opportunity.get('suggested_price', 4.99)} {currency}
  Priority: {opportunity.get('priority', '')}
  Target keywords: {target_kws}

TASK: Generate a COMPLETE Etsy listing for this product. This is a digital Canva template that buyers can edit in Canva.

REQUIREMENTS:
1. TITLE (max 140 chars): SEO-optimised, front-load the most important keywords. Include "Editable", "Canva Template", and the product type. Example format: "Tattoo Gift Certificate Template, Editable Canva Voucher, Tattoo Studio Gift Card"

2. DESCRIPTION: Write a compelling Etsy description with these sections:
   - Opening hook (2-3 sentences about the product)
   - WHAT'S INCLUDED section (bullet points)
   - HOW TO EDIT section (Canva instructions)
   - FEATURES section (bullet points)
   - PLEASE NOTE section (digital download disclaimer)
   Use emoji sparingly (1-2 max). Keep it professional.

3. TAGS: Exactly 13 tags, each max 20 characters. Long-tail, buyer-intent keywords. What would a {focus_niche} shop owner search for on Etsy?

4. PRICE: Suggested price in {currency}

RESPOND IN EXACT JSON FORMAT:
{{
  "title": "Your listing title here (max 140 chars)",
  "description": "Full description text with line breaks",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8", "tag9", "tag10", "tag11", "tag12", "tag13"],
  "price": 4.99,
  "product_type": "Brief product type label"
}}"""

    def _call_claude(self, api_key, model, prompt):
        """Call the Anthropic Claude API."""
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

        content = data.get("content", [])
        for block in content:
            if block.get("type") == "text":
                return block.get("text", "")
        return ""

    def _parse_response(self, response_text, opportunity):
        """Parse Claude's JSON response into a structured listing."""
        text = response_text.strip()

        # Handle markdown code blocks
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
            text = text.strip()

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON object
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                try:
                    parsed = json.loads(text[start:end])
                except json.JSONDecodeError:
                    return None
            else:
                return None

        if not parsed.get("title"):
            return None

        # Enforce constraints
        title = parsed["title"][:140]
        tags = [t[:20] for t in parsed.get("tags", [])[:13]]

        return {
            "title": title,
            "description": parsed.get("description", ""),
            "tags": tags,
            "price": parsed.get("price", opportunity.get("suggested_price", 4.99)),
            "product_type": parsed.get("product_type", ""),
            "source_rank": opportunity.get("rank", 0),
            "source_priority": opportunity.get("priority", ""),
            "source_effort": opportunity.get("effort", ""),
            "source_why": opportunity.get("why", ""),
        }
