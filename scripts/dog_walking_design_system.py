#!/usr/bin/env python3
"""
Dog Walking & Pet Sitting Design System
Palette, fonts, and shared drawing helpers for the entire bundle.
Import from all build_dog_walking_*.py scripts.
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# ── Palette ─────────────────────────────────────────────────────────────────────
GREEN      = (45, 95, 62)      # #2D5F3E — headers, accents, section bars
GOLD       = (201, 169, 110)   # #C9A96E — dividers, highlights
CREAM      = (245, 240, 232)   # #F5F0E8 — light backgrounds
CHARCOAL   = (26, 26, 26)      # #1A1A1A — body text, dark card bg
WHITE      = (255, 255, 255)
GREEN_DARK = (20, 55, 35)      # #14371C — darker green for contrast
CREAM_ALT  = (235, 228, 218)   # alternating table rows

# ── Canvas sizes (pixels @ 300 dpi) ─────────────────────────────────────────────
A4          = (2480, 3508)     # A4 portrait
A4_LAND     = (3508, 2480)     # A4 landscape
BCARD       = (1050, 600)      # Business / appointment / loyalty card
GIFT_CERT   = (2550, 1800)     # Gift certificate landscape
SOCIAL      = (1080, 1080)     # Instagram / social post
LISTING_IMG = (3000, 3000)     # Etsy listing image

# ── Fonts ────────────────────────────────────────────────────────────────────────
FONT_BOLD    = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SERIF   = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_SERIFB  = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"


def font(size: int, bold: bool = False, serif: bool = False, serifbold: bool = False):
    if serifbold: return ImageFont.truetype(FONT_SERIFB, size)
    if serif:     return ImageFont.truetype(FONT_SERIF,  size)
    if bold:      return ImageFont.truetype(FONT_BOLD,   size)
    return ImageFont.truetype(FONT_REGULAR, size)


# ── Drawing helpers ──────────────────────────────────────────────────────────────

def centred(draw, y, text, fill, f, canvas_w=None):
    w = canvas_w or draw.im.size[0]
    bb = draw.textbbox((0, 0), text, font=f)
    tw = bb[2] - bb[0]
    draw.text(((w - tw) // 2, y), text, fill=fill, font=f)


def right(draw, x_right, y, text, fill, f):
    bb = draw.textbbox((0, 0), text, font=f)
    tw = bb[2] - bb[0]
    draw.text((x_right - tw, y), text, fill=fill, font=f)


def gold_rule(draw, y, x0=0, x1=None, thickness=6, canvas_w=None):
    if x1 is None:
        x1 = canvas_w or draw.im.size[0]
    draw.rectangle([x0, y, x1, y + thickness], fill=GOLD)


def green_bar(draw, y, h, x0=0, x1=None, canvas_w=None):
    if x1 is None:
        x1 = canvas_w or draw.im.size[0]
    draw.rectangle([x0, y, x1, y + h], fill=GREEN)


def section_head(draw, x, y, text, width=None, canvas_w=None):
    """Draw a green section header bar. Returns y after the bar."""
    w = width or (canvas_w or draw.im.size[0]) - x
    draw.rectangle([x, y, x + w, y + 72], fill=GREEN)
    draw.text((x + 24, y + 14), text, fill=WHITE, font=font(42, bold=True))
    return y + 72


def field_line(draw, x, y, label, width=2240, font_size=36):
    draw.text((x, y), label, fill=CHARCOAL, font=font(font_size, bold=True))
    y += 58
    draw.rectangle([x, y, x + width, y + 3], fill=GREEN)
    return y + 52


def field_pair(draw, x, y, label1, label2, total_w=2240, font_size=36):
    half = (total_w - 60) // 2
    draw.text((x, y), label1, fill=CHARCOAL, font=font(font_size, bold=True))
    draw.text((x + half + 60, y), label2, fill=CHARCOAL, font=font(font_size, bold=True))
    y2 = y + 58
    draw.rectangle([x, y2, x + half, y2 + 3], fill=GREEN)
    draw.rectangle([x + half + 60, y2, x + total_w, y2 + 3], fill=GREEN)
    return y2 + 52


def field_triple(draw, x, y, labels, total_w=2240, font_size=34):
    w3 = (total_w - 80) // 3
    for i, lbl in enumerate(labels[:3]):
        xoff = x + i * (w3 + 40)
        draw.text((xoff, y), lbl, fill=CHARCOAL, font=font(font_size, bold=True))
        y2 = y + 54
        draw.rectangle([xoff, y2, xoff + w3, y2 + 3], fill=GREEN)
    return y + 54 + 50


def checkbox(draw, x, y, label, font_size=34):
    draw.rectangle([x, y + 4, x + 36, y + 40], outline=GREEN, width=3)
    draw.text((x + 52, y + 4), label, fill=CHARCOAL, font=font(font_size))
    return y + 50


def table_row(draw, x, y, cols, widths, row_h=60, alt=False, header=False):
    bg = GREEN if header else (CREAM_ALT if alt else WHITE)
    fg = WHITE if header else CHARCOAL
    total_w = sum(widths)
    draw.rectangle([x, y, x + total_w, y + row_h], fill=bg)
    draw.rectangle([x, y, x + total_w, y + row_h], outline=GOLD, width=1)
    cx = x
    for i, (col, w) in enumerate(zip(cols, widths)):
        draw.text((cx + 12, y + 12), str(col), fill=fg,
                  font=font(34 if not header else 36, bold=header))
        if i < len(cols) - 1:
            draw.line([(cx + w, y), (cx + w, y + row_h)], fill=GOLD, width=1)
        cx += w
    return y + row_h


# ── Paw print ────────────────────────────────────────────────────────────────────

def paw_print(draw, cx_, cy_, size=60, fill=GOLD):
    pad_w = int(size * 1.0)
    pad_h = int(size * 1.15)
    draw.ellipse([cx_ - pad_w, cy_ - pad_h // 2,
                  cx_ + pad_w, cy_ + pad_h + pad_h // 2], fill=fill)
    tr = int(size * 0.38)
    toe_y_offset = int(size * 1.55)
    positions = [
        (cx_ - int(size * 0.95), cy_ - toe_y_offset + int(tr * 0.3)),
        (cx_ - int(size * 0.38), cy_ - toe_y_offset - int(tr * 0.4)),
        (cx_ + int(size * 0.38), cy_ - toe_y_offset - int(tr * 0.4)),
        (cx_ + int(size * 0.95), cy_ - toe_y_offset + int(tr * 0.3)),
    ]
    for tx, ty in positions:
        draw.ellipse([tx - tr, ty - tr, tx + tr, ty + tr], fill=fill)


# ── A4 form helpers ───────────────────────────────────────────────────────────────

def a4_header(img, draw, title, subtitle="Dog Walking & Pet Sitting"):
    W = img.width
    draw.rectangle([0, 0, W, 420], fill=GREEN)
    paw_print(draw, 180, 210, size=80, fill=GOLD)
    draw.text((300, 80), "YOUR BUSINESS NAME", fill=GOLD, font=font(56, bold=True))
    draw.text((300, 155), subtitle, fill=CREAM, font=font(38))
    centred(draw, 255, title, WHITE, font(66, bold=True), canvas_w=W)
    gold_rule(draw, 420, thickness=8, canvas_w=W)
    return 460


def a4_footer(draw, canvas_w, canvas_h, template_name=""):
    draw.rectangle([0, canvas_h - 100, canvas_w, canvas_h], fill=GREEN)
    gold_rule(draw, canvas_h - 100, thickness=6, canvas_w=canvas_w)
    centred(draw, canvas_h - 76, "© PurpleOcaz — purpleocaz.etsy.com", CREAM,
            font(30), canvas_w=canvas_w)


# ── Spaces upload ─────────────────────────────────────────────────────────────────

import os, boto3, urllib.request
from dotenv import load_dotenv


def upload_to_spaces(local_path: Path, spaces_key: str, content_type="image/png") -> str:
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
