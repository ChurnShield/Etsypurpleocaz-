#!/usr/bin/env python3
"""Car Detailing Walk-In/Booking Flyer. A4 portrait, full bleed photo.
65% dark overlay, dark badge top centre, services list bottom right.
"""

import os

from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import Color, white, HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

PHOTO_PATH = os.path.join(os.path.dirname(__file__), '..', 'assets', 'photos', 'car_detail_flyer_walkin', 'photo_1.jpg')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'car-detail-flyer-walkin')
OUTPUT_PATH = os.path.join(OUTPUT_DIR, 'Car_Detail_Flyer_WalkIn.pdf')

PAGE_W, PAGE_H = A4
DARK = HexColor('#0D0D0D')
RED = HexColor('#E02020')


def build_pdf():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    c = canvas.Canvas(OUTPUT_PATH, pagesize=A4)
    c.setTitle('Car Detailing Walk-In Flyer')

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

    # ─── DARK OVERLAY 65% ─────────────────────────────────────────────────
    c.setFillColor(Color(0, 0, 0, alpha=0.65))
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    # ─── DARK BADGE (top centre) ─────────────────────────────────────────
    badge_w = 160 * mm
    badge_h = 32 * mm
    badge_x = (PAGE_W - badge_w) / 2
    badge_y = PAGE_H - 65 * mm

    c.setFillColor(Color(0.05, 0.05, 0.05, alpha=0.9))
    c.roundRect(badge_x, badge_y, badge_w, badge_h, 3 * mm, fill=1, stroke=0)

    # Red border
    c.setStrokeColor(Color(0.878, 0.125, 0.125, alpha=0.5))
    c.setLineWidth(0.6)
    c.roundRect(badge_x, badge_y, badge_w, badge_h, 3 * mm, fill=0, stroke=1)

    # Badge text in red
    c.setFillColor(RED)
    c.setFont('Helvetica-Bold', 16)
    c.drawCentredString(cx, badge_y + 17 * mm, 'YOUR STUDIO NAME')
    c.setFont('Helvetica', 7)
    c.drawCentredString(cx, badge_y + 7 * mm, 'C A R   D E T A I L I N G')

    # ─── SCRIPT TAGLINE (left aligned, middle) ────────────────────────────
    c.setFillColor(white)
    c.setFont('Times-Bold', 52)
    c.drawString(margin, PAGE_H * 0.48, 'Transform')
    c.setFillColor(RED)
    c.setFont('Times-BoldItalic', 52)
    c.drawString(margin, PAGE_H * 0.48 - 18 * mm, 'your car')

    # ─── SERVICES LIST (bottom right) ─────────────────────────────────────
    services_x = PAGE_W - margin
    services_y = 95 * mm

    c.setFillColor(RED)
    c.setFont('Helvetica-Bold', 10)
    c.drawRightString(services_x, services_y, 'DETAILING SERVICES')

    c.setFillColor(Color(1, 1, 1, alpha=0.85))
    c.setFont('Helvetica', 9)
    services = ['Exterior Detail', 'Interior Detail', 'Machine Polish', 'Ceramic Coat', 'Full Valet']
    for i, svc in enumerate(services):
        c.drawRightString(services_x, services_y - (i + 1) * 12, svc)

    # ─── BOTTOM TEXT ──────────────────────────────────────────────────────
    c.setFillColor(white)
    c.setFont('Helvetica', 9)
    c.drawCentredString(cx, 22 * mm, 'Walk-ins welcome  |  Free quotes  |  @yourstudio')

    c.setFillColor(Color(1, 1, 1, alpha=0.7))
    c.setFont('Helvetica', 8)
    c.drawCentredString(cx, 14 * mm, '+44 (0) 000 000 0000  |  www.yourstudio.com')

    # ─── RED ACCENT RULE AT BOTTOM ───────────────────────────────────────
    c.setStrokeColor(RED)
    c.setLineWidth(2)
    c.line(0, 5 * mm, PAGE_W, 5 * mm)

    c.save()
    print(f"PDF saved: {OUTPUT_PATH}")
    print(f"Size: {os.path.getsize(OUTPUT_PATH) / 1024:.0f} KB")


if __name__ == '__main__':
    build_pdf()
