#!/usr/bin/env python3
"""
Restaurant Cafe Coffee Shop — Pinterest pins + video pin.

Builds:
  - 5 static pins  (1000×1500 PNG)
  - 1 video pin    (1000×1500 MP4, 10 seconds, Ken Burns + fade)
Uploads all 6 to DO Spaces under pinterest/
Reports all Spaces URLs.

Run from project root:
    python scripts/build_restaurant_cafe_pinterest.py
"""

import os
import sys
import subprocess
import urllib.request

import boto3
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ── Paths ─────────────────────────────────────────────────────────────────────
PROJECT    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(PROJECT, "outputs", "pinterest-restaurant")
TMPL_DIR   = os.path.join(PROJECT, "outputs", "restaurant-cafe-coffee-shop", "templates")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Fonts ─────────────────────────────────────────────────────────────────────
F_BOLD    = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F_REG     = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
F_SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
F_SERIF   = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"

# ── Colour palette — warm cafe / bistro aesthetic ────────────────────────────
ESPRESSO   = (74,  42,  22)    # #4A2A16 — deep espresso brown (primary)
BRASS      = (193, 154,  89)   # #C19A59 — warm brass/gold
CREAM      = (245, 238, 225)   # #F5EEE1 — warm linen
CHARCOAL   = (28,  24,  20)    # #1C1814 — warm near-black
DARK_PANEL = (42,  28,  14)    # #2A1C0E — dark brown panel
LIGHT_PANEL= (255, 249, 240)   # #FFF9F0 — warm off-white panel
RUST       = (180,  90,  40)   # #B45A28 — terracotta rust
WHITE      = (255, 255, 255)
SILVER     = (200, 190, 175)   # warm silver/grey

# ── Pin dimensions ────────────────────────────────────────────────────────────
W, H = 1000, 1500


def fnt(size, bold=True, serif=False, italic=False):
    if serif and italic:
        path = F_SERIF
    elif serif:
        path = F_SERIF_B
    elif bold:
        path = F_BOLD
    else:
        path = F_REG
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


def rule(draw, y, fill=BRASS, margin=60, thickness=2):
    draw.rectangle([margin, y, W - margin, y + thickness], fill=fill)


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
    text = "Editable in Canva  •  Instant Download"
    f = fnt(22, bold=False)
    bbox = draw.textbbox((0, 0), text, font=f)
    tw = bbox[2] - bbox[0]
    px, py, pw, ph = (W - tw) // 2 - 20, y - 8, tw + 40, 44
    rounded_rect(draw, px, py, pw, ph, 22, DARK_PANEL)
    draw.text(((W - tw) // 2, y), text, fill=SILVER, font=f)


def purpleocaz_badge(draw, y):
    f = fnt(18, bold=False)
    cx(draw, "PurpleOcaz  |  purpleocaz.etsy.com", y, f, BRASS)


def warm_bg(img):
    """Add a subtle warm diagonal texture to a dark image."""
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    for i in range(25):
        x = i * 80 - 200
        odraw.line([(x, 0), (x + H, H)], fill=(193, 154, 89, 5), width=1)
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def load_template(filename, max_w, max_h):
    """Load a template PNG, resize to fit bounds."""
    path = os.path.join(TMPL_DIR, filename)
    if not os.path.exists(path):
        return None
    img = Image.open(path).convert("RGB")
    img.thumbnail((max_w, max_h), Image.LANCZOS)
    return img


def paste_centered(base, overlay, cy_center, shadow=True):
    """Paste overlay centred horizontally at a given y-centre with optional drop shadow."""
    if overlay is None:
        return
    ow, oh = overlay.size
    ox = (W - ow) // 2
    oy = cy_center - oh // 2
    if shadow:
        shadow_img = Image.new("RGBA", (ow + 20, oh + 20), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_img)
        shadow_draw.rectangle([10, 10, ow + 10, oh + 10], fill=(0, 0, 0, 80))
        shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(12))
        base.paste(shadow_img.convert("RGB"), (ox - 10, oy - 5),
                   shadow_img.split()[3])
    base.paste(overlay, (ox, oy))


# ═══════════════════════════════════════════════════════════════════════════════
# PIN 1 — Hero Overview (warm dark background, category checklist)
# ═══════════════════════════════════════════════════════════════════════════════
def pin_1():
    print("[1/5] Pin 1 — Hero Overview")
    img = Image.new("RGB", (W, H), ESPRESSO)
    img = warm_bg(img)
    draw = ImageDraw.Draw(img)

    # Brass accent top bar
    bar(draw, 0, 14, BRASS)

    # Niche label
    cx(draw, "CAFE & RESTAURANT BUSINESS KIT", 26, fnt(20), BRASS)
    rule(draw, 60, BRASS, 80)

    # Big "32"
    f_huge = fnt(210, bold=True)
    bbox = draw.textbbox((0, 0), "32", font=f_huge)
    tw = bbox[2] - bbox[0]
    # Warm shadow
    draw.text(((W - tw) // 2 + 6, 76 + 6), "32", fill=DARK_PANEL, font=f_huge)
    draw.text(((W - tw) // 2, 76), "32", fill=BRASS, font=f_huge)

    cx(draw, "PROFESSIONAL", 305, fnt(66, bold=True), WHITE)
    cx(draw, "CANVA TEMPLATES", 378, fnt(66, bold=True), WHITE)
    cx(draw, "for Your Cafe or Restaurant", 456, fnt(28, bold=False, serif=True, italic=True), SILVER)

    rule(draw, 502, BRASS, 50)

    # Category checklist 2-column
    cats = [
        ("Branding Cards",    "6"),
        ("Social Media",      "5"),
        ("Menus & Price List","2"),
        ("Gift Certificate",  "1"),
        ("Client Forms",      "8"),
        ("Operations",        "5"),
        ("Flyers",            "2"),
        ("Staff Schedules",   "4"),
    ]
    col1 = cats[:4]
    col2 = cats[4:]
    f_item  = fnt(25)
    f_count = fnt(21, bold=False)
    y_start = 525
    step    = 66
    lx, rx  = 65, 535

    for i, (name, count) in enumerate(col1):
        y = y_start + i * step
        rounded_rect(draw, lx, y + 4, 26, 26, 4, BRASS)
        draw.text((lx + 6, y + 4), "✓", fill=ESPRESSO, font=fnt(15))
        draw.text((lx + 38, y), name, fill=WHITE, font=f_item)
        # count pill
        bw = draw.textbbox((0, 0), name, font=f_item)[2]
        nx = lx + 38 + bw + 10
        rounded_rect(draw, nx, y + 4, 38, 24, 10, RUST)
        cw = draw.textbbox((0, 0), count, font=f_count)[2]
        draw.text((nx + (38 - cw) // 2, y + 5), count, fill=WHITE, font=f_count)

    for i, (name, count) in enumerate(col2):
        y = y_start + i * step
        rounded_rect(draw, rx, y + 4, 26, 26, 4, BRASS)
        draw.text((rx + 6, y + 4), "✓", fill=ESPRESSO, font=fnt(15))
        draw.text((rx + 38, y), name, fill=WHITE, font=f_item)
        bw = draw.textbbox((0, 0), name, font=f_item)[2]
        nx = rx + 38 + bw + 10
        rounded_rect(draw, nx, y + 4, 38, 24, 10, RUST)
        cw = draw.textbbox((0, 0), count, font=f_count)[2]
        draw.text((nx + (38 - cw) // 2, y + 5), count, fill=WHITE, font=f_count)

    rule(draw, 1305, BRASS, 60)
    cx(draw, "Worth over £70 in templates", 1320, fnt(24, bold=False), SILVER)
    pill(draw, W // 2, 1356, 260, 62, BRASS, "£39.99", ESPRESSO, 36)

    canva_tag(draw, 1440)
    bar(draw, H - 18, 18, BRASS)
    purpleocaz_badge(draw, H - 16)

    path = os.path.join(OUTPUT_DIR, "restaurant-pin-1.png")
    img.save(path, "PNG")
    print(f"  Saved: {os.path.basename(path)}")
    return path


# ═══════════════════════════════════════════════════════════════════════════════
# PIN 2 — Menu & Branding Showcase (warm light background, actual template mockups)
# ═══════════════════════════════════════════════════════════════════════════════
def pin_2():
    print("[2/5] Pin 2 — Menu & Branding")
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)

    # Espresso top bar
    bar(draw, 0, 16, ESPRESSO)
    cx(draw, "MENUS • CARDS • BRANDING", 28, fnt(20), ESPRESSO)
    rule(draw, 64, ESPRESSO, 80)

    cx(draw, "Look Professional", 82, fnt(56, bold=True), ESPRESSO)
    cx(draw, "From Day One", 146, fnt(56, bold=True), ESPRESSO)
    cx(draw, "Fully editable in Canva — no design skills needed", 220,
       fnt(24, bold=False, serif=True, italic=True), RUST)
    rule(draw, 260, ESPRESSO, 80)

    # Template card row 1: Business card dark + light side by side
    CARD_W, CARD_H = 420, 250
    y_row = 285

    def draw_biz_dark(x, y):
        c = Image.new("RGB", (CARD_W, CARD_H), ESPRESSO)
        cd = ImageDraw.Draw(c)
        cd.rectangle([0, 0, CARD_W, 8], fill=BRASS)
        cd.rectangle([0, CARD_H - 8, CARD_W, CARD_H], fill=BRASS)
        cd.text((22, 26), "YOUR CAFE", fill=WHITE, font=fnt(22, bold=True))
        cd.text((22, 56), "Head Barista / Owner", fill=BRASS, font=fnt(13, bold=False))
        cd.rectangle([22, 80, 180, 82], fill=BRASS)
        cd.text((22, 90), "+44 7000 000 000", fill=SILVER, font=fnt(12, bold=False))
        cd.text((22, 108), "hello@yourcafe.com", fill=SILVER, font=fnt(12, bold=False))
        cd.text((22, 126), "www.yourcafe.com", fill=SILVER, font=fnt(12, bold=False))
        # Right: coffee cup icon placeholder
        cd.rounded_rectangle([CARD_W - 100, 30, CARD_W - 20, 130], radius=8, outline=BRASS, width=2)
        cd.text((CARD_W - 82, 68), "☕", fill=BRASS, font=fnt(28, bold=False))
        # Shadow + paste
        shadow = Image.new("RGBA", (CARD_W + 16, CARD_H + 16), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        sd.rectangle([8, 8, CARD_W + 8, CARD_H + 8], fill=(0, 0, 0, 70))
        shadow = shadow.filter(ImageFilter.GaussianBlur(10))
        img.paste(shadow.convert("RGB"), (x - 8, y - 8), shadow.split()[3])
        img.paste(c, (x, y))

    def draw_biz_light(x, y):
        c = Image.new("RGB", (CARD_W, CARD_H), LIGHT_PANEL)
        cd = ImageDraw.Draw(c)
        cd.rectangle([0, 0, CARD_W, 8], fill=ESPRESSO)
        cd.rectangle([0, CARD_H - 8, CARD_W, CARD_H], fill=ESPRESSO)
        cd.text((22, 26), "YOUR CAFE", fill=ESPRESSO, font=fnt(22, bold=True))
        cd.text((22, 56), "Head Barista / Owner", fill=RUST, font=fnt(13, bold=False))
        cd.rectangle([22, 80, 180, 82], fill=ESPRESSO)
        cd.text((22, 90), "+44 7000 000 000", fill=CHARCOAL, font=fnt(12, bold=False))
        cd.text((22, 108), "hello@yourcafe.com", fill=CHARCOAL, font=fnt(12, bold=False))
        cd.text((22, 126), "www.yourcafe.com", fill=CHARCOAL, font=fnt(12, bold=False))
        cd.rounded_rectangle([CARD_W - 100, 30, CARD_W - 20, 130], radius=8, outline=ESPRESSO, width=2)
        cd.text((CARD_W - 82, 68), "☕", fill=ESPRESSO, font=fnt(28, bold=False))
        shadow = Image.new("RGBA", (CARD_W + 16, CARD_H + 16), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        sd.rectangle([8, 8, CARD_W + 8, CARD_H + 8], fill=(0, 0, 0, 50))
        shadow = shadow.filter(ImageFilter.GaussianBlur(10))
        img.paste(shadow.convert("RGB"), (x - 8, y - 8), shadow.split()[3])
        img.paste(c, (x, y))

    draw_biz_dark(40, y_row)
    draw_biz_light(540, y_row + 30)

    rule(draw, 570, ESPRESSO, 60)

    # Menu card
    def draw_menu(x, y):
        mw, mh = 900, 380
        c = Image.new("RGB", (mw, mh), LIGHT_PANEL)
        cd = ImageDraw.Draw(c)
        cd.rectangle([0, 0, mw, 10], fill=ESPRESSO)
        cd.rectangle([0, mh - 10, mw, mh], fill=ESPRESSO)
        cd.rectangle([28, 28, mw - 28, 32], fill=BRASS)
        cx2 = mw // 2
        bbox = cd.textbbox((0, 0), "OUR MENU", font=fnt(36, bold=True))
        tw = bbox[2] - bbox[0]
        cd.text((cx2 - tw // 2, 46), "OUR MENU", fill=ESPRESSO, font=fnt(36, bold=True))
        cd.rectangle([28, 96, mw - 28, 98], fill=BRASS)
        items = [("Espresso", "£2.50"), ("Flat White", "£3.20"), ("Croissant", "£2.80"),
                 ("Avocado Toast", "£7.50"), ("Eggs Benedict", "£9.00")]
        f_item = fnt(20, bold=False)
        f_price = fnt(20, bold=True)
        for i, (name, price) in enumerate(items):
            yi = 110 + i * 46
            cd.text((36, yi), name, fill=CHARCOAL, font=f_item)
            pb = cd.textbbox((0, 0), price, font=f_price)
            cd.text((mw - 36 - (pb[2] - pb[0]), yi), price, fill=RUST, font=f_price)
            if i < len(items) - 1:
                cd.line([(36, yi + 38), (mw - 36, yi + 38)], fill=(220, 210, 195), width=1)
        cd.text((mw // 2 - 80, mh - 40), "www.yourcafe.com", fill=CHARCOAL, font=fnt(16, bold=False))
        shadow = Image.new("RGBA", (mw + 16, mh + 16), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        sd.rectangle([8, 8, mw + 8, mh + 8], fill=(0, 0, 0, 60))
        shadow = shadow.filter(ImageFilter.GaussianBlur(12))
        img.paste(shadow.convert("RGB"), (x - 8, y - 8), shadow.split()[3])
        img.paste(c, (x, y))

    draw_menu(50, 596)

    rule(draw, 1006, ESPRESSO, 60)
    cx(draw, "Every template included in the bundle", 1020, fnt(26, bold=False), CHARCOAL)
    cx(draw, "is fully editable in Canva Free", 1056, fnt(26, bold=False), CHARCOAL)

    rule(draw, 1100, BRASS, 60)
    cx(draw, "BRANDING THAT FILLS TABLES", 1120, fnt(42, bold=True), ESPRESSO)
    cx(draw, "Edit. Print. Open for business.", 1176, fnt(26, bold=False, serif=True, italic=True), RUST)

    pill(draw, W // 2, 1230, 420, 62, ESPRESSO, "Get the bundle — £39.99", WHITE, 26)

    canva_tag(draw, 1360)
    rule(draw, 1420, ESPRESSO, 60)
    bar(draw, H - 18, 18, ESPRESSO)
    purpleocaz_badge(draw, H - 16)

    path = os.path.join(OUTPUT_DIR, "restaurant-pin-2.png")
    img.save(path, "PNG")
    print(f"  Saved: {os.path.basename(path)}")
    return path


# ═══════════════════════════════════════════════════════════════════════════════
# PIN 3 — Social Media Kit Showcase
# ═══════════════════════════════════════════════════════════════════════════════
def pin_3():
    print("[3/5] Pin 3 — Social Media Kit")
    img = Image.new("RGB", (W, H), ESPRESSO)
    img = warm_bg(img)
    draw = ImageDraw.Draw(img)

    bar(draw, 0, 14, BRASS)
    cx(draw, "SOCIAL MEDIA TEMPLATES", 26, fnt(20), BRASS)
    rule(draw, 60, BRASS, 80)

    cx(draw, "STOP THE", 80, fnt(90, bold=True), WHITE)
    cx(draw, "SCROLL", 174, fnt(90, bold=True), BRASS)
    cx(draw, "5 done-for-you Instagram post templates", 278,
       fnt(26, bold=False, serif=True, italic=True), SILVER)

    rule(draw, 322, BRASS, 60)

    # 5 social post mini cards staggered
    SQSZ = 280
    cards = [
        ("Daily Special", "TODAY'S\nSPECIAL", RUST),
        ("Loyalty Reward", "DOUBLE\nSTAMPS", ESPRESSO),
        ("Promo Offer", "20% OFF\nLUNCH", DARK_PANEL),
        ("Leave a Review", "LOVED IT?\nTELL US!", ESPRESSO),
        ("Daily Tip", "BARISTA\nTIP", RUST),
    ]
    positions = [
        (60,   350),
        (360,  350),
        (660,  350),
        (60,   660),
        (360,  660),
    ]
    for (title_text, big_text, bg), (cx_pos, cy_pos) in zip(cards, positions):
        c = Image.new("RGB", (SQSZ, SQSZ), bg)
        cd = ImageDraw.Draw(c)
        cd.rectangle([0, 0, SQSZ, SQSZ], outline=BRASS, width=3)
        # Brass accent corner
        cd.rectangle([0, 0, SQSZ, 6], fill=BRASS)
        cd.rectangle([0, SQSZ - 6, SQSZ, SQSZ], fill=BRASS)
        # Title
        t = fnt(16, bold=False)
        bbox = cd.textbbox((0, 0), title_text, font=t)
        tw = bbox[2] - bbox[0]
        cd.text(((SQSZ - tw) // 2, 14), title_text, fill=BRASS, font=t)
        # Big text
        lines = big_text.split("\n")
        fsize = 38 if len(lines[0]) <= 7 else 30
        f_big = fnt(fsize, bold=True)
        for li, line in enumerate(lines):
            bbox = cd.textbbox((0, 0), line, font=f_big)
            tw = bbox[2] - bbox[0]
            y_l = SQSZ // 2 - 30 + li * (fsize + 6)
            cd.text(((SQSZ - tw) // 2, y_l), line, fill=WHITE, font=f_big)
        # Bottom brand
        fb = fnt(12, bold=False)
        bbox = cd.textbbox((0, 0), "@yourcafe", font=fb)
        tw = bbox[2] - bbox[0]
        cd.text(((SQSZ - tw) // 2, SQSZ - 30), "@yourcafe", fill=SILVER, font=fb)

        shadow = Image.new("RGBA", (SQSZ + 12, SQSZ + 12), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        sd.rectangle([6, 6, SQSZ + 6, SQSZ + 6], fill=(0, 0, 0, 80))
        shadow = shadow.filter(ImageFilter.GaussianBlur(8))
        img.paste(shadow.convert("RGB"), (cx_pos - 6, cy_pos - 6), shadow.split()[3])
        img.paste(c, (cx_pos, cy_pos))

    # Floating 5th card centred bottom area
    c5_pos = (660, 660)
    c = Image.new("RGB", (SQSZ, SQSZ), DARK_PANEL)
    cd = ImageDraw.Draw(c)
    cd.rectangle([0, 0, SQSZ, SQSZ], outline=BRASS, width=3)
    cd.rectangle([0, 0, SQSZ, 6], fill=BRASS)
    cd.rectangle([0, SQSZ - 6, SQSZ, SQSZ], fill=BRASS)
    t = fnt(16, bold=False)
    bbox = cd.textbbox((0, 0), "Daily Tip", font=t)
    cd.text(((SQSZ - (bbox[2]-bbox[0])) // 2, 14), "Daily Tip", fill=BRASS, font=t)
    f_big = fnt(36, bold=True)
    for li, line in enumerate(["BARISTA", "TIP"]):
        bbox = cd.textbbox((0, 0), line, font=f_big)
        tw = bbox[2] - bbox[0]
        cd.text(((SQSZ - tw) // 2, SQSZ // 2 - 30 + li * 44), line, fill=WHITE, font=f_big)
    fb = fnt(12, bold=False)
    bbox = cd.textbbox((0, 0), "@yourcafe", font=fb)
    cd.text(((SQSZ - (bbox[2]-bbox[0])) // 2, SQSZ - 30), "@yourcafe", fill=SILVER, font=fb)
    shadow = Image.new("RGBA", (SQSZ + 12, SQSZ + 12), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rectangle([6, 6, SQSZ + 6, SQSZ + 6], fill=(0, 0, 0, 80))
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))
    img.paste(shadow.convert("RGB"), (c5_pos[0] - 6, c5_pos[1] - 6), shadow.split()[3])
    img.paste(c, c5_pos)

    # Bottom section
    rule(draw, 970, BRASS, 60)
    cx(draw, "ALL 5 POST TEMPLATES INCLUDED", 990, fnt(28, bold=True), WHITE)
    cx(draw, "Ready to post. Just add your logo.", 1034, fnt(24, bold=False, serif=True, italic=True), SILVER)

    # Feature checklist
    features = ["Daily specials + menu drops", "Loyalty reward posts",
                 "Promotional offers", "Review call-outs + staff spotlights"]
    f_feat = fnt(24)
    for i, feat in enumerate(features):
        y_f = 1080 + i * 54
        rounded_rect(draw, 60, y_f + 4, 26, 26, 4, BRASS)
        draw.text((66, y_f + 4), "✓", fill=ESPRESSO, font=fnt(15))
        draw.text((100, y_f), feat, fill=WHITE, font=f_feat)

    rule(draw, 1308, BRASS, 60)
    pill(draw, W // 2, 1326, 440, 60, BRASS, "Get all 5 — in the bundle", ESPRESSO, 26)

    canva_tag(draw, 1435)
    bar(draw, H - 18, 18, BRASS)
    purpleocaz_badge(draw, H - 16)

    path = os.path.join(OUTPUT_DIR, "restaurant-pin-3.png")
    img.save(path, "PNG")
    print(f"  Saved: {os.path.basename(path)}")
    return path


# ═══════════════════════════════════════════════════════════════════════════════
# PIN 4 — Forms & Operations
# ═══════════════════════════════════════════════════════════════════════════════
def pin_4():
    print("[4/5] Pin 4 — Forms + Operations")
    img = Image.new("RGB", (W, H), LIGHT_PANEL)
    draw = ImageDraw.Draw(img)

    bar(draw, 0, 16, ESPRESSO)
    cx(draw, "FORMS + STAFF OPERATIONS", 28, fnt(20), ESPRESSO)
    rule(draw, 64, ESPRESSO, 80)

    cx(draw, "EVERYTHING BEHIND", 84, fnt(50, bold=True), ESPRESSO)
    cx(draw, "THE COUNTER", 142, fnt(50, bold=True), ESPRESSO)
    cx(draw, "Professional forms for a smooth-running kitchen", 210,
       fnt(24, bold=False, serif=True, italic=True), RUST)
    rule(draw, 252, ESPRESSO, 80)

    # Form category tiles (2x4 grid)
    form_cats = [
        ("Customer\nIntake", "clipboard"),
        ("Allergy\nConsent", "shield"),
        ("Staff\nSchedule", "calendar"),
        ("Event\nEnquiry", "star"),
        ("Invoice &\nBooking", "receipt"),
        ("Daily\nChecklist", "checklist"),
        ("Income\nTracker", "chart"),
        ("Waste &\nStock Log", "package"),
    ]
    tile_w, tile_h = 218, 155
    gap = 14
    start_x, start_y = 46, 275
    icon_map = {
        "clipboard": "📋", "shield": "🛡", "calendar": "📅", "star": "⭐",
        "receipt": "🧾", "checklist": "✅", "chart": "📊", "package": "📦",
    }
    f_tile_title = fnt(21, bold=True)
    for i, (name, icon_key) in enumerate(form_cats):
        col = i % 4
        row = i // 4
        tx = start_x + col * (tile_w + gap)
        ty = start_y + row * (tile_h + gap)
        # Tile bg
        rounded_rect(draw, tx, ty, tile_w, tile_h, 10, CREAM)
        draw.rounded_rectangle([tx, ty, tx + tile_w, ty + tile_h], radius=10,
                                outline=ESPRESSO, width=2)
        # Brass accent left bar
        draw.rectangle([tx, ty + 12, tx + 5, ty + tile_h - 12], fill=ESPRESSO)
        # Icon
        icon = icon_map.get(icon_key, "📄")
        fi = fnt(30, bold=False)
        bbox = draw.textbbox((0, 0), icon, font=fi)
        tw = bbox[2] - bbox[0]
        draw.text((tx + (tile_w - tw) // 2, ty + 14), icon, fill=ESPRESSO, font=fi)
        # Title lines
        lines = name.split("\n")
        for li, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=f_tile_title)
            tw = bbox[2] - bbox[0]
            draw.text((tx + (tile_w - tw) // 2, ty + 68 + li * 30), line, fill=CHARCOAL, font=f_tile_title)

    rule(draw, 945, ESPRESSO, 60)

    # Trust bullet points
    bullets = [
        "Allergen + allergy forms included",
        "Staff schedules ready to print",
        "Event catering order forms",
        "Income + expenses trackers",
        "UK-compliant layout (A4 + US Letter)",
    ]
    f_bull = fnt(26)
    for i, bullet in enumerate(bullets):
        y_b = 970 + i * 64
        rounded_rect(draw, 60, y_b, tile_w * 4 + gap * 3, 54, 8, CREAM)
        draw.rectangle([60, y_b, 65, y_b + 54], fill=ESPRESSO)
        draw.text((90, y_b + 12), "✓  " + bullet, fill=CHARCOAL, font=f_bull)

    rule(draw, 1300, ESPRESSO, 60)
    cx(draw, "8 OPERATIONAL FORMS IN THE BUNDLE", 1318, fnt(28, bold=True), ESPRESSO)
    pill(draw, W // 2, 1362, 420, 60, ESPRESSO, "Download instantly — £39.99", WHITE, 26)

    canva_tag(draw, 1444)
    bar(draw, H - 18, 18, ESPRESSO)
    purpleocaz_badge(draw, H - 16)

    path = os.path.join(OUTPUT_DIR, "restaurant-pin-4.png")
    img.save(path, "PNG")
    print(f"  Saved: {os.path.basename(path)}")
    return path


# ═══════════════════════════════════════════════════════════════════════════════
# PIN 5 — Full Bundle CTA (rich dark, maximum appetite appeal)
# ═══════════════════════════════════════════════════════════════════════════════
def pin_5():
    print("[5/5] Pin 5 — Full Bundle CTA")
    img = Image.new("RGB", (W, H), CHARCOAL)
    img = warm_bg(img)
    draw = ImageDraw.Draw(img)

    # Gradient bands — warm espresso fade
    for i in range(35):
        opacity = max(0, 50 - i * 1)
        if opacity > 0:
            c = tuple(min(255, ESPRESSO[j] + opacity) for j in range(3))
            draw.rectangle([0, i * 45, W, i * 45 + 45], fill=c)
    draw = ImageDraw.Draw(img)

    bar(draw, 0, 16, BRASS)
    cx(draw, "COMPLETE CAFE + RESTAURANT KIT", 30, fnt(20), BRASS)

    cx(draw, "EVERYTHING",   72, fnt(100, bold=True), WHITE)
    cx(draw, "YOU NEED",    176, fnt(100, bold=True), WHITE)
    cx(draw, "TO OPEN YOUR DREAM", 286, fnt(52, bold=True), BRASS)
    cx(draw, "CAFE OR RESTAURANT", 344, fnt(52, bold=True), BRASS)

    rule(draw, 408, BRASS, 40)

    # Big price badge
    badge_y = 428
    rounded_rect(draw, (W - 360) // 2, badge_y, 360, 130, 20, BRASS)
    cx(draw, "£39.99", badge_y + 20, fnt(80, bold=True), ESPRESSO)
    cx(draw, "Worth over £70 individually", badge_y + 106, fnt(20, bold=False), DARK_PANEL)

    rule(draw, 584, SILVER, 60)

    # 2-column category grid
    cats = [
        ("Business Cards",   "2"),
        ("Social Posts",     "5"),
        ("Menu Templates",   "2"),
        ("Gift Certificate", "1"),
        ("Client Forms",     "6"),
        ("Operations",       "5"),
        ("Flyers",           "2"),
        ("Staff Tools",      "4"),
    ]
    col1, col2 = cats[:4], cats[4:]
    f_cat = fnt(26, bold=True)
    f_num = fnt(22, bold=False)
    y_grid = 604
    row_h  = 82
    lx, rx = 54, 508

    for i, (name, count) in enumerate(col1):
        y = y_grid + i * row_h
        rounded_rect(draw, lx, y + 6, 436, 58, 10, DARK_PANEL)
        draw.rectangle([lx, y + 6, lx + 6, y + 64], fill=BRASS)
        draw.text((lx + 20, y + 14), name, fill=WHITE, font=f_cat)
        rounded_rect(draw, lx + 356, y + 14, 60, 36, 10, RUST)
        bw = draw.textbbox((0, 0), count, font=f_num)[2]
        draw.text((lx + 356 + (60 - bw) // 2, y + 18), count, fill=WHITE, font=f_num)

    for i, (name, count) in enumerate(col2):
        y = y_grid + i * row_h
        rounded_rect(draw, rx, y + 6, 436, 58, 10, DARK_PANEL)
        draw.rectangle([rx, y + 6, rx + 6, y + 64], fill=BRASS)
        draw.text((rx + 20, y + 14), name, fill=WHITE, font=f_cat)
        rounded_rect(draw, rx + 356, y + 14, 60, 36, 10, RUST)
        bw = draw.textbbox((0, 0), count, font=f_num)[2]
        draw.text((rx + 356 + (60 - bw) // 2, y + 18), count, fill=WHITE, font=f_num)

    rule(draw, 1296, BRASS, 60)
    cx(draw, "32 TEMPLATES  —  INSTANT DOWNLOAD", 1316, fnt(30, bold=True), WHITE)
    pill(draw, W // 2, 1362, 500, 64, BRASS, "BUY NOW — purpleocaz.etsy.com", ESPRESSO, 24)

    canva_tag(draw, 1440)
    bar(draw, H - 18, 18, BRASS)

    path = os.path.join(OUTPUT_DIR, "restaurant-pin-5.png")
    img.save(path, "PNG")
    print(f"  Saved: {os.path.basename(path)}")
    return path


# ═══════════════════════════════════════════════════════════════════════════════
# VIDEO PIN — Ken Burns zoom + crossfade, 10 seconds
# ═══════════════════════════════════════════════════════════════════════════════
def build_video_pin(pin_paths):
    print("\n[6/6] Video Pin — Ken Burns + fade (10s)")
    out_path = os.path.join(OUTPUT_DIR, "restaurant-video-pin.mp4")

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
    content_type = {".png": "image/png", ".mp4": "video/mp4"}.get(ext, "application/octet-stream")
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
    print("RESTAURANT CAFE — PINTEREST PINS BUILD")
    print("=" * 60)

    print("\n=== Step 1: Build Static Pins ===")
    p1 = pin_1()
    p2 = pin_2()
    p3 = pin_3()
    p4 = pin_4()
    p5 = pin_5()
    pin_paths = [p1, p2, p3, p4, p5]

    print("\n=== Step 2: Build Video Pin ===")
    v1 = build_video_pin(pin_paths)

    print("\n=== Step 3: Upload to DO Spaces ===")
    load_spaces_env()
    s3 = get_s3()

    all_urls = {}
    for i, path in enumerate(pin_paths, 1):
        key = f"pinterest/restaurant-cafe-pin-{i}.png"
        all_urls[f"pin_{i}"] = upload(s3, path, key)

    all_urls["video"] = upload(s3, v1, "pinterest/restaurant-cafe-video-pin.mp4")

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
