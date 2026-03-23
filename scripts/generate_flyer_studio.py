#!/usr/bin/env python3
"""Tattoo Studio General Flyer — split layout. A4 portrait."""

import os
import random

from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import Color, white, HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

PHOTO_PATH = os.path.join(os.path.dirname(__file__), '..', 'assets', 'photos', 'tattoo_flyer_studio', 'photo_1.jpg')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'tattoo-flyer-studio')
OUTPUT_PATH = os.path.join(OUTPUT_DIR, 'Tattoo_Flyer_Studio.pdf')

PAGE_W, PAGE_H = A4
DARK = HexColor('#1A1A1A')
GOLD = HexColor('#C9A96E')


def build_pdf():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    c = canvas.Canvas(OUTPUT_PATH, pagesize=A4)
    c.setTitle('Tattoo Studio Flyer')

    split_x = PAGE_W * 0.45  # left panel width
    padding = 16 * mm

    # ─── RIGHT HALF: FULL PHOTO ───────────────────────────────────────────
    img = Image.open(PHOTO_PATH)
    iw, ih = img.size
    right_w = PAGE_W - split_x
    target_ratio = right_w / PAGE_H
    crop_w = int(ih * target_ratio)
    if crop_w > iw:
        crop_h = int(iw / target_ratio)
        top = (ih - crop_h) // 2
        img = img.crop((0, top, iw, top + crop_h))
    else:
        left = (iw - crop_w) // 2
        img = img.crop((left, 0, left + crop_w, ih))

    c.drawImage(ImageReader(img), split_x, 0, width=right_w, height=PAGE_H)

    # ─── LEFT HALF: DARK PANEL ────────────────────────────────────────────
    c.setFillColor(DARK)
    c.rect(0, 0, split_x, PAGE_H, fill=1, stroke=0)

    # ─── TORN EDGE dividing left and right ────────────────────────────────
    random.seed(55)
    segments = 100
    p = c.beginPath()
    p.moveTo(split_x + 8, PAGE_H)
    for i in range(segments + 1):
        y = PAGE_H - (PAGE_H * i / segments)
        x = split_x + random.uniform(-6, 6)
        p.lineTo(x, y)
    p.lineTo(split_x + 8, 0)
    p.lineTo(0, 0)
    p.lineTo(0, PAGE_H)
    p.close()
    c.setFillColor(DARK)
    c.drawPath(p, fill=1, stroke=0)

    # ─── LEFT PANEL CONTENT ───────────────────────────────────────────────
    lx = padding
    lw = split_x - 2 * padding

    # Logo/name placeholder
    c.setFillColor(white)
    c.setFont('Helvetica-Bold', 8)
    c.drawString(lx, PAGE_H - 28 * mm, 'Y O U R   S T U D I O')

    # Thin gold rule
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.5)
    c.line(lx, PAGE_H - 34 * mm, lx + lw, PAGE_H - 34 * mm)

    # TATTOO large + Studio script
    c.setFillColor(white)
    c.setFont('Times-Bold', 42)
    c.drawString(lx, PAGE_H - 60 * mm, 'TATTOO')

    c.setFillColor(GOLD)
    c.setFont('Times-Italic', 28)
    c.drawString(lx, PAGE_H - 78 * mm, 'Studio')

    # Description placeholder
    c.setFillColor(Color(1, 1, 1, alpha=0.6))
    c.setFont('Helvetica', 7)
    c.drawString(lx, PAGE_H - 95 * mm, 'Custom tattoos crafted with')
    c.drawString(lx, PAGE_H - 100 * mm, 'precision, passion and artistry.')

    # Thin rule
    c.setStrokeColor(Color(1, 1, 1, alpha=0.2))
    c.setLineWidth(0.4)
    c.line(lx, PAGE_H - 110 * mm, lx + lw, PAGE_H - 110 * mm)

    # Opening hours
    c.setFillColor(GOLD)
    c.setFont('Helvetica-Bold', 7)
    c.drawString(lx, PAGE_H - 120 * mm, 'OPENING HOURS')
    c.setFillColor(Color(1, 1, 1, alpha=0.7))
    c.setFont('Helvetica', 7)
    c.drawString(lx, PAGE_H - 127 * mm, 'Mon \u2013 Fri:  10:00 \u2013 19:00')
    c.drawString(lx, PAGE_H - 133 * mm, 'Saturday:   10:00 \u2013 17:00')
    c.drawString(lx, PAGE_H - 139 * mm, 'Sunday:      Closed')

    # Address
    c.setFillColor(GOLD)
    c.setFont('Helvetica-Bold', 7)
    c.drawString(lx, PAGE_H - 155 * mm, 'LOCATION')
    c.setFillColor(Color(1, 1, 1, alpha=0.7))
    c.setFont('Helvetica', 7)
    c.drawString(lx, PAGE_H - 162 * mm, '123 Your Street')
    c.drawString(lx, PAGE_H - 168 * mm, 'City, Postcode')

    # BOOK NOW gold CTA button
    btn_w = lw
    btn_h = 12 * mm
    btn_y = PAGE_H - 195 * mm
    c.setFillColor(GOLD)
    c.roundRect(lx, btn_y, btn_w, btn_h, 2 * mm, fill=1, stroke=0)
    c.setFillColor(DARK)
    c.setFont('Helvetica-Bold', 10)
    c.drawCentredString(lx + btn_w / 2, btn_y + 3.5 * mm, 'BOOK NOW')

    # Phone + website
    c.setFillColor(Color(1, 1, 1, alpha=0.6))
    c.setFont('Helvetica', 7)
    c.drawString(lx, btn_y - 12 * mm, '+44 (0) 000 000 0000')
    c.drawString(lx, btn_y - 19 * mm, 'www.yourstudio.com')
    c.drawString(lx, btn_y - 26 * mm, '@yourstudio')

    c.save()
    print(f"PDF saved: {OUTPUT_PATH}")
    print(f"Size: {os.path.getsize(OUTPUT_PATH) / 1024:.0f} KB")


if __name__ == '__main__':
    build_pdf()
