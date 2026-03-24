#!/usr/bin/env python3
"""
Car Detailing Vehicle Condition & Job Forms — 3 A4 PNGs.
Pre-detail condition report, detailing job checklist, post-detail handover.
Uploads to DO Spaces and builds a 3x1 preview grid.
"""

import os
import boto3
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ── Paths & Config ─────────────────────────────────────
PROJECT_ROOT = Path("/root/NEW-AI-PROJECT")
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "car-detail-job-forms"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

W, H = 2480, 3508

BG = (13, 13, 13)
ACCENT = (224, 32, 32)
WHITE = (255, 255, 255)
SILVER = (192, 192, 192)
BODY_WHITE = (255, 255, 255)
DARK_TEXT = (40, 40, 40)
GREY = (160, 160, 160)
LIGHT_BG = (245, 245, 245)
LINE_GREY = (200, 200, 200)


def font(size, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REGULAR, size)


def centred(draw, y, text, fill, f):
    bbox = draw.textbbox((0, 0), text, font=f)
    draw.text(((W - (bbox[2] - bbox[0])) // 2, y), text, fill=fill, font=f)


def draw_header(draw, title, subtitle):
    draw.rectangle([0, 0, W, 380], fill=BG)
    centred(draw, 80, "YOUR STUDIO NAME", WHITE, font(72, True))
    centred(draw, 170, "CAR DETAILING SPECIALIST", ACCENT, font(36))
    draw.rectangle([0, 240, W, 246], fill=ACCENT)
    centred(draw, 280, title, WHITE, font(48, True))
    draw.rectangle([0, 370, W, 380], fill=ACCENT)


def draw_footer(draw, y=3200):
    draw.rectangle([0, y, W, H], fill=BG)
    centred(draw, y + 60, "YOUR STUDIO NAME  |  +1 (555) 000-0000  |  www.yourstudio.com", SILVER, font(24))
    centred(draw, y + 110, "hello@yourstudio.com  |  Your City, State", SILVER, font(22))


def section_header(draw, y, text):
    draw.rectangle([140, y, 152, y + 32], fill=ACCENT)
    draw.text((170, y - 2), text, fill=ACCENT, font=font(30, True))
    return y + 55


def form_line(draw, y, label, line_w=600, x=170):
    draw.text((x, y), label, fill=DARK_TEXT, font=font(24))
    lx = x + draw.textbbox((0, 0), label, font=font(24))[2] + 15
    draw.line([(lx, y + 30), (lx + line_w, y + 30)], fill=LINE_GREY, width=2)
    return y + 50


def form_line_pair(draw, y, label1, label2, x1=170, x2=1300):
    form_line(draw, y, label1, line_w=500, x=x1)
    form_line(draw, y, label2, line_w=500, x=x2)
    return y + 50


def checkbox(draw, x, y, text, size=26):
    s = size
    draw.rectangle([x, y + 2, x + s, y + 2 + s], outline=DARK_TEXT, width=2)
    draw.text((x + s + 12, y), text, fill=DARK_TEXT, font=font(24))
    return y + 45


def checkbox_with_init(draw, x, y, text, w=1800):
    s = 26
    draw.rectangle([x, y + 2, x + s, y + 2 + s], outline=DARK_TEXT, width=2)
    draw.text((x + s + 12, y), text, fill=DARK_TEXT, font=font(22))
    # initials line at right
    draw.text((w, y + 2), "Init:", fill=GREY, font=font(18))
    draw.line([(w + 50, y + 28), (w + 160, y + 28)], fill=LINE_GREY, width=2)
    return y + 42


def detail_box(draw, x, y, w, h, title=None):
    draw.rectangle([x, y, x + w, y + h], outline=DARK_TEXT, width=2)
    if title:
        draw.rectangle([x, y, x + w, y + 6], fill=ACCENT)
    return y + 10


def check_item_red(draw, y, text, x=210):
    draw.text((x, y), ">", fill=ACCENT, font=font(22, True))
    draw.text((x + 30, y), text, fill=DARK_TEXT, font=font(24))
    return y + 42


# ═══════════════════════════════════════════════════════
# TEMPLATE 1 — PRE-DETAIL VEHICLE CONDITION REPORT
# ═══════════════════════════════════════════════════════
def build_condition_report():
    print("\n[1/3] Vehicle Condition Report")
    img = Image.new("RGB", (W, H), BODY_WHITE)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "VEHICLE CONDITION REPORT", "Pre-Detail Inspection")
    centred(draw, 340, "Pre-Detail Inspection", SILVER, font(22))

    y = 420

    # Customer Details
    y = section_header(draw, y, "CUSTOMER DETAILS")
    box_top = y
    detail_box(draw, 140, y, W - 280, 180, title=True)
    y += 20
    y = form_line_pair(draw, y, "Name:", "Phone:", 170, 1300)
    y = form_line_pair(draw, y, "Email:", "Date:", 170, 1300)
    form_line(draw, y, "Time:", line_w=400, x=1300)
    y = box_top + 200

    # Vehicle Details
    y = section_header(draw, y, "VEHICLE DETAILS")
    detail_box(draw, 140, y, W - 280, 180, title=True)
    y += 20
    y = form_line_pair(draw, y, "Make:", "Model:", 170, 1300)
    y = form_line_pair(draw, y, "Year:", "Colour:", 170, 1300)
    form_line_pair(draw, y, "Reg/VIN:", "Mileage:", 170, 1300)
    y += 70

    # Service Requested
    y = section_header(draw, y, "SERVICE REQUESTED")
    services_l = ["Exterior Wash", "Paint Correction", "Engine Bay", "Other:"]
    services_r = ["Interior Detail", "Ceramic Coating", "Full Detail"]
    for i, svc in enumerate(services_l):
        checkbox(draw, 200, y + i * 45, svc)
    for i, svc in enumerate(services_r):
        checkbox(draw, 1100, y + i * 45, svc)
    # Other line
    draw.line([(550, y + 3 * 45 + 28), (900, y + 3 * 45 + 28)], fill=LINE_GREY, width=2)
    y += len(services_l) * 45 + 30

    # Vehicle Condition Map
    y = section_header(draw, y, "VEHICLE CONDITION MAP")

    # Simple top-down car rectangle with 4 wheel circles
    car_cx, car_cy = W // 2, y + 220
    car_w, car_h = 400, 600
    # Body
    draw.rounded_rectangle(
        [car_cx - car_w // 2, car_cy - car_h // 2,
         car_cx + car_w // 2, car_cy + car_h // 2],
        radius=40, outline=DARK_TEXT, width=3
    )
    # Windshield line
    draw.line([(car_cx - 140, car_cy - 180), (car_cx + 140, car_cy - 180)], fill=DARK_TEXT, width=2)
    # Rear window line
    draw.line([(car_cx - 140, car_cy + 180), (car_cx + 140, car_cy + 180)], fill=DARK_TEXT, width=2)
    # 4 wheels
    wh = 70
    ww = 35
    for wx, wy in [
        (car_cx - car_w // 2 - ww // 2, car_cy - 160),
        (car_cx + car_w // 2 - ww // 2, car_cy - 160),
        (car_cx - car_w // 2 - ww // 2, car_cy + 160),
        (car_cx + car_w // 2 - ww // 2, car_cy + 160),
    ]:
        draw.rounded_rectangle([wx, wy, wx + ww, wy + wh], radius=8, fill=DARK_TEXT)
    # Labels
    draw.text((car_cx - 35, car_cy - car_h // 2 - 35), "FRONT", fill=ACCENT, font=font(22, True))
    draw.text((car_cx - 30, car_cy + car_h // 2 + 10), "REAR", fill=ACCENT, font=font(22, True))
    draw.text((car_cx - car_w // 2 - 120, car_cy - 10), "LEFT", fill=ACCENT, font=font(22, True))
    draw.text((car_cx + car_w // 2 + 30, car_cy - 10), "RIGHT", fill=ACCENT, font=font(22, True))

    centred(draw, car_cy + car_h // 2 + 50, "Mark any existing damage with X", GREY, font(22))

    y = car_cy + car_h // 2 + 90

    # Condition scale
    draw.text((170, y), "Condition:", fill=DARK_TEXT, font=font(24, True))
    cx = 420
    for label in ["Excellent", "Good", "Fair", "Poor"]:
        checkbox(draw, cx, y, label)
        cx += 300
    y += 60

    # Existing Damage Notes
    y = section_header(draw, y, "EXISTING DAMAGE NOTES")
    for i in range(4):
        draw.line([(170, y + 35), (W - 170, y + 35)], fill=LINE_GREY, width=2)
        y += 50

    # Customer Declaration
    y += 10
    detail_box(draw, 140, y, W - 280, 200, title=True)
    y += 15
    draw.text((170, y), "CUSTOMER DECLARATION", fill=ACCENT, font=font(22, True))
    y += 35
    draw.text((170, y), "I confirm the above accurately reflects the condition of my vehicle", fill=DARK_TEXT, font=font(22))
    y += 30
    draw.text((170, y), "prior to detailing services.", fill=DARK_TEXT, font=font(22))
    y += 50
    form_line_pair(draw, y, "Signature:", "Date:", 170, 1300)

    draw_footer(draw)

    path = OUTPUT_DIR / "jobform_01_condition_report.png"
    img.save(path, "PNG")
    print(f"  Saved: {path.name}")
    return path


# ═══════════════════════════════════════════════════════
# TEMPLATE 2 — DETAILING JOB CHECKLIST
# ═══════════════════════════════════════════════════════
def build_job_checklist():
    print("\n[2/3] Detailing Job Checklist")
    img = Image.new("RGB", (W, H), BODY_WHITE)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "DETAILING JOB CHECKLIST", "Technician Work Record")
    centred(draw, 340, "Technician Work Record", SILVER, font(22))

    y = 420

    # Job Details
    y = section_header(draw, y, "JOB DETAILS")
    detail_box(draw, 140, y, W - 280, 180, title=True)
    y += 20
    y = form_line_pair(draw, y, "Job #:", "Date:", 170, 1300)
    y = form_line_pair(draw, y, "Vehicle:", "Technician:", 170, 1300)
    form_line(draw, y, "Service:", line_w=700, x=170)
    y += 80

    # Exterior Checklist
    y = section_header(draw, y, "EXTERIOR CHECKLIST")
    ext_items = [
        "Pre-rinse & snow foam application",
        "Two-bucket hand wash",
        "Wheel & tyre cleaning",
        "Door jambs & shuts",
        "Clay bar decontamination",
        "Paint correction / polish",
        "Wax / sealant application",
        "Window clean (exterior)",
        "Tyre dressing applied",
        "Final exterior rinse & dry",
    ]
    for item in ext_items:
        y = checkbox_with_init(draw, 200, y, item)

    y += 15

    # Interior Checklist
    y = section_header(draw, y, "INTERIOR CHECKLIST")
    int_items = [
        "Full vacuum (seats, carpets, boot)",
        "Dashboard & console wipe down",
        "Door cards & pockets cleaned",
        "Window clean (interior)",
        "Leather treatment (if applicable)",
        "Air freshener applied",
        "Final interior inspection",
    ]
    for item in int_items:
        y = checkbox_with_init(draw, 200, y, item)

    y += 15

    # Quality Check
    y = section_header(draw, y, "QUALITY CHECK")
    qa_items = [
        "Exterior — no water spots or streaks",
        "Interior — no dust or residue",
        "Customer notified job complete",
        "Photos taken (before & after)",
    ]
    for item in qa_items:
        y = checkbox_with_init(draw, 200, y, item)

    y += 25

    # Technician Sign-Off
    detail_box(draw, 140, y, W - 280, 200, title=True)
    y += 15
    draw.text((170, y), "TECHNICIAN SIGN-OFF", fill=ACCENT, font=font(22, True))
    y += 40
    y = form_line_pair(draw, y, "Technician:", "Signature:", 170, 1300)
    y = form_line_pair(draw, y, "Time completed:", "Quality checked by:", 170, 1300)
    form_line(draw, y, "QC Signature:", line_w=500, x=1300)

    draw_footer(draw)

    path = OUTPUT_DIR / "jobform_02_job_checklist.png"
    img.save(path, "PNG")
    print(f"  Saved: {path.name}")
    return path


# ═══════════════════════════════════════════════════════
# TEMPLATE 3 — POST-DETAIL HANDOVER FORM
# ═══════════════════════════════════════════════════════
def build_handover():
    print("\n[3/3] Post-Detail Handover Form")
    img = Image.new("RGB", (W, H), BODY_WHITE)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "VEHICLE HANDOVER", "Post-Detail Customer Sign-Off")
    centred(draw, 340, "Post-Detail Customer Sign-Off", SILVER, font(22))

    y = 420

    # Job Summary
    y = section_header(draw, y, "JOB SUMMARY")
    detail_box(draw, 140, y, W - 280, 180, title=True)
    y += 20
    y = form_line_pair(draw, y, "Job #:", "Date:", 170, 1300)
    y = form_line_pair(draw, y, "Vehicle:", "Technician:", 170, 1300)
    form_line(draw, y, "Service completed:", line_w=600, x=170)
    y += 80

    # Services Completed
    y = section_header(draw, y, "SERVICES COMPLETED")
    completed = [
        "Exterior wash & dry",
        "Interior vacuum & wipe down",
        "Dashboard & console clean",
        "Window clean (inside & out)",
        "Wheel & tyre cleaning",
        "Tyre dressing",
        "Air freshener",
    ]
    for item in completed:
        y = checkbox(draw, 200, y, item)

    y += 10

    # Aftercare Advice
    y = section_header(draw, y, "AFTERCARE ADVICE")
    draw.text((210, y), "To maintain your detail results:", fill=DARK_TEXT, font=font(24))
    y += 45
    advice = [
        "Avoid washing for 24 hours",
        "Avoid direct sunlight for 2 hours",
        "Use pH-neutral shampoo for future washes",
        "Consider a maintenance detail every 8-12 weeks",
    ]
    for item in advice:
        y = check_item_red(draw, y, item)

    y += 15

    # Payment Summary
    y = section_header(draw, y, "PAYMENT SUMMARY")
    detail_box(draw, 140, y, W - 280, 220, title=True)
    y += 20
    y = form_line_pair(draw, y, "Service:", "Amount: $", 170, 1300)
    y += 10
    draw.text((170, y), "Payment method:", fill=DARK_TEXT, font=font(24))
    cx = 520
    for method in ["Cash", "Card", "Bank Transfer"]:
        checkbox(draw, cx, y, method)
        cx += 380
    y += 55
    draw.text((170, y), "Paid:", fill=DARK_TEXT, font=font(24))
    checkbox(draw, 320, y, "Yes")
    checkbox(draw, 520, y, "Invoice sent")
    y += 70

    # Review Request
    y = section_header(draw, y, "REVIEW REQUEST")
    draw.text((210, y), "Enjoyed your detail? We'd love a review!", fill=DARK_TEXT, font=font(24))
    y += 45
    y = form_line(draw, y, "Google:", line_w=700, x=210)
    y = form_line(draw, y, "Yelp:", line_w=700, x=210)
    y = form_line(draw, y, "Facebook:", line_w=700, x=210)

    y += 10

    # Customer Sign-Off
    detail_box(draw, 140, y, W - 280, 260, title=True)
    y += 15
    draw.text((170, y), "CUSTOMER SIGN-OFF", fill=ACCENT, font=font(22, True))
    y += 35
    draw.text((170, y), "I am satisfied with the detailing services provided and confirm", fill=DARK_TEXT, font=font(22))
    y += 30
    draw.text((170, y), "my vehicle has been returned in good order.", fill=DARK_TEXT, font=font(22))
    y += 50
    y = form_line_pair(draw, y, "Signature:", "Date:", 170, 1300)
    form_line(draw, y, "Print name:", line_w=600, x=170)

    draw_footer(draw)

    path = OUTPUT_DIR / "jobform_03_handover.png"
    img.save(path, "PNG")
    print(f"  Saved: {path.name}")
    return path


# ═══════════════════════════════════════════════════════
# PREVIEW GRID (3x1 horizontal)
# ═══════════════════════════════════════════════════════
def build_preview_grid(paths):
    print("\n[GRID] Building 3x1 preview grid...")
    thumb_w, thumb_h = 800, 1130
    pad = 40
    gw = 3 * thumb_w + 4 * pad
    gh = thumb_h + 2 * pad
    grid = Image.new("RGB", (gw, gh), BG)

    for idx, p in enumerate(paths):
        thumb = Image.open(p).convert("RGB")
        thumb.thumbnail((thumb_w, thumb_h), Image.LANCZOS)
        x = pad + idx * (thumb_w + pad) + (thumb_w - thumb.width) // 2
        y = pad + (thumb_h - thumb.height) // 2
        grid.paste(thumb, (x, y))

    out = OUTPUT_DIR / "preview_grid.png"
    grid.save(out, "PNG")
    print(f"  Saved: {out.name} ({gw}x{gh})")
    return out


# ═══════════════════════════════════════════════════════
# DO SPACES UPLOAD
# ═══════════════════════════════════════════════════════
def upload_to_spaces(paths):
    env_text = open("/root/NEW-AI-PROJECT/purpleocaz-canva-mcp/.env").read()
    key = re.search(r'DO_SPACES_KEY=(\S+)', env_text).group(1)
    secret = re.search(r'DO_SPACES_SECRET=(\S+)', env_text).group(1)
    s3 = boto3.client("s3", endpoint_url="https://lon1.digitaloceanspaces.com",
                      aws_access_key_id=key, aws_secret_access_key=secret)
    urls = {}
    for p in paths:
        sk = f"job-forms/car-detail/{p.name}"
        print(f"  Uploading {p.name} -> {sk}")
        s3.put_object(Bucket="purpleocaz-assets", Key=sk,
                      Body=p.read_bytes(), ContentType="image/png", ACL="public-read")
        urls[p.name] = f"https://purpleocaz-assets.lon1.digitaloceanspaces.com/{sk}"
    return urls


def main():
    print("=" * 60)
    print("CAR DETAILING VEHICLE CONDITION & JOB FORMS — 3 Templates")
    print("=" * 60)

    paths = [build_condition_report(), build_job_checklist(), build_handover()]
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

    return urls


if __name__ == "__main__":
    main()
