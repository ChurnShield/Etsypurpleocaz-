#!/usr/bin/env python3
"""
Barbershop Design System Reference Sheet — 2480x3508px (A4 at 300dpi).
Defines colour palette, typography, icons, spacing, components,
and header/footer templates for the entire barbershop bundle.
Uploads to DO Spaces.
"""

import os
import re
import math
import boto3
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ── Config ─────────────────────────────────────────────
PROJECT_ROOT = Path("/root/NEW-AI-PROJECT")
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "barbershop"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"

W, H = 2480, 3508

# ── Barbershop Palette ─────────────────────────────────
BG =       (10, 10, 10)      # #0A0A0A
PANELS =   (26, 26, 26)      # #1A1A1A
BOXES =    (42, 42, 42)      # #2A2A2A
GOLD =     (201, 169, 110)   # #C9A96E
WHITE =    (255, 255, 255)
GREY =     (136, 136, 136)   # #888888
BODY_WHITE = (255, 255, 255)


def font(size, bold=False, italic=False):
    path = FONT_SERIF if italic else (FONT_BOLD if bold else FONT_REGULAR)
    return ImageFont.truetype(path, size)


def centred(draw, y, text, fill, f):
    bbox = draw.textbbox((0, 0), text, font=f)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, y), text, fill=fill, font=f)


def gold_rule(draw, y, thickness=6, x1=0, x2=None):
    if x2 is None:
        x2 = W
    draw.rectangle([x1, y, x2, y + thickness], fill=GOLD)


def section_title(draw, y, text):
    gold_rule(draw, y)
    draw.text((120, y + 40), text, fill=GOLD, font=font(40, bold=True))
    return y + 40


def label_text(draw, x, y, text, fill=WHITE, size=20):
    draw.text((x, y), text, fill=fill, font=font(size))


def draw_pill(draw, cx, y, w, h, fill=None, outline=None, text="", text_color=WHITE, text_size=24):
    x = cx - w // 2
    r = h // 2
    if fill:
        draw.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=fill)
    if outline:
        draw.rounded_rectangle([x, y, x + w, y + h], radius=r, outline=outline, width=3)
    f = font(text_size, bold=True)
    bbox = draw.textbbox((0, 0), text, font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((x + (w - tw) // 2, y + (h - th) // 2 - 2), text, fill=text_color, font=f)


def main():
    print("Building Barbershop Design System Reference Sheet...")

    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # ════════════════════════════════════════════════════
    # SECTION 1 — COLOUR PALETTE (y=0 to y=600)
    # ════════════════════════════════════════════════════
    centred(draw, 80, "BARBERSHOP DESIGN SYSTEM", WHITE, font(72, bold=True))
    centred(draw, 160, "PurpleOcaz Template Bundle — Reference Sheet", GOLD, font(32))
    gold_rule(draw, 220)

    swatches = [
        (BG, "BACKGROUND", "#0A0A0A"),
        (PANELS, "PANELS", "#1A1A1A"),
        (BOXES, "BOXES", "#2A2A2A"),
        (GOLD, "GOLD ACCENT", "#C9A96E"),
        (WHITE, "WHITE TEXT", "#FFFFFF"),
        (GREY, "GREY BODY", "#888888"),
    ]

    sw_w, sw_h = 300, 200
    gap = (W - 6 * sw_w) // 7
    sy = 280

    for i, (color, label, hex_val) in enumerate(swatches):
        x = gap + i * (sw_w + gap)
        # Swatch rectangle with subtle gold border
        draw.rectangle([x, sy, x + sw_w, sy + sw_h], fill=color, outline=GOLD, width=2)
        # Label
        f22 = font(22)
        bbox = draw.textbbox((0, 0), label, font=f22)
        lw = bbox[2] - bbox[0]
        draw.text((x + (sw_w - lw) // 2, sy + sw_h + 15), label, fill=WHITE, font=f22)
        # Hex
        f18 = font(18)
        bbox = draw.textbbox((0, 0), hex_val, font=f18)
        hw = bbox[2] - bbox[0]
        draw.text((x + (sw_w - hw) // 2, sy + sw_h + 45), hex_val, fill=GOLD, font=f18)

    # ════════════════════════════════════════════════════
    # SECTION 2 — TYPOGRAPHY (y=620 to y=1200)
    # ════════════════════════════════════════════════════
    section_title(draw, 620, "TYPOGRAPHY")

    type_samples = [
        (720, "SHOP NAME", 72, True, WHITE, "72pt Bold — Shop Name / Hero"),
        (820, "MASTER BARBERS", 36, True, GOLD, "36pt Bold Gold — Subtitle / Title"),
        (900, "Section Header", 28, True, GOLD, "28pt Bold Gold — Section Headers"),
        (960, "Body copy text example here", 24, False, WHITE, "24pt Regular White — Body Text"),
        (1020, "Supporting detail text", 22, False, GREY, "22pt Regular Grey — Supporting Text"),
        (1080, "SMALL CAPS LABEL", 18, False, GOLD, "18pt Gold — Labels / Categories"),
        (1140, "fine print / disclaimer text", 16, False, GREY, "16pt Grey — Fine Print"),
    ]

    for y, text, size, bold, color, desc in type_samples:
        draw.text((180, y), text, fill=color, font=font(size, bold=bold))
        # Description label right-aligned
        f18 = font(18)
        bbox = draw.textbbox((0, 0), desc, font=f18)
        draw.text((W - 180 - (bbox[2] - bbox[0]), y + 5), desc, fill=GREY, font=f18)

    # ════════════════════════════════════════════════════
    # SECTION 3 — ICONS (y=1220 to y=1600)
    # ════════════════════════════════════════════════════
    section_title(draw, 1220, "ICONS")

    icon_positions = [
        (350, "SCISSORS"),
        (750, "MOUSTACHE"),
        (1150, "COMB"),
        (1550, "BARBER POLE"),
    ]

    icon_cy = 1380
    icon_size = 80

    # SCISSORS — two crossing diagonal lines with circles at ends
    sx = 350
    draw.line([(sx - 40, icon_cy - 40), (sx + 40, icon_cy + 40)], fill=GOLD, width=8)
    draw.line([(sx + 40, icon_cy - 40), (sx - 40, icon_cy + 40)], fill=GOLD, width=8)
    for cx, cy in [(sx - 40, icon_cy - 40), (sx + 40, icon_cy - 40),
                    (sx - 40, icon_cy + 40), (sx + 40, icon_cy + 40)]:
        draw.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], outline=GOLD, width=3)

    # MOUSTACHE — two curved arcs using polygon approximation
    mx = 750
    # Left half
    left_pts = []
    for angle in range(0, 181, 10):
        rad = math.radians(angle)
        px = mx - 10 - 35 * math.cos(rad)
        py = icon_cy + 5 - 25 * math.sin(rad)
        left_pts.append((px, py))
    # Right half (mirror)
    right_pts = []
    for angle in range(0, 181, 10):
        rad = math.radians(angle)
        px = mx + 10 + 35 * math.cos(rad)
        py = icon_cy + 5 - 25 * math.sin(rad)
        right_pts.append((px, py))
    for pts in [left_pts, right_pts]:
        for i in range(len(pts) - 1):
            draw.line([pts[i], pts[i + 1]], fill=GOLD, width=6)
    # Curl tips
    draw.ellipse([mx - 55, icon_cy - 5, mx - 45, icon_cy + 10], fill=GOLD)
    draw.ellipse([mx + 45, icon_cy - 5, mx + 55, icon_cy + 10], fill=GOLD)

    # COMB — rectangle with vertical lines
    cx_icon = 1150
    comb_w, comb_h = 80, 30
    cx1 = cx_icon - comb_w // 2
    cy1 = icon_cy - comb_h // 2
    draw.rectangle([cx1, cy1, cx1 + comb_w, cy1 + comb_h], outline=GOLD, width=3)
    # Teeth below
    tooth_count = 12
    for t in range(tooth_count):
        tx = cx1 + 4 + t * (comb_w - 8) // (tooth_count - 1)
        draw.line([(tx, cy1 + comb_h), (tx, cy1 + comb_h + 35)], fill=GOLD, width=3)

    # BARBER POLE — vertical rectangle with diagonal stripes
    bx = 1550
    pole_w, pole_h = 30, 80
    bx1 = bx - pole_w // 2
    by1 = icon_cy - pole_h // 2
    draw.rectangle([bx1, by1, bx1 + pole_w, by1 + pole_h], outline=GOLD, width=3)
    # Diagonal stripes
    for s in range(6):
        sy_off = by1 + s * 18 - 10
        draw.line([(bx1 + 3, sy_off), (bx1 + pole_w - 3, sy_off + 20)], fill=GOLD, width=4)
    # Top and bottom caps
    draw.rectangle([bx1 - 5, by1 - 8, bx1 + pole_w + 5, by1], fill=GOLD)
    draw.rectangle([bx1 - 5, by1 + pole_h, bx1 + pole_w + 5, by1 + pole_h + 8], fill=GOLD)
    # Ball on top
    draw.ellipse([bx - 10, by1 - 22, bx + 10, by1 - 2], fill=GOLD)

    # Labels
    for x, label in icon_positions:
        f20 = font(20)
        bbox = draw.textbbox((0, 0), label, font=f20)
        lw = bbox[2] - bbox[0]
        draw.text((x - lw // 2, icon_cy + 60), label, fill=WHITE, font=f20)

    # ════════════════════════════════════════════════════
    # SECTION 4 — SPACING & RULES (y=1620 to y=1900)
    # ════════════════════════════════════════════════════
    section_title(draw, 1620, "SPACING & DIVIDERS")

    rules = [
        (1720, 8, "Header/Footer Bar — 8px"),
        (1770, 4, "Section Divider — 4px"),
        (1810, 2, "Content Rule — 2px"),
    ]
    for y, thick, label in rules:
        gold_rule(draw, y, thick, 180, W - 180)
        draw.text((W - 180 - draw.textbbox((0, 0), label, font=font(18))[2], y - 22), label, fill=GREY, font=font(18))

    # Short accent rule
    y = 1850
    cw_rule = 400
    gold_rule(draw, y, 2, (W - cw_rule) // 2, (W + cw_rule) // 2)
    label = "Short Accent Rule — 400px"
    draw.text((W - 180 - draw.textbbox((0, 0), label, font=font(18))[2], y - 22), label, fill=GREY, font=font(18))

    # Margins note
    margins = "Left margin: 180px  |  Right margin: 180px  |  Section gap: 60px  |  Item spacing: 40px"
    centred(draw, 1890, margins, WHITE, font(22))

    # ════════════════════════════════════════════════════
    # SECTION 5 — COMPONENT EXAMPLES (y=1920 to y=2800)
    # ════════════════════════════════════════════════════
    section_title(draw, 1940, "COMPONENTS")

    # Primary CTA Button
    draw_pill(draw, W // 2, 2040, 400, 60, fill=GOLD, text="BOOK NOW", text_color=WHITE)
    centred(draw, 2115, "Primary CTA Button — Gold Fill", GREY, font(20))

    # Secondary Button (outline)
    draw_pill(draw, W // 2, 2160, 400, 60, outline=GOLD, text="LEARN MORE", text_color=GOLD)
    centred(draw, 2235, "Secondary Button — Gold Outline", GREY, font(20))

    # Checkboxes
    cb_y = 2290
    cb_items = ["Service option one", "Service option two", "Service option three"]
    for i, item in enumerate(cb_items):
        bx = 400
        by = cb_y + i * 45
        draw.rectangle([bx, by, bx + 30, by + 30], outline=GOLD, width=2)
        draw.text((bx + 45, by + 2), item, fill=WHITE, font=font(22))
    centred(draw, cb_y + 150, "Checkbox Style — 30x30px Gold Outline", GREY, font(20))

    # Detail Box
    box_y = 2500
    box_x = (W - 2100) // 2
    draw.rectangle([box_x, box_y, box_x + 2100, box_y + 120], fill=BOXES)
    draw.rectangle([box_x, box_y, box_x + 2100, box_y + 6], fill=GOLD)
    draw.text((box_x + 30, box_y + 40), "Name: _________________    |    Phone: _________________", fill=WHITE, font=font(24))
    centred(draw, box_y + 140, "Form Field Box — #2A2A2A Background", GREY, font(20))

    # Section Header pattern
    sh_y = 2700
    draw.rectangle([178, sh_y, 190, sh_y + 34], fill=GOLD)
    draw.text((200, sh_y), "SECTION HEADER", fill=GOLD, font=font(28, bold=True))
    gold_rule(draw, sh_y + 50, 2, 180, W - 180)
    label = "Section Header + Rule Pattern"
    draw.text((W - 180 - draw.textbbox((0, 0), label, font=font(18))[2], sh_y + 10), label, fill=GREY, font=font(18))

    # ════════════════════════════════════════════════════
    # SECTION 6 — HEADER/FOOTER TEMPLATE (y=2820 to y=3508)
    # ════════════════════════════════════════════════════
    section_title(draw, 2820, "HEADER & FOOTER TEMPLATE")

    # Header band
    draw.rectangle([0, 2900, W, 3100], fill=BG)
    gold_rule(draw, 2900, 4)

    # Scissors icon (small, centred)
    hcx = W // 2
    hcy = 2940
    draw.line([(hcx - 18, hcy - 18), (hcx + 18, hcy + 18)], fill=GOLD, width=4)
    draw.line([(hcx + 18, hcy - 18), (hcx - 18, hcy + 18)], fill=GOLD, width=4)
    for cx, cy in [(hcx - 18, hcy - 18), (hcx + 18, hcy - 18),
                    (hcx - 18, hcy + 18), (hcx + 18, hcy + 18)]:
        draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], outline=GOLD, width=2)

    centred(draw, 2975, "YOUR BARBERSHOP NAME", WHITE, font(48, bold=True))
    centred(draw, 3035, "MASTER BARBERS", GOLD, font(24))
    gold_rule(draw, 3080, 4)

    # Footer band
    draw.rectangle([0, 3130, W, 3300], fill=BG)
    gold_rule(draw, 3130, 4)
    centred(draw, 3165, "Thank you for your business", WHITE, font(26, italic=True))
    centred(draw, 3215, "yourshop.com  ·  +1 (555) 000-0000  ·  Your City, State", GOLD, font(20))
    gold_rule(draw, 3265, 4)

    # Label
    centred(draw, 3320, "Standard Header + Footer — used on ALL A4 templates", WHITE, font(20))

    # Bottom branding
    gold_rule(draw, 3400, 2)
    centred(draw, 3420, "PURPLEOCAZ  |  Barbershop Template Bundle  |  Design System v1.0", GREY, font(18))

    # Save
    path = OUTPUT_DIR / "design_system_reference.png"
    img.save(path, "PNG")
    print(f"Saved: {path.name} ({W}x{H}, {path.stat().st_size // 1024}KB)")
    return path


def upload_to_spaces(path):
    env = open("/root/NEW-AI-PROJECT/purpleocaz-canva-mcp/.env").read()
    key = re.search(r'DO_SPACES_KEY=(\S+)', env).group(1)
    secret = re.search(r'DO_SPACES_SECRET=(\S+)', env).group(1)
    s3 = boto3.client("s3", endpoint_url="https://lon1.digitaloceanspaces.com",
                      aws_access_key_id=key, aws_secret_access_key=secret)
    sk = f"barbershop/{path.name}"
    s3.put_object(Bucket="purpleocaz-assets", Key=sk,
                  Body=path.read_bytes(), ContentType="image/png", ACL="public-read")
    url = f"https://purpleocaz-assets.lon1.digitaloceanspaces.com/{sk}"
    print(f"Uploaded: {url}")
    return url


if __name__ == "__main__":
    path = main()
    url = upload_to_spaces(path)
