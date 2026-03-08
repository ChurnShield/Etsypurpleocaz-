# =============================================================================
# workflows/auto_listing_creator/tools/text_compositor.py
#
# Hybrid text compositor for Nano Banana hero images.
#
# Solves the AI typography problem: Gemini generates the flat-lay scene
# with blank/minimal cards, then this module overlays pixel-perfect text
# using Playwright (browser-quality rendering with Google Fonts) composited
# onto the scene via Pillow.
#
# Why Playwright instead of Pillow for text?
#   - Sub-pixel anti-aliasing (crisp at every size)
#   - Proper kerning and ligatures from Google Fonts
#   - CSS letter-spacing, line-height, text-shadow — all native
#   - Identical rendering quality to the Tier 2 HTML pipeline
#
# The result is a hero image with professional AI photography AND
# browser-quality typography — the best of both worlds.
# =============================================================================

import os

from tools.design_constants import (
    IMG_W, IMG_H, BAND_H, ACCENT_ORANGE, BRAND_PURPLE, FONTS_CSS, esc,
)


# ---- Card text layout definitions -------------------------------------------

CARD_TEXT_LAYOUTS = {
    "appointment card": {
        "front": {
            "title": "Appointment Card",
            "fields": ["NAME:", "DATE:", "TIME:", "DAY:"],
        },
        "back": {
            "title": "Book Appointment",
            "fields": ["EMAIL:", "PHONE:", "WEBSITE:"],
        },
    },
    "gift certificate": {
        "front": {
            "title": "Gift Certificate",
            "fields": ["TO:", "FROM:", "AMOUNT:", "EXPIRES:"],
        },
    },
    "gift voucher": {
        "front": {
            "title": "Gift Voucher",
            "fields": ["RECIPIENT:", "AMOUNT:", "FROM:", "VALID UNTIL:"],
        },
    },
    "price list": {
        "front": {
            "title": "Price List",
            "fields": ["SERVICE:", "PRICE:", "SERVICE:", "PRICE:"],
        },
    },
    "service menu": {
        "front": {
            "title": "Service Menu",
            "fields": ["SERVICE:", "PRICE:", "SERVICE:", "PRICE:"],
        },
    },
    "business card": {
        "front": {
            "title": "Business Card",
            "fields": ["NAME:", "PHONE:", "EMAIL:", "WEBSITE:"],
        },
        "back": {
            "title": "Contact Details",
            "fields": ["PHONE:", "EMAIL:", "WEBSITE:", "ADDRESS:"],
        },
    },
    "aftercare card": {
        "front": {
            "title": "Aftercare Instructions",
            "fields": ["STEP 1:", "STEP 2:", "STEP 3:"],
        },
    },
    "branding bundle": {
        "front": {
            "title": "Branding Bundle",
            "fields": ["STUDIO:", "TAGLINE:", "PHONE:", "EMAIL:"],
        },
    },
    "consent form": {
        "front": {
            "title": "Consent Form",
            "fields": ["CLIENT NAME:", "DATE:", "SIGNATURE:"],
        },
    },
}


def _get_card_layout(product_type):
    """Look up card text layout for a product type."""
    pt_lower = product_type.lower().strip()
    for key, layout in CARD_TEXT_LAYOUTS.items():
        if key in pt_lower:
            return layout
    return {
        "front": {
            "title": product_type.title(),
            "fields": ["NAME:", "DATE:", "PHONE:", "EMAIL:"],
        },
    }


def composite_text_on_hero(gemini_image_path, product_type, niche,
                           hero_title, tagline, output_path,
                           browser=None):
    """Overlay pixel-perfect text onto a Gemini-generated flat-lay scene.

    Uses Playwright to render text overlays as transparent PNGs with
    browser-quality font rendering (sub-pixel anti-aliasing, proper
    kerning, Google Fonts via CSS). Then composites them onto the
    Gemini scene using Pillow.

    The Gemini image should contain:
      - Top 70%: flat-lay scene with BLANK white cards (no text),
        props, beige background
      - Bottom 30%: solid black footer banner area (no text)

    This function adds:
      - Card text (script title + sans-serif field labels + underlines)
      - Footer banner text (hero title + tagline)
      - "EDIT IN CANVA" badge

    Args:
        gemini_image_path: Path to the raw Gemini scene image.
        product_type: e.g. "appointment card"
        niche: e.g. "tattoo"
        hero_title: Bold title for the footer banner.
        tagline: Subtitle for the footer banner.
        output_path: Where to save the composited hero image.
        browser: Playwright browser instance (reuses existing connection).
                 If None, creates and closes its own.

    Returns:
        output_path on success, None on failure.
    """
    try:
        from PIL import Image
    except ImportError:
        print("       ERROR: Pillow not installed", flush=True)
        return None

    own_browser = False
    try:
        # If no browser provided, create one
        if browser is None:
            try:
                from playwright.sync_api import sync_playwright
                pw = sync_playwright().start()
                browser = pw.chromium.launch(headless=True)
                own_browser = True
            except Exception as e:
                print(f"       Playwright not available: {e}", flush=True)
                return _fallback_pillow_composite(
                    gemini_image_path, product_type, niche,
                    hero_title, tagline, output_path,
                )

        # Open and resize the Gemini scene to Etsy dimensions
        scene = Image.open(gemini_image_path).convert("RGBA")
        scene = scene.resize((IMG_W, IMG_H), Image.LANCZOS)

        # ---- Render card text overlay (transparent PNG) ---------------------
        layout = _get_card_layout(product_type)
        front = layout.get("front", {})

        if front:
            card_overlay_path = output_path + ".card_overlay.png"
            _render_card_overlay(browser, front, card_overlay_path)

            card_overlay = Image.open(card_overlay_path).convert("RGBA")
            # Position: centred in the top 70% scene area
            showcase_h = IMG_H - BAND_H
            paste_x = (IMG_W - card_overlay.width) // 2
            paste_y = int(showcase_h * 0.12)
            scene.paste(card_overlay, (paste_x, paste_y), card_overlay)
            card_overlay.close()
            _cleanup(card_overlay_path)

        # ---- Render footer banner overlay -----------------------------------
        banner_overlay_path = output_path + ".banner_overlay.png"
        _render_banner_overlay(
            browser, hero_title, tagline, banner_overlay_path,
        )

        banner_overlay = Image.open(banner_overlay_path).convert("RGBA")
        banner_y = IMG_H - BAND_H
        # Ensure the black banner is solid (in case Gemini was imperfect)
        from PIL import ImageDraw
        draw = ImageDraw.Draw(scene)
        draw.rectangle([(0, banner_y), (IMG_W, IMG_H)], fill=(0, 0, 0, 255))
        scene.paste(banner_overlay, (0, banner_y), banner_overlay)
        banner_overlay.close()
        _cleanup(banner_overlay_path)

        # ---- Render badge overlay -------------------------------------------
        badge_overlay_path = output_path + ".badge_overlay.png"
        badge_size = 240
        _render_badge_overlay(browser, badge_size, badge_overlay_path)

        badge_overlay = Image.open(badge_overlay_path).convert("RGBA")
        badge_x = IMG_W - badge_size - 120
        badge_y = banner_y - badge_size // 2
        scene.paste(badge_overlay, (badge_x, badge_y), badge_overlay)
        badge_overlay.close()
        _cleanup(badge_overlay_path)

        # ---- Save final composite -------------------------------------------
        output = scene.convert("RGB")
        output.save(output_path, "PNG")
        output.close()
        scene.close()

        size_kb = os.path.getsize(output_path) // 1024
        print(f"       Text composited: {os.path.basename(output_path)} "
              f"({size_kb}KB)", flush=True)
        return output_path

    except Exception as e:
        print(f"       Text composite error: {e}", flush=True)
        return None

    finally:
        if own_browser and browser:
            try:
                browser.close()
                pw.stop()
            except Exception:
                pass


def _render_card_overlay(browser, card_layout, output_path):
    """Render card text as a transparent PNG via Playwright.

    Produces a cropped image containing just the card title, divider,
    and form fields — ready to paste onto the scene.
    """
    from config import PLAYWRIGHT_PAGE_TIMEOUT_MS

    title = esc(card_layout.get("title", ""))
    fields = card_layout.get("fields", [])

    fields_html = "\n".join(
        f'<div class="field">'
        f'  <span class="label">{esc(f)}</span>'
        f'  <span class="line"></span>'
        f'</div>'
        for f in fields
    )

    # Card overlay dimensions (matches the white card area in the scene)
    card_w = int(IMG_W * 0.56)
    card_h = int((IMG_H - BAND_H) * 0.62)

    html = f'''<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
{FONTS_CSS}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{
    width: {card_w}px;
    height: {card_h}px;
    overflow: hidden;
    background: transparent;
}}
body {{
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: {int(card_h * 0.06)}px {int(card_w * 0.10)}px;
}}
.title {{
    font-family: 'Great Vibes', cursive;
    font-size: 52px;
    color: #282828;
    text-align: center;
    margin-bottom: {int(card_h * 0.04)}px;
}}
.divider {{
    width: 50%;
    height: 2px;
    background: #666;
    margin-bottom: {int(card_h * 0.04)}px;
    position: relative;
}}
.divider::after {{
    content: '';
    position: absolute;
    left: 50%;
    top: 50%;
    width: 10px;
    height: 10px;
    background: #666;
    transform: translate(-50%, -50%) rotate(45deg);
}}
.fields {{
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: {int(card_h * 0.06)}px;
}}
.field {{
    display: flex;
    align-items: baseline;
    gap: 12px;
}}
.label {{
    font-family: 'Montserrat', sans-serif;
    font-weight: 700;
    font-size: 22px;
    color: #3C3C3C;
    white-space: nowrap;
    letter-spacing: 1px;
}}
.line {{
    flex: 1;
    height: 0;
    border-bottom: 2px solid #8C8C8C;
}}
</style></head><body>
<div class="title">{title}</div>
<div class="divider"></div>
<div class="fields">
    {fields_html}
</div>
</body></html>'''

    page = browser.new_page(
        viewport={"width": card_w, "height": card_h},
        device_scale_factor=1,
    )
    page.set_content(html, wait_until="networkidle", timeout=PLAYWRIGHT_PAGE_TIMEOUT_MS)
    page.wait_for_timeout(1500)
    page.screenshot(
        path=output_path,
        clip={"x": 0, "y": 0, "width": card_w, "height": card_h},
        omit_background=True,
    )
    page.close()


def _render_banner_overlay(browser, hero_title, tagline, output_path):
    """Render footer banner text as a transparent PNG via Playwright."""
    from config import PLAYWRIGHT_PAGE_TIMEOUT_MS

    html = f'''<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Montserrat:wght@400;600&display=swap');
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{
    width: {IMG_W}px;
    height: {BAND_H}px;
    overflow: hidden;
    background: transparent;
}}
body {{
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 40px 160px;
    gap: 25px;
}}
.title {{
    font-family: 'Playfair Display', serif;
    font-size: 86px;
    font-weight: 900;
    color: #FFFFFF;
    line-height: 1.15;
    letter-spacing: 2px;
}}
.tagline {{
    font-family: 'Montserrat', sans-serif;
    font-size: 28px;
    font-weight: 600;
    color: #CCCCCC;
    letter-spacing: 4px;
    text-transform: uppercase;
}}
</style></head><body>
<div class="title">{esc(hero_title)}</div>
<div class="tagline">{esc(tagline)}</div>
</body></html>'''

    page = browser.new_page(
        viewport={"width": IMG_W, "height": BAND_H},
        device_scale_factor=1,
    )
    page.set_content(html, wait_until="networkidle", timeout=PLAYWRIGHT_PAGE_TIMEOUT_MS)
    page.wait_for_timeout(1500)
    page.screenshot(
        path=output_path,
        clip={"x": 0, "y": 0, "width": IMG_W, "height": BAND_H},
        omit_background=True,
    )
    page.close()


def _render_badge_overlay(browser, size, output_path):
    """Render the EDIT IN CANVA badge as a transparent PNG via Playwright."""
    from config import PLAYWRIGHT_PAGE_TIMEOUT_MS

    html = f'''<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@600;800&display=swap');
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{
    width: {size}px;
    height: {size}px;
    overflow: hidden;
    background: transparent;
}}
.badge {{
    width: {size}px;
    height: {size}px;
    border-radius: 50%;
    background: {ACCENT_ORANGE};
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 2px;
}}
.top {{
    font-family: 'Montserrat', sans-serif;
    font-size: 30px;
    font-weight: 600;
    color: white;
    letter-spacing: 2px;
}}
.bottom {{
    font-family: 'Montserrat', sans-serif;
    font-size: 44px;
    font-weight: 800;
    color: white;
    letter-spacing: 3px;
}}
</style></head><body>
<div class="badge">
    <div class="top">EDIT IN</div>
    <div class="bottom">CANVA</div>
</div>
</body></html>'''

    page = browser.new_page(
        viewport={"width": size, "height": size},
        device_scale_factor=1,
    )
    page.set_content(html, wait_until="networkidle", timeout=PLAYWRIGHT_PAGE_TIMEOUT_MS)
    page.wait_for_timeout(1000)
    page.screenshot(
        path=output_path,
        clip={"x": 0, "y": 0, "width": size, "height": size},
        omit_background=True,
    )
    page.close()


def _cleanup(path):
    """Remove a temporary file silently."""
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


def _fallback_pillow_composite(gemini_image_path, product_type, niche,
                               hero_title, tagline, output_path):
    """Fallback: basic Pillow text rendering if Playwright is unavailable.

    Lower quality than the Playwright path but still better than
    AI-generated text.
    """
    from PIL import Image, ImageDraw, ImageFont

    img = Image.open(gemini_image_path).convert("RGB")
    img = img.resize((IMG_W, IMG_H), Image.LANCZOS)
    draw = ImageDraw.Draw(img)

    # Use default font — no external downloads needed for fallback
    try:
        font_large = ImageFont.truetype("DejaVuSans-Bold", 72)
        font_medium = ImageFont.truetype("DejaVuSans", 28)
    except Exception:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()

    # Black footer banner
    banner_y = IMG_H - BAND_H
    draw.rectangle([(0, banner_y), (IMG_W, IMG_H)], fill=(0, 0, 0))

    # Hero title
    bbox = draw.textbbox((0, 0), hero_title, font=font_large)
    tw = bbox[2] - bbox[0]
    draw.text(
        ((IMG_W - tw) / 2, banner_y + BAND_H * 0.30),
        hero_title, font=font_large, fill=(255, 255, 255),
    )

    # Tagline
    bbox = draw.textbbox((0, 0), tagline, font=font_medium)
    tw = bbox[2] - bbox[0]
    draw.text(
        ((IMG_W - tw) / 2, banner_y + BAND_H * 0.55),
        tagline, font=font_medium, fill=(200, 200, 200),
    )

    img.save(output_path, "PNG")
    img.close()

    print(f"       Text composited (fallback): "
          f"{os.path.basename(output_path)}", flush=True)
    return output_path
