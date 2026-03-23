#!/usr/bin/env python3
"""Car Detailing Seasonal Special Flyer. A4 portrait.
Full dark background, full bleed photo with dark overlay, torn paper edges.
"""

import os
import random

from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import Color, white, HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

PHOTO_PATH = os.path.join(os.path.dirname(__file__), '..', 'assets', 'photos', 'car_detail_flyer_seasonal', 'photo_1.jpg')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'car-detail-flyer-seasonal')
OUTPUT_PATH = os.path.join(OUTPUT_DIR, 'Car_Detail_Flyer_Seasonal.pdf')

PAGE_W, PAGE_H = A4
DARK = HexColor('#0D0D0D')
RED = HexColor('#E02020')


def torn_edge_line(c, y_base, page_w, amplitude=5, segments=80):
    random.seed(77)
    p = c.beginPath()
    p.moveTo(0, y_base)
    for i in range(segments + 1):
        x = page_w * i / segments
        jitter = random.uniform(-amplitude, amplitude)
        p.lineTo(x, y_base + jitter)
    return p


def build_pdf():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    c = canvas.Canvas(OUTPUT_PATH, pagesize=A4)
    c.setTitle('Car Detailing Seasonal Special Flyer')

    cx = PAGE_W / 2
    margin = 22 * mm

    # ─── FULL BLEED PHOTO ─────────────────────────────────────────────────
    img = Image.open(PHOTO_PATH)
    iw, ih = img.size
    target_ratio = PAGE_W / PAGE_H
    crop_w = int(ih * target_ratio)
    if crop_w > iw:
        crop_h = int(iw / target_ratio)
        top = (ih - crop_h) // 2
        img = img.crop((0, top, iw, top + crop_h))
    else:
        left = (iw - crop_w) // 2
        img = img.crop((left, 0, left + crop_w, ih))

    c.drawImage(ImageReader(img), 0, 0, width=PAGE_W, height=PAGE_H)

    # ─── DARK OVERLAY 70% ─────────────────────────────────────────────────
    c.setFillColor(Color(0.05, 0.05, 0.05, alpha=0.70))
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    # ─── TORN PAPER EDGES (top and bottom) ────────────────────────────────
    # Top torn edge — dark fill above
    random.seed(88)
    top_y = PAGE_H - 30 * mm
    p_top = c.beginPath()
    p_top.moveTo(0, PAGE_H)
    for i in range(81):
        x = PAGE_W * i / 80
        jitter = random.uniform(-4, 4)
        p_top.lineTo(x, top_y + jitter)
    p_top.lineTo(PAGE_W, PAGE_H)
    p_top.close()
    c.setFillColor(DARK)
    c.drawPath(p_top, fill=1, stroke=0)

    # Bottom torn edge
    random.seed(99)
    bot_y = 30 * mm
    p_bot = c.beginPath()
    p_bot.moveTo(0, 0)
    for i in range(81):
        x = PAGE_W * i / 80
        jitter = random.uniform(-4, 4)
        p_bot.lineTo(x, bot_y + jitter)
    p_bot.lineTo(PAGE_W, 0)
    p_bot.close()
    c.setFillColor(DARK)
    c.drawPath(p_bot, fill=1, stroke=0)

    # ─── CONTENT ──────────────────────────────────────────────────────────
    # Main title
    c.setFillColor(white)
    c.setFont('Times-Bold', 44)
    c.drawCentredString(cx, PAGE_H * 0.58, 'SUMMER')
    c.drawCentredString(cx, PAGE_H * 0.58 - 16 * mm, 'DETAILING')
    c.drawCentredString(cx, PAGE_H * 0.58 - 32 * mm, 'SPECIAL')

    # Script tagline
    c.setFillColor(RED)
    c.setFont('Times-Italic', 20)
    c.drawCentredString(cx, PAGE_H * 0.58 - 48 * mm, 'Your car deserves the best')

    # Offer placeholder
    c.setFillColor(Color(1, 1, 1, alpha=0.7))
    c.setFont('Helvetica', 10)
    c.drawCentredString(cx, PAGE_H * 0.58 - 62 * mm, 'Valid: [Start Date] \u2013 [End Date]')
    c.drawCentredString(cx, PAGE_H * 0.58 - 72 * mm, '[Your Offer Details Here]')

    # Contact at bottom
    c.setFillColor(white)
    c.setFont('Helvetica-Bold', 9)
    c.drawCentredString(cx, 14 * mm, 'YOUR STUDIO NAME')
    c.setFillColor(Color(1, 1, 1, alpha=0.6))
    c.setFont('Helvetica', 7)
    c.drawCentredString(cx, 8 * mm, '+44 (0) 000 000 0000  |  hello@yourstudio.com  |  www.yourstudio.com')

    c.save()
    print(f"PDF saved: {OUTPUT_PATH}")
    print(f"Size: {os.path.getsize(OUTPUT_PATH) / 1024:.0f} KB")


if __name__ == '__main__':
    build_pdf()
