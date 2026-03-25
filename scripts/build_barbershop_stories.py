#!/usr/bin/env python3
"""
Barbershop Instagram Stories — 6 x 1080x1920px.
Design system: #1A1A1A bg, #C9A96E gold, #FFFFFF white, #888888 grey.

Stories:
 01 — Book Now (swipe-up CTA)
 02 — Today's Availability
 03 — Flash Deal (24h offer)
 04 — Tip of the Day
 05 — Customer Shoutout
 06 — Weekend Special
"""

import os, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import boto3
from dotenv import load_dotenv

PROJECT_ROOT = Path("/root/NEW-AI-PROJECT")
OUTPUT_DIR   = PROJECT_ROOT / "outputs" / "barbershop" / "stories"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FONT_BOLD   = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG    = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SERIF  = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_SERIFB = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

BG    = (26, 26, 26)
DARK  = (10, 10, 10)
PANEL = (38, 38, 38)
GOLD  = (201, 169, 110)
WHITE = (255, 255, 255)
GREY  = (136, 136, 136)
CREAM = (255, 253, 245)

W, H = 1080, 1920


# ─── Helpers ──────────────────────────────────────────────────────────────────

def font(size, bold=False, serif=False, serifbold=False):
    if serifbold: return ImageFont.truetype(FONT_SERIFB, size)
    if serif:     return ImageFont.truetype(FONT_SERIF,  size)
    if bold:      return ImageFont.truetype(FONT_BOLD,   size)
    return ImageFont.truetype(FONT_REG, size)


def cx(draw, y, text, fill, f):
    bb = draw.textbbox((0, 0), text, font=f)
    draw.text(((W - (bb[2] - bb[0])) // 2, y), text, fill=fill, font=f)


def gold_bar(draw, y, h=4, x0=0, x1=W):
    draw.rectangle([x0, y, x1, y + h], fill=GOLD)


def scissors(draw, x, y, size=36):
    draw.line([(x - size, y - size // 2), (x + size, y + size // 2)], fill=GOLD, width=7)
    draw.line([(x + size, y - size // 2), (x - size, y + size // 2)], fill=GOLD, width=7)
    for ex, ey in [(x - size, y - size // 2), (x + size, y - size // 2),
                   (x - size, y + size // 2), (x + size, y + size // 2)]:
        draw.ellipse([ex - 10, ey - 10, ex + 10, ey + 10], outline=GOLD, width=3)


def star(draw, cx, cy, r_outer=32, r_inner=14, fill=GOLD):
    pts = []
    for i in range(10):
        angle = math.pi * i / 5 - math.pi / 2
        r = r_outer if i % 2 == 0 else r_inner
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    draw.polygon(pts, fill=fill)


def shop_badge(draw, img, y=48):
    """Top-of-story shop name badge."""
    gold_bar(draw, 0, h=6)
    draw.text((44, y), "YOUR BARBERSHOP NAME", fill=GOLD, font=font(26, bold=True))
    draw.text((44, y + 36), "EST. 2015  ·  Master Barbers", fill=GREY, font=font(18))


def swipe_cta(draw, y=H - 100):
    """Bottom swipe-up CTA strip."""
    gold_bar(draw, H - 6, h=6)
    draw.rounded_rectangle([60, y - 56, W - 60, y + 4],
                            radius=30, fill=GOLD)
    cx(draw, y - 42, "↑  SWIPE UP TO BOOK  ↑", DARK, font(26, bold=True))


def save(img, name):
    out = OUTPUT_DIR / name
    img.save(str(out), "PNG")
    print(f"  Saved: {out.name}")
    return out


# ─── STORY 01 — Book Now ──────────────────────────────────────────────────────

def story_01_book_now():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Top gold band
    draw.rectangle([0, 0, W, 260], fill=DARK)
    gold_bar(draw, 0, h=6)
    shop_badge(draw, img)

    # Large scissors centre
    scissors(draw, W // 2, 480, size=90)
    gold_bar(draw, 590, h=4, x0=W // 2 - 220, x1=W // 2 + 220)

    # Main headline
    cx(draw, 625, "READY FOR YOUR", GREY, font(34, bold=True))
    cx(draw, 680, "NEXT LEVEL", WHITE, font(86, bold=True))
    cx(draw, 780, "LOOK?", GOLD, font(86, bold=True))

    gold_bar(draw, 888, h=4, x0=80, x1=W - 80)

    # Steps
    steps = [
        ("DM us on Instagram", "@yourbarbershop"),
        ("Call us directly",    "+1 (555) 000-0000"),
        ("Book online",         "yourbarbershop.com"),
    ]
    sy = 916
    for label, value in steps:
        draw.ellipse([80, sy + 8, 110, sy + 38], fill=GOLD)
        draw.text((80, sy + 8), "›", fill=DARK, font=font(24, bold=True))
        draw.text((130, sy + 6), label, fill=WHITE, font=font(26, bold=True))
        draw.text((130, sy + 38), value, fill=GOLD, font=font(22))
        sy += 86

    gold_bar(draw, sy + 20, h=2, x0=80, x1=W - 80)

    # Hours
    cx(draw, sy + 36, "Mon–Fri 9–8  ·  Sat 9–7  ·  Sun 10–4", GREY, font(22))
    cx(draw, sy + 76, "Walk-ins welcome · Appointments preferred", WHITE, font(20))

    # Dots progress bar (story 1 of 6)
    dot_y = H - 160
    dot_r = 8
    dot_gap = 28
    total = 6
    dots_w = total * (dot_r * 2) + (total - 1) * dot_gap
    dx = (W - dots_w) // 2
    for i in range(total):
        col = GOLD if i == 0 else GREY
        draw.ellipse([dx, dot_y - dot_r, dx + dot_r * 2, dot_y + dot_r],
                     fill=col)
        dx += dot_r * 2 + dot_gap

    swipe_cta(draw)

    return save(img, "barber_story_01_book_now.png")


# ─── STORY 02 — Today's Availability ─────────────────────────────────────────

def story_02_availability():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    gold_bar(draw, 0, h=6)
    shop_badge(draw, img)

    # Urgency header
    draw.rectangle([0, 130, W, 310], fill=GOLD)
    cx(draw, 143, "TODAY'S SLOTS", DARK, font(52, bold=True))
    cx(draw, 218, "Wednesday · Limited Availability", DARK, font(26))

    scissors(draw, W // 2, 400, size=55)
    gold_bar(draw, 470, h=3, x0=100, x1=W - 100)

    cx(draw, 496, "AVAILABLE TIMES", WHITE, font(36, bold=True))

    slots = [
        ("10:00 am", "Classic Cut", "AVAILABLE"),
        ("11:30 am", "Fade + Beard", "AVAILABLE"),
        ("1:00 pm",  "Hot Towel Shave", "BOOKED"),
        ("2:30 pm",  "Classic Cut", "AVAILABLE"),
        ("4:00 pm",  "Cut & Beard Combo", "BOOKED"),
        ("5:30 pm",  "Classic Cut", "AVAILABLE"),
        ("7:00 pm",  "Any Service", "AVAILABLE"),
    ]

    slot_y = 556
    for time, service, status in slots:
        avail = status == "AVAILABLE"
        bg_col = (38, 42, 28) if avail else (38, 30, 30)
        border  = GOLD if avail else GREY
        draw.rounded_rectangle([44, slot_y, W - 44, slot_y + 80],
                               radius=10, fill=bg_col, outline=border, width=2)
        draw.text((70, slot_y + 14), time, fill=WHITE, font=font(24, bold=True))
        draw.text((70, slot_y + 44), service, fill=GREY, font=font(18))
        # Status badge
        scol = GOLD if avail else (100, 60, 60)
        stxt = "✓ OPEN" if avail else "✗ FULL"
        bb = draw.textbbox((0, 0), stxt, font=font(18, bold=True))
        draw.text((W - 70 - (bb[2] - bb[0]), slot_y + 26),
                  stxt, fill=scol, font=font(18, bold=True))
        slot_y += 96

    gold_bar(draw, slot_y + 14, h=3, x0=60, x1=W - 60)
    cx(draw, slot_y + 32, "Slots fill fast — DM to reserve yours", WHITE, font(24, bold=True))
    cx(draw, slot_y + 70, "@yourbarbershop", GOLD, font(26, bold=True))

    swipe_cta(draw)
    return save(img, "barber_story_02_availability.png")


# ─── STORY 03 — Flash Deal ────────────────────────────────────────────────────

def story_03_flash_deal():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Bold alert top
    draw.rectangle([0, 0, W, 340], fill=GOLD)
    gold_bar(draw, 0, h=8)
    cx(draw, 40,  "⚡ FLASH DEAL ⚡", DARK, font(58, bold=True))
    cx(draw, 130, "24 HOURS ONLY", DARK, font(38, bold=True))
    cx(draw, 195, "YOUR BARBERSHOP NAME", DARK, font(22))
    gold_bar(draw, 340, h=6)

    scissors(draw, W // 2, 460, size=70)

    # Deal
    cx(draw, 560, "HOT TOWEL SHAVE", WHITE, font(46, bold=True))
    cx(draw, 630, "+", GOLD, font(38))
    cx(draw, 680, "CLASSIC HAIRCUT", WHITE, font(46, bold=True))

    # Price struck & new
    cx(draw, 764, "Usually £38", GREY, font(30))
    bb = draw.textbbox((0, 0), "Usually £38", font=font(30))
    lx = (W - (bb[2] - bb[0])) // 2
    draw.rectangle([lx, 784, lx + (bb[2] - bb[0]), 788], fill=GREY)

    cx(draw, 824, "TODAY ONLY: £25", GOLD, font(52, bold=True))
    cx(draw, 900, "Save £13 — one day only", WHITE, font(26))

    gold_bar(draw, 960, h=3, x0=80, x1=W - 80)

    # Countdown feel
    draw.rounded_rectangle([80, 984, W - 80, 1084],
                           radius=16, fill=PANEL, outline=GOLD, width=3)
    cx(draw, 994, "Offer expires midnight tonight", WHITE, font(24, bold=True))
    cx(draw, 1032, "First come, first served · Limited slots", GOLD, font(20))

    # How to claim
    cx(draw, 1108, "HOW TO CLAIM", WHITE, font(30, bold=True))
    gold_bar(draw, 1152, h=2, x0=120, x1=W - 120)

    claim_steps = [
        "DM the word FLASH to @yourbarbershop",
        "We'll confirm your slot within the hour",
        "Show this story when you arrive",
    ]
    cy = 1174
    for step in claim_steps:
        draw.ellipse([80, cy + 6, 104, cy + 30], fill=GOLD)
        draw.text((124, cy + 4), step, fill=WHITE, font=font(22))
        cy += 58

    gold_bar(draw, cy + 18, h=2, x0=80, x1=W - 80)
    cx(draw, cy + 38, "Share this story to spread the word!", GREY, font(20))

    # Dots (story 3)
    dot_y = H - 160
    dot_r = 8
    dot_gap = 28
    total = 6
    dots_w = total * (dot_r * 2) + (total - 1) * dot_gap
    dx = (W - dots_w) // 2
    for i in range(total):
        col = GOLD if i == 2 else GREY
        draw.ellipse([dx, dot_y - dot_r, dx + dot_r * 2, dot_y + dot_r], fill=col)
        dx += dot_r * 2 + dot_gap

    swipe_cta(draw)
    return save(img, "barber_story_03_flash_deal.png")


# ─── STORY 04 — Tip of the Day ────────────────────────────────────────────────

def story_04_tip_of_day():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    gold_bar(draw, 0, h=6)
    shop_badge(draw, img)

    # Tip label badge
    draw.rounded_rectangle([W // 2 - 180, 180, W // 2 + 180, 256],
                           radius=38, fill=GOLD)
    cx(draw, 195, "BARBER TIP", DARK, font(34, bold=True))

    scissors(draw, W // 2, 360, size=70)
    gold_bar(draw, 450, h=3, x0=80, x1=W - 80)

    cx(draw, 480, "HOW TO MAINTAIN", WHITE, font(44, bold=True))
    cx(draw, 544, "YOUR FADE AT HOME", GOLD, font(40, bold=True))

    gold_bar(draw, 610, h=3, x0=80, x1=W - 80)

    tips = [
        ("USE THE RIGHT PRODUCT",
         "A light pomade or matte clay\nworks best for short fades.\nAvoid heavy waxes."),
        ("BRUSH DAILY",
         "Use a soft-bristle brush in\nthe direction of growth.\nKeeps shape looking fresh."),
        ("MOISTURISE YOUR SCALP",
         "Dry skin shows more on a\nshort fade. Use a light\nscalp oil 2–3x a week."),
        ("BOOK REGULAR TRIMS",
         "Every 2–3 weeks. Don't wait\ntill it grows out — maintain\nthe shape while it's clean."),
    ]

    ty = 650
    for i, (headline, body) in enumerate(tips):
        # Number circle
        draw.ellipse([60, ty, 110, ty + 50], fill=GOLD)
        bb = draw.textbbox((0, 0), str(i + 1), font=font(24, bold=True))
        draw.text((60 + (50 - (bb[2] - bb[0])) // 2, ty + 8),
                  str(i + 1), fill=DARK, font=font(24, bold=True))
        draw.text((132, ty + 4), headline, fill=WHITE, font=font(22, bold=True))
        # Body lines
        for j, line in enumerate(body.split("\n")):
            draw.text((132, ty + 36 + j * 28), line, fill=GREY, font=font(18))
        ty += 168

    gold_bar(draw, ty + 10, h=2, x0=60, x1=W - 60)
    cx(draw, ty + 30, "Follow for daily barber tips", WHITE, font(22))
    cx(draw, ty + 66, "@yourbarbershop", GOLD, font(24, bold=True))
    cx(draw, ty + 104, "#BarberTips  #FadeGame  #MensGrooming", GREY, font(18))

    swipe_cta(draw)
    return save(img, "barber_story_04_tip_of_day.png")


# ─── STORY 05 — Customer Shoutout ─────────────────────────────────────────────

def story_05_shoutout():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    gold_bar(draw, 0, h=6)
    shop_badge(draw, img)

    # Shoutout heading
    cx(draw, 175, "CLIENT", GREY, font(34, bold=True))
    cx(draw, 225, "SHOUTOUT", WHITE, font(72, bold=True))
    gold_bar(draw, 320, h=3, x0=80, x1=W - 80)

    # Stars
    star_y = 370
    sx_start = W // 2 - 2 * 80
    for i in range(5):
        star(draw, sx_start + i * 80, star_y + 28, r_outer=28, r_inner=12)
    cx(draw, star_y + 70, "5-Star Review", GOLD, font(22, bold=True))

    gold_bar(draw, 470, h=2, x0=100, x1=W - 100)

    # Photo placeholder
    ph_r = 140
    ph_cx = W // 2
    ph_cy = 680
    draw.ellipse([ph_cx - ph_r, ph_cy - ph_r, ph_cx + ph_r, ph_cy + ph_r],
                 fill=PANEL, outline=GOLD, width=4)
    # Silhouette
    draw.ellipse([ph_cx - 45, ph_cy - ph_r + 25,
                  ph_cx + 45, ph_cy - ph_r + 25 + 90], fill=(55, 55, 55))
    draw.ellipse([ph_cx - 90, ph_cy + 20,
                  ph_cx + 90, ph_cy + ph_r - 10], fill=(55, 55, 55))
    cx(draw, ph_cy + ph_r + 18, "Add client photo here", GREY, font(18))

    # Client name
    cx(draw, ph_cy + ph_r + 58, "Marcus R.", WHITE, font(38, bold=True))
    cx(draw, ph_cy + ph_r + 104, "Loyal client since 2021", GOLD, font(22))

    gold_bar(draw, ph_cy + ph_r + 142, h=2, x0=80, x1=W - 80)

    # Quote
    draw.text((70, ph_cy + ph_r + 162), "\u201c", fill=GOLD,
              font=font(80, serifbold=True))

    quote = [
        "Every single visit I leave",
        "looking cleaner than I thought",
        "possible. These guys are artists.",
        "Wouldn't go anywhere else.",
    ]
    qy = ph_cy + ph_r + 230
    for line in quote:
        cx(draw, qy, line, WHITE, font(26, serif=True))
        qy += 48

    bb = draw.textbbox((0, 0), "\u201d", font=font(80, serifbold=True))
    draw.text((W - 90, qy - 30), "\u201d", fill=GOLD, font=font(80, serifbold=True))

    gold_bar(draw, qy + 30, h=2, x0=80, x1=W - 80)

    cx(draw, qy + 50, "Want to be featured? Tag us!", WHITE, font(24, bold=True))
    cx(draw, qy + 88, "@yourbarbershop", GOLD, font(26, bold=True))
    cx(draw, qy + 126, "#YourBarbershop  #ClientLove", GREY, font(18))

    swipe_cta(draw)
    return save(img, "barber_story_05_shoutout.png")


# ─── STORY 06 — Weekend Special ───────────────────────────────────────────────

def story_06_weekend_special():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Full-width gold top block
    draw.rectangle([0, 0, W, 380], fill=GOLD)
    gold_bar(draw, 0, h=8)

    cx(draw, 36,  "WEEKEND", DARK, font(80, bold=True))
    cx(draw, 128, "SPECIAL", DARK, font(80, bold=True))
    cx(draw, 232, "YOUR BARBERSHOP NAME", DARK, font(22))
    cx(draw, 278, "Saturday & Sunday Only", DARK, font(26, bold=True))

    gold_bar(draw, 380, h=6)

    scissors(draw, W // 2, 500, size=70)
    gold_bar(draw, 592, h=3, x0=100, x1=W - 100)

    # Offers
    offers = [
        ("FREE",       "Hot towel finish\nwith every haircut"),
        ("£5 OFF",     "Any combo service\n(Cut + Beard or more)"),
        ("FREE",       "Kid's cut (under 10)\nwith adult booking"),
    ]

    oy = 620
    for badge, desc in offers:
        # Badge pill
        draw.rounded_rectangle([60, oy, 240, oy + 70], radius=12, fill=GOLD)
        bb = draw.textbbox((0, 0), badge, font=font(28, bold=True))
        draw.text((60 + (180 - (bb[2] - bb[0])) // 2, oy + 16),
                  badge, fill=DARK, font=font(28, bold=True))
        # Description
        for j, line in enumerate(desc.split("\n")):
            draw.text((264, oy + 6 + j * 34), line, fill=WHITE, font=font(24))
        oy += 108
        gold_bar(draw, oy - 14, h=1, x0=60, x1=W - 60)

    gold_bar(draw, oy + 6, h=3, x0=60, x1=W - 60)

    cx(draw, oy + 30, "Sat 9am–7pm  ·  Sun 10am–4pm", GOLD, font(26, bold=True))
    cx(draw, oy + 74, "Walk-ins welcome all weekend", WHITE, font(24))
    cx(draw, oy + 114, "123 Main Street, Your City", GREY, font(20))

    gold_bar(draw, oy + 154, h=2, x0=80, x1=W - 80)

    cx(draw, oy + 174, "Share this story — tag a mate", WHITE, font(24, bold=True))
    cx(draw, oy + 214, "who needs a fresh cut this weekend!", WHITE, font(22))
    cx(draw, oy + 260, "@yourbarbershop", GOLD, font(28, bold=True))
    cx(draw, oy + 304, "#WeekendVibes  #FreshCut  #BarberLife", GREY, font(18))

    gold_bar(draw, H - 6, h=6)

    swipe_cta(draw)
    return save(img, "barber_story_06_weekend_special.png")


# ─── PREVIEW GRID (vertical strip, 2-col) ────────────────────────────────────

def build_preview_grid(files):
    print("Building preview grid...")
    thumb_w = 360
    thumb_h = int(thumb_w * (H / W))   # maintain 9:16
    cols    = 3
    padding = 30
    gap     = 20
    rows    = -(-len(files) // cols)

    grid_w = padding * 2 + thumb_w * cols + gap * (cols - 1)
    grid_h = padding * 2 + thumb_h * rows + gap * (rows - 1)
    grid   = Image.new("RGB", (grid_w, grid_h), DARK)

    for idx, f in enumerate(files):
        r, c = divmod(idx, cols)
        im = Image.open(f).resize((thumb_w, thumb_h), Image.LANCZOS)
        x = padding + c * (thumb_w + gap)
        y = padding + r * (thumb_h + gap)
        grid.paste(im, (x, y))

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
    s3.upload_file(str(local_path), "purpleocaz-assets", key,
                   ExtraArgs={"ACL": "public-read", "ContentType": "image/png"})
    url = f"https://purpleocaz-assets.lon1.digitaloceanspaces.com/{key}"
    print(f"  Uploaded → {url}")
    return url


# ─── MAIN ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    builders = [
        story_01_book_now,
        story_02_availability,
        story_03_flash_deal,
        story_04_tip_of_day,
        story_05_shoutout,
        story_06_weekend_special,
    ]

    files = [fn() for fn in builders]
    grid  = build_preview_grid(files)

    print("\nUploading to Spaces...")
    for f in files:
        upload(f, f"barbershop/stories/{f.name}")
    grid_url = upload(grid, "barbershop/stories/preview_grid.png")

    print("\nVerifying uploads...")
    import urllib.request
    all_ok = True
    for f in files:
        url = f"https://purpleocaz-assets.lon1.digitaloceanspaces.com/barbershop/stories/{f.name}"
        try:
            code = urllib.request.urlopen(url).getcode()
            status = f"HTTP {code}"
        except Exception as e:
            status = f"FAILED — {e}"
            all_ok = False
        print(f"  {f.name}: {status}")

    print(f"\nPreview grid: {grid_url}")
    print(f"Done. 6 stories uploaded. All OK: {all_ok}")
