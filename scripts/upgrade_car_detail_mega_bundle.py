#!/usr/bin/env python3
"""
Car Detailing Mega Bundle Upgrade — adds appointment cards + welcome sign.

Steps:
  1. Build 3 new templates (appointment card dark, light, welcome sign) with Pillow
  2. Upload to DO Spaces
  3. Regenerate Delivery_Mega_Bundle.pdf (53 templates, 9 sections)
  4. Upload new delivery PDF to Spaces
  5. Replace delivery file on Etsy listing #4476909005
  6. PATCH listing price to £39.99
  7. PATCH listing title + description
  8. Verify

Run from project root:
    python scripts/upgrade_car_detail_mega_bundle.py
"""

import io
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

import boto3
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.colors import HexColor, white as rl_white
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as rl_canvas

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT)

# ── Paths ─────────────────────────────────────────────────────────────────────
OUTPUT_DIR = os.path.join(PROJECT, "outputs", "car-detail-mega-bundle")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Fonts ─────────────────────────────────────────────────────────────────────
FONT_BOLD    = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"


def _font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def _center(draw, text, y, fnt, fill, canvas_w):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    tw = bbox[2] - bbox[0]
    draw.text(((canvas_w - tw) // 2, y), text, font=fnt, fill=fill)


# ── Colours ───────────────────────────────────────────────────────────────────
BG      = (13, 13, 13)        # #0D0D0D
ACCENT  = (224, 32, 32)       # #E02020
WHITE   = (255, 255, 255)
SILVER  = (192, 192, 192)
PANEL   = (26, 26, 26)        # #1A1A1A
LIGHT_BG = (248, 248, 248)    # #F8F8F8
LIGHT_PANEL = (235, 235, 235) # #EBEBEB


# ═══════════════════════════════════════════════════════════════════════════════
# TEMPLATE 1 — APPOINTMENT CARD DARK  (1050 × 600, CR80 proportions)
# ═══════════════════════════════════════════════════════════════════════════════
def build_appointment_card_dark():
    print("\n[1/3] Appointment Card — Dark")
    W, H = 1050, 600
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Red bars top + bottom
    draw.rectangle([0, 0, W, 6], fill=ACCENT)
    draw.rectangle([0, H - 6, W, H], fill=ACCENT)

    # Left red accent column
    draw.rectangle([0, 6, 8, H - 6], fill=ACCENT)

    # Header panel (38% height)
    header_h = int(H * 0.38)
    draw.rectangle([0, 6, W, header_h], fill=PANEL)

    # Header text
    _center(draw, "YOUR NEXT APPOINTMENT", header_h // 2 - 22,
            _font(FONT_BOLD, 30), WHITE, W)
    _center(draw, "CAR DETAILING SPECIALIST", header_h // 2 + 18,
            _font(FONT_REGULAR, 15), ACCENT, W)

    # Red divider
    draw.rectangle([30, header_h + 2, W - 30, header_h + 4], fill=ACCENT)

    # Form fields
    mx = 50
    fields = [
        ("Date",       header_h + 24),
        ("Time",       header_h + 70),
        ("Service",    header_h + 116),
        ("Technician", header_h + 162),
        ("Notes",      header_h + 208),
    ]
    for label, y in fields:
        draw.text((mx, y), f"{label}:", fill=SILVER, font=_font(FONT_BOLD, 13))
        lbl_w = draw.textbbox((mx, y), f"{label}:", font=_font(FONT_BOLD, 13))[2]
        draw.rectangle([lbl_w + 12, y + 16, W - 50, y + 17], fill=ACCENT)

    # Footer
    footer = "We look forward to seeing you · Call or text to reschedule"
    _center(draw, footer, H - 36, _font(FONT_REGULAR, 11), SILVER, W)

    path = os.path.join(OUTPUT_DIR, "cd_appointment_card_dark.png")
    img.save(path, "PNG")
    print(f"  Saved: {os.path.basename(path)} ({W}×{H})")
    return path


# ═══════════════════════════════════════════════════════════════════════════════
# TEMPLATE 2 — APPOINTMENT CARD LIGHT  (1050 × 600)
# ═══════════════════════════════════════════════════════════════════════════════
def build_appointment_card_light():
    print("\n[2/3] Appointment Card — Light")
    W, H = 1050, 600
    img = Image.new("RGB", (W, H), LIGHT_BG)
    draw = ImageDraw.Draw(img)

    # Red bars top + bottom
    draw.rectangle([0, 0, W, 6], fill=ACCENT)
    draw.rectangle([0, H - 6, W, H], fill=ACCENT)

    # Dark header panel
    header_h = int(H * 0.38)
    draw.rectangle([0, 6, W, header_h], fill=BG)

    # Header text
    _center(draw, "YOUR NEXT APPOINTMENT", header_h // 2 - 22,
            _font(FONT_BOLD, 30), WHITE, W)
    _center(draw, "CAR DETAILING SPECIALIST", header_h // 2 + 18,
            _font(FONT_REGULAR, 15), ACCENT, W)

    # Red divider
    draw.rectangle([30, header_h + 2, W - 30, header_h + 4], fill=ACCENT)

    # Light panel background
    draw.rectangle([0, header_h, W, H - 6], fill=LIGHT_BG)

    # Form fields
    mx = 50
    DARK_TEXT = (40, 40, 40)
    fields = [
        ("Date",       header_h + 24),
        ("Time",       header_h + 70),
        ("Service",    header_h + 116),
        ("Technician", header_h + 162),
        ("Notes",      header_h + 208),
    ]
    for label, y in fields:
        draw.text((mx, y), f"{label}:", fill=DARK_TEXT, font=_font(FONT_BOLD, 13))
        lbl_w = draw.textbbox((mx, y), f"{label}:", font=_font(FONT_BOLD, 13))[2]
        draw.rectangle([lbl_w + 12, y + 16, W - 50, y + 17], fill=ACCENT)

    # Studio name placeholder at bottom-right
    draw.text((W - 310, H - 36), "YOUR STUDIO NAME  |  Car Detailing",
              fill=ACCENT, font=_font(FONT_BOLD, 12))

    path = os.path.join(OUTPUT_DIR, "cd_appointment_card_light.png")
    img.save(path, "PNG")
    print(f"  Saved: {os.path.basename(path)} ({W}×{H})")
    return path


# ═══════════════════════════════════════════════════════════════════════════════
# TEMPLATE 3 — WELCOME SIGN  (2480 × 3508, A4 portrait @ 300 dpi)
# ═══════════════════════════════════════════════════════════════════════════════
def build_welcome_sign():
    print("\n[3/3] Welcome Sign — A4 Portrait")
    W, H = 2480, 3508
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Subtle diagonal texture overlay
    from PIL import Image as PILImage
    overlay = PILImage.new("RGBA", (W, H), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    for i in range(30):
        x = i * 120 - 500
        odraw.line([(x, 0), (x + H, H)], fill=(255, 255, 255, 5), width=1)
    img = PILImage.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Red bars top + bottom
    draw.rectangle([0, 0, W, 20], fill=ACCENT)
    draw.rectangle([0, H - 20, W, H], fill=ACCENT)

    # Top accent bar (thick)
    draw.rectangle([0, 20, W, 120], fill=ACCENT)

    # Studio name in top bar
    _center(draw, "YOUR STUDIO NAME", 42, _font(FONT_BOLD, 52), WHITE, W)

    # Red rule
    draw.rectangle([80, 150, W - 80, 158], fill=ACCENT)

    # WELCOME headline
    _center(draw, "WELCOME", 200, _font(FONT_BOLD, 240), WHITE, W)

    # Subheadline
    _center(draw, "CAR DETAILING SPECIALIST", 480, _font(FONT_REGULAR, 72), ACCENT, W)

    # Red rule
    draw.rectangle([80, 600, W - 80, 608], fill=ACCENT)

    # Tagline
    _center(draw, "We're glad you're here. Our team will be right with you.",
            650, _font(FONT_REGULAR, 48), SILVER, W)

    # Services section
    _center(draw, "OUR SERVICES", 820, _font(FONT_BOLD, 56), WHITE, W)
    draw.rectangle([80, 890, W - 80, 894], fill=PANEL)

    services = [
        "Exterior Detail",
        "Interior Detail",
        "Paint Correction",
        "Ceramic Coating",
        "Engine Bay Clean",
        "Mobile Service Available",
    ]
    y = 930
    for svc in services:
        # Red bullet
        draw.rectangle([140, y + 22, 152, y + 34], fill=ACCENT)
        draw.text((180, y), svc, fill=WHITE, font=_font(FONT_REGULAR, 56))
        y += 100

    # Red rule before footer
    draw.rectangle([80, y + 30, W - 80, y + 34], fill=ACCENT)

    # Contact placeholders
    y += 70
    _center(draw, "Tel: +1 (555) 000-0000", y, _font(FONT_REGULAR, 52), SILVER, W)
    y += 80
    _center(draw, "www.yourstudio.com  |  Your City, State", y,
            _font(FONT_REGULAR, 46), SILVER, W)

    # Footer
    draw.rectangle([0, H - 160, W, H - 20], fill=PANEL)
    _center(draw, "Thank you for choosing us — we'll be with you shortly.",
            H - 130, _font(FONT_REGULAR, 42), SILVER, W)

    path = os.path.join(OUTPUT_DIR, "cd_welcome_sign.png")
    img.save(path, "PNG")
    print(f"  Saved: {os.path.basename(path)} ({W}×{H})")
    return path


# ═══════════════════════════════════════════════════════════════════════════════
# SPACES UPLOAD
# ═══════════════════════════════════════════════════════════════════════════════
def load_env():
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


def upload_file(s3, local_path, spaces_key):
    bucket = os.environ.get("DO_SPACES_BUCKET", "purpleocaz-assets")
    content_type = "application/pdf" if local_path.endswith(".pdf") else "image/png"
    s3.upload_file(
        local_path, bucket, spaces_key,
        ExtraArgs={"ACL": "public-read", "ContentType": content_type},
    )
    cdn_base = os.environ.get("DO_SPACES_CDN_BASE",
                              "https://purpleocaz-assets.lon1.digitaloceanspaces.com")
    url = f"{cdn_base}/{spaces_key}"
    print(f"  Uploaded → {url}")
    return url


# ═══════════════════════════════════════════════════════════════════════════════
# DELIVERY PDF
# ═══════════════════════════════════════════════════════════════════════════════
# All shortlinks pulled from design_registry.json / existing delivery PDF
SOCIAL_LINKS = [
    ("Post 01 — Premium Detailing Services",  "https://www.canva.com/d/fKxNNBGipTeBPyj"),
    ("Post 02 — Ceramic Coating",             "https://www.canva.com/d/kL2az2XzQISNP33"),
    ("Post 03 — Interior Detailing",          "https://www.canva.com/d/LISdwiNJTOZ37Ue"),
    ("Post 04 — Paint Correction",            "https://www.canva.com/d/hFqCQB5u0rQGM1K"),
    ("Post 05 — Detailing Packages",          "https://www.canva.com/d/a-nkYv1rV7Lsw_N"),
    ("Post 06 — Limited Time Offer",          "https://www.canva.com/d/51KqgMnKUlb-wzh"),
    ("Post 07 — Free Quote",                  "https://www.canva.com/d/fZ6uOaXYSH4xezI"),
    ("Post 08 — Referral Offer",              "https://www.canva.com/d/Fq2NlROLWuG3K5T"),
    ("Post 09 — Seasonal Special",            "https://www.canva.com/d/ASUv_LZTcS1U2E5"),
    ("Post 10 — Five-Star Review",            "https://www.canva.com/d/bcHcmfmCvfmN0Lb"),
    ("Post 11 — Before & After",              "https://www.canva.com/d/ZQ8Rc-o2AMNrmHA"),
    ("Post 12 — Customer Spotlight",          "https://www.canva.com/d/ajpNaWk1GzTNk8m"),
    ("Post 13 — Years in Business",           "https://www.canva.com/d/E-I4kGlLL5LHanb"),
    ("Post 14 — Did You Know",                "https://www.canva.com/d/3Xlt9sNtiyxjvtl"),
    ("Post 15 — Why Ceramic Coating",         "https://www.canva.com/d/k6vs7kFALWVFgBx"),
    ("Post 16 — Detailing Tip",               "https://www.canva.com/d/1vL7lMSQqiYK4xn"),
    ("Post 17 — Before You Sell",             "https://www.canva.com/d/X8YpkC1EXFCpxJX"),
    ("Post 18 — About Us",                    "https://www.canva.com/d/sBDDodmH8zVWvVu"),
    ("Post 19 — Follow Us",                   "https://www.canva.com/d/5De3Ho1sMXb1MQQ"),
    ("Post 20 — Contact Us",                  "https://www.canva.com/d/N_yHRe-6A5zj7S5"),
]

BRANDING_LINKS = [
    ("Business Card Front", "https://www.canva.com/d/ufSHsZ-CdmwOsQE"),
    ("Business Card Back",  "https://www.canva.com/d/Y4Q0Skv03_HlP7q"),
    ("Letterhead",          "https://www.canva.com/d/WgXLFiQGw4lmAyb"),
    ("Email Signature",     "https://www.canva.com/d/XGZVkdrIhb-Sv4i"),
    ("Invoice",             "https://www.canva.com/d/KA2Yn_0eiGYP19j"),
    ("Thank You Card",      "https://www.canva.com/d/kYD6o2BI10LFWOa"),
]

EMAIL_LINKS = [
    ("Booking Confirmation", "https://www.canva.com/d/qlh-Uz5BfylUXKz"),
    ("Appointment Reminder", "https://www.canva.com/d/4a5-4p7_bSuyu8e"),
    ("Job Completion",       "https://www.canva.com/d/-bsJCScnt2_YKRC"),
    ("Follow-Up",            "https://www.canva.com/d/UGmzvUrmerC9VU3"),
    ("Referral Program",     "https://www.canva.com/d/qH1kxQAXAhJH2kr"),
    ("Seasonal Promotion",   "https://www.canva.com/d/IqEKaKOH3KzLx2X"),
]

JOB_FORMS_LINKS = [
    ("Condition Report", "https://www.canva.com/d/tegCDgP2FkzVBAo"),
    ("Job Checklist",    "https://www.canva.com/d/vbSYRDs8v1WDIs9"),
    ("Handover Form",    "https://www.canva.com/d/3soeEB2fpq9OxxG"),
]


def generate_delivery_pdf(appt_dark_url, appt_light_url, welcome_url):
    """Regenerate the full 53-template delivery PDF."""
    out_path = os.path.join(OUTPUT_DIR, "Delivery_Mega_Bundle.pdf")
    W_pt, H_pt = A4  # 595.27 x 841.89 points

    # ReportLab colours
    C_DARK   = HexColor("#0D0D0D")
    C_RED    = HexColor("#E02020")
    C_WHITE  = HexColor("#FFFFFF")
    C_SILVER = HexColor("#C0C0C0")
    C_PANEL  = HexColor("#1A1A1A")
    C_LGREY  = HexColor("#F5F5F5")

    SANS_B = "Helvetica-Bold"
    SANS   = "Helvetica"

    c = rl_canvas.Canvas(out_path, pagesize=A4)

    def _cx(text, y, font, size, color):
        c.setFont(font, size)
        c.setFillColor(color)
        tw = c.stringWidth(text, font, size)
        c.drawString((W_pt - tw) / 2, y, text)

    def _bar(y, h, color):
        c.setFillColor(color)
        c.rect(0, y, W_pt, h, fill=1, stroke=0)

    def _rule(y, color=None):
        c.setStrokeColor(color or C_RED)
        c.setLineWidth(1)
        c.line(20 * mm, y, W_pt - 20 * mm, y)

    def section_header(title, subtitle):
        """Draw a dark header band at top of page with section title."""
        _bar(H_pt - 60, 60, C_PANEL)
        _bar(H_pt - 64, 4, C_RED)
        c.setFont(SANS_B, 16)
        c.setFillColor(C_WHITE)
        c.drawString(20 * mm, H_pt - 46, title)
        c.setFont(SANS, 10)
        c.setFillColor(C_RED)
        c.drawString(20 * mm, H_pt - 58, subtitle)

    def footer_line(page_num):
        c.setFont(SANS, 7)
        c.setFillColor(C_SILVER)
        c.drawString(20 * mm, 8 * mm, f"Page {page_num}  |  PurpleOcaz  |  Car Detailing Mega Bundle")

    def link_block(name, url, y):
        """Draw a template entry with name + clickable URL."""
        c.setFont(SANS_B, 10)
        c.setFillColor(C_PANEL)
        c.drawString(20 * mm, y + 4, name)
        c.setFont(SANS, 9)
        c.setFillColor(C_RED)
        c.drawString(20 * mm, y - 8, url)
        c.linkURL(url, (20 * mm, y - 10, W_pt - 20 * mm, y + 12),
                  relative=0, thickness=0)
        _rule(y - 13, C_LGREY)

    def no_link_block(name, desc, y):
        """Draw a template entry without URL."""
        c.setFont(SANS_B, 10)
        c.setFillColor(C_PANEL)
        c.drawString(20 * mm, y + 4, name)
        c.setFont(SANS, 9)
        c.setFillColor(C_SILVER)
        c.drawString(20 * mm, y - 8, desc)
        _rule(y - 13, C_LGREY)

    # ── PAGE 1: COVER ────────────────────────────────────────────────────────
    _bar(0, H_pt, C_DARK)
    _bar(H_pt - 10, 10, C_RED)
    _bar(0, 10, C_RED)

    _cx("COMPLETE CAR DETAILING", H_pt - 160, SANS_B, 28, C_WHITE)
    _cx("BUSINESS KIT", H_pt - 200, SANS_B, 28, C_WHITE)

    c.setFont(SANS_B, 72)
    c.setFillColor(C_RED)
    tw = c.stringWidth("53+", SANS_B, 72)
    c.drawString((W_pt - tw) / 2, H_pt - 310, "53+")

    _cx("PROFESSIONAL CANVA TEMPLATES", H_pt - 340, SANS, 13, C_SILVER)

    # Section list
    sections = [
        "— Client Forms (8)",
        "— Visual Templates (4)",
        "— Marketing Flyers (4)",
        "— Social Media Posts (20)",
        "— Branding Kit (6)",
        "— Email Templates (6)",
        "— Job Forms (3)",
        "— Appointment Cards (2)",
    ]
    y = H_pt - 390
    for line in sections:
        _cx(line, y, SANS, 12, C_WHITE)
        y -= 22

    _rule(y - 10)

    _cx("HOW TO USE YOUR TEMPLATES:", y - 35, SANS_B, 10, C_WHITE)
    steps = [
        "1. Find the template you need in the sections below",
        "2. Click the Canva link to open it",
        "3. Click 'Use this template' to create your own copy",
        "4. Edit with your business details, logo and colours",
        "5. Download as PDF or PNG — ready to print or send!",
    ]
    ys = y - 55
    for step in steps:
        _cx(step, ys, SANS, 9, C_SILVER)
        ys -= 16

    _cx("PurpleOcaz  |  purpleocaz.etsy.com", 30, SANS, 9, C_SILVER)
    _cx("Thank you for your purchase!", 18, SANS_B, 9, C_RED)
    _cx("This bundle is worth over £60 — enjoy!", 6, SANS, 8, C_SILVER)

    c.showPage()

    # ── PAGE 2: CLIENT FORMS ─────────────────────────────────────────────────
    section_header("SECTION 1: CLIENT FORMS", "8 Templates")
    forms = [
        ("Vehicle Intake Form",     "Customise with your shop details and print"),
        ("Consent & Liability Waiver", "Legal protection for your business"),
        ("Service Agreement",       "Set clear expectations with every client"),
        ("Invoice Template",        "Professional billing for every job"),
        ("Customer Feedback Form",  "Collect reviews and improve your service"),
        ("Appointment Booking Form","Pre-appointment details form"),
        ("Aftercare Instructions",  "Help clients care for their vehicle post-detail"),
        ("Detailing Package Menu",  "Showcase your services with pricing"),
    ]
    y = H_pt - 90
    for name, desc in forms:
        no_link_block(name, "(Edit and print — see Canva folder)", y)
        y -= 50
    footer_line(2)
    c.showPage()

    # ── PAGE 3: VISUAL TEMPLATES ─────────────────────────────────────────────
    section_header("SECTION 2: VISUAL TEMPLATES", "4 Templates")
    visuals = [
        ("Gift Certificate",  "(Edit and print — see Canva folder)"),
        ("Price List",        "(Edit and print — see Canva folder)"),
        ("Loyalty Card",      "(Edit and print — see Canva folder)"),
        ("Welcome Sign",      f"Download: {welcome_url}"),
    ]
    y = H_pt - 90
    for name, desc in visuals:
        no_link_block(name, desc, y)
        y -= 50
    footer_line(3)
    c.showPage()

    # ── PAGE 4: MARKETING FLYERS ─────────────────────────────────────────────
    section_header("SECTION 3: MARKETING FLYERS", "4 Templates")
    flyers = [
        ("Promo Flyer",          "(Edit and print — see Canva folder)"),
        ("Seasonal Flyer",       "(Edit and print — see Canva folder)"),
        ("Mobile Service Flyer", "(Edit and print — see Canva folder)"),
        ("Walk-In Flyer",        "(Edit and print — see Canva folder)"),
    ]
    y = H_pt - 90
    for name, desc in flyers:
        no_link_block(name, desc, y)
        y -= 50
    footer_line(4)
    c.showPage()

    # ── PAGES 5-6: SOCIAL MEDIA PACK ─────────────────────────────────────────
    section_header("SECTION 4: SOCIAL MEDIA PACK", "20 Templates")
    y = H_pt - 90
    page_num = 5
    for i, (name, url) in enumerate(SOCIAL_LINKS):
        if i == 13:  # overflow to page 6
            footer_line(page_num)
            c.showPage()
            page_num = 6
            section_header("SECTION 4: SOCIAL MEDIA PACK (continued)", "")
            y = H_pt - 90
        link_block(name, url, y)
        y -= 50
    footer_line(page_num)
    c.showPage()

    # ── PAGE 7: BRANDING KIT ─────────────────────────────────────────────────
    section_header("SECTION 5: BRANDING KIT", "6 Templates")
    y = H_pt - 90
    for name, url in BRANDING_LINKS:
        link_block(name, url, y)
        y -= 50
    footer_line(7)
    c.showPage()

    # ── PAGE 8: EMAIL TEMPLATES ───────────────────────────────────────────────
    section_header("SECTION 6: EMAIL TEMPLATES", "6 Templates")
    y = H_pt - 90
    for name, url in EMAIL_LINKS:
        link_block(name, url, y)
        y -= 50
    footer_line(8)
    c.showPage()

    # ── PAGE 9: JOB FORMS ────────────────────────────────────────────────────
    section_header("SECTION 7: JOB FORMS", "3 Templates")
    y = H_pt - 90
    for name, url in JOB_FORMS_LINKS:
        link_block(name, url, y)
        y -= 50
    footer_line(9)
    c.showPage()

    # ── PAGE 10: APPOINTMENT CARDS ───────────────────────────────────────────
    section_header("SECTION 8: APPOINTMENT CARDS", "2 Templates — Physical reminder cards (CR80)")
    y = H_pt - 90
    no_link_block("Appointment Card — Dark",
                  f"Download: {appt_dark_url}", y)
    y -= 60
    no_link_block("Appointment Card — Light",
                  f"Download: {appt_light_url}", y)
    y -= 80

    # Usage note
    c.setFont(SANS, 9)
    c.setFillColor(C_SILVER)
    usage_note = (
        "These are CR80 business card-sized reminder cards. Edit with your studio name, "
        "print on card stock, and hand\nto customers at the end of each appointment. "
        "Fields: Date, Time, Service, Technician, Notes."
    )
    c.drawString(20 * mm, y, "How to use these cards:")
    c.setFont(SANS, 9)
    for i, line in enumerate(usage_note.split("\n")):
        c.drawString(20 * mm, y - 14 - (i * 12), line)

    footer_line(10)
    c.showPage()

    # ── PAGE 11: HOW TO USE CANVA ────────────────────────────────────────────
    _bar(0, H_pt, C_DARK)
    _bar(H_pt - 10, 10, C_RED)
    _bar(0, 10, C_RED)

    _cx("HOW TO USE CANVA", H_pt - 100, SANS_B, 22, C_WHITE)
    _rule(H_pt - 115)

    steps_canva = [
        ("1. Create a free Canva account",
         "Go to canva.com and sign up — it's free!"),
        ("2. Click any template link",
         "Each link opens a professional template in Canva."),
        ("3. Click 'Use this template'",
         "This creates YOUR OWN copy — the original stays safe."),
        ("4. Edit everything",
         "Change text, colours, images, fonts — make it yours."),
        ("5. Add your logo",
         "Upload your logo and drag it onto the design."),
        ("6. Download",
         "Click Share > Download > choose PDF or PNG."),
        ("7. Print or send digitally",
         "Take to a print shop or email/text to customers."),
    ]
    y = H_pt - 170
    for title, body in steps_canva:
        c.setFont(SANS_B, 12)
        c.setFillColor(C_WHITE)
        c.drawString(25 * mm, y, title)
        c.setFont(SANS, 10)
        c.setFillColor(C_SILVER)
        c.drawString(25 * mm, y - 14, body)
        y -= 52

    _rule(y - 10)
    y -= 30
    c.setFont(SANS_B, 11)
    c.setFillColor(C_WHITE)
    _cx("NEED HELP?", y, SANS_B, 11, C_WHITE)
    y -= 18
    _cx("Message us on Etsy — we respond within 24 hours.", y, SANS, 10, C_SILVER)
    y -= 14
    _cx("purpleocaz.etsy.com", y, SANS, 10, C_RED)
    y -= 30
    _cx("Thank you for choosing PurpleOcaz!", y - 6, SANS_B, 12, C_WHITE)
    _cx("If you love your templates, we'd appreciate a 5-star review.", y - 22, SANS, 9, C_SILVER)

    c.save()
    print(f"\n  Delivery PDF saved: {out_path}")
    return out_path


# ═══════════════════════════════════════════════════════════════════════════════
# ETSY API
# ═══════════════════════════════════════════════════════════════════════════════
load_dotenv(os.path.join(PROJECT, ".env"))
TOKEN_FILE = os.path.join(PROJECT, "workflows", "etsy_analytics", "etsy_tokens.json")
ETSY_BASE  = "https://openapi.etsy.com/v3/application"
API_KEY    = os.getenv("ETSY_API_KEYSTRING", "")
SECRET     = os.getenv("ETSY_SHARED_SECRET", "")
SHOP_ID    = os.getenv("ETSY_SHOP_ID", "")
X_API_KEY  = f"{API_KEY}:{SECRET}"
LISTING_ID = "4476909005"


def load_tokens():
    with open(TOKEN_FILE) as f:
        return json.load(f)


def refresh_token(tokens):
    data = urllib.parse.urlencode({
        "grant_type":    "refresh_token",
        "client_id":     API_KEY,
        "refresh_token": tokens["refresh_token"],
    }).encode()
    req = urllib.request.Request(
        "https://api.etsy.com/v3/public/oauth/token",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    resp = urllib.request.urlopen(req)
    new_tokens = json.loads(resp.read())
    with open(TOKEN_FILE, "w") as f:
        json.dump(new_tokens, f, indent=2)
    print(f"  Token refreshed, expires in {new_tokens.get('expires_in', '?')}s")
    return new_tokens


def etsy_request(method, endpoint, tokens, body=None,
                 content_type="application/x-www-form-urlencoded"):
    url = f"{ETSY_BASE}{endpoint}"
    if body and content_type == "application/x-www-form-urlencoded":
        data = urllib.parse.urlencode(body).encode()
    elif body:
        data = body
    else:
        data = None

    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("x-api-key", X_API_KEY)
    req.add_header("Authorization", f"Bearer {tokens['access_token']}")
    if content_type and method != "GET":
        req.add_header("Content-Type", content_type)

    try:
        resp = urllib.request.urlopen(req)
        raw = resp.read()
        return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        if e.code == 401:
            print("  401 — refreshing token...")
            tokens.update(refresh_token(tokens))
            return etsy_request(method, endpoint, tokens, body, content_type)
        raise RuntimeError(f"HTTP {e.code}: {error_body}")


def upload_etsy_file(pdf_path, tokens):
    """Upload a file to Etsy listing and return file_id."""
    boundary = "----PurpleOcazFileBoundary"
    filename = "Car-Detailing-Mega-Bundle-DELIVERY.pdf"

    with open(pdf_path, "rb") as f:
        file_data = f.read()

    body = bytearray()
    # name field (required by Etsy)
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(f'Content-Disposition: form-data; name="name"\r\n\r\n{filename}\r\n'.encode())
    # file field
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode())
    body.extend(b"Content-Type: application/pdf\r\n\r\n")
    body.extend(file_data)
    body.extend(b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode())

    url = f"{ETSY_BASE}/shops/{SHOP_ID}/listings/{LISTING_ID}/files"
    req = urllib.request.Request(url, data=bytes(body), method="POST")
    req.add_header("x-api-key", X_API_KEY)
    req.add_header("Authorization", f"Bearer {tokens['access_token']}")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    try:
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read())
        return result
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        if e.code == 401:
            print("  401 — refreshing token...")
            tokens.update(refresh_token(tokens))
            return upload_etsy_file(pdf_path, tokens)
        raise RuntimeError(f"File upload HTTP {e.code}: {error_body}")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    print("=" * 65)
    print("CAR DETAILING MEGA BUNDLE UPGRADE")
    print("Adding: Appointment Cards (dark + light) + Welcome Sign")
    print("=" * 65)

    # ── Step 1: Build templates ───────────────────────────────────────────────
    print("\n=== Step 1: Build New Templates ===")
    dark_path  = build_appointment_card_dark()
    light_path = build_appointment_card_light()
    sign_path  = build_welcome_sign()

    # ── Step 2: Upload to Spaces ──────────────────────────────────────────────
    print("\n=== Step 2: Upload to Spaces ===")
    load_env()
    s3 = get_s3()

    dark_url  = upload_file(s3, dark_path,
                            "templates/car-detail-appointment-cards/CD_Appointment_Card_Dark.png")
    light_url = upload_file(s3, light_path,
                            "templates/car-detail-appointment-cards/CD_Appointment_Card_Light.png")
    sign_url  = upload_file(s3, sign_path,
                            "templates/car-detail-welcome-sign/CD_Welcome_Sign.png")

    # Verify Spaces uploads
    print("\n  Verifying Spaces uploads...")
    for label, url in [("Dark card", dark_url), ("Light card", light_url), ("Welcome sign", sign_url)]:
        req = urllib.request.Request(url, method="HEAD")
        try:
            resp = urllib.request.urlopen(req)
            print(f"  {label}: HTTP {resp.status} OK")
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"Spaces verify FAILED for {label}: HTTP {e.code}")

    # ── Step 3: Regenerate delivery PDF ───────────────────────────────────────
    print("\n=== Step 3: Regenerate Delivery PDF (53 templates) ===")
    pdf_path = generate_delivery_pdf(dark_url, light_url, sign_url)

    # ── Step 4: Upload PDF to Spaces ──────────────────────────────────────────
    print("\n=== Step 4: Upload Delivery PDF to Spaces ===")
    pdf_spaces_url = upload_file(s3, pdf_path,
                                 "templates/car-detail-mega-bundle/Delivery_Mega_Bundle.pdf")
    req = urllib.request.Request(pdf_spaces_url, method="HEAD")
    resp = urllib.request.urlopen(req)
    print(f"  PDF Spaces verify: HTTP {resp.status} OK")

    # ── Step 5: Replace file on Etsy ──────────────────────────────────────────
    print("\n=== Step 5: Replace Delivery File on Etsy ===")
    tokens = load_tokens()

    # GET current files
    current_files = etsy_request(
        "GET", f"/shops/{SHOP_ID}/listings/{LISTING_ID}/files", tokens)
    print(f"  Current files: {len(current_files.get('results', []))} found")

    # Delete all existing files
    for f in current_files.get("results", []):
        fid = f.get("listing_file_id") or f.get("file_id")
        fname = f.get("filename", "?")
        print(f"  Deleting file_id={fid} ({fname})")
        etsy_request("DELETE",
                     f"/shops/{SHOP_ID}/listings/{LISTING_ID}/files/{fid}",
                     tokens)
        print(f"    Deleted.")
        time.sleep(0.5)

    # Upload new PDF
    print(f"  Uploading {os.path.basename(pdf_path)}...")
    upload_result = upload_etsy_file(pdf_path, tokens)
    print(f"  Upload result: {json.dumps(upload_result, indent=2)[:300]}")

    # Verify
    time.sleep(1)
    verify_files = etsy_request(
        "GET", f"/shops/{SHOP_ID}/listings/{LISTING_ID}/files", tokens)
    file_count = len(verify_files.get("results", []))
    print(f"\n  File verify: {file_count} file(s) on listing")
    if file_count == 0:
        raise RuntimeError("File upload verification failed — 0 files on listing")
    print(f"  Filename: {verify_files['results'][0].get('filename', '?')}")

    # ── Step 6: Update price ──────────────────────────────────────────────────
    print("\n=== Step 6: Update Price → £39.99 ===")
    patch = etsy_request(
        "PATCH", f"/listings/{LISTING_ID}", tokens,
        body={"price": "39.99"})
    new_price = patch.get("price", {})
    print(f"  Price response: {new_price}")

    # ── Step 7: Update title + description ───────────────────────────────────
    print("\n=== Step 7: Update Title + Description ===")
    NEW_TITLE = (
        "Car Detailing Business Bundle | 53 Canva Templates | "
        "Forms, Social Media, Branding, Flyers, Email, Cards"
    )
    NEW_DESC = (
        "THE COMPLETE CAR DETAILING BUSINESS KIT — 53 PROFESSIONAL CANVA TEMPLATES\n\n"
        "Everything you need to run a polished, professional car detailing business. "
        "53 editable Canva templates across 8 categories — instant download, no design skills needed.\n\n"
        "WHAT'S INCLUDED (53 templates):\n\n"
        "CLIENT FORMS — 8 templates\n"
        "Vehicle Intake Form | Consent & Liability Waiver | Service Agreement | Invoice "
        "| Customer Feedback Form | Appointment Booking | Aftercare Instructions | Package Menu\n\n"
        "VISUAL TEMPLATES — 4 templates\n"
        "Gift Certificate | Price List | Loyalty Stamp Card | Welcome Sign\n\n"
        "MARKETING FLYERS — 4 templates\n"
        "Promo Flyer | Seasonal Flyer | Mobile Service Flyer | Walk-In Flyer\n\n"
        "SOCIAL MEDIA POSTS — 20 templates (1080×1080)\n"
        "20 professionally designed Instagram posts covering services, offers, reviews, tips, and more.\n\n"
        "BRANDING KIT — 6 templates\n"
        "Business Card (Front + Back) | Letterhead | Email Signature | Invoice | Thank You Card\n\n"
        "EMAIL MARKETING — 6 templates\n"
        "Booking Confirmation | Appointment Reminder | Job Completion | Follow-Up | Referral | Seasonal Promo\n\n"
        "JOB FORMS — 3 templates\n"
        "Vehicle Condition Report | Job Checklist | Handover Form\n\n"
        "APPOINTMENT CARDS — 2 templates (CR80 card size)\n"
        "Dark & Light variants — hand to customers at the end of each appointment\n\n"
        "HOW IT WORKS:\n"
        "1. Purchase and download your delivery PDF\n"
        "2. Click any Canva link to open the template\n"
        "3. Click 'Use this template' to create your own editable copy\n"
        "4. Customise with your studio name, logo, colours and contact details\n"
        "5. Download as PDF or PNG — print ready or digital\n\n"
        "WHY CHOOSE THIS BUNDLE:\n"
        "✓ 53 templates — worth over £60 individually\n"
        "✓ Fully editable in FREE Canva (no paid plan needed)\n"
        "✓ Instant download — start using today\n"
        "✓ Print-ready and digital-friendly\n"
        "✓ Professional car detailing design style\n"
        "✓ Perfect for mobile detailers, auto detail shops, and car wash businesses\n\n"
        "A free Canva account is required to edit the templates.\n"
        "All templates are for personal or business use.\n"
        "No physical products are shipped — this is a digital download."
    )

    patch2 = etsy_request(
        "PATCH", f"/listings/{LISTING_ID}", tokens,
        body={"title": NEW_TITLE, "description": NEW_DESC})
    print(f"  New title: {patch2.get('title', 'N/A')[:80]}")
    print(f"  Description updated: {len(NEW_DESC)} chars")

    # ── Step 8: Final GET verification ───────────────────────────────────────
    print("\n=== Step 8: Final Verification ===")
    listing = etsy_request(
        "GET", f"/listings/{LISTING_ID}", tokens)
    print(f"  Listing ID:  {listing.get('listing_id')}")
    print(f"  Title:       {listing.get('title', '')[:80]}")
    price = listing.get("price", {})
    print(f"  Price:       {price.get('currency_code', '')} {price.get('amount', 0) / max(price.get('divisor', 100), 1):.2f}")
    print(f"  State:       {listing.get('state')}")

    print("\n" + "=" * 65)
    print("UPGRADE COMPLETE")
    print(f"  53 templates | 8 sections | £39.99")
    print(f"  Listing: https://www.etsy.com/listing/{LISTING_ID}")
    print(f"  New templates uploaded to Spaces:")
    print(f"    Dark card:  {dark_url}")
    print(f"    Light card: {light_url}")
    print(f"    Welcome:    {sign_url}")
    print("=" * 65)

    print("\nRun verify:")
    print(f"  python scripts/verify_listing.py {LISTING_ID} --bundle")


if __name__ == "__main__":
    main()
