#!/usr/bin/env python3
"""
Barbershop Print Essentials — 4 templates + preview grid.
1. Business Card — CR80 landscape (1050x600px) front + back
2. Appointment Card — CR80 landscape (1050x600px)
3. Thank You Card — A6 landscape (1240x874px)
4. Refer A Friend Card — A6 landscape (1240x874px)

Design system: #1A1A1A bg, #C9A96E gold, #FFFFFF white.
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import boto3
from dotenv import load_dotenv

PROJECT_ROOT = Path("/root/NEW-AI-PROJECT")
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "barbershop" / "print"
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
CREAM = (255, 253, 245)
DARK_TEXT = (26, 26, 26)


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


def right_aligned(draw, x_right, y, text, fill, f):
    bbox = draw.textbbox((0, 0), text, font=f)
    tw = bbox[2] - bbox[0]
    draw.text((x_right - tw, y), text, fill=fill, font=f)


def draw_scissors(draw, cx, cy, size=80):
    draw.line([(cx - size, cy - 50), (cx + size, cy + 50)], fill=GOLD, width=8)
    draw.line([(cx + size, cy - 50), (cx - size, cy + 50)], fill=GOLD, width=8)
    for ex, ey in [(cx - size, cy - 50), (cx + size, cy - 50),
                   (cx - size, cy + 50), (cx + size, cy + 50)]:
        draw.ellipse([ex - 10, ey - 10, ex + 10, ey + 10], outline=GOLD, width=3)


def gold_rule(draw, x1, y, x2):
    draw.rectangle([x1, y, x2, y + 2], fill=GOLD)


def load_photo_cover(photo_path, w, h, overlay_alpha=140):
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
    return img


# ════════════════════════════════════════════
# 1. BUSINESS CARD — FRONT
# ════════════════════════════════════════════

def build_business_card_front():
    print("Building business card (front)...")
    W, H = 1050, 600
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Gold border
    draw.rectangle([0, 0, W - 1, H - 1], outline=GOLD, width=3)

    # Left section: photo strip
    photo_w = int(W * 0.35)
    photo = load_photo_cover(PHOTO_DIR / "photo_1.jpg", photo_w, H, overlay_alpha=120)
    img.paste(photo, (0, 0))
    # Gold vertical divider
    draw.rectangle([photo_w, 0, photo_w + 3, H], fill=GOLD)

    # Right section: info
    rx = photo_w + 40
    rr = W - 30

    draw.text((rx, 50), "YOUR", fill=WHITE, font=font(22, bold=True))
    draw.text((rx, 80), "BARBERSHOP", fill=WHITE, font=font(22, bold=True))
    draw.text((rx, 110), "NAME", fill=WHITE, font=font(22, bold=True))
    gold_rule(draw, rx, 148, rr)

    draw.text((rx, 165), "Your Name Here", fill=GOLD, font=font(16, bold=True))
    draw.text((rx, 190), "Master Barber", fill=GREY, font=font(12))

    gold_rule(draw, rx, 220, rr)

    # Contact details
    y = 240
    details = [
        ("+1 (555) 000-0000", WHITE),
        ("hello@yourbarbershop.com", WHITE),
        ("www.yourbarbershop.com", GOLD),
        ("123 Main St, Your City", GREY),
        ("@yourbarbershop", GREY),
    ]
    for text, colour in details:
        draw.text((rx, y), text, fill=colour, font=font(12))
        y += 28

    # Hours at bottom
    y += 10
    draw.text((rx, y), "Mon-Sat 9-8  |  Sun 10-4", fill=GREY, font=font(10))

    # Gold bars
    draw.rectangle([0, 0, W, 4], fill=GOLD)
    draw.rectangle([0, H - 4, W, H], fill=GOLD)

    out = OUTPUT_DIR / "barber_print_01a_business_card_front.png"
    img.save(str(out), "PNG")
    print(f"  Saved: {out}")
    return out


# ════════════════════════════════════════════
# 1b. BUSINESS CARD — BACK
# ════════════════════════════════════════════

def build_business_card_back():
    print("Building business card (back)...")
    W, H = 1050, 600
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Gold border
    draw.rectangle([0, 0, W - 1, H - 1], outline=GOLD, width=3)
    draw.rectangle([0, 0, W, 4], fill=GOLD)
    draw.rectangle([0, H - 4, W, H], fill=GOLD)

    # Central scissors motif
    draw_scissors(draw, W // 2, H // 2 - 40, size=50)

    # Tagline
    centred(draw, H // 2 + 30, "MASTER BARBERS", GOLD, font(28, bold=True), W)

    # Decorative rules
    rule_w = 250
    rx = (W - rule_w) // 2
    gold_rule(draw, rx, H // 2 + 20, rx + rule_w)
    gold_rule(draw, rx, H // 2 + 72, rx + rule_w)

    # Website at bottom
    centred(draw, H - 60, "www.yourbarbershop.com", GREY, font(11), W)

    out = OUTPUT_DIR / "barber_print_01b_business_card_back.png"
    img.save(str(out), "PNG")
    print(f"  Saved: {out}")
    return out


# ════════════════════════════════════════════
# 2. APPOINTMENT CARD
# ════════════════════════════════════════════

def build_appointment_card():
    print("Building appointment card...")
    W, H = 1050, 600
    CREAM_BG = (255, 253, 245)
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Top dark header (35%)
    header_h = int(H * 0.35)

    # Gold bars
    draw.rectangle([0, 0, W, 4], fill=GOLD)

    # Header content
    draw_scissors(draw, 80, header_h // 2, size=25)
    draw.text((120, header_h // 2 - 22), "YOUR BARBERSHOP NAME", fill=WHITE, font=font(18, bold=True))
    draw.text((120, header_h // 2 + 8), "APPOINTMENT CARD", fill=GOLD, font=font(12))

    # Gold divider
    draw.rectangle([0, header_h, W, header_h + 3], fill=GOLD)

    # Bottom cream section with form fields
    draw.rectangle([0, header_h + 3, W, H], fill=CREAM_BG)

    mx = 40
    mx_end = W - 40

    def form_line(y, label):
        draw.text((mx, y), label, fill=DARK_TEXT, font=font(12))
        lbl_bbox = draw.textbbox((mx, y), label, font=font(12))
        line_start = lbl_bbox[2] + 10
        draw.rectangle([line_start, y + 16, mx_end, y + 17], fill=GOLD)
        return y + 38

    y = header_h + 20
    y = form_line(y, "Name:")
    y = form_line(y, "Date:")
    y = form_line(y, "Time:")
    y = form_line(y, "Barber:")
    y = form_line(y, "Notes:")

    # Footer
    centred(draw, H - 40, "We look forward to seeing you", DARK_TEXT, font(11, italic=True), W)

    # Bottom gold bar
    draw.rectangle([0, H - 4, W, H], fill=GOLD)

    out = OUTPUT_DIR / "barber_print_02_appointment_card.png"
    img.save(str(out), "PNG")
    print(f"  Saved: {out}")
    return out


# ════════════════════════════════════════════
# 3. THANK YOU CARD — A6 landscape
# ════════════════════════════════════════════

def build_thank_you_card():
    print("Building thank you card...")
    W, H = 1240, 874
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Gold border
    draw.rectangle([12, 12, W - 12, H - 12], outline=GOLD, width=3)
    draw.rectangle([0, 0, W, 6], fill=GOLD)
    draw.rectangle([0, H - 6, W, H], fill=GOLD)

    # Scissors
    draw_scissors(draw, W // 2, 100, size=45)

    # Title
    centred(draw, 170, "THANK YOU", WHITE, font(52, bold=True, serif=True), W)
    centred(draw, 235, "FOR YOUR VISIT", GOLD, font(30, bold=True), W)

    # Decorative rule
    rule_w = 300
    rx = (W - rule_w) // 2
    gold_rule(draw, rx, 285, rx + rule_w)

    # Shop name
    centred(draw, 305, "YOUR BARBERSHOP NAME", WHITE, font(18, bold=True), W)

    # Personal note area (cream box)
    box_mx = 80
    box_y = 360
    box_h = 200
    draw.rectangle([box_mx, box_y, W - box_mx, box_y + box_h], fill=CREAM)
    draw.rectangle([box_mx, box_y, W - box_mx, box_y + box_h], outline=GOLD, width=2)
    draw.text((box_mx + 20, box_y + 15), "Personal note:", fill=DARK_TEXT, font=font(13, italic=True))
    # Lines for writing
    for i in range(3):
        line_y = box_y + 55 + i * 45
        draw.rectangle([box_mx + 20, line_y, W - box_mx - 20, line_y + 1], fill=GOLD)

    # Discount offer
    y = box_y + box_h + 40
    centred(draw, y, "ENJOY 10% OFF YOUR NEXT VISIT", GOLD, font(22, bold=True), W)
    y += 40
    centred(draw, y, "Show this card to redeem  |  Valid 30 days", GREY, font(13), W)

    # Footer
    gold_rule(draw, 80, H - 70, W - 80)
    centred(draw, H - 50, "+1 (555) 000-0000  |  www.yourbarbershop.com", GREY, font(12), W)

    out = OUTPUT_DIR / "barber_print_03_thank_you.png"
    img.save(str(out), "PNG")
    print(f"  Saved: {out}")
    return out


# ════════════════════════════════════════════
# 4. REFER A FRIEND CARD — A6 landscape
# ════════════════════════════════════════════

def build_refer_a_friend():
    print("Building refer a friend card...")
    W, H = 1240, 874
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Gold border
    draw.rectangle([12, 12, W - 12, H - 12], outline=GOLD, width=3)
    draw.rectangle([0, 0, W, 6], fill=GOLD)
    draw.rectangle([0, H - 6, W, H], fill=GOLD)

    # Scissors
    draw_scissors(draw, W // 2, 85, size=40)

    # Title
    centred(draw, 155, "REFER A FRIEND", WHITE, font(46, bold=True, serif=True), W)

    # Offer pill
    pill_w, pill_h = 500, 50
    px = (W - pill_w) // 2
    py = 225
    draw.rounded_rectangle([px, py, px + pill_w, py + pill_h], radius=pill_h // 2, fill=GOLD)
    centred(draw, py + 12, "GET £10 OFF YOUR NEXT CUT", BG, font(18, bold=True), W)

    # Shop name
    centred(draw, 300, "YOUR BARBERSHOP NAME", GREY, font(14), W)

    # Form fields on cream background
    box_mx = 80
    box_y = 340
    box_h = 280
    draw.rectangle([box_mx, box_y, W - box_mx, box_y + box_h], fill=CREAM)
    draw.rectangle([box_mx, box_y, W - box_mx, box_y + box_h], outline=GOLD, width=2)

    mx_inner = box_mx + 25
    mx_end_inner = W - box_mx - 25

    def form_field(y, label):
        draw.text((mx_inner, y), label, fill=DARK_TEXT, font=font(13))
        lbl_bbox = draw.textbbox((mx_inner, y), label, font=font(13))
        draw.rectangle([mx_inner, y + 24, mx_end_inner, y + 25], fill=GOLD)
        return y + 50

    fy = box_y + 20
    fy = form_field(fy, "Your Name (Referrer):")
    fy = form_field(fy, "Your Phone / Email:")
    fy = form_field(fy, "Friend's Name:")
    fy = form_field(fy, "Friend's Phone / Email:")

    # Terms
    centred(draw, fy + 15, "Friend must be a new client. Discount on next visit after friend's first cut.", DARK_TEXT, font(10), W)

    # Expiry
    y = box_y + box_h + 25
    centred(draw, y, "Valid until: _______________", GREY, font(13), W)

    # Footer
    gold_rule(draw, 80, H - 70, W - 80)
    centred(draw, H - 50, "+1 (555) 000-0000  |  www.yourbarbershop.com", GREY, font(12), W)

    out = OUTPUT_DIR / "barber_print_04_refer_a_friend.png"
    img.save(str(out), "PNG")
    print(f"  Saved: {out}")
    return out


# ════════════════════════════════════════════
# PREVIEW GRID — 2x3
# ════════════════════════════════════════════

def build_preview_grid(files):
    print("Building preview grid...")
    thumb_w = 1000
    padding = 50
    gap = 40

    thumbs = []
    for f in files:
        im = Image.open(f)
        w, h = im.size
        scale = thumb_w / w
        im = im.resize((thumb_w, int(h * scale)), Image.LANCZOS)
        thumbs.append(im)

    # 2 columns, 3 rows (5 items: front, back, appt, thankyou, refer)
    cols = 2
    rows = 3
    max_h_per_row = []
    for r in range(rows):
        row_thumbs = thumbs[r * cols:(r + 1) * cols]
        if row_thumbs:
            max_h_per_row.append(max(t.size[1] for t in row_thumbs))
        else:
            max_h_per_row.append(0)

    grid_w = padding * 2 + thumb_w * cols + gap * (cols - 1)
    grid_h = padding * 2 + sum(max_h_per_row) + gap * (rows - 1)

    grid = Image.new("RGB", (grid_w, grid_h), DARK)

    idx = 0
    y = padding
    for r in range(rows):
        x = padding
        for c in range(cols):
            if idx < len(thumbs):
                grid.paste(thumbs[idx], (x, y))
                idx += 1
            x += thumb_w + gap
        y += max_h_per_row[r] + gap

    out = OUTPUT_DIR / "preview_grid.png"
    grid.save(str(out), "PNG")
    print(f"  Saved: {out}")
    return out


# ════════════════════════════════════════════
# UPLOAD
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
    f1a = build_business_card_front()
    f1b = build_business_card_back()
    f2 = build_appointment_card()
    f3 = build_thank_you_card()
    f4 = build_refer_a_friend()
    fg = build_preview_grid([f1a, f1b, f2, f3, f4])

    uploads = [
        (f1a, "barbershop/print/barber_print_01a_business_card_front.png"),
        (f1b, "barbershop/print/barber_print_01b_business_card_back.png"),
        (f2,  "barbershop/print/barber_print_02_appointment_card.png"),
        (f3,  "barbershop/print/barber_print_03_thank_you.png"),
        (f4,  "barbershop/print/barber_print_04_refer_a_friend.png"),
        (fg,  "barbershop/print/preview_grid.png"),
    ]
    for local, key in uploads:
        upload_to_spaces(local, key)

    print("\nDone. All 6 files uploaded.")
