#!/usr/bin/env python3
"""Car Detailing Mobile Flyer — split layout. A4 portrait.
Left half dark panel, right half full bleed photo, jagged torn edge divider.
"""

import os
import random

from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import Color, white, HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

PHOTO_PATH = os.path.join(os.path.dirname(__file__), '..', 'assets', 'photos', 'car_detail_flyer_mobile', 'photo_1.jpg')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'car-detail-flyer-mobile')
OUTPUT_PATH = os.path.join(OUTPUT_DIR, 'Car_Detail_Flyer_Mobile.pdf')

PAGE_W, PAGE_H = A4
DARK = HexColor('#0D0D0D')
RED = HexColor('#E02020')


def build_pdf():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    c = canvas.Canvas(OUTPUT_PATH, pagesize=A4)
    c.setTitle('Mobile Car Detailing Flyer')

    split_x = PAGE_W * 0.45
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

    # ─── TORN EDGE divider ────────────────────────────────────────────────
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

    # Logo placeholder
    c.setFillColor(white)
    c.setFont('Helvetica-Bold', 8)
    c.drawString(lx, PAGE_H - 28 * mm, 'Y O U R   S T U D I O')

    # Red rule
    c.setStrokeColor(RED)
    c.setLineWidth(0.5)
    c.line(lx, PAGE_H - 34 * mm, lx + lw, PAGE_H - 34 * mm)

    # MOBILE large + "CAR DETAILING"
    c.setFillColor(white)
    c.setFont('Times-Bold', 36)
    c.drawString(lx, PAGE_H - 58 * mm, 'MOBILE')

    c.setFillColor(white)
    c.setFont('Times-Bold', 22)
    c.drawString(lx, PAGE_H - 72 * mm, 'CAR')

    c.setFillColor(RED)
    c.setFont('Times-Italic', 28)
    c.drawString(lx, PAGE_H - 88 * mm, 'Detailing')

    # Tagline
    c.setFillColor(Color(1, 1, 1, alpha=0.6))
    c.setFont('Helvetica', 7)
    c.drawString(lx, PAGE_H - 100 * mm, 'We come to you — professional')
    c.drawString(lx, PAGE_H - 105 * mm, 'detailing at your home or office.')

    # Rule
    c.setStrokeColor(Color(1, 1, 1, alpha=0.2))
    c.setLineWidth(0.4)
    c.line(lx, PAGE_H - 112 * mm, lx + lw, PAGE_H - 112 * mm)

    # Services
    c.setFillColor(RED)
    c.setFont('Helvetica-Bold', 7)
    c.drawString(lx, PAGE_H - 122 * mm, 'OUR SERVICES')
    c.setFillColor(Color(1, 1, 1, alpha=0.7))
    c.setFont('Helvetica', 7)
    services = [
        'Full Exterior Wash & Dry',
        'Interior Vacuum & Wipe',
        'Machine Polish & Wax',
        'Full Valet (Interior + Exterior)',
        'Ceramic Coating',
        'Engine Bay Clean',
    ]
    for i, svc in enumerate(services):
        c.drawString(lx, PAGE_H - (129 + i * 6.5) * mm, f'\u2713  {svc}')

    # CTA button
    btn_w = lw
    btn_h = 12 * mm
    btn_y = PAGE_H - 195 * mm
    c.setFillColor(RED)
    c.roundRect(lx, btn_y, btn_w, btn_h, 2 * mm, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont('Helvetica-Bold', 10)
    c.drawCentredString(lx + btn_w / 2, btn_y + 3.5 * mm, 'BOOK NOW')

    # Contact
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
