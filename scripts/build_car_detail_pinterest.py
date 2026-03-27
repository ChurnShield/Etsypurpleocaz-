#!/usr/bin/env python3
"""
Car Detailing Mega Bundle — Pinterest pins + video pin.

Builds:
  - 5 static pins  (1000×1500 PNG)
  - 1 video pin    (1000×1500 MP4, 10 seconds, Ken Burns + fade)
Uploads all 6 to DO Spaces under pinterest/
Reports all Spaces URLs.

Run from project root:
    python scripts/build_car_detail_pinterest.py
"""

import os
import sys
import subprocess
import math
import urllib.request

import boto3
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ── Paths ─────────────────────────────────────────────────────────────────────
PROJECT    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(PROJECT, "outputs", "pinterest")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Fonts ─────────────────────────────────────────────────────────────────────
F_BOLD    = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F_REG     = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
F_SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
F_SERIF   = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"

# ── Colour palette ────────────────────────────────────────────────────────────
BG      = (13, 13, 13)        # #0D0D0D
RED     = (204, 0, 0)         # #CC0000
RED_D   = (160, 0, 0)         # darker red for depth
WHITE   = (255, 255, 255)
SILVER  = (180, 180, 180)
PANEL   = (26, 26, 26)        # #1A1A1A
PANEL_L = (38, 38, 38)        # #262626

# ── Pin dimensions ────────────────────────────────────────────────────────────
W, H = 1000, 1500


def fnt(size, bold=True, serif=False):
    path = F_SERIF_B if (serif and bold) else (F_SERIF if serif else (F_BOLD if bold else F_REG))
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def cx(draw, text, y, font, fill, canvas_w=W):
    """Centre text horizontally."""
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((canvas_w - tw) // 2, y), text, fill=fill, font=font)


def bar(draw, y, h, fill):
    draw.rectangle([0, y, W, y + h], fill=fill)


def rule(draw, y, fill=RED, margin=60):
    draw.rectangle([margin, y, W - margin, y + 2], fill=fill)


def shadow_text(draw, xy, text, font, fill, shadow_fill=(0, 0, 0), offset=3):
    draw.text((xy[0] + offset, xy[1] + offset), text, fill=shadow_fill, font=font)
    draw.text(xy, text, fill=fill, font=font)


def rounded_rect(draw, x, y, w, h, r, fill, outline=None, outline_w=2):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=fill,
                            outline=outline, width=outline_w)


def pill(draw, cx_val, y, w, h, fill, text, text_fill, text_size):
    x = cx_val - w // 2
    rounded_rect(draw, x, y, w, h, h // 2, fill)
    f = fnt(text_size, bold=True)
    bbox = draw.textbbox((0, 0), text, font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((cx_val - tw // 2, y + (h - th) // 2 - 2), text, fill=text_fill, font=f)


def canva_tag(draw, y):
    """Bottom 'Editable in Canva • Instant Download' tag."""
    text = "Editable in Canva  •  Instant Download"
    f = fnt(22, bold=False)
    bbox = draw.textbbox((0, 0), text, font=f)
    tw = bbox[2] - bbox[0]
    # Dark pill background
    px, py, pw, ph = (W - tw) // 2 - 20, y - 8, tw + 40, 44
    rounded_rect(draw, px, py, pw, ph, 22, PANEL_L)
    draw.text(((W - tw) // 2, y), text, fill=SILVER, font=f)


def purpleocaz_badge(draw, y):
    f = fnt(18, bold=False)
    cx(draw, "PurpleOcaz  |  purpleocaz.etsy.com", y, f, (100, 100, 100))


# ═══════════════════════════════════════════════════════════════════════════════
# PIN 1 — Hero Overview
# Layout: Centered big number + category checklist
# ═══════════════════════════════════════════════════════════════════════════════
def pin_1():
    print("[1/5] Pin 1 — Hero Overview")
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Diagonal texture
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    for i in range(20):
        x = i * 100 - 300
        odraw.line([(x, 0), (x + H, H)], fill=(255, 255, 255, 4), width=1)
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Top red bar
    bar(draw, 0, 18, RED)

    # "CAR DETAILING" label
    cx(draw, "CAR DETAILING BUSINESS KIT", 38, fnt(22), RED)

    # Red underline
    rule(draw, 72, RED, 100)

    # Huge "53"
    f_huge = fnt(220, bold=True)
    bbox = draw.textbbox((0, 0), "53", font=f_huge)
    tw = bbox[2] - bbox[0]
    # Shadow
    draw.text(((W - tw) // 2 + 5, 85 + 5), "53", fill=RED_D, font=f_huge)
    draw.text(((W - tw) // 2, 85), "53", fill=RED, font=f_huge)

    # "PROFESSIONAL TEMPLATES"
    cx(draw, "PROFESSIONAL", 310, fnt(68, bold=True), WHITE)
    cx(draw, "TEMPLATES", 388, fnt(68, bold=True), WHITE)

    # Subtitle
    cx(draw, "for Your Detailing Business", 470, fnt(28, bold=False, serif=True), SILVER)

    # Red divider
    rule(draw, 518, RED, 60)
    rule(draw, 522, RED_D, 60)

    # Category checklist (2 columns)
    cats = [
        ("Client Forms", "8"),
        ("Social Media Posts", "20"),
        ("Branding Kit", "6"),
        ("Email Templates", "6"),
        ("Marketing Flyers", "4"),
        ("Job Forms", "3"),
        ("Appointment Cards", "2"),
        ("Visual Templates", "4"),
    ]
    col1 = cats[:4]
    col2 = cats[4:]
    f_item = fnt(26)
    f_count = fnt(22, bold=False)
    y_start = 545
    step = 68
    col1_x, col2_x = 70, 540
    for i, (name, count) in enumerate(col1):
        y = y_start + i * step
        # Red checkmark box
        draw.rectangle([col1_x, y + 4, col1_x + 24, y + 28], fill=RED)
        draw.text((col1_x + 6, y + 5), "✓", fill=WHITE, font=fnt(16))
        draw.text((col1_x + 36, y), name, fill=WHITE, font=f_item)
        # Count pill
        bbox = draw.textbbox((0, 0), name, font=f_item)
        nx = col1_x + 36 + bbox[2] - bbox[0] + 10
        rounded_rect(draw, nx, y + 4, 40, 24, 12, RED_D)
        bw = draw.textbbox((0, 0), count, font=f_count)[2]
        draw.text((nx + (40 - bw) // 2, y + 5), count, fill=WHITE, font=f_count)
    for i, (name, count) in enumerate(col2):
        y = y_start + i * step
        draw.rectangle([col2_x, y + 4, col2_x + 24, y + 28], fill=RED)
        draw.text((col2_x + 6, y + 5), "✓", fill=WHITE, font=fnt(16))
        draw.text((col2_x + 36, y), name, fill=WHITE, font=f_item)
        bbox = draw.textbbox((0, 0), name, font=f_item)
        nx = col2_x + 36 + bbox[2] - bbox[0] + 10
        rounded_rect(draw, nx, y + 4, 40, 24, 12, RED_D)
        bw = draw.textbbox((0, 0), count, font=f_count)[2]
        draw.text((nx + (40 - bw) // 2, y + 5), count, fill=WHITE, font=f_count)

    # "Worth over £60 — yours for £39.99"
    rule(draw, 1305, RED, 60)
    cx(draw, "Worth over £60 in templates", 1318, fnt(24, bold=False), SILVER)

    # Price pill
    pill(draw, W // 2, 1355, 260, 60, RED, "£39.99", WHITE, 34)

    # Canva tag
    canva_tag(draw, 1440)

    # Bottom red bar
    bar(draw, H - 18, 18, RED)
    purpleocaz_badge(draw, H - 16)

    path = os.path.join(OUTPUT_DIR, "car-detail-pin-1.png")
    img.save(path, "PNG")
    print(f"  Saved: {os.path.basename(path)}")
    return path


# ═══════════════════════════════════════════════════════════════════════════════
# PIN 2 — Business Cards Focus
# Layout: Visual card mockup (top 55%) + bold text (bottom 45%)
# ═══════════════════════════════════════════════════════════════════════════════
def pin_2():
    print("[2/5] Pin 2 — Business Cards")
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # ── Card mockup zone (top 55%, y 0-825) ──────────────────────────────────
    CARD_W, CARD_H = 480, 280

    def draw_card_dark(cx_pos, cy_pos, angle=0):
        """Draw a dark business card at position, optionally rotated."""
        card = Image.new("RGB", (CARD_W, CARD_H), PANEL)
        cd = ImageDraw.Draw(card)
        # Red bars
        cd.rectangle([0, 0, CARD_W, 6], fill=RED)
        cd.rectangle([0, CARD_H - 6, CARD_W, CARD_H], fill=RED)
        # Red vertical divider
        cd.rectangle([CARD_W // 2 - 2, 0, CARD_W // 2 + 2, CARD_H], fill=RED)
        # Text left panel
        cd.text((20, 30), "YOUR STUDIO", fill=WHITE, font=fnt(20, bold=True))
        cd.text((20, 58), "NAME", fill=WHITE, font=fnt(20, bold=True))
        cd.text((20, 88), "Car Detailing Specialist", fill=RED, font=fnt(12, bold=False))
        cd.rectangle([20, 112, 140, 114], fill=SILVER)
        cd.text((20, 122), "+1 (555) 000-0000", fill=SILVER, font=fnt(11, bold=False))
        cd.text((20, 140), "www.yourstudio.com", fill=SILVER, font=fnt(11, bold=False))
        # Right panel: QR placeholder
        cd.rectangle([CARD_W // 2 + 20, 40, CARD_W - 20, CARD_H - 40], outline=RED, width=1)
        cd.text((CARD_W // 2 + 50, 90), "SCAN", fill=SILVER, font=fnt(12))
        cd.text((CARD_W // 2 + 38, 108), "TO BOOK", fill=SILVER, font=fnt(12))
        if angle != 0:
            card = card.rotate(angle, expand=True)
        # Paste onto main image
        pw, ph = card.size
        x = cx_pos - pw // 2
        y = cy_pos - ph // 2
        img.paste(card, (x, y))

    # Draw 3 overlapping cards
    draw_card_dark(320, 310, angle=8)    # back-left, slight tilt
    draw_card_dark(680, 270, angle=-6)   # back-right, opposite tilt
    draw_card_dark(500, 480, angle=0)    # front-center, straight

    # Red stripe separator
    bar(draw, 740, 6, RED)
    bar(draw, 746, 6, RED_D)

    # ── Text zone (bottom 45%, y 752+) ──────────────────────────────────────
    # Dark panel
    draw.rectangle([0, 752, W, H], fill=PANEL)

    f_big = fnt(62, bold=True)
    cx(draw, "Business Cards", 780, f_big, WHITE)
    cx(draw, "THAT MAKE YOU", 852, fnt(44, bold=True), RED)
    cx(draw, "LOOK PRO", 904, fnt(44, bold=True), RED)

    rule(draw, 965, SILVER, 80)

    # 6-piece kit list
    items = ["Business Card (front + back)", "Letterhead", "Email Signature",
             "Invoice Template", "Thank You Card"]
    f_item = fnt(24, bold=False)
    y = 982
    for item in items:
        bbox = draw.textbbox((0, 0), item, font=f_item)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2 - 20
        draw.text((x, y), "—", fill=RED, font=f_item)
        draw.text((x + 28, y), item, fill=SILVER, font=f_item)
        y += 42

    # Part of bundle
    cx(draw, "Part of the 53-template Mega Bundle", 1240, fnt(22, bold=False), SILVER)

    # Price pill
    pill(draw, W // 2, 1282, 240, 56, RED, "£39.99", WHITE, 32)

    # Canva tag
    canva_tag(draw, 1440)

    # Bottom bar
    bar(draw, H - 18, 18, RED)
    purpleocaz_badge(draw, H - 16)

    path = os.path.join(OUTPUT_DIR, "car-detail-pin-2.png")
    img.save(path, "PNG")
    print(f"  Saved: {os.path.basename(path)}")
    return path


# ═══════════════════════════════════════════════════════════════════════════════
# PIN 3 — Client Forms
# Layout: Stacked form pages visual (left) + headline text overlay (right/bottom)
# ═══════════════════════════════════════════════════════════════════════════════
def pin_3():
    print("[3/5] Pin 3 — Client Forms")
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Top red bar
    bar(draw, 0, 18, RED)

    # ── Stacked form pages (centered, top area) ───────────────────────────────
    FORM_W, FORM_H = 420, 560
    form_titles = [
        "VEHICLE INTAKE FORM",
        "SERVICE AGREEMENT",
        "INVOICE TEMPLATE",
        "CONSENT WAIVER",
    ]
    angles  = [-8, -3, 3, 8]
    offsets = [(-120, 180), (-50, 140), (50, 140), (120, 180)]

    for i in range(3, -1, -1):
        form = Image.new("RGB", (FORM_W, FORM_H), WHITE)
        fd = ImageDraw.Draw(form)
        # Red header
        fd.rectangle([0, 0, FORM_W, 50], fill=RED)
        fd.text((20, 14), form_titles[i], fill=WHITE, font=fnt(16, bold=True))
        # Studio name small
        fd.text((FORM_W - 130, 34), "YOUR STUDIO", fill=(255, 200, 200), font=fnt(10))
        # Horizontal lines (form fields)
        for j in range(12):
            y_ln = 70 + j * 36
            fd.rectangle([20, y_ln, FORM_W - 20, y_ln + 1], fill=(200, 200, 200))
            # Label
            labels = ["Client Name:", "Vehicle:", "Date:", "Service:", "Notes:",
                      "Signature:", "Phone:", "Email:", "Mileage:", "Condition:", "Ref #:", "Total:"]
            fd.text((20, y_ln - 16), labels[j], fill=(80, 80, 80), font=fnt(11, bold=False))
        rotated = form.rotate(angles[i], expand=True, fillcolor=(20, 20, 20))
        ox, oy = offsets[i]
        x = W // 2 + ox - rotated.width // 2
        y = 330 + oy - rotated.height // 2
        img.paste(rotated, (x, y))

    # "8 FORMS" badge top right
    rounded_rect(draw, W - 165, 30, 140, 60, 12, RED)
    cx_badge = W - 165 + 70
    draw.text((cx_badge - 26, 42), "8", fill=WHITE, font=fnt(32, bold=True))
    draw.text((cx_badge - 36, 72), "FORMS", fill=WHITE, font=fnt(16))

    # ── Bold headline overlay (below the forms) ───────────────────────────────
    bar(draw, 940, 4, RED)
    bar(draw, 944, 4, RED_D)

    dark_panel_y = 948
    draw.rectangle([0, dark_panel_y, W, H], fill=PANEL)

    cx(draw, "Client Forms &", 970, fnt(58, bold=True), WHITE)
    cx(draw, "Invoices", 1038, fnt(58, bold=True), WHITE)
    cx(draw, "DONE FOR YOU", 1106, fnt(50, bold=True), RED)

    rule(draw, 1170, SILVER, 80)

    forms_short = [
        "Vehicle Intake Form  ·  Service Agreement",
        "Invoice Template  ·  Consent Waiver",
        "Feedback Form  ·  Appointment Booking",
        "Aftercare Instructions  ·  Package Menu",
    ]
    y = 1188
    for line in forms_short:
        cx(draw, line, y, fnt(22, bold=False), SILVER)
        y += 36

    pill(draw, W // 2, 1345, 300, 56, RED, "Mega Bundle  —  £39.99", WHITE, 28)
    canva_tag(draw, 1440)
    bar(draw, H - 18, 18, RED)
    purpleocaz_badge(draw, H - 16)

    path = os.path.join(OUTPUT_DIR, "car-detail-pin-3.png")
    img.save(path, "PNG")
    print(f"  Saved: {os.path.basename(path)}")
    return path


# ═══════════════════════════════════════════════════════════════════════════════
# PIN 4 — Marketing Materials
# Layout: 3 preview cards in a row + headline above + detail below
# ═══════════════════════════════════════════════════════════════════════════════
def pin_4():
    print("[4/5] Pin 4 — Marketing Materials")
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Top bar
    bar(draw, 0, 18, RED)

    # ── Headline ──────────────────────────────────────────────────────────────
    cx(draw, "PRICE LISTS,", 42, fnt(70, bold=True), WHITE)
    cx(draw, "FLYERS &", 118, fnt(70, bold=True), WHITE)
    cx(draw, "GIFT CARDS", 194, fnt(70, bold=True), RED)

    rule(draw, 278, RED, 60)
    cx(draw, "Marketing templates for your detailing business", 294, fnt(24, bold=False), SILVER)

    # ── 3 Preview cards ───────────────────────────────────────────────────────
    CARD_W, CARD_H = 280, 380
    card_configs = [
        # (title, subtitle, bg_color, accent)
        ("PROMO\nFLYER", "A5 / A4\nPrint Ready", PANEL, RED),
        ("PRICE\nLIST", "A4 Portrait\nEditable", (20, 20, 40), (80, 80, 200)),
        ("GIFT\nCERT", "A5 Landscape\nPrintable", (20, 30, 20), (40, 160, 80)),
    ]
    start_x = 30
    gap = 30
    total_w = 3 * CARD_W + 2 * gap
    start_x = (W - total_w) // 2
    card_y = 340

    for i, (title, subtitle, bg_col, acc_col) in enumerate(card_configs):
        cx_pos = start_x + i * (CARD_W + gap)
        card = Image.new("RGB", (CARD_W, CARD_H), bg_col)
        cd = ImageDraw.Draw(card)

        # Header band
        cd.rectangle([0, 0, CARD_W, 8], fill=acc_col)
        cd.rectangle([0, CARD_H - 8, CARD_W, CARD_H], fill=acc_col)

        # Title (centred, with line break)
        lines = title.split("\n")
        f_title = fnt(44, bold=True)
        total_h = sum(cd.textbbox((0, 0), ln, font=f_title)[3] - cd.textbbox((0, 0), ln, font=f_title)[1] + 6
                      for ln in lines)
        ty = (CARD_H - total_h) // 2 - 20
        for ln in lines:
            bbox = cd.textbbox((0, 0), ln, font=f_title)
            lw = bbox[2] - bbox[0]
            cd.text(((CARD_W - lw) // 2, ty), ln, fill=WHITE, font=f_title)
            ty += bbox[3] - bbox[1] + 6

        # Subtitle at bottom
        for j, sln in enumerate(subtitle.split("\n")):
            f_sub = fnt(18, bold=False)
            bbox = cd.textbbox((0, 0), sln, font=f_sub)
            lw = bbox[2] - bbox[0]
            cd.text(((CARD_W - lw) // 2, CARD_H - 52 + j * 20), sln, fill=acc_col, font=f_sub)

        # Decorative diagonal lines
        for k in range(8):
            xd = k * 50 - 100
            cd.line([(xd, 0), (xd + CARD_H, CARD_H)], fill=(255, 255, 255, 10), width=1)

        # Red border
        cd.rectangle([0, 0, CARD_W - 1, CARD_H - 1], outline=acc_col, width=2)

        img.paste(card, (cx_pos, card_y))

    # ── What's included list ──────────────────────────────────────────────────
    rule(draw, 755, RED, 60)

    items_2col = [
        ("Promo Flyer", "Walk-In Flyer"),
        ("Seasonal Flyer", "Mobile Service Flyer"),
        ("Gift Certificate", "Price List"),
        ("Loyalty Stamp Card", "Welcome Sign"),
    ]
    f_item = fnt(26)
    y = 775
    for left, right in items_2col:
        # left col
        draw.rectangle([80, y + 8, 100, y + 28], fill=RED)
        draw.text((110, y), left, fill=WHITE, font=f_item)
        # right col
        draw.rectangle([530, y + 8, 550, y + 28], fill=RED)
        draw.text((560, y), right, fill=WHITE, font=f_item)
        y += 58

    # ── Value statement ───────────────────────────────────────────────────────
    rule(draw, 1215, RED, 60)
    cx(draw, "All 53 templates — one low price", 1232, fnt(28, bold=False, serif=True), SILVER)
    pill(draw, W // 2, 1275, 260, 60, RED, "£39.99 Bundle", WHITE, 32)

    canva_tag(draw, 1440)
    bar(draw, H - 18, 18, RED)
    purpleocaz_badge(draw, H - 16)

    path = os.path.join(OUTPUT_DIR, "car-detail-pin-4.png")
    img.save(path, "PNG")
    print(f"  Saved: {os.path.basename(path)}")
    return path


# ═══════════════════════════════════════════════════════════════════════════════
# PIN 5 — Full Bundle Value CTA
# Layout: Strong value prop, all categories, clear price CTA
# ═══════════════════════════════════════════════════════════════════════════════
def pin_5():
    print("[5/5] Pin 5 — Full Bundle CTA")
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Large gradient-style background bands (faked with rects)
    for i in range(40):
        alpha = int(20 - i * 0.3)
        if alpha > 0:
            draw.rectangle([0, i * 40, W, i * 40 + 40],
                           fill=(alpha, 0, 0))

    # Top bar
    bar(draw, 0, 18, RED)

    # Small label
    cx(draw, "COMPLETE CAR DETAILING KIT", 32, fnt(20), RED)

    # Main headline — 3 lines, bold
    cx(draw, "EVERYTHING", 72, fnt(96, bold=True), WHITE)
    cx(draw, "YOU NEED", 174, fnt(96, bold=True), WHITE)
    cx(draw, "TO LAUNCH YOUR", 276, fnt(52, bold=True), RED)
    cx(draw, "DETAILING BRAND", 334, fnt(52, bold=True), RED)

    # Red rule
    rule(draw, 400, RED, 40)

    # Big price badge
    badge_y = 420
    rounded_rect(draw, (W - 340) // 2, badge_y, 340, 130, 20, RED)
    cx(draw, "£39.99", badge_y + 22, fnt(76, bold=True), WHITE)
    cx(draw, "Worth over £60 individually", badge_y + 104, fnt(20, bold=False), (255, 200, 200))

    # Rule
    rule(draw, 570, SILVER, 60)

    # 2-column category grid
    cats = [
        ("Client Forms",       "8"),
        ("Social Media",       "20"),
        ("Branding Kit",       "6"),
        ("Email Templates",    "6"),
        ("Flyers",             "4"),
        ("Job Forms",          "3"),
        ("Appointment Cards",  "2"),
        ("Visual Templates",   "4"),
    ]
    col1, col2 = cats[:4], cats[4:]
    f_cat  = fnt(28, bold=True)
    f_num  = fnt(22, bold=False)
    y_grid = 590
    row_h  = 80
    lx, rx = 60, 510

    for i, (name, count) in enumerate(col1):
        y = y_grid + i * row_h
        rounded_rect(draw, lx, y + 6, 440, 58, 10, PANEL_L)
        draw.rectangle([lx, y + 6, lx + 6, y + 64], fill=RED)
        draw.text((lx + 20, y + 14), name, fill=WHITE, font=f_cat)
        # Count
        rounded_rect(draw, lx + 360, y + 14, 60, 36, 10, RED)
        bw = draw.textbbox((0, 0), count, font=f_num)[2]
        draw.text((lx + 360 + (60 - bw) // 2, y + 18), count, fill=WHITE, font=f_num)

    for i, (name, count) in enumerate(col2):
        y = y_grid + i * row_h
        rounded_rect(draw, rx, y + 6, 440, 58, 10, PANEL_L)
        draw.rectangle([rx, y + 6, rx + 6, y + 64], fill=RED)
        draw.text((rx + 20, y + 14), name, fill=WHITE, font=f_cat)
        rounded_rect(draw, rx + 360, y + 14, 60, 36, 10, RED)
        bw = draw.textbbox((0, 0), count, font=f_num)[2]
        draw.text((rx + 360 + (60 - bw) // 2, y + 18), count, fill=WHITE, font=f_num)

    # Total count
    rule(draw, 1300, RED, 60)
    cx(draw, "53 TEMPLATES  —  INSTANT DOWNLOAD", 1320, fnt(30, bold=True), WHITE)

    # Large CTA pill
    pill(draw, W // 2, 1362, 480, 64, RED, "BUY NOW — purpleocaz.etsy.com", WHITE, 24)

    canva_tag(draw, 1440)
    bar(draw, H - 18, 18, RED)

    path = os.path.join(OUTPUT_DIR, "car-detail-pin-5.png")
    img.save(path, "PNG")
    print(f"  Saved: {os.path.basename(path)}")
    return path


# ═══════════════════════════════════════════════════════════════════════════════
# VIDEO PIN — Ken Burns + fade, 10 seconds
# ═══════════════════════════════════════════════════════════════════════════════
def build_video_pin(pin_paths):
    print("\n[6/6] Video Pin — Ken Burns + fade (10s)")
    out_path = os.path.join(OUTPUT_DIR, "car-detail-video-pin.mp4")

    # 2.5s per image, 0.5s fade transitions
    # Total = 5*2.5 - 4*0.5 = 10.5s → trim to 10s
    # xfade offsets: 2.0, 4.0, 6.0, 8.0
    # zoompan: zoom from 1.0 to ~1.15 over 75 frames (2.5s @ 30fps)

    inputs = []
    for p in pin_paths:
        inputs += ["-loop", "1", "-t", "2.6", "-i", p]

    zoom_filter = (
        "zoompan=z='min(zoom+0.001,1.15)':d=78:"
        "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1000x1500,"
        "fps=30,setpts=PTS-STARTPTS"
    )

    filter_parts = []
    for i in range(5):
        filter_parts.append(f"[{i}:v]{zoom_filter}[v{i}]")

    filter_parts.append("[v0][v1]xfade=transition=fade:duration=0.5:offset=2.0[xf1]")
    filter_parts.append("[xf1][v2]xfade=transition=fade:duration=0.5:offset=4.0[xf2]")
    filter_parts.append("[xf2][v3]xfade=transition=fade:duration=0.5:offset=6.0[xf3]")
    filter_parts.append("[xf3][v4]xfade=transition=fade:duration=0.5:offset=8.0[out]")

    filter_complex = ";".join(filter_parts)

    cmd = (inputs +
           ["-filter_complex", filter_complex,
            "-map", "[out]",
            "-t", "10",
            "-pix_fmt", "yuv420p",
            "-c:v", "libx264",
            "-crf", "23",
            "-preset", "fast",
            "-y", out_path])

    full_cmd = ["ffmpeg"] + cmd
    print(f"  Running FFmpeg ({len(full_cmd)} args)...")
    result = subprocess.run(full_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  FFmpeg stderr:\n{result.stderr[-2000:]}")
        raise RuntimeError(f"FFmpeg failed with code {result.returncode}")

    size_mb = os.path.getsize(out_path) / (1024 * 1024)
    print(f"  Saved: {os.path.basename(out_path)} ({size_mb:.1f} MB)")
    return out_path


# ═══════════════════════════════════════════════════════════════════════════════
# SPACES UPLOAD
# ═══════════════════════════════════════════════════════════════════════════════
def load_spaces_env():
    env_path = os.path.join(PROJECT, "purpleocaz-canva-mcp", ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())


def get_s3():
    return boto3.client(
        "s3",
        endpoint_url=os.environ["DO_SPACES_ENDPOINT"],
        aws_access_key_id=os.environ["DO_SPACES_KEY"],
        aws_secret_access_key=os.environ["DO_SPACES_SECRET"],
        region_name=os.environ["DO_SPACES_REGION"],
    )


def upload(s3, local_path, spaces_key):
    bucket = os.environ.get("DO_SPACES_BUCKET", "purpleocaz-assets")
    ext = os.path.splitext(local_path)[1].lower()
    content_type = {"png": "image/png", "mp4": "video/mp4"}.get(ext.lstrip("."), "application/octet-stream")
    s3.upload_file(
        local_path, bucket, spaces_key,
        ExtraArgs={"ACL": "public-read", "ContentType": content_type},
    )
    cdn = os.environ.get("DO_SPACES_CDN_BASE",
                         "https://purpleocaz-assets.lon1.digitaloceanspaces.com")
    url = f"{cdn}/{spaces_key}"
    print(f"  ↑ {os.path.basename(local_path)} → {url}")
    return url


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    print("=" * 60)
    print("CAR DETAILING — PINTEREST PINS BUILD")
    print("=" * 60)

    # Build static pins
    print("\n=== Step 1: Build Static Pins ===")
    p1 = pin_1()
    p2 = pin_2()
    p3 = pin_3()
    p4 = pin_4()
    p5 = pin_5()
    pin_paths = [p1, p2, p3, p4, p5]

    # Build video
    print("\n=== Step 2: Build Video Pin ===")
    v1 = build_video_pin(pin_paths)

    # Upload to Spaces
    print("\n=== Step 3: Upload to DO Spaces ===")
    load_spaces_env()
    s3 = get_s3()

    all_urls = {}
    for i, path in enumerate(pin_paths, 1):
        key = f"pinterest/car-detail-pin-{i}.png"
        all_urls[f"pin_{i}"] = upload(s3, path, key)

    all_urls["video"] = upload(s3, v1, "pinterest/car-detail-video-pin.mp4")

    # Verify all uploads
    print("\n=== Step 4: Verify Spaces uploads ===")
    for name, url in all_urls.items():
        req = urllib.request.Request(url, method="HEAD")
        resp = urllib.request.urlopen(req)
        print(f"  {name}: HTTP {resp.status} OK")

    print("\n" + "=" * 60)
    print("ALL 6 SPACES URLs:")
    print("=" * 60)
    for name, url in all_urls.items():
        print(f"  {name:8s}  {url}")
    print("=" * 60)


if __name__ == "__main__":
    main()
