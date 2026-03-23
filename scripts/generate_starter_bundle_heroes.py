#!/usr/bin/env python3
"""
Generate starter bundle hero thumbnails for all 5 niches.
Bold minimal dark design: dark bg, white serif title, gold price,
gold dividers, feature pills, niche subtitle, footer bar.

Usage:
    python scripts/generate_starter_bundle_heroes.py
"""

import os
from PIL import Image, ImageDraw, ImageFont

# ── Config ────────────────────────────────────────────────────────────────────
SZ = 3000  # Square canvas
PRICE = "£9.99"

# Colors
BG_COLOR = (28, 28, 30)           # Near-black
GOLD = (191, 163, 100)            # Muted gold for price, dividers, subtitle
GOLD_PILL = (160, 140, 85)        # Slightly darker gold for pill outlines/text
WHITE = (255, 255, 255)
FOOTER_BG = (191, 163, 100)      # Gold footer bar
FOOTER_TEXT = (40, 40, 40)        # Dark text on gold bar

# Fonts
_SERIF_BOLD = '/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf'
_SANS_BOLD  = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
_SANS       = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

def _font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

# Niche definitions
NICHES = [
    {
        "name": "Tattoo",
        "subtitle": "TATTOO STUDIO",
        "output_dir": "outputs/tattoo-starter-bundle",
        "output_file": "hero_v2.png",
    },
    {
        "name": "Barbershop",
        "subtitle": "BARBERSHOP",
        "output_dir": "outputs/barbershop-starter-bundle",
        "output_file": "hero_starter_bundle.png",
    },
    {
        "name": "Nail Tech",
        "subtitle": "NAIL TECH",
        "output_dir": "outputs/nail-tech-starter-bundle",
        "output_file": "hero_starter_bundle.png",
    },
    {
        "name": "Lash Tech",
        "subtitle": "LASH TECH",
        "output_dir": "outputs/lash-tech-starter-bundle",
        "output_file": "hero_starter_bundle.png",
    },
    {
        "name": "Hair Salon",
        "subtitle": "HAIR SALON",
        "output_dir": "outputs/hair-salon-starter-bundle",
        "output_file": "hero_starter_bundle.png",
    },
]

PILLS = ["8 PDF Forms", "Business Card", "Appointment Card"]


def _center_text(draw, text, y, font, fill):
    """Draw text centered horizontally at given y."""
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (SZ - tw) // 2
    draw.text((x, y), text, font=font, fill=fill)


def _draw_pill(draw, cx, cy, text, font):
    """Draw a rounded pill outline with text centered."""
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    pad_x, pad_y = 55, 28
    pw, ph = tw + pad_x * 2, th + pad_y * 2
    x0, y0 = cx - pw // 2, cy - ph // 2
    draw.rounded_rectangle(
        [x0, y0, x0 + pw, y0 + ph],
        radius=ph // 2,
        outline=GOLD_PILL,
        width=4,
    )
    tx = cx - tw // 2
    ty = cy - th // 2
    draw.text((tx, ty), text, font=font, fill=GOLD_PILL)


def generate_hero(niche):
    img = Image.new('RGB', (SZ, SZ), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Fonts
    f_title = _font(_SERIF_BOLD, 220)
    f_price_symbol = _font(_SERIF_BOLD, 200)
    f_price = _font(_SERIF_BOLD, 280)
    f_pill = _font(_SANS_BOLD, 56)
    f_subtitle = _font(_SANS, 60)
    f_footer = _font(_SANS, 40)

    # ── Title: "STARTER" / "BUNDLE" ──────────────────────────────────────
    _center_text(draw, "STARTER", 280, f_title, WHITE)
    _center_text(draw, "BUNDLE", 520, f_title, WHITE)

    # ── Gold divider line 1 ──────────────────────────────────────────────
    div_y1 = 800
    div_margin = 600
    draw.line([(div_margin, div_y1), (SZ - div_margin, div_y1)],
              fill=GOLD, width=4)

    # ── Price: "£9.99" with £ in gold, rest in gold ─────────────────────
    # Measure the full price text to center it
    price_text = PRICE
    bbox_full = draw.textbbox((0, 0), price_text, font=f_price)

    # Split into £ symbol and number
    symbol = "£"
    number = PRICE[1:]  # "9.99"

    bbox_sym = draw.textbbox((0, 0), symbol, font=f_price_symbol)
    sym_w = bbox_sym[2] - bbox_sym[0]
    bbox_num = draw.textbbox((0, 0), number, font=f_price)
    num_w = bbox_num[2] - bbox_num[0]

    total_w = sym_w + num_w + 10  # small gap
    start_x = (SZ - total_w) // 2
    price_y = 900

    # Draw £ slightly smaller
    draw.text((start_x, price_y + 40), symbol, font=f_price_symbol, fill=GOLD)
    draw.text((start_x + sym_w + 10, price_y), number, font=f_price, fill=GOLD)

    # ── Gold divider line 2 ──────────────────────────────────────────────
    div_y2 = 1300
    draw.line([(div_margin, div_y2), (SZ - div_margin, div_y2)],
              fill=GOLD, width=4)

    # ── Feature pills ────────────────────────────────────────────────────
    pill_y = 1500
    pill_spacing = 780
    start_pill_x = SZ // 2 - pill_spacing
    for i, label in enumerate(PILLS):
        cx = start_pill_x + i * pill_spacing
        _draw_pill(draw, cx, pill_y, label, f_pill)

    # ── Niche subtitle ───────────────────────────────────────────────────
    _center_text(draw, niche["subtitle"], 1700, f_subtitle, GOLD)

    # ── Gold footer bar ──────────────────────────────────────────────────
    footer_h = 100
    footer_y = SZ - footer_h
    draw.rectangle([0, footer_y, SZ, SZ], fill=FOOTER_BG)
    footer_text = "PurpleOcaz  ·  Professional Templates"
    _center_text(draw, footer_text, footer_y + 20, f_footer, FOOTER_TEXT)

    # ── Save ─────────────────────────────────────────────────────────────
    out_dir = niche["output_dir"]
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, niche["output_file"])
    img.save(out_path, quality=96)
    print(f"  Saved: {out_path}")
    return out_path


if __name__ == "__main__":
    print("Generating starter bundle heroes with £9.99...")
    for niche in NICHES:
        generate_hero(niche)
    print("Done!")
