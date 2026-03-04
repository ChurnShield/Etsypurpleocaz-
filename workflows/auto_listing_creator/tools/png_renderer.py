# =============================================================================
# workflows/auto_listing_creator/tools/png_renderer.py
#
# Pure Pillow (PIL) image generation — no HTML, no browser.
# Produces high-quality PNG images for Etsy listing pages.
# =============================================================================

import os
import math
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance

from tools.design_constants import (
    EXPORT_DIR, IMG_W, IMG_H, BAND_H, TMPL_W, TMPL_H,
)

# ── Fonts ──────────────────────────────────────────────────────────────────
FONT_SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
FONT_SERIF_REG = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
FONT_SERIF_IT = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
FONT_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SANS_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# ── Colors ─────────────────────────────────────────────────────────────────
IVORY = (250, 246, 239)
IVORY_DARK = (232, 223, 208)
GOLD = (201, 168, 76)
GOLD_LIGHT = (228, 208, 150)
GOLD_DIM = (160, 134, 60)
DARK = (26, 26, 26)
DARK_BG = (12, 10, 16)
DARK_CARD = (30, 28, 36)
ORANGE = (230, 126, 34)
WHITE = (255, 255, 255)
WARM_GREY = (154, 144, 128)
RED_SEAL = (180, 30, 50)
RED_SEAL_DARK = (100, 10, 20)


def _font(path, size):
    """Load a TrueType font, falling back to default."""
    try:
        return ImageFont.truetype(path, size)
    except (OSError, IOError):
        return ImageFont.load_default()


def _draw_text_centered(draw, text, y, font, fill, width):
    """Draw text centered horizontally at the given y position."""
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (width - tw) // 2
    draw.text((x, y), text, fill=fill, font=font)
    return bbox[3] - bbox[1]


def _draw_gold_line(draw, y, cx, half_w, fill=None):
    """Draw a centered horizontal gold gradient line."""
    color = fill or (*GOLD, 120)
    for i in range(half_w):
        alpha = int(120 * (1 - i / half_w))
        c = (*GOLD[:3], alpha) if fill is None else fill
        draw.point((cx - i, y), fill=c)
        draw.point((cx + i, y), fill=c)


def _add_noise(img, intensity=8):
    """Add subtle noise texture to an image for depth."""
    w, h = img.size
    noise = Image.new("L", (w // 4, h // 4))
    noise_data = [random.randint(0, intensity) for _ in range((w // 4) * (h // 4))]
    noise.putdata(noise_data)
    noise = noise.resize((w, h), Image.BILINEAR)
    noise_rgba = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    noise_rgba.putalpha(noise)
    return Image.alpha_composite(img, noise_rgba)


# ═══════════════════════════════════════════════════════════════════════════
#   GIFT CERTIFICATE TEMPLATE
# ═══════════════════════════════════════════════════════════════════════════

def render_gift_certificate_png():
    """Render a premium gift certificate as a pure PNG.

    Ivory/cream card with dark borders, gold accents, decorative corners,
    dark title banner with white text, and professional typography.
    """
    W, H = TMPL_W, TMPL_H
    img = Image.new("RGBA", (W, H), DARK_BG + (255,))
    card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)

    # Card dimensions (with margin)
    margin = 15
    cw, ch = W - margin * 2, H - margin * 2
    cx, cy = W // 2, H // 2

    # ── Ivory card background with gradient ──
    for y in range(margin, margin + ch):
        frac = (y - margin) / ch
        r = int(IVORY[0] - 12 * frac)
        g = int(IVORY[1] - 15 * frac)
        b = int(IVORY[2] - 18 * frac)
        draw.line([(margin, y), (margin + cw - 1, y)], fill=(r, g, b, 255))

    # ── Dark outer border ──
    border_w = 3
    draw.rectangle(
        [margin, margin, margin + cw - 1, margin + ch - 1],
        outline=DARK, width=border_w,
    )

    # ── Gold inner border ──
    inset = 14
    draw.rectangle(
        [margin + inset, margin + inset,
         margin + cw - inset - 1, margin + ch - inset - 1],
        outline=GOLD, width=2,
    )

    # ── Corner L-brackets (dark) ──
    bracket_len = 60
    bw = 3
    corners = [
        (margin + 4, margin + 4, 1, 1),      # top-left
        (margin + cw - 5, margin + 4, -1, 1),  # top-right
        (margin + 4, margin + ch - 5, 1, -1),  # bottom-left
        (margin + cw - 5, margin + ch - 5, -1, -1),  # bottom-right
    ]
    for bx, by, dx, dy in corners:
        # Horizontal arm
        x1 = bx
        x2 = bx + bracket_len * dx
        draw.line([(min(x1, x2), by), (max(x1, x2), by)], fill=DARK, width=bw)
        # Vertical arm
        y1 = by
        y2 = by + bracket_len * dy
        draw.line([(bx, min(y1, y2)), (bx, max(y1, y2))], fill=DARK, width=bw)

    # ── Gold inner corner accents ──
    gold_len = 40
    gi = inset + 6
    for bx, by, dx, dy in [
        (margin + gi, margin + gi, 1, 1),
        (margin + cw - gi, margin + gi, -1, 1),
        (margin + gi, margin + ch - gi, 1, -1),
        (margin + cw - gi, margin + ch - gi, -1, -1),
    ]:
        x2 = bx + gold_len * dx
        draw.line([(min(bx, x2), by), (max(bx, x2), by)], fill=GOLD, width=1)
        y2 = by + gold_len * dy
        draw.line([(bx, min(by, y2)), (bx, max(by, y2))], fill=GOLD, width=1)

    # ── Corner diamonds ──
    diamond_size = 6
    for dx, dy in [(margin + 6, margin + 6), (margin + cw - 7, margin + 6),
                   (margin + 6, margin + ch - 7), (margin + cw - 7, margin + ch - 7)]:
        draw.polygon([
            (dx, dy - diamond_size), (dx + diamond_size, dy),
            (dx, dy + diamond_size), (dx - diamond_size, dy),
        ], fill=GOLD)

    # ── Dark title banner ──
    banner_h = 150
    banner_top = cy - 70
    # Semi-transparent dark banner
    banner = Image.new("RGBA", (cw - inset * 2 - 40, banner_h), (0, 0, 0, 0))
    banner_draw = ImageDraw.Draw(banner)
    for y in range(banner_h):
        alpha = 230 if 5 < y < banner_h - 5 else 200
        banner_draw.line([(0, y), (banner.width - 1, y)],
                         fill=(18, 16, 24, alpha))
    # Gold top/bottom lines on banner
    banner_draw.line([(0, 0), (banner.width - 1, 0)], fill=GOLD + (180,), width=1)
    banner_draw.line([(0, banner_h - 1), (banner.width - 1, banner_h - 1)],
                     fill=GOLD + (180,), width=1)
    card.paste(banner, (margin + inset + 20, banner_top), banner)

    # ── Top flourish (gold line — diamond — gold line) ──
    fl_y = banner_top - 30
    line_len = 100
    draw.line([(cx - line_len - 10, fl_y), (cx - 10, fl_y)],
              fill=GOLD + (160,), width=1)
    draw.line([(cx + 10, fl_y), (cx + line_len + 10, fl_y)],
              fill=GOLD + (160,), width=1)
    # Center diamond
    ds = 5
    draw.polygon([(cx, fl_y - ds), (cx + ds, fl_y),
                  (cx, fl_y + ds), (cx - ds, fl_y)], fill=GOLD)

    # ── Business name ──
    f_biz = _font(FONT_SANS, 18)
    biz_text = "YOUR  STUDIO  NAME"
    _draw_text_centered(draw, biz_text, banner_top + 18, f_biz, GOLD, W)

    # ── Main title ──
    f_title = _font(FONT_SERIF, 76)
    _draw_text_centered(draw, "Gift Certificate", banner_top + 45, f_title, WHITE, W)

    # ── Subtitle ──
    f_sub = _font(FONT_SANS_REG, 15)
    _draw_text_centered(draw, "TATTOO  &  BODY  ART", banner_top + 125, f_sub,
                        (160, 160, 160, 255), W)

    # ── Amount display ──
    f_amount = _font(FONT_SERIF, 48)
    _draw_text_centered(draw, "$100", banner_top + banner_h + 25, f_amount,
                        GOLD_DIM + (100,), W)

    # ── Bottom flourish ──
    fl2_y = banner_top + banner_h + 15
    draw.line([(cx - 60, fl2_y), (cx - 8, fl2_y)], fill=GOLD + (100,), width=1)
    draw.line([(cx + 8, fl2_y), (cx + 60, fl2_y)], fill=GOLD + (100,), width=1)
    draw.ellipse([(cx - 3, fl2_y - 3), (cx + 3, fl2_y + 3)], fill=GOLD + (120,))

    # ── Form fields ──
    f_label = _font(FONT_SANS, 12)
    fields = [("RECIPIENT", -280, -1), ("AMOUNT", 280, -1),
              ("FROM", -280, 1), ("VALID  UNTIL", 280, 1)]
    field_base_y = banner_top + banner_h + 90
    for label, x_off, row in fields:
        fy = field_base_y + (row + 1) * 30
        fx = cx + x_off - 150
        draw.text((fx, fy), label, fill=(60, 54, 46, 140), font=f_label)
        draw.line([(fx, fy + 20), (fx + 300, fy + 20)],
                  fill=(60, 54, 46, 60), width=1)

    # ── Fine print ──
    f_fine = _font(FONT_SERIF_IT, 12)
    fine_text = "This voucher is non-refundable and cannot be exchanged for cash"
    _draw_text_centered(draw, fine_text, H - margin - 30, f_fine,
                        WARM_GREY + (180,), W)

    # Composite card onto dark background
    img = Image.alpha_composite(img, card)

    # Add subtle noise texture
    img = _add_noise(img, 5)

    # Save
    os.makedirs(EXPORT_DIR, exist_ok=True)
    path = os.path.join(EXPORT_DIR, "_template_gift_certificate.png")
    img.convert("RGB").save(path, "PNG")
    return path


# ═══════════════════════════════════════════════════════════════════════════
#   HERO IMAGE (PAGE 1) — Styled flat-lay scene
# ═══════════════════════════════════════════════════════════════════════════

def _marble_background(w, h):
    """Create a warm beige/cream craft paper surface (PurpleOcaz brand style)."""
    bg = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    draw = ImageDraw.Draw(bg)

    # Base: warm beige/cream gradient (matching top Etsy sellers)
    for y in range(h):
        frac = y / h
        r = int(215 + 12 * math.sin(frac * math.pi * 1.5))
        g = int(205 + 10 * math.sin(frac * math.pi * 1.5))
        b = int(188 + 8 * math.sin(frac * math.pi * 1.5))
        draw.line([(0, y), (w, y)], fill=(r, g, b, 255))

    # Subtle kraft paper texture — horizontal fiber streaks
    for _ in range(40):
        y1 = random.randint(0, h)
        x1 = random.randint(0, w)
        length = random.randint(200, 800)
        for i in range(length):
            px = x1 + i
            py = y1 + random.randint(-1, 1)
            if 0 <= px < w and 0 <= py < h:
                a = random.randint(2, 8)
                draw.point((px, py), fill=(180, 170, 152, a))

    # Diagonal creases (subtle fold lines)
    for _ in range(3):
        x1 = random.randint(0, w)
        y1 = random.randint(0, h)
        angle = random.uniform(0.5, 1.2)
        length = random.randint(600, 1500)
        for i in range(length):
            px = int(x1 + i * math.cos(angle))
            py = int(y1 + i * math.sin(angle))
            if 0 <= px < w and 0 <= py < h:
                draw.point((px, py), fill=(190, 180, 162, 6))

    # Warm ambient glow from top-left (simulates daylight)
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    for r_val in range(600, 0, -6):
        alpha = int(3 * (r_val / 600))
        if alpha > 0:
            glow_draw.ellipse(
                [-r_val, -r_val, r_val * 2, r_val * 2],
                fill=(255, 245, 220, alpha),
            )
    bg = Image.alpha_composite(bg, glow)

    # Fine noise for paper grain
    bg = _add_noise(bg, 4)

    return bg


def _window_light_overlay(w, h):
    """Create diagonal window light bars (soft daylight through blinds)."""
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Diagonal light bands — warm soft daylight
    bands = [
        (0.15, 0.30, 10),   # band 1 (wide, bright)
        (0.42, 0.52, 7),    # band 2
        (0.64, 0.72, 5),    # band 3
        (0.82, 0.88, 3),    # band 4 (faint)
    ]
    angle = math.radians(55)
    for start_f, end_f, alpha in bands:
        for y in range(h):
            x_offset = int(y / math.tan(angle))
            x1 = int(start_f * w) + x_offset
            x2 = int(end_f * w) + x_offset
            x1 = max(0, min(w, x1))
            x2 = max(0, min(w, x2))
            if x1 < x2:
                # Feathered edges for softer light
                mid = (x1 + x2) // 2
                for x in range(x1, x2):
                    dist = abs(x - mid) / max(1, (x2 - x1) // 2)
                    a = int(alpha * (1 - dist * 0.6))
                    if a > 0:
                        draw.point((x, y), fill=(255, 248, 230, a))

    return overlay


def _draw_wax_seal(size=80):
    """Create a red wax seal prop."""
    seal = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(seal)
    cx, cy = size // 2, size // 2
    r = size // 2 - 4

    # Outer edge with slight irregularity
    for angle_deg in range(360):
        angle = math.radians(angle_deg)
        wobble = random.uniform(0.95, 1.05)
        pr = int(r * wobble)
        px = int(cx + pr * math.cos(angle))
        py = int(cy + pr * math.sin(angle))
        draw.ellipse([(px - 2, py - 2), (px + 2, py + 2)], fill=RED_SEAL)

    # Fill center
    draw.ellipse([(cx - r + 2, cy - r + 2), (cx + r - 2, cy + r - 2)], fill=RED_SEAL)

    # Highlight (top-left)
    highlight = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    h_draw = ImageDraw.Draw(highlight)
    h_draw.ellipse([(cx - r // 2, cy - r // 2 - 5),
                    (cx, cy - 5)], fill=(255, 180, 180, 30))
    seal = Image.alpha_composite(seal, highlight)

    # Inner ring
    draw = ImageDraw.Draw(seal)
    inner_r = r - 15
    draw.ellipse([(cx - inner_r, cy - inner_r),
                  (cx + inner_r, cy + inner_r)],
                 outline=(255, 200, 200, 40), width=1)

    # Shadow
    shadow = Image.new("RGBA", (size + 20, size + 20), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow)
    s_draw.ellipse([(6, 8), (size + 14, size + 16)], fill=(0, 0, 0, 80))
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))
    shadow.paste(seal, (10, 10), seal)
    return shadow


def _draw_pen(w=300, h=16):
    """Create a decorative pen prop."""
    pen = Image.new("RGBA", (w + 30, h + 10), (0, 0, 0, 0))
    draw = ImageDraw.Draw(pen)

    y_mid = h // 2 + 5

    # Barrel
    draw.rounded_rectangle(
        [(5, y_mid - h // 2), (w - 40, y_mid + h // 2)],
        radius=h // 2,
        fill=(50, 44, 38),
    )

    # Gold band
    draw.rectangle([(w - 80, y_mid - h // 2), (w - 40, y_mid + h // 2)],
                   fill=GOLD)

    # Nib
    draw.polygon([
        (w - 40, y_mid - 3),
        (w + 5, y_mid),
        (w - 40, y_mid + 3),
    ], fill=(120, 120, 120))

    # Rotate
    pen = pen.rotate(-25, expand=True, resample=Image.BICUBIC,
                     fillcolor=(0, 0, 0, 0))
    return pen


def _draw_eucalyptus(w=200, h=400):
    """Draw a decorative eucalyptus sprig prop."""
    sprig = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sprig)

    # Stem — thin dark green curved line
    stem_x = w // 2
    for y in range(20, h - 20):
        frac = y / h
        x = stem_x + int(15 * math.sin(frac * math.pi * 1.3))
        draw.line([(x - 1, y), (x + 1, y)], fill=(80, 100, 70, 200))

    # Leaves along the stem — alternating left/right
    leaf_positions = [(0.15, -1), (0.25, 1), (0.35, -1), (0.45, 1),
                      (0.55, -1), (0.65, 1), (0.75, -1), (0.85, 1)]
    for frac, side in leaf_positions:
        ly = int(frac * h)
        lx = stem_x + int(15 * math.sin(frac * math.pi * 1.3))
        # Oval leaf
        leaf_w, leaf_h = 28, 18
        offset_x = side * (leaf_w + 5)
        leaf_cx = lx + offset_x
        # Muted sage green with slight variation
        green_r = random.randint(115, 135)
        green_g = random.randint(140, 160)
        green_b = random.randint(110, 125)
        draw.ellipse(
            [leaf_cx - leaf_w, ly - leaf_h, leaf_cx + leaf_w, ly + leaf_h],
            fill=(green_r, green_g, green_b, 180),
        )
        # Leaf vein
        draw.line([(leaf_cx - leaf_w + 5, ly), (leaf_cx + leaf_w - 5, ly)],
                  fill=(90, 110, 80, 60), width=1)

    # Rotate slightly
    sprig = sprig.rotate(-15, expand=True, resample=Image.BICUBIC,
                         fillcolor=(0, 0, 0, 0))
    return sprig


def _draw_coffee_cup(size=140):
    """Draw a latte art coffee cup seen from above (circle prop)."""
    cup = Image.new("RGBA", (size + 40, size + 40), (0, 0, 0, 0))
    draw = ImageDraw.Draw(cup)
    cx, cy = (size + 40) // 2, (size + 40) // 2
    r = size // 2

    # Cup shadow
    draw.ellipse([(cx - r - 4, cy - r + 8), (cx + r + 4, cy + r + 12)],
                 fill=(0, 0, 0, 40))

    # White cup rim
    draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)],
                 fill=(245, 242, 236))

    # Coffee (warm brown circle inside)
    inner_r = r - 8
    draw.ellipse([(cx - inner_r, cy - inner_r), (cx + inner_r, cy + inner_r)],
                 fill=(120, 80, 50))

    # Latte art — simple leaf/fern pattern
    # Central line
    draw.line([(cx, cy - inner_r + 15), (cx, cy + inner_r - 15)],
              fill=(200, 180, 150, 100), width=2)
    # Leaf strokes
    for offset in range(-20, 25, 10):
        y_pos = cy + offset
        spread = max(5, inner_r - 25 - abs(offset))
        draw.arc([(cx - spread, y_pos - 8), (cx, y_pos + 8)],
                 180, 0, fill=(200, 180, 150, 80), width=1)
        draw.arc([(cx, y_pos - 8), (cx + spread, y_pos + 8)],
                 0, 180, fill=(200, 180, 150, 80), width=1)

    # Cup handle (small arc on the right)
    draw.arc([(cx + r - 5, cy - 15), (cx + r + 20, cy + 15)],
             -60, 60, fill=(235, 232, 226), width=4)

    return cup


def render_hero_png(template_path, title, tagline, band_color_hex, safe_title):
    """Render the complete hero image as a pure PNG flat-lay scene.

    Args:
        template_path: Path to the template PNG
        title: Product title for the bottom band
        tagline: Tagline text for the bottom band
        band_color_hex: Hex color for the band background
        safe_title: Safe filename prefix
    Returns:
        Path to the saved hero PNG
    """
    showcase_h = IMG_H - BAND_H

    # ── Background: warm beige craft paper (PurpleOcaz brand style) ──
    hero = _marble_background(IMG_W, IMG_H)

    # ── Window light overlay ──
    window = _window_light_overlay(IMG_W, IMG_H)
    hero = Image.alpha_composite(hero, window)

    # ── Load template ──
    template = Image.open(template_path).convert("RGBA")
    enhancer = ImageEnhance.Contrast(template)
    template = enhancer.enhance(1.1)

    showcase_cx = IMG_W // 2
    showcase_cy = showcase_h // 2

    # ── Props: Eucalyptus sprig (top-left, partially cropped) ──
    eucalyptus = _draw_eucalyptus(200, 400)
    hero.paste(eucalyptus, (-30, 80), eucalyptus)

    # ── Props: Coffee cup (top-right, partially cropped) ──
    coffee = _draw_coffee_cup(130)
    hero.paste(coffee, (IMG_W - 160, 50), coffee)

    # ── Back cards (ivory/cream, fanned out — matching template style) ──
    back_card_w = int(TMPL_W * 0.70)
    back_card_h = int(TMPL_H * 0.70)

    for rot, x_off, y_off in [(14, -160, -100), (-11, 180, -70)]:
        bc = Image.new("RGBA", (back_card_w, back_card_h), (0, 0, 0, 0))
        bc_draw = ImageDraw.Draw(bc)
        # Ivory card with subtle gradient (matching gift certificate style)
        for y in range(back_card_h):
            frac = y / back_card_h
            r = int(248 - 14 * frac)
            g = int(242 - 16 * frac)
            b = int(232 - 20 * frac)
            bc_draw.line([(0, y), (back_card_w - 1, y)], fill=(r, g, b, 255))
        # Dark outer border
        bc_draw.rectangle([0, 0, back_card_w - 1, back_card_h - 1],
                          outline=DARK + (120,), width=2)
        # Gold inner border (subtle)
        bc_draw.rectangle([8, 8, back_card_w - 9, back_card_h - 9],
                          outline=GOLD + (50,), width=1)
        # Faint text hint (makes it look like a real back-of-card)
        f_hint = _font(FONT_SERIF, 18)
        _draw_text_centered(bc_draw, "Gift Certificate", back_card_h // 2 - 12,
                            f_hint, (80, 74, 66, 80), back_card_w)

        # Shadow
        shadow = Image.new("RGBA",
                           (back_card_w + 80, back_card_h + 80), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(shadow)
        s_draw.rectangle([48, 52, back_card_w + 48, back_card_h + 52],
                         fill=(0, 0, 0, 60))
        shadow = shadow.filter(ImageFilter.GaussianBlur(20))
        shadow.paste(bc, (40, 40), bc)

        # Rotate
        shadow_rot = shadow.rotate(rot, expand=True, resample=Image.BICUBIC,
                                   fillcolor=(0, 0, 0, 0))
        px = showcase_cx + x_off - shadow_rot.width // 2
        py = showcase_cy + y_off - shadow_rot.height // 2
        hero.paste(shadow_rot, (px, py), shadow_rot)

    # ── Main card (front-center, dominant) ──
    main_w = int(TMPL_W * 0.85)
    main_h = int(TMPL_H * 0.85)
    main_card = template.resize((main_w, main_h), Image.LANCZOS)

    # Dramatic shadow for main card
    shadow_pad = 80
    main_shadow = Image.new(
        "RGBA", (main_w + shadow_pad * 2, main_h + shadow_pad * 2), (0, 0, 0, 0))
    ms_draw = ImageDraw.Draw(main_shadow)
    ms_draw.rectangle(
        [shadow_pad + 12, shadow_pad + 20,
         shadow_pad + main_w + 12, shadow_pad + main_h + 20],
        fill=(0, 0, 0, 90))
    main_shadow = main_shadow.filter(ImageFilter.GaussianBlur(30))

    # Slight rotation for main card (casual placement feel)
    main_rot = 2.0
    main_shadow_rot = main_shadow.rotate(main_rot, expand=True,
                                         resample=Image.BICUBIC,
                                         fillcolor=(0, 0, 0, 0))
    main_card_rot = main_card.rotate(main_rot, expand=True,
                                     resample=Image.BICUBIC,
                                     fillcolor=(0, 0, 0, 0))

    mcx = showcase_cx - main_card_rot.width // 2
    mcy = showcase_cy + 40 - main_card_rot.height // 2
    msx = showcase_cx - main_shadow_rot.width // 2
    msy = showcase_cy + 40 - main_shadow_rot.height // 2

    hero.paste(main_shadow_rot, (msx, msy), main_shadow_rot)
    hero.paste(main_card_rot, (mcx, mcy), main_card_rot)

    # ── Props: Wax seal (bottom-left of showcase) ──
    seal = _draw_wax_seal(90)
    hero.paste(seal, (showcase_cx - main_w // 2 - 20,
                      showcase_cy + main_h // 2 - 10), seal)

    # ── Props: Pen (bottom-right, angled) ──
    pen = _draw_pen(300, 15)
    hero.paste(pen, (showcase_cx + main_w // 2 - 220,
                     showcase_cy + main_h // 2 + 10), pen)

    # ── Props: Second eucalyptus (bottom-right, smaller, cropped) ──
    euc2 = _draw_eucalyptus(150, 300)
    euc2 = euc2.rotate(45, expand=True, resample=Image.BICUBIC,
                       fillcolor=(0, 0, 0, 0))
    hero.paste(euc2, (IMG_W - 200, showcase_h - 300), euc2)

    # ── Bottom band ──
    band = Image.new("RGBA", (IMG_W, BAND_H), (0, 0, 0, 0))
    band_draw = ImageDraw.Draw(band)

    # Band gradient
    try:
        band_r = int(band_color_hex.lstrip("#")[0:2], 16)
        band_g = int(band_color_hex.lstrip("#")[2:4], 16)
        band_b = int(band_color_hex.lstrip("#")[4:6], 16)
    except (ValueError, IndexError):
        band_r, band_g, band_b = 20, 18, 30

    for y in range(BAND_H):
        frac = y / BAND_H
        r = int(band_r * (1 - frac * 0.5))
        g = int(band_g * (1 - frac * 0.5))
        b = int(band_b * (1 - frac * 0.5))
        band_draw.line([(0, y), (IMG_W, y)], fill=(r, g, b, 255))

    # Gold accent line at top of band
    band_draw.line([(int(IMG_W * 0.1), 0), (int(IMG_W * 0.9), 0)],
                   fill=GOLD + (100,), width=2)

    # Gold ornament
    bcx = IMG_W // 2
    diamond_y = 30
    ds = 4
    band_draw.polygon([(bcx, diamond_y - ds), (bcx + ds, diamond_y),
                       (bcx, diamond_y + ds), (bcx - ds, diamond_y)],
                      fill=GOLD + (100,))
    band_draw.line([(bcx - 60, diamond_y), (bcx - 8, diamond_y)],
                   fill=GOLD + (80,), width=1)
    band_draw.line([(bcx + 8, diamond_y), (bcx + 60, diamond_y)],
                   fill=GOLD + (80,), width=1)

    # Title
    f_band_title = _font(FONT_SERIF, 76)
    _draw_text_centered(band_draw, title, 50, f_band_title, WHITE, IMG_W)

    # Tagline
    f_tagline = _font(FONT_SANS, 20)
    _draw_text_centered(band_draw, tagline, 145, f_tagline,
                        GOLD + (160,), IMG_W)

    hero.paste(band, (0, IMG_H - BAND_H), band)

    # ── "Edit in Canva" badge ──
    badge_size = 190
    badge = Image.new("RGBA", (badge_size, badge_size), (0, 0, 0, 0))
    b_draw = ImageDraw.Draw(badge)
    # Shadow
    b_draw.ellipse([(6, 8), (badge_size - 4, badge_size + 2)],
                   fill=(0, 0, 0, 80))
    badge = badge.filter(ImageFilter.GaussianBlur(6))
    b_draw = ImageDraw.Draw(badge)
    # Orange circle
    b_draw.ellipse([(5, 5), (badge_size - 5, badge_size - 5)], fill=ORANGE)
    # Text
    f_badge_top = _font(FONT_SANS_REG, 22)
    f_badge_bot = _font(FONT_SANS, 34)
    _draw_text_centered(b_draw, "EDIT IN", badge_size // 2 - 22,
                        f_badge_top, WHITE, badge_size)
    _draw_text_centered(b_draw, "CANVA", badge_size // 2 + 8,
                        f_badge_bot, WHITE, badge_size)

    badge_x = IMG_W - badge_size - 80
    badge_y = IMG_H - BAND_H - badge_size // 2
    hero.paste(badge, (badge_x, badge_y), badge)

    # ── Save ──
    path = os.path.join(EXPORT_DIR, f"{safe_title}_page1.png")
    hero.convert("RGB").save(path, "PNG", quality=95)
    return path
