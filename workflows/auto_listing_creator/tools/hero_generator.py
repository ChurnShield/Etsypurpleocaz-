# =============================================================================
# workflows/auto_listing_creator/tools/hero_generator.py
#
# PurpleOcaz Hero Image Generator
# Composites real Canva card exports onto a branded linen background
# to produce a polished Etsy primary listing image.
#
# Called by product_creator_tool._inject_hero() for every listing.
# =============================================================================

import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ── Output config ─────────────────────────────────────────────────────────────
W, H           = 2000, 1500
CARD_W_RATIO   = 0.50
BACK_ANGLE     = -5
FRONT_ANGLE    =  4
BACK_POS       = (0.34, 0.06)
FRONT_POS      = (0.16, 0.28)
BANNER_RATIO   = 0.16
BADGE_R        = 130
BADGE_POS      = (0.785, 0.60)

# Font paths — DejaVu ships with most Linux/Python environments
_FONT_BOLD   = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
_FONT_SERIF  = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
_FONT_SANS   = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'


def _load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def _make_background(w, h):
    """Warm linen texture with crimson corner triangles."""
    np.random.seed(7)
    arr = np.zeros((h, w, 3), dtype=np.float32)
    br, bg, bb = 225, 210, 188
    for y in range(h):
        for x in range(w):
            nx, ny = x / w, y / h
            dist = ((nx - 0.5) ** 2 + (ny - 0.45) ** 2) ** 0.5
            v = 1.0 - dist * 0.55
            arr[y, x] = [br * v, bg * v, bb * v]
    for y in range(0, h, 4):
        a = np.random.uniform(0.92, 1.08, w)
        arr[y, :, 0] *= a
        arr[y, :, 1] *= a * 0.99
        arr[y, :, 2] *= a * 0.97
    for x in range(0, w, 4):
        a = np.random.uniform(0.94, 1.06, h)
        arr[:, x, 0] *= a
        arr[:, x, 1] *= a * 0.99
        arr[:, x, 2] *= a * 0.97
    noise = np.random.normal(0, 3.5, (h, w, 3))
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    bg_img = Image.fromarray(arr).filter(
        ImageFilter.GaussianBlur(radius=0.4)
    ).convert('RGBA')

    # Crimson corner triangles
    ac = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ad = ImageDraw.Draw(ac)
    ad.polygon([(0, 0), (480, 0), (0, 380)],         fill=(140, 20, 20, 230))
    ad.polygon([(w, h), (w-480, h), (w, h-380)],     fill=(140, 20, 20, 210))
    ad.polygon([(0, 0), (320, 0), (0, 240)],          fill=(100, 10, 10, 180))
    ad.polygon([(w, h), (w-320, h), (w, h-240)],     fill=(100, 10, 10, 160))
    ad.line([(480, 0), (0, 380)],     fill=(200, 160, 100, 180), width=3)
    ad.line([(w-480, h), (w, h-380)], fill=(200, 160, 100, 160), width=3)
    return Image.alpha_composite(bg_img, ac)


def _rotate_with_shadow(img, angle):
    shadow = Image.new('RGBA', img.size, (0, 0, 0, 200))
    return (
        img.rotate(angle, expand=True, resample=Image.BICUBIC),
        shadow.rotate(angle, expand=True, resample=Image.BICUBIC),
    )


def _paste_shadow_card(canvas, card, shadow, x, y):
    blurred = shadow.filter(ImageFilter.GaussianBlur(radius=22))
    canvas.paste(blurred, (x + 22, y + 22), blurred)
    canvas.paste(card, (x, y), card)


def _draw_star(draw, cx, cy, r_out, r_in, fill, outline=None):
    pts = [
        (cx + (r_out if i % 2 == 0 else r_in) * math.cos(math.radians(i * 36 - 90)),
         cy + (r_out if i % 2 == 0 else r_in) * math.sin(math.radians(i * 36 - 90)))
        for i in range(10)
    ]
    draw.polygon(pts, fill=fill, outline=outline)


def generate_hero_image(front_path, back_path, output_path, title):
    """Generate a branded PurpleOcaz Etsy hero image.

    Args:
        front_path:  Path to front card PNG (Book Appointment side)
        back_path:   Path to back card PNG (Appointment Card / fields side)
        output_path: Where to save the finished JPG
        title:       Product title shown in the bottom banner
    """
    bg     = _make_background(W, H)
    front  = Image.open(front_path).convert('RGBA')
    back   = Image.open(back_path).convert('RGBA')

    cw = int(W * CARD_W_RATIO)
    ch = int(cw * (front.size[1] / front.size[0]))
    back_card,  back_shad  = _rotate_with_shadow(
        back.resize((cw, ch),  Image.LANCZOS), BACK_ANGLE)
    front_card, front_shad = _rotate_with_shadow(
        front.resize((cw, ch), Image.LANCZOS), FRONT_ANGLE)

    canvas = bg.copy()
    _paste_shadow_card(canvas, back_card,  back_shad,
                       int(W * BACK_POS[0]),  int(H * BACK_POS[1]))
    _paste_shadow_card(canvas, front_card, front_shad,
                       int(W * FRONT_POS[0]), int(H * FRONT_POS[1]))

    # ── Star Seller badge ─────────────────────────────────────────────────────
    bw, bh = 520, 175
    badge  = Image.new('RGBA', (bw, bh), (0, 0, 0, 0))
    bd     = ImageDraw.Draw(badge)
    bd.rounded_rectangle([0, 0, bw-1, bh-1], radius=20, fill=(20, 20, 20, 235))
    bd.rounded_rectangle([3, 3, bw-4, bh-4], radius=18,
                          outline=(200, 160, 50, 255), width=3)
    bd.text((bw // 2, 46), 'STAR SELLER',
            font=_load_font(_FONT_BOLD, 44), fill='white', anchor='mm')
    sx = (bw - 4 * 58 - 48) // 2 + 24
    for i in range(5):
        _draw_star(bd, sx + i * 58, 125, 29, 12, (255, 200, 40, 60))
        _draw_star(bd, sx + i * 58, 125, 24, 10,
                   (255, 200, 40, 255), (180, 130, 20, 255))
    canvas.paste(badge, (44, 44), badge)

    # ── Edit in Canva badge ───────────────────────────────────────────────────
    br = BADGE_R
    bcx, bcy = int(W * BADGE_POS[0]), int(H * BADGE_POS[1])
    eb = Image.new('RGBA', (br * 2, br * 2), (0, 0, 0, 0))
    ed = ImageDraw.Draw(eb)
    ed.ellipse([0, 0, br*2-1, br*2-1], fill=(30, 30, 30, 255))
    ed.ellipse([6, 6, br*2-7, br*2-7], outline=(180, 140, 60, 255), width=3)
    f_b = _load_font(_FONT_BOLD, 30)
    ed.text((br, br - 22), 'EDIT IN', font=f_b,
            fill=(220, 220, 220, 255), anchor='mm')
    ed.text((br, br + 16), 'CANVA',   font=f_b,
            fill=(255, 255, 255, 255), anchor='mm')
    canvas.paste(eb, (bcx - br, bcy - br), eb)

    # ── Canva Template scroll-stopper pill ────────────────────────────────────
    tw, th = 420, 85
    tag = Image.new('RGBA', (tw, th), (0, 0, 0, 0))
    td  = ImageDraw.Draw(tag)
    td.rounded_rectangle([0, 0, tw-1, th-1], radius=42, fill=(140, 20, 20, 240))
    td.rounded_rectangle([4, 4, tw-5,  th-5], radius=40,
                          outline=(200, 160, 60, 200), width=2)
    td.text((tw // 2, th // 2), '✦  CANVA TEMPLATE  ✦',
            font=_load_font(_FONT_BOLD, 30), fill='white', anchor='mm')
    canvas.paste(tag, (int(W * 0.60), int(H * 0.055)), tag)

    # ── Bottom banner ─────────────────────────────────────────────────────────
    BH     = int(H * BANNER_RATIO)
    banner = Image.new('RGBA', (W, BH), (18, 18, 20, 252))
    bd2    = ImageDraw.Draw(banner)
    bd2.line([(0, 0), (W, 0)], fill=(180, 140, 60, 200), width=4)

    display_title = title[:55] if len(title) > 55 else title

    bd2.text((W // 2, BH // 2 - 22), display_title,
             font=_load_font(_FONT_SERIF, 82), fill='white', anchor='mm')
    bd2.text((W // 2, BH // 2 + 50),
             'EDITABLE CANVA TEMPLATE  ·  INSTANT DOWNLOAD  ·  FRONT & BACK',
             font=_load_font(_FONT_BOLD, 28), fill=(180, 140, 60, 230),
             anchor='mm')
    canvas.paste(banner, (0, H - BH), banner)

    # ── Save ──────────────────────────────────────────────────────────────────
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    canvas.convert('RGB').save(output_path, quality=96)
