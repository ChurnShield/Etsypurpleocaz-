#!/usr/bin/env python3
"""Generate Etsy listing images for the Tattoo Flyer Pack."""

import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'tattoo-flyer-pack')
PREVIEWS = [
    os.path.join(os.path.dirname(__file__), '..', 'outputs', 'tattoo-flyer-promo', 'preview.png'),
    os.path.join(os.path.dirname(__file__), '..', 'outputs', 'tattoo-flyer-flash', 'preview.png'),
    os.path.join(os.path.dirname(__file__), '..', 'outputs', 'tattoo-flyer-studio', 'preview.png'),
    os.path.join(os.path.dirname(__file__), '..', 'outputs', 'tattoo-flyer-walkin', 'preview.png'),
]

SIZE = 3000
DARK = (26, 26, 26)
GOLD = (201, 169, 110)
WHITE = (255, 255, 255)
GREY = (140, 140, 140)


def load_font(bold=False, size=60):
    """Try to load a nice font, fall back to default."""
    paths = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def text_centre_x(draw, text, font, canvas_w):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    return (canvas_w - tw) // 2


def build_hero():
    """Image 1: Hero thumbnail — white bg, fanned flyers, dark banner bottom."""
    img = Image.new('RGB', (SIZE, SIZE), WHITE)

    # Banner height (bottom 20%)
    banner_h = int(SIZE * 0.20)
    flyer_area_h = SIZE - banner_h

    # Fan out 4 flyer previews — fill ~80% of flyer area
    angles = [-7, -2.5, 2.5, 7]
    card_h = int(flyer_area_h * 0.88)
    card_w = int(card_h * 1654 / 2339)
    canvas = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))

    for i, (preview_path, angle) in enumerate(zip(PREVIEWS, angles)):
        preview = Image.open(preview_path).resize((card_w, card_h), Image.LANCZOS)
        # Light grey border to frame against white bg
        bordered = Image.new('RGB', (card_w + 6, card_h + 6), (210, 210, 210))
        bordered.paste(preview, (3, 3))
        rotated = bordered.convert('RGBA').rotate(angle, expand=True, resample=Image.BICUBIC)

        spread = 540
        cx = SIZE // 2 + (i - 1.5) * spread
        cy = flyer_area_h // 2 + 20
        px = int(cx - rotated.width // 2)
        py = int(cy - rotated.height // 2)
        canvas.paste(rotated, (px, py), rotated)

    img = img.convert('RGBA')
    img = Image.alpha_composite(img, canvas)
    img = img.convert('RGB')

    # Dark banner at bottom
    draw = ImageDraw.Draw(img)
    banner_y = SIZE - banner_h
    draw.rectangle([0, banner_y, SIZE, SIZE], fill=DARK)

    # Banner main text
    font_banner = load_font(True, 68)
    banner_text = 'TATTOO STUDIO FLYER PACK'
    x = text_centre_x(draw, banner_text, font_banner, SIZE)
    draw.text((x, banner_y + 55), banner_text, fill=WHITE, font=font_banner)

    # Banner sub text in gold
    font_sub = load_font(False, 36)
    sub = '4 Editable Canva Templates  |  Instant Digital Download'
    x = text_centre_x(draw, sub, font_sub, SIZE)
    draw.text((x, banner_y + 150), sub, fill=GOLD, font=font_sub)

    img.save(os.path.join(OUT, 'hero.png'), 'PNG')
    print('Saved hero.png')


def build_whats_included():
    """Image 2: What's included — 2x2 grid."""
    img = Image.new('RGB', (SIZE, SIZE), WHITE)
    draw = ImageDraw.Draw(img)

    font_title = load_font(True, 50)
    title = "W H A T ' S   I N C L U D E D"
    x = text_centre_x(draw, title, font_title, SIZE)
    draw.text((x, 120), title, fill=GOLD, font=font_title)

    labels = ['Promo Flyer', 'Flash Day Flyer', 'Studio Flyer', 'Walk-In Flyer']
    font_label = load_font(False, 36)

    card_h = 1000
    card_w = int(card_h * 1654 / 2339)
    gap_x = (SIZE - 2 * card_w) // 3
    gap_y = 60
    start_y = 280

    for i, (preview_path, label) in enumerate(zip(PREVIEWS, labels)):
        col = i % 2
        row = i // 2
        preview = Image.open(preview_path).resize((card_w, card_h), Image.LANCZOS)
        # White border
        bordered = Image.new('RGB', (card_w + 8, card_h + 8), (230, 230, 230))
        bordered.paste(preview, (4, 4))

        px = gap_x + col * (card_w + gap_x)
        py = start_y + row * (card_h + gap_y + 60)
        img.paste(bordered, (px, py))

        # Label
        lx = text_centre_x(draw, label, font_label, card_w + 8) + px
        draw.text((lx, py + card_h + 14), label, fill=DARK, font=font_label)

    img.save(os.path.join(OUT, 'whats_included.png'), 'PNG')
    print('Saved whats_included.png')


def build_how_it_works():
    """Image 3: How it works — 4 steps."""
    img = Image.new('RGB', (SIZE, SIZE), WHITE)
    draw = ImageDraw.Draw(img)

    font_title = load_font(True, 50)
    title = 'H O W   I T   W O R K S'
    x = text_centre_x(draw, title, font_title, SIZE)
    draw.text((x, 200), title, fill=GOLD, font=font_title)

    # Thin gold rule
    draw.line([(400, 300), (SIZE - 400, 300)], fill=GOLD, width=2)

    steps = [
        ('🛒', 'Purchase', 'Buy and download\ninstantly'),
        ('📄', 'Open PDF', 'Click the Canva\nlink inside'),
        ('✏', 'Edit', 'Customise text,\ncolours and photos'),
        ('🖨', 'Print or Post', 'Download and\nuse anywhere'),
    ]

    font_icon = load_font(False, 90)
    font_step_title = load_font(True, 44)
    font_step_desc = load_font(False, 32)
    font_step_num = load_font(True, 28)

    col_w = SIZE // 4
    cy = SIZE // 2 - 50

    for i, (icon, step_title, desc) in enumerate(steps):
        cx = col_w * i + col_w // 2

        # Circle background
        r = 100
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GOLD, width=3)

        # Step number
        num = f'Step {i + 1}'
        nx = text_centre_x(draw, num, font_step_num, col_w) + col_w * i
        draw.text((nx, cy - r - 60), num, fill=GREY, font=font_step_num)

        # Icon
        ix = text_centre_x(draw, icon, font_icon, col_w) + col_w * i
        draw.text((ix, cy - 50), icon, fill=DARK, font=font_icon)

        # Title
        tx = text_centre_x(draw, step_title, font_step_title, col_w) + col_w * i
        draw.text((tx, cy + r + 30), step_title, fill=DARK, font=font_step_title)

        # Description
        for j, line in enumerate(desc.split('\n')):
            dx = text_centre_x(draw, line, font_step_desc, col_w) + col_w * i
            draw.text((dx, cy + r + 90 + j * 40), line, fill=GREY, font=font_step_desc)

    # Bottom gold rule
    draw.line([(400, SIZE - 300), (SIZE - 400, SIZE - 300)], fill=GOLD, width=2)

    img.save(os.path.join(OUT, 'how_it_works.png'), 'PNG')
    print('Saved how_it_works.png')


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    build_hero()
    build_whats_included()
    build_how_it_works()
