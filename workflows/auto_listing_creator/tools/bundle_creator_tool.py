# =============================================================================
# workflows/auto_listing_creator/tools/bundle_creator_tool.py
#
# Anti-Gravity: Automatic Bundle Creator
#
# Groups individual product listings into value bundles that:
#   - Increase Average Order Value (AOV) without creating new designs
#   - Cross-pollinate traffic between related listings
#   - Signal "topical authority" to Etsy's algorithm
#   - Create higher-priced listings that rank differently in search
#
# Bundle strategy:
#   - Groups products by bundle_tags (from GenerateListingContentTool)
#   - Creates "Starter Kit", "Complete Bundle", and "Mega Pack" tiers
#   - Generates unique bundle titles/descriptions via Claude
#   - Prices bundles at 60-70% of individual total (perceived value)
# =============================================================================

import json
import time
import urllib.request
import urllib.error
import sys
import os
from collections import defaultdict

_here = os.path.dirname(os.path.abspath(__file__))
_workflow = os.path.dirname(_here)
_project_root = os.path.dirname(os.path.dirname(_workflow))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_tool import BaseTool

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"

# Bundle tier definitions
BUNDLE_TIERS = {
    "starter": {
        "min_items": 3,
        "max_items": 5,
        "discount": 0.35,  # 35% off individual total
        "name_suffix": "Starter Kit",
    },
    "complete": {
        "min_items": 5,
        "max_items": 10,
        "discount": 0.40,  # 40% off individual total
        "name_suffix": "Complete Bundle",
    },
    "mega": {
        "min_items": 10,
        "max_items": 25,
        "discount": 0.45,  # 45% off individual total
        "name_suffix": "Mega Pack",
    },
}


class BundleCreatorTool(BaseTool):
    """Group individual listings into value bundles for higher AOV."""

    def execute(self, **kwargs) -> dict:
        listings      = kwargs.get("generated_listings", [])
        api_key       = kwargs.get("anthropic_api_key", "")
        model         = kwargs.get("model", "claude-sonnet-4-20250514")
        focus_niche   = kwargs.get("focus_niche", "tattoo")
        currency      = kwargs.get("currency", "GBP")
        min_bundle    = kwargs.get("min_bundle_size", 3)

        if not listings:
            return {
                "success": True,
                "data": {"bundles": [], "stats": {"bundles_created": 0}},
                "error": None,
                "tool_name": self.get_name(),
                "metadata": {"reason": "no_listings"},
            }

        try:
            # -- Group listings by bundle_tags --
            tag_groups = defaultdict(list)
            for i, listing in enumerate(listings):
                bundle_tags = listing.get("bundle_tags", [])
                if not bundle_tags:
                    # Infer bundle tag from product_type
                    pt = listing.get("product_type", "").lower().strip()
                    if pt:
                        bundle_tags = [pt.replace(" ", "-")]
                for tag in bundle_tags:
                    tag_groups[tag.lower().strip()].append(i)

            print(f"     Bundle grouping: {len(tag_groups)} categories found",
                  flush=True)
            for tag, indices in sorted(tag_groups.items(),
                                        key=lambda x: -len(x[1])):
                print(f"       {tag}: {len(indices)} products", flush=True)

            # -- Create bundles from groups with enough items --
            bundles = []
            used_indices = set()

            for tag, indices in sorted(tag_groups.items(),
                                        key=lambda x: -len(x[1])):
                # Remove already-bundled items
                available = [i for i in indices if i not in used_indices]
                if len(available) < min_bundle:
                    continue

                # Determine best tier
                tier = self._select_tier(len(available))
                if not tier:
                    continue

                tier_cfg = BUNDLE_TIERS[tier]
                bundle_items = available[:tier_cfg["max_items"]]
                bundle_listings = [listings[i] for i in bundle_items]

                # Calculate bundle price
                individual_total = sum(
                    float(l.get("price", 4.99)) for l in bundle_listings
                )
                bundle_price = round(
                    individual_total * (1 - tier_cfg["discount"]), 2
                )
                # Floor at reasonable minimum
                bundle_price = max(bundle_price, 8.99)

                bundle = {
                    "bundle_tag": tag,
                    "tier": tier,
                    "item_indices": bundle_items,
                    "item_titles": [l["title"] for l in bundle_listings],
                    "item_count": len(bundle_items),
                    "individual_total": round(individual_total, 2),
                    "bundle_price": bundle_price,
                    "savings_pct": int(tier_cfg["discount"] * 100),
                    "focus_niche": focus_niche,
                    "currency": currency,
                }

                bundles.append(bundle)
                used_indices.update(bundle_items)

            print(f"     Bundles to create: {len(bundles)}", flush=True)

            # -- Generate bundle listing content via Claude --
            final_bundles = []
            for j, bundle in enumerate(bundles):
                print(f"     Generating bundle {j+1}/{len(bundles)}: "
                      f"{bundle['bundle_tag']} ({bundle['tier']})...",
                      flush=True)

                if api_key:
                    content = self._generate_bundle_content(
                        api_key, model, bundle, focus_niche, currency,
                    )
                    if content:
                        bundle.update(content)
                        final_bundles.append(bundle)
                        print(f"       -> {bundle.get('title', '?')[:50]}... "
                              f"({bundle['currency']}{bundle['bundle_price']})",
                              flush=True)
                    else:
                        print(f"       -> FAILED to generate content",
                              flush=True)
                else:
                    # Fallback: basic bundle without Claude
                    bundle["title"] = self._fallback_title(bundle, focus_niche)
                    bundle["description"] = self._fallback_description(bundle)
                    bundle["tags"] = self._fallback_tags(bundle, focus_niche)
                    final_bundles.append(bundle)

                if j < len(bundles) - 1:
                    time.sleep(1)

            return {
                "success": True,
                "data": {
                    "bundles": final_bundles,
                    "stats": {
                        "bundles_created": len(final_bundles),
                        "total_items_bundled": len(used_indices),
                        "unbundled_items": len(listings) - len(used_indices),
                    },
                },
                "error": None,
                "tool_name": self.get_name(),
                "metadata": {
                    "bundles": len(final_bundles),
                    "items_bundled": len(used_indices),
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

    def _select_tier(self, count):
        """Select the best bundle tier for the item count."""
        if count >= BUNDLE_TIERS["mega"]["min_items"]:
            return "mega"
        if count >= BUNDLE_TIERS["complete"]["min_items"]:
            return "complete"
        if count >= BUNDLE_TIERS["starter"]["min_items"]:
            return "starter"
        return None

    def _generate_bundle_content(self, api_key, model, bundle,
                                  focus_niche, currency):
        """Use Claude to generate bundle listing content."""
        tier_cfg = BUNDLE_TIERS[bundle["tier"]]
        items_list = "\n".join(
            f"  - {t}" for t in bundle["item_titles"]
        )

        prompt = f"""You are an expert Etsy seller. Generate a BUNDLE listing for a {focus_niche} template bundle called a "{tier_cfg['name_suffix']}".

BUNDLE DETAILS:
  Category: {bundle['bundle_tag']}
  Items included ({bundle['item_count']}):
{items_list}
  Individual total: {currency}{bundle['individual_total']}
  Bundle price: {currency}{bundle['bundle_price']} (Save {bundle['savings_pct']}%)

REQUIREMENTS:
1. TITLE (max 140 chars): Must include "{tier_cfg['name_suffix']}", the niche, and "Editable". Front-load the highest-value keyword. Example: "{focus_niche.title()} Studio {tier_cfg['name_suffix']}, Editable Canva Templates, {bundle['item_count']} Professional Templates"

2. DESCRIPTION: Write a value-focused bundle description:
   - Opening: Emphasise the savings and value proposition
   - WHAT'S INCLUDED: List every item with bullet points
   - PERFECT FOR: 3-5 use cases for who needs this bundle
   - WHY A BUNDLE: Explain the cost savings vs buying individually
   - HOW TO EDIT: Brief Canva instructions
   - FAQ: 2 questions about the bundle
   - PLEASE NOTE: Digital download disclaimer

3. TAGS: 13 tags (max 20 chars each), focused on bundle/kit search terms

RESPOND IN EXACT JSON:
{{
  "title": "Bundle title (max 140 chars)",
  "description": "Full description",
  "tags": ["tag1", "tag2", ..., "tag13"],
  "product_type": "bundle"
}}"""

        try:
            payload = json.dumps({
                "model": model,
                "max_tokens": 4096,
                "messages": [{"role": "user", "content": prompt}],
            }).encode("utf-8")

            req = urllib.request.Request(
                ANTHROPIC_API_URL, data=payload, method="POST",
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

            return self._parse_bundle_response(text)

        except Exception:
            return None

    def _parse_bundle_response(self, text):
        """Parse Claude's JSON response for a bundle listing."""
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(
                lines[1:-1] if lines[-1].strip() == "```" else lines[1:]
            )
            text = text.strip()

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
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

        return {
            "title": parsed["title"][:140],
            "description": parsed.get("description", ""),
            "tags": [t[:20] for t in parsed.get("tags", [])[:13]],
            "product_type": parsed.get("product_type", "bundle"),
        }

    # -- Fallback generators (no Claude needed) --------------------------------

    def _fallback_title(self, bundle, focus_niche):
        tier_cfg = BUNDLE_TIERS[bundle["tier"]]
        title = (
            f"{focus_niche.title()} {bundle['bundle_tag'].replace('-', ' ').title()} "
            f"{tier_cfg['name_suffix']}, {bundle['item_count']} Editable Canva Templates"
        )
        return title[:140]

    def _fallback_description(self, bundle):
        items = "\n".join(f"- {t}" for t in bundle["item_titles"])
        return (
            f"Save {bundle['savings_pct']}% with this professional template bundle!\n\n"
            f"WHAT'S INCLUDED ({bundle['item_count']} templates):\n{items}\n\n"
            f"Individual value: {bundle['currency']}{bundle['individual_total']}\n"
            f"Bundle price: {bundle['currency']}{bundle['bundle_price']}\n\n"
            f"All templates are fully editable in Canva (free account).\n\n"
            f"PLEASE NOTE: This is a digital download. No physical item will be shipped."
        )

    def _fallback_tags(self, bundle, focus_niche):
        tag_word = bundle["bundle_tag"].replace("-", " ")
        tags = [
            f"{focus_niche} bundle",
            f"{tag_word} bundle",
            f"{focus_niche} templates",
            "template bundle",
            "canva templates",
            "editable templates",
            f"{focus_niche} branding",
            "digital download",
            "small business kit",
            f"{focus_niche} starter kit",
            "printable templates",
            "business templates",
            "instant download",
        ]
        return [t[:20] for t in tags[:13]]
