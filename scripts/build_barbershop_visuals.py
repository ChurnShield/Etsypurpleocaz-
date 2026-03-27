#!/usr/bin/env python3
"""
Barbershop Visual Bundle — 3 templates + preview grid.
1. Service Price List (2550x3300 US Letter)
2. Gift Certificate (2550x1800 landscape)
3. Loyalty Punch Card (1050x600 business card)

Design system: #0A0A0A bg, #C9A96E gold, #FFFFFF white, #888888 grey.
"""

import os, io, math
import boto3, requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

PROJECT_ROOT = Path("/root/NEW-AI-PROJECT")
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "barbershop" / "visual"
PHOTO_DIR = PROJECT_ROOT / "assets" / "photos" / "barbershop"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PHOTO_DIR.mkdir(parents=True, exist_ok=True)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"

BG      = (10, 10, 10)
PANEL   = (26, 26, 26)
BOX     = (42, 42, 42)
GOLD    = (201, 169, 110)
WHITE   = (255, 255, 255)
GREY    = (136, 136, 136)


def font(size, bold=False, italic=False):
    p = FONT_SERIF if italic else (FONT_BOLD if bold else FONT_REGULAR)
    return ImageFont.truetype(p, size)


def centred(draw, y, text, fill, f, canvas_w=None):
    w = canvas_w or draw.im.size[0]
    bbox = draw.textbbox((0, 0), text, font=f)
    tw = bbox[2] - bbox[0]
    draw.text(((w - tw) // 2, y), text, fill=fill, font=f)


def right_aligned(draw, x_right, y, text, fill, f):
    bbox = draw.textbbox((0, 0), text, font=f)
    tw = bbox[2] - bbox[0]
    draw.text((x_right - tw, y), text, fill=fill, font=f)


def draw_scissors(draw, cx, cy, size=80):
    draw.line([(cx - size, cy - 50), (cx + size, cy + 50)], fill=GOLD, width=8)
    draw.line([(cx + size, cy - 50), (cx - size, cy + 50)], fill=GOLD, width=8)
    for ex, ey in [(cx - size, cy - 50), (cx + size, cy - 50),
                   (cx - size, cy + 50), (cx + size, cy + 50)]:
        draw.ellipse([ex - 10, ey - 10, ex + 10, ey + 10], outline=GOLD, width=3)


def fetch_photo(query, filename, w=680, h=813):
    """Fetch from Unsplash. On failure, return None."""
    path = PHOTO_DIR / filename
    if path.exists():
        print(f"  Photo cached: {filename}")
        return path
    try:
        url = f"https://source.unsplash.com/random/{w}x{h}/?{query.replace(' ', ',')}"
        r = requests.get(url, timeout=15, allow_redirects=True)
        if r.status_code == 200 and len(r.content) > 5000:
            path.write_bytes(r.content)
            print(f"  Fetched photo: {filename} ({len(r.content)} bytes)")
            return path
    except Exception as e:
        print(f"  Photo fetch failed ({filename}): {e}")
    return None


def make_photo_panel(photo_path, w, h, overlay_alpha=115):
    """Load photo, resize to wxh, apply dark overlay."""
    if photo_path and photo_path.exists():
        img = Image.open(photo_path).convert("RGBA").resize((w, h), Image.LANCZOS)
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, overlay_alpha))
        img = Image.alpha_composite(img, overlay)
        return img.convert("RGB")
    # Fallback: solid panel with scissors
    img = Image.new("RGB", (w, h), PANEL)
    d = ImageDraw.Draw(img)
    draw_scissors(d, w // 2, h // 2, size=60)
    return img


# ════════════════════════════════════════════
# VISUAL 1 — SERVICE PRICE LIST
# ════════════════════════════════════════════

def build_price_list():
    print("Building price list...")
    W, H = 2550, 3300
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Margins
    mx = 200
    mx_end = W - 200

    def section_title(y, title):
        draw.text((mx, y), title, fill=GOLD, font=font(34, bold=True))
        draw.rectangle([mx, y + 48, mx_end, y + 50], fill=GOLD)
        return y + 60

    def service_row(y, name, price):
        draw.text((mx, y), name, fill=WHITE, font=font(28))
        right_aligned(draw, mx_end, y, price, GOLD, font(28))
        name_bbox = draw.textbbox((mx, y), name, font=font(28))
        price_bbox = draw.textbbox((0, 0), price, font=font(28))
        dot_start = name_bbox[2] + 20
        dot_end = mx_end - (price_bbox[2] - price_bbox[0]) - 20
        dot_y = y + 18
        x = dot_start
        while x < dot_end:
            draw.ellipse([x, dot_y, x + 4, dot_y + 4], fill=GREY)
            x += 14
        return y + 56

    # ── Header ──
    draw.rectangle([0, 0, W, 10], fill=GOLD)
    draw_scissors(draw, W // 2, 100, size=80)
    centred(draw, 200, "YOUR BARBERSHOP NAME", WHITE, font(72, bold=True), W)
    centred(draw, 280, "MASTER BARBERS", GOLD, font(30), W)
    draw.rectangle([mx, 340, mx_end, 344], fill=GOLD)
    centred(draw, 380, "SERVICE MENU & PRICE LIST", WHITE, font(50, bold=True), W)
    draw.rectangle([mx, 450, mx_end, 454], fill=GOLD)

    # ── Classic Cuts ──
    y = section_title(510, "CLASSIC CUTS")
    for name, price in [("Haircut", "$25"), ("Children's Cut", "$18"),
                        ("Buzz Cut", "$20"), ("Crew Cut", "$22")]:
        y = service_row(y, name, price)

    # ── Fades & Tapers ──
    y = section_title(y + 40, "FADES & TAPERS")
    for name, price in [("Low Fade", "$28"), ("Mid Fade", "$28"),
                        ("High Fade", "$28"), ("Skin Fade", "$32"),
                        ("Taper Fade", "$30")]:
        y = service_row(y, name, price)

    # ── Beard Services ──
    y = section_title(y + 40, "BEARD SERVICES")
    for name, price in [("Beard Trim", "$15"), ("Beard Shape Up", "$20"),
                        ("Hot Towel Shave", "$30"), ("Beard + Cut Combo", "$40")]:
        y = service_row(y, name, price)

    # ── Colour & Treatments ──
    y = section_title(y + 40, "COLOUR & TREATMENTS")
    for name, price in [("Grey Blending", "$35"), ("Full Colour", "$45"),
                        ("Scalp Treatment", "$25"), ("Keratin Treatment", "$50"),
                        ("Hair Design / Pattern", "$15")]:
        y = service_row(y, name, price)

    # ── Gold divider ──
    y += 30
    draw.rectangle([mx, y, mx_end, y + 4], fill=GOLD)
    y += 4

    # ── Packages ──
    y = section_title(y + 40, "PACKAGES")
    for name, price in [("The Works (Cut + Beard + Wash)", "$55"),
                        ("Father & Son Combo", "$40"),
                        ("Groom's Package (Cut + Shave + Style)", "$65"),
                        ("VIP Experience (Cut + Beard + Towel + Wash)", "$75")]:
        y = service_row(y, name, price)

    # ── Add-Ons ──
    y = section_title(y + 40, "ADD-ONS")
    for name, price in [("Line Up", "$10"), ("Hair Wash", "$12"),
                        ("Eyebrow Shape", "$10"), ("Hot Towel Treatment", "$8"),
                        ("Neck Shave", "$5")]:
        y = service_row(y, name, price)

    # ── Walk-ins banner ──
    y += 50
    draw.rectangle([mx, y, mx_end, y + 4], fill=GOLD)
    centred(draw, y + 30, "WALK-INS WELCOME  ·  APPOINTMENTS PREFERRED", GOLD, font(28), W)

    # ── Decorative scissors ──
    centred_y = y + 100
    draw_scissors(draw, W // 2, centred_y, size=60)

    # ── Footer ──
    footer_top = H - 280
    draw.rectangle([0, footer_top, W, footer_top + 6], fill=GOLD)
    centred(draw, footer_top + 40, "BOOK YOUR APPOINTMENT TODAY", GOLD, font(40, bold=True), W)
    centred(draw, footer_top + 100, "+1 (555) 000-0000  ·  www.yourbarbershop.com", WHITE, font(28), W)
    centred(draw, footer_top + 150, "123 Main St, Your City, ST  ·  Mon-Sat 9AM-8PM  Sun 10AM-4PM", GOLD, font(24), W)
    draw_scissors(draw, 200, footer_top + 120, size=40)
    draw_scissors(draw, W - 200, footer_top + 120, size=40)
    draw.rectangle([0, H - 10, W, H], fill=GOLD)

    out = OUTPUT_DIR / "barber_visual_01_pricelist.png"
    img.save(str(out), "PNG")
    print(f"  Saved: {out} ({out.stat().st_size} bytes)")
    return out


# ════════════════════════════════════════════
# VISUAL 2 — GIFT CERTIFICATE
# ════════════════════════════════════════════

def build_gift_certificate():
    print("Building gift certificate...")
    W, H = 2550, 1800
    CREAM = (255, 253, 245)
    DARK_TEXT = (26, 26, 26)
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)

    # ── TOP 40%: dark premium header ──
    top_h = int(H * 0.40)  # 720px

    # Photo strip across top (4 photos, full top_h)
    photo_dir = PROJECT_ROOT / "assets" / "photos" / "barbershop_haircut_fade_dark"
    slot_w = W // 4
    for i in range(1, 5):
        photo_path = photo_dir / f"photo_{i}.jpg"
        if photo_path.exists():
            p = Image.open(photo_path).convert("RGB")
            pw, ph = p.size
            target_ratio = slot_w / top_h
            crop_w = int(ph * target_ratio)
            if crop_w > pw:
                crop_h = int(pw / target_ratio)
                top = (ph - crop_h) // 2
                p = p.crop((0, top, pw, top + crop_h))
            else:
                left = (pw - crop_w) // 2
                p = p.crop((left, 0, left + crop_w, ph))
            p = p.resize((slot_w, top_h), Image.LANCZOS)
            overlay = Image.new("RGBA", (slot_w, top_h), (0, 0, 0, 130))
            p = Image.alpha_composite(p.convert("RGBA"), overlay).convert("RGB")
            img.paste(p, ((i - 1) * slot_w, 0))
        else:
            draw.rectangle([(i - 1) * slot_w, 0, i * slot_w, top_h], fill=BG)

    # Gold border top
    draw.rectangle([0, 0, W, 8], fill=GOLD)

    # Title content over dark photos
    draw_scissors(draw, W // 2, 140, size=55)
    centred(draw, 230, "GIFT CERTIFICATE", WHITE, font(90, bold=True), W)
    rule_x = (W - 600) // 2
    draw.rectangle([rule_x, 345, rule_x + 600, 349], fill=GOLD)
    centred(draw, 380, "YOUR BARBERSHOP NAME", GOLD, font(52, bold=True), W)
    centred(draw, 455, "MASTER BARBERS", WHITE, font(28), W)

    # Gold border at split
    draw.rectangle([0, top_h - 4, W, top_h + 4], fill=GOLD)

    # ── BOTTOM 60%: cream writable section ──
    mx = 280
    mx_end = W - 280

    # Form fields
    def form_field(y, label):
        draw.text((mx, y), label, fill=DARK_TEXT, font=font(30))
        label_bbox = draw.textbbox((mx, y), label, font=font(30))
        line_y = y + 48
        draw.rectangle([mx, line_y, mx_end, line_y + 2], fill=GOLD)
        return line_y + 50

    y = top_h + 60
    centred(draw, y, "This certificate entitles the bearer to:", DARK_TEXT, font(28, italic=True), W)

    y = top_h + 130
    y = form_field(y, "Recipient Name:")
    y = form_field(y, "Value / Service:")
    y = form_field(y, "Valid Until:")
    y = form_field(y, "Authorised By:")

    # Gold outline pill — NOT REDEEMABLE FOR CASH
    pill_w, pill_h = 620, 54
    pill_x = (W - pill_w) // 2
    pill_y = y + 30
    r = pill_h // 2
    draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h],
                           radius=r, outline=GOLD, width=3)
    centred(draw, pill_y + 13, "NOT REDEEMABLE FOR CASH", DARK_TEXT, font(22, bold=True), W)

    # Decorative scissors
    draw_scissors(draw, W // 2, pill_y + pill_h + 70, size=40)

    # ── Footer ──
    draw.rectangle([0, H - 70, W, H - 66], fill=GOLD)
    centred(draw, H - 50, "www.yourbarbershop.com  ·  +1 (555) 000-0000", DARK_TEXT, font(22), W)
    draw.rectangle([0, H - 8, W, H], fill=GOLD)

    out = OUTPUT_DIR / "barber_visual_02_giftcert.png"
    img.save(str(out), "PNG")
    print(f"  Saved: {out} ({out.stat().st_size} bytes)")
    return out


# ════════════════════════════════════════════
# VISUAL 3 — LOYALTY PUNCH CARD
# ════════════════════════════════════════════

def build_loyalty_card():
    print("Building loyalty card (CR80: 1012x638)...")
    # CR80 standard: 85.6mm x 53.98mm. At 300 DPI = 1012 x 638 px
    W, H = 1012, 638
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # ── Left third: photo with dark overlay ──
    left_w = int(W * 0.35)  # 354px
    photo_path = PROJECT_ROOT / "assets" / "photos" / "barber_tools_scissors_razor" / "photo_1.jpg"
    if photo_path.exists():
        p = Image.open(photo_path).convert("RGB")
        pw, ph = p.size
        # Centre-crop to left_w x H
        target_ratio = left_w / H
        crop_w = int(ph * target_ratio)
        if crop_w > pw:
            crop_h = int(pw / target_ratio)
            top = (ph - crop_h) // 2
            p = p.crop((0, top, pw, top + crop_h))
        else:
            left = (pw - crop_w) // 2
            p = p.crop((left, 0, left + crop_w, ph))
        p = p.resize((left_w, H), Image.LANCZOS)
        # Dark overlay for readability
        overlay = Image.new("RGBA", (left_w, H), (0, 0, 0, 140))
        p = Image.alpha_composite(p.convert("RGBA"), overlay).convert("RGB")
        img.paste(p, (0, 0))
    else:
        draw.rectangle([0, 0, left_w, H], fill=PANEL)
        draw_scissors(draw, left_w // 2, H // 2, size=30)

    # Gold vertical divider
    draw.rectangle([left_w, 0, left_w + 3, H], fill=GOLD)

    # Gold bars top/bottom
    draw.rectangle([0, 0, W, 6], fill=GOLD)
    draw.rectangle([0, H - 6, W, H], fill=GOLD)

    # ── Left text overlay ──
    lx = 30
    draw.text((lx, 50), "YOUR", fill=WHITE, font=font(20, bold=True))
    draw.text((lx, 78), "BARBERSHOP", fill=WHITE, font=font(20, bold=True))
    draw.text((lx, 106), "NAME", fill=WHITE, font=font(20, bold=True))
    draw.rectangle([lx, 140, lx + 120, 142], fill=GOLD)
    draw.text((lx, 155), "LOYALTY CARD", fill=GOLD, font=font(13))
    draw.text((lx, 220), "YOUR 10TH", fill=WHITE, font=font(16, bold=True))
    draw.text((lx, 245), "CUT IS FREE", fill=GOLD, font=font(16, bold=True))
    draw.text((lx, 580), "@yourbarbershop", fill=GREY, font=font(11))

    # ── Right section ──
    rx = left_w + 30
    rr = W - 25
    draw.text((rx, 45), "COLLECT YOUR STAMPS", fill=GREY, font=font(12))

    # 10 circles in 2 rows of 5
    circle_d = 48
    h_spacing = (rr - rx) / 5
    for row in range(2):
        for col in range(5):
            num = row * 5 + col + 1
            cx = int(rx + col * h_spacing + (h_spacing - circle_d) / 2)
            cy = 90 + row * 90
            draw.ellipse([cx, cy, cx + circle_d, cy + circle_d], outline=GOLD, width=2)
            # Number below
            num_str = str(num)
            nb = draw.textbbox((0, 0), num_str, font=font(10))
            nw = nb[2] - nb[0]
            draw.text((cx + (circle_d - nw) // 2, cy + circle_d + 4),
                      num_str, fill=GREY, font=font(10))
            # Stamp in circle 1
            if num == 1:
                sb = draw.textbbox((0, 0), "✂", font=font(18))
                sw = sb[2] - sb[0]
                sh = sb[3] - sb[1]
                draw.text((cx + (circle_d - sw) // 2, cy + (circle_d - sh) // 2 - 2),
                          "✂", fill=GOLD, font=font(18))

    draw.text((rx, 310), "Ask your barber to stamp after each visit",
              fill=GREY, font=font(11))
    draw.rectangle([rx, 340, rr, 342], fill=GOLD)

    # Bottom info
    draw.text((rx, 365), "Valid at: YOUR BARBERSHOP NAME", fill=GREY, font=font(11))
    draw.text((rx, 390), "+1 (555) 000-0000  ·  www.yourbarbershop.com", fill=GREY, font=font(11))

    # Bottom-right scissors
    draw_scissors(draw, rr - 60, 550, size=25)

    out = OUTPUT_DIR / "barber_visual_03_loyalty.png"
    img.save(str(out), "PNG")
    print(f"  Saved: {out} ({out.stat().st_size} bytes)")
    return out


# ════════════════════════════════════════════
# PREVIEW GRID — 3x1 side by side
# ════════════════════════════════════════════

def build_preview_grid(files):
    print("Building preview grid (vertical stack)...")
    grid_w = 2400
    padding = 60
    gap = 50
    content_w = grid_w - padding * 2

    # Load and scale all images to fit content_w
    scaled = []
    for f in files:
        im = Image.open(f)
        w, h = im.size
        scale = content_w / w
        new_w = content_w
        new_h = int(h * scale)
        im = im.resize((new_w, new_h), Image.LANCZOS)
        scaled.append(im)

    total_h = padding * 2 + sum(im.size[1] for im in scaled) + gap * (len(scaled) - 1)
    grid = Image.new("RGB", (grid_w, total_h), BG)

    y = padding
    for im in scaled:
        x = (grid_w - im.size[0]) // 2
        grid.paste(im, (x, y))
        y += im.size[1] + gap

    out = OUTPUT_DIR / "preview_grid.png"
    grid.save(str(out), "PNG")
    print(f"  Saved: {out} ({out.stat().st_size} bytes)")
    return out


# ════════════════════════════════════════════
# UPLOAD TO DO SPACES
# ════════════════════════════════════════════

def upload_to_spaces(local_path, spaces_key):
    load_dotenv("/root/NEW-AI-PROJECT/purpleocaz-canva-mcp/.env")
    s3 = boto3.client("s3",
        endpoint_url="https://lon1.digitaloceanspaces.com",
        aws_access_key_id=os.getenv("DO_SPACES_KEY"),
        aws_secret_access_key=os.getenv("DO_SPACES_SECRET"),
        region_name="lon1",
    )
    s3.upload_file(
        str(local_path), "purpleocaz-assets", spaces_key,
        ExtraArgs={"ACL": "public-read", "ContentType": "image/png"},
    )
    url = f"https://purpleocaz-assets.lon1.digitaloceanspaces.com/{spaces_key}"
    print(f"  Uploaded: {url}")
    return url


# ════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════

if __name__ == "__main__":
    f1 = build_price_list()
    f2 = build_gift_certificate()
    f3 = build_loyalty_card()
    fg = build_preview_grid([f1, f2, f3])

    uploads = [
        (f1, "barbershop/visual/barber_visual_01_pricelist.png"),
        (f2, "barbershop/visual/barber_visual_02_giftcert.png"),
        (f3, "barbershop/visual/barber_visual_03_loyalty.png"),
        (fg, "barbershop/visual/preview_grid.png"),
    ]
    for local, key in uploads:
        upload_to_spaces(local, key)

    print("\nDone. All 4 files uploaded.")
