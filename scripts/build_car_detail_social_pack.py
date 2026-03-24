#!/usr/bin/env python3
"""
Build 20 Car Detailing Instagram Post Templates (1080x1080 PNG).

Design system:
  Background: #0D0D0D | Accent: #E02020 | Text: #FFFFFF / #C0C0C0
  Fonts: DejaVu Sans Bold (headlines), DejaVu Sans (body)

Fetches photos from Unsplash, composites with dark overlays, renders text.
Uploads to DO Spaces at social/car-detail/{filename}.
"""

import os
import sys
import json
import math
import random
import requests
from pathlib import Path
from io import BytesIO
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

# ── Config ──────────────────────────────────────────────────────────────────
load_dotenv("/root/NEW-AI-PROJECT/.env")
load_dotenv("/root/NEW-AI-PROJECT/purpleocaz-canva-mcp/.env", override=True)

UNSPLASH_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
W, H = 1080, 1080

PHOTO_DIR = Path("/root/NEW-AI-PROJECT/assets/photos/car-detail-social")
OUTPUT_DIR = Path("/root/NEW-AI-PROJECT/outputs/car-detail-social")
PHOTO_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Colours
BG = "#0D0D0D"
RED = "#E02020"
WHITE = "#FFFFFF"
SILVER = "#C0C0C0"
GOLD = "#FFD700"
DARK_GREY = "#1A1A1A"
MID_GREY = "#333333"

# Fonts
FONT_BOLD_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SERIF_BOLD_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"


def font_bold(size):
    return ImageFont.truetype(FONT_BOLD_PATH, size)


def font_reg(size):
    return ImageFont.truetype(FONT_REG_PATH, size)


def font_serif_bold(size):
    return ImageFont.truetype(FONT_SERIF_BOLD_PATH, size)


# ── Unsplash ────────────────────────────────────────────────────────────────
def fetch_photo(query, filename):
    """Fetch a photo from Unsplash and save to PHOTO_DIR. Returns path."""
    path = PHOTO_DIR / filename
    if path.exists():
        print(f"  Photo cached: {filename}")
        return path
    url = "https://api.unsplash.com/search/photos"
    params = {
        "query": query,
        "per_page": 1,
        "orientation": "squarish",
        "client_id": UNSPLASH_KEY,
    }
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("results"):
        print(f"  WARNING: No Unsplash results for '{query}', using fallback")
        # Create a dark gradient fallback
        img = Image.new("RGB", (W, H), BG)
        img.save(path, "PNG")
        return path
    photo_url = data["results"][0]["urls"]["regular"]
    img_resp = requests.get(photo_url, timeout=30)
    img_resp.raise_for_status()
    img = Image.open(BytesIO(img_resp.content)).convert("RGB")
    img = img.resize((W, H), Image.LANCZOS)
    img.save(path, "PNG")
    print(f"  Fetched: {filename}")
    return path


# ── Drawing helpers ─────────────────────────────────────────────────────────
def new_canvas():
    return Image.new("RGB", (W, H), BG)


def dark_overlay(img, alpha=0.65):
    """Apply dark overlay to photo."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, int(255 * alpha)))
    base = img.convert("RGBA")
    base.paste(overlay, (0, 0), overlay)
    return base.convert("RGB")


def draw_pill(draw, x, y, text, bg_color=RED, text_color=WHITE, font_size=22, padding_x=20, padding_y=8):
    """Draw a pill/badge shape with text."""
    f = font_bold(font_size)
    bbox = draw.textbbox((0, 0), text, font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    rx = x - tw // 2 - padding_x
    ry = y - padding_y
    rw = tw + padding_x * 2
    rh = th + padding_y * 2
    draw.rounded_rectangle([rx, ry, rx + rw, ry + rh], radius=rh // 2, fill=bg_color)
    draw.text((x - tw // 2, y), text, font=f, fill=text_color)
    return rh


def draw_button(draw, cx, y, text, bg_color=RED, text_color=WHITE, font_size=24, padding_x=40, padding_y=14):
    """Draw a button centred at cx."""
    f = font_bold(font_size)
    bbox = draw.textbbox((0, 0), text, font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    rx = cx - tw // 2 - padding_x
    ry = y
    rw = tw + padding_x * 2
    rh = th + padding_y * 2
    draw.rounded_rectangle([rx, ry, rx + rw, ry + rh], radius=8, fill=bg_color)
    draw.text((cx - tw // 2, y + padding_y), text, font=f, fill=text_color)
    return rh


def draw_centered(draw, y, text, font, fill=WHITE):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text((W // 2 - tw // 2, y), text, font=font, fill=fill)


def draw_left(draw, x, y, text, font, fill=WHITE):
    draw.text((x, y), text, font=font, fill=fill)


def contact_footer(draw, y=1010):
    f = font_reg(16)
    text = "+1 (555) 000-0000  |  www.yourstudio.com"
    draw_centered(draw, y, text, f, SILVER)


def studio_name_top(draw, y=30, size=18):
    f = font_bold(size)
    draw_centered(draw, y, "YOUR STUDIO NAME", f, WHITE)


def top_bar(draw, height=12, color=RED):
    draw.rectangle([0, 0, W, height], fill=color)


def bottom_bar(draw, height=12, color=RED):
    draw.rectangle([0, H - height, W, H], fill=color)


# ── POST BUILDERS ───────────────────────────────────────────────────────────

def post_01():
    """Premium Detailing Services"""
    photo = fetch_photo("car detailing professional studio", "post_01_photo.png")
    img = dark_overlay(Image.open(photo))
    draw = ImageDraw.Draw(img)
    top_bar(draw)
    studio_name_top(draw, y=30)
    draw_centered(draw, 120, "PREMIUM", font_bold(72), WHITE)
    draw_centered(draw, 210, "DETAILING SERVICES", font_bold(48), RED)
    draw_pill(draw, W // 2, 310, "OUR SERVICES", RED, WHITE, 20)
    services = ["Standard Wash", "Interior Detail", "Paint Correction", "Ceramic Coating"]
    y = 380
    for s in services:
        draw_centered(draw, y, f"|  {s}  |", font_reg(26), SILVER)
        y += 50
    draw.line([W // 2 - 100, y + 10, W // 2 + 100, y + 10], fill=RED, width=2)
    draw_button(draw, W // 2, y + 40, "BOOK NOW  \u2192")
    contact_footer(draw, y=H - 60)
    img.save(OUTPUT_DIR / "post_01.png")


def post_02():
    """Ceramic Coating"""
    photo = fetch_photo("ceramic coating car paint shiny", "post_02_photo.png")
    img = dark_overlay(Image.open(photo), 0.6)
    draw = ImageDraw.Draw(img)
    # Red parallelogram stripe
    points = [(0, 440), (W, 380), (W, 560), (0, 620)]
    draw.polygon(points, fill=RED)
    draw_centered(draw, 120, "CERAMIC COATING", font_bold(56), WHITE)
    draw_centered(draw, 200, "The ultimate paint protection", font_reg(28), SILVER)
    draw_pill(draw, W // 2, 480, "STARTING FROM $499", RED, WHITE, 28)
    details = ["Multi-layer nano coating", "5+ years protection", "Hydrophobic finish"]
    y = 660
    for d in details:
        draw_centered(draw, y, d, font_reg(24), SILVER)
        y += 40
    draw_button(draw, W // 2, 820, "BOOK TODAY")
    contact_footer(draw)


    img.save(OUTPUT_DIR / "post_02.png")


def post_03():
    """Interior Detailing"""
    photo = fetch_photo("car interior detailing luxury", "post_03_photo.png")
    img = dark_overlay(Image.open(photo), 0.7)
    draw = ImageDraw.Draw(img)
    # Giant watermark
    wm_font = font_bold(140)
    wm_bbox = draw.textbbox((0, 0), "INTERIOR", font=wm_font)
    wm_w = wm_bbox[2] - wm_bbox[0]
    # Draw very faint watermark
    wm_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wm_draw = ImageDraw.Draw(wm_layer)
    wm_draw.text((W // 2 - wm_w // 2, 350), "INTERIOR", font=wm_font, fill=(255, 255, 255, 25))
    img = Image.alpha_composite(img.convert("RGBA"), wm_layer).convert("RGB")
    draw = ImageDraw.Draw(img)
    # Red header
    draw.rectangle([0, 0, W, 70], fill=RED)
    draw_centered(draw, 18, "YOUR STUDIO NAME", font_bold(28), WHITE)
    draw_centered(draw, 130, "INTERIOR", font_bold(64), WHITE)
    draw_centered(draw, 210, "DETAILING", font_bold(64), WHITE)
    bullets = ["Deep vacuum & extraction", "Leather conditioning", "Dashboard & trim restoration", "Odour elimination"]
    y = 340
    for b in bullets:
        draw.ellipse([100, y + 8, 116, y + 24], fill=RED)
        draw_left(draw, 130, y, b, font_reg(26), WHITE)
        y += 55
    contact_footer(draw)
    img.save(OUTPUT_DIR / "post_03.png")


def post_04():
    """Paint Correction — split layout"""
    photo = fetch_photo("car paint correction polishing", "post_04_photo.png")
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    # Left dark panel
    draw.rectangle([0, 0, 520, H], fill=BG)
    # Red vertical divider
    draw.rectangle([518, 0, 524, H], fill=RED)
    # Right photo
    ph = Image.open(photo).resize((556, H), Image.LANCZOS)
    img.paste(ph, (524, 0))
    draw = ImageDraw.Draw(img)
    # Left panel content
    draw_left(draw, 40, 80, "PAINT", font_bold(56), WHITE)
    draw_left(draw, 40, 155, "CORRECTION", font_bold(56), RED)
    benefits = ["Remove swirl marks & scratches", "Restore factory-fresh gloss", "Increase resale value"]
    y = 300
    for b in benefits:
        draw.ellipse([50, y + 6, 64, y + 20], fill=RED)
        draw_left(draw, 80, y, b, font_reg(22), SILVER)
        y += 55
    draw_button(draw, 260, 700, "GET A QUOTE")
    f = font_reg(16)
    draw_left(draw, 50, 800, "+1 (555) 000-0000", f, SILVER)
    draw_left(draw, 50, 830, "www.yourstudio.com", f, SILVER)
    img.save(OUTPUT_DIR / "post_04.png")


def post_05():
    """Detailing Packages — no photo"""
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    draw_centered(draw, 40, "CHOOSE YOUR", font_bold(42), SILVER)
    draw_centered(draw, 95, "PACKAGE", font_bold(60), WHITE)
    draw.line([W // 2 - 80, 170, W // 2 + 80, 170], fill=RED, width=3)

    packages = [
        ("BASIC", "$79", ["Exterior Wash", "Hand Dry", "Tyre Shine"]),
        ("STANDARD", "$149", ["+ Interior Vacuum", "+ Windows", "+ Wipe Down"]),
        ("PREMIUM", "$249", ["+ Polish & Wax", "+ Engine Bay", "+ Ceramic Spray"]),
    ]
    box_w = 300
    gap = 30
    start_x = (W - (box_w * 3 + gap * 2)) // 2
    y_top = 210
    box_h = 580

    for i, (name, price, items) in enumerate(packages):
        x = start_x + i * (box_w + gap)
        # Outlined box
        draw.rounded_rectangle([x, y_top, x + box_w, y_top + box_h], radius=8, outline=RED, width=2)
        # Header area
        draw.rectangle([x + 1, y_top + 1, x + box_w - 1, y_top + 70], fill=RED)
        nf = font_bold(28)
        nbbox = draw.textbbox((0, 0), name, font=nf)
        nw = nbbox[2] - nbbox[0]
        draw.text((x + box_w // 2 - nw // 2, y_top + 18), name, font=nf, fill=WHITE)
        # Price
        pf = font_bold(48)
        pbbox = draw.textbbox((0, 0), price, font=pf)
        pw = pbbox[2] - pbbox[0]
        draw.text((x + box_w // 2 - pw // 2, y_top + 95), price, font=pf, fill=WHITE)
        # Items
        iy = y_top + 180
        for item in items:
            itemf = font_reg(20)
            ibbox = draw.textbbox((0, 0), item, font=itemf)
            iw = ibbox[2] - ibbox[0]
            draw.text((x + box_w // 2 - iw // 2, iy), item, font=itemf, fill=SILVER)
            iy += 40
            # Separator
            draw.line([x + 30, iy, x + box_w - 30, iy], fill=MID_GREY, width=1)
            iy += 20

    draw_button(draw, W // 2, 850, "BOOK NOW")
    contact_footer(draw, 960)
    img.save(OUTPUT_DIR / "post_05.png")


def post_06():
    """Limited Time Offer"""
    photo = fetch_photo("luxury car close up detail", "post_06_photo.png")
    img = dark_overlay(Image.open(photo), 0.65)
    draw = ImageDraw.Draw(img)
    draw_pill(draw, W // 2, 100, "THIS MONTH ONLY", RED, WHITE, 24)
    draw_centered(draw, 220, "20% OFF", font_bold(100), WHITE)
    draw_centered(draw, 370, "Full Interior & Exterior Detail", font_reg(30), SILVER)
    draw.line([W // 2 - 120, 430, W // 2 + 120, 430], fill=RED, width=3)
    draw_centered(draw, 460, "Professional hand wash, clay bar,", font_reg(24), SILVER)
    draw_centered(draw, 500, "polish, wax & full interior clean", font_reg(24), SILVER)
    draw_button(draw, W // 2, 620, "BOOK NOW")
    draw_centered(draw, 760, "Offer expires March 31, 2026", font_reg(20), SILVER)
    contact_footer(draw)
    img.save(OUTPUT_DIR / "post_06.png")


def post_07():
    """Free Quote — no photo"""
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    top_bar(draw)
    studio_name_top(draw, 30)
    draw_centered(draw, 140, "GET YOUR", font_bold(48), SILVER)
    draw_centered(draw, 210, "FREE QUOTE", font_bold(72), WHITE)
    draw.line([W // 2 - 100, 300, W // 2 + 100, 300], fill=RED, width=3)
    checks = [
        "No obligation",
        "Same day response",
        "Competitive pricing",
    ]
    y = 350
    for c in checks:
        cf = font_reg(30)
        draw_left(draw, 280, y, f"\u2713  {c}", cf, RED)
        y += 60
    draw_centered(draw, 600, "+1 (555) 000-0000", font_bold(48), WHITE)
    draw_button(draw, W // 2, 720, "CALL OR TEXT TODAY", RED, WHITE, 28)
    contact_footer(draw, 950)
    bottom_bar(draw)
    img.save(OUTPUT_DIR / "post_07.png")


def post_08():
    """Refer a Friend"""
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    # Diagonal red accent lines
    for offset in range(-200, 1200, 80):
        draw.line([(offset, 0), (offset - 300, H)], fill="#1A0808", width=2)
    studio_name_top(draw, 40)
    draw.line([W // 2 - 80, 80, W // 2 + 80, 80], fill=RED, width=3)
    draw_centered(draw, 160, "REFER A", font_bold(52), SILVER)
    draw_centered(draw, 230, "FRIEND", font_bold(72), WHITE)
    draw_centered(draw, 380, "$25 OFF", font_bold(80), RED)
    draw_centered(draw, 490, "your next detail", font_bold(36), WHITE)
    draw.line([W // 2 - 150, 560, W // 2 + 150, 560], fill=RED, width=2)
    draw_centered(draw, 600, "When your referral books", font_reg(26), SILVER)
    draw_centered(draw, 640, "any full detail service", font_reg(26), SILVER)
    draw_centered(draw, 740, "Mention this post when booking", font_reg(22), MID_GREY)
    contact_footer(draw)
    img.save(OUTPUT_DIR / "post_08.png")


def post_09():
    """Seasonal Special"""
    photo = fetch_photo("car driving summer road", "post_09_photo.png")
    img = dark_overlay(Image.open(photo), 0.65)
    draw = ImageDraw.Draw(img)
    top_bar(draw)
    draw_centered(draw, 80, "SUMMER", font_bold(80), WHITE)
    draw_centered(draw, 175, "READY?", font_bold(80), RED)
    draw_centered(draw, 290, "Get your car looking its best", font_reg(28), SILVER)
    draw.line([W // 2 - 100, 340, W // 2 + 100, 340], fill=RED, width=2)
    services = ["Full exterior wash & wax", "Interior deep clean", "AC system refresh", "UV paint protection"]
    y = 380
    for s in services:
        draw.ellipse([320, y + 8, 336, y + 24], fill=RED)
        draw_centered(draw, y, f"   {s}", font_reg(26), WHITE)
        y += 50
    draw_button(draw, W // 2, 650, "BOOK NOW")
    contact_footer(draw, 800)
    img.save(OUTPUT_DIR / "post_09.png")


def post_10():
    """5 Star Review — no photo"""
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    draw.line([W // 2 - 200, 80, W // 2 + 200, 80], fill=RED, width=2)
    # Stars
    stars = "\u2605 \u2605 \u2605 \u2605 \u2605"
    draw_centered(draw, 110, stars, font_bold(60), GOLD)
    draw.line([W // 2 - 200, 200, W // 2 + 200, 200], fill=RED, width=2)
    # Quote
    quote_lines = [
        '"The best detail I\'ve ever had.',
        "My car looks brand new \u2014",
        'I couldn\'t be happier!"',
    ]
    y = 280
    for line in quote_lines:
        draw_centered(draw, y, line, font_reg(30), WHITE)
        y += 50
    draw_centered(draw, 520, "\u2014 [Customer Name], [City]", font_reg(24), SILVER)
    draw.line([W // 2 - 150, 600, W // 2 + 150, 600], fill=RED, width=3)
    draw_centered(draw, 660, "YOUR STUDIO NAME", font_bold(36), WHITE)
    draw_centered(draw, 720, "Professional Car Detailing", font_reg(22), SILVER)
    contact_footer(draw, 850)
    img.save(OUTPUT_DIR / "post_10.png")


def post_11():
    """Before & After — Cinematic (monochromatic, no red)"""
    photo = fetch_photo("car front view clean white", "post_11_photo.png")
    car_img = Image.open(photo).resize((W, H), Image.LANCZOS)
    img = Image.new("RGB", (W, H), "#1C1C1C")

    # Place car image in middle band
    car_region_top = 180
    car_region_bottom = 900
    car_h = car_region_bottom - car_region_top
    car_cropped = car_img.resize((W, car_h), Image.LANCZOS)

    # Left half desaturated
    left = car_cropped.crop((0, 0, W // 2, car_h)).convert("L").convert("RGB")
    # Darken left side slightly
    enhancer = ImageEnhance.Brightness(left)
    left = enhancer.enhance(0.7)

    # Right half normal/bright
    right = car_cropped.crop((W // 2, 0, W, car_h))
    enhancer = ImageEnhance.Brightness(right)
    right = enhancer.enhance(1.1)
    enhancer = ImageEnhance.Color(right)
    right = enhancer.enhance(1.2)

    img.paste(left, (0, car_region_top))
    img.paste(right, (W // 2, car_region_top))

    draw = ImageDraw.Draw(img)

    # Thin white vertical line down centre
    draw.line([(W // 2, car_region_top), (W // 2, car_region_bottom)], fill=WHITE, width=2)

    # Dark header panel
    draw.rectangle([0, 0, W, car_region_top], fill="#1C1C1C")
    draw_centered(draw, 30, "Car Detailing", font_serif_bold(48), WHITE)
    # BEFORE / AFTER labels
    bf = font_bold(22)
    draw_left(draw, 80, 120, "BEFORE", bf, SILVER)
    # Vertical divider in header
    draw.line([(W // 2, 110), (W // 2, 160)], fill=SILVER, width=1)
    abbox = draw.textbbox((0, 0), "AFTER", font=bf)
    aw = abbox[2] - abbox[0]
    draw.text((W - 80 - aw, 120), "AFTER", font=bf, fill=WHITE)

    # Bottom
    draw.rectangle([0, car_region_bottom, W, H], fill="#1C1C1C")
    draw_centered(draw, car_region_bottom + 40, "@yourstudioname", font_reg(22), SILVER)

    img.save(OUTPUT_DIR / "post_11.png")


def post_12():
    """Customer Spotlight"""
    photo = fetch_photo("happy person car clean smiling", "post_12_photo.png")
    ph = Image.open(photo).resize((W, H), Image.LANCZOS)
    img = new_canvas()
    # Photo top 60%
    photo_h = int(H * 0.6)
    photo_cropped = ph.crop((0, 0, W, photo_h))
    # Slight dark gradient at bottom of photo
    gradient = Image.new("RGBA", (W, photo_h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gradient)
    for i in range(150):
        alpha = int(255 * (i / 150) * 0.7)
        gd.line([(0, photo_h - 150 + i), (W, photo_h - 150 + i)], fill=(0, 0, 0, alpha))
    photo_rgba = photo_cropped.convert("RGBA")
    photo_rgba = Image.alpha_composite(photo_rgba, gradient)
    img.paste(photo_rgba.convert("RGB"), (0, 0))

    draw = ImageDraw.Draw(img)
    # Dark panel bottom 40%
    draw.rectangle([0, photo_h, W, H], fill=BG)
    draw_pill(draw, W // 2, photo_h - 50, "ANOTHER HAPPY CLIENT", RED)
    draw_centered(draw, photo_h + 20, "\u2605 \u2605 \u2605 \u2605 \u2605", font_bold(36), GOLD)
    draw_centered(draw, photo_h + 80, '"Absolutely incredible work!', font_reg(24), WHITE)
    draw_centered(draw, photo_h + 115, 'My car has never looked this good."', font_reg(24), WHITE)
    draw_centered(draw, photo_h + 170, "\u2014 [Customer Name]", font_reg(20), SILVER)
    draw_centered(draw, H - 50, "YOUR STUDIO NAME", font_bold(22), WHITE)
    img.save(OUTPUT_DIR / "post_12.png")


def post_13():
    """By The Numbers — no photo"""
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    top_bar(draw)
    draw_centered(draw, 60, "WHY CHOOSE US?", font_bold(48), WHITE)
    draw.line([W // 2 - 80, 130, W // 2 + 80, 130], fill=RED, width=3)

    stats = [
        ("500+", "Satisfied Clients"),
        ("5\u2605", "Average Rating"),
        ("10+", "Years Experience"),
    ]
    y = 200
    for num, label in stats:
        draw_centered(draw, y, num, font_bold(80), RED)
        draw_centered(draw, y + 95, label, font_reg(28), SILVER)
        y += 200
        if y < 800:
            draw.line([W // 2 - 120, y - 30, W // 2 + 120, y - 30], fill=MID_GREY, width=2)

    draw_centered(draw, 860, "Professional. Reliable. Exceptional.", font_bold(26), WHITE)
    contact_footer(draw, 950)
    bottom_bar(draw)
    img.save(OUTPUT_DIR / "post_13.png")


def post_14():
    """Did You Know — split layout"""
    photo = fetch_photo("car paint swirl marks close up", "post_14_photo.png")
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    # Left dark panel
    draw.rectangle([0, 0, 540, H], fill=BG)
    # Right photo
    ph = Image.open(photo).resize((540, H), Image.LANCZOS)
    img.paste(ph, (540, 0))
    draw = ImageDraw.Draw(img)
    # Slight overlay on right
    overlay = Image.new("RGBA", (540, H), (0, 0, 0, 80))
    img_rgba = img.convert("RGBA")
    img_rgba.paste(overlay, (540, 0), overlay)
    img = img_rgba.convert("RGB")
    draw = ImageDraw.Draw(img)

    draw_pill(draw, 270, 80, "DID YOU KNOW?", RED, WHITE, 22)
    # Fact text
    lines = [
        "Regular detailing",
        "can increase your",
        "car's resale value",
        "by up to",
    ]
    y = 200
    for line in lines:
        draw_left(draw, 50, y, line, font_reg(28), SILVER)
        y += 42
    draw_left(draw, 50, y + 10, "15%", font_bold(80), WHITE)
    draw.line([50, y + 110, 200, y + 110], fill=RED, width=3)
    draw_left(draw, 50, y + 140, "Book a detail today \u2192", font_bold(24), RED)
    contact_footer(draw, H - 50)
    img.save(OUTPUT_DIR / "post_14.png")


def post_15():
    """Why Ceramic Coating — no photo"""
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    top_bar(draw)
    draw_centered(draw, 60, "3 REASONS TO GET", font_bold(40), SILVER)
    draw_centered(draw, 120, "CERAMIC COATING", font_bold(52), WHITE)
    draw.line([W // 2 - 100, 195, W // 2 + 100, 195], fill=RED, width=3)

    reasons = [
        ("1", "Protects against UV,\ndirt and scratches"),
        ("2", "Makes cleaning\n10x easier"),
        ("3", "Keeps your car looking\nnew for years"),
    ]
    y = 250
    for num, text in reasons:
        # Red circle with number
        cx = 150
        draw.ellipse([cx - 30, y - 5, cx + 30, y + 55], fill=RED)
        nf = font_bold(32)
        nbbox = draw.textbbox((0, 0), num, font=nf)
        nw = nbbox[2] - nbbox[0]
        draw.text((cx - nw // 2, y + 5), num, font=nf, fill=WHITE)
        # Text
        lines = text.split("\n")
        ty = y + 5
        for line in lines:
            draw_left(draw, 210, ty, line, font_reg(28), WHITE)
            ty += 38
        y += 170

    draw_button(draw, W // 2, 820, "PROTECT YOUR PAINT TODAY")
    contact_footer(draw, 950)
    bottom_bar(draw)
    img.save(OUTPUT_DIR / "post_15.png")


def post_16():
    """Weekly Tip — no photo"""
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    top_bar(draw)
    draw_pill(draw, W // 2, 80, "#TIP OF THE WEEK", RED, WHITE, 24)
    draw.line([W // 2 - 120, 150, W // 2 + 120, 150], fill=MID_GREY, width=1)
    # Large tip text
    tip_lines = [
        "Always wash your",
        "car in the shade \u2014",
        "direct sunlight",
        "causes water spots",
    ]
    y = 220
    for line in tip_lines:
        draw_centered(draw, y, line, font_bold(40), WHITE)
        y += 60
    draw.line([W // 2 - 80, y + 20, W // 2 + 80, y + 20], fill=RED, width=3)
    draw_centered(draw, y + 60, "Follow for weekly detailing tips", font_reg(24), SILVER)
    draw_centered(draw, y + 120, "@yourstudioname", font_bold(30), WHITE)
    bottom_bar(draw)
    img.save(OUTPUT_DIR / "post_16.png")


def post_17():
    """Before You Sell"""
    photo = fetch_photo("car for sale sign dealership", "post_17_photo.png")
    img = dark_overlay(Image.open(photo), 0.7)
    draw = ImageDraw.Draw(img)
    top_bar(draw)
    draw_centered(draw, 80, "THINKING OF", font_bold(44), SILVER)
    draw_centered(draw, 140, "SELLING YOUR CAR?", font_bold(52), WHITE)
    draw.line([W // 2 - 120, 220, W // 2 + 120, 220], fill=RED, width=3)
    # Highlight text
    draw_centered(draw, 280, "A professional detail could add", font_reg(26), SILVER)
    draw_centered(draw, 330, "$500 \u2013 $2,000", font_bold(60), RED)
    draw_centered(draw, 410, "to your sale price", font_reg(26), SILVER)
    # Bullets
    bullets = ["Paint correction", "Deep interior clean", "Odour removal"]
    y = 510
    for b in bullets:
        draw.ellipse([320, y + 8, 336, y + 24], fill=RED)
        draw_left(draw, 350, y, b, font_reg(26), WHITE)
        y += 50
    draw_button(draw, W // 2, 720, "BOOK NOW")
    contact_footer(draw)
    img.save(OUTPUT_DIR / "post_17.png")


def post_18():
    """About Us — split layout"""
    photo = fetch_photo("car detailing studio professional", "post_18_photo.png")
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    # Left dark panel
    draw.rectangle([0, 0, 540, H], fill=BG)
    # Right photo
    ph = Image.open(photo).resize((540, H), Image.LANCZOS)
    img.paste(ph, (540, 0))
    # Slight overlay on right photo
    overlay_img = Image.new("RGBA", (540, H), (0, 0, 0, 100))
    img_rgba = img.convert("RGBA")
    img_rgba.paste(overlay_img, (540, 0), overlay_img)
    img = img_rgba.convert("RGB")
    draw = ImageDraw.Draw(img)

    draw_pill(draw, 270, 80, "WHO WE ARE", RED, WHITE, 22)
    draw_left(draw, 50, 170, "YOUR", font_bold(48), WHITE)
    draw_left(draw, 50, 230, "STUDIO", font_bold(48), WHITE)
    draw_left(draw, 50, 290, "NAME", font_bold(48), RED)
    draw.line([50, 360, 200, 360], fill=RED, width=3)
    props = [
        "Fully insured & certified",
        "Mobile & studio service",
        "100% satisfaction guaranteed",
    ]
    y = 400
    for p in props:
        draw_left(draw, 50, y, f"\u2713  {p}", font_reg(22), WHITE)
        y += 50
    draw.line([50, y + 10, 480, y + 10], fill=MID_GREY, width=1)
    draw_left(draw, 50, y + 30, "+1 (555) 000-0000", font_reg(18), SILVER)
    draw_left(draw, 50, y + 60, "hello@yourstudio.com", font_reg(18), SILVER)
    draw_left(draw, 50, y + 90, "www.yourstudio.com", font_reg(18), SILVER)
    img.save(OUTPUT_DIR / "post_18.png")


def post_19():
    """Follow Us — no photo"""
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    top_bar(draw)
    draw_centered(draw, 80, "FOLLOW US", font_bold(60), WHITE)
    draw_centered(draw, 160, "FOR", font_bold(60), RED)
    draw.line([W // 2 - 80, 240, W // 2 + 80, 240], fill=RED, width=3)
    items = ["Detailing tips", "Before & afters", "Special offers", "Behind the scenes"]
    y = 290
    for item in items:
        draw.ellipse([300, y + 8, 316, y + 24], fill=RED)
        draw_left(draw, 340, y, item, font_reg(30), WHITE)
        y += 55
    draw_centered(draw, 570, "@yourstudioname", font_bold(44), WHITE)
    draw.line([W // 2 - 150, 640, W // 2 + 150, 640], fill=MID_GREY, width=1)
    # Platform text
    platforms = "Instagram  |  Facebook  |  TikTok"
    draw_centered(draw, 670, platforms, font_reg(24), SILVER)
    draw_pill(draw, W // 2, 770, "NEW POSTS EVERY WEEK", RED, WHITE, 22)
    contact_footer(draw, 920)
    bottom_bar(draw)
    img.save(OUTPUT_DIR / "post_19.png")


def post_20():
    """Contact Card — clean professional"""
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    top_bar(draw, 16)
    bottom_bar(draw, 16)
    # Logo placeholder
    draw_centered(draw, 60, "YOUR STUDIO", font_bold(36), WHITE)
    draw_centered(draw, 105, "NAME", font_bold(36), RED)
    draw.line([W // 2 - 80, 165, W // 2 + 80, 165], fill=RED, width=3)
    draw_centered(draw, 200, "GET IN TOUCH", font_bold(52), WHITE)
    draw.line([W // 2 - 100, 270, W // 2 + 100, 270], fill=MID_GREY, width=1)

    contacts = [
        ("\U0001F4DE", "+1 (555) 000-0000"),
        ("\U0001F4E7", "hello@yourstudio.com"),
        ("\U0001F310", "www.yourstudio.com"),
        ("\U0001F4CD", "123 Main St, Your City, State"),
    ]
    y = 330
    for icon, text in contacts:
        # Red icon background circle
        draw.ellipse([260, y, 300, y + 40], fill=RED)
        icon_f = font_reg(20)
        draw.text((269, y + 8), icon, font=icon_f, fill=WHITE)
        draw_left(draw, 320, y + 5, text, font_reg(26), WHITE)
        y += 80
        if y < 650:
            draw.line([260, y - 15, W - 260, y - 15], fill=MID_GREY, width=1)

    draw_pill(draw, W // 2, 710, "OPEN 7 DAYS", RED, WHITE, 24)
    draw_centered(draw, 810, "Mon\u2013Fri: 8am\u20136pm", font_reg(22), SILVER)
    draw_centered(draw, 845, "Sat\u2013Sun: 9am\u20134pm", font_reg(22), SILVER)
    img.save(OUTPUT_DIR / "post_20.png")


# ── Main ────────────────────────────────────────────────────────────────────
POST_BUILDERS = [
    post_01, post_02, post_03, post_04, post_05,
    post_06, post_07, post_08, post_09, post_10,
    post_11, post_12, post_13, post_14, post_15,
    post_16, post_17, post_18, post_19, post_20,
]

POST_NAMES = [
    "Premium Detailing Services",
    "Ceramic Coating",
    "Interior Detailing",
    "Paint Correction",
    "Detailing Packages",
    "Limited Time Offer",
    "Free Quote",
    "Refer a Friend",
    "Seasonal Special",
    "5 Star Review",
    "Before & After — Cinematic",
    "Customer Spotlight",
    "By The Numbers",
    "Did You Know",
    "Why Ceramic Coating",
    "Weekly Tip",
    "Before You Sell",
    "About Us",
    "Follow Us",
    "Contact Card",
]


def build_all():
    print(f"Building {len(POST_BUILDERS)} posts...")
    for i, builder in enumerate(POST_BUILDERS):
        num = i + 1
        print(f"\n[{num:02d}/20] {POST_NAMES[i]}")
        builder()
        print(f"  Saved: post_{num:02d}.png")
    print(f"\nAll 20 posts saved to {OUTPUT_DIR}")


def build_preview_grid():
    """Build 4x5 grid of all 20 posts at 5400x5400."""
    print("\nBuilding preview grid (4x5, 5400x5400)...")
    cols, rows = 4, 5
    grid_w, grid_h = 5400, 5400
    thumb_w = grid_w // cols  # 1350
    thumb_h = grid_h // rows  # 1080
    grid = Image.new("RGB", (grid_w, grid_h), BG)

    for i in range(20):
        path = OUTPUT_DIR / f"post_{i + 1:02d}.png"
        thumb = Image.open(path).resize((thumb_w, thumb_h), Image.LANCZOS)
        col = i % cols
        row = i // cols
        grid.paste(thumb, (col * thumb_w, row * thumb_h))

    grid_path = OUTPUT_DIR / "preview_grid.png"
    grid.save(grid_path, "PNG")
    print(f"Preview grid saved: {grid_path}")
    return grid_path


def upload_to_spaces():
    """Upload all PNGs to DO Spaces."""
    import boto3
    from botocore.config import Config as BotoConfig

    key = os.getenv("DO_SPACES_KEY")
    secret = os.getenv("DO_SPACES_SECRET")
    bucket = os.getenv("DO_SPACES_BUCKET", "purpleocaz-assets")
    region = os.getenv("DO_SPACES_REGION", "lon1")
    endpoint = os.getenv("DO_SPACES_ENDPOINT", f"https://{region}.digitaloceanspaces.com")

    session = boto3.session.Session()
    client = session.client(
        "s3",
        region_name=region,
        endpoint_url=endpoint,
        aws_access_key_id=key,
        aws_secret_access_key=secret,
    )

    files = sorted(OUTPUT_DIR.glob("post_*.png")) + [OUTPUT_DIR / "preview_grid.png"]
    results = []
    for f in files:
        if not f.exists():
            continue
        s3_key = f"social/car-detail/{f.name}"
        print(f"  Uploading {f.name} -> {s3_key}")
        client.put_object(
            Bucket=bucket,
            Key=s3_key,
            Body=f.read_bytes(),
            ContentType="image/png",
            ACL="public-read",
        )
        url = f"https://{bucket}.{region}.digitaloceanspaces.com/{s3_key}"
        size_kb = f.stat().st_size / 1024
        results.append((f.name, size_kb, url))

    return results


if __name__ == "__main__":
    build_all()
    build_preview_grid()

    if "--upload" in sys.argv:
        print("\nUploading to DO Spaces...")
        results = upload_to_spaces()
        print(f"\n{len(results)} files uploaded.")
        for name, size, url in results:
            print(f"  {name}: {size:.0f}KB -> {url}")
