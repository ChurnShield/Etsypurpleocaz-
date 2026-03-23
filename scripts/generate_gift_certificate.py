#!/usr/bin/env python3
"""Generate a Tattoo Studio Gift Certificate PDF.

A4 landscape, white background, photo strip with 4 crops,
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

PHOTO_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'assets', 'photos',
    'tattoo_artist_studio', 'photo_1.jpg'
)
OUTPUT_DIR = os.path.join(
    os.path.dirname(__file__), '..', 'outputs', 'tattoo-gift-certificate'
)
OUTPUT_PATH = os.path.join(OUTPUT_DIR, 'Tattoo_Gift_Certificate.pdf')

PAGE_W, PAGE_H = landscape(A4)  # 841.89 x 595.28 pts

NEAR_BLACK = HexColor('#1A1A1A')
GOLD = HexColor('#C9A96E')
WHITE_BG = HexColor('#FFFFFF')
GREY_LIGHT = Color(0.4, 0.4, 0.4)


def crop_region(img, region):
    """Crop a region from the source image. region is (left%, top%, right%, bottom%)."""
    iw, ih = img.size
    l = int(iw * region[0])
    t = int(ih * region[1])
    r = int(iw * region[2])
    b = int(ih * region[3])
    return img.crop((l, t, r, b))


def build_pdf():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    c = canvas.Canvas(OUTPUT_PATH, pagesize=landscape(A4))
    c.setTitle('Tattoo Studio Gift Certificate')

    # White background
    c.setFillColor(WHITE_BG)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    # Layout constants
    side_margin = 0
    top_bar_h = 28 * mm
    footer_h = 18 * mm
    rule_weight = 0.75
    photo_strip_h = PAGE_H * 0.35
    top_bar_top = PAGE_H
    top_bar_bottom = PAGE_H - top_bar_h

    # ─── TOP BAR ──────────────────────────────────────────────────────────
    # "TATTOO STUDIO" left, small caps
    c.setFillColor(NEAR_BLACK)
    c.setFont('Helvetica', 8)
    ts_text = 'T A T T O O   S T U D I O'
    c.drawString(20 * mm, top_bar_bottom + 10 * mm, ts_text)

    # "Gift Certificate" right, serif italic
    c.setFont('Times-Italic', 22)
    c.drawRightString(PAGE_W - 20 * mm, top_bar_bottom + 8 * mm, 'Gift Certificate')

    # ─── GOLD RULE below top bar ──────────────────────────────────────────
    c.setStrokeColor(GOLD)
    c.setLineWidth(rule_weight)
    rule1_y = top_bar_bottom
    c.line(0, rule1_y, PAGE_W, rule1_y)

    # ─── PHOTO STRIP ─────────────────────────────────────────────────────
    img = Image.open(PHOTO_PATH)

    # 4 different crops for variety
    crops = [
        (0.0, 0.0, 0.35, 0.7),    # top-left region
        (0.25, 0.1, 0.65, 0.9),   # centre
        (0.5, 0.2, 0.85, 0.95),   # right portion
        (0.6, 0.0, 1.0, 0.75),    # top-right region
    ]

    strip_top = rule1_y
    strip_bottom = strip_top - photo_strip_h
    slot_w = PAGE_W / 4
    gap = 1.5  # thin gap between photos

    for i, crop_rect in enumerate(crops):
        cropped = crop_region(img, crop_rect)
        x = side_margin + i * slot_w + (gap if i > 0 else 0)
        w = slot_w - (gap if i > 0 else 0)
        c.drawImage(
            ImageReader(cropped), x, strip_bottom,
            width=w, height=photo_strip_h,
            preserveAspectRatio=False
        )

    # ─── GOLD RULE below photos ───────────────────────────────────────────
    c.setStrokeColor(GOLD)
    c.setLineWidth(rule_weight)
    rule2_y = strip_bottom
    c.line(0, rule2_y, PAGE_W, rule2_y)

    # ─── FORM FIELDS SECTION ─────────────────────────────────────────────
    form_top = rule2_y - 12 * mm
    lm = 25 * mm  # left margin
    rm = PAGE_W - 25 * mm
    mid = PAGE_W / 2
    label_gap = 18 * mm  # space after label text for underline start
    underline_offset = -2  # below baseline

    def draw_form_row(y, fields):
        """fields: list of (label, x_start, x_end)"""
        for label, x0, x1 in fields:
            # Label in small caps
            c.setFillColor(GREY_LIGHT)
            c.setFont('Helvetica', 8)
            spaced = '  '.join(label.upper())
            c.drawString(x0, y, spaced)
            lw = c.stringWidth(spaced, 'Helvetica', 8)
            # Underline from after label to end
            c.setStrokeColor(GOLD)
            c.setLineWidth(0.5)
            line_start = x0 + lw + 4 * mm
            c.line(line_start, y + underline_offset, x1, y + underline_offset)

    # Row 1: TO | AMOUNT
    row1_y = form_top
    draw_form_row(row1_y, [
        ('To:', lm, mid - 15 * mm),
        ('Amount:', mid + 5 * mm, rm),
    ])

    # Row 2: FROM | EXPIRES
    row2_y = form_top - 18 * mm
    draw_form_row(row2_y, [
        ('From:', lm, mid - 15 * mm),
        ('Expires:', mid + 5 * mm, rm),
    ])

    # ─── DISCLAIMER ──────────────────────────────────────────────────────
    c.setFillColor(GREY_LIGHT)
    c.setFont('Times-Italic', 7.5)
    c.drawCentredString(
        PAGE_W / 2, row2_y - 16 * mm,
        'This certificate is non-refundable and cannot be exchanged for cash.'
    )

    # ─── FOOTER BAR ──────────────────────────────────────────────────────
    c.setFillColor(NEAR_BLACK)
    c.rect(0, 0, PAGE_W, footer_h, fill=1, stroke=0)

    # Footer text — white, small, centred items separated by pipes
    c.setFillColor(Color(1, 1, 1, alpha=0.8))
    c.setFont('Helvetica', 7)
    items = [
        'hello@yourstudio.com',
        '+44 (0) 000 000 0000',
        '123 Ink Street, London',
        'www.yourstudio.com',
    ]
    footer_text = '     |     '.join(items)
    c.drawCentredString(PAGE_W / 2, footer_h / 2 - 1 * mm, footer_text)

    # Thin gold line at top of footer
    c.setStrokeColor(GOLD)
    c.setLineWidth(rule_weight)
    c.line(0, footer_h, PAGE_W, footer_h)

    c.save()
    print(f"PDF saved: {OUTPUT_PATH}")
    print(f"Size: {os.path.getsize(OUTPUT_PATH) / 1024:.0f} KB")


if __name__ == '__main__':
    build_pdf()
