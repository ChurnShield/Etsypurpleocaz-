# =============================================================================
# thumbnail_generator_tool.py
#
# BaseTool generating 7 Etsy listing images at 2250x3000px.
# Brand-aligned aesthetic: light backgrounds, purple accents, white cards.
#
# Page 1: Hero (flat-lay SVG designs on white cards, purple banner)
# Page 2: "What You Get" (format cards, stats bar, sample grid)
# Page 3: "Please Note" (trust signals, commercial license badge)
# Page 4: "Endless Possibilities" (use-case cards, editorial style)
# Page 5: Category Preview (8 categories, counts, samples)
# Page 6: "Leave a Review" (star rating, 3-step instructions)
# Page 7: "Thank You" (small business appreciation)
# =============================================================================

import os
import re
from typing import Any, Dict

from lib.orchestrator.base_tool import BaseTool
from config import PLAYWRIGHT_PAGE_TIMEOUT_MS
from workflows.auto_listing_creator.tools.brand_reference import BRAND_COLORS

IMG_W, IMG_H = 2250, 3000

# ── Brand palette (sourced from brand_reference.py) ──
BG_LIGHT   = BRAND_COLORS["hero_bg"]              # #F5F5F5
BG_NOTE    = BRAND_COLORS["note_bg"]               # #F8F6F3
CARD_WHITE = BRAND_COLORS["card_bg"]               # #FFFFFF
PURPLE     = BRAND_COLORS["brand_purple"]           # #6B3E9E
PURPLE_LT  = BRAND_COLORS["brand_purple_light"]     # #9B59B6
LAVENDER   = BRAND_COLORS["brand_lavender"]          # #A78BFA
TEXT_DARK  = BRAND_COLORS["text_dark"]               # #2C2C2C
TEXT_GRAY  = BRAND_COLORS["text_gray"]               # #999999
BADGE_DARK = BRAND_COLORS["badge_dark"]              # #2C2C2C

FONTS_CSS = (
    "@import url('https://fonts.googleapis.com/css2?"
    "family=Playfair+Display:ital,wght@0,400;0,600;0,700;0,900;1,400"
    "&family=Montserrat:wght@300;400;500;600;700;800"
    "&family=Great+Vibes&display=swap');"
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
    """Collect sample SVG content strings spread across categories."""
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
    """Collect one sample SVG per category."""
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
    """Prepare SVG for inline embedding at given size."""
    if content.startswith("<?xml"):
        content = content[content.index("?>") + 2:].strip()
    content = re.sub(r'width="[^"]*"', f'width="{w}"', content, count=1)
    content = re.sub(r'height="[^"]*"', f'height="{h}"', content, count=1)
    if invert:
        return (f'<span style="display:inline-block;'
                f'filter:invert(1) brightness(1.5)">{content}</span>')
    return content


def _base_css():
    """Shared CSS for all pages — brand-aligned light/purple palette."""
    return f"""
    {FONTS_CSS}
    :root {{ --bg:{BG_LIGHT}; --bg-note:{BG_NOTE}; --card:{CARD_WHITE};
             --purple:{PURPLE}; --purple-lt:{PURPLE_LT}; --lavender:{LAVENDER};
             --text:{TEXT_DARK}; --dim:{TEXT_GRAY}; }}
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ width:{IMG_W}px; height:{IMG_H}px; background:var(--bg);
           font-family:'Montserrat',sans-serif; overflow:hidden;
           color:var(--text); }}
    .serif {{ font-family:'Playfair Display',serif; }}
    .script {{ font-family:'Great Vibes',cursive; }}
    .purple {{ color:var(--purple); }}
    .purple-lt {{ color:var(--purple-lt); }}
    .dim {{ color:var(--dim); }}
    .white {{ color:#FFFFFF; }}
    .divider {{ width:200px; height:3px; background:var(--purple);
                margin:20px auto; opacity:0.6; border-radius:2px; }}
    """


# ── Page 1: Hero ─────────────────────────────────────────────────────────────

def _page1_hero(samples, design_count):
    count_str = f"{design_count}+" if design_count >= 100 else str(design_count)

    # 6 SVGs on white card shadows — flat-lay desk style
    placements = [
        (140,  80, 380, -4),
        (880,  50, 400,  3),
        (1620, 100, 380, -3),
        (220,  580, 370,  4),
        (840,  620, 390, -2),
        (1500, 560, 380,  5),
    ]

    svg_cards = ""
    for i, (x, y, sz, rot) in enumerate(placements):
        if i >= len(samples):
            break
        svg_cards += (
            f'<div class="card" style="left:{x}px;top:{y}px;'
            f'width:{sz}px;height:{sz}px;'
            f'transform:rotate({rot}deg)">'
            f'<div class="card-inner">'
            f'{_svg_inline(samples[i], sz - 60, sz - 60)}</div></div>\n'
        )

    return f"""<!DOCTYPE html><html><head><style>
    {_base_css()}
    body {{ background:var(--bg);
           background-image:radial-gradient(circle at 30% 40%,
           rgba(107,62,158,0.03) 0%, transparent 60%); }}
    .card {{ position:absolute; background:var(--card);
             border-radius:12px;
             box-shadow:0 8px 32px rgba(0,0,0,0.08),
                        0 2px 8px rgba(0,0,0,0.04);
             display:flex; align-items:center; justify-content:center; }}
    .card-inner {{ padding:30px; display:flex;
                   align-items:center; justify-content:center; }}
    .badge {{ position:absolute; top:50px; right:60px;
              background:var(--purple); color:#FFF;
              padding:14px 38px; font-weight:700;
              font-size:24px; letter-spacing:3px;
              text-transform:uppercase; border-radius:6px; }}
    .banner {{ position:absolute; bottom:0; left:0; right:0;
               height:420px; background:var(--purple);
               display:flex; flex-direction:column;
               align-items:center; justify-content:center;
               padding-bottom:20px; }}
    .num {{ font-size:180px; font-weight:900; line-height:1; color:#FFF;
            text-shadow:0 4px 20px rgba(0,0,0,0.15); }}
    .title {{ font-size:72px; font-weight:700; color:#FFF;
              margin-top:5px; letter-spacing:2px; }}
    .sub {{ font-size:62px; font-weight:400; font-style:italic;
            color:{PURPLE_LT}; margin-top:2px; }}
    .fmts {{ font-size:26px; letter-spacing:8px; text-transform:uppercase;
             color:rgba(255,255,255,0.7); margin-top:30px; }}
    .logo {{ font-size:24px; letter-spacing:5px; color:rgba(255,255,255,0.5);
             margin-top:16px; }}
    </style></head><body>
    <div class="badge">INSTANT DOWNLOAD</div>
    {svg_cards}
    <div class="banner">
        <div class="num serif">{count_str}</div>
        <div class="title serif">Fine-Line Botanical</div>
        <div class="sub serif">Tattoo Designs</div>
        <div class="fmts">SVG &middot; PNG &middot; DXF &middot; PDF &middot; EPS</div>
        <div class="logo serif">PURPLEOCAZ</div>
    </div>
    </body></html>"""


# ── Page 2: What You Get ─────────────────────────────────────────────────────

def _page2_what_you_get(samples, design_count):
    total_files = design_count * 5

    formats = [
        ("SVG", "Scalable Vector", "Infinite scaling, edit in Illustrator"),
        ("PNG", "4096 &times; 4096px", "High-res transparent background"),
        ("DXF", "CAD Format", "Cricut, Silhouette, laser cutters"),
        ("PDF", "Print Ready", "Perfect for professional printing"),
        ("EPS", "Professional", "Industry-standard vector format"),
    ]

    fmt_cards = ""
    for ext, label, desc in formats:
        fmt_cards += f"""
        <div class="fmt-card">
            <div class="ext purple">{ext}</div>
            <div class="label">{label}</div>
            <div class="desc dim">{desc}</div>
        </div>"""

    grid_items = ""
    for i, s in enumerate(samples[:12]):
        grid_items += f'<div class="cell">{_svg_inline(s, 160, 160)}</div>'

    return f"""<!DOCTYPE html><html><head><style>
    {_base_css()}
    .head {{ text-align:center; padding:80px 0 40px; }}
    .head h1 {{ font-size:72px; font-weight:700; letter-spacing:3px; }}
    .formats {{ display:flex; justify-content:center; gap:30px;
                padding:20px 60px; flex-wrap:wrap; }}
    .fmt-card {{ background:var(--card); border-radius:16px; padding:30px 28px;
                 width:380px; text-align:center;
                 border-top:4px solid var(--purple);
                 box-shadow:0 4px 16px rgba(0,0,0,0.06); }}
    .ext {{ font-size:42px; font-weight:800; }}
    .label {{ font-size:22px; font-weight:600; margin-top:6px; }}
    .desc {{ font-size:18px; margin-top:4px; }}
    .stats {{ display:flex; justify-content:center; gap:80px;
              padding:50px 0; text-align:center; }}
    .stat-num {{ font-size:96px; font-weight:900; line-height:1; }}
    .stat-label {{ font-size:24px; font-weight:400; margin-top:8px; }}
    .times {{ font-size:60px; padding-top:20px; }}
    .grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:20px;
             padding:0 100px; }}
    .cell {{ background:var(--card); border-radius:12px; padding:20px;
             display:flex; align-items:center; justify-content:center;
             box-shadow:0 2px 8px rgba(0,0,0,0.05); }}
    </style></head><body>
    <div class="head"><h1 class="serif purple">What You Get</h1>
    <div class="divider"></div></div>
    <div class="formats">{fmt_cards}</div>
    <div class="stats">
        <div><div class="stat-num serif purple">{design_count}+</div>
             <div class="stat-label dim">Designs</div></div>
        <div class="times purple">&times;</div>
        <div><div class="stat-num serif purple">5</div>
             <div class="stat-label dim">Formats</div></div>
        <div class="times purple">=</div>
        <div><div class="stat-num serif purple">{total_files}+</div>
             <div class="stat-label dim">Total Files</div></div>
    </div>
    <div class="grid">{grid_items}</div>
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
        <div class="note">
            <div class="num">{num}</div>
            <div class="note-text">
                <div class="note-title">{title}</div>
                <div class="note-desc dim">{desc}</div>
            </div>
        </div>"""

    return f"""<!DOCTYPE html><html><head><style>
    {_base_css()}
    body {{ background:{BG_NOTE}; display:flex; flex-direction:column;
           align-items:center; justify-content:center;
           padding:120px 160px; }}
    h1 {{ font-size:120px; margin-bottom:10px; }}
    .notes {{ margin-top:60px; width:100%; }}
    .note {{ display:flex; align-items:flex-start; gap:36px;
             margin-bottom:50px; }}
    .num {{ width:70px; height:70px; border-radius:50%;
            background:var(--purple); color:#FFF;
            font-size:32px; font-weight:800;
            display:flex; align-items:center; justify-content:center;
            flex-shrink:0; }}
    .note-title {{ font-size:36px; font-weight:700; }}
    .note-desc {{ font-size:26px; margin-top:6px; }}
    .trust {{ margin-top:70px; border:2px solid var(--purple);
              border-radius:16px; padding:40px 60px; text-align:center;
              width:100%; background:var(--card); }}
    .trust-title {{ font-size:32px; font-weight:700; letter-spacing:3px; }}
    .trust-sub {{ font-size:24px; margin-top:8px; }}
    .logo {{ margin-top:80px; font-size:36px; letter-spacing:5px;
             opacity:0.4; }}
    </style></head><body>
    <h1 class="script">Please Note</h1>
    <div class="divider"></div>
    <div class="notes">{items}</div>
    <div class="trust">
        <div class="trust-title purple">&#9733; COMMERCIAL LICENSE INCLUDED &#9733;</div>
        <div class="trust-sub dim">Personal &amp; commercial use permitted</div>
    </div>
    <div class="logo serif purple">PURPLEOCAZ</div>
    </body></html>"""


# ── Page 4: Usage Ideas ──────────────────────────────────────────────────────

def _page4_usage(samples):
    uses = [
        ("Tattoo Stencils", "Professional fine-line tattoo references"),
        ("Cricut &amp; Cutting", "SVG &amp; DXF ready for cutting machines"),
        ("Wall Art &amp; Prints", "High-res PNG for gallery-quality prints"),
        ("Apparel &amp; Products", "Sublimation, embroidery, engraving"),
    ]

    cards = ""
    for i, (title, desc) in enumerate(uses):
        svg = _svg_inline(samples[i], 280, 280) if i < len(samples) else ""
        cards += f"""
        <div class="use-card">
            <div class="use-svg">{svg}</div>
            <div class="use-overlay">
                <div class="use-title">{title}</div>
                <div class="use-desc">{desc}</div>
            </div>
        </div>"""

    pills = ["Stickers", "Invitations", "Journals", "Engraving",
             "Embroidery", "Nail Art"]
    pill_html = "".join(
        f'<span class="pill">{p}</span>' for p in pills)

    return f"""<!DOCTYPE html><html><head><style>
    {_base_css()}
    .head {{ text-align:center; padding:80px 0 50px; }}
    .head h1 {{ font-size:68px; font-weight:700; letter-spacing:3px; }}
    .grid {{ display:grid; grid-template-columns:1fr 1fr; gap:30px;
             padding:0 80px; }}
    .use-card {{ background:var(--card); border-radius:20px;
                 height:560px; position:relative; overflow:hidden;
                 display:flex; align-items:center; justify-content:center;
                 box-shadow:0 4px 16px rgba(0,0,0,0.06); }}
    .use-svg {{ opacity:0.2; }}
    .use-overlay {{ position:absolute; bottom:0; left:0; right:0;
                    padding:40px 36px;
                    background:linear-gradient(transparent,
                    rgba(107,62,158,0.92) 50%); }}
    .use-title {{ font-size:40px; font-weight:700; color:#FFF; }}
    .use-desc {{ font-size:22px; margin-top:8px; color:rgba(255,255,255,0.85); }}
    .also {{ text-align:center; padding:50px 80px 0; }}
    .also-label {{ font-size:28px; font-weight:600; margin-bottom:20px; }}
    .pills {{ display:flex; justify-content:center; gap:18px;
              flex-wrap:wrap; }}
    .pill {{ border:2px solid var(--purple); border-radius:40px;
             padding:14px 32px; font-size:22px; font-weight:600;
             color:var(--purple); }}
    </style></head><body>
    <div class="head"><h1 class="serif purple">Endless Possibilities</h1>
    <div class="divider"></div></div>
    <div class="grid">{cards}</div>
    <div class="also">
        <div class="also-label dim">Also perfect for</div>
        <div class="pills">{pill_html}</div>
    </div>
    </body></html>"""


# ── Page 5: Category Preview ─────────────────────────────────────────────────

def _page5_categories(cat_samples, category_counts):
    cards = ""
    for cat_name in sorted(category_counts.keys()):
        count = category_counts[cat_name]
        svg = _svg_inline(cat_samples.get(cat_name, ""), 180, 180)
        display_name = cat_name.replace("-", " ")
        cards += f"""
        <div class="cat-card">
            <div class="cat-svg">{svg}</div>
            <div class="cat-info">
                <div class="cat-name">{display_name}</div>
                <div class="cat-count purple">{count} designs</div>
            </div>
        </div>"""

    return f"""<!DOCTYPE html><html><head><style>
    {_base_css()}
    .head {{ text-align:center; padding:80px 0 50px; }}
    .head h1 {{ font-size:68px; font-weight:700; letter-spacing:3px; }}
    .head p {{ font-size:28px; margin-top:12px; }}
    .grid {{ display:grid; grid-template-columns:1fr 1fr; gap:28px;
             padding:0 80px; }}
    .cat-card {{ background:var(--card); border-radius:16px; padding:28px;
                 display:flex; align-items:center; gap:28px;
                 border-left:4px solid var(--purple);
                 box-shadow:0 4px 16px rgba(0,0,0,0.06); }}
    .cat-svg {{ background:rgba(107,62,158,0.04); border-radius:12px;
                padding:10px; flex-shrink:0;
                width:200px; height:200px;
                display:flex; align-items:center; justify-content:center; }}
    .cat-name {{ font-size:32px; font-weight:700; }}
    .cat-count {{ font-size:24px; margin-top:6px; font-weight:600; }}
    .footer {{ position:absolute; bottom:0; left:0; right:0;
               background:var(--purple); padding:30px; text-align:center;
               font-size:22px; letter-spacing:5px; font-weight:600;
               color:#FFF; }}
    </style></head><body>
    <div class="head">
        <h1 class="serif purple">8 Design Categories</h1>
        <div class="divider"></div>
        <p class="dim">Something for every style</p>
    </div>
    <div class="grid">{cards}</div>
    <div class="footer serif">PURPLEOCAZ &middot; FINE-LINE BOTANICAL COLLECTION</div>
    </body></html>"""


# ── Page 6: Leave a Review ───────────────────────────────────────────────────

def _page6_leave_review():
    stars = "".join(
        f'<span class="star">&#9733;</span>' for _ in range(5))

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
        <div class="step">
            <div class="step-num">{num}</div>
            <div class="step-body">
                <div class="step-title">{title}</div>
                <div class="step-desc dim">{desc}</div>
            </div>
        </div>"""

    return f"""<!DOCTYPE html><html><head><style>
    {_base_css()}
    body {{ display:flex; flex-direction:column; align-items:center;
           justify-content:center; padding:100px 160px; }}
    h1 {{ font-size:100px; margin-bottom:10px; }}
    .stars {{ margin:30px 0 50px; }}
    .star {{ font-size:90px; color:var(--purple); margin:0 8px; }}
    .card {{ background:var(--card); border-radius:24px;
             padding:60px 80px; width:100%;
             box-shadow:0 8px 32px rgba(0,0,0,0.06); }}
    .steps {{ display:flex; flex-direction:column; gap:40px; }}
    .step {{ display:flex; align-items:flex-start; gap:32px; }}
    .step-num {{ width:64px; height:64px; border-radius:50%;
                 background:var(--purple); color:#FFF;
                 font-size:28px; font-weight:800;
                 display:flex; align-items:center; justify-content:center;
                 flex-shrink:0; }}
    .step-title {{ font-size:34px; font-weight:700; }}
    .step-desc {{ font-size:24px; margin-top:6px; }}
    .note {{ margin-top:50px; font-size:26px; font-style:italic;
             text-align:center; }}
    .logo {{ margin-top:60px; font-size:32px; letter-spacing:5px;
             opacity:0.4; }}
    </style></head><body>
    <h1 class="script">We'd Love Your Feedback!</h1>
    <div class="divider"></div>
    <div class="stars">{stars}</div>
    <div class="card">
        <div class="steps">{step_html}</div>
    </div>
    <div class="note dim">Your reviews help small creators grow &#10084;</div>
    <div class="logo serif purple">PURPLEOCAZ</div>
    </body></html>"""


# ── Page 7: Thank You ────────────────────────────────────────────────────────

def _page7_thank_you():
    return f"""<!DOCTYPE html><html><head><style>
    {_base_css()}
    body {{ display:flex; flex-direction:column; align-items:center;
           justify-content:center; padding:0; }}
    .top {{ flex:1; display:flex; flex-direction:column;
            align-items:center; justify-content:center;
            padding:100px 160px; text-align:center; }}
    .heart {{ font-size:80px; color:var(--purple); margin-bottom:20px; }}
    h1 {{ font-size:130px; margin-bottom:10px; }}
    .subtitle {{ font-size:48px; font-weight:300;
                 margin-top:10px; letter-spacing:1px; }}
    .card {{ background:var(--card); border-radius:24px;
             padding:50px 80px; margin-top:40px;
             max-width:1600px; text-align:center;
             box-shadow:0 8px 32px rgba(0,0,0,0.06); }}
    .card p {{ font-size:30px; line-height:1.7; }}
    .banner {{ width:100%; background:var(--purple);
               padding:60px 80px; text-align:center; }}
    .brand {{ font-size:56px; letter-spacing:8px; color:#FFF;
              font-weight:700; }}
    .tagline {{ font-size:24px; color:rgba(255,255,255,0.6);
                letter-spacing:4px; margin-top:12px;
                text-transform:uppercase; }}
    </style></head><body>
    <div class="top">
        <div class="heart">&#10084;</div>
        <h1 class="script">Thank You!</h1>
        <div class="divider"></div>
        <div class="subtitle dim">for supporting our small business</div>
        <div class="card">
            <p>Every purchase helps us continue creating beautiful<br>
            designs for makers, artists, and creators like you.</p>
        </div>
    </div>
    <div class="banner">
        <div class="brand serif">PURPLEOCAZ</div>
        <div class="tagline">Handcrafted Digital Designs</div>
    </div>
    </body></html>"""
