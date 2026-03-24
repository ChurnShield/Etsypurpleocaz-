#!/usr/bin/env python3
"""
Barbershop Visual Bundle — 3 templates + preview grid.
1. Service Price List (2550x3300 US Letter)
2. Gift Certificate (2550x1800 landscape)
3. Loyalty Punch Card (1050x600 business card)

Design system: #0A0A0A bg, #C9A96E gold, #FFFFFF white, #888888 grey.
"""

import os, io, math
import boto3, requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

PROJECT_ROOT = Path("/root/NEW-AI-PROJECT")
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "barbershop" / "visual"
PHOTO_DIR = PROJECT_ROOT / "assets" / "photos" / "barbershop"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PHOTO_DIR.mkdir(parents=True, exist_ok=True)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"

BG      = (10, 10, 10)
PANEL   = (26, 26, 26)
BOX     = (42, 42, 42)
GOLD    = (201, 169, 110)
WHITE   = (255, 255, 255)
GREY    = (136, 136, 136)


def font(size, bold=False, italic=False):
    p = FONT_SERIF if italic else (FONT_BOLD if bold else FONT_REGULAR)
    return ImageFont.truetype(p, size)


def centred(draw, y, text, fill, f, canvas_w=None):
    w = canvas_w or draw.im.size[0]
    bbox = draw.textbbox((0, 0), text, font=f)
    tw = bbox[2] - bbox[0]
    draw.text(((w - tw) // 2, y), text, fill=fill, font=f)


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


def fetch_photo(query, filename, w=680, h=813):
    """Fetch from Unsplash. On failure, return None."""
    path = PHOTO_DIR / filename
    if path.exists():
        print(f"  Photo cached: {filename}")
        return path
    try:
        url = f"https://source.unsplash.com/random/{w}x{h}/?{query.replace(' ', ',')}"
        r = requests.get(url, timeout=15, allow_redirects=True)
        if r.status_code == 200 and len(r.content) > 5000:
            path.write_bytes(r.content)
            print(f"  Fetched photo: {filename} ({len(r.content)} bytes)")
            return path
    except Exception as e:
        print(f"  Photo fetch failed ({filename}): {e}")
    return None


def make_photo_panel(photo_path, w, h, overlay_alpha=115):
    """Load photo, resize to wxh, apply dark overlay."""
    if photo_path and photo_path.exists():
        img = Image.open(photo_path).convert("RGBA").resize((w, h), Image.LANCZOS)
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, overlay_alpha))
        img = Image.alpha_composite(img, overlay)
        return img.convert("RGB")
    # Fallback: solid panel with scissors
    img = Image.new("RGB", (w, h), PANEL)
    d = ImageDraw.Draw(img)
    draw_scissors(d, w // 2, h // 2, size=60)
    return img


# ════════════════════════════════════════════
# VISUAL 1 — SERVICE PRICE LIST
# ════════════════════════════════════════════

def build_price_list():
    print("Building price list...")
    W, H = 2550, 3300
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # ── Header y=0 to y=380 ──
    draw.rectangle([0, 0, W, 380], fill=BG)
    draw_scissors(draw, 1275, 70, size=80)
    centred(draw, 150, "YOUR BARBERSHOP NAME", WHITE, font(60, bold=True), W)
    centred(draw, 210, "MASTER BARBERS", GOLD, font(28), W)
    draw.rectangle([0, 254, W, 260], fill=GOLD)
    centred(draw, 310, "SERVICE MENU & PRICE LIST", WHITE, font(44, bold=True), W)

    # ── Left photo strip x=0..680 y=380..2820 ──
    photo_queries = [
        ("barbershop haircut fade", "barber_price_1.jpg"),
        ("barber beard trim close up", "barber_price_2.jpg"),
        ("barbershop chair interior dark", "barber_price_3.jpg"),
    ]
    strip_h = 2820 - 380  # 2440
    panel_h = strip_h // 3  # 813
    for i, (query, fname) in enumerate(photo_queries):
        photo = fetch_photo(query, fname, 680, panel_h)
        panel = make_photo_panel(photo, 680, panel_h)
        img.paste(panel, (0, 380 + i * panel_h))

    # ── Right content area ──
    rx = 730
    rx_end = 2420

    def section_title(y, title):
        draw.text((rx, y), title, fill=GOLD, font=font(30, bold=True))
        draw.rectangle([rx, y + 40, rx_end, y + 42], fill=GOLD)
        return y + 42

    def service_row(y, name, price):
        draw.text((rx, y + 8), name, fill=WHITE, font=font(24))
        right_aligned(draw, rx_end, y + 8, price, GOLD, font(24))
        # Dotted line between
        name_bbox = draw.textbbox((rx, y + 8), name, font=font(24))
        price_bbox = draw.textbbox((0, 0), price, font=font(24))
        dot_start = name_bbox[2] + 15
        dot_end = rx_end - (price_bbox[2] - price_bbox[0]) - 15
        dot_y = y + 24
        x = dot_start
        while x < dot_end:
            draw.ellipse([x, dot_y, x + 3, dot_y + 3], fill=GREY)
            x += 12
        return y + 48

    # Classic Cuts
    y = section_title(420, "CLASSIC CUTS")
    for name, price in [("Haircut", "$25"), ("Children's Cut", "$18"),
                        ("Buzz Cut", "$20"), ("Crew Cut", "$22")]:
        y = service_row(y, name, price)

    # Fades & Tapers
    y = section_title(y + 30, "FADES & TAPERS")
    for name, price in [("Low Fade", "$28"), ("Mid Fade", "$28"),
                        ("High Fade", "$28"), ("Skin Fade", "$32"),
                        ("Taper Fade", "$30")]:
        y = service_row(y, name, price)

    # Beard Services
    y = section_title(y + 30, "BEARD SERVICES")
    for name, price in [("Beard Trim", "$15"), ("Beard Shape Up", "$20"),
                        ("Hot Towel Shave", "$30"), ("Beard + Cut Combo", "$40")]:
        y = service_row(y, name, price)

    # Add-Ons
    y = section_title(y + 30, "ADD-ONS")
    for name, price in [("Line Up", "$10"), ("Hair Wash", "$12"),
                        ("Eyebrow Shape", "$10"), ("Hot Towel Treatment", "$8")]:
        y = service_row(y, name, price)

    # Walk-ins banner
    draw.rectangle([0, 1454, W, 1458], fill=GOLD)
    centred(draw, 1500, "WALK-INS WELCOME  ·  APPOINTMENTS PREFERRED", GOLD, font(24), W)

    # ── Footer y=2820..3300 ──
    draw.rectangle([0, 2820, W, 3300], fill=BG)
    draw.rectangle([0, 2820, W, 2826], fill=GOLD)
    centred(draw, 2880, "BOOK YOUR APPOINTMENT TODAY", GOLD, font(36, bold=True), W)
    centred(draw, 2950, "+1 (555) 000-0000  ·  www.yourbarbershop.com", WHITE, font(26), W)
    centred(draw, 3010, "123 Main St, Your City, ST  ·  Mon-Sat 9AM-8PM  Sun 10AM-4PM", GOLD, font(22), W)
    # Footer scissors
    draw_scissors(draw, 200, 2960, size=40)
    draw_scissors(draw, 2350, 2960, size=40)

    out = OUTPUT_DIR / "barber_visual_01_pricelist.png"
    img.save(str(out), "PNG")
    print(f"  Saved: {out} ({out.stat().st_size} bytes)")
    return out


# ════════════════════════════════════════════
# VISUAL 2 — GIFT CERTIFICATE
# ════════════════════════════════════════════

def build_gift_certificate():
    print("Building gift certificate...")
    W, H = 2550, 1800
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Gold rules top/bottom
    draw.rectangle([0, 0, W, 8], fill=GOLD)
    draw.rectangle([0, 1792, W, 1800], fill=GOLD)

    # Gold border frame
    draw.rectangle([40, 40, 2510, 1760], outline=GOLD, width=4)

    # Large scissors icon
    draw_scissors(draw, 1275, 150, size=50)

    # Title
    centred(draw, 280, "GIFT CERTIFICATE", WHITE, font(80, bold=True), W)

    # Gold rule centred 500px
    rule_x = (W - 500) // 2
    draw.rectangle([rule_x, 380, rule_x + 500, 384], fill=GOLD)

    # Shop name
    centred(draw, 440, "YOUR BARBERSHOP NAME", GOLD, font(52, bold=True), W)
    centred(draw, 510, "MASTER BARBERS", WHITE, font(28), W)

    # Gold rule
    draw.rectangle([rule_x, 570, rule_x + 500, 574], fill=GOLD)

    # Certificate body
    centred(draw, 630, "This certificate entitles", GREY, font(30, italic=True), W)
    centred(draw, 690, "_________________________________", WHITE, font(34), W)
    centred(draw, 750, "to the value of", GREY, font(28), W)
    centred(draw, 850, "$ ___________", GOLD, font(80, bold=True), W)

    # Gold rule
    rule_x2 = (W - 400) // 2
    draw.rectangle([rule_x2, 950, rule_x2 + 400, 954], fill=GOLD)

    # Validity
    centred(draw, 1010, "Valid until: _____________________", GREY, font(28), W)
    centred(draw, 1060, "Redeemable at: YOUR BARBERSHOP NAME", GREY, font(24), W)

    # Gold pill "NOT REDEEMABLE FOR CASH"
    pill_w, pill_h = 600, 50
    pill_x = (W - pill_w) // 2
    pill_y = 1120
    r = pill_h // 2
    draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h],
                           radius=r, fill=GOLD)
    centred(draw, pill_y + 12, "NOT REDEEMABLE FOR CASH", BG, font(20, bold=True), W)

    # Details box
    bx1, by1, bx2, by2 = 300, 1200, 2250, 1440
    draw.rectangle([bx1, by1, bx2, by2], outline=GOLD, width=2)
    draw.text((320, 1240), "Purchased by: _______________________", fill=WHITE, font=font(26))
    draw.text((320, 1300), "Authorised by: _____________________", fill=WHITE, font=font(26))
    draw.text((320, 1360), "Date issued: ________________________", fill=WHITE, font=font(26))

    # Footer
    centred(draw, 1520, "www.yourbarbershop.com  ·  +1 (555) 000-0000", GREY, font(22), W)

    out = OUTPUT_DIR / "barber_visual_02_giftcert.png"
    img.save(str(out), "PNG")
    print(f"  Saved: {out} ({out.stat().st_size} bytes)")
    return out


# ════════════════════════════════════════════
# VISUAL 3 — LOYALTY PUNCH CARD
# ════════════════════════════════════════════

def build_loyalty_card():
    print("Building loyalty card...")
    W, H = 1050, 600
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Gold bars top/bottom
    draw.rectangle([0, 0, W, 8], fill=GOLD)
    draw.rectangle([0, 592, W, 600], fill=GOLD)

    # ── Left section x=0..400 ──
    draw_scissors(draw, 70, 220, size=30)
    draw.text((40, 290), "YOUR BARBERSHOP", fill=WHITE, font=font(22, bold=True))
    draw.text((40, 322), "NAME", fill=WHITE, font=font(22, bold=True))
    draw.text((40, 360), "LOYALTY CARD", fill=GOLD, font=font(16))
    draw.rectangle([40, 390, 240, 392], fill=GOLD)
    draw.text((40, 420), "YOUR 10TH", fill=WHITE, font=font(18, bold=True))
    draw.text((40, 450), "CUT IS FREE", fill=GOLD, font=font(18, bold=True))
    draw.text((40, 530), "@yourbarbershop", fill=GREY, font=font(14))

    # ── Right section x=420..1050 ──
    draw.text((430, 120), "COLLECT YOUR STAMPS", fill=GREY, font=font(14))

    # 10 circles in 2 rows of 5
    circle_xs = [430, 490, 550, 610, 670]
    circle_d = 45
    for row, cy in enumerate([180, 280]):
        for col, cx in enumerate(circle_xs):
            num = row * 5 + col + 1
            x1 = cx
            y1 = cy
            x2 = cx + circle_d
            y2 = cy + circle_d
            draw.ellipse([x1, y1, x2, y2], outline=GOLD, width=2)
            # Number below
            num_str = str(num)
            nb = draw.textbbox((0, 0), num_str, font=font(12))
            nw = nb[2] - nb[0]
            draw.text((cx + (circle_d - nw) // 2, y2 + 5), num_str,
                      fill=GREY, font=font(12))
            # Example stamp in circle 1
            if num == 1:
                sb = draw.textbbox((0, 0), "✂", font=font(20))
                sw = sb[2] - sb[0]
                sh = sb[3] - sb[1]
                draw.text((cx + (circle_d - sw) // 2, cy + (circle_d - sh) // 2 - 2),
                          "✂", fill=GOLD, font=font(20))

    draw.text((430, 380), "Ask your barber to stamp after each visit",
              fill=GREY, font=font(12))
    draw.rectangle([430, 420, 1020, 422], fill=GOLD)
    draw.text((430, 450), "Valid at: YOUR BARBERSHOP NAME", fill=GREY, font=font(12))
    draw.text((430, 480), "+1 (555) 000-0000", fill=GREY, font=font(12))

    out = OUTPUT_DIR / "barber_visual_03_loyalty.png"
    img.save(str(out), "PNG")
    print(f"  Saved: {out} ({out.stat().st_size} bytes)")
    return out


# ════════════════════════════════════════════
# PREVIEW GRID — 3x1 side by side
# ════════════════════════════════════════════

def build_preview_grid(files):
    print("Building preview grid...")
    grid_w, grid_h = 3240, 1080
    gap = 20
    n = len(files)
    slot_w = (grid_w - gap * (n - 1)) // n  # 1066 each

    grid = Image.new("RGB", (grid_w, grid_h), BG)

    for i, f in enumerate(files):
        im = Image.open(f)
        # Scale proportionally to fit in slot_w x grid_h
        w, h = im.size
        scale = min(slot_w / w, grid_h / h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        im = im.resize((new_w, new_h), Image.LANCZOS)
        x = i * (slot_w + gap) + (slot_w - new_w) // 2
        y = (grid_h - new_h) // 2
        grid.paste(im, (x, y))

    out = OUTPUT_DIR / "preview_grid.png"
    grid.save(str(out), "PNG")
    print(f"  Saved: {out} ({out.stat().st_size} bytes)")
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
    f1 = build_price_list()
    f2 = build_gift_certificate()
    f3 = build_loyalty_card()
    fg = build_preview_grid([f1, f2, f3])

    uploads = [
        (f1, "barbershop/visual/barber_visual_01_pricelist.png"),
        (f2, "barbershop/visual/barber_visual_02_giftcert.png"),
        (f3, "barbershop/visual/barber_visual_03_loyalty.png"),
        (fg, "barbershop/visual/preview_grid.png"),
    ]
    for local, key in uploads:
        upload_to_spaces(local, key)

    print("\nDone. All 4 files uploaded.")
