#!/usr/bin/env python3
"""Build all 6 Etsy listing images for Tattoo Studio Business Kit.
Output: 2700x2700px square, large text readable at thumbnail size."""

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

EXPORTS = os.path.dirname(os.path.abspath(__file__))
SZ = 2700
FINAL_SIZE = (SZ, SZ)

# Colors
GOLD = (201, 168, 76)
GOLD_DIM = (201, 168, 76, 140)
CREAM = (253, 251, 247)
CHARCOAL = (26, 26, 26)
DARK_BG = (18, 18, 18)
MID_GRAY = (120, 120, 120)
LIGHT_GRAY = (180, 180, 180)

# Font paths
_SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
_SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(size, bold=False, serif=True):
    if serif:
        path = _SERIF_BOLD if bold else _SERIF
    else:
        path = _SANS_BOLD if bold else _SANS
    if os.path.exists(path):
        return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def text_center_x(draw, text, y, fnt, fill, img_w=SZ):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    tw = bbox[2] - bbox[0]
    draw.text(((img_w - tw) // 2, y), text, fill=fill, font=fnt)
    return bbox[3] - bbox[1]


def gold_line(draw, y, width=300):
    x0 = (SZ - width) // 2
    draw.rectangle([(x0, y), (x0 + width, y + 5)], fill=GOLD)


def drop_shadow(card, blur=35, offset=20, alpha=140):
    pad = 120
    canvas = Image.new("RGBA", (card.width + pad*2, card.height + pad*2), (0, 0, 0, 0))
    shadow = Image.new("RGBA", card.size, (0, 0, 0, alpha))
    canvas.paste(shadow, (pad + offset, pad + offset))
    canvas = canvas.filter(ImageFilter.GaussianBlur(blur))
    canvas.paste(card, (pad, pad), card if card.mode == "RGBA" else None)
    return canvas


def dark_texture_bg():
    """Dark background with subtle noise."""
    import random
    random.seed(42)
    bg = Image.new("RGBA", FINAL_SIZE, DARK_BG + (255,))
    noise = Image.new("RGBA", FINAL_SIZE, (0, 0, 0, 0))
    nd = ImageDraw.Draw(noise)
    step = 6
    for x in range(0, SZ, step):
        for y in range(0, SZ, step):
            v = random.randint(12, 28)
            nd.rectangle([x, y, x+step-1, y+step-1], fill=(v, v, v, 255))
    return Image.alpha_composite(bg, noise)


# ============================================================
# LISTING 1 — Hero composite resized to 2700x2700
# ============================================================
def build_listing_1():
    print("  [1] Hero composite...")
    src = os.path.join(EXPORTS, "hero_composite.png")
    if not os.path.exists(src):
        print("    SKIP: hero_composite.png not found")
        return
    img = Image.open(src).convert("RGB")
    # Crop to square from centre, then resize
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    sq = img.crop((left, top, left + side, top + side))
    sq = sq.resize(FINAL_SIZE, Image.LANCZOS)
    out = os.path.join(EXPORTS, "listing_1.png")
    sq.save(out, quality=95)
    print(f"    Saved: {out} ({os.path.getsize(out)//1024}KB)")


# ============================================================
# LISTING 2 — Both cards side by side
# ============================================================
def build_listing_2():
    print("  [2] Both versions side by side...")
    bg = dark_texture_bg()

    dark = Image.open(os.path.join(EXPORTS, "dark_front.png")).convert("RGBA")
    light = Image.open(os.path.join(EXPORTS, "light_front.png")).convert("RGBA")

    # Cards fill 75% of frame width. Two cards + gap = 75% of 2700 = 2025
    gap = 70
    card_w = (2025 - gap) // 2  # ~977px each
    dark_h = int(dark.height * card_w / dark.width)
    light_h = int(light.height * card_w / light.width)
    dark_r = dark.resize((card_w, dark_h), Image.LANCZOS)
    light_r = light.resize((card_w, light_h), Image.LANCZOS)

    dark_s = drop_shadow(dark_r)
    light_s = drop_shadow(light_r)

    # Text zone at top
    draw = ImageDraw.Draw(bg)
    f_headline = font(130, bold=True)
    f_sub = font(56, bold=False, serif=False)

    text_center_x(draw, "2 Designs Included", 120, f_headline, GOLD)
    gold_line(draw, 290, 350)
    text_center_x(draw, "Dark + Light  —  Both Fully Editable", 340, f_sub, LIGHT_GRAY)

    # Position cards
    total_w = dark_s.width + gap + light_s.width
    start_x = (SZ - total_w) // 2
    card_y = 520

    bg.paste(dark_s, (start_x, card_y), dark_s)
    bg.paste(light_s, (start_x + dark_s.width + gap, card_y), light_s)

    out = os.path.join(EXPORTS, "listing_2.png")
    bg.convert("RGB").save(out, quality=95)
    print(f"    Saved: {out} ({os.path.getsize(out)//1024}KB)")


# ============================================================
# LISTING 3 — Back card detail on cream background
# ============================================================
def build_listing_3():
    print("  [3] Back card detail (cream bg)...")
    bg = Image.new("RGB", FINAL_SIZE, CREAM)

    back = Image.open(os.path.join(EXPORTS, "dark_back.png")).convert("RGBA")
    # Card fills 70% of frame width
    card_w = int(SZ * 0.70)  # 1890
    card_h = int(back.height * card_w / back.width)
    back_r = back.resize((card_w, card_h), Image.LANCZOS)
    back_s = drop_shadow(back_r, blur=40, offset=25, alpha=100)

    draw = ImageDraw.Draw(bg)
    f_headline = font(120, bold=True)
    f_sub = font(54, bold=False, serif=False)

    text_center_x(draw, "Fully Editable in Canva", 130, f_headline, GOLD)
    gold_line(draw, 300, 350)
    text_center_x(draw, "Add Your Studio Name, Contact Details & More", 360, f_sub, CHARCOAL)

    # Centre card below text
    cx = (SZ - back_s.width) // 2
    cy = 520
    bg.paste(back_s, (cx, cy), back_s)

    out = os.path.join(EXPORTS, "listing_3.png")
    bg.save(out, quality=95)
    print(f"    Saved: {out} ({os.path.getsize(out)//1024}KB)")


# ============================================================
# LISTING 4 — How It Works
# ============================================================
def build_listing_4():
    print("  [4] How It Works...")
    bg = Image.new("RGB", FINAL_SIZE, CREAM)
    draw = ImageDraw.Draw(bg)

    f_headline = font(130, bold=True)
    f_sub = font(48, bold=False, serif=False)
    f_step_num = font(120, bold=True)
    f_step_title = font(64, bold=True, serif=False)
    f_step_desc = font(44, bold=False, serif=False)

    text_center_x(draw, "How It Works", 100, f_headline, CHARCOAL)
    gold_line(draw, 280, 350)
    text_center_x(draw, "Ready to use in under 5 minutes", 340, f_sub, MID_GRAY)

    steps = [
        ("1", "Purchase on Etsy", "Complete your order and\nget instant file access"),
        ("2", "Open in Canva", "Click your link — works\nwith free Canva accounts"),
        ("3", "Edit & Download", "Add your details and\ndownload print-ready files"),
    ]

    # 3 columns
    col_w = SZ // 3
    circle_r = 120
    start_y = 560

    for i, (num, title, desc) in enumerate(steps):
        cx = col_w * i + col_w // 2

        # Dark circle with gold number
        circle_bbox = [cx - circle_r, start_y, cx + circle_r, start_y + circle_r * 2]
        draw.ellipse(circle_bbox, fill=CHARCOAL)
        # Number in circle
        nbbox = draw.textbbox((0, 0), num, font=f_step_num)
        nw = nbbox[2] - nbbox[0]
        nh = nbbox[3] - nbbox[1]
        draw.text((cx - nw//2, start_y + circle_r - nh//2 - 10), num, fill=GOLD, font=f_step_num)

        # Title below circle
        ty = start_y + circle_r * 2 + 60
        tbbox = draw.textbbox((0, 0), title, font=f_step_title)
        tw = tbbox[2] - tbbox[0]
        draw.text((cx - tw//2, ty), title, fill=CHARCOAL, font=f_step_title)

        # Gold line
        draw.rectangle([(cx - 60, ty + 90), (cx + 60, ty + 95)], fill=GOLD)

        # Description (multiline)
        dy = ty + 130
        for line in desc.split("\n"):
            lbbox = draw.textbbox((0, 0), line, font=f_step_desc)
            lw = lbbox[2] - lbbox[0]
            draw.text((cx - lw//2, dy), line, fill=MID_GRAY, font=f_step_desc)
            dy += 60

    # Footer
    f_footer = font(40, bold=False, serif=False)
    text_center_x(draw, "Works with free Canva accounts  •  No software to install", SZ - 180, f_footer, MID_GRAY)

    out = os.path.join(EXPORTS, "listing_4.png")
    bg.save(out, quality=95)
    print(f"    Saved: {out} ({os.path.getsize(out)//1024}KB)")


# ============================================================
# LISTING 5 — What's Included
# ============================================================
def build_listing_5():
    print("  [5] What's Included...")
    bg = dark_texture_bg()
    draw = ImageDraw.Draw(bg)

    f_headline = font(130, bold=True)
    f_sub = font(50, bold=False, serif=False)
    f_item = font(62, bold=False, serif=False)
    f_check = font(68, bold=True, serif=False)

    text_center_x(draw, "What's Included", 140, f_headline, GOLD)
    gold_line(draw, 320, 350)
    text_center_x(draw, "Tattoo Studio Business Card Kit", 380, f_sub, LIGHT_GRAY)

    items = [
        "Dark Business Card (Front & Back)",
        "Light Business Card (Front & Back)",
        "Fully Editable in Canva",
        "Commercial Use Licence",
        "Instant Digital Download",
    ]

    start_y = 600
    row_h = 160
    item_x = 480

    for i, item in enumerate(items):
        y = start_y + i * row_h

        # Gold check circle
        cr = 36
        cy = y + 10
        cx_circle = item_x - 80
        draw.ellipse([cx_circle - cr, cy - cr, cx_circle + cr, cy + cr],
                     fill=(201, 168, 76, 40), outline=GOLD, width=3)
        # Checkmark
        cbbox = draw.textbbox((0, 0), "✓", font=f_check)
        cw = cbbox[2] - cbbox[0]
        draw.text((cx_circle - cw//2, cy - cr + 2), "✓", fill=GOLD, font=f_check)

        # Item text
        draw.text((item_x, y - 10), item, fill=CREAM, font=f_item)

        # Subtle separator line
        if i < len(items) - 1:
            draw.rectangle([(item_x, y + row_h - 40), (SZ - 480, y + row_h - 39)],
                           fill=(60, 60, 60))

    # Footer box
    box_y = start_y + len(items) * row_h + 60
    box_pad = 40
    draw.rounded_rectangle(
        [(400, box_y), (SZ - 400, box_y + 120)],
        radius=12, outline=GOLD, width=3
    )
    f_footer = font(44, bold=False, serif=False)
    text_center_x(draw, "INSTANT DIGITAL DOWNLOAD", box_y + box_pad - 5, f_footer, GOLD)

    out = os.path.join(EXPORTS, "listing_5.png")
    bg.convert("RGB").save(out, quality=95)
    print(f"    Saved: {out} ({os.path.getsize(out)//1024}KB)")


# ============================================================
# LISTING 6 — Trust slide
# ============================================================
def build_listing_6():
    print("  [6] Trust slide...")
    bg = Image.new("RGB", FINAL_SIZE, CREAM)
    draw = ImageDraw.Draw(bg)

    f_headline = font(120, bold=True)
    f_badge_title = font(52, bold=True, serif=False)
    f_badge_sub = font(36, bold=False, serif=False)
    f_message = font(44, bold=False, serif=False)
    f_brand = font(50, bold=True, serif=False)

    # Headline
    text_center_x(draw, "Instant Digital Download", 180, f_headline, CHARCOAL)
    gold_line(draw, 360, 400)

    # 3 trust badges in a row
    badges = [
        ("Free Canva", "Account Works"),
        ("Print Ready", "High-Res Files"),
        ("Commercial", "Licence Included"),
    ]

    badge_y = 550
    col_w = SZ // 3
    badge_r = 140  # circle radius

    for i, (line1, line2) in enumerate(badges):
        cx = col_w * i + col_w // 2

        # Large gold-outline circle
        draw.ellipse(
            [cx - badge_r, badge_y, cx + badge_r, badge_y + badge_r * 2],
            fill=None, outline=GOLD, width=5
        )
        # Inner circle fill
        inner = badge_r - 15
        draw.ellipse(
            [cx - inner, badge_y + 15, cx + inner, badge_y + badge_r * 2 - 15],
            fill=(248, 245, 238)
        )

        # Badge icon (gold checkmark in circle)
        icon_font = font(100, bold=True)
        ibbox = draw.textbbox((0, 0), "✓", font=icon_font)
        iw = ibbox[2] - ibbox[0]
        draw.text((cx - iw//2, badge_y + badge_r - 55), "✓", fill=GOLD, font=icon_font)

        # Badge text below circle
        ty = badge_y + badge_r * 2 + 50
        b1bbox = draw.textbbox((0, 0), line1, font=f_badge_title)
        draw.text((cx - (b1bbox[2]-b1bbox[0])//2, ty), line1, fill=CHARCOAL, font=f_badge_title)
        b2bbox = draw.textbbox((0, 0), line2, font=f_badge_sub)
        draw.text((cx - (b2bbox[2]-b2bbox[0])//2, ty + 70), line2, fill=MID_GRAY, font=f_badge_sub)

    # Message
    msg_y = 1650
    gold_line(draw, msg_y, 300)
    text_center_x(draw, "Questions? Message us — we reply within 24 hours",
                  msg_y + 50, f_message, MID_GRAY)

    # Brand name
    text_center_x(draw, "PURPLEOCAZ", SZ - 200, f_brand, GOLD)

    out = os.path.join(EXPORTS, "listing_6.png")
    bg.save(out, quality=95)
    print(f"    Saved: {out} ({os.path.getsize(out)//1024}KB)")


# ============================================================
if __name__ == "__main__":
    print(f"Building 6 Etsy listing images ({SZ}x{SZ}px)...")
    build_listing_1()
    build_listing_2()
    build_listing_3()
    build_listing_4()
    build_listing_5()
    build_listing_6()
    print("\nDone! All images in exports/")
