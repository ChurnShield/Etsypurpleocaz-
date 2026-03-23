#!/usr/bin/env python3
"""Generate a Car Detailing Gift Certificate PDF.

A4 landscape, white background, 4 unique Unsplash photos in strip,
red accent rules, minimal form fields, dark footer bar.
"""

import os

from PIL import Image
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.colors import Color, white, HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

PHOTOS_DIR = os.path.join(
    os.path.dirname(__file__), '..', 'assets', 'photos', 'car_detail_gift_cert'
)
PHOTO_PATHS = [os.path.join(PHOTOS_DIR, f'photo_{i}.jpg') for i in range(1, 5)]

OUTPUT_DIR = os.path.join(
    os.path.dirname(__file__), '..', 'outputs', 'car-detail-gift-certificate'
)
OUTPUT_PATH = os.path.join(OUTPUT_DIR, 'Car_Detail_Gift_Certificate.pdf')

PAGE_W, PAGE_H = landscape(A4)

DARK = HexColor('#0D0D0D')
RED = HexColor('#E02020')
GREY_LIGHT = Color(0.55, 0.55, 0.55)


def build_pdf():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    c = canvas.Canvas(OUTPUT_PATH, pagesize=landscape(A4))
    c.setTitle('Car Detailing Gift Certificate')

    # White background
    c.setFillColor(white)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    top_bar_h = 24 * mm
    footer_h = 14 * mm
    rule_weight = 0.75
    photo_strip_h = PAGE_H * 0.38
    top_bar_bottom = PAGE_H - top_bar_h

    # ─── TOP BAR ──────────────────────────────────────────────────────────
    c.setFillColor(DARK)
    c.setFont('Helvetica', 8)
    c.drawString(20 * mm, top_bar_bottom + 8 * mm, 'Y O U R   D E T A I L I N G   S T U D I O')

    c.setFont('Helvetica', 9)
    c.drawCentredString(PAGE_W / 2, top_bar_bottom + 8 * mm, '\u2726')

    c.setFont('Helvetica', 8)
    c.drawRightString(PAGE_W - 20 * mm, top_bar_bottom + 8 * mm, 'C A R   D E T A I L I N G')

    c.setFont('Times-Italic', 22)
    c.drawRightString(PAGE_W - 20 * mm, top_bar_bottom + 16 * mm, '')
    # Title on left side
    c.setFillColor(DARK)
    c.setFont('Times-Italic', 22)

    # ─── RED RULE between header and photos ──────────────────────────────
    c.setStrokeColor(RED)
    c.setLineWidth(rule_weight)
    c.line(0, top_bar_bottom, PAGE_W, top_bar_bottom)

    # ─── PHOTO STRIP — 4 unique photos ────────────────────────────────────
    strip_top = top_bar_bottom
    strip_bottom = strip_top - photo_strip_h
    slot_w = PAGE_W / 4
    gap = 1.5

    for i, photo_path in enumerate(PHOTO_PATHS):
        img = Image.open(photo_path)
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

    # ─── RED RULE below photos ───────────────────────────────────────────
    c.setStrokeColor(RED)
    c.setLineWidth(rule_weight)
    c.line(0, strip_bottom, PAGE_W, strip_bottom)

    # ─── CONTENT AREA ────────────────────────────────────────────────────
    content_top = strip_bottom
    content_bottom = footer_h
    space = content_top - content_bottom

    form_centre_y = content_bottom + space * 0.68
    biz_centre_y = content_bottom + space * 0.18

    lm = 25 * mm
    rm = PAGE_W - 25 * mm

    def draw_form_row(y, fields):
        for label, x0, x1 in fields:
            c.setFillColor(DARK)
            c.setFont('Helvetica', 8)
            spaced = '  '.join(label.upper())
            c.drawString(x0, y, spaced)
            lw = c.stringWidth(spaced, 'Helvetica', 8)
            c.setStrokeColor(RED)
            c.setLineWidth(0.5)
            line_start = x0 + lw + 4 * mm
            c.line(line_start, y - 2, x1, y - 2)

    row1_y = form_centre_y + 7 * mm
    draw_form_row(row1_y, [
        ('To:', lm, PAGE_W / 2 - 15 * mm),
        ('Amount:', PAGE_W / 2 + 5 * mm, rm),
    ])

    row2_y = form_centre_y - 7 * mm
    draw_form_row(row2_y, [
        ('From:', lm, PAGE_W / 2 - 15 * mm),
        ('Expires:', PAGE_W / 2 + 5 * mm, rm),
    ])

    # ─── DISCLAIMER ──────────────────────────────────────────────────────
    c.setFillColor(GREY_LIGHT)
    c.setFont('Times-Italic', 7.5)
    disclaimer_y = form_centre_y - 18 * mm
    c.drawCentredString(
        PAGE_W / 2, disclaimer_y,
        'This certificate is non-refundable and cannot be exchanged for cash.'
    )

    # ─── BUSINESS DETAILS ────────────────────────────────────────────────
    c.setFillColor(DARK)
    c.setFont('Helvetica-Bold', 11)
    c.drawCentredString(PAGE_W / 2, biz_centre_y + 5, 'YOUR STUDIO NAME')

    c.setFillColor(HexColor('#888888'))
    c.setFont('Helvetica', 7.5)
    c.drawCentredString(
        PAGE_W / 2, biz_centre_y - 9,
        '123 Your Street, City  |  hello@yourstudio.com  |  +44 (0) 000 000 0000  |  www.yourstudio.com'
    )

    # ─── FOOTER BAR ──────────────────────────────────────────────────────
    c.setStrokeColor(RED)
    c.setLineWidth(rule_weight)
    c.line(0, footer_h, PAGE_W, footer_h)

    c.setFillColor(DARK)
    c.rect(0, 0, PAGE_W, footer_h, fill=1, stroke=0)

    c.setFillColor(white)
    c.setFont('Helvetica', 8)
    c.drawCentredString(PAGE_W / 2, footer_h / 2 - 1 * mm,
                        'GIFT CERTIFICATE  \u2014  VALID FOR 12 MONTHS FROM DATE OF ISSUE')

    c.save()
    print(f"PDF saved: {OUTPUT_PATH}")
    print(f"Size: {os.path.getsize(OUTPUT_PATH) / 1024:.0f} KB")


if __name__ == '__main__':
    build_pdf()
