# =============================================================================
# workflows/auto_listing_creator/tools/image_renderer.py
#
# Playwright-based rendering operations:
#   - render_template: dispatch to html_templates, screenshot -> PNG
#   - render_band:     title band screenshot -> PNG
#   - render_badge:    circular badge screenshot -> PNG
#   - create_page2:    "What You Get" infographic -> PNG
#   - create_pdf:      branded PDF digital download
# =============================================================================

import os
import base64
from io import BytesIO

from tools.design_constants import (
    EXPORT_DIR, IMG_W, IMG_H, BAND_H, TMPL_W, TMPL_H,
    BRAND_PURPLE, DARK_BG, ACCENT_ORANGE, FONTS_CSS,
    esc, safe_filename,
)
from tools.html_templates import (
    tmpl_appointment_card,
    tmpl_gift_certificate,
    tmpl_price_list,
    tmpl_aftercare_card,
    tmpl_generic,
)
from config import PLAYWRIGHT_PAGE_TIMEOUT_MS


def render_template(browser, listing, niche, accent, safe_title):
    """Render product-type-specific template design via Playwright."""
    product_type = listing.get("product_type", "Gift Certificate").lower()

    if "appointment" in product_type:
        html = tmpl_appointment_card()
    elif any(kw in product_type for kw in ("gift", "certificate", "voucher")):
        html = tmpl_gift_certificate()
    elif any(kw in product_type for kw in ("price", "menu", "service")):
        html = tmpl_price_list()
    elif "aftercare" in product_type:
        html = tmpl_aftercare_card()
    else:
        html = tmpl_generic(product_type)

    page = browser.new_page(
        viewport={"width": TMPL_W, "height": TMPL_H},
        device_scale_factor=1,
    )
    page.set_content(html, wait_until="networkidle", timeout=PLAYWRIGHT_PAGE_TIMEOUT_MS)
    page.wait_for_timeout(2000)

    path = os.path.join(EXPORT_DIR, f"{safe_title}_template.png")
    page.screenshot(
        path=path,
        clip={"x": 0, "y": 0, "width": TMPL_W, "height": TMPL_H},
    )
    page.close()
    return path


def render_band(browser, title, tagline, band_color, safe_title):
    """Render the bottom title band via Playwright with gradient and ornaments."""
    html = f'''<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Montserrat:wght@400;600;700&display=swap');
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:{IMG_W}px; height:{BAND_H}px; overflow:hidden; }}
body {{
    background: linear-gradient(180deg, {band_color} 0%, #0E0C12 100%);
    display: flex; flex-direction: column;
    justify-content: center; align-items: center;
    text-align: center; padding: 40px 160px; gap: 20px;
    position: relative;
}}
/* Top edge gold accent line */
body::before {{
    content: ''; position: absolute; top: 0; left: 10%; right: 10%;
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(201,168,76,0.5), transparent);
}}
.ornament {{
    display: flex; align-items: center; gap: 16px;
    margin-bottom: 8px;
}}
.orn-line {{
    width: 80px; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(201,168,76,0.4), transparent);
}}
.orn-diamond {{
    width: 6px; height: 6px;
    background: rgba(201,168,76,0.5);
    transform: rotate(45deg);
}}
.title {{
    font-family: 'Playfair Display', serif;
    font-size: 88px; font-weight: 900;
    color: #FFFFFF; line-height: 1.1;
    letter-spacing: 3px;
    text-shadow: 0 2px 20px rgba(0,0,0,0.5);
}}
.tagline {{
    font-family: 'Montserrat', sans-serif;
    font-size: 24px; font-weight: 700;
    color: rgba(201,168,76,0.7); letter-spacing: 6px;
    text-transform: uppercase;
}}
</style></head><body>
<div class="ornament">
    <div class="orn-line"></div>
    <div class="orn-diamond"></div>
    <div class="orn-line"></div>
</div>
<div class="title">{esc(title)}</div>
<div class="tagline">{esc(tagline)}</div>
</body></html>'''

    page = browser.new_page(viewport={"width": IMG_W, "height": BAND_H})
    page.set_content(html, wait_until="networkidle", timeout=PLAYWRIGHT_PAGE_TIMEOUT_MS)
    page.wait_for_timeout(1500)

    path = os.path.join(EXPORT_DIR, f"{safe_title}_band.png")
    page.screenshot(
        path=path,
        clip={"x": 0, "y": 0, "width": IMG_W, "height": BAND_H},
    )
    page.close()
    return path


def render_badge(browser, text_top, text_bottom, safe_title):
    """Render an orange circular badge via Playwright."""
    size = 240
    html = f'''<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@600;800&display=swap');
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:{size}px; height:{size}px; overflow:hidden; background: transparent; }}
.badge {{
    width: {size}px; height: {size}px;
    border-radius: 50%;
    background: {ACCENT_ORANGE};
    display: flex; flex-direction: column;
    justify-content: center; align-items: center;
    gap: 2px;
}}
.top {{
    font-family: 'Montserrat', sans-serif;
    font-size: 30px; font-weight: 600;
    color: white; letter-spacing: 2px;
}}
.bottom {{
    font-family: 'Montserrat', sans-serif;
    font-size: 44px; font-weight: 800;
    color: white; letter-spacing: 3px;
}}
</style></head><body>
<div class="badge">
    <div class="top">{esc(text_top)}</div>
    <div class="bottom">{esc(text_bottom)}</div>
</div>
</body></html>'''

    page = browser.new_page(viewport={"width": size, "height": size})
    page.set_content(html, wait_until="networkidle", timeout=PLAYWRIGHT_PAGE_TIMEOUT_MS)
    page.wait_for_timeout(1000)

    path = os.path.join(EXPORT_DIR, f"{safe_title}_badge.png")
    page.screenshot(
        path=path,
        clip={"x": 0, "y": 0, "width": size, "height": size},
    )
    page.close()
    return path


def create_page2(browser, listing, template_path, niche, accent, safe_title,
                  tier=None):
    """Create page 2: professional dark 'What You Get' slide."""
    from PIL import Image
    from tools.tier_config import TIER_2, PAGE2_FEATURES, PAGE2_STEPS, PAGE2_PILLS

    template = Image.open(template_path).convert("RGBA")
    preview_h = int(900 * TMPL_H / TMPL_W)
    preview = template.resize((900, preview_h), Image.LANCZOS)
    template.close()

    buf = BytesIO()
    preview.save(buf, "PNG")
    tmpl_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    preview.close()

    product_type = listing.get("product_type", "Gift Certificate")
    effective_tier = tier or TIER_2

    # Build tier-aware content
    features = [f.format(product_type=esc(product_type))
                for f in PAGE2_FEATURES[effective_tier]]
    steps = PAGE2_STEPS[effective_tier]
    pills = PAGE2_PILLS[effective_tier]

    features_html = "\n    ".join(
        f'<div class="feat"><div class="feat-check">&#10003;</div>'
        f'<div class="feat-text">{f}</div></div>'
        for f in features
    )
    steps_html = "\n    ".join(
        f'<div class="how-step"><div class="step-circle">{i+1}</div>'
        f'<div class="step-label">{s}</div></div>'
        for i, s in enumerate(steps)
    )
    pills_html = "\n    ".join(
        f'<div class="pill">{p}</div>' for p in pills
    )

    html = f'''<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
{FONTS_CSS}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:{IMG_W}px; height:{IMG_H}px; overflow:hidden; }}
body {{
    font-family: 'Montserrat', sans-serif;
    background: {DARK_BG};
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    padding: 0 160px;
}}
.heading {{
    font-family: 'Oswald', sans-serif;
    font-size: 86px; font-weight: 700;
    color: #FFF; letter-spacing: 8px;
    text-transform: uppercase; text-align: center;
}}
.heading-line {{
    width: 100px; height: 3px;
    background: {ACCENT_ORANGE};
    margin: 20px auto 50px;
}}
.preview-img {{
    width: 900px; border-radius: 10px;
    border: 1px solid #333;
    box-shadow: 0 20px 60px rgba(0,0,0,0.6);
    margin-bottom: 55px;
}}
.features {{
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 32px 80px; width: 100%;
    max-width: 1600px; margin-bottom: 55px;
}}
.feat {{ display: flex; align-items: center; gap: 18px; }}
.feat-check {{
    width: 48px; height: 48px;
    background: {ACCENT_ORANGE}; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; color: white;
    font-size: 24px; font-weight: 700;
}}
.feat-text {{ font-size: 30px; color: #DDD; font-weight: 500; }}
.how-heading {{
    font-family: 'Oswald', sans-serif;
    font-size: 50px; font-weight: 700;
    color: #FFF; letter-spacing: 6px;
    text-transform: uppercase; margin-bottom: 35px;
}}
.how-steps {{ display: flex; gap: 60px; margin-bottom: 50px; }}
.how-step {{
    display: flex; flex-direction: column;
    align-items: center; gap: 14px;
    max-width: 380px;
}}
.step-circle {{
    width: 64px; height: 64px;
    border: 3px solid {ACCENT_ORANGE};
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Oswald', sans-serif;
    font-size: 28px; font-weight: 700;
    color: {ACCENT_ORANGE};
}}
.step-label {{
    font-size: 22px; color: #AAA;
    text-align: center; line-height: 1.4;
}}
.pills {{ display: flex; gap: 24px; }}
.pill {{
    background: transparent;
    border: 2px solid #444; border-radius: 50px;
    padding: 14px 36px; font-size: 20px;
    font-weight: 700; color: #888;
    letter-spacing: 2px; text-transform: uppercase;
}}
</style></head><body>

<div class="heading">What You Get</div>
<div class="heading-line"></div>

<img class="preview-img" src="data:image/png;base64,{tmpl_b64}" alt="preview">

<div class="features">
    {features_html}
</div>

<div class="how-heading">How It Works</div>
<div class="how-steps">
    {steps_html}
</div>

<div class="pills">
    {pills_html}
</div>

</body></html>'''

    page = browser.new_page(
        viewport={"width": IMG_W, "height": IMG_H},
        device_scale_factor=1,
    )
    page.set_content(html, wait_until="networkidle", timeout=PLAYWRIGHT_PAGE_TIMEOUT_MS)
    page.wait_for_timeout(2000)

    path = os.path.join(EXPORT_DIR, f"{safe_title}_page2.png")
    page.screenshot(
        path=path,
        clip={"x": 0, "y": 0, "width": IMG_W, "height": IMG_H},
    )
    page.close()
    return path


def create_pdf(browser, listing, niche):
    """Generate a branded PDF digital download via Playwright."""
    title = listing.get("title", "Template")
    safe_title_str = safe_filename(title)
    product_type = listing.get("product_type", "Gift Certificate")

    html = f'''<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Montserrat:wght@300;400;600&family=Great+Vibes&display=swap');
* {{ margin:0; padding:0; box-sizing:border-box; }}
@page {{ size: A4; margin: 0; }}
body {{
    font-family: 'Montserrat', sans-serif;
    background: #FFFFFF;
    color: #333;
    width: 210mm; min-height: 297mm;
    padding: 30mm 25mm;
    display: flex; flex-direction: column;
    align-items: center;
}}
.logo-area {{
    text-align: center;
    margin-bottom: 20mm;
}}
.brand-name {{
    font-family: 'Great Vibes', cursive;
    font-size: 48px;
    color: {BRAND_PURPLE};
    margin-bottom: 5mm;
}}
.brand-sub {{
    font-size: 14px;
    color: #888;
    letter-spacing: 3px;
    text-transform: uppercase;
}}
.divider {{
    width: 60mm; height: 2px;
    background: {BRAND_PURPLE};
    margin: 10mm auto;
}}
.section-title {{
    font-family: 'Playfair Display', serif;
    font-size: 28px;
    color: #333;
    text-align: center;
    margin-bottom: 8mm;
}}
.section-subtitle {{
    font-size: 14px;
    color: #666;
    text-align: center;
    margin-bottom: 12mm;
    line-height: 1.6;
}}
.link-box {{
    background: #F8F5FA;
    border: 2px solid {BRAND_PURPLE};
    border-radius: 8px;
    padding: 8mm 12mm;
    margin-bottom: 6mm;
    width: 100%;
    max-width: 150mm;
}}
.link-label {{
    font-size: 13px;
    color: {BRAND_PURPLE};
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 3mm;
}}
.link-url {{
    font-size: 15px;
    color: #333;
    word-break: break-all;
}}
.link-url a {{
    color: {BRAND_PURPLE};
    text-decoration: underline;
}}
.instructions {{
    margin-top: 12mm;
    width: 100%;
    max-width: 150mm;
}}
.step {{
    display: flex; gap: 4mm;
    margin-bottom: 4mm;
    font-size: 13px;
    line-height: 1.5;
}}
.step-num {{
    background: {BRAND_PURPLE};
    color: white;
    width: 24px; height: 24px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 600;
    flex-shrink: 0;
}}
.footer-note {{
    margin-top: auto;
    text-align: center;
    font-size: 11px;
    color: #999;
    padding-top: 15mm;
}}
.footer-note a {{ color: {BRAND_PURPLE}; }}
</style></head><body>

<div class="logo-area">
    <div class="brand-name">PurpleOcaz</div>
    <div class="brand-sub">Premium Digital Templates</div>
</div>

<div class="divider"></div>

<div class="section-title">Your Template Links</div>
<div class="section-subtitle">
    Thank you for your purchase! Click the links below to<br>
    open your editable templates in Canva.
</div>

<div class="link-box">
    <div class="link-label">{esc(product_type)} Template (A4 Size)</div>
    <div class="link-url">
        <a href="#">https://www.canva.com/design/your-template-a4</a>
    </div>
</div>

<div class="link-box">
    <div class="link-label">{esc(product_type)} Template (US Letter Size)</div>
    <div class="link-url">
        <a href="#">https://www.canva.com/design/your-template-letter</a>
    </div>
</div>

<div class="link-box">
    <div class="link-label">Print Layout Sheet (3-Up)</div>
    <div class="link-url">
        <a href="#">https://www.canva.com/design/your-print-layout</a>
    </div>
</div>

<div class="instructions">
    <div class="section-title" style="font-size:20px; margin-bottom:6mm;">How to Edit Your Template</div>
    <div class="step"><div class="step-num">1</div><div>Click the template link above. It will open directly in Canva.</div></div>
    <div class="step"><div class="step-num">2</div><div>You will need a free Canva account (canva.com). Sign up if you don't have one.</div></div>
    <div class="step"><div class="step-num">3</div><div>Click "Use this template" to create your own editable copy.</div></div>
    <div class="step"><div class="step-num">4</div><div>Customise with your business name, logo, colours, photos and text.</div></div>
    <div class="step"><div class="step-num">5</div><div>Download as PDF or JPG. Use "PDF Print" with bleed &amp; crop marks for best results.</div></div>
    <div class="step"><div class="step-num">6</div><div>Print at home or at your local print shop. Enjoy!</div></div>
</div>

<div class="footer-note">
    Need help? Watch our video tutorial: <a href="#">Tutorial Link</a><br><br>
    &copy; PurpleOcaz &mdash; Thank you for supporting a small business!
</div>

</body></html>'''

    page = browser.new_page(viewport={"width": 794, "height": 1123})
    page.set_content(html, wait_until="networkidle", timeout=PLAYWRIGHT_PAGE_TIMEOUT_MS)
    page.wait_for_timeout(2000)

    path = os.path.join(EXPORT_DIR, f"{safe_title_str}_download.pdf")
    page.pdf(
        path=path,
        format="A4",
        print_background=True,
        margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
    )
    page.close()

    if os.path.exists(path):
        size_kb = os.path.getsize(path) // 1024
        print(f"       PDF: {os.path.basename(path)} ({size_kb}KB)", flush=True)
        return path
    return None
