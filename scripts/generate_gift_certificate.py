#!/usr/bin/env python3
"""Generate a Tattoo Studio Gift Certificate PDF.

A4 landscape, white background, 4 unique Unsplash photos in strip,
gold accent rules, minimal form fields, dark footer bar.

Usage:
    python3 scripts/generate_gift_certificate.py
"""

import os

from PIL import Image
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.colors import Color, white, HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

PHOTOS_DIR = os.path.join(
    os.path.dirname(__file__), '..', 'assets', 'photos', 'tattoo_gift_cert'
)
PHOTO_PATHS = [os.path.join(PHOTOS_DIR, f'photo_{i}.jpg') for i in range(1, 5)]

OUTPUT_DIR = os.path.join(
    os.path.dirname(__file__), '..', 'outputs', 'tattoo-gift-certificate'
)
OUTPUT_PATH = os.path.join(OUTPUT_DIR, 'Tattoo_Gift_Certificate.pdf')

PAGE_W, PAGE_H = landscape(A4)  # 841.89 x 595.28 pts

NEAR_BLACK = HexColor('#1A1A1A')
GOLD = HexColor('#C9A96E')
GREY_LIGHT = Color(0.55, 0.55, 0.55)


def build_pdf():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    c = canvas.Canvas(OUTPUT_PATH, pagesize=landscape(A4))
    c.setTitle('Tattoo Studio Gift Certificate')

    # White background
    c.setFillColor(white)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    # Layout constants
    top_bar_h = 24 * mm
    footer_h = 14 * mm
    rule_weight = 0.75
    photo_strip_h = PAGE_H * 0.38
    top_bar_bottom = PAGE_H - top_bar_h

    # ─── TOP BAR ──────────────────────────────────────────────────────────
    c.setFillColor(NEAR_BLACK)
    c.setFont('Helvetica', 8)
    c.drawString(20 * mm, top_bar_bottom + 8 * mm, 'T A T T O O   S T U D I O')

    c.setFont('Times-Italic', 22)
    c.drawRightString(PAGE_W - 20 * mm, top_bar_bottom + 6 * mm, 'Gift Certificate')

    # ─── GOLD RULE between header and photos ──────────────────────────────
    c.setStrokeColor(GOLD)
    c.setLineWidth(rule_weight)
    c.line(0, top_bar_bottom, PAGE_W, top_bar_bottom)

    # ─── PHOTO STRIP — 4 unique photos ────────────────────────────────────
    strip_top = top_bar_bottom
    strip_bottom = strip_top - photo_strip_h
    slot_w = PAGE_W / 4
    gap = 1.5

    for i, photo_path in enumerate(PHOTO_PATHS):
        img = Image.open(photo_path)
        # Centre crop to match slot aspect ratio
        iw, ih = img.size
        target_ratio = slot_w / photo_strip_h
        crop_w = int(ih * target_ratio)
        if crop_w > iw:
            crop_h = int(iw / target_ratio)
            top = (ih - crop_h) // 2
            img = img.crop((0, top, iw, top + crop_h))
        else:
            left = (iw - crop_w) // 2
            img = img.crop((left, 0, left + crop_w, ih))

        x = i * slot_w + (gap if i > 0 else 0)
        w = slot_w - (gap if i > 0 else 0)
        c.drawImage(
            ImageReader(img), x, strip_bottom,
            width=w, height=photo_strip_h,
            preserveAspectRatio=False
        )

    # ─── GOLD RULE below photos ───────────────────────────────────────────
    c.setStrokeColor(GOLD)
    c.setLineWidth(rule_weight)
    c.line(0, strip_bottom, PAGE_W, strip_bottom)

    # ─── DISTRIBUTE CONTENT EVENLY ─────────────────────────────────────
    # Available space between photo strip bottom and footer top
    content_top = strip_bottom
    content_bottom = footer_h
    space = content_top - content_bottom

    # Split into 3 zones: form fields (middle-upper), disclaimer, biz details (lower)
    # Form fields centred in upper half, biz details anchored near footer
    form_centre_y = content_bottom + space * 0.68
    biz_centre_y = content_bottom + space * 0.18

    lm = 25 * mm
    rm = PAGE_W - 25 * mm
    mid = PAGE_W / 2

    def draw_form_row(y, fields):
        for label, x0, x1 in fields:
            c.setFillColor(NEAR_BLACK)
            c.setFont('Helvetica', 8)
            spaced = '  '.join(label.upper())
            c.drawString(x0, y, spaced)
            lw = c.stringWidth(spaced, 'Helvetica', 8)
            c.setStrokeColor(GOLD)
            c.setLineWidth(0.5)
            line_start = x0 + lw + 4 * mm
            c.line(line_start, y - 2, x1, y - 2)

    row1_y = form_centre_y + 7 * mm
    draw_form_row(row1_y, [
        ('To:', lm, mid - 15 * mm),
        ('Amount:', mid + 5 * mm, rm),
    ])

    row2_y = form_centre_y - 7 * mm
    draw_form_row(row2_y, [
        ('From:', lm, mid - 15 * mm),
        ('Expires:', mid + 5 * mm, rm),
    ])

    # ─── DISCLAIMER ──────────────────────────────────────────────────────
    c.setFillColor(GREY_LIGHT)
    c.setFont('Times-Italic', 7.5)
    disclaimer_y = form_centre_y - 18 * mm
    c.drawCentredString(
        PAGE_W / 2, disclaimer_y,
        'This certificate is non-refundable and cannot be exchanged for cash.'
    )

    # ─── PLACEHOLDER BUSINESS DETAILS (anchored near footer) ─────────────
    c.setFillColor(NEAR_BLACK)
    c.setFont('Helvetica-Bold', 11)
    c.drawCentredString(PAGE_W / 2, biz_centre_y + 5, 'YOUR STUDIO NAME')

    c.setFillColor(HexColor('#888888'))
    c.setFont('Helvetica', 7.5)
    c.drawCentredString(
        PAGE_W / 2, biz_centre_y - 9,
        '123 Your Street, City  |  hello@yourstudio.com  |  +44 (0) 000 000 0000  |  www.yourstudio.com'
    )

    # ─── FOOTER BAR ──────────────────────────────────────────────────────
    c.setStrokeColor(GOLD)
    c.setLineWidth(rule_weight)
    c.line(0, footer_h, PAGE_W, footer_h)

    c.setFillColor(NEAR_BLACK)
    c.rect(0, 0, PAGE_W, footer_h, fill=1, stroke=0)

    c.setFillColor(white)
    c.setFont('Helvetica', 6)
    c.drawCentredString(PAGE_W / 2, footer_h / 2 - 1 * mm, 'GIFT CERTIFICATE  —  VALID FOR 12 MONTHS FROM DATE OF ISSUE')

    c.save()
    print(f"PDF saved: {OUTPUT_PATH}")
    print(f"Size: {os.path.getsize(OUTPUT_PATH) / 1024:.0f} KB")


if __name__ == '__main__':
    build_pdf()
