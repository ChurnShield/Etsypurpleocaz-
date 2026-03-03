#!/usr/bin/env python3
"""
preview_thumbnails.py — Generate preview HTML files for all 7 Etsy thumbnail pages.

Usage:
    python scripts/preview_thumbnails.py

Output:
    output/thumbnail_preview/  (7 HTML files you can open in any browser)

No Playwright or API keys needed. Uses sample SVG botanicals so you can see
exactly what customers will see.
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflows.auto_listing_creator.tools.brand_reference import BRAND_COLORS

# ── Brand palette ──
BG_LIGHT   = BRAND_COLORS["hero_bg"]
BG_NOTE    = BRAND_COLORS["note_bg"]
CARD_WHITE = BRAND_COLORS["card_bg"]
PURPLE     = BRAND_COLORS["brand_purple"]
PURPLE_LT  = BRAND_COLORS["brand_purple_light"]
LAVENDER   = BRAND_COLORS["brand_lavender"]
TEXT_DARK  = BRAND_COLORS["text_dark"]
TEXT_GRAY  = BRAND_COLORS["text_gray"]

IMG_W, IMG_H = 2250, 3000

FONTS_CSS = (
    "@import url('https://fonts.googleapis.com/css2?"
    "family=Playfair+Display:ital,wght@0,400;0,600;0,700;0,900;1,400"
    "&family=Montserrat:wght@300;400;500;600;700;800"
    "&family=Great+Vibes&display=swap');"
)

# ── Sample SVGs (botanical line art) for preview ──
SAMPLE_SVGS = [
    # Rose
    '''<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
    <g fill="none" stroke="#2C2C2C" stroke-width="1.5" stroke-linecap="round">
        <path d="M100 180 C100 180 100 120 100 100"/>
        <path d="M100 100 C80 90 60 95 55 80 C50 65 65 50 80 55 C70 45 75 25 90 30 C95 20 105 20 110 30 C125 25 130 45 120 55 C135 50 150 65 145 80 C140 95 120 90 100 100"/>
        <path d="M85 130 C70 125 55 135 60 150"/>
        <path d="M115 140 C130 135 145 145 140 160"/>
    </g>
    </svg>''',
    # Lavender
    '''<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
    <g fill="none" stroke="#2C2C2C" stroke-width="1.5" stroke-linecap="round">
        <path d="M100 190 C100 190 95 120 100 80"/>
        <path d="M100 80 C95 75 90 65 95 55 C97 50 103 50 105 55 C110 65 105 75 100 80"/>
        <path d="M95 70 C88 68 82 58 87 50 C90 45 96 47 95 52"/>
        <path d="M105 70 C112 68 118 58 113 50 C110 45 104 47 105 52"/>
        <path d="M93 58 C86 55 82 45 87 38"/>
        <path d="M107 58 C114 55 118 45 113 38"/>
        <path d="M95 48 C90 44 88 35 93 30"/>
        <path d="M105 48 C110 44 112 35 107 30"/>
        <path d="M80 150 C85 140 92 135 100 130"/>
        <path d="M120 155 C115 145 108 138 100 135"/>
    </g>
    </svg>''',
    # Fern
    '''<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
    <g fill="none" stroke="#2C2C2C" stroke-width="1.5" stroke-linecap="round">
        <path d="M100 190 C100 190 100 100 100 30"/>
        <path d="M100 50 C85 45 75 50 70 60"/>
        <path d="M100 50 C115 45 125 50 130 60"/>
        <path d="M100 70 C80 65 68 72 63 85"/>
        <path d="M100 70 C120 65 132 72 137 85"/>
        <path d="M100 90 C75 85 60 95 55 110"/>
        <path d="M100 90 C125 85 140 95 145 110"/>
        <path d="M100 110 C70 105 55 118 48 135"/>
        <path d="M100 110 C130 105 145 118 152 135"/>
        <path d="M100 130 C65 125 48 140 40 160"/>
        <path d="M100 130 C135 125 152 140 160 160"/>
    </g>
    </svg>''',
    # Daisy
    '''<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
    <g fill="none" stroke="#2C2C2C" stroke-width="1.5" stroke-linecap="round">
        <path d="M100 185 C100 185 98 130 100 110"/>
        <path d="M100 85 C100 75 90 65 100 55 C110 65 100 75 100 85"/>
        <path d="M100 85 C110 80 120 70 115 60 C105 65 108 78 100 85"/>
        <path d="M100 85 C115 85 125 80 125 70 C115 72 112 82 100 85"/>
        <path d="M100 85 C115 90 125 95 125 105 C115 100 112 90 100 85"/>
        <path d="M100 85 C110 95 115 105 110 115 C105 105 105 95 100 85"/>
        <path d="M100 85 C90 95 85 105 90 115 C95 105 95 95 100 85"/>
        <path d="M100 85 C85 90 75 95 75 105 C85 100 88 90 100 85"/>
        <path d="M100 85 C85 85 75 80 75 70 C85 72 88 82 100 85"/>
        <path d="M100 85 C90 80 80 70 85 60 C95 65 92 78 100 85"/>
        <circle cx="100" cy="85" r="12"/>
        <path d="M85 140 C70 135 55 145 60 160"/>
        <path d="M115 150 C130 145 140 155 135 170"/>
    </g>
    </svg>''',
    # Eucalyptus
    '''<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
    <g fill="none" stroke="#2C2C2C" stroke-width="1.5" stroke-linecap="round">
        <path d="M100 190 C100 190 100 100 105 20"/>
        <ellipse cx="82" cy="40" rx="15" ry="10" transform="rotate(-20 82 40)"/>
        <ellipse cx="118" cy="55" rx="15" ry="10" transform="rotate(20 118 55)"/>
        <ellipse cx="80" cy="70" rx="16" ry="11" transform="rotate(-15 80 70)"/>
        <ellipse cx="120" cy="88" rx="16" ry="11" transform="rotate(15 120 88)"/>
        <ellipse cx="78" cy="105" rx="18" ry="12" transform="rotate(-10 78 105)"/>
        <ellipse cx="122" cy="125" rx="18" ry="12" transform="rotate(10 122 125)"/>
        <ellipse cx="80" cy="145" rx="20" ry="13" transform="rotate(-8 80 145)"/>
        <ellipse cx="120" cy="165" rx="20" ry="13" transform="rotate(8 120 165)"/>
    </g>
    </svg>''',
    # Peony
    '''<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
    <g fill="none" stroke="#2C2C2C" stroke-width="1.5" stroke-linecap="round">
        <path d="M100 185 C100 185 100 130 100 110"/>
        <path d="M100 100 C85 85 65 80 55 88 C50 95 60 105 75 100 C65 108 62 120 72 125 C82 130 90 118 100 100"/>
        <path d="M100 100 C115 85 135 80 145 88 C150 95 140 105 125 100 C135 108 138 120 128 125 C118 130 110 118 100 100"/>
        <path d="M100 100 C95 80 85 65 90 55 C98 48 102 48 110 55 C115 65 105 80 100 100"/>
        <path d="M100 100 C88 95 78 100 75 110 C72 120 82 125 92 118"/>
        <path d="M100 100 C112 95 122 100 125 110 C128 120 118 125 108 118"/>
        <path d="M80 140 C65 135 50 142 55 158"/>
        <path d="M120 145 C135 140 150 148 145 162"/>
    </g>
    </svg>''',
    # Wildflower
    '''<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
    <g fill="none" stroke="#2C2C2C" stroke-width="1.5" stroke-linecap="round">
        <path d="M100 190 C100 190 95 140 90 110"/>
        <path d="M90 110 C85 100 80 85 90 80 C95 78 95 85 90 90"/>
        <path d="M90 90 C82 88 75 82 80 75 C85 72 88 78 90 85"/>
        <path d="M75 170 C70 160 60 155 50 160"/>
        <path d="M105 150 C110 140 120 135 130 140"/>
        <path d="M130 140 C135 130 140 120 135 115 C130 118 132 128 130 140"/>
        <path d="M50 160 C45 150 40 140 45 135 C50 138 48 148 50 160"/>
        <circle cx="90" cy="85" r="5"/>
        <circle cx="130" cy="130" r="4"/>
        <circle cx="50" cy="150" r="4"/>
    </g>
    </svg>''',
    # Monstera leaf
    '''<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
    <g fill="none" stroke="#2C2C2C" stroke-width="1.5" stroke-linecap="round">
        <path d="M100 190 C100 190 100 140 100 100"/>
        <path d="M100 100 C70 80 50 50 55 30 C65 25 80 35 90 50 C85 40 88 25 100 20 C112 25 115 40 110 50 C120 35 135 25 145 30 C150 50 130 80 100 100"/>
        <path d="M90 50 C95 60 95 75 90 85"/>
        <path d="M110 50 C105 60 105 75 110 85"/>
        <path d="M75 65 C85 70 92 80 95 90"/>
        <path d="M125 65 C115 70 108 80 105 90"/>
    </g>
    </svg>''',
]


def _base_css():
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


def _wrap_html(title, body_html):
    """Wrap page HTML with a viewport meta and zoom-to-fit style so it's viewable in a browser."""
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{title} — PurpleOcaz Preview</title>
<style>
{_base_css()}
/* Preview: scale to fit browser window */
@media screen {{
    html {{ height: 100vh; }}
    body {{
        transform-origin: top left;
        transform: scale(min(calc(100vw / {IMG_W}), calc(100vh / {IMG_H})));
    }}
}}
</style>
</head>
<body>
{body_html}
</body>
</html>"""


def _svg_inline(content, w=200, h=200):
    """Resize SVG for inline use."""
    import re
    content = re.sub(r'viewBox="[^"]*"', f'viewBox="0 0 200 200" width="{w}" height="{h}"', content, count=1)
    return content


# ── Page 1: Hero ──

def page1_hero():
    design_count = 150
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
        if i >= len(SAMPLE_SVGS):
            break
        svg_cards += (
            f'<div class="card" style="left:{x}px;top:{y}px;'
            f'width:{sz}px;height:{sz}px;'
            f'transform:rotate({rot}deg)">'
            f'<div class="card-inner">'
            f'{_svg_inline(SAMPLE_SVGS[i], sz - 60, sz - 60)}</div></div>\n'
        )

    return _wrap_html("01 Hero", f"""
    <style>
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
    </style>
    <div class="badge">INSTANT DOWNLOAD</div>
    {svg_cards}
    <div class="banner">
        <div class="num serif">{design_count}+</div>
        <div class="title serif">Fine-Line Botanical</div>
        <div class="sub serif">Tattoo Designs</div>
        <div class="fmts">SVG &middot; PNG &middot; DXF &middot; PDF &middot; EPS</div>
        <div class="logo serif">PURPLEOCAZ</div>
    </div>
    """)


# ── Page 2: What You Get ──

def page2_what_you_get():
    design_count = 150
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
    for i, s in enumerate(SAMPLE_SVGS[:8]):
        grid_items += f'<div class="cell">{_svg_inline(s, 160, 160)}</div>'

    return _wrap_html("02 What You Get", f"""
    <style>
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
    </style>
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
    """)


# ── Page 3: Please Note ──

def page3_please_note():
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

    return _wrap_html("03 Please Note", f"""
    <style>
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
    </style>
    <h1 class="script">Please Note</h1>
    <div class="divider"></div>
    <div class="notes">{items}</div>
    <div class="trust">
        <div class="trust-title purple">&#9733; COMMERCIAL LICENSE INCLUDED &#9733;</div>
        <div class="trust-sub dim">Personal &amp; commercial use permitted</div>
    </div>
    <div class="logo serif purple">PURPLEOCAZ</div>
    """)


# ── Page 4: Usage Ideas ──

def page4_usage():
    uses = [
        ("Tattoo Stencils", "Professional fine-line tattoo references"),
        ("Cricut &amp; Cutting", "SVG &amp; DXF ready for cutting machines"),
        ("Wall Art &amp; Prints", "High-res PNG for gallery-quality prints"),
        ("Apparel &amp; Products", "Sublimation, embroidery, engraving"),
    ]

    cards = ""
    for i, (title, desc) in enumerate(uses):
        svg = _svg_inline(SAMPLE_SVGS[i], 280, 280) if i < len(SAMPLE_SVGS) else ""
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
    pill_html = "".join(f'<span class="pill">{p}</span>' for p in pills)

    return _wrap_html("04 Endless Possibilities", f"""
    <style>
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
    </style>
    <div class="head"><h1 class="serif purple">Endless Possibilities</h1>
    <div class="divider"></div></div>
    <div class="grid">{cards}</div>
    <div class="also">
        <div class="also-label dim">Also perfect for</div>
        <div class="pills">{pill_html}</div>
    </div>
    """)


# ── Page 5: Categories ──

def page5_categories():
    categories = {
        "roses": 22, "wildflowers": 18, "ferns": 15, "eucalyptus": 20,
        "peonies": 16, "lavender": 14, "monstera": 12, "daisies": 18,
    }

    cards = ""
    for i, (cat_name, count) in enumerate(sorted(categories.items())):
        svg = _svg_inline(SAMPLE_SVGS[i % len(SAMPLE_SVGS)], 180, 180)
        display_name = cat_name.replace("-", " ").title()
        cards += f"""
        <div class="cat-card">
            <div class="cat-svg">{svg}</div>
            <div class="cat-info">
                <div class="cat-name">{display_name}</div>
                <div class="cat-count purple">{count} designs</div>
            </div>
        </div>"""

    return _wrap_html("05 Categories", f"""
    <style>
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
    </style>
    <div class="head">
        <h1 class="serif purple">8 Design Categories</h1>
        <div class="divider"></div>
        <p class="dim">Something for every style</p>
    </div>
    <div class="grid">{cards}</div>
    <div class="footer serif">PURPLEOCAZ &middot; FINE-LINE BOTANICAL COLLECTION</div>
    """)


# ── Page 6: Leave a Review ──

def page6_leave_review():
    stars = "".join('<span class="star">&#9733;</span>' for _ in range(5))

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

    return _wrap_html("06 Leave a Review", f"""
    <style>
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
    </style>
    <h1 class="script">We'd Love Your Feedback!</h1>
    <div class="divider"></div>
    <div class="stars">{stars}</div>
    <div class="card">
        <div class="steps">{step_html}</div>
    </div>
    <div class="note dim">Your reviews help small creators grow &#10084;</div>
    <div class="logo serif purple">PURPLEOCAZ</div>
    """)


# ── Page 7: Thank You ──

def page7_thank_you():
    return _wrap_html("07 Thank You", f"""
    <style>
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
    </style>
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
    """)


# ── Index page ──

def index_page():
    return """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>PurpleOcaz Thumbnail Preview</title>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&family=Great+Vibes&display=swap');
    * { margin:0; padding:0; box-sizing:border-box; }
    body { font-family:'Montserrat',sans-serif; background:#F5F5F5; padding:40px; }
    h1 { font-family:'Great Vibes',cursive; font-size:48px; color:#6B3E9E;
         text-align:center; margin-bottom:10px; }
    .sub { text-align:center; color:#999; margin-bottom:40px; font-size:14px; }
    .grid { display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr));
            gap:24px; max-width:1200px; margin:0 auto; }
    .card { background:#FFF; border-radius:16px; padding:32px; text-align:center;
            box-shadow:0 4px 16px rgba(0,0,0,0.06); transition:transform 0.2s;
            text-decoration:none; color:#2C2C2C; }
    .card:hover { transform:translateY(-4px); box-shadow:0 8px 32px rgba(0,0,0,0.1); }
    .card .num { font-size:48px; font-weight:700; color:#6B3E9E; }
    .card .name { font-size:18px; font-weight:600; margin-top:8px; }
    .card .desc { font-size:13px; color:#999; margin-top:6px; }
    .note { text-align:center; margin-top:40px; color:#999; font-size:13px; }
</style>
</head>
<body>
<h1>PurpleOcaz</h1>
<p class="sub">Etsy Thumbnail Preview — 7 listing images at 2250x3000px</p>
<div class="grid">
    <a class="card" href="01-Hero.html">
        <div class="num">01</div>
        <div class="name">Hero</div>
        <div class="desc">Flat-lay SVG designs on white cards, purple banner</div>
    </a>
    <a class="card" href="02-What-You-Get.html">
        <div class="num">02</div>
        <div class="name">What You Get</div>
        <div class="desc">5 format cards, stats bar, sample grid</div>
    </a>
    <a class="card" href="03-Please-Note.html">
        <div class="num">03</div>
        <div class="name">Please Note</div>
        <div class="desc">Trust signals, commercial license badge</div>
    </a>
    <a class="card" href="04-Usage-Ideas.html">
        <div class="num">04</div>
        <div class="name">Endless Possibilities</div>
        <div class="desc">Use-case cards, editorial style</div>
    </a>
    <a class="card" href="05-Categories.html">
        <div class="num">05</div>
        <div class="name">Categories</div>
        <div class="desc">8 categories with counts and samples</div>
    </a>
    <a class="card" href="06-Leave-Review.html">
        <div class="num">06</div>
        <div class="name">Leave a Review</div>
        <div class="desc">Star rating, 3-step instructions</div>
    </a>
    <a class="card" href="07-Thank-You.html">
        <div class="num">07</div>
        <div class="name">Thank You</div>
        <div class="desc">Small business appreciation, brand banner</div>
    </a>
</div>
<p class="note">These previews use sample botanical SVGs. Real listings use AI-generated designs.</p>
</body>
</html>"""


def main():
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "output", "thumbnail_preview")
    os.makedirs(out_dir, exist_ok=True)

    pages = [
        ("01-Hero.html", page1_hero()),
        ("02-What-You-Get.html", page2_what_you_get()),
        ("03-Please-Note.html", page3_please_note()),
        ("04-Usage-Ideas.html", page4_usage()),
        ("05-Categories.html", page5_categories()),
        ("06-Leave-Review.html", page6_leave_review()),
        ("07-Thank-You.html", page7_thank_you()),
        ("index.html", index_page()),
    ]

    for filename, html in pages:
        path = os.path.join(out_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  {filename}")

    print(f"\nPreview ready: {out_dir}/index.html")
    print(f"Open in browser: file://{out_dir}/index.html")


if __name__ == "__main__":
    main()
