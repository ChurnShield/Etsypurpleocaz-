#!/usr/bin/env python3
"""
Barbershop Instagram Posts — 12 x 1080x1080px square posts.
Design system: #1A1A1A bg, #C9A96E gold, #FFFFFF white, #888888 grey.

Posts:
 01 — Brand Welcome
 02 — Services Menu
 03 — Book Now CTA
 04 — New Client Offer
 05 — Customer Testimonial
 06 — Tip of the Week
 07 — Before & After teaser
 08 — Meet the Barber
 09 — Opening Hours
 10 — Loyalty Program
 11 — Referral Offer
 12 — Seasonal Promo
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import boto3
from dotenv import load_dotenv

PROJECT_ROOT = Path("/root/NEW-AI-PROJECT")
OUTPUT_DIR   = PROJECT_ROOT / "outputs" / "barbershop" / "instagram"
PHOTO_DIR    = PROJECT_ROOT / "assets" / "photos" / "barbershop_haircut_fade_dark"
TOOLS_DIR    = PROJECT_ROOT / "assets" / "photos" / "barber_tools_scissors_razor"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FONT_BOLD    = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG     = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SERIF   = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_SERIFB  = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

BG      = (26, 26, 26)
DARK    = (10, 10, 10)
PANEL   = (38, 38, 38)
GOLD    = (201, 169, 110)
WHITE   = (255, 255, 255)
GREY    = (136, 136, 136)
CREAM   = (255, 253, 245)
DARK_TEXT = (26, 26, 26)

W = H = 1080


# ─── Helpers ──────────────────────────────────────────────────────────────────

def font(size, bold=False, serif=False, serifbold=False):
    if serifbold:
        return ImageFont.truetype(FONT_SERIFB, size)
    if serif:
        return ImageFont.truetype(FONT_SERIF, size)
    if bold:
        return ImageFont.truetype(FONT_BOLD, size)
    return ImageFont.truetype(FONT_REG, size)


def cx(draw, y, text, fill, f, w=W):
    bb = draw.textbbox((0, 0), text, font=f)
    tw = bb[2] - bb[0]
    draw.text(((w - tw) // 2, y), text, fill=fill, font=f)


def gold_bar(draw, y, thickness=3, x0=0, x1=W):
    draw.rectangle([x0, y, x1, y + thickness], fill=GOLD)


def gold_border(draw, margin=20, width=3):
    draw.rectangle([margin, margin, W - margin, H - margin],
                   outline=GOLD, width=width)


def scissors_icon(draw, x, y, size=30):
    """Simple X scissors at (x,y) centre."""
    s = size
    draw.line([(x - s, y - s // 2), (x + s, y + s // 2)], fill=GOLD, width=6)
    draw.line([(x + s, y - s // 2), (x - s, y + s // 2)], fill=GOLD, width=6)
    for ex, ey in [(x - s, y - s // 2), (x + s, y - s // 2),
                   (x - s, y + s // 2), (x + s, y + s // 2)]:
        draw.ellipse([ex - 8, ey - 8, ex + 8, ey + 8], outline=GOLD, width=3)


def load_photo(path, w, h, alpha=140):
    if path and path.exists():
        p = Image.open(path).convert("RGBA")
        pw, ph = p.size
        ratio = w / h
        if pw / ph > ratio:
            crop_w = int(ph * ratio)
            p = p.crop(((pw - crop_w) // 2, 0, (pw - crop_w) // 2 + crop_w, ph))
        else:
            crop_h = int(pw / ratio)
            p = p.crop((0, (ph - crop_h) // 2, pw, (ph - crop_h) // 2 + crop_h))
        p = p.resize((w, h), Image.LANCZOS)
        ov = Image.new("RGBA", (w, h), (0, 0, 0, alpha))
        p = Image.alpha_composite(p, ov)
        return p.convert("RGB")
    return Image.new("RGB", (w, h), BG)


def standard_header(draw, img, title_line1, title_line2=None,
                    photo_path=None, header_h=320, photo_alpha=150):
    """Dark photo/gradient header with shop name."""
    if photo_path and photo_path.exists():
        ph = load_photo(photo_path, W, header_h, alpha=photo_alpha)
        img.paste(ph, (0, 0))
        d = ImageDraw.Draw(img)
    else:
        draw.rectangle([0, 0, W, header_h], fill=DARK)
    gold_bar(draw, 0, thickness=5)
    gold_bar(draw, header_h - 5, thickness=5)

    # Shop name top-left
    draw.text((40, 28), "YOUR BARBERSHOP", fill=GOLD, font=font(18, bold=True))
    draw.text((40, 54), "EST. 2015", fill=GREY, font=font(12))

    # Title
    y = header_h // 2 - (30 if title_line2 else 20)
    cx(draw, y, title_line1, WHITE, font(48, bold=True))
    if title_line2:
        cx(draw, y + 60, title_line2, GOLD, font(28, bold=True))


def save(img, name):
    out = OUTPUT_DIR / name
    img.save(str(out), "PNG")
    print(f"  Saved: {out.name}")
    return out


# ─── POST 01 — Brand Welcome ───────────────────────────────────────────────────

def post_01_brand_welcome():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Full-bleed dark background with diagonal gold stripe accents
    for i, y in enumerate(range(0, H + 200, 120)):
        draw.line([(0, y), (W, y - 200)], fill=(201, 169, 110, 30), width=1)

    # Thick top/bottom bars
    draw.rectangle([0, 0, W, 8], fill=GOLD)
    draw.rectangle([0, H - 8, W, H], fill=GOLD)

    # Inner border
    gold_border(draw, margin=28, width=2)

    # Scissors motif at top
    scissors_icon(draw, W // 2, 130, size=40)
    gold_bar(draw, 185, thickness=2, x0=W // 2 - 120, x1=W // 2 + 120)

    # Main tagline
    cx(draw, 220, "WHERE EVERY", GREY, font(22, bold=True))
    cx(draw, 270, "CUT TELLS A STORY", WHITE, font(52, bold=True))
    gold_bar(draw, 340, thickness=3, x0=W // 2 - 180, x1=W // 2 + 180)

    # Shop name big
    cx(draw, 375, "YOUR BARBERSHOP", GOLD, font(38, bold=True))
    cx(draw, 430, "N A M E", GREY, font(16, bold=True))

    # Three pillars
    pillars = [
        ("PRECISION", "CUTS"),
        ("CLASSIC", "FADES"),
        ("HOT TOWEL", "SHAVES"),
    ]
    pill_y = 520
    col_w = W // 3
    for i, (l1, l2) in enumerate(pillars):
        x = i * col_w + col_w // 2
        draw.ellipse([x - 44, pill_y - 44, x + 44, pill_y + 44],
                     outline=GOLD, width=2)
        cx_x = i * col_w
        bb1 = draw.textbbox((0, 0), l1, font=font(14, bold=True))
        bb2 = draw.textbbox((0, 0), l2, font=font(12))
        draw.text((x - (bb1[2] - bb1[0]) // 2, pill_y - 16), l1,
                  fill=WHITE, font=font(14, bold=True))
        draw.text((x - (bb2[2] - bb2[0]) // 2, pill_y + 6), l2,
                  fill=GOLD, font=font(12))

    # Dividers between pillars
    for xi in [col_w, col_w * 2]:
        draw.rectangle([xi - 1, 490, xi, 590], fill=GOLD)

    # CTA
    cx(draw, 660, "Book Your Appointment Today", WHITE, font(22))
    cx(draw, 700, "@yourbarbershop  |  www.yourbarbershop.com", GREY, font(14))

    # Hashtags
    cx(draw, 800, "#YourBarbershop  #FreshCut  #BarberLife", GOLD, font(16))
    cx(draw, 840, "#MasterBarber  #MensGrooming  #FadeGame", GREY, font(14))

    # Location
    cx(draw, 920, "📍 123 Main Street, Your City", WHITE, font(16))

    return save(img, "barber_ig_01_brand_welcome.png")


# ─── POST 02 — Services Menu ───────────────────────────────────────────────────

def post_02_services_menu():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, W, 8], fill=GOLD)
    draw.rectangle([0, H - 8, W, H], fill=GOLD)
    gold_border(draw, margin=20, width=2)

    # Header
    scissors_icon(draw, W // 2, 90, size=35)
    cx(draw, 145, "OUR SERVICES", WHITE, font(42, bold=True))
    cx(draw, 200, "YOUR BARBERSHOP NAME", GOLD, font(18, bold=True))
    gold_bar(draw, 238, thickness=2, x0=80, x1=W - 80)

    # Services list
    services = [
        ("Classic Haircut",         "from £18"),
        ("Skin Fade / Taper Fade",  "from £22"),
        ("Beard Trim & Shape",      "from £12"),
        ("Hot Towel Shave",         "from £20"),
        ("Cut & Beard Combo",       "from £30"),
        ("Kid's Cut (under 12)",    "from £14"),
        ("Hair Design / Line-Up",   "from £8"),
        ("Scalp Treatment",         "from £15"),
    ]

    sy = 265
    row_h = 72
    for i, (name, price) in enumerate(services):
        row_y = sy + i * row_h
        # Alternating row tint
        if i % 2 == 0:
            draw.rectangle([38, row_y - 4, W - 38, row_y + row_h - 8],
                           fill=(38, 38, 38))
        # Gold dot
        draw.ellipse([50, row_y + 15, 62, row_y + 27], fill=GOLD)
        draw.text((80, row_y + 8), name, fill=WHITE, font=font(20, bold=True))
        draw.text((80, row_y + 34), "Customisable to your style", fill=GREY, font=font(13))
        # Price right-aligned
        bb = draw.textbbox((0, 0), price, font=font(22, bold=True))
        draw.text((W - 60 - (bb[2] - bb[0]), row_y + 16),
                  price, fill=GOLD, font=font(22, bold=True))

    gold_bar(draw, sy + len(services) * row_h - 2, thickness=2, x0=40, x1=W - 40)
    cx(draw, sy + len(services) * row_h + 14,
       "Prices may vary — DM for a quote", GREY, font(14))

    return save(img, "barber_ig_02_services_menu.png")


# ─── POST 03 — Book Now CTA ────────────────────────────────────────────────────

def post_03_book_now():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Dramatic dark gradient feel — top band
    draw.rectangle([0, 0, W, 360], fill=DARK)
    draw.rectangle([0, 0, W, 6], fill=GOLD)
    draw.rectangle([0, H - 6, W, H], fill=GOLD)

    # Scissors large
    scissors_icon(draw, W // 2, 160, size=70)

    cx(draw, 255, "READY FOR A", GREY, font(24, bold=True))
    cx(draw, 300, "FRESH CUT?", WHITE, font(64, bold=True))

    gold_bar(draw, 382, thickness=3, x0=W // 2 - 200, x1=W // 2 + 200)

    cx(draw, 410, "YOUR BARBERSHOP NAME", GOLD, font(22, bold=True))

    # CTA pill button
    btn_w, btn_h = 500, 72
    bx = (W - btn_w) // 2
    by = 470
    draw.rounded_rectangle([bx, by, bx + btn_w, by + btn_h],
                           radius=btn_h // 2, fill=GOLD)
    cx(draw, by + 18, "BOOK YOUR APPOINTMENT", DARK, font(22, bold=True))

    # Steps
    steps = [
        ("1", "DM us on Instagram"),
        ("2", "Call +1 (555) 000-0000"),
        ("3", "Book at yourbarbershop.com"),
    ]
    step_y = 590
    for num, text in steps:
        draw.ellipse([W // 2 - 250, step_y, W // 2 - 210, step_y + 40],
                     fill=GOLD)
        bb = draw.textbbox((0, 0), num, font=font(18, bold=True))
        draw.text((W // 2 - 240, step_y + 8), num,
                  fill=DARK, font=font(18, bold=True))
        draw.text((W // 2 - 195, step_y + 8), text,
                  fill=WHITE, font=font(18))
        step_y += 65

    # Hours
    gold_bar(draw, 820, thickness=2, x0=80, x1=W - 80)
    cx(draw, 838, "Mon–Fri 9am–8pm  |  Sat 9am–7pm  |  Sun 10am–4pm",
       GREY, font(15))

    # Address + handle
    cx(draw, 900, "123 Main Street, Your City", WHITE, font(16))
    cx(draw, 940, "@yourbarbershop", GOLD, font(18, bold=True))

    return save(img, "barber_ig_03_book_now.png")


# ─── POST 04 — New Client Offer ────────────────────────────────────────────────

def post_04_new_client_offer():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Full gold top block
    draw.rectangle([0, 0, W, 280], fill=GOLD)

    # TOP: large offer text in dark on gold
    cx(draw, 30, "NEW CLIENT?", DARK, font(52, bold=True))
    cx(draw, 100, "WELCOME OFFER", DARK, font(36, bold=True))
    cx(draw, 150, "YOUR BARBERSHOP NAME", DARK, font(18))
    gold_bar(draw, 280, thickness=6)

    # Centre: big discount
    cx(draw, 310, "20% OFF", WHITE, font(90, bold=True))
    cx(draw, 420, "YOUR FIRST VISIT", GOLD, font(32, bold=True))

    gold_bar(draw, 475, thickness=3, x0=80, x1=W - 80)

    # Terms
    terms = [
        "Valid for first-time clients only",
        "Cannot be combined with other offers",
        "Show this post when you arrive",
        "Book in advance — limited slots per week",
    ]
    ty = 500
    for t in terms:
        # Tick
        draw.ellipse([80, ty + 4, 102, ty + 26], fill=GOLD)
        draw.text((88, ty + 5), "✓", fill=DARK, font=font(13, bold=True))
        draw.text((118, ty + 4), t, fill=WHITE, font=font(18))
        ty += 46

    gold_bar(draw, ty + 18, thickness=2, x0=80, x1=W - 80)

    cx(draw, ty + 36, "Book Now — DM or Call", WHITE, font(22, bold=True))
    cx(draw, ty + 72, "+1 (555) 000-0000  |  @yourbarbershop", GOLD, font(18))
    cx(draw, ty + 110, "Offer expires end of month", GREY, font(14))

    draw.rectangle([0, H - 6, W, H], fill=GOLD)

    return save(img, "barber_ig_04_new_client_offer.png")


# ─── POST 05 — Customer Testimonial ───────────────────────────────────────────

def post_05_testimonial():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, W, 6], fill=GOLD)
    draw.rectangle([0, H - 6, W, H], fill=GOLD)
    gold_border(draw, margin=24, width=2)

    # Stars
    star_y = 100
    star_spacing = 80
    star_x_start = W // 2 - 2 * star_spacing
    for i in range(5):
        sx = star_x_start + i * star_spacing
        # Simple 5-point star via polygon
        import math
        pts = []
        for p in range(10):
            angle = math.pi * p / 5 - math.pi / 2
            r = 28 if p % 2 == 0 else 12
            pts.append((sx + r * math.cos(angle), star_y + r * math.sin(angle)))
        draw.polygon(pts, fill=GOLD)

    cx(draw, star_y + 50, "5 STAR REVIEW", GOLD, font(20, bold=True))
    gold_bar(draw, 185, thickness=2, x0=100, x1=W - 100)

    # Opening quote
    draw.text((70, 205), "\u201c", fill=GOLD, font=font(100, serifbold=True))

    # Quote text — wrapped manually
    quote_lines = [
        "Best barber I've ever been to.",
        "The fade was absolutely clean,",
        "hot towel shave was incredible,",
        "and the whole vibe in the shop",
        "is just unmatched.",
    ]
    qy = 250
    for line in quote_lines:
        cx(draw, qy, line, WHITE, font(26, serif=True))
        qy += 46

    # Closing quote
    bb = draw.textbbox((0, 0), "\u201d", font=font(100, serifbold=True))
    draw.text((W - 90, qy - 20), "\u201d", fill=GOLD, font=font(100, serifbold=True))

    gold_bar(draw, qy + 40, thickness=2, x0=100, x1=W - 100)

    # Attribution
    cx(draw, qy + 58, "— James T., Verified Client", GOLD, font(20, bold=True))
    cx(draw, qy + 94, "Google Review · YOUR BARBERSHOP NAME", GREY, font(15))

    # CTA
    cx(draw, H - 90, "Leave us a review — link in bio", WHITE, font(18))
    cx(draw, H - 50, "@yourbarbershop", GOLD, font(18, bold=True))

    return save(img, "barber_ig_05_testimonial.png")


# ─── POST 06 — Tip of the Week ────────────────────────────────────────────────

def post_06_tip_of_the_week():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Gold header band
    draw.rectangle([0, 0, W, 220], fill=GOLD)
    draw.rectangle([0, 220, W, 226], fill=DARK)

    cx(draw, 28, "TIP OF THE WEEK", DARK, font(36, bold=True))
    cx(draw, 80, "BARBER ADVICE FROM THE PROS", DARK, font(18))
    scissors_icon(draw, W // 2, 165, size=30)

    draw.rectangle([0, H - 6, W, H], fill=GOLD)

    # Tip number badge
    badge_cx = W // 2
    badge_cy = 310
    draw.ellipse([badge_cx - 50, badge_cy - 50,
                  badge_cx + 50, badge_cy + 50], fill=GOLD)
    cx(draw, badge_cy - 22, "#01", DARK, font(28, bold=True))

    cx(draw, 385, "KEEP YOUR FADE FRESH", WHITE, font(36, bold=True))
    cx(draw, 435, "EVERY 2\u20133 WEEKS", GOLD, font(28, bold=True))
    gold_bar(draw, 480, thickness=2, x0=80, x1=W - 80)

    tip_lines = [
        "A fade grows out fast. To keep it sharp",
        "and clean, book a maintenance trim every",
        "2 to 3 weeks. A quick tidy-up takes",
        "just 15–20 minutes and makes all the",
        "difference to your overall look.",
    ]
    ty = 505
    for line in tip_lines:
        cx(draw, ty, line, WHITE, font(20))
        ty += 40

    gold_bar(draw, ty + 15, thickness=2, x0=80, x1=W - 80)
    cx(draw, ty + 32, "Follow for weekly tips from YOUR BARBERSHOP NAME", GOLD, font(16))
    cx(draw, ty + 64, "@yourbarbershop  |  #BarberTip  #FadeGame", GREY, font(14))

    return save(img, "barber_ig_06_tip_of_the_week.png")


# ─── POST 07 — Before & After ─────────────────────────────────────────────────

def post_07_before_after():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, W, 6], fill=GOLD)
    draw.rectangle([0, H - 6, W, H], fill=GOLD)

    # Header
    cx(draw, 30, "BEFORE  &  AFTER", WHITE, font(42, bold=True))
    cx(draw, 88, "YOUR BARBERSHOP NAME", GOLD, font(18, bold=True))
    gold_bar(draw, 125, thickness=2, x0=40, x1=W - 40)

    # Two panels
    panel_y = 145
    panel_h = 600
    left_w  = W // 2 - 4
    right_w = W // 2 - 4

    # Left panel — BEFORE (darker)
    draw.rectangle([20, panel_y, 20 + left_w, panel_y + panel_h], fill=(18, 18, 18))
    draw.rectangle([20, panel_y, 20 + left_w, panel_y + panel_h], outline=GREY, width=2)
    label_font = font(22, bold=True)
    cx_w = left_w
    bb = draw.textbbox((0, 0), "BEFORE", font=label_font)
    draw.text((20 + (left_w - (bb[2] - bb[0])) // 2, panel_y + 20),
              "BEFORE", fill=GREY, font=label_font)

    # Placeholder graphic in BEFORE
    draw.ellipse([20 + left_w // 2 - 80, panel_y + 80,
                  20 + left_w // 2 + 80, panel_y + 240],
                 fill=(40, 40, 40), outline=GREY, width=2)
    draw.rectangle([20 + left_w // 2 - 100, panel_y + 280,
                    20 + left_w // 2 + 100, panel_y + 520],
                   fill=(40, 40, 40), outline=GREY, width=2)
    cx(draw, panel_y + 540, "Add your photo", GREY, font(14))

    # Right panel — AFTER (gold highlight)
    rx = W // 2 + 4
    draw.rectangle([rx, panel_y, rx + right_w, panel_y + panel_h], fill=PANEL)
    draw.rectangle([rx, panel_y, rx + right_w, panel_y + panel_h], outline=GOLD, width=2)
    bb = draw.textbbox((0, 0), "AFTER", font=label_font)
    draw.text((rx + (right_w - (bb[2] - bb[0])) // 2, panel_y + 20),
              "AFTER", fill=GOLD, font=label_font)

    draw.ellipse([rx + right_w // 2 - 80, panel_y + 80,
                  rx + right_w // 2 + 80, panel_y + 240],
                 fill=(50, 50, 50), outline=GOLD, width=2)
    draw.rectangle([rx + right_w // 2 - 100, panel_y + 280,
                    rx + right_w // 2 + 100, panel_y + 520],
                   fill=(50, 50, 50), outline=GOLD, width=2)
    cx(draw, panel_y + 540, "Add your photo", GOLD, font(14))

    # Gold centre divider
    draw.rectangle([W // 2 - 4, panel_y, W // 2 + 4, panel_y + panel_h], fill=GOLD)

    # Footer
    gold_bar(draw, panel_y + panel_h + 14, thickness=2, x0=40, x1=W - 40)
    cx(draw, panel_y + panel_h + 30,
       "Tag us in your transformation!", WHITE, font(22, bold=True))
    cx(draw, panel_y + panel_h + 66,
       "@yourbarbershop  |  #YourBarberTransformation", GOLD, font(16))

    return save(img, "barber_ig_07_before_after.png")


# ─── POST 08 — Meet the Barber ────────────────────────────────────────────────

def post_08_meet_the_barber():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, W, 8], fill=GOLD)
    draw.rectangle([0, H - 8, W, H], fill=GOLD)
    gold_border(draw, margin=22, width=2)

    cx(draw, 40, "MEET THE BARBER", WHITE, font(38, bold=True))
    cx(draw, 92, "YOUR BARBERSHOP NAME", GOLD, font(18, bold=True))
    gold_bar(draw, 132, thickness=2, x0=80, x1=W - 80)

    # Profile photo placeholder circle
    ph_r = 170
    ph_cx = W // 2
    ph_cy = 340
    draw.ellipse([ph_cx - ph_r, ph_cy - ph_r, ph_cx + ph_r, ph_cy + ph_r],
                 fill=PANEL, outline=GOLD, width=4)
    # Person silhouette
    head_r = 55
    draw.ellipse([ph_cx - head_r, ph_cy - ph_r + 30,
                  ph_cx + head_r, ph_cy - ph_r + 30 + head_r * 2],
                 fill=(60, 60, 60))
    draw.ellipse([ph_cx - head_r * 2, ph_cy + 20,
                  ph_cx + head_r * 2, ph_cy + ph_r - 10],
                 fill=(60, 60, 60))
    cx(draw, ph_cy + 195, "Add your photo here", GREY, font(14))

    # Name & title
    cx(draw, ph_cy + ph_r + 30, "Your Name Here", WHITE, font(32, bold=True))
    cx(draw, ph_cy + ph_r + 70, "MASTER BARBER  |  10+ YEARS", GOLD, font(18, bold=True))

    gold_bar(draw, ph_cy + ph_r + 104, thickness=2, x0=80, x1=W - 80)

    # Bio bullets
    bullets = [
        "Specialises in skin fades & classic cuts",
        "Trained in London & New York",
        "Passionate about clean lines & detail",
        "Book with me — DM @yourbarbershop",
    ]
    by = ph_cy + ph_r + 120
    for b in bullets:
        draw.ellipse([80, by + 7, 96, by + 23], fill=GOLD)
        draw.text((112, by + 4), b, fill=WHITE, font=font(18))
        by += 44

    return save(img, "barber_ig_08_meet_the_barber.png")


# ─── POST 09 — Opening Hours ──────────────────────────────────────────────────

def post_09_opening_hours():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Gold top and bottom
    draw.rectangle([0, 0, W, 8], fill=GOLD)
    draw.rectangle([0, H - 8, W, H], fill=GOLD)
    gold_border(draw, margin=22, width=2)

    scissors_icon(draw, W // 2, 90, size=35)
    cx(draw, 145, "OPENING HOURS", WHITE, font(44, bold=True))
    cx(draw, 200, "YOUR BARBERSHOP NAME", GOLD, font(18, bold=True))
    gold_bar(draw, 238, thickness=2, x0=80, x1=W - 80)

    hours = [
        ("Monday",    "9:00 am – 8:00 pm"),
        ("Tuesday",   "9:00 am – 8:00 pm"),
        ("Wednesday", "9:00 am – 8:00 pm"),
        ("Thursday",  "9:00 am – 8:00 pm"),
        ("Friday",    "9:00 am – 8:00 pm"),
        ("Saturday",  "9:00 am – 7:00 pm"),
        ("Sunday",    "10:00 am – 4:00 pm"),
    ]

    hy = 265
    row_h = 80
    today_idx = 2  # Highlight Wednesday as example

    for i, (day, time) in enumerate(hours):
        row_y = hy + i * row_h
        if i == today_idx:
            draw.rectangle([40, row_y - 6, W - 40, row_y + row_h - 14],
                           fill=(50, 42, 20))
            draw.rectangle([40, row_y - 6, W - 40, row_y + row_h - 14],
                           outline=GOLD, width=2)
            day_col = GOLD
            time_col = GOLD
            tag = " ← TODAY"
        else:
            day_col = WHITE
            time_col = GREY
            tag = ""

        draw.text((60, row_y + 10), day + tag, fill=day_col, font=font(20, bold=True))
        # Time right-aligned
        bb = draw.textbbox((0, 0), time, font=font(20))
        draw.text((W - 60 - (bb[2] - bb[0]), row_y + 10),
                  time, fill=time_col, font=font(20))

        if i < len(hours) - 1:
            gold_bar(draw, row_y + row_h - 15, thickness=1, x0=60, x1=W - 60)

    # Footer
    foot_y = hy + len(hours) * row_h + 10
    gold_bar(draw, foot_y, thickness=2, x0=40, x1=W - 40)
    cx(draw, foot_y + 18, "Walk-ins welcome · Appointments preferred",
       WHITE, font(18))
    cx(draw, foot_y + 50, "123 Main Street, Your City", GOLD, font(16))

    return save(img, "barber_ig_09_opening_hours.png")


# ─── POST 10 — Loyalty Program ────────────────────────────────────────────────

def post_10_loyalty_program():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, W, 8], fill=GOLD)
    draw.rectangle([0, H - 8, W, H], fill=GOLD)
    gold_border(draw, margin=22, width=2)

    cx(draw, 40, "LOYALTY REWARDS", WHITE, font(42, bold=True))
    cx(draw, 96, "YOUR BARBERSHOP NAME", GOLD, font(18, bold=True))
    gold_bar(draw, 134, thickness=2, x0=80, x1=W - 80)

    cx(draw, 160, "Collect stamps. Get free cuts.", WHITE, font(22))

    # Stamp grid — 10 stamps (3+4+3 layout)
    stamp_r = 68
    stamp_y_rows = [310, 460, 610]
    stamp_counts = [3, 4, 3]
    stamp_num = 0
    STAMP_FILLED = 6  # Show 6 filled

    for row_i, (sy, count) in enumerate(zip(stamp_y_rows, stamp_counts)):
        total_w = count * (stamp_r * 2 + 20) - 20
        sx_start = (W - total_w) // 2
        for col_i in range(count):
            stamp_num += 1
            sx = sx_start + col_i * (stamp_r * 2 + 20) + stamp_r
            filled = stamp_num <= STAMP_FILLED
            fill_col = GOLD if filled else PANEL
            outline_col = GOLD
            draw.ellipse([sx - stamp_r, sy - stamp_r, sx + stamp_r, sy + stamp_r],
                         fill=fill_col, outline=outline_col, width=3)
            if filled:
                scissors_icon(draw, sx, sy, size=24)
            else:
                cx(draw, sy - 10, str(stamp_num), GREY, font(18, bold=True), W)

    gold_bar(draw, 695, thickness=2, x0=80, x1=W - 80)

    # Reward message
    cx(draw, 718, "Every 10th cut is FREE!", GOLD, font(28, bold=True))
    cx(draw, 762, "Ask in-shop for your loyalty card", WHITE, font(18))

    gold_bar(draw, 810, thickness=2, x0=80, x1=W - 80)

    cx(draw, 828, "Already a member? Bring your card each visit.", WHITE, font(16))
    cx(draw, 866, "New to us? Start collecting today.", GREY, font(15))
    cx(draw, 920, "@yourbarbershop  |  #BarberLoyalty", GOLD, font(17))

    return save(img, "barber_ig_10_loyalty_program.png")


# ─── POST 11 — Referral Offer ─────────────────────────────────────────────────

def post_11_referral():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Gold top half feel
    draw.rectangle([0, 0, W, 340], fill=GOLD)
    draw.rectangle([0, 340, W, 346], fill=DARK)
    draw.rectangle([0, H - 6, W, H], fill=GOLD)

    cx(draw, 30, "TELL A FRIEND.", DARK, font(52, bold=True))
    cx(draw, 96, "GET REWARDED.", DARK, font(44, bold=True))
    cx(draw, 165, "YOUR BARBERSHOP NAME", DARK, font(18))

    # Arrows / icon area
    scissors_icon(draw, W // 2, 270, size=35)

    # Bottom dark section
    cx(draw, 375, "HOW IT WORKS", WHITE, font(28, bold=True))
    gold_bar(draw, 415, thickness=2, x0=80, x1=W - 80)

    steps_ref = [
        ("STEP 1", "Refer a friend who's never visited us"),
        ("STEP 2", "They book & get 15% off their first cut"),
        ("STEP 3", "You get £10 off your next visit"),
    ]
    sy = 440
    for step, desc in steps_ref:
        draw.rounded_rectangle([60, sy, 260, sy + 46],
                                radius=8, fill=GOLD)
        bb = draw.textbbox((0, 0), step, font=font(17, bold=True))
        draw.text((60 + (200 - (bb[2] - bb[0])) // 2, sy + 10),
                  step, fill=DARK, font=font(17, bold=True))
        draw.text((278, sy + 10), desc, fill=WHITE, font=font(17))
        sy += 70

    gold_bar(draw, sy + 10, thickness=2, x0=80, x1=W - 80)
    cx(draw, sy + 30, "No limit on referrals — earn every time!", GOLD, font(20, bold=True))
    cx(draw, sy + 68, "DM us or mention it in-shop", WHITE, font(17))
    cx(draw, sy + 100, "@yourbarbershop", GOLD, font(18, bold=True))

    return save(img, "barber_ig_11_referral.png")


# ─── POST 12 — Seasonal Promo ─────────────────────────────────────────────────

def post_12_seasonal_promo():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, W, 8], fill=GOLD)
    draw.rectangle([0, H - 8, W, H], fill=GOLD)
    gold_border(draw, margin=22, width=2)

    # Top banner: season label
    draw.rectangle([60, 50, W - 60, 130], fill=GOLD)
    cx(draw, 67, "SPRING SPECIAL OFFER", DARK, font(28, bold=True))

    cx(draw, 155, "LOOK SHARP.", WHITE, font(56, bold=True))
    cx(draw, 225, "PAY LESS.", GOLD, font(56, bold=True))

    gold_bar(draw, 300, thickness=3, x0=80, x1=W - 80)

    cx(draw, 325, "YOUR BARBERSHOP NAME", WHITE, font(20, bold=True))

    # Offer highlight
    draw.rounded_rectangle([80, 380, W - 80, 510], radius=16, fill=PANEL,
                           outline=GOLD, width=3)
    cx(draw, 395, "Cut + Beard Trim Combo", WHITE, font(24, bold=True))
    # Strikethrough price
    old_price = "£35"
    bb = draw.textbbox((0, 0), old_price, font=font(22))
    ox = (W - (bb[2] - bb[0])) // 2
    draw.text((ox, 432), old_price, fill=GREY, font=font(22))
    draw.rectangle([ox, 444, ox + (bb[2] - bb[0]), 447], fill=GREY)

    cx(draw, 465, "NOW ONLY £26", GOLD, font(28, bold=True))

    cx(draw, 535, "Limited time — ends 30th April", GREY, font(16))

    gold_bar(draw, 575, thickness=2, x0=80, x1=W - 80)

    offer2_items = [
        "Free hot towel finish with every cut this month",
        "Free beard shape with any new client booking",
        "10% off for students — bring your student card",
    ]
    oy = 600
    for item in offer2_items:
        draw.ellipse([80, oy + 6, 98, oy + 24], fill=GOLD)
        draw.text((116, oy + 2), item, fill=WHITE, font=font(18))
        oy += 46

    gold_bar(draw, oy + 14, thickness=2, x0=80, x1=W - 80)
    cx(draw, oy + 32, "DM to book  |  @yourbarbershop", GOLD, font(20, bold=True))
    cx(draw, oy + 68, "Offer valid while slots available. T&Cs apply.", GREY, font(14))

    return save(img, "barber_ig_12_seasonal_promo.png")


# ─── PREVIEW GRID ─────────────────────────────────────────────────────────────

def build_preview_grid(files):
    print("Building preview grid...")
    cols = 4
    thumb_w = 540
    padding = 40
    gap = 20
    rows = -(-len(files) // cols)  # ceiling div

    thumbs = []
    for f in files:
        im = Image.open(f)
        im = im.resize((thumb_w, thumb_w), Image.LANCZOS)
        thumbs.append(im)

    grid_w = padding * 2 + thumb_w * cols + gap * (cols - 1)
    grid_h = padding * 2 + thumb_w * rows + gap * (rows - 1)
    grid = Image.new("RGB", (grid_w, grid_h), DARK)

    for idx, th in enumerate(thumbs):
        r, c = divmod(idx, cols)
        x = padding + c * (thumb_w + gap)
        y = padding + r * (thumb_w + gap)
        grid.paste(th, (x, y))

    out = OUTPUT_DIR / "preview_grid.png"
    grid.save(str(out), "PNG")
    print(f"  Saved: {out.name}")
    return out


# ─── UPLOAD ───────────────────────────────────────────────────────────────────

def upload(local_path, key):
    load_dotenv("/root/NEW-AI-PROJECT/purpleocaz-canva-mcp/.env", override=True)
    s3 = boto3.client("s3",
        endpoint_url="https://lon1.digitaloceanspaces.com",
        aws_access_key_id=os.getenv("DO_SPACES_KEY"),
        aws_secret_access_key=os.getenv("DO_SPACES_SECRET"),
        region_name="lon1",
    )
    s3.upload_file(
        str(local_path), "purpleocaz-assets", key,
        ExtraArgs={"ACL": "public-read", "ContentType": "image/png"},
    )
    url = f"https://purpleocaz-assets.lon1.digitaloceanspaces.com/{key}"
    print(f"  Uploaded → {url}")
    return url


# ─── MAIN ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    builders = [
        post_01_brand_welcome,
        post_02_services_menu,
        post_03_book_now,
        post_04_new_client_offer,
        post_05_testimonial,
        post_06_tip_of_the_week,
        post_07_before_after,
        post_08_meet_the_barber,
        post_09_opening_hours,
        post_10_loyalty_program,
        post_11_referral,
        post_12_seasonal_promo,
    ]

    files = []
    for fn in builders:
        files.append(fn())

    grid = build_preview_grid(files)

    print("\nUploading to Spaces...")
    for f in files:
        upload(f, f"barbershop/instagram/{f.name}")

    grid_url = upload(grid, "barbershop/instagram/preview_grid.png")

    # GET verification
    import urllib.request
    print("\nVerifying uploads...")
    for f in files:
        url = f"https://purpleocaz-assets.lon1.digitaloceanspaces.com/barbershop/instagram/{f.name}"
        try:
            code = urllib.request.urlopen(url).getcode()
            print(f"  {f.name}: HTTP {code}")
        except Exception as e:
            print(f"  {f.name}: FAILED — {e}")

    print(f"\nPreview grid: {grid_url}")
    print("Done. 12 posts + grid uploaded.")
