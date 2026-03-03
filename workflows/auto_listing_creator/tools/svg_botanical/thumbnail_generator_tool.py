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

# ── Brand palette (sourced from brand_reference.py + gold/black aesthetic) ──
BG_LIGHT   = BRAND_COLORS["hero_bg"]              # #F5F5F5
BG_NOTE    = BRAND_COLORS["note_bg"]               # #F8F6F3
CARD_WHITE = BRAND_COLORS["card_bg"]               # #FFFFFF
PURPLE     = BRAND_COLORS["brand_purple"]           # #6B3E9E
PURPLE_LT  = BRAND_COLORS["brand_purple_light"]     # #9B59B6
LAVENDER   = BRAND_COLORS["brand_lavender"]          # #A78BFA
TEXT_DARK  = BRAND_COLORS["text_dark"]               # #2C2C2C
TEXT_GRAY  = BRAND_COLORS["text_gray"]               # #999999
BADGE_DARK = BRAND_COLORS["badge_dark"]              # #2C2C2C

# Gold / black split aesthetic (from Etsy reference design)
GOLD_FOIL  = "#D4AF77"
BLACK_BG   = "#0F0F0F"
WARM_BEIGE = "#E8D5B7"
MOCKUP_BG  = "#F5F0E6"

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
    """Shared CSS reset, fonts, and utility classes for all pages.

    NOTE: Does NOT set body background or color — each page controls its own
    palette via inline styles so gold/black and warm-beige pages work correctly.
    """
    return f"""
    {FONTS_CSS}
    :root {{
        --gold:{GOLD_FOIL}; --black:{BLACK_BG}; --warm:{WARM_BEIGE};
        --mockup:{MOCKUP_BG}; --text:{TEXT_DARK}; --dim:{TEXT_GRAY};
    }}
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ width:{IMG_W}px; height:{IMG_H}px;
           font-family:'Montserrat',sans-serif; overflow:hidden; }}
    .serif {{ font-family:'Playfair Display',serif; }}
    .script {{ font-family:'Great Vibes',cursive; }}
    .gold {{ color:var(--gold); }}
    .white {{ color:#FFFFFF; }}
    .dim {{ color:var(--dim); }}
    .divider {{ width:200px; height:3px; background:var(--gold);
                margin:20px auto; opacity:0.6; border-radius:2px; }}
    """


# ── Page 1: Hero ─────────────────────────────────────────────────────────────

def _page1_hero(samples, design_count):
    """Gold/black split cards with SVG tattoo art on warm beige mockup.

    Layout: 6 gold/black split cards showing SVG designs, arranged in a
    styled flat-lay on a warm beige fabric background. Each card has the
    left ~38% gold foil texture, right black with the tattoo art in white.
    Bottom: warm beige banner with product title + "EDIT IN CANVA" badge.
    """
    count_str = f"{design_count}+" if design_count >= 100 else str(design_count)

    # 6 split cards arranged in a styled flat-lay
    placements = [
        (140,  60, 400, -4),
        (880,  30, 420,  3),
        (1620, 80, 400, -3),
        (220,  560, 390,  4),
        (840,  600, 410, -2),
        (1500, 540, 400,  5),
    ]

    svg_cards = ""
    for i, (x, y, sz, rot) in enumerate(placements):
        if i >= len(samples):
            break
        svg_sz = int(sz * 0.55)
        svg_cards += (
            f'<div class="split-card" style="left:{x}px;top:{y}px;'
            f'width:{sz}px;height:{sz}px;'
            f'transform:rotate({rot}deg)">'
            f'<div class="gold-side"></div>'
            f'<div class="torn-edge"></div>'
            f'<div class="black-side">'
            f'<div class="svg-art">'
            f'{_svg_inline(samples[i], svg_sz, svg_sz, invert=True)}'
            f'</div></div></div>\n'
        )

    return f"""<!DOCTYPE html><html><head><style>
    {_base_css()}
    body {{ background:{MOCKUP_BG};
           background-image:
             url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='t'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.4' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23t)' opacity='0.04'/%3E%3C/svg%3E"); }}

    /* ── split card (gold left / black right / torn edge) ── */
    .split-card {{
        position:absolute; border-radius:12px; overflow:hidden;
        box-shadow:0 12px 40px rgba(0,0,0,0.18),
                   0 4px 12px rgba(0,0,0,0.08);
        display:flex;
    }}
    .gold-side {{
        width:38%; height:100%;
        background:
            url("data:image/svg+xml,%3Csvg viewBox='0 0 300 300' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='f'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='5' stitchTiles='stitch'/%3E%3CfeColorMatrix type='saturate' values='0.3'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23f)' opacity='0.18'/%3E%3C/svg%3E"),
            linear-gradient(135deg, #E8D5A8 0%, {GOLD_FOIL} 30%,
                            #B8944A 55%, {GOLD_FOIL} 75%, #E8D5A8 100%);
        flex-shrink:0;
    }}
    .torn-edge {{
        width:8%; height:100%; flex-shrink:0;
        background:{BLACK_BG};
        clip-path: polygon(
            60% 0%, 55% 2%, 65% 4%, 50% 6%, 68% 8%,
            45% 10%, 58% 12%, 42% 14%, 62% 16%, 38% 18%,
            55% 20%, 35% 22%, 60% 24%, 30% 26%, 52% 28%,
            28% 30%, 48% 32%, 25% 34%, 45% 36%, 22% 38%,
            42% 40%, 20% 42%, 38% 44%, 18% 46%, 35% 48%,
            15% 50%, 32% 52%, 12% 54%, 28% 56%, 10% 58%,
            25% 60%, 8% 62%, 22% 64%, 5% 66%, 18% 68%,
            3% 70%, 15% 72%, 0% 74%, 12% 76%, 0% 78%,
            10% 80%, 0% 82%, 8% 84%, 0% 86%, 5% 88%,
            0% 90%, 3% 92%, 0% 94%, 0% 96%, 0% 100%,
            100% 100%, 100% 0%
        );
        margin-left:-4%;
    }}
    .black-side {{
        flex:1; height:100%; background:{BLACK_BG};
        display:flex; align-items:center; justify-content:center;
        margin-left:-4%;
    }}
    .svg-art {{
        display:flex; align-items:center; justify-content:center;
    }}

    /* ── top badge ── */
    .badge {{
        position:absolute; top:50px; right:60px;
        background:{BADGE_DARK}; color:#FFF;
        padding:14px 38px; font-weight:700;
        font-size:24px; letter-spacing:3px;
        text-transform:uppercase; border-radius:6px;
        z-index:10;
    }}

    /* ── bottom banner (warm beige) ── */
    .banner {{
        position:absolute; bottom:0; left:0; right:0;
        height:480px; background:{WARM_BEIGE};
        display:flex; flex-direction:column;
        align-items:center; justify-content:center;
        padding-bottom:20px; z-index:10;
    }}
    .num {{
        font-size:160px; font-weight:900; line-height:1;
        color:{TEXT_DARK};
    }}
    .title {{
        font-size:68px; font-weight:800; color:{TEXT_DARK};
        margin-top:5px; letter-spacing:2px;
    }}
    .sub {{
        font-size:56px; font-weight:400; font-style:italic;
        color:#5C4A32; margin-top:2px;
    }}
    .tagline-bar {{
        background:#FFFFFF; padding:16px 48px; border-radius:4px;
        margin-top:24px;
    }}
    .fmts {{
        font-size:24px; letter-spacing:6px; text-transform:uppercase;
        color:{TEXT_DARK}; font-weight:700;
    }}
    .canva-badge {{
        position:absolute; bottom:380px; right:80px;
        width:180px; height:180px; border-radius:50%;
        background:{BADGE_DARK}; color:#FFF;
        display:flex; flex-direction:column;
        align-items:center; justify-content:center;
        font-weight:800; z-index:11;
    }}
    .canva-top {{ font-size:22px; letter-spacing:2px; }}
    .canva-bot {{ font-size:34px; letter-spacing:3px; }}
    .logo {{
        font-size:22px; letter-spacing:5px;
        color:rgba(92,74,50,0.5); margin-top:16px;
    }}
    </style></head><body>
    <div class="badge">INSTANT DOWNLOAD</div>
    {svg_cards}
    <div class="canva-badge">
        <span class="canva-top">EDIT IN</span>
        <span class="canva-bot">CANVA</span>
    </div>
    <div class="banner">
        <div class="num serif">{count_str}</div>
        <div class="title">Fine-Line Botanical</div>
        <div class="sub serif">Tattoo Designs</div>
        <div class="tagline-bar">
            <div class="fmts">SVG &middot; PNG &middot; DXF &middot; PDF &middot; EPS</div>
        </div>
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
            <div class="ext gold">{ext}</div>
            <div class="label">{label}</div>
            <div class="desc dim">{desc}</div>
        </div>"""

    grid_items = ""
    for i, s in enumerate(samples[:12]):
        grid_items += f'<div class="cell">{_svg_inline(s, 160, 160, invert=True)}</div>'

    return f"""<!DOCTYPE html><html><head><style>
    {_base_css()}
    body {{ background:{BLACK_BG}; color:#FFFFFF; }}
    .gold {{ color:{GOLD_FOIL}; }}
    .head {{ text-align:center; padding:80px 0 40px; }}
    .head h1 {{ font-size:72px; font-weight:700; letter-spacing:3px;
                color:{GOLD_FOIL}; }}
    .divider {{ background:{GOLD_FOIL}; }}
    .formats {{ display:flex; justify-content:center; gap:30px;
                padding:20px 60px; flex-wrap:wrap; }}
    .fmt-card {{ background:#1A1A1A; border-radius:16px; padding:30px 28px;
                 width:380px; text-align:center;
                 border-top:4px solid {GOLD_FOIL};
                 box-shadow:0 4px 16px rgba(0,0,0,0.3); }}
    .ext {{ font-size:42px; font-weight:800; }}
    .label {{ font-size:22px; font-weight:600; margin-top:6px; color:#EEE; }}
    .desc {{ font-size:18px; margin-top:4px; color:#888; }}
    .stats {{ display:flex; justify-content:center; gap:80px;
              padding:50px 0; text-align:center; }}
    .stat-num {{ font-size:96px; font-weight:900; line-height:1;
                 color:{GOLD_FOIL}; }}
    .stat-label {{ font-size:24px; font-weight:400; margin-top:8px;
                   color:#888; }}
    .times {{ font-size:60px; padding-top:20px; color:{GOLD_FOIL}; }}
    .grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:20px;
             padding:0 100px; }}
    .cell {{ background:#1A1A1A; border-radius:12px; padding:20px;
             display:flex; align-items:center; justify-content:center;
             box-shadow:0 2px 8px rgba(0,0,0,0.3); }}
    </style></head><body>
    <div class="head"><h1 class="serif">What You Get</h1>
    <div class="divider"></div></div>
    <div class="formats">{fmt_cards}</div>
    <div class="stats">
        <div><div class="stat-num serif">{design_count}+</div>
             <div class="stat-label">Designs</div></div>
        <div class="times">&times;</div>
        <div><div class="stat-num serif">5</div>
             <div class="stat-label">Formats</div></div>
        <div class="times">=</div>
        <div><div class="stat-num serif">{total_files}+</div>
             <div class="stat-label">Total Files</div></div>
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
                <div class="note-desc">{desc}</div>
            </div>
        </div>"""

    return f"""<!DOCTYPE html><html><head><style>
    {_base_css()}
    body {{ background:{WARM_BEIGE}; display:flex; flex-direction:column;
           align-items:center; justify-content:center;
           padding:120px 160px; color:{TEXT_DARK}; }}
    h1 {{ font-size:120px; margin-bottom:10px; color:{TEXT_DARK}; }}
    .divider {{ background:{GOLD_FOIL}; }}
    .notes {{ margin-top:60px; width:100%; }}
    .note {{ display:flex; align-items:flex-start; gap:36px;
             margin-bottom:50px; }}
    .num {{ width:70px; height:70px; border-radius:50%;
            background:{BLACK_BG}; color:{GOLD_FOIL};
            font-size:32px; font-weight:800;
            display:flex; align-items:center; justify-content:center;
            flex-shrink:0; }}
    .note-title {{ font-size:36px; font-weight:700; color:{TEXT_DARK}; }}
    .note-desc {{ font-size:26px; margin-top:6px; color:#6B5C4A; }}
    .trust {{ margin-top:70px; border:2px solid {GOLD_FOIL};
              border-radius:16px; padding:40px 60px; text-align:center;
              width:100%; background:#FFFFFF; }}
    .trust-title {{ font-size:32px; font-weight:700; letter-spacing:3px;
                    color:{TEXT_DARK}; }}
    .trust-sub {{ font-size:24px; margin-top:8px; color:#6B5C4A; }}
    .logo {{ margin-top:80px; font-size:36px; letter-spacing:5px;
             color:rgba(92,74,50,0.4); }}
    </style></head><body>
    <h1 class="script">Please Note</h1>
    <div class="divider"></div>
    <div class="notes">{items}</div>
    <div class="trust">
        <div class="trust-title">&#9733; COMMERCIAL LICENSE INCLUDED &#9733;</div>
        <div class="trust-sub">Personal &amp; commercial use permitted</div>
    </div>
    <div class="logo serif">PURPLEOCAZ</div>
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
        svg = _svg_inline(samples[i], 280, 280, invert=True) if i < len(samples) else ""
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
    body {{ background:{BLACK_BG}; color:#FFFFFF; }}
    .head {{ text-align:center; padding:80px 0 50px; }}
    .head h1 {{ font-size:68px; font-weight:700; letter-spacing:3px;
                color:{GOLD_FOIL}; }}
    .divider {{ background:{GOLD_FOIL}; }}
    .grid {{ display:grid; grid-template-columns:1fr 1fr; gap:30px;
             padding:0 80px; }}
    .use-card {{ background:#1A1A1A; border-radius:20px;
                 height:560px; position:relative; overflow:hidden;
                 display:flex; align-items:center; justify-content:center;
                 box-shadow:0 4px 16px rgba(0,0,0,0.3); }}
    .use-svg {{ opacity:0.25; }}
    .use-overlay {{ position:absolute; bottom:0; left:0; right:0;
                    padding:40px 36px;
                    background:linear-gradient(transparent,
                    rgba(15,15,15,0.95) 50%); }}
    .use-title {{ font-size:40px; font-weight:700; color:{GOLD_FOIL}; }}
    .use-desc {{ font-size:22px; margin-top:8px; color:rgba(255,255,255,0.7); }}
    .also {{ text-align:center; padding:50px 80px 0; }}
    .also-label {{ font-size:28px; font-weight:600; margin-bottom:20px;
                   color:#888; }}
    .pills {{ display:flex; justify-content:center; gap:18px;
              flex-wrap:wrap; }}
    .pill {{ border:2px solid {GOLD_FOIL}; border-radius:40px;
             padding:14px 32px; font-size:22px; font-weight:600;
             color:{GOLD_FOIL}; }}
    </style></head><body>
    <div class="head"><h1 class="serif">Endless Possibilities</h1>
    <div class="divider"></div></div>
    <div class="grid">{cards}</div>
    <div class="also">
        <div class="also-label">Also perfect for</div>
        <div class="pills">{pill_html}</div>
    </div>
    </body></html>"""


# ── Page 5: Category Preview ─────────────────────────────────────────────────

def _page5_categories(cat_samples, category_counts):
    cards = ""
    for cat_name in sorted(category_counts.keys()):
        count = category_counts[cat_name]
        svg = _svg_inline(cat_samples.get(cat_name, ""), 180, 180, invert=True)
        display_name = cat_name.replace("-", " ")
        cards += f"""
        <div class="cat-card">
            <div class="cat-svg">{svg}</div>
            <div class="cat-info">
                <div class="cat-name">{display_name}</div>
                <div class="cat-count">{count} designs</div>
            </div>
        </div>"""

    return f"""<!DOCTYPE html><html><head><style>
    {_base_css()}
    body {{ background:{BLACK_BG}; color:#FFFFFF; }}
    .head {{ text-align:center; padding:80px 0 50px; }}
    .head h1 {{ font-size:68px; font-weight:700; letter-spacing:3px;
                color:{GOLD_FOIL}; }}
    .head p {{ font-size:28px; margin-top:12px; color:#888; }}
    .divider {{ background:{GOLD_FOIL}; }}
    .grid {{ display:grid; grid-template-columns:1fr 1fr; gap:28px;
             padding:0 80px; }}
    .cat-card {{ background:#1A1A1A; border-radius:16px; padding:28px;
                 display:flex; align-items:center; gap:28px;
                 border-left:4px solid {GOLD_FOIL};
                 box-shadow:0 4px 16px rgba(0,0,0,0.3); }}
    .cat-svg {{ background:rgba(212,175,119,0.06); border-radius:12px;
                padding:10px; flex-shrink:0;
                width:200px; height:200px;
                display:flex; align-items:center; justify-content:center; }}
    .cat-name {{ font-size:32px; font-weight:700; color:#EEE; }}
    .cat-count {{ font-size:24px; margin-top:6px; font-weight:600;
                  color:{GOLD_FOIL}; }}
    .footer {{ position:absolute; bottom:0; left:0; right:0;
               background:{GOLD_FOIL}; padding:30px; text-align:center;
               font-size:22px; letter-spacing:5px; font-weight:600;
               color:{TEXT_DARK}; }}
    </style></head><body>
    <div class="head">
        <h1 class="serif">8 Design Categories</h1>
        <div class="divider"></div>
        <p>Something for every style</p>
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
                <div class="step-desc">{desc}</div>
            </div>
        </div>"""

    return f"""<!DOCTYPE html><html><head><style>
    {_base_css()}
    body {{ background:{WARM_BEIGE}; display:flex; flex-direction:column;
           align-items:center; justify-content:center;
           padding:100px 160px; color:{TEXT_DARK}; }}
    h1 {{ font-size:100px; margin-bottom:10px; color:{TEXT_DARK}; }}
    .divider {{ background:{GOLD_FOIL}; }}
    .stars {{ margin:30px 0 50px; }}
    .star {{ font-size:90px; color:{GOLD_FOIL}; margin:0 8px; }}
    .card {{ background:#FFFFFF; border-radius:24px;
             padding:60px 80px; width:100%;
             box-shadow:0 8px 32px rgba(0,0,0,0.08); }}
    .steps {{ display:flex; flex-direction:column; gap:40px; }}
    .step {{ display:flex; align-items:flex-start; gap:32px; }}
    .step-num {{ width:64px; height:64px; border-radius:50%;
                 background:{BLACK_BG}; color:{GOLD_FOIL};
                 font-size:28px; font-weight:800;
                 display:flex; align-items:center; justify-content:center;
                 flex-shrink:0; }}
    .step-title {{ font-size:34px; font-weight:700; color:{TEXT_DARK}; }}
    .step-desc {{ font-size:24px; margin-top:6px; color:#6B5C4A; }}
    .note {{ margin-top:50px; font-size:26px; font-style:italic;
             text-align:center; color:#6B5C4A; }}
    .logo {{ margin-top:60px; font-size:32px; letter-spacing:5px;
             color:rgba(92,74,50,0.4); }}
    </style></head><body>
    <h1 class="script">We'd Love Your Feedback!</h1>
    <div class="divider"></div>
    <div class="stars">{stars}</div>
    <div class="card">
        <div class="steps">{step_html}</div>
    </div>
    <div class="note">Your reviews help small creators grow &#10084;</div>
    <div class="logo serif">PURPLEOCAZ</div>
    </body></html>"""


# ── Page 7: Thank You ────────────────────────────────────────────────────────

def _page7_thank_you():
    return f"""<!DOCTYPE html><html><head><style>
    {_base_css()}
    body {{ background:{BLACK_BG}; display:flex; flex-direction:column;
           align-items:center; justify-content:center;
           padding:0; color:#FFFFFF; }}
    .top {{ flex:1; display:flex; flex-direction:column;
            align-items:center; justify-content:center;
            padding:100px 160px; text-align:center; }}
    .heart {{ font-size:80px; color:{GOLD_FOIL}; margin-bottom:20px; }}
    h1 {{ font-size:130px; margin-bottom:10px; color:#FFFFFF; }}
    .divider {{ background:{GOLD_FOIL}; }}
    .subtitle {{ font-size:48px; font-weight:300;
                 margin-top:10px; letter-spacing:1px; color:#888; }}
    .card {{ background:#1A1A1A; border-radius:24px;
             border:1px solid rgba(212,175,119,0.2);
             padding:50px 80px; margin-top:40px;
             max-width:1600px; text-align:center;
             box-shadow:0 8px 32px rgba(0,0,0,0.3); }}
    .card p {{ font-size:30px; line-height:1.7; color:#CCC; }}
    .banner {{ width:100%; background:{GOLD_FOIL};
               padding:60px 80px; text-align:center; }}
    .brand {{ font-size:56px; letter-spacing:8px; color:{TEXT_DARK};
              font-weight:700; }}
    .tagline {{ font-size:24px; color:rgba(44,44,44,0.6);
                letter-spacing:4px; margin-top:12px;
                text-transform:uppercase; }}
    </style></head><body>
    <div class="top">
        <div class="heart">&#10084;</div>
        <h1 class="script">Thank You!</h1>
        <div class="divider"></div>
        <div class="subtitle">for supporting our small business</div>
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
