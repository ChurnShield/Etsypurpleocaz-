#!/usr/bin/env python3
"""
Render the torn-paper appointment card from design spec → PNG.

Generates both the card template and a hero image preview.
Output goes to: workflows/auto_listing_creator/exports/

Usage:
    python scripts/render_appointment_card.py
"""

import os
import sys
import math
import random
import json

from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ── Paths ────────────────────────────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
EXPORT_DIR = os.path.join(_ROOT, "workflows", "auto_listing_creator", "exports")
SPEC_PATH = os.path.join(
    _ROOT, "workflows", "auto_listing_creator", "design_specs",
    "book_appointment_card.json",
)

# ── Fonts ────────────────────────────────────────────────────────────────
FONT_SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
FONT_SERIF_IT = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
FONT_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SANS_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# ── Card dimensions ──────────────────────────────────────────────────────
CARD_W = 2000
CARD_H = 950

# ── Hero dimensions (Etsy listing) ───────────────────────────────────────
HERO_W = 2250
HERO_H = 3000
BAND_H = 750


def _font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except (OSError, IOError):
        return ImageFont.load_default()


def _text_centered(draw, text, y, font, fill, width):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (width - tw) // 2
    draw.text((x, y), text, fill=fill, font=font)
    return bbox[3] - bbox[1]


def _text_right(draw, text, y, font, fill, right_x):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = right_x - tw
    draw.text((x, y), text, fill=fill, font=font)


def _generate_torn_edge(h, base_x_start, base_x_end, amplitude=40, freq=12):
    """Generate a jagged torn paper edge path.

    Returns a list of (x, y) points along the tear from top to bottom.
    """
    points = []
    for y in range(h):
        frac = y / h
        # Linear interpolation of base x position
        base_x = base_x_start + (base_x_end - base_x_start) * frac
        # Multiple frequencies of jaggedness for realism
        jag1 = amplitude * math.sin(y / freq * 1.7 + 0.3)
        jag2 = (amplitude * 0.5) * math.sin(y / (freq * 0.4) + 1.2)
        jag3 = (amplitude * 0.25) * math.sin(y / (freq * 0.15) + 2.8)
        # Random micro-jitter
        micro = random.uniform(-3, 3)
        x = int(base_x + jag1 + jag2 + jag3 + micro)
        points.append((x, y))
    return points


def _draw_paper_fibers(draw, torn_points, count=60):
    """Draw white paper fiber threads along the torn edge."""
    for _ in range(count):
        idx = random.randint(5, len(torn_points) - 5)
        tx, ty = torn_points[idx]
        # Fiber extends from the tear outward
        side = random.choice([-1, 1])
        fiber_len = random.randint(4, 18)
        fiber_x = tx + side * fiber_len
        alpha = random.randint(80, 200)
        draw.line([(tx, ty), (fiber_x, ty + random.randint(-2, 2))],
                  fill=(255, 255, 255, alpha), width=1)


def render_back_card():
    """Render the back side of the appointment card (Book Appointment side)."""
    img = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # ── Torn paper edge ──
    # Tear runs diagonally: ~25% from left at top, ~35% from left at bottom
    tear_x_top = int(CARD_W * 0.20)
    tear_x_bot = int(CARD_W * 0.35)
    torn_points = _generate_torn_edge(CARD_H, tear_x_top, tear_x_bot,
                                      amplitude=35, freq=14)

    # Fill the left side with white (the revealed paper)
    for y in range(CARD_H):
        tx = torn_points[y][0]
        if tx > 0:
            draw.line([(0, y), (tx, y)], fill=(255, 255, 255, 255))

    # ── Paper fibers along the tear ──
    fiber_layer = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 0))
    fiber_draw = ImageDraw.Draw(fiber_layer)
    _draw_paper_fibers(fiber_draw, torn_points, count=80)
    img = Image.alpha_composite(img, fiber_layer)
    draw = ImageDraw.Draw(img)

    # ── Subtle shadow on the tear edge (black side casts shadow on white) ──
    shadow_layer = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_layer)
    for y in range(CARD_H):
        tx = torn_points[y][0]
        # Shadow extends a few pixels left of the tear line
        for dx in range(1, 12):
            sx = tx - dx
            if 0 <= sx < CARD_W:
                a = int(50 * (1 - dx / 12))
                shadow_draw.point((sx, y), fill=(0, 0, 0, a))
    img = Image.alpha_composite(img, shadow_layer)
    draw = ImageDraw.Draw(img)

    # ── Add subtle paper texture to white area ──
    for _ in range(30):
        y1 = random.randint(0, CARD_H - 1)
        x1 = random.randint(0, tear_x_top)
        length = random.randint(30, 150)
        for i in range(length):
            px = x1 + i
            py = y1 + random.randint(-1, 1)
            if 0 <= px < CARD_W and 0 <= py < CARD_H:
                # Only draw on white area
                if px < torn_points[min(py, CARD_H - 1)][0]:
                    draw.point((px, py), fill=(230, 228, 224, 30))

    # ── Content area (right side, on black) ──
    # Calculate content center (midpoint of black area)
    content_left = int(CARD_W * 0.40)
    content_cx = (content_left + CARD_W) // 2

    # ── Logo placeholder (top-right) ──
    logo_cx = int(CARD_W * 0.82)
    logo_cy = int(CARD_H * 0.22)
    logo_r = 55

    # Circle border
    draw.ellipse([(logo_cx - logo_r, logo_cy - logo_r),
                  (logo_cx + logo_r, logo_cy + logo_r)],
                 outline=(255, 255, 255), width=2)

    # Camera icon (simplified)
    cam_w, cam_h = 30, 22
    cam_x = logo_cx - cam_w // 2
    cam_y = logo_cy - cam_h // 2 + 5
    draw.rounded_rectangle(
        [(cam_x, cam_y), (cam_x + cam_w, cam_y + cam_h)],
        radius=4, outline=(255, 255, 255), width=2,
    )
    # Lens
    lens_r = 7
    draw.ellipse([(logo_cx - lens_r, cam_y + cam_h // 2 - lens_r),
                  (logo_cx + lens_r, cam_y + cam_h // 2 + lens_r)],
                 outline=(255, 255, 255), width=2)
    # Flash bump
    draw.rectangle([(logo_cx - 5, cam_y - 4), (logo_cx + 5, cam_y)],
                   fill=(255, 255, 255))

    # "YOUR LOGO HERE" curved text (simplified as straight text above circle)
    f_logo = _font(FONT_SANS, 11)
    _text_centered(draw, "YOUR  LOGO  HERE", logo_cy - logo_r - 18,
                   f_logo, (255, 255, 255), CARD_W)

    # ── "Book Appointment" heading ──
    f_heading = _font(FONT_SERIF_IT, 68)
    heading_y = int(CARD_H * 0.40)
    bbox = draw.textbbox((0, 0), "Book Appointment", font=f_heading)
    tw = bbox[2] - bbox[0]
    heading_x = content_cx - tw // 2
    draw.text((heading_x, heading_y), "Book Appointment",
              fill=(255, 255, 255), font=f_heading)

    # ── Contact details ──
    f_contact = _font(FONT_SANS_REG, 22)
    f_website = _font(FONT_SANS, 24)

    contacts = [
        ("name@yourbusiness.com", f_contact, int(CARD_H * 0.62)),
        ("555-5555-5555", f_contact, int(CARD_H * 0.72)),
        ("WWW.YOURBUSINESS.COM", f_website, int(CARD_H * 0.83)),
    ]
    for text, font, y in contacts:
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        x = content_cx - tw // 2
        draw.text((x, y), text, fill=(255, 255, 255), font=font)

    return img


def render_front_card():
    """Render the front side of the appointment card (fields side)."""
    img = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # ── Torn paper edge (mirrored — tear on right side) ──
    tear_x_top = int(CARD_W * 0.75)
    tear_x_bot = int(CARD_W * 0.65)
    torn_points = _generate_torn_edge(CARD_H, tear_x_top, tear_x_bot,
                                      amplitude=35, freq=14)

    # Fill the right side with white
    for y in range(CARD_H):
        tx = torn_points[y][0]
        if tx < CARD_W:
            draw.line([(tx, y), (CARD_W - 1, y)], fill=(255, 255, 255, 255))

    # Paper fibers
    fiber_layer = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 0))
    fiber_draw = ImageDraw.Draw(fiber_layer)
    _draw_paper_fibers(fiber_draw, torn_points, count=80)
    img = Image.alpha_composite(img, fiber_layer)
    draw = ImageDraw.Draw(img)

    # Shadow on tear edge
    shadow_layer = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_layer)
    for y in range(CARD_H):
        tx = torn_points[y][0]
        for dx in range(1, 12):
            sx = tx + dx
            if 0 <= sx < CARD_W:
                a = int(50 * (1 - dx / 12))
                shadow_draw.point((sx, y), fill=(0, 0, 0, a))
    img = Image.alpha_composite(img, shadow_layer)
    draw = ImageDraw.Draw(img)

    # ── Content (left side, on black) ──
    content_right = int(CARD_W * 0.60)
    content_cx = content_right // 2

    # ── "Appointment Card" heading ──
    f_heading = _font(FONT_SERIF_IT, 62)
    heading_y = int(CARD_H * 0.10)
    bbox = draw.textbbox((0, 0), "Appointment Card", font=f_heading)
    tw = bbox[2] - bbox[0]
    heading_x = content_cx - tw // 2
    draw.text((heading_x, heading_y), "Appointment Card",
              fill=(255, 255, 255), font=f_heading)

    # ── Thin ornamental divider ──
    div_y = heading_y + 80
    div_half = 120
    draw.line([(content_cx - div_half, div_y), (content_cx - 8, div_y)],
              fill=(255, 255, 255, 80), width=1)
    draw.line([(content_cx + 8, div_y), (content_cx + div_half, div_y)],
              fill=(255, 255, 255, 80), width=1)
    # Small diamond center
    ds = 4
    draw.polygon([(content_cx, div_y - ds), (content_cx + ds, div_y),
                  (content_cx, div_y + ds), (content_cx - ds, div_y)],
                 fill=(255, 255, 255, 120))

    # ── Form fields ──
    f_label = _font(FONT_SANS, 20)
    fields = ["NAME", "DATE", "TIME", "DAY"]
    field_start_y = div_y + 40
    field_spacing = 65
    field_left = content_cx - 200
    field_line_right = content_cx + 200  # All lines end at same right edge

    for i, label in enumerate(fields):
        fy = field_start_y + i * field_spacing
        draw.text((field_left, fy), f"{label}:", fill=(255, 255, 255), font=f_label)
        # Measure label width to start line after it
        label_bbox = draw.textbbox((0, 0), f"{label}:", font=f_label)
        label_w = label_bbox[2] - label_bbox[0]
        line_start = field_left + label_w + 15
        line_y = fy + 28
        draw.line([(line_start, line_y), (field_line_right, line_y)],
                  fill=(255, 255, 255, 100), width=1)

    # ── Paper texture on white area ──
    for _ in range(20):
        y1 = random.randint(0, CARD_H - 1)
        x1 = random.randint(content_right, CARD_W)
        length = random.randint(20, 100)
        for j in range(length):
            px = x1 + j
            py = y1 + random.randint(-1, 1)
            if 0 <= px < CARD_W and 0 <= py < CARD_H:
                if px > torn_points[min(py, CARD_H - 1)][0]:
                    draw.point((px, py), fill=(230, 228, 224, 30))

    return img


def render_hero(front_card, back_card):
    """Compose both cards into a hero image with beige background."""
    # ── Beige background ──
    hero = Image.new("RGBA", (HERO_W, HERO_H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(hero)
    for y in range(HERO_H):
        frac = y / HERO_H
        r = int(218 + 10 * math.sin(frac * math.pi * 1.5))
        g = int(210 + 8 * math.sin(frac * math.pi * 1.5))
        b = int(194 + 6 * math.sin(frac * math.pi * 1.5))
        draw.line([(0, y), (HERO_W, y)], fill=(r, g, b, 255))

    showcase_h = HERO_H - BAND_H
    cx = HERO_W // 2
    cy = showcase_h // 2

    # ── Scale cards ──
    card_scale = 0.80
    scaled_w = int(CARD_W * card_scale)
    scaled_h = int(CARD_H * card_scale)

    # ── Back card (behind, rotated, offset) ──
    back_scaled = back_card.resize((scaled_w, scaled_h), Image.LANCZOS)
    # Add shadow
    shadow_pad = 60
    back_shadow = Image.new("RGBA",
                            (scaled_w + shadow_pad * 2, scaled_h + shadow_pad * 2),
                            (0, 0, 0, 0))
    bs_draw = ImageDraw.Draw(back_shadow)
    bs_draw.rectangle([shadow_pad + 10, shadow_pad + 15,
                       shadow_pad + scaled_w + 10, shadow_pad + scaled_h + 15],
                      fill=(0, 0, 0, 70))
    back_shadow = back_shadow.filter(ImageFilter.GaussianBlur(22))
    back_shadow.paste(back_scaled, (shadow_pad, shadow_pad), back_scaled)

    back_rot = back_shadow.rotate(8, expand=True, resample=Image.BICUBIC,
                                  fillcolor=(0, 0, 0, 0))
    bx = cx - back_rot.width // 2 + 40
    by = cy - back_rot.height // 2 - 60
    hero.paste(back_rot, (bx, by), back_rot)

    # ── Front card (on top, slight rotation) ──
    front_scaled = front_card.resize((scaled_w, scaled_h), Image.LANCZOS)
    front_shadow = Image.new("RGBA",
                             (scaled_w + shadow_pad * 2, scaled_h + shadow_pad * 2),
                             (0, 0, 0, 0))
    fs_draw = ImageDraw.Draw(front_shadow)
    fs_draw.rectangle([shadow_pad + 12, shadow_pad + 18,
                       shadow_pad + scaled_w + 12, shadow_pad + scaled_h + 18],
                      fill=(0, 0, 0, 80))
    front_shadow = front_shadow.filter(ImageFilter.GaussianBlur(26))
    front_shadow.paste(front_scaled, (shadow_pad, shadow_pad), front_scaled)

    front_rot = front_shadow.rotate(-2, expand=True, resample=Image.BICUBIC,
                                    fillcolor=(0, 0, 0, 0))
    fx = cx - front_rot.width // 2 - 20
    fy = cy - front_rot.height // 2 + 50
    hero.paste(front_rot, (fx, fy), front_rot)

    # ── Bottom band ──
    band = Image.new("RGBA", (HERO_W, BAND_H), (0, 0, 0, 255))
    band_draw = ImageDraw.Draw(band)

    # Title
    f_title = _font(FONT_SERIF, 76)
    _text_centered(band_draw, "Tattoo Appointment Card", 60, f_title,
                   (255, 255, 255), HERO_W)

    # Tagline
    f_tag = _font(FONT_SANS, 22)
    _text_centered(band_draw, "EDITABLE CANVA TEMPLATE  |  INSTANT DOWNLOAD",
                   160, f_tag, (201, 168, 76, 200), HERO_W)

    # Gold accent line
    band_draw.line([(int(HERO_W * 0.15), 0), (int(HERO_W * 0.85), 0)],
                   fill=(201, 168, 76, 100), width=2)

    hero.paste(band, (0, HERO_H - BAND_H), band)

    # ── "Edit in Canva" badge ──
    badge_size = 180
    badge = Image.new("RGBA", (badge_size, badge_size), (0, 0, 0, 0))
    b_draw = ImageDraw.Draw(badge)
    b_draw.ellipse([(6, 8), (badge_size - 4, badge_size + 2)],
                   fill=(0, 0, 0, 80))
    badge = badge.filter(ImageFilter.GaussianBlur(6))
    b_draw = ImageDraw.Draw(badge)
    b_draw.ellipse([(5, 5), (badge_size - 5, badge_size - 5)],
                   fill=(230, 126, 34))
    f_badge_top = _font(FONT_SANS_REG, 20)
    f_badge_bot = _font(FONT_SANS, 32)
    _text_centered(b_draw, "EDIT IN", badge_size // 2 - 20,
                   f_badge_top, (255, 255, 255), badge_size)
    _text_centered(b_draw, "CANVA", badge_size // 2 + 8,
                   f_badge_bot, (255, 255, 255), badge_size)
    hero.paste(badge, (HERO_W - badge_size - 80,
                       HERO_H - BAND_H - badge_size // 2), badge)

    return hero


def main():
    os.makedirs(EXPORT_DIR, exist_ok=True)
    random.seed(42)  # Deterministic output for consistency

    print("Rendering torn-paper appointment card...", flush=True)

    # ── Render both card sides ──
    back_card = render_back_card()
    front_card = render_front_card()

    # ── Save individual cards ──
    back_path = os.path.join(EXPORT_DIR, "appointment_card_back.png")
    front_path = os.path.join(EXPORT_DIR, "appointment_card_front.png")
    back_card.convert("RGB").save(back_path, "PNG")
    front_card.convert("RGB").save(front_path, "PNG")
    print(f"  Back card:  {back_path}")
    print(f"  Front card: {front_path}")

    # ── Render hero image ──
    hero = render_hero(front_card, back_card)
    hero_path = os.path.join(EXPORT_DIR, "appointment_card_hero.png")
    hero.convert("RGB").save(hero_path, "PNG")
    print(f"  Hero image: {hero_path}")

    print("\nDone! View these files to see the design.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
