#!/usr/bin/env python3
"""
Demo: End-to-End Tier 1 Tattoo Appointment Card Product Creation

Creates a complete digital product package for an Etsy listing:
  - Page 1: Hero mockup (flat-lay style product photo)
  - Page 2: "What You Get" infographic
  - Pages 3-5: Boilerplate (Please Note, Usage Ideas, Thank You)
  - Editable PDF: 6-page fillable PDF (front/back cards + print sheets)
  - Affiliate guide: 2-page "Getting Started" PDF

Uses Pillow + ReportLab only (no Playwright/Gemini required).
"""

import os
import sys
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "..", "workflows", "auto_listing_creator", "exports")
os.makedirs(OUTPUT_DIR, exist_ok=True)

IMG_W, IMG_H = 2250, 3000
BAND_H = 750

# Colours
DARK_BG = (13, 13, 13)
DARK_CARD = (26, 26, 26)
BRAND_PURPLE = (107, 33, 137)
BRAND_PURPLE_HEX = "#6B2189"
ACCENT_ORANGE = (255, 107, 0)
ACCENT_GOLD = (201, 168, 76)
WHITE = (255, 255, 255)
LIGHT_GREY = (192, 192, 192)
MID_GREY = (115, 115, 115)
FIELD_LINE = (204, 204, 204)
BEIGE_BG = (235, 228, 218)

# Fonts (system)
FONT_SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
FONT_SERIF_ITALIC = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
FONT_SERIF_BOLD_ITALIC = "/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf"
FONT_SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
FONT_SANS_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_SANS_ITALIC = "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"

PRODUCT_TYPE = "Appointment Card"
NICHE = "tattoo"
TITLE = "Tattoo Studio Appointment Card, Editable Template, Instant Download"
SAFE_TITLE = "Tattoo Studio Appointment Card"
HERO_TITLE = "Tattoo Studio\nAppointment Card"
TAGLINE = "KEEP YOUR CLIENTS COMING BACK"


def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


# ===========================================================================
# Page 1: Hero Mockup (flat-lay product photo style)
# ===========================================================================

def _draw_card_front(draw, x, y, w, h):
    """Draw the front appointment card design."""
    # White card background
    draw.rounded_rectangle([x, y, x + w, y + h], radius=12, fill=WHITE)

    # Thin double border
    draw.rounded_rectangle([x + 6, y + 6, x + w - 6, y + h - 6],
                           radius=10, outline=(220, 220, 220), width=1)
    draw.rounded_rectangle([x + 10, y + 10, x + w - 10, y + h - 10],
                           radius=8, outline=(220, 220, 220), width=1)

    cx = x + w // 2

    # Title: "Appointment Card" in italic serif
    title_font = load_font(FONT_SERIF_BOLD_ITALIC, int(h * 0.075))
    bbox = draw.textbbox((0, 0), "Appointment Card", font=title_font)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, y + int(h * 0.06)), "Appointment Card",
              font=title_font, fill=(40, 40, 40))

    # Ornamental divider line
    div_y = y + int(h * 0.17)
    line_half = int(w * 0.25)
    draw.line([(cx - line_half, div_y), (cx + line_half, div_y)],
              fill=(100, 100, 100), width=2)
    # Diamond in centre
    d = 6
    draw.polygon([(cx, div_y - d), (cx + d, div_y),
                  (cx, div_y + d), (cx - d, div_y)], fill=(100, 100, 100))

    # Form fields
    label_font = load_font(FONT_SANS_BOLD, int(h * 0.038))
    fields = ["NAME:", "DATE:", "TIME:", "DAY:"]
    field_left = x + int(w * 0.1)
    field_right = x + int(w * 0.9)
    field_start_y = y + int(h * 0.25)
    field_spacing = int(h * 0.135)

    for i, label in enumerate(fields):
        fy = field_start_y + i * field_spacing
        draw.text((field_left, fy), label, font=label_font, fill=(60, 60, 60))
        bbox = draw.textbbox((0, 0), label, font=label_font)
        lw = bbox[2] - bbox[0]
        line_start = field_left + lw + 12
        line_y = fy + int(h * 0.045)
        draw.line([(line_start, line_y), (field_right, line_y)],
                  fill=FIELD_LINE, width=2)


def _draw_card_back(draw, x, y, w, h):
    """Draw the back appointment card design."""
    # White card background
    draw.rounded_rectangle([x, y, x + w, y + h], radius=12, fill=WHITE)
    draw.rounded_rectangle([x + 6, y + 6, x + w - 6, y + h - 6],
                           radius=10, outline=(220, 220, 220), width=1)
    draw.rounded_rectangle([x + 10, y + 10, x + w - 10, y + h - 10],
                           radius=8, outline=(220, 220, 220), width=1)

    cx = x + w // 2

    # Title
    title_font = load_font(FONT_SERIF_BOLD_ITALIC, int(h * 0.075))
    bbox = draw.textbbox((0, 0), "Book Appointment", font=title_font)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, y + int(h * 0.06)), "Book Appointment",
              font=title_font, fill=(40, 40, 40))

    # Divider
    div_y = y + int(h * 0.17)
    line_half = int(w * 0.25)
    draw.line([(cx - line_half, div_y), (cx + line_half, div_y)],
              fill=(100, 100, 100), width=2)
    d = 6
    draw.polygon([(cx, div_y - d), (cx + d, div_y),
                  (cx, div_y + d), (cx - d, div_y)], fill=(100, 100, 100))

    # Fields
    label_font = load_font(FONT_SANS_BOLD, int(h * 0.038))
    fields = ["EMAIL:", "PHONE:", "WEBSITE:"]
    field_left = x + int(w * 0.1)
    field_right = x + int(w * 0.9)
    field_start_y = y + int(h * 0.25)
    field_spacing = int(h * 0.135)

    for i, label in enumerate(fields):
        fy = field_start_y + i * field_spacing
        draw.text((field_left, fy), label, font=label_font, fill=(60, 60, 60))
        bbox = draw.textbbox((0, 0), label, font=label_font)
        lw = bbox[2] - bbox[0]
        line_start = field_left + lw + 12
        line_y = fy + int(h * 0.045)
        draw.line([(line_start, line_y), (field_right, line_y)],
                  fill=FIELD_LINE, width=2)

    # LOGO circle placeholder (top-right)
    logo_r = int(w * 0.06)
    logo_cx = x + w - int(w * 0.12)
    logo_cy = y + int(h * 0.1)
    draw.ellipse([logo_cx - logo_r, logo_cy - logo_r,
                  logo_cx + logo_r, logo_cy + logo_r],
                 outline=(180, 180, 180), width=2)
    logo_font = load_font(FONT_SANS, int(h * 0.025))
    bbox = draw.textbbox((0, 0), "LOGO", font=logo_font)
    lw = bbox[2] - bbox[0]
    lh = bbox[3] - bbox[1]
    draw.text((logo_cx - lw // 2, logo_cy - lh // 2), "LOGO",
              font=logo_font, fill=(180, 180, 180))

    # Decorative tattoo icon (simple mandala circle) below fields
    icon_y = y + int(h * 0.7)
    icon_r = int(w * 0.05)
    draw.ellipse([cx - icon_r, icon_y - icon_r, cx + icon_r, icon_y + icon_r],
                 outline=(160, 160, 160), width=1)
    inner_r = int(icon_r * 0.6)
    draw.ellipse([cx - inner_r, icon_y - inner_r,
                  cx + inner_r, icon_y + inner_r],
                 outline=(180, 180, 180), width=1)
    # Small cross lines
    tiny = int(icon_r * 0.35)
    draw.line([(cx - tiny, icon_y), (cx + tiny, icon_y)],
              fill=(180, 180, 180), width=1)
    draw.line([(cx, icon_y - tiny), (cx, icon_y + tiny)],
              fill=(180, 180, 180), width=1)


def _draw_tattoo_props(draw, hero):
    """Draw simplified tattoo-niche props around the cards."""
    # Eucalyptus leaves (top-left) - simple leaf shapes
    leaf_colour = (80, 110, 80)
    for angle_offset in range(3):
        lx = 120 + angle_offset * 70
        ly = 80 + angle_offset * 40
        leaf_w, leaf_h = 40, 100
        draw.ellipse([lx, ly, lx + leaf_w, ly + leaf_h],
                     fill=leaf_colour, outline=(60, 90, 60))

    # Ink bottle (top-left area)
    bx, by = 320, 150
    draw.rounded_rectangle([bx, by, bx + 60, by + 90], radius=4,
                           fill=(30, 30, 30), outline=(50, 50, 50))
    draw.rectangle([bx + 18, by - 20, bx + 42, by + 5],
                   fill=(40, 40, 40), outline=(60, 60, 60))

    # Tattoo machine pen (left side)
    px, py = 150, 700
    draw.rounded_rectangle([px, py, px + 30, py + 250], radius=8,
                           fill=(35, 35, 35), outline=(55, 55, 55))
    draw.rounded_rectangle([px + 5, py + 250, px + 25, py + 280], radius=3,
                           fill=(50, 50, 50))

    # Flash art sheet (top-right) - small white paper with tiny drawings
    fx, fy = 1700, 100
    # Slight rotation effect by using polygon
    draw.polygon([(fx, fy), (fx + 300, fy + 20), (fx + 280, fy + 380),
                  (fx - 20, fy + 360)], fill=(248, 248, 248),
                 outline=(220, 220, 220))
    # Tiny line art on the "flash sheet"
    for row in range(3):
        for col in range(2):
            sx = fx + 40 + col * 130
            sy = fy + 50 + row * 100
            draw.ellipse([sx, sy, sx + 60, sy + 60],
                         outline=(180, 180, 180), width=1)

    # Scattered needles (bottom-right)
    for i in range(3):
        nx = 1800 + i * 40
        ny = 1600 + i * 30
        draw.line([(nx, ny), (nx + 80, ny + 10)], fill=(100, 100, 100), width=2)
        draw.ellipse([nx + 78, ny + 8, nx + 84, ny + 14],
                     fill=(120, 120, 120))

    # Nitrile glove (bottom-right)
    gx, gy = 1900, 1700
    draw.rounded_rectangle([gx, gy, gx + 180, gy + 120], radius=15,
                           fill=(25, 25, 30), outline=(40, 40, 45))


def create_page1():
    """Create the hero mockup image (page 1)."""
    print("  Creating Page 1: Hero mockup...", flush=True)

    hero = Image.new("RGB", (IMG_W, IMG_H), BEIGE_BG)
    draw = ImageDraw.Draw(hero)

    # Add subtle texture/noise to beige background
    import random
    random.seed(42)
    for _ in range(50000):
        rx = random.randint(0, IMG_W - 1)
        ry = random.randint(0, int(IMG_H * 0.7) - 1)
        offset = random.randint(-8, 8)
        c = tuple(max(0, min(255, v + offset)) for v in BEIGE_BG)
        draw.point((rx, ry), fill=c)

    # Draw tattoo-niche props
    _draw_tattoo_props(draw, hero)

    # Product showcase area (top 70%)
    showcase_h = IMG_H - BAND_H
    showcase_cx = IMG_W // 2
    showcase_cy = showcase_h // 2

    card_w, card_h = 700, 440

    # Back card (left, rotated slightly)
    back_card = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    back_draw = ImageDraw.Draw(back_card)
    _draw_card_back(back_draw, 0, 0, card_w, card_h)

    # Add shadow
    shadow = Image.new("RGBA", (card_w + 60, card_h + 60), (0, 0, 0, 0))
    shadow_inner = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 80))
    shadow.paste(shadow_inner, (38, 38))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))

    back_rot = back_card.rotate(10, expand=True, resample=Image.BICUBIC,
                                 fillcolor=(0, 0, 0, 0))
    shadow_rot = shadow.rotate(10, expand=True, resample=Image.BICUBIC,
                                fillcolor=(0, 0, 0, 0))

    bx = showcase_cx - 200 - back_rot.width // 2
    by = showcase_cy - 60 - back_rot.height // 2
    hero.paste(Image.new("RGB", shadow_rot.size, BEIGE_BG),
               (bx + 5, by + 5), shadow_rot)
    hero.paste(back_rot, (bx, by), back_rot)

    # Front card (right, overlapping, slight negative rotation)
    front_card = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    front_draw = ImageDraw.Draw(front_card)
    _draw_card_front(front_draw, 0, 0, card_w, card_h)

    shadow2 = Image.new("RGBA", (card_w + 60, card_h + 60), (0, 0, 0, 0))
    shadow_inner2 = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 90))
    shadow2.paste(shadow_inner2, (38, 38))
    shadow2 = shadow2.filter(ImageFilter.GaussianBlur(20))

    front_rot = front_card.rotate(-5, expand=True, resample=Image.BICUBIC,
                                   fillcolor=(0, 0, 0, 0))
    shadow2_rot = shadow2.rotate(-5, expand=True, resample=Image.BICUBIC,
                                  fillcolor=(0, 0, 0, 0))

    fx = showcase_cx + 100 - front_rot.width // 2
    fy = showcase_cy + 80 - front_rot.height // 2
    hero.paste(Image.new("RGB", shadow2_rot.size, BEIGE_BG),
               (fx + 5, fy + 5), shadow2_rot)
    hero.paste(front_rot, (fx, fy), front_rot)

    # Bottom banner (solid black, bottom 30%)
    draw.rectangle([(0, IMG_H - BAND_H), (IMG_W, IMG_H)], fill=(0, 0, 0))

    # Banner text
    title_font = load_font(FONT_SERIF_BOLD, 96)
    tagline_font = load_font(FONT_SANS_BOLD, 34)

    lines = HERO_TITLE.split("\n")
    banner_cx = IMG_W // 2
    banner_cy = IMG_H - BAND_H // 2

    # Title lines
    line_height = 115
    total_title_h = len(lines) * line_height
    start_y = banner_cy - total_title_h // 2 - 30

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=title_font)
        tw = bbox[2] - bbox[0]
        draw.text((banner_cx - tw // 2, start_y + i * line_height),
                  line, font=title_font, fill=WHITE)

    # Tagline
    bbox = draw.textbbox((0, 0), TAGLINE, font=tagline_font)
    tw = bbox[2] - bbox[0]
    draw.text((banner_cx - tw // 2, start_y + len(lines) * line_height + 20),
              TAGLINE, font=tagline_font, fill=LIGHT_GREY)

    # "EDITABLE PDF" badge (bottom-right of product area)
    badge_r = 110
    badge_cx = IMG_W - 240
    badge_cy = IMG_H - BAND_H - 10
    draw.ellipse([badge_cx - badge_r, badge_cy - badge_r,
                  badge_cx + badge_r, badge_cy + badge_r],
                 fill=ACCENT_ORANGE)

    badge_top_font = load_font(FONT_SANS_BOLD, 28)
    badge_bottom_font = load_font(FONT_SANS_BOLD, 42)
    bbox1 = draw.textbbox((0, 0), "EDITABLE", font=badge_top_font)
    bbox2 = draw.textbbox((0, 0), "PDF", font=badge_bottom_font)
    draw.text((badge_cx - (bbox1[2] - bbox1[0]) // 2, badge_cy - 30),
              "EDITABLE", font=badge_top_font, fill=WHITE)
    draw.text((badge_cx - (bbox2[2] - bbox2[0]) // 2, badge_cy + 5),
              "PDF", font=badge_bottom_font, fill=WHITE)

    path = os.path.join(OUTPUT_DIR, f"{SAFE_TITLE}_page1.png")
    hero.save(path, "PNG")
    hero.close()
    size_kb = os.path.getsize(path) // 1024
    print(f"    Saved: {os.path.basename(path)} ({size_kb}KB)", flush=True)
    return path


# ===========================================================================
# Page 2: "What You Get" infographic
# ===========================================================================

def create_page2(page1_path):
    """Create the 'What You Get' infographic page."""
    print("  Creating Page 2: What You Get...", flush=True)

    page = Image.new("RGB", (IMG_W, IMG_H), DARK_BG)
    draw = ImageDraw.Draw(page)

    cx = IMG_W // 2

    # Heading
    heading_font = load_font(FONT_SANS_BOLD, 86)
    bbox = draw.textbbox((0, 0), "WHAT YOU GET", font=heading_font)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, 120), "WHAT YOU GET", font=heading_font, fill=WHITE)

    # Orange accent line
    draw.rectangle([(cx - 50, 230), (cx + 50, 236)], fill=ACCENT_ORANGE)

    # Preview thumbnail of page 1
    if page1_path and os.path.exists(page1_path):
        thumb = Image.open(page1_path).convert("RGB")
        thumb_w = 900
        thumb_h = int(thumb.height * thumb_w / thumb.width)
        thumb = thumb.resize((thumb_w, thumb_h), Image.LANCZOS)
        px = cx - thumb_w // 2
        py = 290
        # Border
        draw.rectangle([(px - 3, py - 3), (px + thumb_w + 3, py + thumb_h + 3)],
                       fill=(50, 50, 50))
        page.paste(thumb, (px, py))
        thumb.close()
        content_y = py + thumb_h + 60
    else:
        content_y = 350

    # Features (2-column grid)
    features = [
        "Editable Appointment Card",
        "A4 & US Letter Sizes",
        "Instant Digital Download",
        "Print-Ready (300 DPI)",
        "Fillable PDF - No Software Needed",
        "Works in Any PDF Reader",
    ]

    feat_font = load_font(FONT_SANS, 30)
    check_font = load_font(FONT_SANS_BOLD, 24)
    col_w = 750
    col_gap = 80
    col1_x = cx - col_w - col_gap // 2
    col2_x = cx + col_gap // 2

    for i, feat in enumerate(features):
        col_x = col1_x if i % 2 == 0 else col2_x
        fy = content_y + (i // 2) * 70

        # Orange check circle
        circle_r = 24
        circle_x = col_x + circle_r
        circle_y = fy + 12
        draw.ellipse([circle_x - circle_r, circle_y - circle_r,
                      circle_x + circle_r, circle_y + circle_r],
                     fill=ACCENT_ORANGE)
        draw.text((circle_x - 8, circle_y - 14), "\u2713",
                  font=check_font, fill=WHITE)

        draw.text((col_x + 60, fy), feat, font=feat_font, fill=(220, 220, 220))

    # How It Works
    how_y = content_y + (len(features) // 2) * 70 + 80
    how_font = load_font(FONT_SANS_BOLD, 50)
    bbox = draw.textbbox((0, 0), "HOW IT WORKS", font=how_font)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, how_y), "HOW IT WORKS", font=how_font, fill=WHITE)

    steps = [
        "Download the PDF\nfrom your Etsy receipt",
        "Open in any PDF reader\n(Adobe, Preview, etc.)",
        "Click each field and\ntype your details",
    ]

    step_y = how_y + 80
    step_font = load_font(FONT_SANS, 22)
    num_font = load_font(FONT_SANS_BOLD, 28)
    step_spacing = (IMG_W - 300) // len(steps)

    for i, step in enumerate(steps):
        sx = 150 + i * step_spacing + step_spacing // 2

        # Number circle (orange outline)
        circle_r = 32
        draw.ellipse([sx - circle_r, step_y - circle_r,
                      sx + circle_r, step_y + circle_r],
                     outline=ACCENT_ORANGE, width=3)
        num_text = str(i + 1)
        bbox = draw.textbbox((0, 0), num_text, font=num_font)
        nw = bbox[2] - bbox[0]
        draw.text((sx - nw // 2, step_y - 16), num_text,
                  font=num_font, fill=ACCENT_ORANGE)

        # Step text (centered below circle)
        for j, line in enumerate(step.split("\n")):
            bbox = draw.textbbox((0, 0), line, font=step_font)
            lw = bbox[2] - bbox[0]
            draw.text((sx - lw // 2, step_y + 50 + j * 30),
                      line, font=step_font, fill=(170, 170, 170))

    # Pills at bottom
    pills = ["Editable PDF", "A4 + Letter", "Instant Download"]
    pill_font = load_font(FONT_SANS_BOLD, 20)
    pill_y = IMG_H - 200
    total_pill_w = 0
    pill_sizes = []
    for pill in pills:
        bbox = draw.textbbox((0, 0), pill, font=pill_font)
        pw = bbox[2] - bbox[0] + 72
        pill_sizes.append(pw)
        total_pill_w += pw
    pill_gap = 24
    total_pill_w += pill_gap * (len(pills) - 1)
    pill_x = cx - total_pill_w // 2

    for i, pill in enumerate(pills):
        pw = pill_sizes[i]
        ph = 52
        draw.rounded_rectangle([pill_x, pill_y, pill_x + pw, pill_y + ph],
                               radius=26, outline=(68, 68, 68), width=2)
        bbox = draw.textbbox((0, 0), pill, font=pill_font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text((pill_x + (pw - tw) // 2, pill_y + (ph - th) // 2 - 2),
                  pill, font=pill_font, fill=(136, 136, 136))
        pill_x += pw + pill_gap

    path = os.path.join(OUTPUT_DIR, f"{SAFE_TITLE}_page2.png")
    page.save(path, "PNG")
    page.close()
    size_kb = os.path.getsize(path) // 1024
    print(f"    Saved: {os.path.basename(path)} ({size_kb}KB)", flush=True)
    return path


# ===========================================================================
# Page 3: "Please Note" (trust signals)
# ===========================================================================

def create_page3():
    """Create the 'Please Note' trust signals page."""
    print("  Creating Page 3: Please Note...", flush=True)

    page = Image.new("RGB", (IMG_W, IMG_H), (248, 246, 243))
    draw = ImageDraw.Draw(page)
    cx = IMG_W // 2

    # Purple header band
    draw.rectangle([(0, 0), (IMG_W, 500)], fill=BRAND_PURPLE)
    heading_font = load_font(FONT_SANS_BOLD, 80)
    sub_font = load_font(FONT_SANS, 30)
    bbox = draw.textbbox((0, 0), "PLEASE NOTE", font=heading_font)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, 160), "PLEASE NOTE", font=heading_font, fill=WHITE)

    sub = "Important information about your digital download"
    bbox = draw.textbbox((0, 0), sub, font=sub_font)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, 280), sub, font=sub_font, fill=(220, 200, 240))

    # Info cards
    notes = [
        ("DIGITAL PRODUCT", "This is a digital download — no physical\n"
         "product will be shipped. You will receive\n"
         "instant access after purchase."),
        ("EDITABLE PDF", "Open in any PDF reader (Adobe Acrobat,\n"
         "Preview, Chrome). Click the fields to type\n"
         "your details. No extra software needed."),
        ("PRINT AT HOME", "Print on 300gsm card stock for best results.\n"
         "Select 'Actual Size' in your printer settings\n"
         "to ensure correct dimensions."),
        ("COMMERCIAL USE", "Personal and small business use included.\n"
         "You may print unlimited copies for your\n"
         "own studio. Resale of the template is prohibited."),
        ("NEED HELP?", "Contact us through Etsy messages and\n"
         "we'll be happy to assist you. We typically\n"
         "respond within 24 hours."),
    ]

    card_w = 1800
    card_h = 200
    card_x = cx - card_w // 2
    card_start_y = 580
    card_gap = 30

    title_font = load_font(FONT_SANS_BOLD, 32)
    body_font = load_font(FONT_SANS, 26)

    for i, (title, body) in enumerate(notes):
        cy = card_start_y + i * (card_h + card_gap)
        draw.rounded_rectangle([card_x, cy, card_x + card_w, cy + card_h],
                               radius=10, fill=WHITE, outline=(230, 230, 230))
        # Purple left accent
        draw.rectangle([card_x, cy, card_x + 6, cy + card_h], fill=BRAND_PURPLE)

        draw.text((card_x + 30, cy + 20), title,
                  font=title_font, fill=BRAND_PURPLE)
        for j, line in enumerate(body.split("\n")):
            draw.text((card_x + 30, cy + 65 + j * 36), line,
                      font=body_font, fill=(80, 80, 80))

    # Footer
    footer_font = load_font(FONT_SANS, 24)
    footer = "PurpleOcaz — Premium Digital Templates"
    bbox = draw.textbbox((0, 0), footer, font=footer_font)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, IMG_H - 80), footer,
              font=footer_font, fill=MID_GREY)

    path = os.path.join(OUTPUT_DIR, f"{SAFE_TITLE}_page3.png")
    page.save(path, "PNG")
    page.close()
    size_kb = os.path.getsize(path) // 1024
    print(f"    Saved: {os.path.basename(path)} ({size_kb}KB)", flush=True)
    return path


# ===========================================================================
# Page 4: "Usage Ideas"
# ===========================================================================

def create_page4():
    """Create the 'Usage Ideas' page."""
    print("  Creating Page 4: Usage Ideas...", flush=True)

    page = Image.new("RGB", (IMG_W, IMG_H), DARK_BG)
    draw = ImageDraw.Draw(page)
    cx = IMG_W // 2

    # Heading
    heading_font = load_font(FONT_SANS_BOLD, 80)
    bbox = draw.textbbox((0, 0), "ENDLESS POSSIBILITIES", font=heading_font)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, 140), "ENDLESS POSSIBILITIES",
              font=heading_font, fill=WHITE)

    # Orange accent
    draw.rectangle([(cx - 50, 250), (cx + 50, 256)], fill=ACCENT_ORANGE)

    sub_font = load_font(FONT_SANS, 32)
    sub = "Perfect for tattoo studios, parlours & artists"
    bbox = draw.textbbox((0, 0), sub, font=sub_font)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, 290), sub, font=sub_font, fill=LIGHT_GREY)

    # Use-case cards in 2x2 grid
    uses = [
        ("TATTOO STUDIOS", "Keep your appointment book\norganised and professional"),
        ("PIERCING PARLOURS", "Track client bookings with\nstyle and consistency"),
        ("BEAUTY SALONS", "Impress clients with branded\nappointment reminders"),
        ("BARBER SHOPS", "Professional cards that match\nyour shop's aesthetic"),
    ]

    card_w = 900
    card_h = 380
    gap = 60
    grid_w = card_w * 2 + gap
    grid_start_x = cx - grid_w // 2
    grid_start_y = 420

    title_font = load_font(FONT_SANS_BOLD, 36)
    body_font = load_font(FONT_SANS, 28)

    for i, (title, body) in enumerate(uses):
        col = i % 2
        row = i // 2
        card_x = grid_start_x + col * (card_w + gap)
        card_y = grid_start_y + row * (card_h + gap)

        draw.rounded_rectangle([card_x, card_y, card_x + card_w,
                                card_y + card_h], radius=12, fill=DARK_CARD)
        # Orange top accent
        draw.rectangle([card_x, card_y, card_x + card_w, card_y + 5],
                       fill=ACCENT_ORANGE)

        draw.text((card_x + 40, card_y + 50), title,
                  font=title_font, fill=WHITE)
        for j, line in enumerate(body.split("\n")):
            draw.text((card_x + 40, card_y + 120 + j * 42), line,
                      font=body_font, fill=LIGHT_GREY)

    # "Also perfect for" pills
    pill_y = grid_start_y + 2 * (card_h + gap) + 60
    also_font = load_font(FONT_SANS_BOLD, 30)
    bbox = draw.textbbox((0, 0), "ALSO PERFECT FOR", font=also_font)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, pill_y), "ALSO PERFECT FOR",
              font=also_font, fill=ACCENT_GOLD)

    more_uses = ["Spa & Wellness", "Lash Technicians", "Nail Artists",
                 "Hair Stylists", "Makeup Artists", "Dental Clinics"]
    pill_font = load_font(FONT_SANS, 22)
    pill_row_y = pill_y + 70
    pill_sizes = []
    total_pw = 0
    for mu in more_uses:
        bbox = draw.textbbox((0, 0), mu, font=pill_font)
        pw = bbox[2] - bbox[0] + 48
        pill_sizes.append(pw)
        total_pw += pw
    pill_gap = 20
    total_pw += pill_gap * (len(more_uses) - 1)
    px = cx - total_pw // 2

    for i, mu in enumerate(more_uses):
        pw = pill_sizes[i]
        ph = 48
        draw.rounded_rectangle([px, pill_row_y, px + pw, pill_row_y + ph],
                               radius=24, outline=(80, 80, 80), width=2)
        bbox = draw.textbbox((0, 0), mu, font=pill_font)
        tw = bbox[2] - bbox[0]
        draw.text((px + (pw - tw) // 2, pill_row_y + 10), mu,
                  font=pill_font, fill=(140, 140, 140))
        px += pw + pill_gap

    # Footer
    footer_font = load_font(FONT_SANS, 24)
    footer = "PurpleOcaz — Premium Digital Templates"
    bbox = draw.textbbox((0, 0), footer, font=footer_font)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, IMG_H - 80), footer,
              font=footer_font, fill=MID_GREY)

    path = os.path.join(OUTPUT_DIR, f"{SAFE_TITLE}_page4.png")
    page.save(path, "PNG")
    page.close()
    size_kb = os.path.getsize(path) // 1024
    print(f"    Saved: {os.path.basename(path)} ({size_kb}KB)", flush=True)
    return path


# ===========================================================================
# Page 5: "Thank You"
# ===========================================================================

def create_page5():
    """Create the Thank You / small business appreciation page."""
    print("  Creating Page 5: Thank You...", flush=True)

    page = Image.new("RGB", (IMG_W, IMG_H), DARK_BG)
    draw = ImageDraw.Draw(page)
    cx = IMG_W // 2

    # Purple gradient-ish header area
    for y_pos in range(600):
        alpha = 1.0 - (y_pos / 600.0)
        r = int(BRAND_PURPLE[0] * alpha + DARK_BG[0] * (1 - alpha))
        g = int(BRAND_PURPLE[1] * alpha + DARK_BG[1] * (1 - alpha))
        b = int(BRAND_PURPLE[2] * alpha + DARK_BG[2] * (1 - alpha))
        draw.line([(0, y_pos), (IMG_W, y_pos)], fill=(r, g, b))

    # "Thank You" heading
    heading_font = load_font(FONT_SERIF_BOLD_ITALIC, 120)
    bbox = draw.textbbox((0, 0), "Thank You", font=heading_font)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, 180), "Thank You", font=heading_font, fill=WHITE)

    sub_font = load_font(FONT_SANS, 36)
    sub = "for supporting a small business"
    bbox = draw.textbbox((0, 0), sub, font=sub_font)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, 340), sub, font=sub_font, fill=(220, 200, 240))

    # Divider
    draw.rectangle([(cx - 80, 430), (cx + 80, 434)], fill=ACCENT_GOLD)

    # Message
    msg_font = load_font(FONT_SANS, 30)
    messages = [
        "Every purchase helps us continue creating beautiful,",
        "professional templates for small business owners.",
        "",
        "Your support means the world to us.",
        "",
        "If you love your template, we'd be so grateful",
        "if you could leave us a review on Etsy!",
    ]

    msg_y = 500
    for line in messages:
        if line:
            bbox = draw.textbbox((0, 0), line, font=msg_font)
            tw = bbox[2] - bbox[0]
            draw.text((cx - tw // 2, msg_y), line, font=msg_font, fill=LIGHT_GREY)
        msg_y += 50

    # 5-star review prompt
    star_y = msg_y + 60
    star_font = load_font(FONT_SANS_BOLD, 60)
    stars = "\u2605 \u2605 \u2605 \u2605 \u2605"
    bbox = draw.textbbox((0, 0), stars, font=star_font)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, star_y), stars, font=star_font, fill=ACCENT_GOLD)

    review_font = load_font(FONT_SANS_BOLD, 28)
    review = "YOUR REVIEW MEANS EVERYTHING TO US"
    bbox = draw.textbbox((0, 0), review, font=review_font)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, star_y + 90), review,
              font=review_font, fill=ACCENT_ORANGE)

    # Social links box
    box_y = star_y + 200
    box_w = 1400
    box_h = 350
    box_x = cx - box_w // 2
    draw.rounded_rectangle([box_x, box_y, box_x + box_w, box_y + box_h],
                           radius=12, fill=DARK_CARD)
    draw.rectangle([box_x, box_y, box_x + box_w, box_y + 5], fill=BRAND_PURPLE)

    connect_font = load_font(FONT_SANS_BOLD, 36)
    bbox = draw.textbbox((0, 0), "CONNECT WITH US", font=connect_font)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, box_y + 40), "CONNECT WITH US",
              font=connect_font, fill=WHITE)

    links = [
        "Etsy: etsy.com/shop/PurpleOcaz",
        "Instagram: @purpleocaz",
        "Email: hello@purpleocaz.com",
    ]
    link_font = load_font(FONT_SANS, 28)
    for i, link in enumerate(links):
        bbox = draw.textbbox((0, 0), link, font=link_font)
        tw = bbox[2] - bbox[0]
        draw.text((cx - tw // 2, box_y + 110 + i * 55), link,
                  font=link_font, fill=LIGHT_GREY)

    # Brand footer
    brand_font = load_font(FONT_SERIF_BOLD_ITALIC, 50)
    bbox = draw.textbbox((0, 0), "PurpleOcaz", font=brand_font)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, IMG_H - 200), "PurpleOcaz",
              font=brand_font, fill=BRAND_PURPLE)

    footer_font = load_font(FONT_SANS, 22)
    footer = "PREMIUM DIGITAL TEMPLATES"
    bbox = draw.textbbox((0, 0), footer, font=footer_font)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, IMG_H - 130), footer,
              font=footer_font, fill=MID_GREY)

    copy_font = load_font(FONT_SANS, 20)
    copy_text = "\u00a9 2026 PurpleOcaz. All rights reserved."
    bbox = draw.textbbox((0, 0), copy_text, font=copy_font)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, IMG_H - 80), copy_text,
              font=copy_font, fill=(80, 80, 80))

    path = os.path.join(OUTPUT_DIR, f"{SAFE_TITLE}_page5.png")
    page.save(path, "PNG")
    page.close()
    size_kb = os.path.getsize(path) // 1024
    print(f"    Saved: {os.path.basename(path)} ({size_kb}KB)", flush=True)
    return path


# ===========================================================================
# Editable PDF (6-page AcroForm)
# ===========================================================================

def create_editable_pdf():
    """Create the 6-page editable PDF using ReportLab."""
    print("  Creating Editable PDF (6 pages)...", flush=True)

    from reportlab.pdfgen import canvas
    from reportlab.lib.colors import Color

    A4_W, A4_H = 595.27, 841.89
    LETTER_W, LETTER_H = 612.0, 792.0
    CARD_W, CARD_H = 252.0, 144.0

    output_path = os.path.join(OUTPUT_DIR, f"{SAFE_TITLE}_editable.pdf")
    c = canvas.Canvas(output_path)

    # ---- Page 1: Front card (business card size) ----
    c.setPageSize((CARD_W, CARD_H))
    c.setFillColor(Color(1, 1, 1))
    c.rect(0, 0, CARD_W, CARD_H, fill=1, stroke=0)
    c.setStrokeColor(Color(0.85, 0.85, 0.85))
    c.setLineWidth(0.5)
    c.rect(2, 2, CARD_W - 4, CARD_H - 4, fill=0, stroke=1)

    card_cx = CARD_W / 2
    c.setFont("Helvetica-BoldOblique", 14)
    c.setFillColor(Color(0.15, 0.15, 0.15))
    c.drawCentredString(card_cx, CARD_H - 28, "Appointment Card")

    div_y = CARD_H - 38
    c.setStrokeColor(Color(0.4, 0.4, 0.4))
    c.setLineWidth(0.5)
    c.line(card_cx - 40, div_y, card_cx + 40, div_y)

    front_fields = [
        ("name_front", "Name"),
        ("date_front", "Date"),
        ("time_front", "Time"),
        ("day_front", "Day"),
    ]
    field_left = 16
    line_right = CARD_W - 16
    fy = div_y - 22

    for fname, flabel in front_fields:
        label = flabel.upper() + ":"
        c.setFont("Helvetica-Bold", 7)
        c.setFillColor(Color(0.2, 0.2, 0.2))
        c.drawString(field_left, fy + 2, label)
        lw = c.stringWidth(label, "Helvetica-Bold", 7) + 4
        line_start = field_left + lw
        c.setStrokeColor(Color(0.6, 0.6, 0.6))
        c.setLineWidth(0.4)
        c.line(line_start, fy, line_right, fy)

        c.acroForm.textfield(
            name=fname, tooltip=flabel,
            x=line_start, y=fy - 2,
            width=line_right - line_start, height=12,
            borderWidth=0,
            borderColor=Color(1, 1, 1, alpha=0),
            fillColor=Color(1, 1, 1, alpha=0),
            textColor=Color(0.1, 0.1, 0.1),
            fontSize=8, fontName="Helvetica",
        )
        fy -= 20

    # ---- Page 2: Back card ----
    c.showPage()
    c.setPageSize((CARD_W, CARD_H))
    c.setFillColor(Color(1, 1, 1))
    c.rect(0, 0, CARD_W, CARD_H, fill=1, stroke=0)
    c.setStrokeColor(Color(0.85, 0.85, 0.85))
    c.setLineWidth(0.5)
    c.rect(2, 2, CARD_W - 4, CARD_H - 4, fill=0, stroke=1)

    c.setFont("Helvetica-BoldOblique", 14)
    c.setFillColor(Color(0.15, 0.15, 0.15))
    c.drawCentredString(card_cx, CARD_H - 28, "Book Appointment")

    div_y = CARD_H - 38
    c.setStrokeColor(Color(0.4, 0.4, 0.4))
    c.line(card_cx - 40, div_y, card_cx + 40, div_y)

    back_fields = [
        ("email_back", "Email"),
        ("phone_back", "Phone"),
        ("website_back", "Website"),
    ]
    fy = div_y - 22

    for fname, flabel in back_fields:
        label = flabel.upper() + ":"
        c.setFont("Helvetica-Bold", 7)
        c.setFillColor(Color(0.2, 0.2, 0.2))
        c.drawString(field_left, fy + 2, label)
        lw = c.stringWidth(label, "Helvetica-Bold", 7) + 4
        line_start = field_left + lw
        c.setStrokeColor(Color(0.6, 0.6, 0.6))
        c.setLineWidth(0.4)
        c.line(line_start, fy, line_right, fy)

        c.acroForm.textfield(
            name=fname, tooltip=flabel,
            x=line_start, y=fy - 2,
            width=line_right - line_start, height=12,
            borderWidth=0,
            borderColor=Color(1, 1, 1, alpha=0),
            fillColor=Color(1, 1, 1, alpha=0),
            textColor=Color(0.1, 0.1, 0.1),
            fontSize=8, fontName="Helvetica",
        )
        fy -= 20

    # LOGO placeholder
    c.setStrokeColor(Color(0.7, 0.7, 0.7))
    c.circle(CARD_W - 30, CARD_H - 25, 15, stroke=1, fill=0)
    c.setFont("Helvetica", 5)
    c.setFillColor(Color(0.7, 0.7, 0.7))
    c.drawCentredString(CARD_W - 30, CARD_H - 27, "LOGO")

    # ---- Pages 3-6: Print sheets (8 cards per page) ----
    sheets = [
        (LETTER_W, LETTER_H, "US Letter", "FRONT"),
        (A4_W, A4_H, "A4", "FRONT"),
        (LETTER_W, LETTER_H, "US Letter", "BACK"),
        (A4_W, A4_H, "A4", "BACK"),
    ]

    for pw, ph, size_label, side in sheets:
        c.showPage()
        c.setPageSize((pw, ph))
        c.setFillColor(Color(1, 1, 1))
        c.rect(0, 0, pw, ph, fill=1, stroke=0)

        # Title
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(Color(0.1, 0.1, 0.1))
        c.drawCentredString(pw / 2, ph - 35,
                            f"PRINT AT HOME - 8 CARDS PER PAGE ({side} / {size_label})")

        # 2x4 grid of card outlines
        margin_x, margin_top, margin_bottom = 36, 50, 60
        cols, rows = 2, 4
        gap = 8
        usable_w = pw - 2 * margin_x - gap
        usable_h = ph - margin_top - margin_bottom - 3 * gap
        cw = usable_w / cols
        ch = usable_h / rows
        max_ch = cw / 1.6
        if ch > max_ch:
            ch = max_ch

        for row in range(rows):
            for col in range(cols):
                rx = margin_x + col * (cw + gap)
                ry = ph - margin_top - (row + 1) * ch - row * gap
                c.setStrokeColor(Color(0.75, 0.75, 0.75))
                c.setLineWidth(0.5)
                c.rect(rx, ry, cw, ch, fill=0, stroke=1)

                # Tiny text inside each card slot
                c.setFont("Helvetica-BoldOblique", 8)
                c.setFillColor(Color(0.5, 0.5, 0.5))
                card_title = "Appointment Card" if side == "FRONT" else "Book Appointment"
                c.drawCentredString(rx + cw / 2, ry + ch / 2, card_title)

                # Crop marks
                crop = 8
                c.setStrokeColor(Color(0.3, 0.3, 0.3))
                c.setLineWidth(0.25)
                c.line(rx - crop, ry + ch, rx - 2, ry + ch)
                c.line(rx, ry + ch + 2, rx, ry + ch + crop)
                c.line(rx + cw + 2, ry + ch, rx + cw + crop, ry + ch)
                c.line(rx + cw, ry + ch + 2, rx + cw, ry + ch + crop)
                c.line(rx - crop, ry, rx - 2, ry)
                c.line(rx, ry - 2, rx, ry - crop)
                c.line(rx + cw + 2, ry, rx + cw + crop, ry)
                c.line(rx + cw, ry - 2, rx + cw, ry - crop)

        # Footer
        c.setFont("Helvetica", 7)
        c.setFillColor(Color(0.5, 0.5, 0.5))
        c.drawCentredString(pw / 2, 20, "PurpleOcaz — Premium Digital Templates")
        c.drawRightString(pw - 30, 20, size_label)

    c.save()
    size_kb = os.path.getsize(output_path) // 1024
    print(f"    Saved: {os.path.basename(output_path)} ({size_kb}KB, 6 pages)",
          flush=True)
    return output_path


# ===========================================================================
# Affiliate Guide (2-page "Getting Started" PDF)
# ===========================================================================

def create_affiliate_guide():
    """Create the branded Getting Started guide PDF."""
    print("  Creating Affiliate Guide (2 pages)...", flush=True)

    # Use the existing module directly
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "..", "workflows", "auto_listing_creator"))
    try:
        from tools.affiliate_guide_generator import create_affiliate_guide as _gen
        from tools.tier_config import TIER_1

        listing = {"title": TITLE, "product_type": PRODUCT_TYPE}
        result = _gen(listing, PRODUCT_TYPE, TIER_1, OUTPUT_DIR)
        if result["success"]:
            size_kb = os.path.getsize(result["pdf_path"]) // 1024
            print(f"    Saved: {os.path.basename(result['pdf_path'])} "
                  f"({size_kb}KB, 2 pages)", flush=True)
            return result["pdf_path"]
        else:
            print(f"    Guide generation failed: {result['error']}", flush=True)
            return None
    except Exception as e:
        print(f"    Guide generation failed: {e}", flush=True)
        return None


# ===========================================================================
# Main
# ===========================================================================

def main():
    print("=" * 65)
    print("  TIER 1 END-TO-END: Tattoo Appointment Card")
    print("  Product: Editable PDF (Nano Banana tier)")
    print("  Niche: Tattoo")
    print("=" * 65)
    print()

    outputs = {}

    # Page 1: Hero mockup
    page1 = create_page1()
    outputs["page1"] = page1

    # Page 2: What You Get
    page2 = create_page2(page1)
    outputs["page2"] = page2

    # Page 3: Please Note
    page3 = create_page3()
    outputs["page3"] = page3

    # Page 4: Usage Ideas
    page4 = create_page4()
    outputs["page4"] = page4

    # Page 5: Thank You
    page5 = create_page5()
    outputs["page5"] = page5

    # Editable PDF
    pdf = create_editable_pdf()
    outputs["editable_pdf"] = pdf

    # Affiliate guide
    guide = create_affiliate_guide()
    outputs["affiliate_guide"] = guide

    # Summary
    print()
    print("=" * 65)
    print("  COMPLETE DIGITAL PRODUCT PACKAGE")
    print("=" * 65)
    print()
    print("  Listing Images (for Etsy upload):")
    for i in range(1, 6):
        key = f"page{i}"
        if outputs.get(key):
            size = os.path.getsize(outputs[key]) // 1024
            print(f"    Page {i}: {os.path.basename(outputs[key])} ({size}KB)")

    print()
    print("  Buyer Deliverables (digital download):")
    if outputs.get("editable_pdf"):
        size = os.path.getsize(outputs["editable_pdf"]) // 1024
        print(f"    Editable PDF: {os.path.basename(outputs['editable_pdf'])} ({size}KB)")
    if outputs.get("affiliate_guide"):
        size = os.path.getsize(outputs["affiliate_guide"]) // 1024
        print(f"    Guide PDF: {os.path.basename(outputs['affiliate_guide'])} ({size}KB)")

    print()
    print(f"  Output directory: {OUTPUT_DIR}")
    print()
    print("  NOTE: Hero image uses Pillow rendering (local demo).")
    print("  In production, Tier 1 uses Gemini 2.5 Flash AI for")
    print("  photorealistic flat-lay mockups with real textures.")
    print()

    return outputs


if __name__ == "__main__":
    main()
