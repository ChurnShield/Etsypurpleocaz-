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
import urllib.error
import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
_workflow = os.path.dirname(_here)
_project_root = os.path.dirname(os.path.dirname(_workflow))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_tool import BaseTool

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"

# =============================================================================
# Anti-Gravity: Niche-specific long-tail keyword strategies
#
# Each niche has curated keyword research data:
#   - long_tail_examples: proven high-intent, low-competition search terms
#   - buyer_intent_modifiers: words that signal purchase readiness
#   - product_categories: canonical product types for bundle grouping
# =============================================================================
NICHE_KEYWORD_STRATEGIES = {
    "tattoo": {
        "long_tail_examples": [
            "tattoo gift card", "ink studio voucher",
            "tattoo consent form", "aftercare card template",
            "tattoo price list", "tattoo appointment card",
            "tattoo business card", "tattoo studio branding",
            "tattoo waiver form", "tattoo client intake",
            "flash sheet template", "tattoo social media",
        ],
        "buyer_intent_modifiers": [
            "editable", "printable", "instant download",
            "canva template", "professional", "custom",
            "small business", "studio", "shop owner",
        ],
        "product_categories": [
            "gift certificate", "gift voucher", "consent form",
            "aftercare card", "price list", "service menu",
            "business card", "appointment card", "intake form",
            "flash sheet", "social media template", "branding bundle",
            "waiver form", "release form", "instagram template",
        ],
    },
    "nail": {
        "long_tail_examples": [
            "nail salon gift card", "nail tech voucher",
            "nail price list", "nail service menu",
            "nail salon branding", "nail appointment card",
            "nail tech business card", "manicure gift card",
            "nail art price list", "nail studio template",
        ],
        "buyer_intent_modifiers": [
            "editable", "printable", "instant download",
            "canva template", "nail tech", "salon owner",
            "small business", "professional", "custom",
        ],
        "product_categories": [
            "gift certificate", "gift voucher", "price list",
            "service menu", "business card", "appointment card",
            "social media template", "branding bundle",
            "consent form", "client card", "instagram template",
        ],
    },
    "hair": {
        "long_tail_examples": [
            "hair salon gift card", "hairdresser voucher",
            "barber price list", "salon service menu",
            "hair stylist branding", "salon appointment card",
            "barber business card", "salon social media",
            "hairstylist gift card", "barber shop template",
        ],
        "buyer_intent_modifiers": [
            "editable", "printable", "instant download",
            "canva template", "salon owner", "barber shop",
            "small business", "professional", "stylist",
        ],
        "product_categories": [
            "gift certificate", "gift voucher", "price list",
            "service menu", "business card", "appointment card",
            "social media template", "branding bundle",
            "consultation form", "client card", "instagram template",
        ],
    },
    "beauty": {
        "long_tail_examples": [
            "beauty salon gift card", "spa voucher template",
            "esthetician price list", "beauty service menu",
            "lash tech business card", "beauty appointment card",
            "spa branding bundle", "facial gift certificate",
            "waxing consent form", "beauty social media",
        ],
        "buyer_intent_modifiers": [
            "editable", "printable", "instant download",
            "canva template", "esthetician", "spa owner",
            "lash tech", "beauty professional", "custom",
        ],
        "product_categories": [
            "gift certificate", "gift voucher", "price list",
            "service menu", "business card", "appointment card",
            "consent form", "social media template", "branding bundle",
            "aftercare card", "client intake form", "instagram template",
        ],
    },
    "default": {
        "long_tail_examples": [
            "small business template", "editable gift card",
            "business branding kit", "printable price list",
            "service menu template", "appointment card",
            "business card template", "social media kit",
        ],
        "buyer_intent_modifiers": [
            "editable", "printable", "instant download",
            "canva template", "professional", "custom",
            "small business", "shop owner", "branding",
        ],
        "product_categories": [
            "gift certificate", "gift voucher", "price list",
            "service menu", "business card", "appointment card",
            "social media template", "branding bundle",
            "consent form", "intake form", "instagram template",
        ],
    },
}


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
        """Build a Claude prompt for generating a complete Etsy listing.

        Anti-Gravity keyword strategy:
        - Long-tail keywords with high purchase intent, low competition
        - Niche-specific buyer language (what shop owners actually search)
        - Dwell-time optimised descriptions with FAQs and use cases
        - Bundle-ready product_type classification for auto-bundling
        """
        target_kws = ", ".join(opportunity.get("target_keywords", []))

        # Build niche-specific keyword guidance
        niche_kw_guidance = NICHE_KEYWORD_STRATEGIES.get(
            focus_niche, NICHE_KEYWORD_STRATEGIES["default"]
        )
        kw_examples = ", ".join(f'"{kw}"' for kw in niche_kw_guidance["long_tail_examples"][:6])
        buyer_intent = ", ".join(f'"{bi}"' for bi in niche_kw_guidance["buyer_intent_modifiers"][:6])
        product_categories = ", ".join(f'"{pc}"' for pc in niche_kw_guidance["product_categories"][:8])

        return f"""You are an expert Etsy seller specializing in digital Canva templates for the {focus_niche} industry. You have a shop called "PurpleOcaz" that sells editable templates.

PRODUCT IDEA:
  Title suggestion: {opportunity.get('product_title', '')}
  Why this is an opportunity: {opportunity.get('why', '')}
  Suggested price: {opportunity.get('suggested_price', 4.99)} {currency}
  Priority: {opportunity.get('priority', '')}
  Target keywords: {target_kws}

TASK: Generate a COMPLETE Etsy listing for this product. This is a digital Canva template that buyers can edit in Canva.

KEYWORD STRATEGY (critical for Etsy algorithm ranking):
- Use LONG-TAIL keywords with HIGH PURCHASE INTENT and LOW competition
- Think about what a {focus_niche} business owner types into Etsy search when READY TO BUY
- Avoid generic single-word tags — every tag should be 2-4 words
- Examples of good long-tail tags for this niche: {kw_examples}
- Buyer intent modifiers to weave in: {buyer_intent}
- Product categories in this niche: {product_categories}

REQUIREMENTS:
1. TITLE (max 140 chars): Front-load the highest-intent long-tail keyword phrase. Include "Editable", the template format, and the product type. Separate keyword phrases with commas. Example: "Tattoo Gift Certificate Template, Editable Voucher for Tattoo Studio, Printable Gift Card"

2. DESCRIPTION: Write a conversion-optimised Etsy description with these sections:
   - Opening hook (2-3 sentences — address the buyer's problem, e.g. "Looking for a professional way to offer gift certificates at your {focus_niche} studio?")
   - WHAT'S INCLUDED section (bullet points)
   - HOW TO EDIT section (Canva instructions)
   - FEATURES section (bullet points)
   - PERFECT FOR section (3-5 specific use cases — this increases dwell time)
   - FAQ section (2-3 common questions with answers — increases dwell time and reduces returns)
   - PLEASE NOTE section (digital download disclaimer)
   Use emoji sparingly (1-2 max). Keep it professional.

3. TAGS: Exactly 13 tags, each max 20 characters. Apply this tag formula:
   - Tags 1-3: Core product + niche (e.g. "tattoo gift card", "tattoo voucher")
   - Tags 4-6: Format + modifier (e.g. "editable template", "canva template", "printable voucher")
   - Tags 7-9: Buyer intent + occasion (e.g. "last minute gift", "business branding", "client gift")
   - Tags 10-11: Adjacent niche terms (e.g. "ink studio", "body art gift")
   - Tags 12-13: Seasonal or trending angles (e.g. "holiday gift card", "small business")

4. PRICE: Suggested price in {currency}

5. PRODUCT_TYPE: A precise product category label from this list: {product_categories}. This is used for auto-bundling related products.

6. BUNDLE_TAGS: 2-3 category tags for grouping this product into bundles (e.g. ["gift-certificates", "client-facing", "tattoo-studio-essentials"])

RESPOND IN EXACT JSON FORMAT:
{{
  "title": "Your listing title here (max 140 chars)",
  "description": "Full description text with line breaks",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8", "tag9", "tag10", "tag11", "tag12", "tag13"],
  "price": 4.99,
  "product_type": "Precise product category label",
  "bundle_tags": ["category-tag-1", "category-tag-2"]
}}"""

    def _call_claude(self, api_key, model, prompt):
        """Call the Anthropic Claude API with retry/backoff on 529 (overloaded)."""
        payload = json.dumps({
            "model": model,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}],
        }).encode("utf-8")

        max_attempts = 4
        for attempt in range(1, max_attempts + 1):
            req = urllib.request.Request(ANTHROPIC_API_URL, data=payload, method="POST")
            req.add_header("x-api-key", api_key)
            req.add_header("anthropic-version", "2023-06-01")
            req.add_header("Content-Type", "application/json")

            try:
                with urllib.request.urlopen(req, timeout=120) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                content = data.get("content", [])
                for block in content:
                    if block.get("type") == "text":
                        return block.get("text", "")
                return ""
            except urllib.error.HTTPError as e:
                if e.code == 529 and attempt < max_attempts:
                    wait = 15 * attempt  # 15s, 30s, 45s
                    print(f"       API overloaded (529), waiting {wait}s "
                          f"(attempt {attempt}/{max_attempts})...", flush=True)
                    time.sleep(wait)
                    continue
                raise

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
            "bundle_tags": parsed.get("bundle_tags", []),
            "source_rank": opportunity.get("rank", 0),
            "source_priority": opportunity.get("priority", ""),
            "source_effort": opportunity.get("effort", ""),
            "source_why": opportunity.get("why", ""),
        }
