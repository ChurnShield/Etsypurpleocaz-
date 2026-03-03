# =============================================================================
# thumbnail_generator_tool.py
#
# BaseTool generating 7 Etsy listing images at 2250x3000px using Gemini AI
# (Nano Banana) for professional product photography.
#
# Primary: Gemini 3.1 Flash generates all 7 pages as AI product photography
# Fallback: HTML/Playwright rendering (if Gemini unavailable)
#
# Page 1: Hero (flat-lay botanical grid, count badge, purple banner)
# Page 2: "What You Get" (5 format cards, file math, sample designs)
# Page 3: "Please Note" (4 info bullets, commercial license badge)
# Page 4: "Endless Possibilities" (use-case showcase with designs)
# Page 5: Category Preview (8 category cards with sample designs)
# Page 6: "Leave a Review" (5-star rating, 3-step instructions)
# Page 7: "Thank You" (appreciation + brand footer)
# =============================================================================

import io
import os
import re
from typing import Any, Dict, List, Tuple

from lib.orchestrator.base_tool import BaseTool
from config import GEMINI_API_KEY, PLAYWRIGHT_PAGE_TIMEOUT_MS

IMG_W, IMG_H = 2250, 3000

# ── Brand palette ──
PURPLE     = "#6B3E9E"
PURPLE_LT  = "#9B59B6"
LAVENDER   = "#A78BFA"
GOLD       = "#F5A623"
RED_HEART  = "#E74C3C"
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
    """Generate 7 Etsy listing thumbnail images using Gemini AI."""

    def get_name(self) -> str:
        return "ThumbnailGeneratorTool"

    def execute(self, **kwargs) -> Dict[str, Any]:
        svg_dir = kwargs.get("svg_dir", "")
        output_dir = kwargs.get("output_dir", "")
        design_count = kwargs.get("design_count", 0)
        category_counts = kwargs.get("category_counts", {})
        gemini_api_key = kwargs.get("gemini_api_key", "") or GEMINI_API_KEY

        if not svg_dir or not output_dir:
            return {
                "success": False, "data": None,
                "error": "svg_dir and output_dir are required",
                "tool_name": self.get_name(), "metadata": {},
            }

        thumb_dir = os.path.join(output_dir, "thumbnails")
        os.makedirs(thumb_dir, exist_ok=True)

        # ── AI-powered generation (primary) ──
        if gemini_api_key:
            result = self._generate_ai_thumbnails(
                gemini_api_key, thumb_dir, design_count, category_counts)
            if result["success"]:
                return result
            print(f"       AI thumbnails failed: {result['error']}")
            print(f"       Falling back to HTML/Playwright...")

        # ── HTML/Playwright fallback ──
        return self._generate_html_thumbnails(
            svg_dir, thumb_dir, design_count, category_counts)

    # =========================================================================
    # AI-POWERED THUMBNAIL GENERATION (Gemini / Nano Banana)
    # =========================================================================

    def _generate_ai_thumbnails(
        self, api_key: str, thumb_dir: str,
        design_count: int, category_counts: dict
    ) -> Dict[str, Any]:
        """Generate all 7 pages using Gemini AI image generation."""
        try:
            from tools.gemini_image_client import generate_product_image
        except ImportError:
            return {
                "success": False, "data": None,
                "error": "gemini_image_client not importable",
                "tool_name": self.get_name(), "metadata": {},
            }

        prompts = _build_ai_prompts(design_count, category_counts)
        generated = []

        for name, prompt in prompts:
            print(f"       Generating {name} (AI)...", flush=True)
            result = generate_product_image(
                api_key, prompt,
                aspect_ratio="3:4",
                image_size="2K",
                max_retries=2,
            )

            if not result["success"]:
                return {
                    "success": False, "data": None,
                    "error": f"{name} failed: {result['error']}",
                    "tool_name": self.get_name(), "metadata": {},
                }

            out_path = os.path.join(thumb_dir, f"{name}.png")
            _save_and_resize(result["image_bytes"], out_path, IMG_W, IMG_H)
            generated.append(out_path)
            print(f"       {name}.png", flush=True)

        return {
            "success": True,
            "data": {"count": len(generated), "paths": generated,
                     "thumb_dir": thumb_dir, "method": "ai"},
            "error": None, "tool_name": self.get_name(),
            "metadata": {"pages": len(generated), "method": "ai"},
        }

    # =========================================================================
    # HTML/PLAYWRIGHT FALLBACK
    # =========================================================================

    def _generate_html_thumbnails(
        self, svg_dir: str, thumb_dir: str,
        design_count: int, category_counts: dict,
    ) -> Dict[str, Any]:
        """Fallback: render HTML pages via Playwright screenshots."""
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return {
                "success": False, "data": None,
                "error": "playwright not installed (and Gemini unavailable)",
                "tool_name": self.get_name(), "metadata": {},
            }

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
                    print(f"       {name}.png (HTML)")
                browser.close()
        except Exception as e:
            return {
                "success": False, "data": None, "error": str(e),
                "tool_name": self.get_name(), "metadata": {},
            }

        return {
            "success": True,
            "data": {"count": len(generated), "paths": generated,
                     "thumb_dir": thumb_dir, "method": "html"},
            "error": None, "tool_name": self.get_name(),
            "metadata": {"pages": len(generated), "method": "html"},
        }


# =============================================================================
# AI PROMPT BUILDERS
# =============================================================================

def _build_ai_prompts(
    design_count: int, category_counts: dict
) -> List[Tuple[str, str]]:
    """Build Gemini prompts for all 7 listing pages."""
    count_str = f"{design_count}+" if design_count >= 100 else str(design_count)
    total_files = design_count * 5
    cat_names = sorted(category_counts.keys())
    cat_list = ", ".join(n.replace("-", " ").title() for n in cat_names)
    cat_detail = "  ".join(
        f"{n.replace('-', ' ').title()} ({category_counts[n]} designs),"
        for n in cat_names
    )

    return [
        ("01-Hero", _prompt_hero(count_str, cat_list)),
        ("02-What-You-Get", _prompt_what_you_get(count_str, total_files)),
        ("03-Please-Note", _prompt_please_note()),
        ("04-Usage-Ideas", _prompt_usage_ideas()),
        ("05-Categories", _prompt_categories(cat_detail, len(cat_names))),
        ("06-Leave-Review", _prompt_leave_review()),
        ("07-Thank-You", _prompt_thank_you()),
    ]


def _prompt_hero(count_str: str, cat_list: str) -> str:
    return (
        "A stunning professional product photography flat-lay for an Etsy "
        "digital product listing, shot from directly above. "

        "SCENE: Warm cream/beige textured linen fabric background, natural "
        "and tactile. Soft diffused natural light from the top-left creates "
        "gentle shadows. "

        "CENTER ARRANGEMENT: 9 white paper cards arranged in a loose 3x3 "
        "scattered grid on the linen surface. Each card is slightly rotated "
        "at a casual angle (as if hand-placed on a desk) with subtle drop "
        "shadows. Each white card displays a DIFFERENT fine-line botanical "
        "tattoo design in pure black ink. The designs are: "
        "Top row: an open rose with layered petals, a daisy with detailed "
        "center, a lavender sprig with small buds. "
        "Middle row: a wildflower bouquet tied with a ribbon, a circular "
        "floral wreath made of mixed blooms and leaves, a peony in full bloom. "
        "Bottom row: a birth flower (carnation), a eucalyptus branch with "
        "round leaves, a delicate butterfly with floral wings. "

        "DESIGN STYLE: Every botanical illustration is FINE-LINE ART — "
        "thin delicate black lines only, no color fills, no shading, no "
        "watercolor, no gradients. Think professional tattoo flash sheet "
        "style. Clean, minimalist, elegant line work. "

        "PROPS: Small sprigs of real dried eucalyptus and dried lavender "
        "stems scattered naturally around the edges of the frame. A small "
        "spool of natural jute twine. One or two dried pressed flowers. "
        "All props partially cropped at frame edges for depth. "

        f"BOTTOM BANNER: A bold solid deep purple (#6B3E9E) banner "
        f"spanning the full width of the image at the very bottom "
        f"(approximately bottom 25%). "
        f"Centered white text on the purple banner: "
        f"Line 1 (very large, bold serif font): '{count_str} Fine-Line Botanical' "
        f"Line 2 (large, italic serif): 'Tattoo Designs' "
        f"Line 3 (small, uppercase, widely spaced sans-serif): "
        f"'SVG  ·  PNG  ·  DXF  ·  PDF  ·  EPS' "

        "TOP-LEFT CORNER: A small brand logo lockup with a circled 'P' "
        "monogram and 'PURPLEOCAZ' text in purple (#6B3E9E). "

        "TOP-RIGHT CORNER: A small rounded purple (#6B3E9E) badge with "
        "white uppercase text 'INSTANT DOWNLOAD'. Below it, a smaller "
        "white pill badge with 5 gold (#F5A623) stars and 'Top Rated'. "

        "BANNER VALUE PILLS: Below the format line on the purple banner, "
        "two pill-shaped badges side by side: "
        "Left pill (white background): 'Less than $0.05 per design' in "
        "purple text. "
        "Right pill (transparent with white border): '600+ Total Files "
        "Included' in white text. "

        "The overall image must look like premium Etsy product photography — "
        "warm, inviting, and professionally styled. Crisp details, natural "
        "textures, 300 DPI quality. "
        "Do NOT include any human hands, fingers, or body parts. "
        "Do NOT include any phones, tablets, or device screens."
    )


def _prompt_what_you_get(count_str: str, total_files: int) -> str:
    return (
        "A professional Etsy listing infographic image with a clean, modern "
        "design on a light cream/off-white (#F5F5F0) background. "

        "TOP SECTION: Large elegant serif heading 'What You Get' in dark "
        "charcoal text, centered. Below it, a thin purple (#6B3E9E) "
        "decorative line divider. "

        "FORMAT CARDS ROW: 5 white rounded cards arranged horizontally in "
        "a single row with subtle drop shadows. Each card has: "
        "a large bold purple (#6B3E9E) format label at top, a smaller "
        "description below in dark text, and a subtle note in grey. "
        "Card 1: 'SVG' — 'Scalable Vector' — 'Illustrator / Inkscape' "
        "Card 2: 'PNG' — '4096 x 4096' — 'Transparent background' "
        "Card 3: 'DXF' — 'CAD Format' — 'Cricut & Silhouette ready' "
        "Card 4: 'PDF' — 'Print Ready' — 'Professional printing' "
        "Card 5: 'EPS' — 'Professional' — 'Industry-standard vector' "

        "MATH EQUATION: Below the cards, a visual equation in large "
        "bold purple serif numerals: "
        f"'{count_str}' (with 'Designs' underneath) "
        f"'x' (multiplication symbol) "
        f"'5' (with 'Formats' underneath) "
        f"'=' (equals sign) "
        f"'{total_files}+' (with 'Total Files' underneath) "

        "BOTTOM SECTION: A 4x4 grid of small white cards, each showing "
        "a different fine-line botanical design in black ink. Designs include "
        "roses, daisies, lavender, wildflowers, wreaths, bouquets, ferns, "
        "eucalyptus, peonies, birth flowers, butterflies with floral wings, "
        "and other delicate botanical line art. Each design is pure fine-line "
        "art — thin black lines, no fills, no color, no shading. "

        "Purple (#6B3E9E) accent colors throughout for brand consistency. "
        "Clean professional typography using a serif font for headings "
        "and sans-serif for body text. "
        "The image should look like a high-end Etsy product listing slide. "
        "Do NOT include any human hands, fingers, or body parts."
    )


def _prompt_please_note() -> str:
    return (
        "A professional Etsy listing confidence-building slide with a clean, "
        "elegant design on a light cream/off-white (#F5F5F0) background. "

        "TOP-LEFT: Small brand logo lockup with a circled 'P' monogram "
        "and 'PURPLEOCAZ' text in purple (#6B3E9E). "

        "HEADING: Large elegant serif heading 'Buy With Confidence' in dark "
        "charcoal, centered. Below it, a thin purple (#6B3E9E) decorative "
        "line divider. Subtitle: 'Everything you need to know before you "
        "download' in grey. "

        "FOUR INFO CARDS: Stacked vertically with generous spacing between "
        "them. Each card is a wide white rounded rectangle with a subtle "
        "drop shadow and a bold purple (#6B3E9E) left border (5px). "
        "Each card has: a purple circle with a white checkmark on the left, "
        "then bold title text and a lighter description: "
        "Card 1: 'Instant Digital Download' — 'Files available immediately "
        "after purchase — no waiting' "
        "Card 2: '5 Professional File Formats' — 'SVG, PNG, DXF, PDF & "
        "EPS — works with Cricut & Silhouette' "
        "Card 3: 'Clean Black Line Art' — 'Transparent background — perfect "
        "for tattoo stencils, cutting & printing' "
        "Card 4: 'Lifetime Access' — 'Download anytime from your Etsy "
        "receipt — yours forever' "

        "BOTTOM ROW: Two side-by-side badges. Left badge: white card with "
        "purple border showing 'COMMERCIAL LICENSE' with stars. Right badge: "
        "white card with gold (#F5A623) border showing 5 gold stars and "
        "'Trusted by 100s of happy creators'. "

        "CTA BUTTON: A large purple (#6B3E9E) pill-shaped button with white "
        "text 'Add to Cart → Instant Access'. "
        "Small footnote below: 'No physical product shipped — digital "
        "download only' in light grey. "

        "Purple (#6B3E9E) accent color throughout. Clean professional layout. "
        "Do NOT include any botanical designs or flowers on this page. "
        "Do NOT include any human hands, fingers, or body parts."
    )


def _prompt_usage_ideas() -> str:
    return (
        "A professional Etsy listing slide showcasing usage ideas, "
        "with a clean design on a light cream/off-white (#F5F5F0) background. "

        "TOP: Large elegant serif heading 'Endless Possibilities' in "
        "purple (#6B3E9E), centered. Below it, a thin purple decorative "
        "line divider. "

        "FOUR USE-CASE CARDS: Arranged in a 2x2 grid with generous spacing. "
        "Each card is a white rounded rectangle with subtle shadow. "
        "Each card has a top illustration area showing a relevant scene "
        "with fine-line botanical designs, separated by a thin purple line "
        "from the text below. "

        "Card 1 (top-left): Illustration shows fine-line botanical designs "
        "arranged as tattoo flash art on paper. "
        "Title: 'Tattoo Stencils' in bold purple. "
        "Description: 'Fine-line tattoo references & flash art' in grey. "

        "Card 2 (top-right): Illustration shows botanical designs being "
        "cut on a cutting machine mat. "
        "Title: 'Cricut & Cutting' in bold purple. "
        "Description: 'SVG & DXF ready for cutting machines' in grey. "

        "Card 3 (bottom-left): Illustration shows a framed botanical "
        "print hanging on a wall in a modern room. "
        "Title: 'Wall Art & Prints' in bold purple. "
        "Description: 'High-res PNG for gallery-quality prints' in grey. "

        "Card 4 (bottom-right): Illustration shows botanical designs "
        "printed on t-shirts and tote bags. "
        "Title: 'Apparel & Products' in bold purple. "
        "Description: 'Sublimation, embroidery & engraving' in grey. "

        "BOTTOM: A row of rounded pill-shaped badges in purple outline: "
        "'Stickers' 'Invitations' 'Journals' 'Engraving' "
        "'Embroidery' 'Nail Art' 'Logos' 'Decals' "
        "Text above pills: 'Also perfect for' in grey sans-serif. "

        "All botanical designs shown are fine-line art style — thin black "
        "lines, no fills, no color. "
        "Purple (#6B3E9E) accent color throughout. Clean professional layout. "
        "Do NOT include any human hands, fingers, or body parts."
    )


def _prompt_categories(cat_detail: str, cat_count: int) -> str:
    return (
        "A professional Etsy listing slide showcasing design categories, "
        "with a clean design on a light cream/off-white (#F5F5F0) background. "

        f"TOP: Large elegant serif heading '{cat_count} Design Categories' in "
        f"purple (#6B3E9E), centered. Below it, a thin purple decorative "
        f"line divider. Subtitle: 'Something for every style' in grey. "

        f"CATEGORY CARDS: Arranged in a 2-column grid (4 rows = 8 cards total). "
        f"Each card is a white rounded rectangle with a purple left border "
        f"and subtle shadow. Each card has a light grey square area on the "
        f"left showing a representative fine-line botanical design, and text "
        f"on the right with the category name in bold dark text and a purple "
        f"design count below. "

        f"The categories and their designs: {cat_detail} "

        "For each category, the representative design should match: "
        "Roses: an open rose with layered petals. "
        "Wildflowers: a small wildflower bouquet. "
        "Birth Flowers: a carnation or daffodil. "
        "Botanical Stems: a eucalyptus or fern branch. "
        "Mini: a tiny simple flower or leaf. "
        "Wreaths and Frames: a circular floral wreath. "
        "Bouquets: a hand-tied flower arrangement. "
        "Decorative: a vine with berries or leaves. "

        "All designs are fine-line art — thin black lines, no fills, no color. "

        "FOOTER BAND: A solid purple (#6B3E9E) rounded rectangle spanning "
        "the bottom with white text: "
        "'PURPLEOCAZ · FINE-LINE BOTANICAL COLLECTION' in elegant "
        "widely-spaced serif letters. "

        "Purple (#6B3E9E) accent color throughout. Clean professional layout. "
        "Do NOT include any human hands, fingers, or body parts."
    )


def _prompt_leave_review() -> str:
    return (
        "A professional Etsy listing slide requesting a review, with a "
        "warm and inviting design on a light cream/off-white (#F5F5F0) "
        "background. "

        "TOP-LEFT: Small brand logo lockup with a circled 'P' monogram "
        "and 'PURPLEOCAZ' text in purple (#6B3E9E). "

        "HEADING: Large elegant serif heading 'Loving Your Designs?' in "
        "dark charcoal, centered. Below it, a thin purple (#6B3E9E) "
        "decorative line divider. Subtitle: 'Your feedback means the world "
        "to us and helps fellow creators find exactly what they need'. "

        "STARS: Five large 5-pointed stars in a row, all filled with "
        "GOLD (#F5A623) color — NOT purple. These should be prominent, "
        "warm, and eye-catching like real gold star ratings. "

        "INSTRUCTIONS CARD: A large white rounded card with subtle shadow "
        "containing three numbered steps: "
        "Step 1 (purple circle with white '1'): "
        "'Go to Your Etsy Purchases' — 'Open Etsy → Your Account → "
        "Purchases & Reviews' "
        "Step 2 (purple circle with white '2'): "
        "'Find This Order' — 'Click \"Write a Review\" next to your purchase' "
        "Step 3 (purple circle with white '3'): "
        "'Share Your Experience' — 'It only takes 30 seconds & helps "
        "other makers discover us' "

        "CTA BUTTON: A large purple (#6B3E9E) pill-shaped button with "
        "white text 'Leave a Review & Support Small Business' with heart "
        "symbols on each side. "
        "Below it: 'Every 5-star review helps us create more designs "
        "for you' in light grey. "

        "The overall mood should be warm, friendly, and genuine. "
        "IMPORTANT: Stars must be GOLD (#F5A623), not purple. "
        "Purple (#6B3E9E) accent color for everything else. "
        "Serif font for headings, clean sans-serif for body text. "
        "Do NOT include any botanical designs on this page. "
        "Do NOT include any human hands, fingers, or body parts."
    )


def _prompt_thank_you() -> str:
    return (
        "A professional Etsy listing 'Thank You' slide with an elegant, "
        "warm design. "

        "TOP 70% of the image: Light cream/off-white (#F5F5F0) background. "
        "Centered content: "
        "A large RED (#E74C3C) heart symbol at the top — NOT purple, "
        "it must be warm red like a real heart. "
        "Below it, very large elegant serif heading 'Thank You!' in dark "
        "charcoal. Below that, a thin purple decorative line divider. "
        "Subtitle: 'for supporting our small business' in lighter grey "
        "sans-serif, elegant and understated. "
        "Below that, a white rounded card with subtle shadow containing: "
        "'Every purchase helps us continue creating beautiful designs "
        "for makers, artists, and creators like you.' in medium-sized "
        "dark text with generous line height. "

        "TWO CTA BUTTONS side by side: "
        "Left button: solid purple (#6B3E9E) pill with white text "
        "'Favourite Our Shop' with a heart. "
        "Right button: purple outline pill with purple text "
        "'Browse More Designs →'. "
        "Below the buttons: 'New designs added regularly — follow us "
        "so you never miss a drop!' in light grey. "

        "BOTTOM: A solid deep purple (#6B3E9E) footer banner spanning "
        "the full width. Brand logo lockup centered: circled 'P' monogram "
        "in white next to 'PURPLEOCAZ' in large white serif letters. "
        "Below: 'HANDCRAFTED DIGITAL DESIGNS' in slightly transparent white. "

        "IMPORTANT: The heart must be RED (#E74C3C), not purple. "
        "The overall mood should be warm, appreciative, and professionally "
        "branded. Clean minimalist design. "
        "Do NOT include any botanical designs on this page. "
        "Do NOT include any human hands, fingers, or body parts."
    )


# =============================================================================
# IMAGE SAVE / RESIZE
# =============================================================================

def _save_and_resize(image_bytes: bytes, path: str, width: int, height: int):
    """Save Gemini output bytes as a resized PNG."""
    from PIL import Image

    img = Image.open(io.BytesIO(image_bytes))

    # Ensure RGB mode for PNG save
    if img.mode == "RGBA":
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        img = bg
    elif img.mode != "RGB":
        img = img.convert("RGB")

    img = img.resize((width, height), Image.LANCZOS)
    img.save(path, "PNG", optimize=True)


# =============================================================================
# HTML FALLBACK HELPERS (preserved from previous version)
# =============================================================================

def _collect_sample_svgs(svg_dir, max_per_cat=4):
    # Prioritise visually rich categories first so the hero grid looks best
    _priority = [
        "Roses", "Wreaths-and-Frames", "Bouquets", "Wildflowers",
        "Decorative", "Birth-Flowers", "Botanical-Stems", "Mini",
    ]
    cats = sorted(os.listdir(svg_dir))
    cats.sort(key=lambda c: (
        _priority.index(c) if c in _priority else len(_priority)
    ))
    samples = []
    for cat_name in cats:
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


def _brand_logo(color=None):
    """Inline SVG brand logo lockup (P monogram + PURPLEOCAZ wordmark)."""
    c = color or PURPLE
    sub_c = TEXT_DIM if c == PURPLE else "rgba(255,255,255,0.7)"
    return (
        f'<div style="display:flex;align-items:center;gap:14px">'
        f'<svg width="44" height="44" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">'
        f'<circle cx="50" cy="50" r="46" stroke="{c}" stroke-width="4" fill="none"/>'
        f'<text x="50" y="62" text-anchor="middle" font-family="\'Playfair Display\',serif"'
        f' font-size="52" font-weight="700" fill="{c}">P</text></svg>'
        f'<div><div style="font-family:\'Playfair Display\',serif;font-size:28px;font-weight:700;'
        f'color:{c};letter-spacing:3px;line-height:1">PURPLEOCAZ</div>'
        f'<div style="font-size:12px;letter-spacing:2px;color:{sub_c};text-transform:uppercase;'
        f'margin-top:2px">Handcrafted Digital Designs</div></div></div>'
    )


def _cta_pill(text, filled=True, width="auto"):
    """Reusable CTA pill button."""
    if filled:
        return (
            f'<div style="background:{PURPLE};border-radius:60px;padding:22px 56px;'
            f'text-align:center;width:{width}">'
            f'<span style="font-size:28px;font-weight:700;color:#FFF;letter-spacing:1px">{text}</span></div>'
        )
    return (
        f'<div style="border:3px solid {PURPLE};border-radius:60px;padding:20px 56px;'
        f'text-align:center;width:{width}">'
        f'<span style="font-size:28px;font-weight:700;color:{PURPLE};letter-spacing:1px">{text}</span></div>'
    )


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

    total_files = design_count * 5

    return f"""<!DOCTYPE html><html><head><style>
    {_base_css()}
    .badge {{ position:absolute; top:40px; right:50px; z-index:10;
              background:{PURPLE}; color:#FFF;
              padding:16px 36px; font-weight:700;
              font-size:26px; letter-spacing:3px;
              text-transform:uppercase; border-radius:8px;
              box-shadow:0 4px 16px rgba(107,62,158,0.3); }}
    .banner {{ position:absolute; bottom:0; left:0; right:0;
               height:480px; background:{PURPLE};
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
    <div style="position:absolute;top:40px;left:50px;z-index:10">{_brand_logo()}</div>
    <div class="badge">INSTANT DOWNLOAD</div>
    <div style="position:absolute;top:110px;right:50px;z-index:10;
         background:#FFF;border-radius:50px;padding:12px 28px;
         box-shadow:0 3px 12px rgba(0,0,0,0.1);display:flex;align-items:center;gap:8px">
        <span style="color:{GOLD};font-size:24px">&#9733;&#9733;&#9733;&#9733;&#9733;</span>
        <span style="font-size:18px;font-weight:600;color:{TEXT_MED}">Top Rated</span>
    </div>
    {svg_cards}
    <div class="banner">
        <div class="num serif">{count_str}</div>
        <div class="title serif">Fine-Line Botanical</div>
        <div class="sub serif">Tattoo Designs</div>
        <div class="fmts">SVG &middot; PNG &middot; DXF &middot; PDF &middot; EPS</div>
        <div style="margin-top:20px;display:flex;gap:20px;align-items:center">
            <div style="background:#FFF;border-radius:50px;padding:16px 48px">
                <span style="font-size:24px;font-weight:700;color:{PURPLE}">Less than $0.05 per design</span>
            </div>
            <div style="border:2px solid rgba(255,255,255,0.6);border-radius:50px;padding:16px 48px">
                <span style="font-size:24px;font-weight:600;color:#FFF">{total_files}+ Total Files Included</span>
            </div>
        </div>
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
    <div style="margin-bottom:20px">{_brand_logo()}</div>
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
    <div style="display:flex;gap:24px;margin-top:36px;width:100%;align-items:center;justify-content:center">
        {_cta_pill("Best Value: Less than $0.05 per design")}
        {_cta_pill("Add to Cart &rarr;", filled=False)}
    </div>
    </body></html>"""


# ── Page 3: Please Note ──────────────────────────────────────────────────────

def _page3_please_note():
    notes = [
        ("&#10003;", "Instant Digital Download",
         "Files available immediately after purchase &mdash; no waiting"),
        ("&#10003;", "5 Professional File Formats",
         "SVG, PNG, DXF, PDF &amp; EPS &mdash; works with Cricut &amp; Silhouette"),
        ("&#10003;", "Clean Black Line Art",
         "Transparent background &mdash; perfect for tattoo stencils, cutting &amp; printing"),
        ("&#10003;", "Lifetime Access",
         "Download anytime from your Etsy receipt &mdash; yours forever"),
    ]

    items = ""
    for icon, title, desc in notes:
        items += f"""
        <div style="display:flex;align-items:center;gap:30px;
                     background:#FFF;border-radius:16px;padding:36px 40px;
                     box-shadow:0 3px 12px rgba(0,0,0,0.05);
                     border-left:5px solid {PURPLE}">
            <div style="width:64px;height:64px;border-radius:50%;
                         background:{PURPLE};color:#FFF;
                         font-size:30px;font-weight:800;
                         display:flex;align-items:center;justify-content:center;
                         flex-shrink:0">{icon}</div>
            <div>
                <div style="font-size:34px;font-weight:700;color:{TEXT_DARK}">{title}</div>
                <div style="font-size:24px;margin-top:6px;color:{TEXT_MED}">{desc}</div>
            </div>
        </div>"""

    return f"""<!DOCTYPE html><html><head><style>
    {_base_css()}
    </style></head><body style="display:flex;flex-direction:column;
           align-items:center;justify-content:center;padding:80px 100px">
    <div style="position:absolute;top:40px;left:50px">{_brand_logo()}</div>
    <h1 class="serif" style="font-size:84px;color:{TEXT_DARK};margin-bottom:8px;margin-top:40px">
        Buy With Confidence</h1>
    <div class="divider"></div>
    <p style="font-size:26px;color:{TEXT_MED};margin-top:10px;text-align:center">
        Everything you need to know before you download</p>
    <div style="display:flex;flex-direction:column;gap:28px;width:100%;
                margin-top:44px">{items}</div>
    <div style="display:flex;gap:20px;margin-top:40px;width:100%">
        <div style="flex:1;border:3px solid {PURPLE};border-radius:16px;
                     padding:32px 40px;text-align:center;background:#FFF;
                     box-shadow:0 3px 12px rgba(0,0,0,0.05)">
            <div style="font-size:32px;font-weight:700;color:{PURPLE};
                         letter-spacing:2px">&#9733; COMMERCIAL LICENSE &#9733;</div>
            <div style="font-size:22px;margin-top:8px;color:{TEXT_MED}">
                Personal &amp; commercial use included</div>
        </div>
        <div style="flex:1;border:3px solid {GOLD};border-radius:16px;
                     padding:32px 40px;text-align:center;background:#FFF;
                     box-shadow:0 3px 12px rgba(0,0,0,0.05)">
            <div style="font-size:32px;font-weight:700;color:{GOLD};
                         letter-spacing:2px">&#9733; &#9733; &#9733; &#9733; &#9733;</div>
            <div style="font-size:22px;margin-top:8px;color:{TEXT_MED}">
                Trusted by 100s of happy creators</div>
        </div>
    </div>
    <div style="margin-top:40px;width:100%;max-width:900px;text-align:center">
        {_cta_pill("Add to Cart &rarr; Instant Access")}
    </div>
    <div style="margin-top:14px;font-size:20px;color:{TEXT_DIM};text-align:center">
        No physical product shipped &mdash; digital download only</div>
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
    <div style="margin-bottom:20px">{_brand_logo()}</div>
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
    <div style="display:flex;gap:24px;margin-top:30px;align-items:center;justify-content:center">
        {_cta_pill("Start Creating Today &rarr;")}
        <div style="font-size:24px;color:{TEXT_DIM}">120+ designs ready for your next project</div>
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

    total_designs = sum(category_counts.values())

    return f"""<!DOCTYPE html><html><head><style>
    {_base_css()}
    </style></head><body style="padding:50px 60px;display:flex;flex-direction:column">
    <div style="margin-bottom:20px">{_brand_logo()}</div>
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
                padding:36px;text-align:center;display:flex;flex-direction:column;align-items:center;gap:16px">
        <div style="font-size:36px;font-weight:700;color:#FFF;letter-spacing:1px">
            Get All {total_cats} Categories &mdash; {total_designs}+ Designs</div>
        <div style="background:#FFF;border-radius:50px;padding:16px 60px;margin-top:8px">
            <span style="font-size:26px;font-weight:700;color:{PURPLE}">Add to Cart &rarr; Instant Download</span>
        </div>
        <span class="serif" style="font-size:20px;letter-spacing:5px;
                     font-weight:600;color:rgba(255,255,255,0.7);margin-top:4px">
            PURPLEOCAZ &middot; FINE-LINE BOTANICAL COLLECTION</span>
    </div>
    </body></html>"""


# ── Page 6: Leave a Review ───────────────────────────────────────────────────

def _page6_leave_review():
    stars = "".join(
        f'<span style="font-size:90px;color:{GOLD};margin:0 8px">&#9733;</span>'
        for _ in range(5))

    steps = [
        ("1", "Go to Your Etsy Purchases",
         "Open Etsy &rarr; Your Account &rarr; Purchases &amp; Reviews"),
        ("2", "Find This Order",
         "Click &ldquo;Write a Review&rdquo; next to your purchase"),
        ("3", "Share Your Experience",
         "It only takes 30 seconds &amp; helps other makers discover us"),
    ]

    step_html = ""
    for num, title, desc in steps:
        step_html += f"""
        <div style="display:flex;align-items:center;gap:28px">
            <div style="width:64px;height:64px;border-radius:50%;
                         background:{PURPLE};color:#FFF;
                         font-size:28px;font-weight:800;
                         display:flex;align-items:center;justify-content:center;
                         flex-shrink:0">{num}</div>
            <div>
                <div style="font-size:34px;font-weight:700;color:{TEXT_DARK}">{title}</div>
                <div style="font-size:24px;margin-top:4px;color:{TEXT_MED}">{desc}</div>
            </div>
        </div>"""

    return f"""<!DOCTYPE html><html><head><style>
    {_base_css()}
    </style></head><body style="display:flex;flex-direction:column;
           align-items:center;justify-content:center;padding:80px 100px">
    <div style="position:absolute;top:40px;left:50px">{_brand_logo()}</div>
    <h1 class="serif" style="font-size:78px;color:{TEXT_DARK};margin-top:40px">
        Loving Your Designs?</h1>
    <div class="divider"></div>
    <p style="font-size:28px;color:{TEXT_MED};margin-top:10px;text-align:center;max-width:1600px">
        Your feedback means the world to us and helps fellow creators find exactly what they need</p>
    <div style="margin:36px 0 44px">{stars}</div>
    <div style="background:#FFF;border-radius:20px;
                 padding:56px 64px;width:100%;
                 box-shadow:0 4px 20px rgba(0,0,0,0.06)">
        <div style="display:flex;flex-direction:column;gap:40px">
            {step_html}
        </div>
    </div>
    <div style="margin-top:44px">
        {_cta_pill("&#10084; Leave a Review &amp; Support Small Business &#10084;")}
    </div>
    <div style="margin-top:24px;font-size:24px;color:{TEXT_DIM};text-align:center">
        Every 5-star review helps us create more designs for you</div>
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
        <div style="font-size:100px;color:{RED_HEART};margin-bottom:16px">&#10084;</div>
        <h1 class="serif" style="font-size:110px;color:{TEXT_DARK};margin-bottom:8px">
            Thank You!</h1>
        <div class="divider"></div>
        <div style="font-size:44px;font-weight:300;margin-top:16px;
                     color:{TEXT_MED};letter-spacing:1px">
            for supporting our small business</div>
        <div style="background:#FFF;border-radius:20px;padding:44px 60px;
                     margin-top:40px;max-width:1600px;
                     box-shadow:0 4px 20px rgba(0,0,0,0.06)">
            <p style="font-size:30px;line-height:1.7;color:{TEXT_DARK}">
                Every purchase helps us continue creating beautiful<br>
                designs for makers, artists, and creators like you.</p>
        </div>
        <div style="display:flex;gap:28px;margin-top:44px;flex-wrap:wrap;justify-content:center">
            {_cta_pill("&#10084; Favourite Our Shop")}
            {_cta_pill("Browse More Designs &rarr;", filled=False)}
        </div>
        <div style="margin-top:30px;font-size:22px;color:{TEXT_DIM};text-align:center">
            New designs added regularly &mdash; follow us so you never miss a drop!</div>
    </div>
    <div style="width:100%;background:{PURPLE};
                padding:50px 80px;text-align:center;
                display:flex;flex-direction:column;align-items:center">
        <div style="margin-bottom:12px">{_brand_logo("#FFF")}</div>
        <div style="font-size:22px;color:rgba(255,255,255,0.65);
                     letter-spacing:4px;
                     text-transform:uppercase">Handcrafted Digital Designs</div>
    </div>
    </body></html>"""
