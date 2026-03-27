#!/usr/bin/env python3
"""
Barbershop Client Forms — 3 US Letter PNGs (2550x3300px at 300dpi).
Client consultation, client record card, appointment booking.
Follows barbershop design system: #0A0A0A bg, #C9A96E gold, #FFFFFF white.
"""

import os, re, boto3
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path("/root/NEW-AI-PROJECT")
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "barbershop" / "forms"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"

W, H = 2550, 3300
BG = (10, 10, 10)
GOLD = (201, 169, 110)
WHITE = (255, 255, 255)
GREY = (136, 136, 136)
DARK_TEXT = (10, 10, 10)
FIELD_BG = (245, 245, 245)
FIELD_BORDER = (204, 204, 204)
LINE_GREY = (204, 204, 204)
BODY_WHITE = (255, 255, 255)


def font(size, bold=False, italic=False):
    p = FONT_SERIF if italic else (FONT_BOLD if bold else FONT_REGULAR)
    return ImageFont.truetype(p, size)


def centred(draw, y, text, fill, f):
    bbox = draw.textbbox((0, 0), text, font=f)
    draw.text(((W - (bbox[2] - bbox[0])) // 2, y), text, fill=fill, font=f)


def draw_header(draw):
    draw.rectangle([0, 0, W, 280], fill=BG)
    cx = 1275
    # Scissors icon
    draw.line([(cx - 80, 20), (cx + 80, 120)], fill=GOLD, width=8)
    draw.line([(cx + 80, 20), (cx - 80, 120)], fill=GOLD, width=8)
    for ex, ey in [(cx - 80, 20), (cx + 80, 20), (cx - 80, 120), (cx + 80, 120)]:
        draw.ellipse([ex - 10, ey - 10, ex + 10, ey + 10], outline=GOLD, width=3)
    centred(draw, 140, "YOUR BARBERSHOP NAME", WHITE, font(56, bold=True))
    centred(draw, 195, "MASTER BARBERS", GOLD, font(26))
    draw.rectangle([0, 260, W, 266], fill=GOLD)


def draw_footer(draw):
    draw.rectangle([0, 3020, W, 3300], fill=BG)
    draw.rectangle([0, 3020, W, 3026], fill=GOLD)
    centred(draw, 3070, "YOUR BARBERSHOP NAME", WHITE, font(26, bold=True))
    centred(draw, 3120, "+1 (555) 000-0000  ·  www.yourbarbershop.com  ·  Your City, ST", GOLD, font(20))
    centred(draw, 3190, "Thank you for your business", WHITE, font(22, italic=True))


def section_header(draw, y, text):
    draw.text((180, y), text, fill=GOLD, font=font(28, bold=True))
    draw.rectangle([180, y + 38, 2370, y + 40], fill=GOLD)
    return y + 40


def form_title(draw, y, text):
    draw.text((180, y), text, fill=GOLD, font=font(34, bold=True))
    draw.rectangle([180, y + 45, 2370, y + 48], fill=GOLD)
    return y + 48


def field_box(draw, x1, y1, x2, y2, title=None):
    draw.rectangle([x1, y1, x2, y2], fill=FIELD_BG, outline=FIELD_BORDER, width=2)
    if title:
        draw.text((x1 + 20, y1 + 17), title, fill=GOLD, font=font(22, bold=True))


def dark_box(draw, x1, y1, x2, y2, title=None):
    draw.rectangle([x1, y1, x2, y2], outline=BG, width=3)
    if title:
        draw.text((x1 + 20, y1 + 20), title, fill=GOLD, font=font(22, bold=True))


def gold_box(draw, x1, y1, x2, y2, title=None):
    draw.rectangle([x1, y1, x2, y2], outline=GOLD, width=3)
    if title:
        draw.text((x1 + 20, y1 + 20), title, fill=GOLD, font=font(22, bold=True))


def txt(draw, x, y, text, size=24, color=None, bold=False):
    c = color if color else DARK_TEXT
    draw.text((x, y), text, fill=c, font=font(size, bold=bold))


def checkbox(draw, x, y, label, size=24):
    draw.rectangle([x, y, x + 30, y + 30], outline=GOLD, width=3)
    draw.text((x + 42, y + 1), label, fill=DARK_TEXT, font=font(size))


def lined_rows(draw, y, count, spacing=45, x1=200, x2=2350):
    for i in range(count):
        ly = y + i * spacing
        draw.line([(x1, ly), (x2, ly)], fill=LINE_GREY, width=2)
    return y + count * spacing


# ═══════════════════════════════════════════════════════
# FORM 1 — CLIENT CONSULTATION FORM
# ═══════════════════════════════════════════════════════
def build_consultation():
    print("\n[1/3] Client Consultation Form")
    img = Image.new("RGB", (W, H), BODY_WHITE)
    draw = ImageDraw.Draw(img)
    draw_header(draw)
    draw_footer(draw)

    form_title(draw, 310, "CLIENT CONSULTATION FORM")

    # Personal Details
    field_box(draw, 180, 375, 2370, 570, "PERSONAL DETAILS")
    txt(draw, 200, 442, "Name: ________________________  Date: ________________")
    txt(draw, 200, 492, "Phone: _______________________  Email: ________________")
    txt(draw, 200, 542, "Referred by: ______________________________________________")

    # Hair Profile
    section_header(draw, 595, "HAIR PROFILE")
    col1_items = ["Straight", "Curly", "Fine", "Normal"]
    col2_items = ["Wavy", "Coily", "Thick", "Damaged"]
    for i, item in enumerate(col1_items):
        checkbox(draw, 200, 655 + i * 55, item)
    for i, item in enumerate(col2_items):
        checkbox(draw, 1000, 655 + i * 55, item)

    # Services Interested
    section_header(draw, 920, "SERVICES INTERESTED")
    s1 = ["Haircut", "Hot Towel Shave", "Fade", "Line Up"]
    s2 = ["Beard Trim", "Hair Wash", "Hair Color", "Kids Cut"]
    for i, item in enumerate(s1):
        checkbox(draw, 200, 980 + i * 55, item)
    for i, item in enumerate(s2):
        checkbox(draw, 1000, 980 + i * 55, item)

    # Style Preferences
    section_header(draw, 1240, "STYLE PREFERENCES")
    txt(draw, 180, 1318, "How short on sides? ____________  How short on top? ____________")
    txt(draw, 180, 1378, "Fade level:  ")
    for i, lvl in enumerate(["Low", "Mid", "High", "Skin"]):
        checkbox(draw, 460 + i * 250, 1378, lvl)
    txt(draw, 180, 1438, "Beard:  ")
    for i, b in enumerate(["Full", "Trim", "Shape Up", "Clean Shave"]):
        checkbox(draw, 380 + i * 320, 1438, b)
    txt(draw, 180, 1498, "Style inspiration (describe or bring a photo):")
    lined_rows(draw, 1548, 4, 45, 200, 2350)

    # Allergies & Medical Notes
    section_header(draw, 1748, "ALLERGIES & MEDICAL NOTES")
    field_box(draw, 180, 1806, 2370, 1986)
    lined_rows(draw, 1836, 4, 38, 200, 2350)

    # Previous Experience
    section_header(draw, 2016, "PREVIOUS BARBER EXPERIENCE")
    txt(draw, 180, 2094, "Last haircut: __________________  Previous barber: _______________")
    txt(draw, 180, 2154, "Any issues with previous cuts? _________________________________")
    draw.line([(180, 2220), (2370, 2220)], fill=LINE_GREY, width=2)

    # Customer Declaration
    dark_box(draw, 180, 2260, 2370, 2480, "CUSTOMER DECLARATION")
    txt(draw, 200, 2330, "I confirm the information above is accurate and I consent to", size=21)
    txt(draw, 200, 2365, "the requested services being performed.", size=21)
    txt(draw, 200, 2430, "Signature: ____________________________  Date: ____________")

    path = OUTPUT_DIR / "barber_form_01_consultation.png"
    img.save(path, "PNG")
    print(f"  Saved: {path.name}")
    return path


# ═══════════════════════════════════════════════════════
# FORM 2 — CLIENT RECORD CARD
# ═══════════════════════════════════════════════════════
def build_record_card():
    print("\n[2/3] Client Record Card")
    img = Image.new("RGB", (W, H), BODY_WHITE)
    draw = ImageDraw.Draw(img)
    draw_header(draw)
    draw_footer(draw)

    form_title(draw, 310, "CLIENT RECORD CARD")

    # Client Details
    field_box(draw, 180, 375, 2370, 565, "CLIENT DETAILS")
    txt(draw, 200, 442, "Name: _______________________  Phone: _____________________")
    txt(draw, 200, 492, "Email: _______________________  DOB: ______________________")
    txt(draw, 200, 542, "Member since: ________________  Status:  ")
    for i, s in enumerate(["Standard", "Regular", "VIP"]):
        checkbox(draw, 1380 + i * 280, 542, s, size=22)

    # Visit History
    section_header(draw, 590, "VISIT HISTORY")
    # Table header
    th_y = 648
    draw.rectangle([180, th_y, 2370, th_y + 50], fill=BG)
    cols = [("DATE", 200), ("SERVICE", 560), ("BARBER", 1080), ("NOTES", 1500), ("PRICE", 2200)]
    for label, x in cols:
        draw.text((x, th_y + 12), label, fill=WHITE, font=font(20, bold=True))
    # Column dividers
    for cx in [540, 1060, 1480, 2180]:
        draw.line([(cx, th_y), (cx, th_y + 50 + 5 * 90)], fill=LINE_GREY, width=1)
    # 5 data rows
    for r in range(5):
        ry = th_y + 50 + r * 90
        bg = BODY_WHITE if r % 2 == 0 else FIELD_BG
        draw.rectangle([180, ry, 2370, ry + 90], fill=bg, outline=LINE_GREY, width=1)

    # Regular Preferences
    section_header(draw, 1420, "REGULAR PREFERENCES")
    txt(draw, 180, 1498, "Fade style: _________________  Top length: _________________")
    txt(draw, 180, 1558, "Beard preference: ___________  Part:  ")
    for i, p in enumerate(["Left", "Right", "None"]):
        checkbox(draw, 1340 + i * 260, 1558, p, size=22)
    txt(draw, 180, 1618, "Products used: ____________________________________________")
    txt(draw, 180, 1678, "Allergies/notes: ___________________________________________")

    # Loyalty Tracker
    section_header(draw, 1738, "LOYALTY TRACKER")
    circle_r = 40
    start_x = 260
    spacing = (2300 - start_x) // 9
    for i in range(10):
        cx = start_x + i * spacing
        cy = 1850
        draw.ellipse([cx - circle_r, cy - circle_r, cx + circle_r, cy + circle_r],
                     outline=GOLD, width=3)
        # Number below
        num = str(i + 1)
        bbox = draw.textbbox((0, 0), num, font=font(18))
        nw = bbox[2] - bbox[0]
        draw.text((cx - nw // 2, cy + circle_r + 10), num, fill=GREY, font=font(18))

    centred(draw, 1960, "YOUR 10TH CUT IS FREE", GOLD, font(26, bold=True))
    txt(draw, 180, 2020, "Visits this year: ______  Total visits: ______  Total spend: $______")

    # Notes
    section_header(draw, 2080, "NOTES")
    lined_rows(draw, 2138, 6, 60, 200, 2350)

    path = OUTPUT_DIR / "barber_form_02_record_card.png"
    img.save(path, "PNG")
    print(f"  Saved: {path.name}")
    return path


# ═══════════════════════════════════════════════════════
# FORM 3 — APPOINTMENT BOOKING FORM
# ═══════════════════════════════════════════════════════
def build_booking():
    print("\n[3/3] Appointment Booking Form")
    img = Image.new("RGB", (W, H), BODY_WHITE)
    draw = ImageDraw.Draw(img)
    draw_header(draw)
    draw_footer(draw)

    form_title(draw, 310, "APPOINTMENT BOOKING FORM")

    # Client Details
    field_box(draw, 180, 375, 2370, 535, "CLIENT DETAILS")
    txt(draw, 200, 442, "Name: _______________________  Phone: _____________________")
    txt(draw, 200, 492, "Email: _______________________  New client:  ")
    checkbox(draw, 1400, 492, "Yes", size=22)
    checkbox(draw, 1600, 492, "No", size=22)

    # Appointment Request
    section_header(draw, 560, "APPOINTMENT REQUEST")
    txt(draw, 180, 638, "Preferred date: ________________  Time: ___________________")
    txt(draw, 180, 698, "Alternative date: ______________  Time: ___________________")
    txt(draw, 180, 758, "Service requested: _________________________________________")
    txt(draw, 180, 818, "Preferred barber: ______________  ")
    checkbox(draw, 1200, 818, "No preference", size=22)
    txt(draw, 180, 878, "Duration:  ")
    for i, d in enumerate(["30 min", "45 min", "60 min", "90 min"]):
        checkbox(draw, 420 + i * 340, 878, d, size=22)

    # Deposit Information
    gold_box(draw, 180, 938, 2370, 1118, "DEPOSIT INFORMATION")
    txt(draw, 200, 1008, "Deposit required: $___________")
    txt(draw, 200, 1048, "Deposit paid:  ")
    checkbox(draw, 530, 1048, "Yes", size=22)
    checkbox(draw, 730, 1048, "No", size=22)
    txt(draw, 200, 1088, "Payment:  ")
    for i, pm in enumerate(["Cash", "Card", "Venmo", "CashApp", "Zelle"]):
        checkbox(draw, 400 + i * 340, 1088, pm, size=20)

    # Booking Confirmation
    section_header(draw, 1148, "BOOKING CONFIRMATION")
    txt(draw, 180, 1226, "Confirmed by: _________________  Date: ___________________")
    txt(draw, 180, 1286, "Reminder sent:  ")
    checkbox(draw, 530, 1286, "Yes", size=22)
    checkbox(draw, 730, 1286, "No", size=22)
    txt(draw, 950, 1286, "Via:  ")
    for i, v in enumerate(["Text", "Email", "Call"]):
        checkbox(draw, 1080 + i * 280, 1286, v, size=22)

    # Cancellation Policy
    field_box(draw, 180, 1346, 2370, 1556, "CANCELLATION POLICY")
    txt(draw, 200, 1416, "24 hours notice required for cancellations and rescheduling.", size=22)
    txt(draw, 200, 1466, "Late cancellation fee: $___________", size=22)
    txt(draw, 200, 1506, "No-show fee: $___________", size=22)

    # Signature
    dark_box(draw, 180, 1586, 2370, 1786)
    txt(draw, 200, 1616, "I agree to the cancellation policy stated above.", size=22)
    txt(draw, 200, 1706, "Signature: ____________________________  Date: ____________")

    path = OUTPUT_DIR / "barber_form_03_booking.png"
    img.save(path, "PNG")
    print(f"  Saved: {path.name}")
    return path


# ═══════════════════════════════════════════════════════
# PREVIEW GRID (3x1)
# ═══════════════════════════════════════════════════════
def build_preview_grid(paths):
    print("\n[GRID] Building 3x1 preview grid...")
    tw, th = 1080, 1080
    pad = 0
    gw = 3 * tw
    gh = th
    grid = Image.new("RGB", (gw, gh), BG)
    for idx, p in enumerate(paths):
        thumb = Image.open(p).convert("RGB")
        thumb.thumbnail((tw, th), Image.LANCZOS)
        x = idx * tw + (tw - thumb.width) // 2
        y = (th - thumb.height) // 2
        grid.paste(thumb, (x, y))
    out = OUTPUT_DIR / "preview_grid.png"
    grid.save(out, "PNG")
    print(f"  Saved: {out.name} ({gw}x{gh})")
    return out


# ═══════════════════════════════════════════════════════
# UPLOAD TO SPACES
# ═══════════════════════════════════════════════════════
def upload_to_spaces(paths):
    env = open("/root/NEW-AI-PROJECT/purpleocaz-canva-mcp/.env").read()
    key = re.search(r'DO_SPACES_KEY=(\S+)', env).group(1)
    secret = re.search(r'DO_SPACES_SECRET=(\S+)', env).group(1)
    s3 = boto3.client("s3", endpoint_url="https://lon1.digitaloceanspaces.com",
                      aws_access_key_id=key, aws_secret_access_key=secret)
    urls = {}
    for p in paths:
        sk = f"barbershop/forms/{p.name}"
        print(f"  Uploading {p.name}")
        s3.put_object(Bucket="purpleocaz-assets", Key=sk,
                      Body=p.read_bytes(), ContentType="image/png", ACL="public-read")
        urls[p.name] = f"https://purpleocaz-assets.lon1.digitaloceanspaces.com/{sk}"
    return urls


def main():
    print("=" * 60)
    print("BARBERSHOP CLIENT FORMS — 3 Templates")
    print("=" * 60)

    paths = [build_consultation(), build_record_card(), build_booking()]
    grid = build_preview_grid(paths)
    all_paths = paths + [grid]

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


if __name__ == "__main__":
    main()
