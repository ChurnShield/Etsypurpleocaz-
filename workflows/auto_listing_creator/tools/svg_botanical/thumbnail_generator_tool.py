# =============================================================================
# thumbnail_generator_tool.py
#
# BaseTool generating 5 Etsy listing images at 2250x3000px.
#
# Page 1: Hero flatlay (sample designs on light bg, purple banner)
# Page 2: "What You Get" (format overview, design count, grid preview)
# Page 3: "Please note" (digital download disclaimer, PurpleOcaz logo)
# Page 4: Usage mockup (stencil, Cricut, wall art, t-shirt examples)
# Page 5: Category preview (all 8 categories with representative designs)
# =============================================================================

import os
from typing import Any, Dict

from lib.orchestrator.base_tool import BaseTool
from config import PLAYWRIGHT_PAGE_TIMEOUT_MS

IMG_W, IMG_H = 2250, 3000
BRAND_PURPLE = "#6B3E9E"
BRAND_PURPLE_LIGHT = "#9B59B6"
HERO_BG = "#F5F5F5"
TEXT_DARK = "#2C2C2C"
TEXT_LIGHT = "#FFFFFF"
TEXT_GRAY = "#999999"

FONTS_CSS = (
    "@import url('https://fonts.googleapis.com/css2?"
    "family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400"
    "&family=Montserrat:wght@300;400;600;700;800"
    "&family=Great+Vibes&display=swap');"
)


class ThumbnailGeneratorTool(BaseTool):
    """Generate 5 Etsy listing thumbnail images."""

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
            thumb_dir = os.path.join(output_dir, "thumbnails")
            os.makedirs(thumb_dir, exist_ok=True)

            # Collect sample SVG content for previews
            samples = _collect_sample_svgs(svg_dir, count=24)
            sample_svgs = [s["content"] for s in samples]

            generated = []
            errors = []

            pages = [
                ("01-Hero", _page1_hero_html(
                    sample_svgs[:6], design_count)),
                ("02-What-You-Get", _page2_what_you_get_html(
                    sample_svgs[:12], design_count)),
                ("03-Please-Note", _page3_please_note_html()),
                ("04-Usage-Ideas", _page4_usage_ideas_html(
                    sample_svgs[:4])),
                ("05-Category-Preview", _page5_categories_html(
                    svg_dir, category_counts)),
            ]

            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(
                    viewport={"width": IMG_W, "height": IMG_H},
                    device_scale_factor=1,
                )

                for filename, html in pages:
                    try:
                        out_path = os.path.join(
                            thumb_dir, f"{filename}.png")
                        page.set_content(
                            html, wait_until="networkidle",
                            timeout=PLAYWRIGHT_PAGE_TIMEOUT_MS)
                        page.wait_for_timeout(1500)
                        page.screenshot(
                            path=out_path,
                            clip={"x": 0, "y": 0,
                                  "width": IMG_W, "height": IMG_H},
                        )
                        generated.append(out_path)
                    except Exception as e:
                        errors.append({
                            "page": filename, "error": str(e)})

                page.close()
                browser.close()

            return {
                "success": len(generated) > 0,
                "data": {
                    "thumbnail_dir": thumb_dir,
                    "generated": generated,
                    "count": len(generated),
                },
                "error": None if not errors else f"{len(errors)} pages failed",
                "tool_name": self.get_name(),
                "metadata": {"pages_generated": len(generated)},
            }

        except Exception as e:
            return {
                "success": False, "data": None,
                "error": str(e),
                "tool_name": self.get_name(), "metadata": {},
            }


# ── Sample SVG Collection ────────────────────────────────────────────────────

def _collect_sample_svgs(svg_dir, count=24):
    """Collect sample SVGs for thumbnails, spread across categories."""
    samples = []
    if not os.path.isdir(svg_dir):
        return samples

    categories = sorted(
        d for d in os.listdir(svg_dir)
        if os.path.isdir(os.path.join(svg_dir, d))
    )

    per_cat = max(count // max(len(categories), 1), 1)
    for cat in categories:
        cat_dir = os.path.join(svg_dir, cat)
        files = sorted(
            f for f in os.listdir(cat_dir) if f.endswith(".svg"))
        for fn in files[:per_cat]:
            try:
                with open(os.path.join(cat_dir, fn), "r",
                          encoding="utf-8") as fh:
                    content = fh.read()
                samples.append({
                    "name": fn[:-4], "category": cat,
                    "content": content})
            except Exception:
                pass
        if len(samples) >= count:
            break

    return samples[:count]


def _svg_inline(svg_content, width=200, height=200):
    """Wrap SVG content for inline HTML display at given size."""
    # Strip xml declaration if present
    content = svg_content
    if content.startswith("<?xml"):
        content = content[content.index("?>") + 2:].strip()
    # Override size
    import re
    content = re.sub(r'width="[^"]*"', f'width="{width}"', content, count=1)
    content = re.sub(
        r'height="[^"]*"', f'height="{height}"', content, count=1)
    return content


# ── Page HTML Templates ──────────────────────────────────────────────────────

def _page1_hero_html(sample_svgs, design_count):
    """Hero flatlay: sample designs arranged on light bg with purple banner."""
    # Arrange 6 sample designs in a 3x2 grid above the banner
    grid_items = ""
    for i, svg in enumerate(sample_svgs[:6]):
        grid_items += f"""<div class="design-card">
            {_svg_inline(svg, 320, 320)}
        </div>"""

    return f"""<!DOCTYPE html><html><head><style>
    {FONTS_CSS}
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ width:{IMG_W}px; height:{IMG_H}px; background:{HERO_BG};
           font-family:'Montserrat',sans-serif; overflow:hidden; }}
    .hero-area {{ display:flex; flex-wrap:wrap; justify-content:center;
                  align-items:center; gap:40px; padding:120px 80px 60px;
                  height:{IMG_H - 750}px; }}
    .design-card {{ background:white; border-radius:20px; padding:30px;
                    box-shadow:0 8px 30px rgba(0,0,0,0.08);
                    display:flex; align-items:center; justify-content:center; }}
    .banner {{ position:absolute; bottom:0; width:100%; height:750px;
              background:{BRAND_PURPLE}; display:flex; flex-direction:column;
              align-items:center; justify-content:center; }}
    .banner h1 {{ font-family:'Montserrat'; font-weight:800; font-size:92px;
                  color:{TEXT_LIGHT}; text-transform:uppercase;
                  letter-spacing:4px; text-align:center; line-height:1.1; }}
    .banner p {{ font-family:'Montserrat'; font-weight:400; font-size:38px;
                color:rgba(255,255,255,0.85); text-transform:uppercase;
                letter-spacing:6px; margin-top:20px; }}
    .badge {{ position:absolute; bottom:40px; right:60px; width:200px;
             height:200px; background:{TEXT_DARK}; border-radius:50%;
             display:flex; align-items:center; justify-content:center;
             flex-direction:column; }}
    .badge span {{ color:{TEXT_LIGHT}; font-family:'Montserrat';
                  font-weight:700; font-size:22px; text-transform:uppercase;
                  letter-spacing:2px; text-align:center; line-height:1.3; }}
    .count-badge {{ position:absolute; top:40px; right:60px;
                   background:{BRAND_PURPLE}; color:white; padding:18px 40px;
                   border-radius:40px; font-weight:700; font-size:32px;
                   font-family:'Montserrat'; }}
    </style></head><body>
    <div class="count-badge">{design_count} DESIGNS</div>
    <div class="hero-area">{grid_items}</div>
    <div class="banner">
        <h1>Fine-Line Botanical<br>Tattoo Bundle</h1>
        <p>SVG &bull; PNG &bull; DXF &bull; PDF &bull; EPS</p>
        <div class="badge"><span>INSTANT<br>DOWNLOAD</span></div>
    </div>
    </body></html>"""


def _page2_what_you_get_html(sample_svgs, design_count):
    """What You Get page: format overview, count, grid preview."""
    grid = ""
    for svg in sample_svgs[:12]:
        grid += f"""<div class="preview-cell">
            {_svg_inline(svg, 160, 160)}
        </div>"""

    return f"""<!DOCTYPE html><html><head><style>
    {FONTS_CSS}
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ width:{IMG_W}px; height:{IMG_H}px; background:white;
           font-family:'Montserrat',sans-serif; overflow:hidden; }}
    .header {{ background:{BRAND_PURPLE}; padding:60px; text-align:center; }}
    .header h1 {{ font-family:'Playfair Display'; font-size:72px;
                  color:white; font-weight:700; }}
    .formats {{ display:flex; justify-content:center; gap:30px;
               padding:50px 60px 30px; flex-wrap:wrap; }}
    .fmt {{ background:#F8F6F3; border-radius:16px; padding:24px 36px;
           text-align:center; min-width:180px; }}
    .fmt .name {{ font-weight:700; font-size:28px; color:{BRAND_PURPLE}; }}
    .fmt .desc {{ font-size:18px; color:{TEXT_GRAY}; margin-top:6px; }}
    .stats {{ display:flex; justify-content:center; gap:60px; padding:30px;
             background:{HERO_BG}; margin:20px 60px; border-radius:16px; }}
    .stat {{ text-align:center; }}
    .stat .num {{ font-size:56px; font-weight:800; color:{BRAND_PURPLE}; }}
    .stat .label {{ font-size:20px; color:{TEXT_GRAY}; margin-top:4px; }}
    .grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:20px;
            padding:30px 80px; }}
    .preview-cell {{ background:{HERO_BG}; border-radius:12px; padding:15px;
                    display:flex; align-items:center; justify-content:center; }}
    </style></head><body>
    <div class="header"><h1>What You Get</h1></div>
    <div class="formats">
        <div class="fmt"><div class="name">SVG</div><div class="desc">Vector</div></div>
        <div class="fmt"><div class="name">PNG</div><div class="desc">4096px</div></div>
        <div class="fmt"><div class="name">DXF</div><div class="desc">CAD</div></div>
        <div class="fmt"><div class="name">PDF</div><div class="desc">Print</div></div>
        <div class="fmt"><div class="name">EPS</div><div class="desc">Pro</div></div>
    </div>
    <div class="stats">
        <div class="stat"><div class="num">{design_count}</div>
            <div class="label">Unique Designs</div></div>
        <div class="stat"><div class="num">5</div>
            <div class="label">File Formats</div></div>
        <div class="stat"><div class="num">{design_count * 5}</div>
            <div class="label">Total Files</div></div>
    </div>
    <div class="grid">{grid}</div>
    </body></html>"""


def _page3_please_note_html():
    """Please Note page: digital download disclaimer."""
    return f"""<!DOCTYPE html><html><head><style>
    {FONTS_CSS}
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ width:{IMG_W}px; height:{IMG_H}px; background:#F8F6F3;
           font-family:'Montserrat',sans-serif; overflow:hidden;
           display:flex; flex-direction:column; align-items:center;
           justify-content:center; }}
    h1 {{ font-family:'Great Vibes'; font-size:120px; color:{TEXT_DARK};
         margin-bottom:20px; }}
    .divider {{ width:200px; height:2px; background:{TEXT_DARK};
               margin:10px auto 60px; position:relative; }}
    .divider::after {{ content:'\\2665'; position:absolute; top:-14px;
                      left:50%; transform:translateX(-50%);
                      background:#F8F6F3; padding:0 15px;
                      font-size:20px; color:{BRAND_PURPLE}; }}
    .notes {{ max-width:1600px; padding:0 100px; }}
    .note {{ display:flex; align-items:flex-start; gap:30px;
            margin-bottom:40px; }}
    .note .icon {{ width:60px; height:60px; background:{BRAND_PURPLE};
                  border-radius:50%; display:flex; align-items:center;
                  justify-content:center; flex-shrink:0; }}
    .note .icon span {{ color:white; font-size:28px; font-weight:700; }}
    .note p {{ font-size:32px; color:{TEXT_DARK}; line-height:1.5;
              padding-top:8px; }}
    .logo {{ margin-top:80px; text-align:center; }}
    .logo-text {{ font-family:'Playfair Display'; font-size:36px;
                 color:{BRAND_PURPLE}; font-weight:700; }}
    </style></head><body>
    <h1>Please note</h1>
    <div class="divider"></div>
    <div class="notes">
        <div class="note">
            <div class="icon"><span>1</span></div>
            <p>This is a <b>downloadable digital product</b>.
               You will receive instant access to all files after purchase.</p>
        </div>
        <div class="note">
            <div class="icon"><span>2</span></div>
            <p>There will be <b>NO physical product</b> shipped to you.
               All designs are delivered as digital files.</p>
        </div>
        <div class="note">
            <div class="icon"><span>3</span></div>
            <p>Files include <b>SVG, PNG, DXF, PDF, and EPS</b> formats.
               Compatible with Cricut, Silhouette, and all design software.</p>
        </div>
        <div class="note">
            <div class="icon"><span>4</span></div>
            <p>Designs are <b>black line art on transparent background</b>.
               Perfect for tattoo stencils, vinyl cutting, and printing.</p>
        </div>
    </div>
    <div class="logo">
        <div class="logo-text">Purple OCAZ</div>
    </div>
    </body></html>"""


def _page4_usage_ideas_html(sample_svgs):
    """Usage ideas page showing different use cases."""
    sample = _svg_inline(sample_svgs[0], 200, 200) if sample_svgs else ""

    return f"""<!DOCTYPE html><html><head><style>
    {FONTS_CSS}
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ width:{IMG_W}px; height:{IMG_H}px; background:white;
           font-family:'Montserrat',sans-serif; overflow:hidden; }}
    .header {{ background:{BRAND_PURPLE}; padding:50px; text-align:center; }}
    .header h1 {{ font-family:'Playfair Display'; font-size:68px;
                  color:white; font-weight:700; }}
    .ideas {{ padding:60px 80px; display:grid;
             grid-template-columns:1fr 1fr; gap:40px; }}
    .idea {{ background:{HERO_BG}; border-radius:20px; padding:50px;
            text-align:center; }}
    .idea .emoji {{ font-size:80px; margin-bottom:20px; display:block; }}
    .idea h2 {{ font-size:36px; color:{TEXT_DARK}; margin-bottom:12px; }}
    .idea p {{ font-size:22px; color:{TEXT_GRAY}; line-height:1.5; }}
    .idea .sample {{ margin-top:20px; opacity:0.7; }}
    .bottom {{ background:{HERO_BG}; margin:20px 80px; border-radius:20px;
              padding:50px; text-align:center; }}
    .bottom h2 {{ font-size:40px; color:{TEXT_DARK}; margin-bottom:15px; }}
    .bottom p {{ font-size:24px; color:{TEXT_GRAY}; }}
    .pills {{ display:flex; gap:20px; justify-content:center;
             flex-wrap:wrap; margin-top:25px; }}
    .pill {{ background:{BRAND_PURPLE}; color:white; padding:14px 32px;
            border-radius:30px; font-size:22px; font-weight:600; }}
    </style></head><body>
    <div class="header"><h1>Endless Possibilities</h1></div>
    <div class="ideas">
        <div class="idea">
            <span class="emoji"></span>
            <h2>Tattoo Stencils</h2>
            <p>Print on stencil paper for clean, professional tattoo transfers</p>
        </div>
        <div class="idea">
            <span class="emoji"></span>
            <h2>Cutting Machines</h2>
            <p>SVG files work perfectly with Cricut and Silhouette</p>
        </div>
        <div class="idea">
            <span class="emoji"></span>
            <h2>Wall Art & Prints</h2>
            <p>Print at any size for beautiful botanical wall decor</p>
        </div>
        <div class="idea">
            <span class="emoji"></span>
            <h2>Apparel & Products</h2>
            <p>Use on t-shirts, tote bags, mugs, and more</p>
        </div>
    </div>
    <div class="bottom">
        <h2>Also perfect for...</h2>
        <div class="pills">
            <span class="pill">Stickers</span>
            <span class="pill">Invitations</span>
            <span class="pill">Journals</span>
            <span class="pill">Engraving</span>
            <span class="pill">Embroidery</span>
            <span class="pill">Nail Art</span>
        </div>
    </div>
    </body></html>"""


def _page5_categories_html(svg_dir, category_counts):
    """Category preview showing all 8 categories with sample designs."""
    cat_blocks = ""
    for cat, cnt in sorted(category_counts.items()):
        # Get one sample SVG from this category
        sample_svg = ""
        cat_path = os.path.join(svg_dir, cat)
        if os.path.isdir(cat_path):
            files = sorted(f for f in os.listdir(cat_path)
                           if f.endswith(".svg"))
            if files:
                try:
                    with open(os.path.join(cat_path, files[0]), "r",
                              encoding="utf-8") as fh:
                        sample_svg = _svg_inline(fh.read(), 180, 180)
                except Exception:
                    pass

        display_name = cat.replace("-", " ").replace("and", "&")
        cat_blocks += f"""<div class="cat-card">
            <div class="cat-preview">{sample_svg}</div>
            <div class="cat-name">{display_name}</div>
            <div class="cat-count">{cnt} designs</div>
        </div>"""

    return f"""<!DOCTYPE html><html><head><style>
    {FONTS_CSS}
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ width:{IMG_W}px; height:{IMG_H}px; background:white;
           font-family:'Montserrat',sans-serif; overflow:hidden; }}
    .header {{ background:{BRAND_PURPLE}; padding:50px; text-align:center; }}
    .header h1 {{ font-family:'Playfair Display'; font-size:68px;
                  color:white; font-weight:700; }}
    .header p {{ font-size:28px; color:rgba(255,255,255,0.8);
                margin-top:10px; }}
    .grid {{ display:grid; grid-template-columns:1fr 1fr;
            gap:30px; padding:50px 80px; }}
    .cat-card {{ background:{HERO_BG}; border-radius:20px; padding:35px;
                display:flex; align-items:center; gap:25px; }}
    .cat-preview {{ background:white; border-radius:12px; padding:15px;
                   width:210px; height:210px; display:flex;
                   align-items:center; justify-content:center;
                   flex-shrink:0; }}
    .cat-name {{ font-size:30px; font-weight:700; color:{TEXT_DARK}; }}
    .cat-count {{ font-size:22px; color:{BRAND_PURPLE}; font-weight:600;
                 margin-top:6px; }}
    .footer {{ position:absolute; bottom:0; width:100%; height:120px;
              background:{BRAND_PURPLE}; display:flex; align-items:center;
              justify-content:center; }}
    .footer span {{ color:white; font-size:32px; font-weight:600;
                   letter-spacing:2px; }}
    </style></head><body>
    <div class="header">
        <h1>Design Categories</h1>
        <p>Something for every style</p>
    </div>
    <div class="grid">{cat_blocks}</div>
    <div class="footer">
        <span>PURPLEOCAZ &bull; FINE-LINE BOTANICAL COLLECTION</span>
    </div>
    </body></html>"""
