#!/usr/bin/env python3
"""Tattoo Studio Flash Day Event Flyer. A4 portrait."""

import os
import random

from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import Color, white, HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

PHOTO_PATH = os.path.join(os.path.dirname(__file__), '..', 'assets', 'photos', 'tattoo_flyer_flash', 'photo_1.jpg')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'tattoo-flyer-flash')
OUTPUT_PATH = os.path.join(OUTPUT_DIR, 'Tattoo_Flyer_Flash.pdf')

PAGE_W, PAGE_H = A4
DARK = HexColor('#1A1A1A')
GOLD = HexColor('#C9A96E')


def torn_edge_h(c, y_base, page_w, amplitude=5, segments=80):
    """Return jagged edge points along a horizontal line."""
    random.seed(99)
    return [(page_w * i / segments, y_base + random.uniform(-amplitude, amplitude))
            for i in range(segments + 1)]


def build_pdf():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    c = canvas.Canvas(OUTPUT_PATH, pagesize=A4)
    c.setTitle('Tattoo Flash Day Flyer')

    cx = PAGE_W / 2
    margin = 22 * mm

    # Full dark background
    c.setFillColor(DARK)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    # ─── PHOTO STRIP (centre 40%) with dark overlay ──────────────────────
    photo_top = PAGE_H * 0.62
    photo_bottom = PAGE_H * 0.22
    photo_h = photo_top - photo_bottom

    img = Image.open(PHOTO_PATH)
    iw, ih = img.size
    target_ratio = PAGE_W / photo_h
    crop_w = int(ih * target_ratio)
    if crop_w > iw:
        crop_h = int(iw / target_ratio)
        top = (ih - crop_h) // 2
        img = img.crop((0, top, iw, top + crop_h))
    else:
        left = (iw - crop_w) // 2
        img = img.crop((left, 0, left + crop_w, ih))

    c.drawImage(ImageReader(img), 0, photo_bottom, width=PAGE_W, height=photo_h)

    # Dark overlay on photo
    c.setFillColor(Color(0, 0, 0, alpha=0.55))
    c.rect(0, photo_bottom, PAGE_W, photo_h, fill=1, stroke=0)

    # ─── TORN EDGES above and below photo ─────────────────────────────────
    # Top torn edge (dark covers top of photo)
    random.seed(88)
    p_top = c.beginPath()
    p_top.moveTo(0, PAGE_H)
    p_top.lineTo(0, photo_top)
    for i in range(81):
        x = PAGE_W * i / 80
        y = photo_top + random.uniform(-5, 5)
        p_top.lineTo(x, y)
    p_top.lineTo(PAGE_W, PAGE_H)
    p_top.close()
    c.setFillColor(DARK)
    c.drawPath(p_top, fill=1, stroke=0)

    # Bottom torn edge (dark covers bottom of photo)
    random.seed(77)
    p_bot = c.beginPath()
    p_bot.moveTo(0, 0)
    p_bot.lineTo(0, photo_bottom)
    for i in range(81):
        x = PAGE_W * i / 80
        y = photo_bottom + random.uniform(-5, 5)
        p_bot.lineTo(x, y)
    p_bot.lineTo(PAGE_W, 0)
    p_bot.close()
    c.setFillColor(DARK)
    c.drawPath(p_bot, fill=1, stroke=0)

    # ─── TOP TEXT ─────────────────────────────────────────────────────────
    c.setFillColor(white)
    c.setFont('Times-Bold', 44)
    c.drawCentredString(cx, PAGE_H - 38 * mm, 'TATTOO')
    c.drawCentredString(cx, PAGE_H - 56 * mm, 'FLASH DAY')

    c.setFillColor(GOLD)
    c.setFont('Times-Italic', 14)
    c.drawCentredString(cx, PAGE_H - 72 * mm, 'One day only \u2014 special designs at special prices!')

    # ─── CENTRE TEXT (on photo overlay) ───────────────────────────────────
    mid_y = (photo_top + photo_bottom) / 2
    c.setFillColor(white)
    c.setFont('Helvetica-Bold', 18)
    c.drawCentredString(cx, mid_y + 8 * mm, 'SATURDAY, [DATE]')
    c.setFont('Helvetica', 12)
    c.drawCentredString(cx, mid_y - 4 * mm, '12:00 PM \u2014 8:00 PM')

    c.setFillColor(Color(1, 1, 1, alpha=0.6))
    c.setFont('Helvetica', 8)
    c.drawCentredString(cx, mid_y - 16 * mm, '123 Your Street, City, Postcode')

    # ─── BOTTOM TEXT ──────────────────────────────────────────────────────
    c.setFillColor(GOLD)
    c.setFont('Helvetica-Bold', 12)
    c.drawCentredString(cx, 52 * mm, 'DM OR CALL TO SAVE YOUR SPOT!')

    c.setFillColor(white)
    c.setFont('Helvetica', 9)
    c.drawCentredString(cx, 40 * mm, '+44 (0) 000 000 0000')

    c.setFillColor(Color(1, 1, 1, alpha=0.6))
    c.setFont('Helvetica', 8)
    c.drawCentredString(cx, 30 * mm, '@yourstudio  |  www.yourstudio.com')

    c.save()
    print(f"PDF saved: {OUTPUT_PATH}")
    print(f"Size: {os.path.getsize(OUTPUT_PATH) / 1024:.0f} KB")


if __name__ == '__main__':
    build_pdf()
