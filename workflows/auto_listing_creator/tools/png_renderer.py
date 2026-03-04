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
    """Create a dark marble/slate surface texture."""
    bg = Image.new("RGBA", (w, h), DARK_BG + (255,))
    draw = ImageDraw.Draw(bg)

    # Base gradient — warm charcoal
    for y in range(h):
        frac = y / h
        r = int(16 + 6 * math.sin(frac * math.pi))
        g = int(14 + 5 * math.sin(frac * math.pi))
        b = int(20 + 4 * math.sin(frac * math.pi))
        draw.line([(0, y), (w, y)], fill=(r, g, b, 255))

    # Marble vein streaks
    for _ in range(8):
        x1 = random.randint(0, w)
        y1 = random.randint(0, h)
        angle = random.uniform(0.3, 0.8)
        length = random.randint(400, 1200)
        for i in range(length):
            px = int(x1 + i * math.cos(angle))
            py = int(y1 + i * math.sin(angle))
            if 0 <= px < w and 0 <= py < h:
                jitter = random.randint(-2, 2)
                a = max(0, 12 - abs(jitter) * 3)
                if a > 0:
                    draw.point((px, py + jitter), fill=(255, 255, 255, a))

    # Warm ambient glow from top-center
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    for r_val in range(500, 0, -5):
        alpha = int(4 * (r_val / 500))
        if alpha > 0:
            glow_draw.ellipse(
                [w // 2 - r_val * 2, -r_val, w // 2 + r_val * 2, r_val * 2],
                fill=(201, 168, 76, alpha),
            )
    bg = Image.alpha_composite(bg, glow)

    # Noise texture
    bg = _add_noise(bg, 6)

    return bg


def _window_light_overlay(w, h):
    """Create diagonal window light bars."""
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Diagonal light bands
    bands = [
        (0.20, 0.35, 6),   # band 1 (start_frac, end_frac, alpha)
        (0.45, 0.55, 4),   # band 2
        (0.68, 0.74, 3),   # band 3
    ]
    angle = math.radians(52)
    for start_f, end_f, alpha in bands:
        for y in range(h):
            x_offset = int(y / math.tan(angle))
            x1 = int(start_f * w) + x_offset
            x2 = int(end_f * w) + x_offset
            x1 = max(0, min(w, x1))
            x2 = max(0, min(w, x2))
            if x1 < x2:
                draw.line([(x1, y), (x2, y)], fill=(255, 255, 255, alpha))

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

    # ── Background: dark marble surface ──
    hero = _marble_background(IMG_W, IMG_H)

    # ── Window light overlay ──
    window = _window_light_overlay(IMG_W, IMG_H)
    hero = Image.alpha_composite(hero, window)

    # ── Load template ──
    template = Image.open(template_path).convert("RGBA")
    enhancer = ImageEnhance.Contrast(template)
    template = enhancer.enhance(1.08)

    showcase_cx = IMG_W // 2
    showcase_cy = showcase_h // 2

    # ── Back cards (ivory, fanned) ──
    back_card_w = int(TMPL_W * 0.72)
    back_card_h = int(TMPL_H * 0.72)

    for rot, x_off, y_off in [(12, -30, -40), (-10, 30, -50)]:
        bc = Image.new("RGBA", (back_card_w, back_card_h), (0, 0, 0, 0))
        bc_draw = ImageDraw.Draw(bc)
        # Ivory fill with gradient
        for y in range(back_card_h):
            frac = y / back_card_h
            r = int(235 - 10 * frac)
            g = int(227 - 12 * frac)
            b = int(212 - 14 * frac)
            bc_draw.line([(2, y), (back_card_w - 3, y)], fill=(r, g, b, 255))
        # Dark border
        bc_draw.rectangle([0, 0, back_card_w - 1, back_card_h - 1],
                          outline=DARK + (100,), width=2)

        # Shadow
        shadow = Image.new("RGBA",
                           (back_card_w + 80, back_card_h + 80), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(shadow)
        s_draw.rectangle([48, 52, back_card_w + 48, back_card_h + 52],
                         fill=(0, 0, 0, 80))
        shadow = shadow.filter(ImageFilter.GaussianBlur(22))
        shadow.paste(bc, (40, 40), bc)

        # Rotate
        shadow_rot = shadow.rotate(rot, expand=True, resample=Image.BICUBIC,
                                   fillcolor=(0, 0, 0, 0))
        px = showcase_cx + x_off - shadow_rot.width // 2
        py = showcase_cy + y_off - shadow_rot.height // 2
        hero.paste(shadow_rot, (px, py), shadow_rot)

    # ── Main card (front-center) ──
    main_w = int(TMPL_W * 0.82)
    main_h = int(TMPL_H * 0.82)
    main_card = template.resize((main_w, main_h), Image.LANCZOS)

    # Dramatic shadow for main card
    shadow_pad = 70
    main_shadow = Image.new(
        "RGBA", (main_w + shadow_pad * 2, main_h + shadow_pad * 2), (0, 0, 0, 0))
    ms_draw = ImageDraw.Draw(main_shadow)
    ms_draw.rectangle(
        [shadow_pad + 10, shadow_pad + 18,
         shadow_pad + main_w + 10, shadow_pad + main_h + 18],
        fill=(0, 0, 0, 120))
    main_shadow = main_shadow.filter(ImageFilter.GaussianBlur(28))

    # Gold edge glow
    glow_pad = 6
    edge_glow = Image.new(
        "RGBA", (main_w + glow_pad * 2, main_h + glow_pad * 2), (0, 0, 0, 0))
    eg_fill = Image.new("RGBA", (main_w, main_h), GOLD + (12,))
    edge_glow.paste(eg_fill, (glow_pad, glow_pad))
    edge_glow = edge_glow.filter(ImageFilter.GaussianBlur(6))

    # Slight rotation for main card
    main_rot = 1.5
    main_shadow_rot = main_shadow.rotate(main_rot, expand=True,
                                         resample=Image.BICUBIC,
                                         fillcolor=(0, 0, 0, 0))
    edge_glow_rot = edge_glow.rotate(main_rot, expand=True,
                                     resample=Image.BICUBIC,
                                     fillcolor=(0, 0, 0, 0))
    main_card_rot = main_card.rotate(main_rot, expand=True,
                                     resample=Image.BICUBIC,
                                     fillcolor=(0, 0, 0, 0))

    mcx = showcase_cx - main_card_rot.width // 2
    mcy = showcase_cy + 30 - main_card_rot.height // 2
    msx = showcase_cx - main_shadow_rot.width // 2
    msy = showcase_cy + 30 - main_shadow_rot.height // 2
    mgx = showcase_cx - edge_glow_rot.width // 2
    mgy = showcase_cy + 30 - edge_glow_rot.height // 2

    hero.paste(main_shadow_rot, (msx, msy), main_shadow_rot)
    hero.paste(edge_glow_rot, (mgx, mgy), edge_glow_rot)
    hero.paste(main_card_rot, (mcx, mcy), main_card_rot)

    # ── Props ──
    # Wax seal (bottom-left of showcase)
    seal = _draw_wax_seal(80)
    hero.paste(seal, (showcase_cx - main_w // 2 - 40,
                      showcase_cy + main_h // 2 - 30), seal)

    # Pen (bottom-right)
    pen = _draw_pen(280, 14)
    hero.paste(pen, (showcase_cx + main_w // 2 - 200,
                     showcase_cy + main_h // 2 - 20), pen)

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
