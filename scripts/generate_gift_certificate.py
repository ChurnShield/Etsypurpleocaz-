#!/usr/bin/env python3
"""Generate a Tattoo Studio Gift Certificate PDF.

A4 landscape, full-bleed tattoo photo background with dark overlay,
white minimal typography, fillable fields.

Usage:
    python3 scripts/generate_gift_certificate.py
"""

import os

from PIL import Image
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.colors import Color, white
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

PHOTO_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'assets', 'photos',
    'tattoo_artist_studio', 'photo_1.jpg'
)
OUTPUT_DIR = os.path.join(
    os.path.dirname(__file__), '..', 'outputs', 'tattoo-gift-certificate'
)
OUTPUT_PATH = os.path.join(OUTPUT_DIR, 'Tattoo_Gift_Certificate.pdf')

PAGE_W, PAGE_H = landscape(A4)  # 841.89 x 595.28 points


def build_pdf():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    c = canvas.Canvas(OUTPUT_PATH, pagesize=landscape(A4))
    c.setTitle('Tattoo Studio Gift Certificate')

    # --- Full-bleed background photo ---
    # Crop to landscape aspect ratio from center of the portrait photo
    img = Image.open(PHOTO_PATH)
    iw, ih = img.size
    target_ratio = PAGE_W / PAGE_H
    crop_h = int(iw / target_ratio)
    if crop_h > ih:
        crop_h = ih
        crop_w = int(ih * target_ratio)
        left = (iw - crop_w) // 2
        img = img.crop((left, 0, left + crop_w, ih))
    else:
        top = (ih - crop_h) // 2
        img = img.crop((0, top, iw, top + crop_h))

    c.drawImage(ImageReader(img), 0, 0, width=PAGE_W, height=PAGE_H)

    # --- Dark overlay (70% opacity black) ---
    c.setFillColor(Color(0, 0, 0, alpha=0.70))
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    # --- Decorative border (thin gold line inset 15mm) ---
    gold = Color(0.76, 0.63, 0.35, alpha=0.6)
    c.setStrokeColor(gold)
    c.setLineWidth(0.75)
    inset = 15 * mm
    c.rect(inset, inset, PAGE_W - 2 * inset, PAGE_H - 2 * inset, fill=0, stroke=1)

    # --- Typography ---
    cx = PAGE_W / 2
    c.setFillColor(white)

    # Top label
    c.setFont('Helvetica', 11)
    c.drawCentredString(cx, PAGE_H - 38 * mm, 'GIFT CERTIFICATE')

    # Studio name
    c.setFont('Helvetica-Bold', 36)
    c.drawCentredString(cx, PAGE_H - 58 * mm, 'TATTOO STUDIO')

    # Thin divider
    c.setStrokeColor(Color(1, 1, 1, alpha=0.4))
    c.setLineWidth(0.5)
    div_y = PAGE_H - 65 * mm
    c.line(cx - 80 * mm, div_y, cx + 80 * mm, div_y)

    # Tagline
    c.setFont('Helvetica-Oblique', 10)
    c.drawCentredString(cx, PAGE_H - 73 * mm, 'This certificate entitles the bearer to')

    # --- Form fields ---
    field_color = Color(1, 1, 1, alpha=0.15)
    label_font = ('Helvetica', 8)
    value_font = ('Helvetica-Bold', 14)

    def draw_field(x, y, w, label):
        # Translucent field background
        c.setFillColor(field_color)
        c.roundRect(x, y, w, 22 * mm, 2 * mm, fill=1, stroke=0)
        # Label above
        c.setFillColor(Color(1, 1, 1, alpha=0.6))
        c.setFont(*label_font)
        c.drawString(x + 4 * mm, y + 24 * mm, label)
        # Placeholder line inside
        c.setStrokeColor(Color(1, 1, 1, alpha=0.3))
        c.setLineWidth(0.5)
        c.line(x + 4 * mm, y + 5 * mm, x + w - 4 * mm, y + 5 * mm)

    # Row 1: Recipient Name (full width)
    row1_y = PAGE_H - 108 * mm
    field_w = PAGE_W - 2 * 30 * mm
    draw_field(30 * mm, row1_y, field_w, 'RECIPIENT NAME')

    # Row 2: Amount/Service | Expiry Date (two columns)
    row2_y = PAGE_H - 143 * mm
    col_w = (field_w - 10 * mm) / 2
    draw_field(30 * mm, row2_y, col_w, 'AMOUNT / SERVICE')
    draw_field(30 * mm + col_w + 10 * mm, row2_y, col_w, 'EXPIRY DATE')

    # Row 3: Artist Signature (full width)
    row3_y = PAGE_H - 178 * mm
    draw_field(30 * mm, row3_y, field_w, 'ARTIST SIGNATURE')

    # --- Footer ---
    c.setFillColor(Color(1, 1, 1, alpha=0.35))
    c.setFont('Helvetica', 7)
    c.drawCentredString(cx, 12 * mm, 'This gift certificate is non-refundable and cannot be exchanged for cash. Present this certificate at time of appointment.')

    c.save()
    print(f"PDF saved: {OUTPUT_PATH}")
    print(f"Size: {os.path.getsize(OUTPUT_PATH) / 1024:.0f} KB")


if __name__ == '__main__':
    build_pdf()
