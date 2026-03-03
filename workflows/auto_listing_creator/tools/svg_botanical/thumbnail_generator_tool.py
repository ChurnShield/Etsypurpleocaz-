# =============================================================================
# thumbnail_generator_tool.py
#
# BaseTool generating 7 Etsy listing images at 2250x3000px.
#
# Design principles:
#   - Light backgrounds (#F5F5F5) for ALL pages — high contrast, readable
#   - SVG designs displayed prominently — this is the product
#   - Minimal dead space — content fills the frame
#   - Purple accents for brand consistency
#   - NO appointment card / gift certificate elements
#
# Page 1: Hero (large SVG grid, count badge, purple banner)
# Page 2: "What You Get" (5 format cards, file count math, SVG grid)
# Page 3: "Please Note" (4 bullet items, commercial license badge)
# Page 4: "Endless Possibilities" (use-case showcase with SVGs)
# Page 5: Category Preview (category cards with SVG samples)
# Page 6: "Leave a Review" (5-star rating, 3-step instructions)
# Page 7: "Thank You" (appreciation + brand footer)
# =============================================================================

import os
import re
from typing import Any, Dict

from lib.orchestrator.base_tool import BaseTool
from config import PLAYWRIGHT_PAGE_TIMEOUT_MS

IMG_W, IMG_H = 2250, 3000

# ── Brand palette ──
PURPLE     = "#6B3E9E"
PURPLE_LT  = "#9B59B6"
LAVENDER   = "#A78BFA"
BG_LIGHT   = "#F5F5F5"
CARD_WHITE = "#FFFFFF"
TEXT_DARK  = "#2C2C2C"
TEXT_MED   = "#555555"
TEXT_DIM   = "#888888"

FONTS_CSS = (
    "@import url('https://fonts.googleapis.com/css2?"
    "family=Playfair+Display:ital,wght@0,400;0,600;0,700;0,900;1,400"
    "&family=Montserrat:wght@300;400;500;600;700;800"
    "&display=swap');"
)


class ThumbnailGeneratorTool(BaseTool):
    """Generate 7 Etsy listing thumbnail images with brand-aligned aesthetic."""

    def get_name(self) -> str:
        return "ThumbnailGeneratorTool"

    def execute(self, **kwargs) -> Dict[str, Any]:
        svg_dir = kwargs.get("svg_dir", "")
        output_dir = kwargs.get("output_dir", "")
        design_count = kwargs.get("design_count", 0)
        category_counts = kwargs.get("category_counts", {})

        if not svg_dir or not output_dir:
            return {
                "success": False, "data": None,
                "error": "svg_dir and output_dir are required",
                "tool_name": self.get_name(), "metadata": {},
            }

        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return {
                "success": False, "data": None,
                "error": "playwright not installed",
                "tool_name": self.get_name(), "metadata": {},
            }

        thumb_dir = os.path.join(output_dir, "thumbnails")
        os.makedirs(thumb_dir, exist_ok=True)

        samples = _collect_sample_svgs(svg_dir, max_per_cat=4)
        cat_samples = _collect_category_samples(svg_dir)

        pages = [
            ("01-Hero", _page1_hero(samples, design_count)),
            ("02-What-You-Get", _page2_what_you_get(samples, design_count)),
            ("03-Please-Note", _page3_please_note()),
            ("04-Usage-Ideas", _page4_usage(samples)),
            ("05-Categories", _page5_categories(cat_samples, category_counts)),
            ("06-Leave-Review", _page6_leave_review()),
            ("07-Thank-You", _page7_thank_you()),
        ]

        generated = []
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                for name, html in pages:
                    page = browser.new_page(
                        viewport={"width": IMG_W, "height": IMG_H},
                        device_scale_factor=1,
                    )
                    page.set_content(html, wait_until="networkidle",
                                     timeout=PLAYWRIGHT_PAGE_TIMEOUT_MS)
                    page.wait_for_timeout(2000)
                    out_path = os.path.join(thumb_dir, f"{name}.png")
                    page.screenshot(
                        path=out_path,
                        clip={"x": 0, "y": 0, "width": IMG_W, "height": IMG_H},
                    )
                    page.close()
                    generated.append(out_path)
                    print(f"       {name}.png")
                browser.close()
        except Exception as e:
            return {
                "success": False, "data": None, "error": str(e),
                "tool_name": self.get_name(), "metadata": {},
            }

        return {
            "success": True,
            "data": {"count": len(generated), "paths": generated,
                     "thumb_dir": thumb_dir},
            "error": None, "tool_name": self.get_name(),
            "metadata": {"pages": len(generated)},
        }


# ── Helpers ──────────────────────────────────────────────────────────────────

def _collect_sample_svgs(svg_dir, max_per_cat=4):
    samples = []
    for cat_name in sorted(os.listdir(svg_dir)):
        cat_path = os.path.join(svg_dir, cat_name)
        if not os.path.isdir(cat_path):
            continue
        files = sorted(f for f in os.listdir(cat_path) if f.endswith(".svg"))
        for f in files[:max_per_cat]:
            try:
                with open(os.path.join(cat_path, f), "r", encoding="utf-8") as fh:
                    samples.append(fh.read())
            except Exception:
                continue
    return samples


def _collect_category_samples(svg_dir):
    cat_map = {}
    for cat_name in sorted(os.listdir(svg_dir)):
        cat_path = os.path.join(svg_dir, cat_name)
        if not os.path.isdir(cat_path):
            continue
        files = sorted(f for f in os.listdir(cat_path) if f.endswith(".svg"))
        if files:
            try:
                with open(os.path.join(cat_path, files[0]), "r",
                          encoding="utf-8") as fh:
                    cat_map[cat_name] = fh.read()
            except Exception:
                continue
    return cat_map


def _svg_inline(content, w=200, h=200, invert=False):
    if content.startswith("<?xml"):
        content = content[content.index("?>") + 2:].strip()
    content = re.sub(r'width="[^"]*"', f'width="{w}"', content, count=1)
    content = re.sub(r'height="[^"]*"', f'height="{h}"', content, count=1)
    if invert:
        return (f'<span style="display:inline-block;'
                f'filter:invert(1) brightness(1.5)">{content}</span>')
    return content


def _base_css():
    return f"""
    {FONTS_CSS}
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ width:{IMG_W}px; height:{IMG_H}px; background:{BG_LIGHT};
           font-family:'Montserrat',sans-serif; overflow:hidden;
           color:{TEXT_DARK}; }}
    .serif {{ font-family:'Playfair Display',serif; }}
    .purple {{ color:{PURPLE}; }}
    .white {{ color:#FFFFFF; }}
    .divider {{ width:120px; height:4px; background:{PURPLE};
                margin:16px auto; border-radius:2px; }}
    """


# ── Page 1: Hero ─────────────────────────────────────────────────────────────

def _page1_hero(samples, design_count):
    count_str = f"{design_count}+" if design_count >= 100 else str(design_count)

    # 3x3 grid of SVGs on white cards — fills upper 2/3
    svg_cards = ""
    positions = [
        (60,  40,  640, 640, -2), (780, 20,  660, 660,  1), (1520, 50,  640, 640, -1),
        (100, 720, 620, 620,  3), (800, 700, 640, 640, -2), (1480, 730, 660, 660,  2),
        (60,  1380,640, 640, -1), (780, 1400,660, 660,  1), (1500, 1370,640, 640, -3),
    ]

    for i, (x, y, w, h, rot) in enumerate(positions):
        if i >= len(samples):
            break
        sz = min(w, h) - 80
        svg_cards += (
            f'<div style="position:absolute;left:{x}px;top:{y}px;'
            f'width:{w}px;height:{h}px;background:#FFF;border-radius:16px;'
            f'box-shadow:0 6px 24px rgba(0,0,0,0.08);'
            f'display:flex;align-items:center;justify-content:center;'
            f'transform:rotate({rot}deg)">'
            f'{_svg_inline(samples[i], sz, sz)}</div>\n'
        )

    return f"""<!DOCTYPE html><html><head><style>
    {_base_css()}
    .badge {{ position:absolute; top:40px; right:50px; z-index:10;
              background:{PURPLE}; color:#FFF;
              padding:16px 36px; font-weight:700;
              font-size:26px; letter-spacing:3px;
              text-transform:uppercase; border-radius:8px;
              box-shadow:0 4px 16px rgba(107,62,158,0.3); }}
    .banner {{ position:absolute; bottom:0; left:0; right:0;
               height:380px; background:{PURPLE};
               display:flex; flex-direction:column;
               align-items:center; justify-content:center; }}
    .num {{ font-size:160px; font-weight:900; line-height:1; color:#FFF; }}
    .title {{ font-size:68px; font-weight:700; color:#FFF;
              margin-top:4px; letter-spacing:2px; }}
    .sub {{ font-size:56px; font-weight:400; font-style:italic;
            color:rgba(255,255,255,0.75); margin-top:2px; }}
    .fmts {{ font-size:24px; letter-spacing:6px; text-transform:uppercase;
             color:rgba(255,255,255,0.6); margin-top:20px; }}
    </style></head><body>
    <div class="badge">INSTANT DOWNLOAD</div>
    {svg_cards}
    <div class="banner">
        <div class="num serif">{count_str}</div>
        <div class="title serif">Fine-Line Botanical</div>
        <div class="sub serif">Tattoo Designs</div>
        <div class="fmts">SVG &middot; PNG &middot; DXF &middot; PDF &middot; EPS</div>
    </div>
    </body></html>"""


# ── Page 2: What You Get ─────────────────────────────────────────────────────

def _page2_what_you_get(samples, design_count):
    total_files = design_count * 5

    formats = [
        ("SVG", "Scalable Vector", "Edit in Illustrator / Inkscape"),
        ("PNG", "4096 &times; 4096", "Transparent background"),
        ("DXF", "CAD Format", "Cricut &amp; Silhouette ready"),
        ("PDF", "Print Ready", "Professional printing"),
        ("EPS", "Professional", "Industry-standard vector"),
    ]

    fmt_cards = ""
    for ext, label, desc in formats:
        fmt_cards += f"""
        <div style="background:#FFF;border-radius:14px;padding:28px 20px;
                     text-align:center;border-top:5px solid {PURPLE};
                     box-shadow:0 3px 12px rgba(0,0,0,0.06);flex:1;min-width:0">
            <div style="font-size:44px;font-weight:800;color:{PURPLE}">{ext}</div>
            <div style="font-size:20px;font-weight:600;margin-top:6px;color:{TEXT_DARK}">{label}</div>
            <div style="font-size:17px;margin-top:4px;color:{TEXT_DIM}">{desc}</div>
        </div>"""

    grid_items = ""
    for i, s in enumerate(samples[:16]):
        grid_items += (
            f'<div style="background:#FFF;border-radius:10px;padding:16px;'
            f'display:flex;align-items:center;justify-content:center;'
            f'box-shadow:0 2px 8px rgba(0,0,0,0.05)">'
            f'{_svg_inline(s, 140, 140)}</div>'
        )

    return f"""<!DOCTYPE html><html><head><style>
    {_base_css()}
    </style></head><body style="padding:50px 60px">
    <div style="text-align:center;margin-bottom:36px">
        <h1 class="serif purple" style="font-size:72px;font-weight:700;letter-spacing:2px">
            What You Get</h1>
        <div class="divider"></div>
    </div>
    <div style="display:flex;gap:20px;margin-bottom:40px">{fmt_cards}</div>
    <div style="display:flex;justify-content:center;align-items:center;gap:50px;
                margin:36px 0;text-align:center">
        <div>
            <div class="serif purple" style="font-size:90px;font-weight:900;line-height:1">{design_count}+</div>
            <div style="font-size:22px;color:{TEXT_DIM};margin-top:4px">Designs</div>
        </div>
        <div class="purple" style="font-size:56px;padding-top:10px">&times;</div>
        <div>
            <div class="serif purple" style="font-size:90px;font-weight:900;line-height:1">5</div>
            <div style="font-size:22px;color:{TEXT_DIM};margin-top:4px">Formats</div>
        </div>
        <div class="purple" style="font-size:56px;padding-top:10px">=</div>
        <div>
            <div class="serif purple" style="font-size:90px;font-weight:900;line-height:1">{total_files}+</div>
            <div style="font-size:22px;color:{TEXT_DIM};margin-top:4px">Total Files</div>
        </div>
    </div>
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px">
        {grid_items}
    </div>
    </body></html>"""


# ── Page 3: Please Note ──────────────────────────────────────────────────────

def _page3_please_note():
    notes = [
        ("1", "Digital Download Product",
         "Instant access after purchase &mdash; download from your Etsy receipt"),
        ("2", "No Physical Product Shipped",
         "All designs are delivered as digital files only"),
        ("3", "5 File Formats Included",
         "SVG, PNG, DXF, PDF &amp; EPS &mdash; works with Cricut &amp; Silhouette"),
        ("4", "Black Line Art on Transparent",
         "Perfect for tattoo stencils, cutting machines &amp; printing"),
    ]

    items = ""
    for num, title, desc in notes:
        items += f"""
        <div style="display:flex;align-items:center;gap:30px;
                     background:#FFF;border-radius:16px;padding:36px 40px;
                     box-shadow:0 3px 12px rgba(0,0,0,0.05);
                     border-left:5px solid {PURPLE}">
            <div style="width:64px;height:64px;border-radius:50%;
                         background:{PURPLE};color:#FFF;
                         font-size:30px;font-weight:800;
                         display:flex;align-items:center;justify-content:center;
                         flex-shrink:0">{num}</div>
            <div>
                <div style="font-size:34px;font-weight:700;color:{TEXT_DARK}">{title}</div>
                <div style="font-size:24px;margin-top:6px;color:{TEXT_MED}">{desc}</div>
            </div>
        </div>"""

    return f"""<!DOCTYPE html><html><head><style>
    {_base_css()}
    </style></head><body style="display:flex;flex-direction:column;
           align-items:center;justify-content:center;padding:80px 100px">
    <h1 class="serif" style="font-size:90px;color:{TEXT_DARK};margin-bottom:8px">
        Please Note</h1>
    <div class="divider"></div>
    <div style="display:flex;flex-direction:column;gap:28px;width:100%;
                margin-top:50px">{items}</div>
    <div style="margin-top:50px;border:3px solid {PURPLE};
                border-radius:16px;padding:36px 60px;text-align:center;
                width:100%;background:#FFF;
                box-shadow:0 3px 12px rgba(0,0,0,0.05)">
        <div style="font-size:34px;font-weight:700;color:{PURPLE};
                     letter-spacing:2px">&#9733; COMMERCIAL LICENSE INCLUDED &#9733;</div>
        <div style="font-size:24px;margin-top:8px;color:{TEXT_MED}">
            Personal &amp; commercial use permitted</div>
    </div>
    <div class="serif" style="margin-top:50px;font-size:32px;letter-spacing:5px;
                color:{PURPLE};opacity:0.5">PURPLEOCAZ</div>
    </body></html>"""


# ── Page 4: Usage Ideas ──────────────────────────────────────────────────────

def _page4_usage(samples):
    uses = [
        ("Tattoo Stencils", "Fine-line tattoo references &amp; flash art"),
        ("Cricut &amp; Cutting", "SVG &amp; DXF ready for cutting machines"),
        ("Wall Art &amp; Prints", "High-res PNG for gallery-quality prints"),
        ("Apparel &amp; Products", "Sublimation, embroidery &amp; engraving"),
    ]

    cards = ""
    for i, (title, desc) in enumerate(uses):
        svg = _svg_inline(samples[i], 260, 260) if i < len(samples) else ""
        cards += f"""
        <div style="background:#FFF;border-radius:18px;overflow:hidden;
                     box-shadow:0 4px 16px rgba(0,0,0,0.06);
                     display:flex;flex-direction:column">
            <div style="height:440px;display:flex;align-items:center;
                         justify-content:center;background:{BG_LIGHT};
                         border-bottom:3px solid {PURPLE}">{svg}</div>
            <div style="padding:30px 28px">
                <div style="font-size:34px;font-weight:700;color:{PURPLE}">{title}</div>
                <div style="font-size:22px;margin-top:8px;color:{TEXT_MED}">{desc}</div>
            </div>
        </div>"""

    pills = ["Stickers", "Invitations", "Journals", "Engraving",
             "Embroidery", "Nail Art", "Logos", "Decals"]
    pill_html = "".join(
        f'<span style="border:2px solid {PURPLE};border-radius:40px;'
        f'padding:14px 30px;font-size:22px;font-weight:600;'
        f'color:{PURPLE}">{p}</span>' for p in pills)

    return f"""<!DOCTYPE html><html><head><style>
    {_base_css()}
    </style></head><body style="padding:50px 60px">
    <div style="text-align:center;margin-bottom:36px">
        <h1 class="serif purple" style="font-size:68px;font-weight:700;letter-spacing:2px">
            Endless Possibilities</h1>
        <div class="divider"></div>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:28px">
        {cards}
    </div>
    <div style="text-align:center;margin-top:40px">
        <div style="font-size:26px;font-weight:600;color:{TEXT_DIM};margin-bottom:18px">
            Also perfect for</div>
        <div style="display:flex;justify-content:center;gap:16px;flex-wrap:wrap">
            {pill_html}
        </div>
    </div>
    </body></html>"""


# ── Page 5: Category Preview ─────────────────────────────────────────────────

def _page5_categories(cat_samples, category_counts):
    cards = ""
    for cat_name in sorted(category_counts.keys()):
        count = category_counts[cat_name]
        svg = _svg_inline(cat_samples.get(cat_name, ""), 160, 160)
        display_name = cat_name.replace("-", " ").title()
        cards += f"""
        <div style="background:#FFF;border-radius:14px;padding:24px;
                     display:flex;align-items:center;gap:24px;
                     border-left:5px solid {PURPLE};
                     box-shadow:0 3px 12px rgba(0,0,0,0.05)">
            <div style="background:{BG_LIGHT};border-radius:12px;
                         padding:12px;flex-shrink:0;
                         width:180px;height:180px;
                         display:flex;align-items:center;justify-content:center">
                {svg}
            </div>
            <div>
                <div style="font-size:30px;font-weight:700;color:{TEXT_DARK}">{display_name}</div>
                <div style="font-size:24px;margin-top:6px;font-weight:600;color:{PURPLE}">
                    {count} designs</div>
            </div>
        </div>"""

    total_cats = len(category_counts)

    return f"""<!DOCTYPE html><html><head><style>
    {_base_css()}
    </style></head><body style="padding:50px 60px;display:flex;flex-direction:column">
    <div style="text-align:center;margin-bottom:36px">
        <h1 class="serif purple" style="font-size:68px;font-weight:700;letter-spacing:2px">
            {total_cats} Design Categories</h1>
        <div class="divider"></div>
        <p style="font-size:26px;margin-top:10px;color:{TEXT_DIM}">Something for every style</p>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;flex:1">
        {cards}
    </div>
    <div style="background:{PURPLE};border-radius:14px;margin-top:36px;
                padding:28px;text-align:center">
        <span class="serif" style="font-size:24px;letter-spacing:5px;
                     font-weight:600;color:#FFF">
            PURPLEOCAZ &middot; FINE-LINE BOTANICAL COLLECTION</span>
    </div>
    </body></html>"""


# ── Page 6: Leave a Review ───────────────────────────────────────────────────

def _page6_leave_review():
    stars = "".join(
        f'<span style="font-size:80px;color:{PURPLE};margin:0 6px">&#9733;</span>'
        for _ in range(5))

    steps = [
        ("1", "Go to Your Etsy Purchases",
         "Open Etsy &rarr; Your Account &rarr; Purchases &amp; Reviews"),
        ("2", "Find This Order",
         "Click &ldquo;Write a Review&rdquo; next to your purchase"),
        ("3", "Share Your Experience",
         "Your honest feedback helps other buyers &amp; supports our shop"),
    ]

    step_html = ""
    for num, title, desc in steps:
        step_html += f"""
        <div style="display:flex;align-items:center;gap:28px">
            <div style="width:60px;height:60px;border-radius:50%;
                         background:{PURPLE};color:#FFF;
                         font-size:28px;font-weight:800;
                         display:flex;align-items:center;justify-content:center;
                         flex-shrink:0">{num}</div>
            <div>
                <div style="font-size:32px;font-weight:700;color:{TEXT_DARK}">{title}</div>
                <div style="font-size:24px;margin-top:4px;color:{TEXT_MED}">{desc}</div>
            </div>
        </div>"""

    return f"""<!DOCTYPE html><html><head><style>
    {_base_css()}
    </style></head><body style="display:flex;flex-direction:column;
           align-items:center;justify-content:center;padding:80px 100px">
    <h1 class="serif" style="font-size:80px;color:{TEXT_DARK}">
        We'd Love Your Feedback!</h1>
    <div class="divider"></div>
    <div style="margin:30px 0 40px">{stars}</div>
    <div style="background:#FFF;border-radius:20px;
                 padding:50px 60px;width:100%;
                 box-shadow:0 4px 20px rgba(0,0,0,0.06)">
        <div style="display:flex;flex-direction:column;gap:36px">
            {step_html}
        </div>
    </div>
    <div style="margin-top:40px;font-size:26px;font-style:italic;
                 color:{TEXT_MED};text-align:center">
        Your reviews help small creators grow &#10084;</div>
    <div class="serif" style="margin-top:40px;font-size:32px;letter-spacing:5px;
                color:{PURPLE};opacity:0.5">PURPLEOCAZ</div>
    </body></html>"""


# ── Page 7: Thank You ────────────────────────────────────────────────────────

def _page7_thank_you():
    return f"""<!DOCTYPE html><html><head><style>
    {_base_css()}
    </style></head><body style="display:flex;flex-direction:column;
           align-items:center;justify-content:center;padding:0">
    <div style="flex:1;display:flex;flex-direction:column;
                align-items:center;justify-content:center;
                padding:80px 120px;text-align:center">
        <div style="font-size:80px;color:{PURPLE};margin-bottom:16px">&#10084;</div>
        <h1 class="serif" style="font-size:110px;color:{TEXT_DARK};margin-bottom:8px">
            Thank You!</h1>
        <div class="divider"></div>
        <div style="font-size:44px;font-weight:300;margin-top:16px;
                     color:{TEXT_MED};letter-spacing:1px">
            for supporting our small business</div>
        <div style="background:#FFF;border-radius:20px;padding:44px 60px;
                     margin-top:40px;max-width:1400px;
                     box-shadow:0 4px 20px rgba(0,0,0,0.06)">
            <p style="font-size:30px;line-height:1.7;color:{TEXT_DARK}">
                Every purchase helps us continue creating beautiful<br>
                designs for makers, artists, and creators like you.</p>
        </div>
    </div>
    <div style="width:100%;background:{PURPLE};
                padding:50px 80px;text-align:center">
        <div class="serif" style="font-size:52px;letter-spacing:8px;
                     color:#FFF;font-weight:700">PURPLEOCAZ</div>
        <div style="font-size:22px;color:rgba(255,255,255,0.65);
                     letter-spacing:4px;margin-top:10px;
                     text-transform:uppercase">Handcrafted Digital Designs</div>
    </div>
    </body></html>"""
