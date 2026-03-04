#!/usr/bin/env python3
"""
Generate boilerplate listing images (pages 3-5) for Etsy product listings.

These are generic marketing pages reused across all products:
  Page 3: "How to Edit in Canva" step-by-step guide
  Page 4: "Perfect For" customer use cases
  Page 5: FAQ + support info

Run once to create the template images, then all products reference them.

Usage:
    python scripts/generate_boilerplate_pages.py
"""

import sys
import os

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _project_root)
sys.path.insert(1, os.path.join(_project_root, "workflows", "auto_listing_creator"))

from workflows.auto_listing_creator.tools.design_constants import (
    EXPORT_DIR, IMG_W, IMG_H, DARK_BG, BRAND_PURPLE, ACCENT_ORANGE, FONTS_CSS,
)
from config import PLAYWRIGHT_PAGE_TIMEOUT_MS


def _page3_how_to_edit():
    """Page 3: How to Edit in Canva — step-by-step visual guide."""
    return f'''<!DOCTYPE html>
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
    padding: 120px 160px;
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
    margin: 24px auto 70px;
}}
.steps {{
    display: flex; flex-direction: column;
    gap: 50px; width: 100%; max-width: 1700px;
}}
.step {{
    display: flex; align-items: flex-start; gap: 40px;
}}
.step-num {{
    width: 90px; height: 90px; flex-shrink: 0;
    border: 3px solid {ACCENT_ORANGE}; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Oswald', sans-serif;
    font-size: 40px; font-weight: 700; color: {ACCENT_ORANGE};
}}
.step-content {{ flex: 1; }}
.step-title {{
    font-family: 'Playfair Display', serif;
    font-size: 40px; font-weight: 700;
    color: #FFF; margin-bottom: 10px;
}}
.step-desc {{
    font-size: 28px; color: #AAA; line-height: 1.5;
}}
.footer-note {{
    margin-top: 70px;
    font-size: 26px; color: #666;
    text-align: center; letter-spacing: 2px;
}}
.footer-note span {{ color: {ACCENT_ORANGE}; font-weight: 600; }}
</style></head><body>

<div class="heading">How to Edit in Canva</div>
<div class="heading-line"></div>

<div class="steps">
    <div class="step">
        <div class="step-num">1</div>
        <div class="step-content">
            <div class="step-title">Open Your Template</div>
            <div class="step-desc">Click the Canva link in your downloaded PDF. It opens directly in your browser — no software to install.</div>
        </div>
    </div>
    <div class="step">
        <div class="step-num">2</div>
        <div class="step-content">
            <div class="step-title">Create Your Copy</div>
            <div class="step-desc">Click "Use this template" to save an editable copy to your free Canva account. No Canva Pro needed.</div>
        </div>
    </div>
    <div class="step">
        <div class="step-num">3</div>
        <div class="step-content">
            <div class="step-title">Customise Everything</div>
            <div class="step-desc">Add your business name, logo, colours, contact details, and photos. Drag, drop, and resize — it's that easy.</div>
        </div>
    </div>
    <div class="step">
        <div class="step-num">4</div>
        <div class="step-content">
            <div class="step-title">Download &amp; Print</div>
            <div class="step-desc">Export as PDF (for printing) or PNG (for digital use). Use "PDF Print" with crop marks for professional results.</div>
        </div>
    </div>
    <div class="step">
        <div class="step-num">5</div>
        <div class="step-content">
            <div class="step-title">Reuse Unlimited Times</div>
            <div class="step-desc">Edit and print as many copies as you need. Your template is yours to use forever for your business.</div>
        </div>
    </div>
</div>

<div class="footer-note">Works with <span>FREE</span> Canva accounts &bull; No design experience needed</div>

</body></html>'''


def _page4_perfect_for():
    """Page 4: Perfect For — customer use cases and target audience."""
    return f'''<!DOCTYPE html>
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
    padding: 120px 160px;
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
    margin: 24px auto 70px;
}}
.grid {{
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 50px 80px; width: 100%; max-width: 1700px;
}}
.card {{
    background: #1A1A1A;
    border-radius: 16px;
    padding: 50px 45px;
    border: 1px solid #2A2A2A;
}}
.card-icon {{
    font-size: 50px; margin-bottom: 20px;
}}
.card-title {{
    font-family: 'Playfair Display', serif;
    font-size: 34px; font-weight: 700;
    color: #FFF; margin-bottom: 12px;
}}
.card-desc {{
    font-size: 24px; color: #999; line-height: 1.5;
}}
.bottom-bar {{
    margin-top: 70px;
    display: flex; gap: 30px; flex-wrap: wrap;
    justify-content: center;
}}
.tag {{
    background: transparent;
    border: 2px solid #333; border-radius: 50px;
    padding: 16px 40px; font-size: 22px;
    font-weight: 700; color: #777;
    letter-spacing: 2px; text-transform: uppercase;
}}
</style></head><body>

<div class="heading">Perfect For</div>
<div class="heading-line"></div>

<div class="grid">
    <div class="card">
        <div class="card-icon">&#127961;</div>
        <div class="card-title">Studio Owners</div>
        <div class="card-desc">Professional templates that match your brand aesthetic. Impress clients from the first interaction.</div>
    </div>
    <div class="card">
        <div class="card-icon">&#127912;</div>
        <div class="card-title">Independent Artists</div>
        <div class="card-desc">Look established from day one. No graphic designer needed — just edit in Canva and print.</div>
    </div>
    <div class="card">
        <div class="card-icon">&#128176;</div>
        <div class="card-title">Gift Givers</div>
        <div class="card-desc">The perfect last-minute gift for someone who loves body art. Instant download, print at home.</div>
    </div>
    <div class="card">
        <div class="card-icon">&#128640;</div>
        <div class="card-title">New Businesses</div>
        <div class="card-desc">Launch with a complete branding kit. Gift cards, appointment cards, price lists — all matching.</div>
    </div>
    <div class="card">
        <div class="card-icon">&#127891;</div>
        <div class="card-title">Apprentices</div>
        <div class="card-desc">Setting up your first workspace? Get professional stationery without the professional price tag.</div>
    </div>
    <div class="card">
        <div class="card-icon">&#128197;</div>
        <div class="card-title">Holiday Promotions</div>
        <div class="card-desc">Drive seasonal sales with branded gift certificates. Perfect for Christmas, birthdays, and special occasions.</div>
    </div>
</div>

<div class="bottom-bar">
    <div class="tag">Instant Download</div>
    <div class="tag">Fully Editable</div>
    <div class="tag">Commercial Use</div>
    <div class="tag">Print Ready</div>
</div>

</body></html>'''


def _page5_faq():
    """Page 5: FAQ + support information."""
    return f'''<!DOCTYPE html>
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
    padding: 120px 160px;
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
    margin: 24px auto 60px;
}}
.faqs {{
    width: 100%; max-width: 1700px;
    display: flex; flex-direction: column;
    gap: 40px; margin-bottom: 70px;
}}
.faq {{
    background: #1A1A1A;
    border-radius: 12px;
    padding: 40px 50px;
    border-left: 4px solid {ACCENT_ORANGE};
}}
.faq-q {{
    font-family: 'Playfair Display', serif;
    font-size: 34px; font-weight: 700;
    color: #FFF; margin-bottom: 14px;
}}
.faq-a {{
    font-size: 26px; color: #999; line-height: 1.6;
}}
.support-box {{
    background: #1A1A1A;
    border-radius: 16px;
    padding: 50px 60px;
    text-align: center;
    border: 1px solid #2A2A2A;
    width: 100%; max-width: 1400px;
}}
.support-title {{
    font-family: 'Oswald', sans-serif;
    font-size: 44px; font-weight: 700;
    color: #FFF; letter-spacing: 4px;
    text-transform: uppercase; margin-bottom: 16px;
}}
.support-desc {{
    font-size: 26px; color: #999; line-height: 1.6;
}}
.support-desc span {{ color: {ACCENT_ORANGE}; font-weight: 600; }}
</style></head><body>

<div class="heading">FAQ</div>
<div class="heading-line"></div>

<div class="faqs">
    <div class="faq">
        <div class="faq-q">Do I need Canva Pro to edit this?</div>
        <div class="faq-a">No! This template works perfectly with a free Canva account. No paid subscription required.</div>
    </div>
    <div class="faq">
        <div class="faq-q">Can I change the colours and fonts?</div>
        <div class="faq-a">Absolutely. Every element is fully customisable — colours, fonts, text, images, and layout. Make it yours.</div>
    </div>
    <div class="faq">
        <div class="faq-q">Can I print this at home?</div>
        <div class="faq-a">Yes. Download as PDF and print on any standard printer. For best results, use cardstock paper at a local print shop.</div>
    </div>
    <div class="faq">
        <div class="faq-q">Is commercial use included?</div>
        <div class="faq-a">Yes. You can use these templates for your business — print and give to clients, use at events, include in gift bags.</div>
    </div>
    <div class="faq">
        <div class="faq-q">How do I receive my files?</div>
        <div class="faq-a">Instantly after purchase. You will receive a PDF with clickable Canva template links via Etsy email and your account downloads page.</div>
    </div>
</div>

<div class="support-box">
    <div class="support-title">Need Help?</div>
    <div class="support-desc">
        Message us on Etsy — we reply within <span>24 hours</span>.<br>
        We are happy to help with editing, printing, or any questions about your template.
    </div>
</div>

</body></html>'''


def main():
    from playwright.sync_api import sync_playwright

    os.makedirs(EXPORT_DIR, exist_ok=True)

    pages = {
        3: ("How to Edit in Canva", _page3_how_to_edit),
        4: ("Perfect For", _page4_perfect_for),
        5: ("FAQ", _page5_faq),
    }

    prefix = "Etsy Listing - Gift Certificate Gothic Tattoo"

    print(f"\nGenerating boilerplate pages...")
    print(f"  Output: {EXPORT_DIR}")
    print(f"  Size: {IMG_W}x{IMG_H}px\n")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)

        for page_num, (label, html_fn) in pages.items():
            html = html_fn()
            page = browser.new_page(
                viewport={"width": IMG_W, "height": IMG_H},
                device_scale_factor=1,
            )
            page.set_content(html, wait_until="networkidle",
                             timeout=PLAYWRIGHT_PAGE_TIMEOUT_MS)
            page.wait_for_timeout(2000)

            filename = f"{prefix}_page{page_num}.png"
            path = os.path.join(EXPORT_DIR, filename)
            page.screenshot(
                path=path,
                clip={"x": 0, "y": 0, "width": IMG_W, "height": IMG_H},
            )
            page.close()

            size_kb = os.path.getsize(path) // 1024
            print(f"  Page {page_num} ({label}): {filename} ({size_kb}KB)")

        browser.close()

    print(f"\nDone. All boilerplate pages created.")


if __name__ == "__main__":
    main()
