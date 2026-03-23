#!/usr/bin/env python3
"""listing_2.png — both cards side by side on dark textured background, 2700x2700."""

import os
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

EXPORTS = os.path.dirname(os.path.abspath(__file__))
SZ = 2700

# Colours
GOLD = (201, 168, 76)
CREAM = (245, 240, 232)
BG = (13, 13, 13)
CANVA_TEAL = (0, 196, 204)
WHITE = (255, 255, 255)

# Fonts
_SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
_SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def fnt(size, path=_SERIF_B):
    return ImageFont.truetype(path, size)


def center_text(draw, text, cx, cy, f, fill, spacing=0):
    """Draw text centred at (cx, cy). spacing = extra px between chars."""
    if spacing > 0:
        total_w = sum(draw.textbbox((0, 0), ch, font=f)[2] for ch in text) + spacing * (len(text) - 1)
        bbox0 = draw.textbbox((0, 0), text, font=f)
        th = bbox0[3] - bbox0[1]
        x = cx - total_w // 2
        y = cy - th // 2
        for ch in text:
            draw.text((x, y), ch, fill=fill, font=f)
            x += draw.textbbox((0, 0), ch, font=f)[2] + spacing
    else:
        bbox = draw.textbbox((0, 0), text, font=f)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text((cx - tw // 2, cy - th // 2), text, fill=fill, font=f)


def drop_shadow(img, blur=40, ox=20, oy=20, alpha=153):
    """Drop shadow with specified offset, blur, opacity (alpha 0-255, 60%=153)."""
    pad = 120
    canvas = Image.new("RGBA", (img.width + pad * 2, img.height + pad * 2), (0, 0, 0, 0))
    shadow = Image.new("RGBA", img.size, (0, 0, 0, alpha))
    canvas.paste(shadow, (pad + ox, pad + oy))
    canvas = canvas.filter(ImageFilter.GaussianBlur(blur))
    canvas.paste(img, (pad, pad), img if img.mode == "RGBA" else None)
    return canvas


def paste_centred(bg, img, cx, cy):
    """Paste img onto bg with img's centre at (cx, cy)."""
    x = cx - img.width // 2
    y = cy - img.height // 2
    bg.paste(img, (x, y), img if img.mode == "RGBA" else None)


def main():
    # === BACKGROUND ===
    bg = Image.new("RGBA", (SZ, SZ), BG + (255,))
    random.seed(42)
    noise = Image.new("RGBA", (SZ, SZ), (0, 0, 0, 0))
    nd = ImageDraw.Draw(noise)
    for x in range(0, SZ, 5):
        for y in range(0, SZ, 5):
            v = random.randint(8, 22)
            nd.rectangle([x, y, x + 4, y + 4], fill=(v, v, v, 255))
    bg = Image.alpha_composite(bg, noise)

    # === STEP 3: Gold radial glow behind cards ===
    glow_r = 800
    glow_d = glow_r * 2
    glow = Image.new("RGBA", (glow_d, glow_d), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    # 8% opacity = ~20/255
    gd.ellipse([(0, 0), (glow_d, glow_d)], fill=(201, 168, 76, 20))
    glow = glow.filter(ImageFilter.GaussianBlur(100))
    paste_centred(bg, glow, 1350, 1400)

    # === STEP 1 & 2: Load and resize cards ===
    dark = Image.open(os.path.join(EXPORTS, "dark_card_front.png")).convert("RGBA")
    light = Image.open(os.path.join(EXPORTS, "light_card_front.png")).convert("RGBA")

    print(f"  Dark front: {dark.size} aspect {dark.width/dark.height:.2f}")
    print(f"  Light front: {light.size} aspect {light.width/light.height:.2f}")

    # Dark is landscape (1.75:1), light is portrait (0.87:1)
    # Match both to same HEIGHT (1100px) so they look balanced side by side
    target_h = 1100
    dark_w = int(dark.width * target_h / dark.height)
    dark_r = dark.resize((dark_w, target_h), Image.LANCZOS)

    light_w = int(light.width * target_h / light.height)
    light_r = light.resize((light_w, target_h), Image.LANCZOS)

    print(f"  Dark resized: {dark_r.size}")
    print(f"  Light resized: {light_r.size}")

    # === STEP 3: Rotate and shadow ===
    dark_rot = dark_r.rotate(6, resample=Image.BICUBIC, expand=True, fillcolor=(0, 0, 0, 0))
    light_rot = light_r.rotate(-6, resample=Image.BICUBIC, expand=True, fillcolor=(0, 0, 0, 0))

    dark_s = drop_shadow(dark_rot, blur=40, ox=20, oy=20, alpha=153)
    light_s = drop_shadow(light_rot, blur=40, ox=20, oy=20, alpha=153)

    # Place: dark card left-centre, light card right-centre
    # Ensure both are fully visible within 2700px canvas
    # Dark centre at (1000, 1400), light centre at (1800, 1350)
    paste_centred(bg, dark_s, 1000, 1400)
    paste_centred(bg, light_s, 1800, 1350)

    # === STEP 4: Text overlay ===
    draw = ImageDraw.Draw(bg)

    # Gold decorative line at top
    draw.rectangle([(1350 - 100, 159), (1350 + 100, 161)], fill=GOLD)

    # "2 DESIGNS INCLUDED"
    f_head = fnt(155, _SERIF_B)
    center_text(draw, "2 DESIGNS INCLUDED", 1350, 270, f_head, GOLD, spacing=15)

    # Subtitle
    f_sub = fnt(54, _SANS)
    center_text(draw, "Tattoo Studio Business Card Template  —  Digital Download", 1350, 380, f_sub, CREAM)

    # Gold underline
    draw.rectangle([(1350 - 150, 414), (1350 + 150, 416)], fill=GOLD)

    # === STEP 5: Canva badge ===
    pill_w, pill_h = 580, 110
    pill_cx, pill_cy = 1350, 2530
    pill_x = pill_cx - pill_w // 2
    pill_y = pill_cy - pill_h // 2

    # White outer glow
    glow2 = Image.new("RGBA", (pill_w + 160, pill_h + 160), (0, 0, 0, 0))
    g2d = ImageDraw.Draw(glow2)
    g2d.rounded_rectangle(
        [(0, 0), (pill_w + 160, pill_h + 160)],
        radius=pill_h, fill=(255, 255, 255, 40)
    )
    glow2 = glow2.filter(ImageFilter.GaussianBlur(35))
    paste_centred(bg, glow2, pill_cx, pill_cy)

    draw = ImageDraw.Draw(bg)
    draw.rounded_rectangle(
        [(pill_x, pill_y), (pill_x + pill_w, pill_y + pill_h)],
        radius=55, fill=CANVA_TEAL
    )

    f_badge = fnt(52, _SANS_B)
    center_text(draw, "Edit with Canva", pill_cx, pill_cy, f_badge, WHITE)

    # === SAVE ===
    out = os.path.join(EXPORTS, "listing_2.png")
    bg.convert("RGB").save(out, quality=95)
    kb = os.path.getsize(out) // 1024
    print(f"  Saved: listing_2.png — {SZ}x{SZ}px — {kb}KB")


if __name__ == "__main__":
    print("Building listing_2.png from scratch...")
    main()
