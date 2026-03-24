#!/usr/bin/env python3
"""
Car Detailing Pinterest Pins — 8 portrait pins (1000x1500px).
One pin per Etsy listing. Downloads source images from Spaces,
composites pin layout, generates descriptions, uploads to Spaces.
"""

import os
import re
import requests
import boto3
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ── Config ─────────────────────────────────────────────
PROJECT_ROOT = Path("/root/NEW-AI-PROJECT")
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "pinterest" / "car-detail"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SPACES_BASE = "https://purpleocaz-assets.lon1.digitaloceanspaces.com"

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

W, H = 1000, 1500
BG = (13, 13, 13)
ACCENT = (224, 32, 32)
WHITE = (255, 255, 255)
SILVER = (192, 192, 192)


def font(size, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REGULAR, size)


def centred(draw, y, text, fill, f):
    bbox = draw.textbbox((0, 0), text, font=f)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, y), text, fill=fill, font=f)


def draw_pill(draw, cx, y, w, h, fill, text, text_color, text_size):
    x = cx - w // 2
    r = h // 2
    draw.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=fill)
    f = font(text_size, bold=True)
    bbox = draw.textbbox((0, 0), text, font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((x + (w - tw) // 2, y + (h - th) // 2 - 2), text, fill=text_color, font=f)


def fetch_image(spaces_path):
    """Download image from Spaces, return PIL Image."""
    url = f"{SPACES_BASE}/{spaces_path}"
    resp = requests.get(url, timeout=30)
    if resp.status_code != 200 or len(resp.content) < 1000:
        raise ValueError(f"Failed to fetch {url}: {resp.status_code}, {len(resp.content)} bytes")
    from io import BytesIO
    return Image.open(BytesIO(resp.content)).convert("RGB")


def dark_overlay(img, opacity=0.3):
    from PIL import Image as PILImage
    overlay = PILImage.new("RGBA", img.size, (0, 0, 0, int(255 * opacity)))
    base = img.convert("RGBA")
    return PILImage.alpha_composite(base, overlay).convert("RGB")


PINS = [
    {
        "num": "50+", "product": "CAR DETAILING BUSINESS KIT",
        "subtitle": "Complete Canva Template Bundle", "price": "£34.99",
        "source": "thumbnails/car-detail/hero_mega_bundle.png",
        "etsy_url": "https://www.etsy.com/listing/4476909005",
        "filename": "pin_01_mega_bundle.png",
    },
    {
        "num": "20", "product": "CAR DETAILING SOCIAL MEDIA PACK",
        "subtitle": "Instagram Post Templates", "price": "£7.99",
        "source": "social/car-detail/preview_grid.png",
        "etsy_url": "https://www.etsy.com/listing/4476850754",
        "filename": "pin_02_social.png",
    },
    {
        "num": "6", "product": "CAR DETAILING BRANDING KIT",
        "subtitle": "Business Card, Invoice & More", "price": "£6.99",
        "source": "branding/car-detail/preview_grid.png",
        "etsy_url": "https://www.etsy.com/listing/4476893828",
        "filename": "pin_03_branding.png",
    },
    {
        "num": "6", "product": "CAR DETAILING EMAIL TEMPLATES",
        "subtitle": "Booking, Reviews & Follow-Up", "price": "£5.99",
        "source": "email-templates/car-detail/preview_grid.png",
        "etsy_url": "https://www.etsy.com/listing/4476891933",
        "filename": "pin_04_email.png",
    },
    {
        "num": "15", "product": "CAR DETAILING BUSINESS BUNDLE",
        "subtitle": "Complete Template Collection", "price": "£9.99",
        "source": "thumbnails/car-detail/v3/hero_forms_bundle_v3.png",
        "etsy_url": "https://www.etsy.com/listing/4476610441",
        "filename": "pin_05_business.png",
    },
    {
        "num": "3", "product": "CAR DETAILING JOB FORMS",
        "subtitle": "Condition Report, Checklist & Handover", "price": "£4.99",
        "source": "job-forms/car-detail/preview_grid.png",
        "etsy_url": "https://www.etsy.com/listing/4476913230",
        "filename": "pin_06_jobforms.png",
    },
    {
        "num": "4", "product": "CAR DETAILING FLYER PACK",
        "subtitle": "Print-Ready Marketing Flyers", "price": "£4.99",
        "source": "thumbnails/car-detail/v4/hero_flyer_pack_v4.png",
        "etsy_url": "https://www.etsy.com/listing/4476619330",
        "filename": "pin_07_flyers.png",
    },
    {
        "num": "8", "product": "CAR DETAILING CLIENT FORMS",
        "subtitle": "Professional Canva Templates", "price": "£4.99",
        "source": "thumbnails/car-detail/v3/hero_forms_bundle_v3.png",
        "etsy_url": "https://www.etsy.com/listing/4476619120",
        "filename": "pin_08_forms.png",
    },
]


def build_pin(pin, index):
    num = index + 1
    print(f"\n[{num}/8] {pin['product']}")

    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # ── Top section: number + TEMPLATES ──
    # Giant number
    f_num = font(180, bold=True)
    draw.text((60, 10), pin["num"], fill=WHITE, font=f_num)
    # "TEMPLATES" to the right, vertically centred in top band
    num_bbox = draw.textbbox((60, 10), pin["num"], font=f_num)
    num_right = num_bbox[2] + 30
    draw.text((num_right, 75), "CANVA", fill=ACCENT, font=font(40, bold=True))
    draw.text((num_right, 125), "TEMPLATES", fill=ACCENT, font=font(40, bold=True))

    # ── Middle section: source image with overlay ──
    try:
        src = fetch_image(pin["source"])
        # Crop/resize to 1000x900
        src_ratio = src.width / src.height
        target_ratio = 1000 / 900
        if src_ratio > target_ratio:
            new_h = src.height
            new_w = int(new_h * target_ratio)
            left = (src.width - new_w) // 2
            src = src.crop((left, 0, left + new_w, new_h))
        else:
            new_w = src.width
            new_h = int(new_w / target_ratio)
            top = (src.height - new_h) // 2
            src = src.crop((0, top, new_w, top + new_h))
        src = src.resize((1000, 900), Image.LANCZOS)
        src = dark_overlay(src, 0.3)
        img.paste(src, (0, 200))
        print(f"  Source image loaded: {pin['source']}")
    except Exception as e:
        print(f"  WARNING: Could not load source: {e}")
        draw.rectangle([0, 200, W, 1100], fill=(26, 26, 26))

    # Redraw over pasted image area
    draw = ImageDraw.Draw(img)

    # ── Bottom section ──
    draw.rectangle([0, 1100, W, H], fill=BG)

    # Product name - handle long names by splitting
    product = pin["product"]
    f_prod = font(44, bold=True)
    bbox = draw.textbbox((0, 0), product, font=f_prod)
    if bbox[2] - bbox[0] > W - 60:
        # Split into two lines
        words = product.split()
        mid = len(words) // 2
        line1 = " ".join(words[:mid])
        line2 = " ".join(words[mid:])
        centred(draw, 1120, line1, WHITE, f_prod)
        centred(draw, 1170, line2, WHITE, f_prod)
        sub_y = 1230
    else:
        centred(draw, 1140, product, WHITE, f_prod)
        sub_y = 1210

    # Subtitle
    centred(draw, sub_y, pin["subtitle"], ACCENT, font(30))

    # Red rule
    rule_y = sub_y + 55
    draw.rectangle([(W - 600) // 2, rule_y, (W + 600) // 2, rule_y + 4], fill=ACCENT)

    # Price
    centred(draw, rule_y + 20, pin["price"], WHITE, font(48, bold=True))

    # Red pill CTA
    draw_pill(draw, W // 2, 1390, 400, 54, ACCENT, "SHOP ON ETSY  ->", WHITE, 24)

    # Footer
    centred(draw, 1455, "purpleocaz.etsy.com", SILVER, font(20))

    path = OUTPUT_DIR / pin["filename"]
    img.save(path, "PNG")
    print(f"  Saved: {path.name}")
    return path


DESCRIPTIONS = [
    {
        "title": "50+ Car Detailing Templates | Complete Business Kit | Canva Editable",
        "desc": "Everything you need to run a professional car detailing business in one download. This mega bundle includes 50+ editable Canva templates across 7 categories: client intake forms, marketing flyers, Instagram social media posts, branding kit (business cards, letterhead, invoice), email marketing templates, and job forms. Perfect for mobile detailing businesses, auto detail shops, and car wash professionals. Edit everything in free Canva — add your logo, colours, and details in minutes. Print ready and digital-friendly. Instant download, no design skills needed. Start looking professional today. Shop now at ",
    },
    {
        "title": "20 Car Detailing Instagram Templates | Social Media Posts | Canva",
        "desc": "Level up your car detailing social media with 20 professional Instagram post templates. Designed for auto detailing businesses — promote your services, share before-and-after results, announce seasonal specials, and build your brand. Dark premium aesthetic with red accents that makes your detailing work pop. Each template is fully editable in free Canva. Just swap your photos, edit the text, and post. Perfect for mobile detailers, car wash businesses, and auto detail shops looking to grow their Instagram presence. Instant digital download. Shop now at ",
    },
    {
        "title": "Car Detailing Branding Kit | Business Card Invoice Letterhead | Canva",
        "desc": "Build a professional brand for your car detailing business with this 6-template branding kit. Includes business card (front and back), A4 letterhead, email signature, professional invoice, and thank you card. All designed in a sleek dark theme with red accents — perfect for auto detailing, mobile detailing, and car wash businesses. Every template is fully editable in free Canva. Add your logo, contact details, and brand colours in minutes. Print-ready quality. Instant digital download — start impressing clients today. Shop now at ",
    },
    {
        "title": "Car Detailing Email Templates | Booking Confirmation Review | Canva",
        "desc": "Automate your car detailing client communications with 6 professional email and text templates. Includes booking confirmation, appointment reminder, job completion with review request, 7-day follow-up, referral program ($25 give/get), and seasonal promotion. Perfect for mobile detailers and auto detail shops who want to look professional and get more 5-star reviews. Each template is fully editable in free Canva — just add your business details and send. Works for email, text message, or print. Instant digital download. Shop now at ",
    },
    {
        "title": "Car Detailing Business Bundle | 15 Canva Templates | Forms & Flyers",
        "desc": "Get your car detailing business organised with this 15-template bundle. Includes 8 professional client forms (intake, consent, service agreement, invoice, feedback, booking, aftercare, package menu), plus gift certificate, price list, loyalty card, and 4 marketing flyers. Everything a new or established detailing business needs to look professional from day one. All templates are fully editable in free Canva — add your logo, prices, and business details. Print-ready A4 format. Perfect for mobile detailing, auto detail shops, and car wash businesses. Instant download. Shop now at ",
    },
    {
        "title": "Car Detailing Job Forms | Vehicle Condition Report Checklist | Canva",
        "desc": "Protect your car detailing business with 3 essential job forms. Pre-detail vehicle condition report with damage map, comprehensive detailing job checklist for technicians (21 items across exterior, interior, and quality check), and post-detail customer handover form with payment summary and review request. Professional dark design with red accents. All editable in free Canva — add your business details and print. Essential for mobile detailers, auto detail shops, and any professional detailing operation. Instant digital download. Shop now at ",
    },
    {
        "title": "Car Detailing Flyer Pack | 4 Marketing Flyers | Canva Templates",
        "desc": "Market your car detailing business with 4 professional print-ready flyers. Includes promotional flyer, seasonal special, mobile service flyer, and walk-in special. Eye-catching dark design with red accents that stands out on bulletin boards, in mailboxes, and at local businesses. Each flyer is fully editable in free Canva — add your services, prices, contact details, and photos. A4 print-ready format. Perfect for mobile detailers, car wash businesses, and auto detail shops looking to attract new customers. Instant digital download. Shop now at ",
    },
    {
        "title": "Car Detailing Client Forms | 8 Professional Templates | Canva",
        "desc": "Run your car detailing business like a pro with 8 essential client forms. Vehicle intake form, consent waiver, service agreement, professional invoice, customer feedback form, appointment booking, aftercare instructions, and service package menu. Clean, professional design that builds trust with customers. All templates are fully editable in free Canva — customise with your business name, logo, services, and prices. Print-ready A4 format. Essential for mobile detailing, auto detail shops, and car wash professionals. Instant digital download. Shop now at ",
    },
]


def generate_descriptions():
    print("\n[DESC] Generating pin descriptions...")
    lines = []
    for i, pin in enumerate(PINS):
        d = DESCRIPTIONS[i]
        lines.append("---")
        lines.append(f"PIN {i+1}: {pin['product']}")
        lines.append(f"Title: {d['title']}")
        lines.append(f"Description: {d['desc']}{pin['etsy_url']}")
        lines.append(f"Board: Car Detailing Business Templates")
        lines.append("")

    path = OUTPUT_DIR / "pin_descriptions.txt"
    path.write_text("\n".join(lines))
    print(f"  Saved: {path.name}")
    return path


def build_preview_grid(paths):
    print("\n[GRID] Building 4x2 preview grid...")
    cols, rows = 4, 2
    tw, th = 250, 375
    pad = 20
    gw = cols * tw + (cols + 1) * pad
    gh = rows * th + (rows + 1) * pad
    grid = Image.new("RGB", (gw, gh), BG)
    for idx, p in enumerate(paths):
        r, c = divmod(idx, cols)
        thumb = Image.open(p).convert("RGB")
        thumb.thumbnail((tw, th), Image.LANCZOS)
        x = pad + c * (tw + pad) + (tw - thumb.width) // 2
        y = pad + r * (th + pad) + (th - thumb.height) // 2
        grid.paste(thumb, (x, y))
    out = OUTPUT_DIR / "preview_grid.png"
    grid.save(out, "PNG")
    print(f"  Saved: {out.name} ({gw}x{gh})")
    return out


def upload_to_spaces(paths):
    env = open("/root/NEW-AI-PROJECT/purpleocaz-canva-mcp/.env").read()
    key = re.search(r'DO_SPACES_KEY=(\S+)', env).group(1)
    secret = re.search(r'DO_SPACES_SECRET=(\S+)', env).group(1)
    s3 = boto3.client("s3", endpoint_url="https://lon1.digitaloceanspaces.com",
                      aws_access_key_id=key, aws_secret_access_key=secret)
    urls = {}
    for p in paths:
        sk = f"pinterest/car-detail/{p.name}"
        ct = "text/plain" if p.suffix == ".txt" else "image/png"
        print(f"  Uploading {p.name}")
        s3.put_object(Bucket="purpleocaz-assets", Key=sk,
                      Body=p.read_bytes(), ContentType=ct, ACL="public-read")
        urls[p.name] = f"{SPACES_BASE}/{sk}"
    return urls


def main():
    print("=" * 60)
    print("CAR DETAILING PINTEREST PINS — 8 Pins")
    print("=" * 60)

    paths = []
    for i, pin in enumerate(PINS):
        paths.append(build_pin(pin, i))

    desc_path = generate_descriptions()
    grid_path = build_preview_grid(paths)
    all_paths = paths + [desc_path, grid_path]

    print("\n" + "=" * 60)
    print("UPLOADING TO DO SPACES")
    print("=" * 60)
    urls = upload_to_spaces(all_paths)

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    for name, url in urls.items():
        size = (OUTPUT_DIR / name).stat().st_size
        print(f"  {name}: {size:,} bytes")

    return urls


if __name__ == "__main__":
    main()
