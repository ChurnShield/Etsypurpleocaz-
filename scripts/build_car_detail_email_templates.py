#!/usr/bin/env python3
"""
Car Detailing Email & Text Marketing Templates — 6 A4 PNGs.
Booking confirmation, appointment reminder, job completion,
follow-up, referral program, seasonal promo.
Uploads to DO Spaces and builds a 3x2 preview grid.
"""

import os
import boto3
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

# ── Paths ──────────────────────────────────────────────
PROJECT_ROOT = Path("/root/NEW-AI-PROJECT")
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "car-detail-email-templates"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Fonts ──────────────────────────────────────────────
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"

# ── Colours ────────────────────────────────────────────
BG = (13, 13, 13)
ACCENT = (224, 32, 32)
WHITE = (255, 255, 255)
SILVER = (192, 192, 192)
BODY_WHITE = (255, 255, 255)
GREY = (160, 160, 160)
DARK_BODY = (40, 40, 40)
LIGHT_GREY_BG = (245, 245, 245)
PANEL = (26, 26, 26)

# ── Page dimensions (A4 at 300dpi) ─────────────────────
W, H = 2480, 3508


def font(size, bold=False, italic=False):
    path = FONT_SERIF if italic else (FONT_BOLD if bold else FONT_REGULAR)
    return ImageFont.truetype(path, size)


def centred_text(draw, y, text, fill, f):
    bbox = draw.textbbox((0, 0), text, font=f)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, y), text, fill=fill, font=f)


def draw_pill(draw, cx, y, w, h, fill, text, text_color, text_size):
    x = cx - w // 2
    r = h // 2
    draw.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=fill)
    f = font(text_size, bold=True)
    bbox = draw.textbbox((0, 0), text, font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((x + (w - tw) // 2, y + (h - th) // 2 - 2), text, fill=text_color, font=f)


def draw_red_circle_num(draw, x, y, num, radius=28):
    draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=ACCENT)
    f = font(24, bold=True)
    text = str(num)
    bbox = draw.textbbox((0, 0), text, font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((x - tw // 2, y - th // 2 - 2), text, fill=WHITE, font=f)


def draw_header(draw, studio_line, subtitle_line, hero_line=None):
    """Standard dark header band y=0 to y=400."""
    draw.rectangle([0, 0, W, 400], fill=BG)
    centred_text(draw, 100, studio_line, WHITE, font(72, bold=True))
    centred_text(draw, 190, subtitle_line, ACCENT, font(36))
    draw.rectangle([0, 260, W, 266], fill=ACCENT)
    if hero_line:
        centred_text(draw, 310, hero_line, WHITE, font(56, bold=True))


def draw_footer(draw, y_start=3100):
    """Standard dark footer."""
    draw.rectangle([0, y_start, W, H], fill=BG)
    centred_text(draw, y_start + 80, "+1 (555) 000-0000  |  www.yourstudio.com", SILVER, font(26))
    centred_text(draw, y_start + 130, "hello@yourstudio.com  |  Your City, State", SILVER, font(24))
    centred_text(draw, y_start + 200, "YOUR STUDIO NAME  |  Car Detailing Specialist", WHITE, font(22, bold=True))


def draw_detail_box(draw, x, y, w, lines):
    """Dark outlined box with detail lines."""
    h = 40 + len(lines) * 50
    draw.rectangle([x, y, x + w, y + h], outline=BG, width=3)
    draw.rectangle([x, y, x + w, y + 6], fill=ACCENT)
    f = font(26)
    ly = y + 30
    for label, value in lines:
        draw.text((x + 30, ly), label, fill=GREY, font=font(22))
        draw.text((x + 350, ly), value, fill=DARK_BODY, font=font(26, bold=True))
        ly += 50
    return y + h


def draw_section_header(draw, y, text):
    """Red section header with left accent bar."""
    draw.rectangle([180, y, 190, y + 36], fill=ACCENT)
    draw.text((210, y), text, fill=ACCENT, font=font(32, bold=True))
    return y + 60


def draw_check_item(draw, y, text):
    """Checkmark item with red tick."""
    draw.text((240, y), ">", fill=ACCENT, font=font(24, bold=True))
    draw.text((290, y), text, fill=DARK_BODY, font=font(24))
    return y + 45


# ═══════════════════════════════════════════════════════
# TEMPLATE 1 — BOOKING CONFIRMATION
# ═══════════════════════════════════════════════════════
def build_booking_confirm():
    print("\n[1/6] Booking Confirmation")
    img = Image.new("RGB", (W, H), BODY_WHITE)
    draw = ImageDraw.Draw(img)

    draw_header(draw, "YOUR STUDIO NAME", "CAR DETAILING SPECIALIST", "BOOKING CONFIRMED")

    # Red pill badge
    draw_pill(draw, W // 2, 480, 800, 60, ACCENT, "YOUR APPOINTMENT IS CONFIRMED", WHITE, 24)

    # Appointment details box
    details = [
        ("Date:", "[DATE]"),
        ("Time:", "[TIME]"),
        ("Service:", "[SERVICE]"),
        ("Vehicle:", "[MAKE / MODEL]"),
        ("Duration:", "[X hours]"),
    ]
    box_bottom = draw_detail_box(draw, 180, 600, W - 360, details)

    # What to expect
    y = draw_section_header(draw, box_bottom + 60, "WHAT TO EXPECT")
    steps = [
        "Please arrive 5 minutes early",
        "Leave your keys with our team",
        "We'll text you when your car is ready",
    ]
    for i, step in enumerate(steps):
        draw_red_circle_num(draw, 240, y + 18, i + 1)
        draw.text((290, y + 2), step, fill=DARK_BODY, font=font(26))
        y += 70

    # Need to reschedule?
    y = draw_section_header(draw, y + 40, "NEED TO RESCHEDULE?")
    draw.text((210, y), "Call us at +1 (555) 000-0000 or reply to this message.", fill=DARK_BODY, font=font(24))
    y += 50
    draw.text((210, y), "Please give us at least 24 hours notice.", fill=GREY, font=font(22))

    # Italic closing
    y += 100
    centred_text(draw, y, "We look forward to making your car shine!", GREY, font(28, italic=True))

    draw_footer(draw)

    path = OUTPUT_DIR / "email_01_booking_confirm.png"
    img.save(path, "PNG")
    print(f"  Saved: {path.name}")
    return path


# ═══════════════════════════════════════════════════════
# TEMPLATE 2 — APPOINTMENT REMINDER
# ═══════════════════════════════════════════════════════
def build_appointment_reminder():
    print("\n[2/6] Appointment Reminder")
    img = Image.new("RGB", (W, H), BODY_WHITE)
    draw = ImageDraw.Draw(img)

    draw_header(draw, "YOUR STUDIO NAME", "CAR DETAILING SPECIALIST", "APPOINTMENT REMINDER")

    # REMINDER large red
    centred_text(draw, 480, "REMINDER", ACCENT, font(80, bold=True))
    centred_text(draw, 580, "Your detail is tomorrow!", DARK_BODY, font(44, bold=True))

    # Appointment summary box
    details = [
        ("Date:", "[DATE]"),
        ("Time:", "[TIME]"),
        ("Service:", "[SERVICE]"),
        ("Vehicle:", "[MAKE / MODEL]"),
        ("Location:", "[ADDRESS / MOBILE]"),
    ]
    box_bottom = draw_detail_box(draw, 180, 700, W - 360, details)

    # What to prepare
    y = draw_section_header(draw, box_bottom + 60, "WHAT TO PREPARE")
    items = [
        "Remove personal items from your car",
        "Note any areas of concern to tell our team",
        "Arrange alternative transport if needed",
    ]
    for item in items:
        y = draw_check_item(draw, y, item)

    # Reply to confirm
    y += 50
    draw.rectangle([180, y, W - 180, y + 120], fill=LIGHT_GREY_BG, outline=GREY, width=2)
    centred_text(draw, y + 20, "Reply YES to confirm your appointment", DARK_BODY, font(28, bold=True))
    centred_text(draw, y + 65, "or call +1 (555) 000-0000 to reschedule", GREY, font(24))

    # Looking forward
    y += 180
    centred_text(draw, y, "See you tomorrow!", GREY, font(28, italic=True))

    draw_footer(draw)

    path = OUTPUT_DIR / "email_02_appt_reminder.png"
    img.save(path, "PNG")
    print(f"  Saved: {path.name}")
    return path


# ═══════════════════════════════════════════════════════
# TEMPLATE 3 — JOB COMPLETION + REVIEW REQUEST
# ═══════════════════════════════════════════════════════
def build_job_completion():
    print("\n[3/6] Job Completion + Review Request")
    img = Image.new("RGB", (W, H), BODY_WHITE)
    draw = ImageDraw.Draw(img)

    draw_header(draw, "YOUR STUDIO NAME", "CAR DETAILING SPECIALIST", "YOUR CAR IS READY!")

    # Thank you
    centred_text(draw, 470, "Thank you for choosing", GREY, font(30, italic=True))
    centred_text(draw, 520, "[YOUR STUDIO NAME]", DARK_BODY, font(40, bold=True))

    # Work completed box
    details = [
        ("Service:", "[SERVICE COMPLETED]"),
        ("Date:", "[DATE]"),
        ("Technician:", "[TECH NAME]"),
    ]
    box_bottom = draw_detail_box(draw, 180, 620, W - 360, details)

    # Care instructions
    y = draw_section_header(draw, box_bottom + 50, "CARE INSTRUCTIONS")
    care_items = [
        "Avoid washing for 24 hours",
        "Keep out of direct sunlight today",
        "Use pH-neutral shampoo for future washes",
    ]
    for item in care_items:
        y = draw_check_item(draw, y, item)

    # Review request
    y = draw_section_header(draw, y + 50, "LOVED YOUR DETAIL?")

    # 5 stars
    star_text = "* * * * *"
    centred_text(draw, y, star_text, ACCENT, font(60, bold=True))
    y += 80

    centred_text(draw, y, "Leave us a review — it takes 30 seconds", DARK_BODY, font(28))
    y += 40
    centred_text(draw, y, "and means the world to our small business", DARK_BODY, font(28))
    y += 70

    # Big red LEAVE A REVIEW button
    draw_pill(draw, W // 2, y, 700, 80, ACCENT, "LEAVE A REVIEW  ->", WHITE, 30)
    y += 120

    # Platform names
    centred_text(draw, y, "Google  |  Yelp  |  Facebook", GREY, font(24))

    draw_footer(draw)

    path = OUTPUT_DIR / "email_03_job_complete.png"
    img.save(path, "PNG")
    print(f"  Saved: {path.name}")
    return path


# ═══════════════════════════════════════════════════════
# TEMPLATE 4 — FOLLOW-UP (7 days after)
# ═══════════════════════════════════════════════════════
def build_followup():
    print("\n[4/6] Follow-Up (7 days)")
    img = Image.new("RGB", (W, H), BODY_WHITE)
    draw = ImageDraw.Draw(img)

    draw_header(draw, "YOUR STUDIO NAME", "CAR DETAILING SPECIALIST", "HOW'S YOUR CAR LOOKING?")

    # Opening
    centred_text(draw, 480, "It's been a week since your detail.", DARK_BODY, font(30))
    centred_text(draw, 530, "Here are some tips to keep it looking showroom-fresh.", GREY, font(26))

    # Tips section
    y = draw_section_header(draw, 620, "MAINTAIN YOUR RESULTS")
    tips = [
        "Rinse your car weekly to prevent dirt buildup",
        "Use microfibre cloths only — no sponges",
        "Park in shade when possible to protect the finish",
        "Spot-clean bird droppings immediately",
    ]
    for tip in tips:
        y = draw_check_item(draw, y, tip)

    # Book your next detail
    y = draw_section_header(draw, y + 50, "BOOK YOUR NEXT DETAIL")
    draw.text((210, y), "Based on your last service, we recommend:", fill=DARK_BODY, font=font(26))
    y += 50
    recs = [
        "Interior Deep Clean — recommended every 3 months",
        "Ceramic Coating Top-Up — recommended every 6 months",
    ]
    for rec in recs:
        draw.text((240, y), "- " + rec, fill=DARK_BODY, font=font(24))
        y += 45

    # Loyalty discount box
    y += 20
    draw.rounded_rectangle([180, y, W - 180, y + 130], radius=15, fill=ACCENT)
    centred_text(draw, y + 20, "LOYAL CUSTOMER DISCOUNT", WHITE, font(30, bold=True))
    centred_text(draw, y + 70, "10% OFF your next booking — just mention this email", WHITE, font(26))
    y += 170

    # Referral ask
    y = draw_section_header(draw, y, "REFER A FRIEND")
    draw.text((210, y), "Know someone who'd love a detail?", fill=DARK_BODY, font=font(26))
    y += 40
    draw.text((210, y), "Send them our way — you both save $25!", fill=DARK_BODY, font=font(26, bold=True))
    y += 80

    # Book Now button
    draw_pill(draw, W // 2, y, 600, 80, ACCENT, "BOOK NOW", WHITE, 32)

    draw_footer(draw)

    path = OUTPUT_DIR / "email_04_followup.png"
    img.save(path, "PNG")
    print(f"  Saved: {path.name}")
    return path


# ═══════════════════════════════════════════════════════
# TEMPLATE 5 — REFERRAL PROGRAM
# ═══════════════════════════════════════════════════════
def build_referral():
    print("\n[5/6] Referral Program")
    img = Image.new("RGB", (W, H), BODY_WHITE)
    draw = ImageDraw.Draw(img)

    draw_header(draw, "YOUR STUDIO NAME", "CAR DETAILING SPECIALIST", "GIVE $25, GET $25")

    # Large $25 dominant
    centred_text(draw, 460, "$25", ACCENT, font(180, bold=True))
    centred_text(draw, 680, "for you and a friend", DARK_BODY, font(36))

    # How it works
    y = draw_section_header(draw, 780, "HOW IT WORKS")
    steps = [
        "Share your unique referral link or code",
        "Your friend books any full detail service",
        "You both receive $25 off your next booking",
    ]
    for i, step in enumerate(steps):
        draw_red_circle_num(draw, 240, y + 18, i + 1)
        draw.text((290, y + 2), step, fill=DARK_BODY, font=font(26))
        y += 80

    # Referral code box
    y += 20
    y = draw_section_header(draw, y, "YOUR REFERRAL CODE")
    draw.rounded_rectangle([300, y, W - 300, y + 120], radius=12, outline=ACCENT, width=4)
    centred_text(draw, y + 30, "[YOUR-CODE-HERE]", ACCENT, font(48, bold=True))
    y += 160

    # Terms
    terms = [
        "Valid for new customers only. Cannot be combined with other offers.",
        "Discount applied after referred customer completes their first service.",
        "No limit on referrals — the more friends, the more you save!",
    ]
    for t in terms:
        centred_text(draw, y, t, GREY, font(18))
        y += 30

    # Book Now
    y += 40
    draw_pill(draw, W // 2, y, 600, 80, ACCENT, "BOOK NOW", WHITE, 32)

    draw_footer(draw)

    path = OUTPUT_DIR / "email_05_referral.png"
    img.save(path, "PNG")
    print(f"  Saved: {path.name}")
    return path


# ═══════════════════════════════════════════════════════
# TEMPLATE 6 — SEASONAL PROMOTION
# ═══════════════════════════════════════════════════════
def build_seasonal_promo():
    print("\n[6/6] Seasonal Promotion")
    img = Image.new("RGB", (W, H), BODY_WHITE)
    draw = ImageDraw.Draw(img)

    draw_header(draw, "YOUR STUDIO NAME", "CAR DETAILING SPECIALIST", "SUMMER SPECIAL OFFER")

    # LIMITED TIME badge
    draw_pill(draw, W // 2, 470, 500, 56, ACCENT, "LIMITED TIME", WHITE, 28)

    # Main offer
    centred_text(draw, 580, "XX% OFF", ACCENT, font(100, bold=True))
    centred_text(draw, 710, "Full Interior & Exterior Detail", DARK_BODY, font(40, bold=True))
    centred_text(draw, 775, "Was $XXX  |  Now $XXX", GREY, font(32))

    # Red rule
    draw.rectangle([(W - 600) // 2, 840, (W + 600) // 2, 844], fill=ACCENT)

    # What's included
    y = draw_section_header(draw, 880, "WHAT'S INCLUDED")
    included = [
        "Full exterior wash & dry",
        "Interior vacuum & wipe down",
        "Window clean inside & out",
        "Tyre shine",
        "Air freshener",
    ]
    for item in included:
        y = draw_check_item(draw, y, item)

    # Offer expiry
    y += 40
    draw.rectangle([180, y, W - 180, y + 100], fill=LIGHT_GREY_BG, outline=GREY, width=2)
    centred_text(draw, y + 15, "Offer expires: [DATE]", DARK_BODY, font(28, bold=True))
    centred_text(draw, y + 55, "Use code: SUMMER[XX] at booking", ACCENT, font(26, bold=True))
    y += 140

    # Urgent CTA
    centred_text(draw, y, "SPACES ARE LIMITED", ACCENT, font(36, bold=True))
    y += 50
    centred_text(draw, y, "BOOK TODAY", DARK_BODY, font(30, bold=True))
    y += 70

    # Big red BOOK NOW button
    draw_pill(draw, W // 2, y, 700, 90, ACCENT, "BOOK NOW", WHITE, 36)

    draw_footer(draw)

    path = OUTPUT_DIR / "email_06_seasonal_promo.png"
    img.save(path, "PNG")
    print(f"  Saved: {path.name}")
    return path


# ═══════════════════════════════════════════════════════
# PREVIEW GRID (3x2)
# ═══════════════════════════════════════════════════════
def build_preview_grid(paths):
    print("\n[GRID] Building 3x2 preview grid...")
    cols, rows = 3, 2
    thumb_w, thumb_h = 800, 1130
    pad = 40
    grid_w = cols * thumb_w + (cols + 1) * pad
    grid_h = rows * thumb_h + (rows + 1) * pad
    grid = Image.new("RGB", (grid_w, grid_h), BG)

    for idx, p in enumerate(paths):
        r, c = divmod(idx, cols)
        thumb = Image.open(p).convert("RGB")
        thumb.thumbnail((thumb_w, thumb_h), Image.LANCZOS)
        x = pad + c * (thumb_w + pad) + (thumb_w - thumb.width) // 2
        y = pad + r * (thumb_h + pad) + (thumb_h - thumb.height) // 2
        grid.paste(thumb, (x, y))

    out = OUTPUT_DIR / "preview_grid.png"
    grid.save(out, "PNG")
    print(f"  Saved: {out.name} ({grid_w}x{grid_h})")
    return out


# ═══════════════════════════════════════════════════════
# DO SPACES UPLOAD
# ═══════════════════════════════════════════════════════
def upload_to_spaces(paths):
    load_dotenv("/root/NEW-AI-PROJECT/purpleocaz-canva-mcp/.env")
    s3 = boto3.client(
        "s3", region_name="lon1",
        endpoint_url="https://lon1.digitaloceanspaces.com",
        aws_access_key_id=os.getenv("DO_SPACES_KEY"),
        aws_secret_access_key=os.getenv("DO_SPACES_SECRET"),
    )
    bucket = "purpleocaz-assets"
    urls = {}
    for p in paths:
        key = f"email-templates/car-detail/{p.name}"
        print(f"  Uploading {p.name} -> {key}")
        s3.put_object(
            Bucket=bucket, Key=key,
            Body=p.read_bytes(), ContentType="image/png", ACL="public-read",
        )
        urls[p.name] = f"https://purpleocaz-assets.lon1.digitaloceanspaces.com/{key}"
    return urls


# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════
def main():
    print("=" * 60)
    print("CAR DETAILING EMAIL & TEXT MARKETING TEMPLATES — 6 Templates")
    print("=" * 60)

    paths = [
        build_booking_confirm(),
        build_appointment_reminder(),
        build_job_completion(),
        build_followup(),
        build_referral(),
        build_seasonal_promo(),
    ]

    grid_path = build_preview_grid(paths)
    all_paths = paths + [grid_path]

    print("\n" + "=" * 60)
    print("UPLOADING TO DO SPACES")
    print("=" * 60)
    urls = upload_to_spaces(all_paths)

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    for name, url in urls.items():
        size = (OUTPUT_DIR / name).stat().st_size
        print(f"  {name}: {size:,} bytes -> {url}")

    return urls


if __name__ == "__main__":
    main()
