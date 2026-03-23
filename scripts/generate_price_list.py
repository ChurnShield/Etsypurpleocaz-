#!/usr/bin/env python3
"""Generate a Tattoo Studio Price List PDF.

A4 portrait, cream background, full-width photo, serif title,
3 boxed pricing sections, dark footer bar.

Usage:
    python3 scripts/generate_price_list.py
"""

import os

from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import Color, white, HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

PHOTO_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'assets', 'photos',
    'tattoo_price_list', 'photo_1.jpg'
)
OUTPUT_DIR = os.path.join(
    os.path.dirname(__file__), '..', 'outputs', 'tattoo-price-list'
)
OUTPUT_PATH = os.path.join(OUTPUT_DIR, 'Tattoo_Price_List.pdf')

PAGE_W, PAGE_H = A4  # 595.28 x 841.89 pts

CREAM = HexColor('#FFFFFF')
NEAR_BLACK = HexColor('#1A1A1A')
GOLD = HexColor('#C9A96E')
FOOTER_BG = HexColor('#1A1A1A')

PRICING = [
    {
        'title': 'SMALL TATTOOS',
        'items': [
            ('Minimal designs', 'from £50'),
            ('Simple linework', 'from £80'),
            ('Small colour pieces', 'from £120'),
        ],
    },
    {
        'title': 'LARGE & CUSTOM TATTOOS',
        'items': [
            ('Half sleeve', 'from £400'),
            ('Full sleeve', 'from £800'),
            ('Back piece', 'from £600'),
        ],
    },
    {
        'title': 'TOUCH UPS & CONSULTATIONS',
        'items': [
            ('Touch up', 'from £30'),
            ('Consultation', 'FREE'),
            ('Cover-up', 'from £150'),
        ],
    },
]


def build_pdf():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    c = canvas.Canvas(OUTPUT_PATH, pagesize=A4)
    c.setTitle('Tattoo Studio Price List')

    # Cream background
    c.setFillColor(CREAM)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    margin = 22 * mm
    content_w = PAGE_W - 2 * margin
    footer_h = 14 * mm

    # ─── TOP BAR ──────────────────────────────────────────────────────────
    top_bar_y = PAGE_H - 18 * mm

    c.setFillColor(NEAR_BLACK)
    c.setFont('Helvetica', 7)
    c.drawString(margin, top_bar_y, 'Y O U R   S T U D I O   N A M E')

    c.setFont('Helvetica', 9)
    c.drawCentredString(PAGE_W / 2, top_bar_y, '\u2726')

    c.setFont('Helvetica', 7)
    c.drawRightString(PAGE_W - margin, top_bar_y, 'T A T T O O   S T U D I O')

    # Thin rule below top bar
    rule_y = top_bar_y - 6 * mm
    c.setStrokeColor(NEAR_BLACK)
    c.setLineWidth(0.5)
    c.line(margin, rule_y, PAGE_W - margin, rule_y)

    # ─── PHOTO ────────────────────────────────────────────────────────────
    photo_h = PAGE_H * 0.22
    photo_top = rule_y - 3 * mm
    photo_bottom = photo_top - photo_h

    img = Image.open(PHOTO_PATH)
    iw, ih = img.size
    target_ratio = content_w / photo_h
    crop_w = int(ih * target_ratio)
    if crop_w > iw:
        crop_h = int(iw / target_ratio)
        top = (ih - crop_h) // 2
        img = img.crop((0, top, iw, top + crop_h))
    else:
        left = (iw - crop_w) // 2
        img = img.crop((left, 0, left + crop_w, ih))

    c.drawImage(ImageReader(img), margin, photo_bottom, width=content_w, height=photo_h)

    # ─── TITLE ────────────────────────────────────────────────────────────
    title_y = photo_bottom - 14 * mm
    c.setFillColor(NEAR_BLACK)
    c.setFont('Times-Bold', 36)
    c.drawCentredString(PAGE_W / 2, title_y, 'TATTOO')

    subtitle_y = title_y - 14 * mm
    c.setFont('Times-Italic', 24)
    c.drawCentredString(PAGE_W / 2, subtitle_y, 'Price List')

    # ─── PRICING BOXES ────────────────────────────────────────────────────
    box_top = subtitle_y - 14 * mm
    box_available_h = box_top - footer_h - 8 * mm
    box_gap = 6 * mm
    box_h = (box_available_h - 2 * box_gap) / 3
    box_padding_x = 8 * mm
    box_padding_top = 3 * mm
    rule_half = 18 * mm

    for i, section in enumerate(PRICING):
        by = box_top - i * (box_h + box_gap)
        bx = margin
        bw = content_w
        bb = by - box_h

        # Box border — gold
        c.setStrokeColor(GOLD)
        c.setLineWidth(0.5)
        c.rect(bx, bb, bw, box_h, fill=0, stroke=1)

        # Category header centred with rules either side — gold
        header_y = by - box_padding_top - 10
        c.setFillColor(GOLD)
        c.setFont('Helvetica-Bold', 8)
        header_text = section['title']
        hw = c.stringWidth(header_text, 'Helvetica-Bold', 8)
        c.drawCentredString(PAGE_W / 2, header_y, header_text)

        # Rules either side of header
        c.setStrokeColor(Color(0.788, 0.663, 0.431, alpha=0.4))
        c.setLineWidth(0.4)
        rule_left_end = PAGE_W / 2 - hw / 2 - 4 * mm
        rule_right_start = PAGE_W / 2 + hw / 2 + 4 * mm
        rule_limit_l = bx + box_padding_x
        rule_limit_r = bx + bw - box_padding_x
        c.line(rule_limit_l, header_y + 3, rule_left_end, header_y + 3)
        c.line(rule_right_start, header_y + 3, rule_limit_r, header_y + 3)

        # Items
        items = section['items']
        item_start_y = header_y - 14
        item_spacing = (bb + 6 - item_start_y) / max(len(items), 1)
        # Recalculate to space evenly in remaining box space
        remaining = item_start_y - bb - 4
        item_spacing = remaining / max(len(items), 1)

        for j, (name, price) in enumerate(items):
            iy = item_start_y - j * item_spacing
            c.setFillColor(NEAR_BLACK)
            c.setFont('Helvetica', 8.5)
            c.drawString(bx + box_padding_x, iy, name)
            c.setFont('Helvetica', 8.5)
            c.drawRightString(bx + bw - box_padding_x, iy, price)

    # ─── FOOTER BAR ──────────────────────────────────────────────────────
    c.setFillColor(FOOTER_BG)
    c.rect(0, 0, PAGE_W, footer_h, fill=1, stroke=0)

    c.setFillColor(white)
    c.setFont('Helvetica', 7)
    footer_items = [
        'hello@yourstudio.com',
        '+44 (0) 000 000 0000',
        'www.yourstudio.com',
    ]
    c.drawCentredString(PAGE_W / 2, footer_h / 2 - 1 * mm, '     |     '.join(footer_items))

    c.save()
    print(f"PDF saved: {OUTPUT_PATH}")
    print(f"Size: {os.path.getsize(OUTPUT_PATH) / 1024:.0f} KB")


if __name__ == '__main__':
    build_pdf()
