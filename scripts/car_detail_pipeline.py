#!/usr/bin/env python3
"""Car Detailing pipeline: previews, delivery PDF, DO Spaces uploads, hero images.

Run from project root:
    python scripts/car_detail_pipeline.py
"""

import io
import os
import sys
import json
import fitz  # PyMuPDF
import boto3
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white as rl_white
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTS = os.path.join(PROJECT, "outputs")

RED = (224, 32, 32)       # #E02020
DARK = (13, 13, 13)       # #0D0D0D
WHITE = (255, 255, 255)
BANNER_RED = RED

# Fonts
_SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
_SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
_SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def _font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

def _center(draw, text, y, font, fill, canvas_w):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((canvas_w - tw) // 2, y), text, font=font, fill=fill)
    return bbox[3] - bbox[1]


# ── PDF to Image ──────────────────────────────────────────────────────────────
def pdf_to_image(pdf_path, dpi=150):
    doc = fitz.open(pdf_path)
    page = doc[0]
    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    doc.close()
    return img


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

def upload_file(s3, local_path, key, content_type=None):
    bucket = os.environ.get("DO_SPACES_BUCKET", "purpleocaz-assets")
    if content_type is None:
        if local_path.endswith(".pdf"):
            content_type = "application/pdf"
        elif local_path.endswith(".png"):
            content_type = "image/png"
        else:
            content_type = "application/octet-stream"
    with open(local_path, "rb") as f:
        s3.put_object(Bucket=bucket, Key=key, Body=f.read(),
                      ContentType=content_type, ACL="public-read")
    region = os.environ.get("DO_SPACES_REGION", "lon1")
    url = f"https://{bucket}.{region}.digitaloceanspaces.com/{key}"
    return url

def upload_image(s3, img, key):
    bucket = os.environ.get("DO_SPACES_BUCKET", "purpleocaz-assets")
    buf = io.BytesIO()
    img.save(buf, format="PNG", quality=95)
    buf.seek(0)
    s3.put_object(Bucket=bucket, Key=key, Body=buf.read(),
                  ContentType="image/png", ACL="public-read")
    region = os.environ.get("DO_SPACES_REGION", "lon1")
    return f"https://{bucket}.{region}.digitaloceanspaces.com/{key}"


# ── Step 1: Form Previews ────────────────────────────────────────────────────
FORM_PDFS = [
    "Vehicle_Intake_Form.pdf",
    "Consent_Liability_Waiver.pdf",
    "Service_Agreement.pdf",
    "Invoice_Template.pdf",
    "Customer_Feedback_Form.pdf",
    "Appointment_Booking_Form.pdf",
    "Aftercare_Instructions.pdf",
    "Detailing_Package_Menu.pdf",
]

def generate_previews():
    forms_dir = os.path.join(OUTPUTS, "car-detail-forms")
    previews = []
    for fname in FORM_PDFS:
        pdf_path = os.path.join(forms_dir, fname)
        if not os.path.exists(pdf_path):
            print(f"  SKIP: {fname} not found")
            continue
        img = pdf_to_image(pdf_path, dpi=200)
        png_name = fname.replace(".pdf", "_preview.png")
        png_path = os.path.join(forms_dir, png_name)
        img.save(png_path, "PNG")
        previews.append(png_path)
        print(f"  Preview: {png_name} ({img.size[0]}x{img.size[1]})")
    return previews


# ── Step 2: Delivery Instructions PDF ────────────────────────────────────────
def generate_delivery_pdf(canva_links=None):
    """Generate delivery instructions PDF. canva_links is a dict of product->shortlink."""
    out_path = os.path.join(OUTPUTS, "car-detail-forms", "Delivery_Instructions.pdf")

    RL_RED = HexColor("#E02020")
    RL_DARK = HexColor("#0D0D0D")

    doc = SimpleDocTemplate(out_path, pagesize=A4,
                           leftMargin=25*mm, rightMargin=25*mm,
                           topMargin=25*mm, bottomMargin=25*mm)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("DTitle", parent=styles["Title"],
                              fontName="Times-Italic", fontSize=22,
                              textColor=RL_DARK, spaceAfter=6))
    styles.add(ParagraphStyle("DHeading", parent=styles["Heading2"],
                              fontName="Helvetica-Bold", fontSize=12,
                              textColor=RL_RED, spaceBefore=14, spaceAfter=4))
    styles.add(ParagraphStyle("DBody", parent=styles["Normal"],
                              fontName="Helvetica", fontSize=10,
                              textColor=RL_DARK, spaceAfter=6, leading=14))

    story = []
    story.append(Paragraph("Car Detailing Templates", styles["DTitle"]))
    story.append(Paragraph("Delivery Instructions", styles["DTitle"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Thank You for Your Purchase!", styles["DHeading"]))
    story.append(Paragraph(
        "You now have access to a complete set of professional car detailing templates. "
        "Every template is fully editable in Canva (free account). Follow the steps below "
        "to customise your templates.", styles["DBody"]))

    story.append(Paragraph("How to Edit Your Templates", styles["DHeading"]))
    steps = [
        "1. Click any Canva link below to open the template.",
        "2. Click 'Use this template' to create your own copy.",
        "3. Edit text, colours, photos and fonts to match your brand.",
        "4. Download as PDF or PNG — ready to print or share digitally.",
    ]
    for s in steps:
        story.append(Paragraph(s, styles["DBody"]))

    story.append(Paragraph("Your Canva Template Links", styles["DHeading"]))
    if canva_links:
        for name, link in canva_links.items():
            story.append(Paragraph(
                f'<b>{name}:</b> <a href="{link}" color="#E02020">{link}</a>',
                styles["DBody"]))
    else:
        story.append(Paragraph(
            "<i>Canva template links will be added once designs are imported.</i>",
            styles["DBody"]))

    story.append(Paragraph("Need Help?", styles["DHeading"]))
    story.append(Paragraph(
        "If you have any questions or need assistance, please message us through Etsy. "
        "We typically respond within 24 hours.", styles["DBody"]))

    story.append(Spacer(1, 20))
    story.append(Paragraph(
        "© PurpleOcaz — All templates are for personal/commercial use. "
        "Resale of the templates themselves is not permitted.",
        ParagraphStyle("Footer", parent=styles["Normal"],
                       fontName="Helvetica", fontSize=7,
                       textColor=HexColor("#999999"), alignment=TA_CENTER)))

    doc.build(story)
    print(f"  Delivery PDF: {out_path}")
    return out_path


# ── Step 3: Hero Images ──────────────────────────────────────────────────────
def build_forms_hero():
    """2x4 grid of form previews on white background with red banner."""
    forms_dir = os.path.join(OUTPUTS, "car-detail-forms")
    SZ = 3000
    img = Image.new("RGB", (SZ, SZ), WHITE)
    draw = ImageDraw.Draw(img)

    # Load form previews
    previews = []
    for fname in FORM_PDFS:
        png = os.path.join(forms_dir, fname.replace(".pdf", "_preview.png"))
        if os.path.exists(png):
            previews.append(Image.open(png))

    if len(previews) < 8:
        print(f"  WARNING: Only {len(previews)} previews found for forms hero")

    # Grid: 2 cols x 4 rows
    cols, rows = 2, 4
    margin = 80
    gap = 40
    cell_w = (SZ - 2 * margin - (cols - 1) * gap) // cols
    cell_h = (SZ - 2 * margin - (rows - 1) * gap - 300) // rows  # Leave room for banner

    for i, prev in enumerate(previews[:8]):
        r = i // cols
        c = i % cols
        x = margin + c * (cell_w + gap)
        y = margin + r * (cell_h + gap)
        # Resize maintaining aspect ratio
        pw, ph = prev.size
        scale = min(cell_w / pw, cell_h / ph)
        nw, nh = int(pw * scale), int(ph * scale)
        resized = prev.resize((nw, nh), Image.LANCZOS)
        # Add subtle shadow
        shadow = Image.new("RGBA", (nw + 8, nh + 8), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.rectangle([(4, 4), (nw + 4, nh + 4)], fill=(0, 0, 0, 60))
        from PIL import ImageFilter
        shadow = shadow.filter(ImageFilter.GaussianBlur(6))
        img.paste(Image.new("RGB", (nw + 8, nh + 8), WHITE),
                  (x + (cell_w - nw) // 2 - 2, y + (cell_h - nh) // 2 - 2))
        # Paste shadow then image
        shadow_rgb = Image.new("RGB", shadow.size, WHITE)
        shadow_rgb.paste(shadow, mask=shadow.split()[3])
        img.paste(shadow_rgb, (x + (cell_w - nw) // 2 - 2, y + (cell_h - nh) // 2 - 2))
        img.paste(resized, (x + (cell_w - nw) // 2, y + (cell_h - nh) // 2))

    # Red banner at bottom
    banner_h = 220
    banner_y = SZ - banner_h
    draw.rectangle([(0, banner_y), (SZ, SZ)], fill=RED)

    _center(draw, "CAR DETAILING", banner_y + 30, _font(_SERIF_B, 80), WHITE, SZ)
    _center(draw, "CLIENT FORMS BUNDLE", banner_y + 120, _font(_SANS_B, 50), WHITE, SZ)
    _center(draw, "8 PROFESSIONAL PDF TEMPLATES  |  INSTANT DOWNLOAD", banner_y + 180,
            _font(_SANS, 28), (255, 255, 255, 200), SZ)

    out = os.path.join(OUTPUTS, "car-detail-forms", "hero_forms_bundle.png")
    img.save(out, "PNG")
    print(f"  Forms hero: {out}")
    return out


def build_visual_hero():
    """3 visual docs fanned on white bg, red banner."""
    SZ = 3000
    img = Image.new("RGB", (SZ, SZ), WHITE)
    draw = ImageDraw.Draw(img)

    docs = [
        os.path.join(OUTPUTS, "car-detail-gift-certificate", "Car_Detail_Gift_Certificate.pdf"),
        os.path.join(OUTPUTS, "car-detail-price-list", "Car_Detail_Price_List.pdf"),
        os.path.join(OUTPUTS, "car-detail-loyalty-card", "Car_Detail_Loyalty_Card.pdf"),
    ]

    renders = []
    for d in docs:
        if os.path.exists(d):
            renders.append(pdf_to_image(d, dpi=200))

    # Fan layout
    rotations = [-12, 0, 12]
    center_x, center_y = SZ // 2, SZ // 2 - 100
    doc_h = 1400

    for i, (r, rot) in enumerate(zip(renders, rotations)):
        pw, ph = r.size
        scale = doc_h / ph
        nw, nh = int(pw * scale), int(ph * scale)
        resized = r.resize((nw, nh), Image.LANCZOS)
        rotated = resized.rotate(-rot, expand=True, resample=Image.BICUBIC,
                                  fillcolor=(255, 255, 255))
        rw, rh = rotated.size
        x = int(center_x - rw // 2 + (i - 1) * 250)
        y = int(center_y - rh // 2)
        img.paste(rotated, (x, y))

    # Red banner at bottom
    banner_h = 220
    banner_y = SZ - banner_h
    draw.rectangle([(0, banner_y), (SZ, SZ)], fill=RED)
    _center(draw, "CAR DETAILING", banner_y + 30, _font(_SERIF_B, 80), WHITE, SZ)
    _center(draw, "VISUAL BUNDLE", banner_y + 120, _font(_SANS_B, 50), WHITE, SZ)
    _center(draw, "GIFT CERTIFICATE  |  PRICE LIST  |  LOYALTY CARD", banner_y + 180,
            _font(_SANS, 28), WHITE, SZ)

    out = os.path.join(OUTPUTS, "car-detail-forms", "hero_visual_bundle.png")
    img.save(out, "PNG")
    print(f"  Visual hero: {out}")
    return out


def build_flyer_hero():
    """4 flyers fanned on white bg, dark banner."""
    SZ = 3000
    img = Image.new("RGB", (SZ, SZ), WHITE)
    draw = ImageDraw.Draw(img)

    flyers = [
        os.path.join(OUTPUTS, "car-detail-flyer-promo", "Car_Detail_Flyer_Promo.pdf"),
        os.path.join(OUTPUTS, "car-detail-flyer-seasonal", "Car_Detail_Flyer_Seasonal.pdf"),
        os.path.join(OUTPUTS, "car-detail-flyer-mobile", "Car_Detail_Flyer_Mobile.pdf"),
        os.path.join(OUTPUTS, "car-detail-flyer-walkin", "Car_Detail_Flyer_WalkIn.pdf"),
    ]

    renders = []
    for f in flyers:
        if os.path.exists(f):
            renders.append(pdf_to_image(f, dpi=200))

    rotations = [-15, -5, 5, 15]
    center_x, center_y = SZ // 2, SZ // 2 - 100
    doc_h = 1300

    for i, (r, rot) in enumerate(zip(renders, rotations)):
        pw, ph = r.size
        scale = doc_h / ph
        nw, nh = int(pw * scale), int(ph * scale)
        resized = r.resize((nw, nh), Image.LANCZOS)
        rotated = resized.rotate(-rot, expand=True, resample=Image.BICUBIC,
                                  fillcolor=(255, 255, 255))
        rw, rh = rotated.size
        x = int(center_x - rw // 2 + (i - 1.5) * 200)
        y = int(center_y - rh // 2)
        img.paste(rotated, (x, y))

    # Dark banner
    banner_h = 220
    banner_y = SZ - banner_h
    draw.rectangle([(0, banner_y), (SZ, SZ)], fill=DARK)
    _center(draw, "CAR DETAILING", banner_y + 30, _font(_SERIF_B, 80), WHITE, SZ)
    _center(draw, "FLYER PACK", banner_y + 120, _font(_SANS_B, 50), WHITE, SZ)
    _center(draw, "4 EDITABLE TEMPLATES  |  INSTANT DOWNLOAD", banner_y + 180,
            _font(_SANS, 28), (200, 200, 200), SZ)

    out = os.path.join(OUTPUTS, "car-detail-forms", "hero_flyer_pack.png")
    img.save(out, "PNG")
    print(f"  Flyer hero: {out}")
    return out


def build_starter_hero():
    """All 15 products collage, dark banner."""
    SZ = 3000
    img = Image.new("RGB", (SZ, SZ), WHITE)
    draw = ImageDraw.Draw(img)

    # Collect all PDFs
    all_pdfs = []
    forms_dir = os.path.join(OUTPUTS, "car-detail-forms")
    for fname in FORM_PDFS:
        p = os.path.join(forms_dir, fname)
        if os.path.exists(p):
            all_pdfs.append(p)

    visual_docs = [
        os.path.join(OUTPUTS, "car-detail-gift-certificate", "Car_Detail_Gift_Certificate.pdf"),
        os.path.join(OUTPUTS, "car-detail-price-list", "Car_Detail_Price_List.pdf"),
        os.path.join(OUTPUTS, "car-detail-loyalty-card", "Car_Detail_Loyalty_Card.pdf"),
    ]
    flyers = [
        os.path.join(OUTPUTS, "car-detail-flyer-promo", "Car_Detail_Flyer_Promo.pdf"),
        os.path.join(OUTPUTS, "car-detail-flyer-seasonal", "Car_Detail_Flyer_Seasonal.pdf"),
        os.path.join(OUTPUTS, "car-detail-flyer-mobile", "Car_Detail_Flyer_Mobile.pdf"),
        os.path.join(OUTPUTS, "car-detail-flyer-walkin", "Car_Detail_Flyer_WalkIn.pdf"),
    ]
    all_pdfs.extend([p for p in visual_docs + flyers if os.path.exists(p)])

    # Render thumbnails small
    renders = []
    for p in all_pdfs[:15]:
        renders.append(pdf_to_image(p, dpi=100))

    # 5 cols x 3 rows
    cols, rows = 5, 3
    margin = 100
    gap = 30
    cell_w = (SZ - 2 * margin - (cols - 1) * gap) // cols
    cell_h = (SZ - 2 * margin - (rows - 1) * gap - 300) // rows

    for i, r in enumerate(renders):
        row = i // cols
        col = i % cols
        x = margin + col * (cell_w + gap)
        y = margin + row * (cell_h + gap)
        pw, ph = r.size
        scale = min(cell_w / pw, cell_h / ph)
        nw, nh = int(pw * scale), int(ph * scale)
        resized = r.resize((nw, nh), Image.LANCZOS)
        cx = x + (cell_w - nw) // 2
        cy = y + (cell_h - nh) // 2
        img.paste(resized, (cx, cy))
        # Border
        draw.rectangle([(cx - 1, cy - 1), (cx + nw, cy + nh)], outline=(200, 200, 200), width=1)

    # Dark banner
    banner_h = 240
    banner_y = SZ - banner_h
    draw.rectangle([(0, banner_y), (SZ, SZ)], fill=DARK)
    _center(draw, "COMPLETE CAR DETAILING", banner_y + 20, _font(_SERIF_B, 70), WHITE, SZ)
    _center(draw, "BUSINESS BUNDLE", banner_y + 100, _font(_SANS_B, 60), RED, SZ)
    _center(draw, "15 TEMPLATES  |  FORMS  |  FLYERS  |  PRICE LIST  |  GIFT CERTIFICATE", banner_y + 180,
            _font(_SANS, 24), (200, 200, 200), SZ)

    out = os.path.join(OUTPUTS, "car-detail-forms", "hero_starter_bundle.png")
    img.save(out, "PNG")
    print(f"  Starter hero: {out}")
    return out


# ── Step 4: Upload all to DO Spaces ──────────────────────────────────────────
def upload_all(s3):
    urls = {}

    # Forms
    forms_dir = os.path.join(OUTPUTS, "car-detail-forms")
    for fname in FORM_PDFS:
        path = os.path.join(forms_dir, fname)
        if os.path.exists(path):
            key = f"templates/car-detail-forms/{fname}"
            url = upload_file(s3, path, key)
            urls[f"form_{fname}"] = url
            print(f"  Uploaded: {key}")

    # Delivery PDF
    delivery = os.path.join(forms_dir, "Delivery_Instructions.pdf")
    if os.path.exists(delivery):
        url = upload_file(s3, delivery, "templates/car-detail-forms/Delivery_Instructions.pdf")
        urls["delivery_forms"] = url
        print(f"  Uploaded: delivery instructions")

    # Visual docs
    visual_map = {
        "car-detail-gift-certificate/Car_Detail_Gift_Certificate.pdf": "templates/car-detail-gift-certificate/Car_Detail_Gift_Certificate.pdf",
        "car-detail-price-list/Car_Detail_Price_List.pdf": "templates/car-detail-price-list/Car_Detail_Price_List.pdf",
        "car-detail-loyalty-card/Car_Detail_Loyalty_Card.pdf": "templates/car-detail-loyalty-card/Car_Detail_Loyalty_Card.pdf",
    }
    for local_rel, key in visual_map.items():
        path = os.path.join(OUTPUTS, local_rel)
        if os.path.exists(path):
            url = upload_file(s3, path, key)
            urls[local_rel] = url
            print(f"  Uploaded: {key}")

    # Flyers
    flyer_map = {
        "car-detail-flyer-promo/Car_Detail_Flyer_Promo.pdf": "templates/car-detail-flyer-promo/Car_Detail_Flyer_Promo.pdf",
        "car-detail-flyer-seasonal/Car_Detail_Flyer_Seasonal.pdf": "templates/car-detail-flyer-seasonal/Car_Detail_Flyer_Seasonal.pdf",
        "car-detail-flyer-mobile/Car_Detail_Flyer_Mobile.pdf": "templates/car-detail-flyer-mobile/Car_Detail_Flyer_Mobile.pdf",
        "car-detail-flyer-walkin/Car_Detail_Flyer_WalkIn.pdf": "templates/car-detail-flyer-walkin/Car_Detail_Flyer_WalkIn.pdf",
    }
    for local_rel, key in flyer_map.items():
        path = os.path.join(OUTPUTS, local_rel)
        if os.path.exists(path):
            url = upload_file(s3, path, key)
            urls[local_rel] = url
            print(f"  Uploaded: {key}")

    # Hero images
    heroes = [
        "hero_forms_bundle.png",
        "hero_visual_bundle.png",
        "hero_flyer_pack.png",
        "hero_starter_bundle.png",
    ]
    for h in heroes:
        path = os.path.join(forms_dir, h)
        if os.path.exists(path):
            key = f"templates/car-detail-heroes/{h}"
            url = upload_file(s3, path, key, "image/png")
            urls[f"hero_{h}"] = url
            print(f"  Uploaded: {key}")

    return urls


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    os.chdir(PROJECT)
    load_env()

    print("=== Step 1: Generate Form Previews ===")
    previews = generate_previews()

    print("\n=== Step 2: Generate Delivery PDF ===")
    delivery = generate_delivery_pdf()

    print("\n=== Step 3: Build Hero Images ===")
    h1 = build_forms_hero()
    h2 = build_visual_hero()
    h3 = build_flyer_hero()
    h4 = build_starter_hero()

    print("\n=== Step 4: Upload to DO Spaces ===")
    s3 = get_s3()
    urls = upload_all(s3)

    print(f"\n=== DONE: {len(urls)} files uploaded ===")
    # Save URLs for reference
    urls_path = os.path.join(OUTPUTS, "car-detail-forms", "spaces_urls.json")
    with open(urls_path, "w") as f:
        json.dump(urls, f, indent=2)
    print(f"URLs saved: {urls_path}")
