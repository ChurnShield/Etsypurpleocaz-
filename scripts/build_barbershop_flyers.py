#!/usr/bin/env python3
"""
Barbershop Flyer Bundle — 4 flyers + preview grid.
1. Promotional (20% off first cut) — A4 portrait 2480x3508
2. Seasonal (Father's Day) — A4 portrait 2480x3508
3. Mobile/portrait (Instagram/WhatsApp) — 1080x1920
4. Walk-in special — A4 portrait 2480x3508

Design system: #1A1A1A bg, #C9A96E gold, #FFFFFF white.
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import boto3
from dotenv import load_dotenv

PROJECT_ROOT = Path("/root/NEW-AI-PROJECT")
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "barbershop" / "flyers"
PHOTO_DIR = PROJECT_ROOT / "assets" / "photos" / "barbershop_haircut_fade_dark"
TOOLS_DIR = PROJECT_ROOT / "assets" / "photos" / "barber_tools_scissors_razor"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

BG = (26, 26, 26)
GOLD = (201, 169, 110)
WHITE = (255, 255, 255)
GREY = (136, 136, 136)
DARK = (10, 10, 10)


def font(size, bold=False, italic=False, serif=False):
    if serif:
        p = FONT_SERIF_BOLD if bold else FONT_SERIF
    elif bold:
        p = FONT_BOLD
    elif italic:
        p = FONT_SERIF
    else:
        p = FONT_REGULAR
    return ImageFont.truetype(p, size)


def centred(draw, y, text, fill, f, canvas_w):
    bbox = draw.textbbox((0, 0), text, font=f)
    tw = bbox[2] - bbox[0]
    draw.text(((canvas_w - tw) // 2, y), text, fill=fill, font=f)


def draw_scissors(draw, cx, cy, size=80):
    draw.line([(cx - size, cy - 50), (cx + size, cy + 50)], fill=GOLD, width=8)
    draw.line([(cx + size, cy - 50), (cx - size, cy + 50)], fill=GOLD, width=8)
    for ex, ey in [(cx - size, cy - 50), (cx + size, cy - 50),
                   (cx - size, cy + 50), (cx + size, cy + 50)]:
        draw.ellipse([ex - 10, ey - 10, ex + 10, ey + 10], outline=GOLD, width=3)


def load_photo_cover(photo_path, w, h, overlay_alpha=140):
    """Load photo, centre-crop to wxh, apply dark overlay."""
    if photo_path and photo_path.exists():
        p = Image.open(photo_path).convert("RGBA")
        pw, ph = p.size
        target_ratio = w / h
        current_ratio = pw / ph
        if current_ratio > target_ratio:
            crop_w = int(ph * target_ratio)
            left = (pw - crop_w) // 2
            p = p.crop((left, 0, left + crop_w, ph))
        else:
            crop_h = int(pw / target_ratio)
            top = (ph - crop_h) // 2
            p = p.crop((0, top, pw, top + crop_h))
        p = p.resize((w, h), Image.LANCZOS)
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, overlay_alpha))
        p = Image.alpha_composite(p, overlay)
        return p.convert("RGB")
    img = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(img)
    draw_scissors(d, w // 2, h // 2, size=60)
    return img


def gold_rule(draw, x1, y, x2):
    draw.rectangle([x1, y, x2, y + 4], fill=GOLD)


# ════════════════════════════════════════════
# FLYER 1 — PROMOTIONAL (20% off first cut)
# ════════════════════════════════════════════

def build_flyer_promo():
    print("Building flyer 1: Promotional...")
    W, H = 2480, 3508
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    mx = 200

    # Top photo section (45% height)
    photo_h = int(H * 0.45)
    photo = load_photo_cover(PHOTO_DIR / "photo_1.jpg", W, photo_h, overlay_alpha=120)
    img.paste(photo, (0, 0))

    # Gold bars
    draw.rectangle([0, 0, W, 10], fill=GOLD)
    gold_rule(draw, 0, photo_h - 4, W)

    # Title over photo
    centred(draw, 180, "YOUR BARBERSHOP NAME", WHITE, font(48, bold=True), W)
    centred(draw, 250, "MASTER BARBERS", GOLD, font(28), W)
    draw_scissors(draw, W // 2, 380, size=70)
    centred(draw, 480, "PROFESSIONAL GROOMING", GREY, font(32), W)

    # Big promo text over photo
    centred(draw, 650, "20% OFF", WHITE, font(160, bold=True, serif=True), W)
    centred(draw, 860, "YOUR FIRST CUT", GOLD, font(72, bold=True), W)

    # Gold promo box below photo
    box_h = 120
    box_y = photo_h + 60
    box_mx = 300
    draw.rectangle([box_mx, box_y, W - box_mx, box_y + box_h], fill=GOLD)
    centred(draw, box_y + 25, "MENTION THIS FLYER TO REDEEM", BG, font(36, bold=True), W)
    centred(draw, box_y + 72, "Valid for new customers only", BG, font(24), W)

    # Services section
    y = box_y + box_h + 100
    centred(draw, y, "OUR SERVICES", GOLD, font(40, bold=True), W)
    y += 70
    gold_rule(draw, mx, y, W - mx)
    y += 30

    services = [
        ("Classic Haircut", "$25"),
        ("Skin Fade", "$32"),
        ("Hot Towel Shave", "$30"),
        ("Beard Trim & Shape", "$20"),
        ("The Works (Cut + Beard + Wash)", "$55"),
    ]
    for name, price in services:
        draw.text((mx + 40, y), name, fill=WHITE, font=font(34))
        # Right-align price
        pb = draw.textbbox((0, 0), price, font=font(34, bold=True))
        draw.text((W - mx - 40 - (pb[2] - pb[0]), y), price, fill=GOLD, font=font(34, bold=True))
        y += 65
        # Dotted line
        draw.rectangle([mx + 40, y - 15, W - mx - 40, y - 13], fill=(50, 50, 50))

    # CTA
    y += 60
    centred(draw, y, "BOOK YOUR APPOINTMENT TODAY", WHITE, font(44, bold=True), W)
    y += 80
    draw_scissors(draw, W // 2, y + 20, size=50)

    # ── Contact & info block ──
    y += 100
    gold_rule(draw, mx, y, W - mx)
    y += 50

    # Two-column layout: left = contact, right = hours
    col_left = mx + 60
    col_right = W // 2 + 80

    # Left column — contact
    draw.text((col_left, y), "FIND US", fill=GOLD, font=font(32, bold=True))
    y_left = y + 60
    contact_lines = [
        ("123 Main Street", WHITE),
        ("Your City, ST 00000", WHITE),
        ("", None),
        ("+1 (555) 000-0000", WHITE),
        ("hello@yourbarbershop.com", WHITE),
        ("www.yourbarbershop.com", GOLD),
        ("", None),
        ("@yourbarbershop", GREY),
    ]
    for line, colour in contact_lines:
        if line:
            draw.text((col_left, y_left), line, fill=colour, font=font(28))
        y_left += 48

    # Right column — opening hours
    draw.text((col_right, y), "OPENING HOURS", fill=GOLD, font=font(32, bold=True))
    y_right = y + 60
    hours = [
        ("Monday - Friday", "9AM - 8PM"),
        ("Saturday", "9AM - 6PM"),
        ("Sunday", "10AM - 4PM"),
    ]
    for day, time in hours:
        draw.text((col_right, y_right), day, fill=WHITE, font=font(28))
        draw.text((col_right, y_right + 40), time, fill=GOLD, font=font(28, bold=True))
        y_right += 100

    # Walk-ins note
    y_right += 20
    draw.text((col_right, y_right), "Walk-ins welcome", fill=GREY, font=font(26, italic=True))
    draw.text((col_right, y_right + 40), "Appointments preferred", fill=GREY, font=font(26, italic=True))

    # Vertical gold divider between columns
    div_x = W // 2 + 20
    draw.rectangle([div_x, y + 10, div_x + 3, y + 380], fill=GOLD)

    # Footer
    gold_rule(draw, 0, H - 100, W)
    centred(draw, H - 70, "YOUR BARBERSHOP NAME  |  MASTER BARBERS", GOLD, font(28, bold=True), W)
    draw.rectangle([0, H - 10, W, H], fill=GOLD)

    out = OUTPUT_DIR / "barber_flyer_01_promo.png"
    img.save(str(out), "PNG")
    print(f"  Saved: {out}")
    return out


# ════════════════════════════════════════════
# FLYER 2 — SEASONAL (Father's Day)
# ════════════════════════════════════════════

def build_flyer_seasonal():
    print("Building flyer 2: Seasonal (Father's Day)...")
    W, H = 2480, 3508
    # Full bleed photo with heavy overlay
    img = load_photo_cover(PHOTO_DIR / "photo_2.jpg", W, H, overlay_alpha=160)
    img = img.convert("RGB")
    draw = ImageDraw.Draw(img)

    # Gold frame border
    bw = 8
    draw.rectangle([40, 40, W - 40, H - 40], outline=GOLD, width=bw)

    # Top content
    centred(draw, 200, "YOUR BARBERSHOP NAME", WHITE, font(44, bold=True), W)
    centred(draw, 270, "MASTER BARBERS", GOLD, font(26), W)
    gold_rule(draw, 400, 330, W - 400)

    # Main headline
    draw_scissors(draw, W // 2, 500, size=80)
    centred(draw, 640, "FATHER'S DAY", WHITE, font(130, bold=True, serif=True), W)
    centred(draw, 810, "SPECIAL", GOLD, font(110, bold=True, serif=True), W)

    # Decorative rule
    gold_rule(draw, 500, 960, W - 500)

    # Offer details
    centred(draw, 1040, "Treat Dad to the VIP Experience", WHITE, font(44, italic=True), W)
    centred(draw, 1120, "Cut  +  Hot Towel Shave  +  Beard Trim", WHITE, font(38), W)

    # Price box
    price_box_w, price_box_h = 700, 200
    px = (W - price_box_w) // 2
    py = 1250
    draw.rectangle([px, py, px + price_box_w, py + price_box_h], outline=GOLD, width=4)
    centred(draw, py + 20, "ONLY", GREY, font(32), W)
    centred(draw, py + 65, "$55", WHITE, font(100, bold=True, serif=True), W)

    # Gift card callout
    centred(draw, 1550, "GIFT CARDS AVAILABLE", GOLD, font(40, bold=True), W)
    centred(draw, 1620, "The perfect gift for the man who has everything", GREY, font(28, italic=True), W)

    # Bottom services
    y = 1780
    gold_rule(draw, 400, y, W - 400)
    y += 40
    for svc in ["Classic Cuts", "Skin Fades", "Hot Towel Shaves",
                "Beard Grooming", "Hair Design"]:
        centred(draw, y, svc, WHITE, font(32), W)
        y += 55

    # CTA
    y += 40
    btn_w, btn_h = 900, 100
    bx = (W - btn_w) // 2
    draw.rounded_rectangle([bx, y, bx + btn_w, y + btn_h], radius=12, fill=GOLD)
    centred(draw, y + 22, "BOOK DAD'S APPOINTMENT", BG, font(38, bold=True), W)

    # Footer
    y_foot = H - 200
    gold_rule(draw, 400, y_foot, W - 400)
    centred(draw, y_foot + 30, "+1 (555) 000-0000  |  www.yourbarbershop.com", WHITE, font(28), W)
    centred(draw, y_foot + 80, "123 Main St, Your City  |  @yourbarbershop", GREY, font(24), W)

    out = OUTPUT_DIR / "barber_flyer_02_seasonal.png"
    img.save(str(out), "PNG")
    print(f"  Saved: {out}")
    return out


# ════════════════════════════════════════════
# FLYER 3 — MOBILE / INSTAGRAM STORY (1080x1920)
# ════════════════════════════════════════════

def build_flyer_mobile():
    print("Building flyer 3: Mobile/Instagram story...")
    W, H = 1080, 1920
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    mx = 80

    # Top photo (40%)
    photo_h = int(H * 0.40)
    photo = load_photo_cover(PHOTO_DIR / "photo_3.jpg", W, photo_h, overlay_alpha=100)
    img.paste(photo, (0, 0))

    # Gold bar at top
    draw.rectangle([0, 0, W, 6], fill=GOLD)

    # Shop name over photo
    centred(draw, 60, "YOUR BARBERSHOP", WHITE, font(32, bold=True), W)
    centred(draw, 105, "NAME", WHITE, font(32, bold=True), W)
    draw.rectangle([mx, 155, W - mx, 157], fill=GOLD)

    # Big text over photo
    centred(draw, 250, "FRESH", WHITE, font(110, bold=True, serif=True), W)
    centred(draw, 390, "CUTS", GOLD, font(110, bold=True, serif=True), W)
    centred(draw, 530, "DAILY", WHITE, font(110, bold=True, serif=True), W)

    # Scissors at split
    draw.rectangle([0, photo_h - 3, W, photo_h + 3], fill=GOLD)
    draw_scissors(draw, W // 2, photo_h + 60, size=40)

    # Services
    y = photo_h + 130
    centred(draw, y, "WHAT WE OFFER", GOLD, font(24, bold=True), W)
    y += 50
    draw.rectangle([mx, y, W - mx, y + 2], fill=GOLD)
    y += 25

    services = [
        "Classic Cuts & Fades",
        "Hot Towel Shaves",
        "Beard Trim & Shape",
        "Hair Design & Colour",
        "The VIP Experience",
    ]
    for svc in services:
        centred(draw, y, svc, WHITE, font(28), W)
        y += 55

    # Price callout
    y += 20
    draw.rectangle([mx, y, W - mx, y + 2], fill=GOLD)
    y += 30
    centred(draw, y, "CUTS FROM", GREY, font(22), W)
    centred(draw, y + 40, "$25", GOLD, font(80, bold=True, serif=True), W)

    # CTA button
    y += 160
    btn_w, btn_h = 600, 70
    bx = (W - btn_w) // 2
    draw.rounded_rectangle([bx, y, bx + btn_w, y + btn_h], radius=10, fill=GOLD)
    centred(draw, y + 16, "BOOK NOW", BG, font(30, bold=True), W)

    # Footer
    y_foot = H - 130
    draw.rectangle([0, y_foot, W, y_foot + 4], fill=GOLD)
    centred(draw, y_foot + 25, "+1 (555) 000-0000", WHITE, font(22), W)
    centred(draw, y_foot + 60, "www.yourbarbershop.com  |  @yourbarbershop", GREY, font(18), W)
    draw.rectangle([0, H - 6, W, H], fill=GOLD)

    out = OUTPUT_DIR / "barber_flyer_03_mobile.png"
    img.save(str(out), "PNG")
    print(f"  Saved: {out}")
    return out


# ════════════════════════════════════════════
# FLYER 4 — WALK-IN SPECIAL
# ════════════════════════════════════════════

def build_flyer_walkin():
    print("Building flyer 4: Walk-in special...")
    W, H = 2480, 3508
    # Full bleed photo
    img = load_photo_cover(PHOTO_DIR / "photo_4.jpg", W, H, overlay_alpha=155)
    img = img.convert("RGB")
    draw = ImageDraw.Draw(img)

    # Gold bars
    draw.rectangle([0, 0, W, 10], fill=GOLD)
    draw.rectangle([0, H - 10, W, H], fill=GOLD)

    # Top banner
    centred(draw, 120, "YOUR BARBERSHOP NAME", WHITE, font(44, bold=True), W)
    centred(draw, 185, "MASTER BARBERS", GOLD, font(26), W)
    gold_rule(draw, 300, 240, W - 300)

    # Main headline
    draw_scissors(draw, W // 2, 420, size=80)
    centred(draw, 560, "WALK-INS", WHITE, font(140, bold=True, serif=True), W)
    centred(draw, 740, "WELCOME", GOLD, font(140, bold=True, serif=True), W)

    # Decorative rule
    gold_rule(draw, 500, 920, W - 500)

    # Subtext
    centred(draw, 990, "No appointment? No problem.", WHITE, font(44, italic=True), W)
    centred(draw, 1060, "Grab a seat. We'll get you looking sharp.", GREY, font(34), W)

    # Services in dark panel
    panel_y = 1200
    panel_h = 600
    panel_mx = 250
    draw.rectangle([panel_mx, panel_y, W - panel_mx, panel_y + panel_h],
                   fill=(15, 15, 15, 200))
    draw.rectangle([panel_mx, panel_y, W - panel_mx, panel_y + panel_h],
                   outline=GOLD, width=3)

    centred(draw, panel_y + 30, "TODAY'S SPECIALS", GOLD, font(40, bold=True), W)
    gold_rule(draw, panel_mx + 60, panel_y + 90, W - panel_mx - 60)

    specials = [
        ("Walk-In Haircut", "$22"),
        ("Walk-In Fade", "$26"),
        ("Quick Beard Trim", "$12"),
        ("Student Cut (with ID)", "$18"),
        ("Cut + Beard Combo", "$35"),
    ]
    sy = panel_y + 120
    for name, price in specials:
        draw.text((panel_mx + 80, sy), name, fill=WHITE, font=font(34))
        pb = draw.textbbox((0, 0), price, font=font(34, bold=True))
        draw.text((W - panel_mx - 80 - (pb[2] - pb[0]), sy), price, fill=GOLD, font=font(34, bold=True))
        sy += 80
        if sy < panel_y + panel_h - 40:
            draw.rectangle([panel_mx + 80, sy - 20, W - panel_mx - 80, sy - 18],
                           fill=(50, 50, 50))

    # Opening hours
    y = panel_y + panel_h + 80
    centred(draw, y, "OPENING HOURS", GOLD, font(36, bold=True), W)
    y += 60
    hours = [
        "Monday - Friday: 9AM - 8PM",
        "Saturday: 9AM - 6PM",
        "Sunday: 10AM - 4PM",
    ]
    for line in hours:
        centred(draw, y, line, WHITE, font(30), W)
        y += 50

    # CTA
    y += 50
    btn_w, btn_h = 900, 110
    bx = (W - btn_w) // 2
    draw.rounded_rectangle([bx, y, bx + btn_w, y + btn_h], radius=14, fill=GOLD)
    centred(draw, y + 25, "JUST WALK IN", BG, font(44, bold=True), W)

    # Footer
    y_foot = H - 220
    gold_rule(draw, 300, y_foot, W - 300)
    centred(draw, y_foot + 40, "+1 (555) 000-0000  |  www.yourbarbershop.com", WHITE, font(30), W)
    centred(draw, y_foot + 90, "123 Main St, Your City  |  @yourbarbershop", GREY, font(26), W)

    out = OUTPUT_DIR / "barber_flyer_04_walkin.png"
    img.save(str(out), "PNG")
    print(f"  Saved: {out}")
    return out


# ════════════════════════════════════════════
# PREVIEW GRID — 2x2
# ════════════════════════════════════════════

def build_preview_grid(files):
    print("Building preview grid (2x2)...")
    thumb_w = 1200
    padding = 60
    gap = 50

    # Scale each to thumb_w, preserving aspect ratio
    thumbs = []
    for f in files:
        im = Image.open(f)
        w, h = im.size
        scale = thumb_w / w
        im = im.resize((thumb_w, int(h * scale)), Image.LANCZOS)
        thumbs.append(im)

    # 2x2 grid — find max height per row
    row1_h = max(thumbs[0].size[1], thumbs[1].size[1])
    row2_h = max(thumbs[2].size[1], thumbs[3].size[1])

    grid_w = padding * 2 + thumb_w * 2 + gap
    grid_h = padding * 2 + row1_h + row2_h + gap

    grid = Image.new("RGB", (grid_w, grid_h), DARK)

    positions = [
        (padding, padding),
        (padding + thumb_w + gap, padding),
        (padding, padding + row1_h + gap),
        (padding + thumb_w + gap, padding + row1_h + gap),
    ]
    for im, (x, y) in zip(thumbs, positions):
        grid.paste(im, (x, y))

    out = OUTPUT_DIR / "preview_grid.png"
    grid.save(str(out), "PNG")
    print(f"  Saved: {out}")
    return out


# ════════════════════════════════════════════
# UPLOAD TO DO SPACES
# ════════════════════════════════════════════

def upload_to_spaces(local_path, spaces_key):
    load_dotenv("/root/NEW-AI-PROJECT/purpleocaz-canva-mcp/.env")
    s3 = boto3.client("s3",
        endpoint_url="https://lon1.digitaloceanspaces.com",
        aws_access_key_id=os.getenv("DO_SPACES_KEY"),
        aws_secret_access_key=os.getenv("DO_SPACES_SECRET"),
        region_name="lon1",
    )
    s3.upload_file(
        str(local_path), "purpleocaz-assets", spaces_key,
        ExtraArgs={"ACL": "public-read", "ContentType": "image/png"},
    )
    url = f"https://purpleocaz-assets.lon1.digitaloceanspaces.com/{spaces_key}"
    print(f"  Uploaded: {url}")
    return url


# ════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════

if __name__ == "__main__":
    f1 = build_flyer_promo()
    f2 = build_flyer_seasonal()
    f3 = build_flyer_mobile()
    f4 = build_flyer_walkin()
    fg = build_preview_grid([f1, f2, f3, f4])

    uploads = [
        (f1, "barbershop/flyers/barber_flyer_01_promo.png"),
        (f2, "barbershop/flyers/barber_flyer_02_seasonal.png"),
        (f3, "barbershop/flyers/barber_flyer_03_mobile.png"),
        (f4, "barbershop/flyers/barber_flyer_04_walkin.png"),
        (fg, "barbershop/flyers/preview_grid.png"),
    ]
    for local, key in uploads:
        upload_to_spaces(local, key)

    print("\nDone. All 5 files uploaded.")
