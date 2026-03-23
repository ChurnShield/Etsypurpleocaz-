#!/usr/bin/env python3
"""Generate 28 Etsy listing images for 4 car detailing listings.
7 images per listing at 2000x2000px.

Usage:
    python scripts/car_detail_thumbnails.py
"""

import io
import os
import sys
import json
import fitz  # PyMuPDF
import boto3
from PIL import Image, ImageDraw, ImageFont, ImageFilter

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTS = os.path.join(PROJECT, "outputs")
THUMBS = os.path.join(PROJECT, "thumbnails", "car-detail")
SZ = 2000

# ── Colors ────────────────────────────────────────────────────────────────────
BG_DARK = (13, 13, 13)        # #0D0D0D
BG_WHITE = (255, 255, 255)
RED = (224, 32, 32)            # #E02020
WHITE = (255, 255, 255)
SILVER = (192, 192, 192)       # #C0C0C0
DARK_GREY = (26, 26, 26)      # #1A1A1A
MID_GREY = (100, 100, 100)
LIGHT_GREY = (240, 240, 240)

# ── Fonts ─────────────────────────────────────────────────────────────────────
_SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
_SERIF_BI = "/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf"
_SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
_MONO_B = "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"

def fnt(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

def center_text(draw, text, y, font, fill, canvas_w=SZ):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (canvas_w - tw) // 2
    draw.text((x, y), text, font=font, fill=fill)
    return bbox[3] - bbox[1]

def right_text(draw, text, x, y, font, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text((x - tw, y), text, font=font, fill=fill)

def text_width(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


# ── PDF to Image ──────────────────────────────────────────────────────────────
def pdf_to_image(pdf_path, dpi=150):
    doc = fitz.open(pdf_path)
    page = doc[0]
    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    doc.close()
    return img.convert("RGB")


# ── S3 Upload ─────────────────────────────────────────────────────────────────
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

def upload_png(s3, img, key):
    bucket = os.environ.get("DO_SPACES_BUCKET", "purpleocaz-assets")
    buf = io.BytesIO()
    img.save(buf, format="PNG", quality=95)
    buf.seek(0)
    s3.put_object(Bucket=bucket, Key=key, Body=buf.read(),
                  ContentType="image/png", ACL="public-read")
    region = os.environ.get("DO_SPACES_REGION", "lon1")
    url = f"https://{bucket}.{region}.digitaloceanspaces.com/{key}"
    return url

def upload_file_to_spaces(s3, local_path, key):
    bucket = os.environ.get("DO_SPACES_BUCKET", "purpleocaz-assets")
    with open(local_path, "rb") as f:
        s3.put_object(Bucket=bucket, Key=key, Body=f.read(),
                      ContentType="image/png", ACL="public-read")
    region = os.environ.get("DO_SPACES_REGION", "lon1")
    return f"https://{bucket}.{region}.digitaloceanspaces.com/{key}"


# ── Listing Definitions ───────────────────────────────────────────────────────
FORM_PDFS = [
    ("Vehicle Intake Form", "Vehicle_Intake_Form"),
    ("Consent & Liability Waiver", "Consent_Liability_Waiver"),
    ("Service Agreement", "Service_Agreement"),
    ("Invoice Template", "Invoice_Template"),
    ("Customer Feedback Form", "Customer_Feedback_Form"),
    ("Appointment Booking Form", "Appointment_Booking_Form"),
    ("Aftercare Instructions", "Aftercare_Instructions"),
    ("Detailing Package Menu", "Detailing_Package_Menu"),
]

VISUAL_PDFS = [
    ("Gift Certificate", "car-detail-gift-certificate", "Car_Detail_Gift_Certificate"),
    ("Price List", "car-detail-price-list", "Car_Detail_Price_List"),
    ("Loyalty Card", "car-detail-loyalty-card", "Car_Detail_Loyalty_Card"),
]

FLYER_PDFS = [
    ("Promotional Flyer", "car-detail-flyer-promo", "Car_Detail_Flyer_Promo"),
    ("Seasonal Flyer", "car-detail-flyer-seasonal", "Car_Detail_Flyer_Seasonal"),
    ("Mobile Detailing Flyer", "car-detail-flyer-mobile", "Car_Detail_Flyer_Mobile"),
    ("Walk-In Flyer", "car-detail-flyer-walkin", "Car_Detail_Flyer_WalkIn"),
]

LISTINGS = [
    {
        "slug": "forms_bundle",
        "title_line1": "CAR DETAILING",
        "title_line2": "FORMS BUNDLE",
        "subtitle": "8 EDITABLE CANVA TEMPLATES",
        "count": 8,
        "pdf_sources": "forms",
    },
    {
        "slug": "visual_bundle",
        "title_line1": "CAR DETAILING",
        "title_line2": "VISUAL BUNDLE",
        "subtitle": "3 EDITABLE CANVA TEMPLATES",
        "count": 3,
        "pdf_sources": "visual",
    },
    {
        "slug": "flyer_pack",
        "title_line1": "CAR DETAILING",
        "title_line2": "FLYER PACK",
        "subtitle": "4 EDITABLE CANVA TEMPLATES",
        "count": 4,
        "pdf_sources": "flyers",
    },
    {
        "slug": "starter_bundle",
        "title_line1": "CAR DETAILING",
        "title_line2": "BUSINESS BUNDLE",
        "subtitle": "15 EDITABLE CANVA TEMPLATES",
        "count": 15,
        "pdf_sources": "all",
    },
]


def get_previews(source_type):
    """Load preview images for a given source type."""
    previews = []
    names = []
    if source_type in ("forms", "all"):
        for label, fname in FORM_PDFS:
            path = os.path.join(OUTPUTS, "car-detail-forms", f"{fname}_preview.png")
            if os.path.exists(path):
                previews.append(Image.open(path).convert("RGB"))
                names.append(label)
            else:
                pdf = os.path.join(OUTPUTS, "car-detail-forms", f"{fname}.pdf")
                if os.path.exists(pdf):
                    previews.append(pdf_to_image(pdf))
                    names.append(label)

    if source_type in ("visual", "all"):
        for label, folder, fname in VISUAL_PDFS:
            pdf = os.path.join(OUTPUTS, folder, f"{fname}.pdf")
            if os.path.exists(pdf):
                previews.append(pdf_to_image(pdf))
                names.append(label)

    if source_type in ("flyers", "all"):
        for label, folder, fname in FLYER_PDFS:
            pdf = os.path.join(OUTPUTS, folder, f"{fname}.pdf")
            if os.path.exists(pdf):
                previews.append(pdf_to_image(pdf))
                names.append(label)

    return previews, names


def add_shadow(img, offset=6, blur=15, opacity=80):
    """Add drop shadow to an image."""
    w, h = img.size
    shadow = Image.new("RGBA", (w + blur * 4, h + blur * 4), (0, 0, 0, 0))
    shadow_layer = Image.new("RGBA", (w, h), (0, 0, 0, opacity))
    shadow.paste(shadow_layer, (blur * 2 + offset, blur * 2 + offset))
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    result = Image.new("RGBA", shadow.size, (0, 0, 0, 0))
    result.paste(shadow, (0, 0))
    result.paste(img.convert("RGBA"), (blur * 2, blur * 2), img.convert("RGBA"))
    return result


def resize_preview(img, max_h, max_w=None):
    """Resize keeping aspect ratio."""
    pw, ph = img.size
    scale = max_h / ph
    if max_w:
        scale = min(scale, max_w / pw)
    nw, nh = int(pw * scale), int(ph * scale)
    return img.resize((nw, nh), Image.LANCZOS)


# ══════════════════════════════════════════════════════════════════════════════
# IMAGE BUILDERS
# ══════════════════════════════════════════════════════════════════════════════

def build_rank1_hero(listing):
    """Hero image — dark bg, title, previews fanned, callout strip."""
    img = Image.new("RGB", (SZ, SZ), BG_DARK)
    draw = ImageDraw.Draw(img)

    # Title
    center_text(draw, listing["title_line1"], 100, fnt(_SERIF_B, 100), WHITE)
    center_text(draw, listing["title_line2"], 220, fnt(_SANS_B, 90), WHITE)

    # Red subtitle bar
    bar_y = 360
    draw.rectangle([(200, bar_y), (SZ - 200, bar_y + 70)], fill=RED)
    center_text(draw, listing["subtitle"], bar_y + 12, fnt(_SANS_B, 38), WHITE)

    # Template previews
    previews, _ = get_previews(listing["pdf_sources"])
    if previews:
        n = min(len(previews), 4)
        preview_h = 700
        total_w = n * 320
        start_x = (SZ - total_w) // 2
        rotations = {1: [0], 2: [-6, 6], 3: [-10, 0, 10], 4: [-12, -4, 4, 12]}
        rots = rotations.get(n, rotations[4])

        for i in range(n):
            p = resize_preview(previews[i], preview_h, 300)
            rotated = p.rotate(-rots[i], expand=True, resample=Image.BICUBIC,
                              fillcolor=BG_DARK)
            rw, rh = rotated.size
            x = start_x + i * 320 + (300 - rw) // 2
            y = 500 + (preview_h - rh) // 2
            # Shadow
            shadow_img = add_shadow(rotated, offset=5, blur=12, opacity=100)
            sw, sh = shadow_img.size
            sx = x - 12 * 2
            sy = y - 12 * 2
            img.paste(shadow_img.convert("RGB"), (sx, sy), shadow_img.split()[3])

    # Bottom callout strip
    strip_y = SZ - 160
    draw.rectangle([(0, strip_y), (SZ, SZ)], fill=DARK_GREY)
    callout = "\u2713 Instant Download    \u2713 Edit in Canva    \u2713 Print Ready"
    center_text(draw, callout, strip_y + 55, fnt(_SANS_B, 34), SILVER)

    # Price badge top right
    draw.rectangle([(SZ - 260, 40), (SZ - 40, 130)], fill=RED)
    price = "\u00a39.99" if listing["slug"] == "starter_bundle" else "\u00a34.99"
    center_x = SZ - 150
    bbox = draw.textbbox((0, 0), price, font=fnt(_SANS_B, 52))
    tw = bbox[2] - bbox[0]
    draw.text((center_x - tw // 2, 55), price, font=fnt(_SANS_B, 52), fill=WHITE)

    return img


def build_rank2_whats_inside(listing):
    """What's Inside — white bg, grid of templates."""
    img = Image.new("RGB", (SZ, SZ), BG_WHITE)
    draw = ImageDraw.Draw(img)

    # Red header bar
    draw.rectangle([(0, 0), (SZ, 120)], fill=RED)
    center_text(draw, "WHAT'S INCLUDED", 25, fnt(_SANS_B, 60), WHITE)

    previews, names = get_previews(listing["pdf_sources"])
    n = len(previews)

    if n <= 4:
        cols, rows = 2, 2
    elif n <= 6:
        cols, rows = 3, 2
    elif n <= 9:
        cols, rows = 3, 3
    else:
        cols, rows = 4, 4

    margin = 80
    gap = 30
    label_h = 50
    avail_w = SZ - 2 * margin
    avail_h = SZ - 120 - margin - 140  # header + bottom badge
    cell_w = (avail_w - (cols - 1) * gap) // cols
    cell_h = (avail_h - (rows - 1) * (gap + label_h)) // rows

    for i in range(min(n, cols * rows)):
        r = i // cols
        c = i % cols
        x = margin + c * (cell_w + gap)
        y = 160 + r * (cell_h + gap + label_h)

        p = resize_preview(previews[i], cell_h - 10, cell_w - 10)
        pw, ph = p.size
        px = x + (cell_w - pw) // 2
        py = y + (cell_h - ph) // 2

        # Light border
        draw.rectangle([(px - 2, py - 2), (px + pw + 2, py + ph + 2)],
                       outline=(220, 220, 220), width=2)
        img.paste(p, (px, py))

        # Label
        if i < len(names):
            label = names[i]
            f = fnt(_SANS, 22) if len(label) > 20 else fnt(_SANS, 24)
            bbox = draw.textbbox((0, 0), label, font=f)
            tw = bbox[2] - bbox[0]
            lx = x + (cell_w - tw) // 2
            draw.text((lx, y + cell_h + 5), label, font=f, fill=BG_DARK)

    # Bottom badge
    badge_y = SZ - 110
    draw.rectangle([(300, badge_y), (SZ - 300, badge_y + 70)], fill=RED)
    center_text(draw, "INSTANT DIGITAL DOWNLOAD", badge_y + 14, fnt(_SANS_B, 34), WHITE)

    return img


def build_rank3_lifestyle(listing):
    """Lifestyle mockup — dark bg, photo with overlaid templates."""
    img = Image.new("RGB", (SZ, SZ), BG_DARK)
    draw = ImageDraw.Draw(img)

    # Load mockup photo
    mockup_dirs = [
        os.path.join(PROJECT, "assets", "photos", "car_detail_mockup"),
        os.path.join(PROJECT, "assets", "photos", "car_detailing_studio_professional"),
        os.path.join(PROJECT, "assets", "photos", "car_detailing_professional_close_up"),
    ]
    photo = None
    for d in mockup_dirs:
        p = os.path.join(d, "photo_1.jpg")
        if os.path.exists(p):
            photo = Image.open(p).convert("RGB")
            break

    if photo:
        # Fill background with photo (dark overlay)
        pw, ph = photo.size
        scale = max(SZ / pw, SZ / ph)
        nw, nh = int(pw * scale), int(ph * scale)
        photo = photo.resize((nw, nh), Image.LANCZOS)
        cx = (nw - SZ) // 2
        cy = (nh - SZ) // 2
        photo = photo.crop((cx, cy, cx + SZ, cy + SZ))
        img.paste(photo, (0, 0))

        # Dark overlay 70%
        overlay = Image.new("RGBA", (SZ, SZ), (0, 0, 0, 178))
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)

    # Overlay 2-3 template previews
    previews, _ = get_previews(listing["pdf_sources"])
    if previews:
        n = min(len(previews), 3)
        preview_h = 800
        positions = [
            [(600, 550)],
            [(350, 500), (950, 600)],
            [(200, 500), (700, 550), (1200, 480)],
        ]
        rots = [
            [5],
            [-8, 5],
            [-10, 2, 10],
        ]
        for i in range(n):
            p = resize_preview(previews[i], preview_h, 500)
            rotated = p.rotate(-rots[n-1][i], expand=True, resample=Image.BICUBIC,
                              fillcolor=(0, 0, 0))
            shadow = add_shadow(rotated, offset=8, blur=18, opacity=120)
            sw, sh = shadow.size
            x, y = positions[n-1][i]
            x -= 18 * 2
            y -= 18 * 2
            if x + sw > SZ:
                x = SZ - sw - 10
            if y + sh > SZ:
                y = SZ - sh - 10
            img.paste(shadow.convert("RGB"), (max(0, x), max(0, y)), shadow.split()[3])

    # Red corner badge top right
    badge_w, badge_h = 520, 65
    bx = SZ - badge_w - 50
    by = 60
    draw.rectangle([(bx, by), (bx + badge_w, by + badge_h)], fill=RED)
    center_x = bx + badge_w // 2
    f = fnt(_SANS_B, 30)
    bbox = draw.textbbox((0, 0), "PROFESSIONAL TEMPLATES", font=f)
    tw = bbox[2] - bbox[0]
    draw.text((center_x - tw // 2, by + 15), "PROFESSIONAL TEMPLATES", font=f, fill=WHITE)

    # Bottom text
    center_text(draw, f"{listing['count']} EDITABLE TEMPLATES  |  INSTANT DOWNLOAD",
                SZ - 100, fnt(_SANS_B, 32), SILVER)

    return img


def build_rank4_how_it_works(listing):
    """How It Works — white bg, 3 steps."""
    img = Image.new("RGB", (SZ, SZ), BG_WHITE)
    draw = ImageDraw.Draw(img)

    # Dark header
    draw.rectangle([(0, 0), (SZ, 120)], fill=BG_DARK)
    center_text(draw, "HOW IT WORKS", 25, fnt(_SANS_B, 60), WHITE)

    steps = [
        ("1", "PURCHASE & DOWNLOAD", "Download instantly from Etsy\nafter purchase — no waiting"),
        ("2", "OPEN IN CANVA", "Open your free Canva account\nand click the template link"),
        ("3", "EDIT & PRINT", "Add your business details,\ndownload and print or share"),
    ]

    step_h = 420
    start_y = 200

    for i, (num, title, desc) in enumerate(steps):
        y = start_y + i * step_h
        cx = SZ // 2

        # Red circle with number
        circle_r = 50
        circle_x = cx
        circle_y = y + 30
        draw.ellipse([(circle_x - circle_r, circle_y - circle_r),
                       (circle_x + circle_r, circle_y + circle_r)], fill=RED)
        f_num = fnt(_SANS_B, 56)
        bbox = draw.textbbox((0, 0), num, font=f_num)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text((circle_x - tw // 2, circle_y - th // 2 - 5), num,
                  font=f_num, fill=WHITE)

        # Title
        center_text(draw, title, y + 100, fnt(_SANS_B, 42), BG_DARK)

        # Description
        for j, line in enumerate(desc.split("\n")):
            center_text(draw, line, y + 170 + j * 40, fnt(_SANS, 30), MID_GREY)

        # Arrow between steps
        if i < 2:
            arrow_y = y + step_h - 60
            draw.polygon([(cx - 15, arrow_y), (cx + 15, arrow_y),
                          (cx, arrow_y + 30)], fill=RED)

    # Red footer
    footer_y = SZ - 110
    draw.rectangle([(0, footer_y), (SZ, SZ)], fill=RED)
    center_text(draw, "WORKS ON ANY DEVICE  \u2014  FREE CANVA ACCOUNT",
                footer_y + 28, fnt(_SANS_B, 34), WHITE)

    return img


def build_rank5_why_buy(listing):
    """Why Buy — dark bg, checkmark list."""
    img = Image.new("RGB", (SZ, SZ), BG_DARK)
    draw = ImageDraw.Draw(img)

    # Headline
    center_text(draw, "BUILT FOR", 120, fnt(_SERIF_B, 70), WHITE)
    center_text(draw, "CAR DETAILING", 220, fnt(_SERIF_B, 80), RED)
    center_text(draw, "PROFESSIONALS", 330, fnt(_SERIF_B, 70), WHITE)

    # Red rule
    rule_y = 440
    draw.rectangle([(600, rule_y), (SZ - 600, rule_y + 4)], fill=RED)

    # Checkmarks
    checks = [
        "Fully editable in Canva (free)",
        "Instant digital download",
        "Print at home or professionally",
        "A4 print-ready format",
        "Personal & commercial use",
        "No design skills needed",
        "Works on mobile & desktop",
    ]
    start_y = 510
    x_check = 380
    x_text = 440

    for i, txt in enumerate(checks):
        y = start_y + i * 80
        # Red check
        draw.text((x_check, y), "\u2713", font=fnt(_SANS_B, 42), fill=RED)
        draw.text((x_text, y + 2), txt, font=fnt(_SANS, 36), fill=WHITE)

    # Silver subtext
    center_text(draw, "Used by detailing businesses across the UK",
                SZ - 150, fnt(_SANS, 28), SILVER)

    # Bottom red rule
    draw.rectangle([(0, SZ - 60), (SZ, SZ - 56)], fill=RED)

    return img


def build_rank6_canva_basics(listing):
    """Canva Basics — editing guide."""
    img = Image.new("RGB", (SZ, SZ), BG_WHITE)
    draw = ImageDraw.Draw(img)

    # Dark header
    draw.rectangle([(0, 0), (SZ, 120)], fill=BG_DARK)
    center_text(draw, "EDITING IN CANVA IS EASY", 25, fnt(_SANS_B, 55), WHITE)

    steps = [
        ("1", "CLICK THE LINK", "Open the Canva template link\nfrom your delivery PDF"),
        ("2", "USE THIS TEMPLATE", "Click 'Use this template'\nto create your own copy"),
        ("3", "CUSTOMISE", "Change text, colours, photos\nand fonts to match your brand"),
        ("4", "DOWNLOAD & PRINT", "Export as PDF or PNG —\nprint at home or share online"),
    ]

    cols = 2
    rows = 2
    margin = 100
    gap = 60
    cell_w = (SZ - 2 * margin - gap) // cols
    cell_h = (SZ - 200 - 2 * margin - gap) // rows

    for i, (num, title, desc) in enumerate(steps):
        r = i // cols
        c = i % cols
        x = margin + c * (cell_w + gap)
        y = 180 + r * (cell_h + gap)
        cx = x + cell_w // 2

        # Light grey card
        draw.rounded_rectangle([(x, y), (x + cell_w, y + cell_h)],
                                radius=15, fill=(248, 248, 248), outline=(230, 230, 230))

        # Red circle number
        circle_r = 35
        draw.ellipse([(cx - circle_r, y + 30), (cx + circle_r, y + 30 + circle_r * 2)],
                      fill=RED)
        f_num = fnt(_SANS_B, 40)
        bbox = draw.textbbox((0, 0), num, font=f_num)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text((cx - tw // 2, y + 30 + circle_r - th // 2 - 3), num,
                  font=f_num, fill=WHITE)

        # Title
        f_title = fnt(_SANS_B, 32)
        bbox = draw.textbbox((0, 0), title, font=f_title)
        tw = bbox[2] - bbox[0]
        draw.text((cx - tw // 2, y + 120), title, font=f_title, fill=BG_DARK)

        # Description
        for j, line in enumerate(desc.split("\n")):
            f_desc = fnt(_SANS, 24)
            bbox = draw.textbbox((0, 0), line, font=f_desc)
            tw = bbox[2] - bbox[0]
            draw.text((cx - tw // 2, y + 175 + j * 35), line, font=f_desc, fill=MID_GREY)

    # Footer
    footer_y = SZ - 100
    draw.rectangle([(0, footer_y), (SZ, SZ)], fill=RED)
    center_text(draw, "FREE CANVA ACCOUNT  \u2014  NO DESIGN SKILLS NEEDED",
                footer_y + 25, fnt(_SANS_B, 32), WHITE)

    return img


def build_rank7_please_note(listing):
    """Please Note — digital product disclaimer."""
    img = Image.new("RGB", (SZ, SZ), BG_WHITE)
    draw = ImageDraw.Draw(img)

    # Red header bar
    draw.rectangle([(0, 0), (SZ, 130)], fill=RED)
    center_text(draw, "PLEASE NOTE", 15, fnt(_SANS_B, 65), WHITE)
    center_text(draw, "DIGITAL PRODUCT", 80, fnt(_SANS, 32), (255, 200, 200))

    notes = [
        "This is a DIGITAL download \u2014 nothing\nphysical is shipped",
        "You receive instant access via Etsy\nafter purchase",
        "Editable in Canva \u2014 free account\nrequired",
        "For personal or commercial\nbusiness use",
        "All sales final \u2014 no refunds on\ndigital products",
    ]

    start_y = 230
    bullet_x = 200
    text_x = 280

    for i, note in enumerate(notes):
        y = start_y + i * 260
        # Bullet
        draw.ellipse([(bullet_x, y + 8), (bullet_x + 24, y + 32)], fill=RED)

        lines = note.split("\n")
        for j, line in enumerate(lines):
            f = fnt(_SANS_B, 36) if j == 0 else fnt(_SANS, 32)
            color = BG_DARK if j == 0 else MID_GREY
            draw.text((text_x, y + j * 45), line, font=f, fill=color)

        # Separator line
        if i < len(notes) - 1:
            sep_y = y + 200
            draw.rectangle([(bullet_x, sep_y), (SZ - 200, sep_y + 1)], fill=LIGHT_GREY)

    # Footer
    footer_y = SZ - 100
    draw.rectangle([(0, footer_y), (SZ, SZ)], fill=BG_DARK)
    center_text(draw, "PURPLEOCAZ  \u2014  DIGITAL TEMPLATES",
                footer_y + 28, fnt(_SANS, 30), SILVER)

    return img


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

BUILDERS = [
    ("rank1_hero", build_rank1_hero),
    ("rank2_whats_inside", build_rank2_whats_inside),
    ("rank3_lifestyle", build_rank3_lifestyle),
    ("rank4_how_it_works", build_rank4_how_it_works),
    ("rank5_why_buy", build_rank5_why_buy),
    ("rank6_canva_basics", build_rank6_canva_basics),
    ("rank7_please_note", build_rank7_please_note),
]

if __name__ == "__main__":
    os.chdir(PROJECT)
    load_env()

    all_images = {}  # slug -> [(rank, local_path, spaces_url)]

    for listing in LISTINGS:
        slug = listing["slug"]
        slug_dir = os.path.join(THUMBS, slug)
        os.makedirs(slug_dir, exist_ok=True)
        all_images[slug] = []

        print(f"\n{'='*60}")
        print(f"  {listing['title_line1']} {listing['title_line2']}")
        print(f"{'='*60}")

        for rank_name, builder in BUILDERS:
            print(f"  Building {rank_name}...", end=" ", flush=True)
            img = builder(listing)
            local_path = os.path.join(slug_dir, f"{rank_name}.png")
            img.save(local_path, "PNG")
            print(f"saved ({img.size[0]}x{img.size[1]})")
            all_images[slug].append((rank_name, local_path))

    # Upload all to DO Spaces
    print(f"\n{'='*60}")
    print("  UPLOADING TO DO SPACES")
    print(f"{'='*60}")

    s3 = get_s3()
    urls = {}

    for slug, images in all_images.items():
        urls[slug] = []
        for rank_name, local_path in images:
            key = f"thumbnails/car-detail/{slug}/{rank_name}.png"
            url = upload_file_to_spaces(s3, local_path, key)
            urls[slug].append(url)
            print(f"  [{slug}] {rank_name}: {url}")

    # Save URL map
    urls_path = os.path.join(THUMBS, "spaces_urls.json")
    with open(urls_path, "w") as f:
        json.dump(urls, f, indent=2)

    print(f"\n=== DONE: {sum(len(v) for v in urls.values())} images built and uploaded ===")
    print(f"URLs saved: {urls_path}")
