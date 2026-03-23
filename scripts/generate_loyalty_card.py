#!/usr/bin/env python3
"""Generate a Tattoo Studio Loyalty Card PDF.

Credit card size landscape (85.6mm x 54mm at 300dpi).
Dark background, circular photo frame with gold ring, stamp circles.

Usage:
    python3 scripts/generate_loyalty_card.py
"""

import math
import os

from PIL import Image
from reportlab.lib.units import mm
from reportlab.lib.colors import Color, white, HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

PHOTO_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'assets', 'photos',
    'tattoo_loyalty_card', 'photo_1.jpg'
)
OUTPUT_DIR = os.path.join(
    os.path.dirname(__file__), '..', 'outputs', 'tattoo-loyalty-card'
)
OUTPUT_PATH = os.path.join(OUTPUT_DIR, 'Tattoo_Loyalty_Card.pdf')

# Credit card dimensions
CARD_W = 85.6 * mm
CARD_H = 54 * mm

DARK = HexColor('#1A1A1A')
GOLD = HexColor('#C9A96E')
GOLD_DIM = Color(0.788, 0.663, 0.431, alpha=0.5)


def build_pdf():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    c = canvas.Canvas(OUTPUT_PATH, pagesize=(CARD_W, CARD_H))
    c.setTitle('Tattoo Studio Loyalty Card')

    # ─── DARK BACKGROUND ──────────────────────────────────────────────────
    c.setFillColor(DARK)
    c.rect(0, 0, CARD_W, CARD_H, fill=1, stroke=0)

    # ─── LAYOUT ZONES ────────────────────────────────────────────────────
    left_w = CARD_W * 0.33
    right_x = left_w
    right_w = CARD_W - left_w
    padding = 3 * mm

    # ─── CIRCULAR PHOTO WITH GOLD RING (left third) ──────────────────────
    circle_r = 16 * mm
    circle_cx = left_w / 2
    circle_cy = CARD_H / 2 + 1 * mm

    # Crop photo to square, then we'll clip to circle
    img = Image.open(PHOTO_PATH)
    iw, ih = img.size
    sq = min(iw, ih)
    left = (iw - sq) // 2
    top = (ih - sq) // 2
    img = img.crop((left, top, left + sq, top + sq))

    # Draw the photo inside a clipping circle
    c.saveState()
    p = c.beginPath()
    p.circle(circle_cx, circle_cy, circle_r)
    p.close()
    c.clipPath(p, stroke=0, fill=0)
    img_x = circle_cx - circle_r
    img_y = circle_cy - circle_r
    c.drawImage(ImageReader(img), img_x, img_y,
                width=circle_r * 2, height=circle_r * 2)
    c.restoreState()

    # Gold ring border
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.2)
    c.circle(circle_cx, circle_cy, circle_r, stroke=1, fill=0)

    # ─── RIGHT SIDE CONTENT ──────────────────────────────────────────────
    rx = right_x + padding
    rr = CARD_W - padding

    # "YOUR STUDIO NAME" — white small caps
    c.setFillColor(white)
    c.setFont('Helvetica', 4.5)
    c.drawString(rx, CARD_H - 7 * mm, 'Y O U R   S T U D I O   N A M E')

    # "Loyalty Card" — gold script
    c.setFillColor(GOLD)
    c.setFont('Times-Italic', 16)
    c.drawString(rx, CARD_H - 14.5 * mm, 'Loyalty Card')

    # "Book 10 sessions..." — white small text
    c.setFillColor(Color(1, 1, 1, alpha=0.7))
    c.setFont('Helvetica', 4.5)
    c.drawString(rx, CARD_H - 19 * mm, 'Book 10 sessions \u2014 get your next one FREE')

    # ─── STAMP CIRCLES (2 rows of 5) ─────────────────────────────────────
    stamp_r = 3.2 * mm
    cols = 5
    rows = 2
    grid_w = rr - rx
    h_spacing = grid_w / cols
    row_top = CARD_H - 24 * mm
    v_spacing = 9 * mm

    for row in range(rows):
        for col in range(cols):
            idx = row * cols + col
            sx = rx + h_spacing * col + h_spacing / 2
            sy = row_top - row * v_spacing

            if idx == 9:
                # Last circle: filled gold with "FREE"
                c.setFillColor(GOLD)
                c.circle(sx, sy, stamp_r, stroke=0, fill=1)
                c.setFillColor(DARK)
                c.setFont('Helvetica-Bold', 4)
                c.drawCentredString(sx, sy - 1.3, 'FREE')
            else:
                # Empty circle with gold outline
                c.setStrokeColor(GOLD)
                c.setLineWidth(0.6)
                c.circle(sx, sy, stamp_r, stroke=1, fill=0)

    # ─── THIN GOLD RULE + CONTACT TEXT ────────────────────────────────────
    rule_y = 6.5 * mm
    c.setStrokeColor(GOLD_DIM)
    c.setLineWidth(0.4)
    c.line(rx, rule_y, rr, rule_y)

    c.setFillColor(Color(1, 1, 1, alpha=0.5))
    c.setFont('Helvetica', 3.5)
    c.drawString(rx, 3.5 * mm, 'hello@yourstudio.com  |  +44 (0) 000 000 0000  |  www.yourstudio.com')

    c.save()
    print(f"PDF saved: {OUTPUT_PATH}")
    print(f"Size: {os.path.getsize(OUTPUT_PATH) / 1024:.0f} KB")


if __name__ == '__main__':
    build_pdf()
