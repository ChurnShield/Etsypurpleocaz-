# =============================================================================
# workflows/auto_listing_creator/tools/product_creator_tool.py
#
# Slim BaseTool orchestrator for professional product image creation.
#
# Two-tier design strategy:
#   Tier 1 (Nano Banana): AI-generated mockups + editable PDF (premium products)
#   Tier 2 (HTML/Playwright): existing HTML template pipeline (utility products)
#
# Delegates rendering to image_renderer, compositing to image_compositor,
# and constants/templates to their own modules.
# =============================================================================

import os
import sys
import time
import shutil

_here = os.path.dirname(os.path.abspath(__file__))
_workflow = os.path.dirname(_here)
_project_root = os.path.dirname(os.path.dirname(_workflow))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_tool import BaseTool

from tools.design_constants import EXPORT_DIR, THEME_ACCENTS, safe_filename
from tools.image_renderer import (
    render_template, render_band, render_badge, create_page2, create_pdf,
)
from tools.image_compositor import composite_hero, copy_boilerplate_pages
from tools.tier_config import classify_tier, TIER_1, BADGE_TEXT
from tools.gemini_image_client import generate_product_image, build_product_prompt
from tools.editable_pdf_generator import create_editable_pdf
from tools.affiliate_guide_generator import create_affiliate_guide


class ProductCreatorTool(BaseTool):
    """Create professional listing images + PDF.

    Routes products through two tiers:
      Tier 1 (Nano Banana): Gemini AI mockup + editable PDF
      Tier 2 (HTML/Playwright): HTML template + Playwright screenshot
    """

    def execute(self, **kwargs) -> dict:
        listings = kwargs.get("generated_listings", [])
        focus_niche = kwargs.get("focus_niche", "tattoo")
        theme = kwargs.get("theme", "dark")
        gemini_api_key = kwargs.get("gemini_api_key", "")

        if not listings:
            return {
                "success": False, "data": None,
                "error": "No listings to create products for",
                "tool_name": self.get_name(), "metadata": {},
            }

        try:
            from playwright.sync_api import sync_playwright

            os.makedirs(EXPORT_DIR, exist_ok=True)

            all_exports = []
            image_map = {}
            pdf_map = {}

            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)

                for i, listing in enumerate(listings):
                    title = listing.get("title", "Untitled")[:60]
                    product_type = listing.get("product_type", "Gift Certificate")
                    tier = classify_tier(product_type)

                    tier_label = "Nano Banana" if tier == TIER_1 else "HTML"
                    print(f"     Creating product {i+1}/{len(listings)} "
                          f"[{tier_label}]: {title}...", flush=True)

                    try:
                        if tier == TIER_1 and gemini_api_key:
                            result = self._create_tier1_listing(
                                browser, listing, focus_niche, theme,
                                gemini_api_key, i,
                            )
                        else:
                            if tier == TIER_1 and not gemini_api_key:
                                print("       No Gemini key — falling "
                                      "back to HTML pipeline", flush=True)
                            result = self._create_tier2_listing(
                                browser, listing, focus_niche, theme, i,
                            )

                        png_paths = result["png_paths"]
                        pdf_path = result["pdf_path"]

                        guide_path = result.get("guide_path")
                        export_result = {
                            "listing_index": i, "title": title,
                            "product_type": product_type,
                            "tier": tier,
                            "png_paths": png_paths,
                            "pdf_path": pdf_path,
                            "guide_path": guide_path,
                            "page_count": len(png_paths),
                            "status": "CREATED",
                        }
                        all_exports.append(export_result)
                        image_map[i] = png_paths
                        if pdf_path:
                            pdf_map[i] = pdf_path

                        tier_detail = "editable PDF" if result.get("has_editable_pdf") else "PDF"
                        print(f"       {len(png_paths)} images + {tier_detail} created",
                              flush=True)

                    except Exception as e:
                        print(f"       FAILED: {str(e)[:100]}", flush=True)
                        all_exports.append({
                            "listing_index": i, "title": title,
                            "product_type": product_type,
                            "tier": tier,
                            "png_paths": [], "pdf_path": None,
                            "page_count": 0, "status": "FAILED",
                        })

                    if i < len(listings) - 1:
                        time.sleep(1)

                browser.close()

            created_count = sum(1 for e in all_exports if e["status"] == "CREATED")

            return {
                "success": True,
                "data": {
                    "exports": all_exports,
                    "image_map": image_map,
                    "pdf_map": pdf_map,
                    "created_count": created_count,
                    "total_listings": len(listings),
                    "export_dir": EXPORT_DIR,
                },
                "error": None,
                "tool_name": self.get_name(),
                "metadata": {"created": created_count, "total": len(listings)},
            }

        except Exception as e:
            return {
                "success": False, "data": None,
                "error": str(e),
                "tool_name": self.get_name(),
                "metadata": {"exception_type": type(e).__name__},
            }

    # ---- Tier 1: Nano Banana + Editable PDF -----------------------------------

    def _create_tier1_listing(self, browser, listing, niche, theme,
                              gemini_api_key, index):
        """Create listing images using Gemini AI mockup + editable PDF.

        The Gemini image is a complete product photo (background, cards,
        props, footer banner, badge) so it is used directly as the hero
        — no dark-background compositing needed.

        Falls back to Tier 2 HTML pipeline if Gemini generation fails.
        """
        from PIL import Image

        title = listing.get("title", "Template")
        safe_title = safe_filename(title)
        accent = THEME_ACCENTS.get(theme, THEME_ACCENTS["default"])
        product_type = listing.get("product_type", "Gift Certificate")

        # Derive hero text for the Gemini prompt footer banner
        hero_title = self._derive_hero_title(title, product_type, niche)
        tagline = self._derive_tagline(product_type, niche)

        # Step 1: Generate AI mockup via Gemini (complete scene)
        print("       Generating Nano Banana mockup...", flush=True)
        prompt = build_product_prompt(
            product_type, niche, theme,
            hero_title=hero_title, tagline=tagline,
        )
        gen_result = generate_product_image(gemini_api_key, prompt)

        if not gen_result["success"]:
            print(f"       Gemini failed: {gen_result['error'][:80]}", flush=True)
            print("       Falling back to HTML pipeline...", flush=True)
            return self._create_tier2_listing(
                browser, listing, niche, theme, index,
            )

        # Step 2: Save raw mockup
        mockup_path = os.path.join(EXPORT_DIR, f"{safe_title}_mockup.png")
        with open(mockup_path, "wb") as f:
            f.write(gen_result["image_bytes"])
        print(f"       Mockup saved: {os.path.basename(mockup_path)} "
              f"({len(gen_result['image_bytes']) // 1024}KB)", flush=True)

        # Step 3: Resize Gemini image to Etsy dimensions (2250x3000)
        # The Gemini output is already a complete product photo with
        # background, cards, props, footer banner, and badge — so we
        # just resize to the correct Etsy listing dimensions.
        print("       Resizing hero to Etsy dimensions...", flush=True)
        hero_path = os.path.join(EXPORT_DIR, f"{safe_title}_page1.png")
        img = Image.open(mockup_path).convert("RGB")
        from tools.design_constants import IMG_W, IMG_H
        img_resized = img.resize((IMG_W, IMG_H), Image.LANCZOS)
        img_resized.save(hero_path, "PNG")
        img_resized.close()
        img.close()
        print(f"       Hero saved: {os.path.basename(hero_path)}", flush=True)

        # Step 4: Create page 2 (What You Get — tier-aware)
        print("       Creating page 2...", flush=True)
        page2_path = create_page2(
            browser, listing, mockup_path, niche, accent, safe_title,
            tier=TIER_1,
        )

        # Step 5: Copy boilerplate pages 3-5
        png_paths = [hero_path, page2_path]
        png_paths.extend(copy_boilerplate_pages(safe_title))

        # Step 6: Create editable PDF (buyer-facing deliverable)
        print("       Creating editable PDF...", flush=True)
        listing_with_niche = dict(listing, focus_niche=niche)
        pdf_result = create_editable_pdf(
            listing_with_niche, product_type, mockup_path,
            gemini_api_key=gemini_api_key,
        )

        pdf_path = None
        if pdf_result["success"]:
            pdf_path = pdf_result["pdf_path"]
        else:
            print(f"       Editable PDF failed: {pdf_result['error'][:80]}",
                  flush=True)
            pdf_path = create_pdf(browser, listing, niche)

        # Step 7: Create affiliate Getting Started guide
        print("       Creating Getting Started guide...", flush=True)
        guide_result = create_affiliate_guide(listing, product_type, TIER_1)
        guide_path = guide_result.get("pdf_path") if guide_result["success"] else None

        return {
            "png_paths": png_paths,
            "pdf_path": pdf_path,
            "guide_path": guide_path,
            "has_editable_pdf": pdf_result["success"],
        }

    # ---- Tier 2: HTML/Playwright (existing pipeline) --------------------------

    def _create_tier2_listing(self, browser, listing, niche, theme, index):
        """Create all 5 listing images using HTML templates + Playwright."""
        title = listing.get("title", "Template")
        safe_title = safe_filename(title)
        accent = THEME_ACCENTS.get(theme, THEME_ACCENTS["default"])

        product_type = listing.get("product_type", "Gift Certificate")
        hero_title = self._derive_hero_title(title, product_type, niche)
        tagline = self._derive_tagline(product_type, niche)

        # Step 1: Render template design
        print("       Rendering template design...", flush=True)
        template_path = render_template(
            browser, listing, niche, accent, safe_title,
        )

        # Copy template to canva_designs/ for easy Canva upload
        canva_dir = os.path.join(EXPORT_DIR, "canva_designs")
        os.makedirs(canva_dir, exist_ok=True)
        if template_path and os.path.exists(template_path):
            shutil.copy2(
                template_path,
                os.path.join(canva_dir, os.path.basename(template_path)),
            )

        # Step 2: Render bottom band
        print("       Rendering title band...", flush=True)
        band_path = render_band(
            browser, hero_title, tagline, accent["band"], safe_title,
        )

        # Step 3: Render badge
        badge_path = render_badge(browser, "EDIT IN", "CANVA", safe_title)

        # Step 4: Composite hero image (page 1)
        print("       Compositing hero image...", flush=True)
        hero_path = composite_hero(
            template_path, band_path, badge_path, safe_title,
        )

        # Step 5: Create page 2 (What You Get)
        print("       Creating page 2...", flush=True)
        page2_path = create_page2(
            browser, listing, template_path, niche, accent, safe_title,
        )

        # Step 6: Copy boilerplate pages 3-5
        png_paths = [hero_path, page2_path]
        png_paths.extend(copy_boilerplate_pages(safe_title))

        # Step 7: Standard Playwright PDF
        pdf_path = create_pdf(browser, listing, niche)

        # Step 8: Create affiliate Getting Started guide
        from tools.tier_config import TIER_2
        print("       Creating Getting Started guide...", flush=True)
        guide_result = create_affiliate_guide(listing, product_type, TIER_2)
        guide_path = guide_result.get("pdf_path") if guide_result["success"] else None

        return {
            "png_paths": png_paths,
            "pdf_path": pdf_path,
            "guide_path": guide_path,
            "has_editable_pdf": False,
        }

    # ---- Shared helpers -------------------------------------------------------

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
