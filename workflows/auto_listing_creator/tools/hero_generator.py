# =============================================================================
# workflows/auto_listing_creator/tools/hero_generator.py
#
# Standalone BaseTool for generating Etsy listing hero images (page 1).
#
# Two-tier hero generation:
#   Tier 1 (Nano Banana): Gemini AI flat-lay scene + text compositing
#   Tier 2 (HTML/Playwright): HTML template + dark-bg fanned-card composite
#
# Delegates rendering to image_renderer, compositing to image_compositor
# and text_compositor, and AI generation to gemini_image_client.
# =============================================================================

import os
import sys
import time

_here = os.path.dirname(os.path.abspath(__file__))
_workflow = os.path.dirname(_here)
_project_root = os.path.dirname(os.path.dirname(_workflow))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_tool import BaseTool

from tools.design_constants import (
    EXPORT_DIR, IMG_W, IMG_H, THEME_ACCENTS, safe_filename,
)
from tools.image_renderer import render_template, render_band, render_badge
from tools.image_compositor import composite_hero
from tools.text_compositor import composite_text_on_hero
from tools.tier_config import classify_tier, TIER_1, TIER_2, BADGE_TEXT
from tools.gemini_image_client import generate_product_image, build_product_prompt


class HeroGeneratorTool(BaseTool):
    """Generate a single hero image (page 1) for an Etsy listing.

    Routes through Tier 1 (Gemini AI + text compositing) or Tier 2
    (HTML template + Pillow compositing) based on product type.

    Required kwargs:
        listing (dict): Listing data with at least 'title' and 'product_type'.
        focus_niche (str): Niche keyword, e.g. 'tattoo'.

    Optional kwargs:
        theme (str): Theme name from THEME_ACCENTS. Default 'dark'.
        gemini_api_key (str): API key for Tier 1 Gemini generation.
        browser: Playwright browser instance (reused if provided).
    """

    def execute(self, **kwargs) -> dict:
        listing = kwargs.get("listing")
        focus_niche = kwargs.get("focus_niche", "tattoo")
        theme = kwargs.get("theme", "dark")
        gemini_api_key = kwargs.get("gemini_api_key", "")
        browser = kwargs.get("browser")

        if not listing:
            return {
                "success": False,
                "data": None,
                "error": "No listing provided",
                "tool_name": self.get_name(),
                "metadata": {},
            }

        title = listing.get("title", "Untitled")[:60]
        product_type = listing.get("product_type", "Gift Certificate")
        safe_title = safe_filename(title)
        tier = classify_tier(product_type)
        accent = THEME_ACCENTS.get(theme, THEME_ACCENTS["default"])

        hero_title = self._derive_hero_title(title, product_type, focus_niche)
        tagline = self._derive_tagline(product_type, focus_niche)

        os.makedirs(EXPORT_DIR, exist_ok=True)

        own_browser = False
        try:
            # Launch Playwright browser if not provided
            if browser is None:
                try:
                    from playwright.sync_api import sync_playwright
                    pw = sync_playwright().start()
                    browser = pw.chromium.launch(headless=True)
                    own_browser = True
                except Exception as e:
                    return {
                        "success": False,
                        "data": None,
                        "error": f"Playwright unavailable: {e}",
                        "tool_name": self.get_name(),
                        "metadata": {"tier": tier},
                    }

            # Route to the appropriate tier
            if tier == TIER_1 and gemini_api_key:
                hero_path, mockup_path = self._generate_tier1_hero(
                    browser, listing, product_type, focus_niche,
                    theme, gemini_api_key, safe_title,
                    hero_title, tagline,
                )
            else:
                if tier == TIER_1 and not gemini_api_key:
                    print("       HeroGenerator: No Gemini key — "
                          "falling back to HTML pipeline", flush=True)
                hero_path = self._generate_tier2_hero(
                    browser, listing, focus_niche, accent,
                    safe_title, hero_title, tagline,
                )
                mockup_path = None

            if not hero_path or not os.path.exists(hero_path):
                return {
                    "success": False,
                    "data": None,
                    "error": "Hero image generation failed — no output file",
                    "tool_name": self.get_name(),
                    "metadata": {"tier": tier, "safe_title": safe_title},
                }

            size_kb = os.path.getsize(hero_path) // 1024
            return {
                "success": True,
                "data": {
                    "hero_path": hero_path,
                    "mockup_path": mockup_path,
                    "tier": tier,
                    "hero_title": hero_title,
                    "tagline": tagline,
                    "safe_title": safe_title,
                    "size_kb": size_kb,
                },
                "error": None,
                "tool_name": self.get_name(),
                "metadata": {
                    "tier": tier,
                    "product_type": product_type,
                    "size_kb": size_kb,
                },
            }

        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": str(e),
                "tool_name": self.get_name(),
                "metadata": {"exception_type": type(e).__name__, "tier": tier},
            }

        finally:
            if own_browser and browser:
                try:
                    browser.close()
                    pw.stop()
                except Exception:
                    pass

    # ---- Tier 1: Gemini AI + text compositing --------------------------------

    def _generate_tier1_hero(self, browser, listing, product_type,
                             niche, theme, gemini_api_key, safe_title,
                             hero_title, tagline):
        """Generate hero via Gemini AI flat-lay scene + text compositing.

        Returns (hero_path, mockup_path) tuple.
        Falls back to Tier 2 if Gemini fails.
        """
        print("       HeroGenerator: Generating Nano Banana mockup...",
              flush=True)

        prompt = build_product_prompt(
            product_type, niche, theme,
            hero_title=hero_title, tagline=tagline,
        )
        gen_result = generate_product_image(gemini_api_key, prompt)

        if not gen_result["success"]:
            print(f"       HeroGenerator: Gemini failed: "
                  f"{gen_result['error'][:80]}", flush=True)
            print("       HeroGenerator: Falling back to HTML pipeline...",
                  flush=True)
            accent = THEME_ACCENTS.get(theme, THEME_ACCENTS["default"])
            hero_path = self._generate_tier2_hero(
                browser, listing, niche, accent,
                safe_title, hero_title, tagline,
            )
            return hero_path, None

        # Save raw mockup (blank cards, no text)
        mockup_path = os.path.join(EXPORT_DIR, f"{safe_title}_mockup.png")
        with open(mockup_path, "wb") as f:
            f.write(gen_result["image_bytes"])
        print(f"       HeroGenerator: Mockup saved: "
              f"{os.path.basename(mockup_path)} "
              f"({len(gen_result['image_bytes']) // 1024}KB)", flush=True)

        # Composite text onto the Gemini scene using real fonts
        print("       HeroGenerator: Compositing text with real fonts...",
              flush=True)
        hero_path = os.path.join(EXPORT_DIR, f"{safe_title}_page1.png")
        composite_result = composite_text_on_hero(
            mockup_path, product_type, niche,
            hero_title=hero_title, tagline=tagline,
            output_path=hero_path, browser=browser,
        )

        if not composite_result:
            # Fallback: resize raw Gemini image to Etsy dimensions
            print("       HeroGenerator: Text composite failed, "
                  "using raw mockup...", flush=True)
            from PIL import Image
            img = Image.open(mockup_path).convert("RGB")
            img_resized = img.resize((IMG_W, IMG_H), Image.LANCZOS)
            img_resized.save(hero_path, "PNG")
            img_resized.close()
            img.close()

        print(f"       HeroGenerator: Hero saved: "
              f"{os.path.basename(hero_path)}", flush=True)
        return hero_path, mockup_path

    # ---- Tier 2: HTML template + Pillow compositing --------------------------

    def _generate_tier2_hero(self, browser, listing, niche, accent,
                             safe_title, hero_title, tagline):
        """Generate hero via HTML template rendering + dark-bg composite.

        Returns hero_path string.
        """
        # Render the product template
        print("       HeroGenerator: Rendering template design...", flush=True)
        template_path = render_template(
            browser, listing, niche, accent, safe_title,
        )

        # Render bottom title band
        print("       HeroGenerator: Rendering title band...", flush=True)
        band_path = render_band(
            browser, hero_title, tagline, accent["band"], safe_title,
        )

        # Render badge
        badge_top, badge_bottom = BADGE_TEXT.get(TIER_2, ("EDIT IN", "CANVA"))
        badge_path = render_badge(browser, badge_top, badge_bottom, safe_title)

        # Composite hero (dark bg + fanned cards + band + badge)
        print("       HeroGenerator: Compositing hero image...", flush=True)
        hero_path = composite_hero(
            template_path, band_path, badge_path, safe_title,
        )

        print(f"       HeroGenerator: Hero saved: "
              f"{os.path.basename(hero_path)}", flush=True)
        return hero_path

    # ---- Shared helpers ------------------------------------------------------

    def _derive_hero_title(self, full_title, product_type, niche):
        """Derive a short, punchy title for the hero image band."""
        skip_words = {
            "template", "editable", "canva", "instant", "download",
            "printable", "digital", "customizable", "customisable",
        }
        words = full_title.split(",")[0].strip().split()
        clean = [w for w in words if w.lower() not in skip_words]

        if len(clean) <= 5:
            return " ".join(clean)
        return " ".join(clean[:5])

    def _derive_tagline(self, product_type, niche):
        """Generate a tagline for the hero band."""
        taglines = {
            "gift certificate": "MAKE EXTRA INCOME SELLING GIFT CERTIFICATES",
            "price list": "SHOWCASE YOUR SERVICES WITH STYLE",
            "business card": "LEAVE A LASTING FIRST IMPRESSION",
            "appointment card": "KEEP YOUR CLIENTS COMING BACK",
            "aftercare card": "PROFESSIONAL AFTERCARE FOR YOUR CLIENTS",
            "social media": "GROW YOUR BUSINESS ON SOCIAL MEDIA",
            "branding bundle": "EVERYTHING YOUR STUDIO NEEDS IN ONE BUNDLE",
        }
        pt_lower = product_type.lower()
        for key, tagline in taglines.items():
            if key in pt_lower:
                return tagline
        return f"PROFESSIONAL {niche.upper()} TEMPLATES"
