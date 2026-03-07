# =============================================================================
# workflows/notebooklm_audio/tools/audio_product_packager_tool.py
#
# Phase 3: Packages audio files into Etsy-ready digital products.
# Generates listing content, creates cover art, and assembles product bundles.
# =============================================================================

import json
import sys
import os
import time
import urllib.request
import urllib.error

_here = os.path.dirname(os.path.abspath(__file__))
_workflow = os.path.dirname(_here)
_project_root = os.path.dirname(os.path.dirname(_workflow))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_tool import BaseTool

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"


class AudioProductPackagerTool(BaseTool):
    """Packages audio files into Etsy-ready digital products.

    For each audio file:
    - Generates optimised listing content (title, description, tags)
    - Prepares product metadata for Etsy publishing
    """

    def execute(self, **kwargs) -> dict:
        audio_products = kwargs.get("audio_products", [])
        anthropic_api_key = kwargs.get("anthropic_api_key", "")
        model = kwargs.get("model", "claude-sonnet-4-20250514")
        currency = kwargs.get("currency", "GBP")
        default_price = kwargs.get("default_price", 3.99)
        bundle_with_templates = kwargs.get("bundle_with_templates", True)

        if not audio_products:
            return {
                "success": False,
                "data": None,
                "error": "No audio products to package",
                "tool_name": self.get_name(),
                "metadata": {},
            }

        if not anthropic_api_key:
            return {
                "success": False,
                "data": None,
                "error": "anthropic_api_key required",
                "tool_name": self.get_name(),
                "metadata": {},
            }

        try:
            packaged = []
            failed = 0

            for i, product in enumerate(audio_products, 1):
                niche = product.get("niche", "business")
                audio_path = product.get("audio_path", "")

                print(f"     Packaging audio product {i}/{len(audio_products)}: "
                      f"{niche} guide...", flush=True)

                # Generate listing content via Claude
                listing = self._generate_audio_listing(
                    anthropic_api_key, model, niche, currency, default_price,
                )

                if not listing:
                    print(f"       -> Failed to generate listing content", flush=True)
                    failed += 1
                    continue

                listing["audio_path"] = audio_path
                listing["niche"] = niche
                listing["is_audio_product"] = True

                if bundle_with_templates:
                    listing["bundle_tags"] = [
                        f"{niche}-audio-guide",
                        f"{niche}-business-essentials",
                        "audio-product",
                    ]

                packaged.append(listing)
                print(f"       -> Packaged: {listing['title'][:50]}...", flush=True)

                if i < len(audio_products):
                    time.sleep(1)

            return {
                "success": len(packaged) > 0,
                "data": {
                    "packaged_products": packaged,
                    "stats": {
                        "packaged": len(packaged),
                        "failed": failed,
                        "total": len(audio_products),
                    },
                },
                "error": None if packaged else "No products packaged",
                "tool_name": self.get_name(),
                "metadata": {
                    "packaged": len(packaged),
                    "failed": failed,
                },
            }

        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": str(e),
                "tool_name": self.get_name(),
                "metadata": {"exception_type": type(e).__name__},
            }

    def _generate_audio_listing(self, api_key, model, niche, currency, default_price):
        """Generate Etsy listing content for an audio product."""
        prompt = f"""You are an expert Etsy seller. Generate a listing for an AUDIO GUIDE digital product.

PRODUCT: A professionally narrated audio guide for {niche} business owners.
FORMAT: Digital audio download (MP3/WAV)
NICHE: {niche} industry
CURRENCY: {currency}

This audio guide covers essential business topics for {niche} professionals:
- Setting up and branding your {niche} business
- Client management and professional documentation
- Marketing strategies and seasonal promotions
- Tips from industry experts

REQUIREMENTS:
1. TITLE (max 140 chars): Include "Audio Guide", the niche, and buyer-intent keywords
2. DESCRIPTION: Etsy-formatted with WHAT'S INCLUDED, PERFECT FOR, FAQ sections
3. TAGS: Exactly 13 tags (max 20 chars each), targeting {niche} business owners looking for audio guides
4. PRICE: Suggested in {currency} (around {default_price})

RESPOND IN EXACT JSON:
{{
  "title": "Title here",
  "description": "Description here",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8", "tag9", "tag10", "tag11", "tag12", "tag13"],
  "price": {default_price}
}}"""

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

            if not text:
                return None

            # Parse JSON (handle markdown code blocks)
            text = text.strip()
            if text.startswith("```"):
                lines = text.split("\n")
                text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
                text = text.strip()

            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                start = text.find("{")
                end = text.rfind("}") + 1
                if start >= 0 and end > start:
                    parsed = json.loads(text[start:end])
                else:
                    return None

            if not parsed.get("title"):
                return None

            return {
                "title": parsed["title"][:140],
                "description": parsed.get("description", ""),
                "tags": [t[:20] for t in parsed.get("tags", [])[:13]],
                "price": parsed.get("price", default_price),
                "product_type": "audio_guide",
            }

        except Exception:
            return None
