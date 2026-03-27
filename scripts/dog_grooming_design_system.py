#!/usr/bin/env python3
"""
Dog Grooming Design System
Palette, fonts, and shared drawing helpers for the entire dog grooming bundle.
Import this from all build_dog_grooming_*.py scripts.
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# ── Palette ────────────────────────────────────────────────────────────────────
TEAL     = (13, 92, 99)       # #0D5C63  — headers, accents, section bars
GOLD     = (201, 169, 110)    # #C9A96E  — dividers, paw accents, highlights
CREAM    = (245, 240, 232)    # #F5F0E8  — light backgrounds, card light variant
CHARCOAL = (26, 26, 26)       # #1A1A1A  — body text, dark card background
WHITE    = (255, 255, 255)    # #FFFFFF  — text on dark, form fields
TEAL_MID = (20, 120, 128)     # mid-teal for hover/alt accents
TEAL_DARK= (8, 60, 65)        # darker teal for contrast
CREAM_ALT= (235, 228, 218)    # slightly darker cream for alternating rows

# ── Canvas sizes (pixels @ 300 dpi) ──────────────────────────────────────────
A4            = (2480, 3508)   # A4 portrait
A4_LAND       = (3508, 2480)   # A4 landscape
BCARD         = (1050, 600)    # Business card / appointment card / loyalty card
GIFT_CERT     = (2550, 1800)   # Gift certificate landscape
SOCIAL        = (1080, 1080)   # Instagram/social post
LISTING_IMG   = (3000, 3000)   # Etsy listing image

# ── Fonts ─────────────────────────────────────────────────────────────────────
FONT_BOLD    = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SERIF   = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_SERIFB  = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"


def font(size: int, bold: bool = False, serif: bool = False, serifbold: bool = False) -> ImageFont.FreeTypeFont:
    if serifbold: return ImageFont.truetype(FONT_SERIFB, size)
    if serif:     return ImageFont.truetype(FONT_SERIF,  size)
    if bold:      return ImageFont.truetype(FONT_BOLD,   size)
    return ImageFont.truetype(FONT_REGULAR, size)


# ── Drawing helpers ───────────────────────────────────────────────────────────

def centred(draw: ImageDraw.ImageDraw, y: int, text: str, fill, f, canvas_w: int = None):
    """Draw text horizontally centred on canvas_w (defaults to image width)."""
    w = canvas_w or draw.im.size[0]
    bb = draw.textbbox((0, 0), text, font=f)
    tw = bb[2] - bb[0]
    draw.text(((w - tw) // 2, y), text, fill=fill, font=f)


def right(draw: ImageDraw.ImageDraw, x_right: int, y: int, text: str, fill, f):
    """Draw text right-aligned to x_right."""
    bb = draw.textbbox((0, 0), text, font=f)
    tw = bb[2] - bb[0]
    draw.text((x_right - tw, y), text, fill=fill, font=f)


def gold_rule(draw: ImageDraw.ImageDraw, y: int, x0: int = 0, x1: int = None,
              thickness: int = 6, canvas_w: int = None):
    """Draw a gold horizontal rule."""
    if x1 is None:
        x1 = canvas_w or draw.im.size[0]
    draw.rectangle([x0, y, x1, y + thickness], fill=GOLD)


def teal_bar(draw: ImageDraw.ImageDraw, y: int, h: int, x0: int = 0,
             x1: int = None, canvas_w: int = None):
    """Draw a solid teal horizontal bar."""
    if x1 is None:
        x1 = canvas_w or draw.im.size[0]
    draw.rectangle([x0, y, x1, y + h], fill=TEAL)


def section_head(draw: ImageDraw.ImageDraw, x: int, y: int, text: str,
                 width: int = None, canvas_w: int = None) -> int:
    """Draw a teal section header bar. Returns y after the bar."""
    w = width or (canvas_w or draw.im.size[0]) - x
    draw.rectangle([x, y, x + w, y + 72], fill=TEAL)
    draw.text((x + 24, y + 14), text, fill=WHITE, font=font(42, bold=True))
    return y + 72


def field_line(draw: ImageDraw.ImageDraw, x: int, y: int, label: str,
               width: int = 2240, font_size: int = 36) -> int:
    """Draw a labelled underline field. Returns y after the field."""
    draw.text((x, y), label, fill=CHARCOAL, font=font(font_size, bold=True))
    y += 58
    draw.rectangle([x, y, x + width, y + 3], fill=TEAL)
    return y + 52


def field_pair(draw: ImageDraw.ImageDraw, x: int, y: int,
               label1: str, label2: str, total_w: int = 2240,
               font_size: int = 36) -> int:
    """Draw two side-by-side labelled fields. Returns y after."""
    half = (total_w - 60) // 2
    draw.text((x, y), label1, fill=CHARCOAL, font=font(font_size, bold=True))
    draw.text((x + half + 60, y), label2, fill=CHARCOAL, font=font(font_size, bold=True))
    y2 = y + 58
    draw.rectangle([x, y2, x + half, y2 + 3], fill=TEAL)
    draw.rectangle([x + half + 60, y2, x + total_w, y2 + 3], fill=TEAL)
    return y2 + 52


def checkbox(draw: ImageDraw.ImageDraw, x: int, y: int, label: str,
             font_size: int = 34) -> int:
    """Draw a checkbox with label. Returns y after."""
    draw.rectangle([x, y + 4, x + 36, y + 40], outline=TEAL, width=3)
    draw.text((x + 52, y + 4), label, fill=CHARCOAL, font=font(font_size))
    return y + 50


def table_row(draw: ImageDraw.ImageDraw, x: int, y: int, cols: list,
              widths: list, row_h: int = 60, alt: bool = False,
              header: bool = False) -> int:
    """Draw a table row with column text. Returns y after."""
    bg = TEAL if header else (CREAM_ALT if alt else WHITE)
    fg = WHITE if header else CHARCOAL
    total_w = sum(widths)
    draw.rectangle([x, y, x + total_w, y + row_h], fill=bg)
    draw.rectangle([x, y, x + total_w, y + row_h], outline=GOLD, width=1)
    cx = x
    for i, (col, w) in enumerate(zip(cols, widths)):
        draw.text((cx + 16, y + 14), str(col), fill=fg,
                  font=font(34 if not header else 36, bold=header))
        if i < len(cols) - 1:
            draw.line([(cx + w, y), (cx + w, y + row_h)], fill=GOLD, width=1)
        cx += w
    return y + row_h


# ── Paw print ──────────────────────────────────────────────────────────────────

def paw_print(draw: ImageDraw.ImageDraw, cx_: int, cy_: int,
              size: int = 60, fill=GOLD):
    """
    Draw a simple dog paw print.
    cx_, cy_ = centre of the main pad.
    size = radius of main pad.
    """
    # Main pad (slightly oval)
    pad_w = int(size * 1.0)
    pad_h = int(size * 1.15)
    draw.ellipse([cx_ - pad_w, cy_ - pad_h // 2,
                  cx_ + pad_w, cy_ + pad_h + pad_h // 2], fill=fill)

    # 4 toe pads
    tr = int(size * 0.38)
    toe_y_offset = int(size * 1.55)
    positions = [
        (cx_ - int(size * 0.95), cy_ - toe_y_offset + int(tr * 0.3)),  # far left
        (cx_ - int(size * 0.38), cy_ - toe_y_offset - int(tr * 0.4)),  # left inner
        (cx_ + int(size * 0.38), cy_ - toe_y_offset - int(tr * 0.4)),  # right inner
        (cx_ + int(size * 0.95), cy_ - toe_y_offset + int(tr * 0.3)),  # far right
    ]
    for tx, ty in positions:
        draw.ellipse([tx - tr, ty - tr, tx + tr, ty + tr], fill=fill)


# ── A4 form helpers ───────────────────────────────────────────────────────────

def a4_header(img: Image.Image, draw: ImageDraw.ImageDraw,
              title: str, subtitle: str = "Professional Dog Grooming") -> int:
    """
    Draw the standard A4 form header.
    Returns the y position where content should start.
    """
    W = img.width
    # Teal header band
    draw.rectangle([0, 0, W, 420], fill=TEAL)
    # Paw print — left side
    paw_print(draw, 180, 210, size=80, fill=GOLD)
    # Salon name placeholder
    draw.text((300, 80), "YOUR SALON NAME", fill=GOLD, font=font(56, bold=True))
    draw.text((300, 155), subtitle, fill=CREAM, font=font(38))
    # Form title — centred
    centred(draw, 255, title, WHITE, font(66, bold=True), canvas_w=W)
    # Gold rule
    gold_rule(draw, 420, thickness=8, canvas_w=W)
    return 460  # content starts here


def a4_footer(draw: ImageDraw.ImageDraw, canvas_w: int, canvas_h: int,
              template_name: str = ""):
    """Draw standard A4 footer."""
    draw.rectangle([0, canvas_h - 100, canvas_w, canvas_h], fill=TEAL)
    gold_rule(draw, canvas_h - 100, thickness=6, canvas_w=canvas_w)
    centred(draw, canvas_h - 76, "© PurpleOcaz — purpleocaz.etsy.com", CREAM,
            font(30), canvas_w=canvas_w)


# ── Spaces upload ─────────────────────────────────────────────────────────────

import os, boto3, urllib.request
from dotenv import load_dotenv


def upload_to_spaces(local_path: Path, spaces_key: str,
                     content_type: str = "image/png") -> str:
    """Upload file to DO Spaces with public-read ACL. Returns CDN URL."""
    load_dotenv("/root/NEW-AI-PROJECT/purpleocaz-canva-mcp/.env")
    s3 = boto3.client(
        "s3",
        endpoint_url="https://lon1.digitaloceanspaces.com",
        aws_access_key_id=os.environ["DO_SPACES_KEY"],
        aws_secret_access_key=os.environ["DO_SPACES_SECRET"],
    )
    s3.upload_file(
        str(local_path),
        "purpleocaz-assets",
        spaces_key,
        ExtraArgs={"ACL": "public-read", "ContentType": content_type},
    )
    url = f"https://purpleocaz-assets.lon1.digitaloceanspaces.com/{spaces_key}"
    resp = urllib.request.urlopen(url)
    assert resp.status == 200, f"Spaces verify failed: {url}"
    print(f"  ↑ {spaces_key} → HTTP 200")
    return url
