#!/usr/bin/env python3
"""Tattoo Studio Promotional/Discount Flyer. A4 portrait."""

import os
import random

from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import Color, white, HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

PHOTO_PATH = os.path.join(os.path.dirname(__file__), '..', 'assets', 'photos', 'tattoo_flyer_promo', 'photo_1.jpg')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'tattoo-flyer-promo')
OUTPUT_PATH = os.path.join(OUTPUT_DIR, 'Tattoo_Flyer_Promo.pdf')

PAGE_W, PAGE_H = A4
DARK = HexColor('#1A1A1A')
GOLD = HexColor('#C9A96E')


def torn_edge_path(c, y_base, page_w, amplitude=6, segments=60, direction='down'):
    """Draw a jagged torn-paper edge as a filled polygon."""
    random.seed(42)
    p = c.beginPath()
    points = []
    for i in range(segments + 1):
        x = page_w * i / segments
        jitter = random.uniform(-amplitude, amplitude)
        points.append((x, y_base + jitter))

    if direction == 'down':
        p.moveTo(0, y_base + amplitude + 2)
        for x, y in points:
            p.lineTo(x, y)
        p.lineTo(page_w, y_base + amplitude + 2)
    else:
        p.moveTo(0, y_base - amplitude - 2)
        for x, y in points:
            p.lineTo(x, y)
        p.lineTo(page_w, y_base - amplitude - 2)
    p.close()
    return p


def build_pdf():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    c = canvas.Canvas(OUTPUT_PATH, pagesize=A4)
    c.setTitle('Tattoo Studio Promotional Flyer')

    split_y = PAGE_H * 0.35  # bottom third for photo

    # ─── DARK TOP SECTION ─────────────────────────────────────────────────
    c.setFillColor(DARK)
    c.rect(0, split_y, PAGE_W, PAGE_H - split_y, fill=1, stroke=0)

    margin = 22 * mm
    cx = PAGE_W / 2

    # Top bar: studio name left, icon placeholders right
    c.setFillColor(white)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(margin, PAGE_H - 22 * mm, 'YOUR STUDIO NAME')

    c.setFillColor(Color(1, 1, 1, alpha=0.5))
    c.setFont('Helvetica', 7)
    icons_y = PAGE_H - 22 * mm
    c.drawRightString(PAGE_W - margin, icons_y + 5, 'www.yourstudio.com')
    c.drawRightString(PAGE_W - margin, icons_y - 5, '123 Ink Street, London')
    c.drawRightString(PAGE_W - margin, icons_y - 15, '+44 (0) 000 000 0000')

    # Centre content
    c.setFillColor(Color(1, 1, 1, alpha=0.6))
    c.setFont('Helvetica', 8)
    c.drawCentredString(cx, PAGE_H - 55 * mm, 'P R O F E S S I O N A L   T A T T O O   A R T I S T')

    c.setFillColor(white)
    c.setFont('Times-Bold', 48)
    c.drawCentredString(cx, PAGE_H - 75 * mm, 'TATTOO')
    c.setFont('Times-Bold', 48)
    c.drawCentredString(cx, PAGE_H - 95 * mm, 'STUDIO')

    c.setFillColor(Color(1, 1, 1, alpha=0.6))
    c.setFont('Helvetica', 8)
    c.drawCentredString(cx, PAGE_H - 112 * mm, 'Custom designs crafted with precision and passion')
    c.drawCentredString(cx, PAGE_H - 119 * mm, 'Walk-ins welcome \u2014 appointments preferred')

    # Gold promo box
    box_w = 180 * mm
    box_h = 18 * mm
    box_x = (PAGE_W - box_w) / 2
    box_y = PAGE_H - 148 * mm
    c.setFillColor(GOLD)
    c.rect(box_x, box_y, box_w, box_h, fill=1, stroke=0)
    c.setFillColor(DARK)
    c.setFont('Helvetica-Bold', 14)
    c.drawCentredString(cx, box_y + 5 * mm, 'X% OFF  |  ONLY THIS MONTH')

    # Address placeholder below box
    c.setFillColor(Color(1, 1, 1, alpha=0.5))
    c.setFont('Helvetica', 7)
    c.drawCentredString(cx, box_y - 8 * mm, '123 Your Street, City, Postcode  |  hello@yourstudio.com')

    # ─── TORN EDGE ────────────────────────────────────────────────────────
    c.setFillColor(white)
    path = torn_edge_path(c, split_y, PAGE_W, amplitude=5, segments=80, direction='down')
    c.drawPath(path, fill=1, stroke=0)

    # ─── BOTTOM PHOTO ─────────────────────────────────────────────────────
    img = Image.open(PHOTO_PATH)
    iw, ih = img.size
    target_ratio = PAGE_W / split_y
    crop_h = int(iw / target_ratio)
    if crop_h > ih:
        crop_w = int(ih * target_ratio)
        left = (iw - crop_w) // 2
        img = img.crop((left, 0, left + crop_w, ih))
    else:
        top = (ih - crop_h) // 2
        img = img.crop((0, top, iw, top + crop_h))

    c.drawImage(ImageReader(img), 0, 0, width=PAGE_W, height=split_y)

    # Redraw torn edge on top of photo
    c.setFillColor(DARK)
    path2 = torn_edge_path(c, split_y, PAGE_W, amplitude=5, segments=80, direction='up')
    c.drawPath(path2, fill=1, stroke=0)

    c.save()
    print(f"PDF saved: {OUTPUT_PATH}")
    print(f"Size: {os.path.getsize(OUTPUT_PATH) / 1024:.0f} KB")


if __name__ == '__main__':
    build_pdf()
