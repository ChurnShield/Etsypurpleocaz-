#!/usr/bin/env python3
"""
Car Detailing Branding Kit — 6 professional PNG templates.
Fetches photos from Unsplash, composites with Pillow.
Uploads to DO Spaces and builds a 3x2 preview grid.
"""

import os
import math
import requests
import boto3
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from dotenv import load_dotenv

# ── Paths ──────────────────────────────────────────────
PROJECT_ROOT = Path("/root/NEW-AI-PROJECT")
PHOTO_DIR = PROJECT_ROOT / "assets" / "photos" / "car-detail-branding"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "car-detail-branding"
PHOTO_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Fonts ──────────────────────────────────────────────
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"

# ── Colours ────────────────────────────────────────────
BG = (13, 13, 13)           # #0D0D0D
ACCENT = (224, 32, 32)      # #E02020
WHITE = (255, 255, 255)
SILVER = (192, 192, 192)    # #C0C0C0
PANEL_DARK = (26, 26, 26)   # #1A1A1A
BODY_WHITE = (255, 255, 255)
TABLE_ALT = (245, 245, 245) # #F5F5F5
GREY_PLACEHOLDER = (160, 160, 160)

# ── Unsplash photo fetcher ─────────────────────────────
# Map each template to an existing local photo
LOCAL_PHOTOS = {
    "bc_front": PROJECT_ROOT / "assets/photos/car_detailing_close_up_shine/photo_1.jpg",
    "letterhead": PROJECT_ROOT / "assets/photos/luxury_car_detailing_studio_interior/photo_1.jpg",
    "email_sig": PROJECT_ROOT / "assets/photos/car-detail-branding/email_sig_photo.jpg",
    "thankyou": PROJECT_ROOT / "assets/photos/shiny_clean_car_exterior/photo_1.jpg",
}

def fetch_photo(key: str, query: str = "", width: int = 1600) -> Image.Image:
    """Load photo from local assets (Unsplash source API is deprecated)."""
    cached = PHOTO_DIR / f"{key}.jpg"
    if cached.exists():
        print(f"  Using cached photo: {cached.name}")
        return Image.open(cached).convert("RGB")

    src = LOCAL_PHOTOS.get(key)
    if src and src.exists():
        print(f"  Using local photo: {src.name}")
        img = Image.open(src).convert("RGB")
        img.save(cached, quality=92)
        return img

    raise FileNotFoundError(f"No photo found for key '{key}'. Add to LOCAL_PHOTOS.")


def dark_overlay(img: Image.Image, opacity: float = 0.55) -> Image.Image:
    """Apply dark overlay to photo."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, int(255 * opacity)))
    base = img.convert("RGBA")
    return Image.alpha_composite(base, overlay).convert("RGB")


def font(size: int, bold: bool = False, italic: bool = False) -> ImageFont.FreeTypeFont:
    # Use serif for italic feel (no DejaVu Sans Oblique available)
    path = FONT_SERIF if italic else (FONT_BOLD if bold else FONT_REGULAR)
    return ImageFont.truetype(path, size)


def draw_pill(draw, x, y, w, h, fill, text, text_color, text_size, bold=True):
    """Draw a rounded pill button with centred text."""
    r = h // 2
    draw.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=fill)
    f = font(text_size, bold=bold)
    bbox = draw.textbbox((0, 0), text, font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((x + (w - tw) // 2, y + (h - th) // 2 - 2), text, fill=text_color, font=f)


def draw_outlined_rect(draw, x, y, w, h, outline_color, text=None, text_color=WHITE, text_size=14):
    """Draw an outlined rectangle, optionally with centred text."""
    draw.rectangle([x, y, x + w, y + h], outline=outline_color, width=2)
    if text:
        f = font(text_size, bold=False)
        bbox = draw.textbbox((0, 0), text, font=f)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text((x + (w - tw) // 2, y + (h - th) // 2), text, fill=text_color, font=f)


# ═══════════════════════════════════════════════════════
# TEMPLATE 1 — BUSINESS CARD FRONT (1050x600)
# ═══════════════════════════════════════════════════════
def build_bc_front():
    print("\n[1/6] Business Card Front")
    W, H = 1050, 600
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Right half: photo with overlay
    photo = fetch_photo("bc_front")
    photo = photo.resize((525, 600), Image.LANCZOS)
    photo = dark_overlay(photo, 0.5)
    img.paste(photo, (525, 0))

    # Red bars top + bottom
    draw.rectangle([0, 0, W, 8], fill=ACCENT)
    draw.rectangle([0, H - 8, W, H], fill=ACCENT)

    # Red vertical divider
    draw.rectangle([523, 0, 527, H], fill=ACCENT)

    # Left panel content
    # Logo placeholder
    draw_outlined_rect(draw, 40, 80, 120, 40, WHITE, "[YOUR LOGO]", WHITE, 11)

    # Studio name
    draw.text((40, 160), "YOUR STUDIO NAME", fill=WHITE, font=font(36, bold=True))

    # Subtitle
    draw.text((40, 210), "CAR DETAILING SPECIALIST", fill=ACCENT, font=font(18, bold=False))

    # White rule
    draw.rectangle([40, 245, 240, 247], fill=WHITE)

    # Contact info
    contacts = [
        ("  +1 (555) 000-0000", 275),
        ("  www.yourstudio.com", 300),
        ("  hello@yourstudio.com", 325),
        ("  Your City, State", 350),
    ]
    icons = ["Tel:", "Web:", "Mail:", "Loc:"]
    for i, (text, y) in enumerate(contacts):
        draw.text((40, y), icons[i], fill=ACCENT, font=font(12, bold=True))
        draw.text((85, y), text.strip(), fill=SILVER, font=font(14, bold=False))

    # Right panel: "Book Online" bottom right
    draw.text((720, 545), "Book Online:", fill=WHITE, font=font(12, italic=True))

    path = OUTPUT_DIR / "branding_01_bc_front.png"
    img.save(path, "PNG")
    print(f"  Saved: {path.name} ({W}x{H})")
    return path


# ═══════════════════════════════════════════════════════
# TEMPLATE 2 — BUSINESS CARD BACK (1050x600)
# ═══════════════════════════════════════════════════════
def build_bc_back():
    print("\n[2/6] Business Card Back")
    W, H = 1050, 600
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Subtle diagonal texture
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    for i in range(15):
        x_offset = i * 80 - 200
        odraw.line([(x_offset, 0), (x_offset + H, H)], fill=(255, 255, 255, 8), width=1)
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Red bars
    draw.rectangle([0, 0, W, 8], fill=ACCENT)
    draw.rectangle([0, H - 8, W, H], fill=ACCENT)

    # Logo placeholder centred
    draw_outlined_rect(draw, (W - 150) // 2, 130, 150, 50, WHITE, "[YOUR LOGO]", WHITE, 13)

    # Studio name centred
    f32 = font(32, bold=True)
    bbox = draw.textbbox((0, 0), "YOUR STUDIO NAME", font=f32)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, 230), "YOUR STUDIO NAME", fill=WHITE, font=f32)

    # Red rule
    draw.rectangle([(W - 300) // 2, 275, (W + 300) // 2, 278], fill=ACCENT)

    # "OUR SERVICES"
    f14 = font(14, bold=False)
    bbox = draw.textbbox((0, 0), "OUR SERVICES", font=f14)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, 295), "OUR SERVICES", fill=SILVER, font=f14)

    # Services list
    services = [
        "Exterior Detailing  ·  Interior Detailing",
        "Paint Correction  ·  Ceramic Coating",
        "Engine Bay  ·  Mobile Service",
    ]
    f13 = font(13, bold=False)
    y = 325
    for svc in services:
        bbox = draw.textbbox((0, 0), svc, font=f13)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) // 2, y), svc, fill=WHITE, font=f13)
        y += 30

    # Red pill button
    draw_pill(draw, (W - 340) // 2, 440, 340, 44, ACCENT,
              "BOOK YOUR DETAIL TODAY", WHITE, 14, bold=True)

    path = OUTPUT_DIR / "branding_02_bc_back.png"
    img.save(path, "PNG")
    print(f"  Saved: {path.name} ({W}x{H})")
    return path


# ═══════════════════════════════════════════════════════
# TEMPLATE 3 — LETTERHEAD (2480x3508 A4)
# ═══════════════════════════════════════════════════════
def build_letterhead():
    print("\n[3/6] Letterhead")
    W, H = 2480, 3508
    img = Image.new("RGB", (W, H), BODY_WHITE)
    draw = ImageDraw.Draw(img)

    # Header band with photo
    photo = fetch_photo("letterhead")
    photo = photo.resize((W, 320), Image.LANCZOS)
    photo = dark_overlay(photo, 0.7)
    img.paste(photo, (0, 0))
    draw = ImageDraw.Draw(img)

    # Header text
    f72 = font(72, bold=True)
    bbox = draw.textbbox((0, 0), "YOUR STUDIO NAME", font=f72)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, 120), "YOUR STUDIO NAME", fill=WHITE, font=f72)

    f36 = font(36, bold=False)
    bbox = draw.textbbox((0, 0), "CAR DETAILING SPECIALIST", font=f36)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, 210), "CAR DETAILING SPECIALIST", fill=ACCENT, font=f36)

    contact_line = "+1 (555) 000-0000  |  www.yourstudio.com  |  Your City, State"
    f24 = font(24, bold=False)
    bbox = draw.textbbox((0, 0), contact_line, font=f24)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, 270), contact_line, fill=SILVER, font=f24)

    # Red rule at y=320
    draw.rectangle([0, 320, W, 326], fill=ACCENT)

    # Thin red left margin line
    draw.rectangle([180, 350, 183, 3100], fill=ACCENT)

    # Placeholder content
    f28_grey = font(28, bold=False)
    placeholder = "[YOUR CONTENT HERE]"
    bbox = draw.textbbox((0, 0), placeholder, font=f28_grey)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, 1800), placeholder, fill=GREY_PLACEHOLDER, font=f28_grey)

    # Footer band
    draw.rectangle([0, 3200, W, H], fill=BG)
    f28i = font(28, italic=True)
    text = "Thank you for your business"
    bbox = draw.textbbox((0, 0), text, font=f28i)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, 3300), text, fill=WHITE, font=f28i)

    f22 = font(22, bold=False)
    text = "YOUR STUDIO NAME  ·  www.yourstudio.com"
    bbox = draw.textbbox((0, 0), text, font=f22)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, 3370), text, fill=SILVER, font=f22)

    path = OUTPUT_DIR / "branding_03_letterhead.png"
    img.save(path, "PNG")
    print(f"  Saved: {path.name} ({W}x{H})")
    return path


# ═══════════════════════════════════════════════════════
# TEMPLATE 4 — EMAIL SIGNATURE (1800x450)
# ═══════════════════════════════════════════════════════
def build_email_signature():
    print("\n[4/6] Email Signature")
    W, H = 1800, 450
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # LEFT third: photo
    photo = fetch_photo("email_sig")
    photo = photo.resize((600, H), Image.LANCZOS)
    photo = dark_overlay(photo, 0.6)
    img.paste(photo, (0, 0))
    draw = ImageDraw.Draw(img)

    # RIGHT panel: #1A1A1A
    draw.rectangle([1300, 0, W, H], fill=PANEL_DARK)

    # Red left + right borders
    draw.rectangle([0, 0, 8, H], fill=ACCENT)
    draw.rectangle([W - 8, 0, W, H], fill=ACCENT)

    # CENTRE panel content
    cx = 950  # centre of 600-1300 range
    draw_outlined_rect(draw, cx - 60, 100, 120, 40, WHITE, "[YOUR LOGO]", WHITE, 11)

    f38 = font(38, bold=True)
    text = "YOUR STUDIO NAME"
    bbox = draw.textbbox((0, 0), text, font=f38)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, 170), text, fill=WHITE, font=f38)

    f22 = font(22, bold=False)
    text = "CAR DETAILING SPECIALIST"
    bbox = draw.textbbox((0, 0), text, font=f22)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, 225), text, fill=ACCENT, font=f22)

    # Silver rule
    draw.rectangle([cx - 150, 265, cx + 150, 267], fill=SILVER)

    f20 = font(20, bold=False)
    text = "+1 (555) 000-0000 | www.yourstudio.com"
    bbox = draw.textbbox((0, 0), text, font=f20)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, 290), text, fill=SILVER, font=f20)

    # RIGHT panel content
    rx = 1550  # centre of 1300-1800
    draw_pill(draw, rx - 120, 140, 240, 56, ACCENT, "BOOK NOW", WHITE, 22, bold=True)

    f18 = font(18, bold=False)
    checks = ["  Mobile Service", "  Free Quotes", "  5-Star Results"]
    y = 230
    for chk in checks:
        draw.text((rx - 80, y), chk, fill=WHITE, font=f18)
        y += 35

    path = OUTPUT_DIR / "branding_04_email_sig.png"
    img.save(path, "PNG")
    print(f"  Saved: {path.name} ({W}x{H})")
    return path


# ═══════════════════════════════════════════════════════
# TEMPLATE 5 — INVOICE (2480x3508 A4)
# ═══════════════════════════════════════════════════════
def build_invoice():
    print("\n[5/6] Invoice")
    W, H = 2480, 3508
    img = Image.new("RGB", (W, H), BODY_WHITE)
    draw = ImageDraw.Draw(img)

    # Header band
    draw.rectangle([0, 0, W, 380], fill=BG)

    # Studio name + subtitle
    draw.text((180, 100), "YOUR STUDIO NAME", fill=WHITE, font=font(72, bold=True))
    draw.text((180, 190), "CAR DETAILING SPECIALIST", fill=ACCENT, font=font(34, bold=False))
    draw.text((180, 250), "+1 (555) 000-0000  |  www.yourstudio.com  |  Your City, State",
              fill=SILVER, font=font(24, bold=False))

    # INVOICE title right-aligned
    f96 = font(96, bold=True)
    bbox = draw.textbbox((0, 0), "INVOICE", font=f96)
    tw = bbox[2] - bbox[0]
    draw.text((W - 180 - tw, 100), "INVOICE", fill=WHITE, font=f96)

    # Red outlined box for invoice details
    draw.rectangle([1800, 220, 2300, 360], outline=ACCENT, width=2)
    f22 = font(22, bold=False)
    draw.text((1820, 235), "Invoice #:  INV-0001", fill=WHITE, font=f22)
    draw.text((1820, 270), "Date:         MM/DD/YYYY", fill=WHITE, font=f22)
    draw.text((1820, 305), "Due:          MM/DD/YYYY", fill=WHITE, font=f22)

    # Red rule
    draw.rectangle([0, 380, W, 386], fill=ACCENT)

    # BILL TO section
    draw.text((180, 420), "BILL TO:", fill=ACCENT, font=font(28, bold=True))
    f22g = font(22, bold=False)
    draw.text((180, 465), "Client Name", fill=GREY_PLACEHOLDER, font=f22g)
    draw.text((180, 495), "123 Client Street", fill=GREY_PLACEHOLDER, font=f22g)
    draw.text((180, 525), "City, State ZIP", fill=GREY_PLACEHOLDER, font=f22g)

    # VEHICLE DETAILS
    draw.text((180, 590), "VEHICLE DETAILS:", fill=ACCENT, font=font(28, bold=True))
    draw.text((180, 635), "Make / Model:   ________________", fill=GREY_PLACEHOLDER, font=f22g)
    draw.text((180, 665), "Year:                  ________________", fill=GREY_PLACEHOLDER, font=f22g)
    draw.text((180, 695), "Color:                ________________", fill=GREY_PLACEHOLDER, font=f22g)

    # Services table
    table_x = 140
    table_w = W - 280
    col_widths = [800, 600, 200, 300, 300]  # SERVICE, DESCRIPTION, QTY, PRICE, TOTAL
    headers = ["SERVICE", "DESCRIPTION", "QTY", "PRICE", "TOTAL"]

    # Header row
    ty = 790
    draw.rectangle([table_x, ty, table_x + table_w, ty + 60], fill=BG)
    hx = table_x + 20
    f20b = font(20, bold=True)
    for i, header in enumerate(headers):
        draw.text((hx, ty + 18), header, fill=WHITE, font=f20b)
        hx += col_widths[i]

    # Data rows (5 alternating)
    row_h = 120
    f20 = font(20, bold=False)
    for r in range(5):
        ry = ty + 60 + r * row_h
        bg_color = BODY_WHITE if r % 2 == 0 else TABLE_ALT
        draw.rectangle([table_x, ry, table_x + table_w, ry + row_h], fill=bg_color)
        draw.rectangle([table_x, ry, table_x + table_w, ry + row_h], outline=(220, 220, 220), width=1)
        if r == 0:
            rx = table_x + 20
            placeholders = ["Exterior Detail", "Full wash & polish", "1", "$150.00", "$150.00"]
            for i, p in enumerate(placeholders):
                draw.text((rx, ry + 45), p, fill=GREY_PLACEHOLDER, font=f20)
                rx += col_widths[i]

    # Totals section
    total_x = table_x + table_w - 500
    ty2 = 2400
    draw.text((total_x, ty2), "Subtotal:", fill=BG, font=font(28, bold=False))
    draw.text((total_x + 300, ty2), "$0.00", fill=BG, font=font(28, bold=False))
    draw.text((total_x, ty2 + 50), "Tax (8%):", fill=BG, font=font(28, bold=False))
    draw.text((total_x + 300, ty2 + 50), "$0.00", fill=BG, font=font(28, bold=False))
    draw.rectangle([total_x, ty2 + 90, total_x + 500, ty2 + 92], fill=ACCENT)
    draw.text((total_x, ty2 + 110), "TOTAL:", fill=ACCENT, font=font(40, bold=True))
    draw.text((total_x + 250, ty2 + 110), "$0.00", fill=ACCENT, font=font(40, bold=True))

    # Footer
    draw.rectangle([0, 3100, W, H], fill=BG)
    f28 = font(28, bold=False)
    text = "Thank you for choosing YOUR STUDIO NAME"
    bbox = draw.textbbox((0, 0), text, font=f28)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, 3200), text, fill=WHITE, font=f28)

    f22s = font(22, bold=False)
    terms = "Payment due within 30 days  |  Please include invoice number with payment"
    bbox = draw.textbbox((0, 0), terms, font=f22s)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, 3280), terms, fill=SILVER, font=f22s)

    contact = "+1 (555) 000-0000  |  hello@yourstudio.com  |  www.yourstudio.com"
    bbox = draw.textbbox((0, 0), contact, font=f22s)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, 3340), contact, fill=SILVER, font=f22s)

    path = OUTPUT_DIR / "branding_05_invoice.png"
    img.save(path, "PNG")
    print(f"  Saved: {path.name} ({W}x{H})")
    return path


# ═══════════════════════════════════════════════════════
# TEMPLATE 6 — THANK YOU CARD (1050x600)
# ═══════════════════════════════════════════════════════
def build_thankyou():
    print("\n[6/6] Thank You Card")
    W, H = 1050, 600
    img_bg = fetch_photo("thankyou")
    img_bg = img_bg.resize((W, H), Image.LANCZOS)
    img_bg = dark_overlay(img_bg, 0.65)
    img = img_bg
    draw = ImageDraw.Draw(img)

    # Red bars
    draw.rectangle([0, 0, W, 8], fill=ACCENT)
    draw.rectangle([0, H - 8, W, H], fill=ACCENT)

    # THANK YOU
    f72 = font(72, bold=True)
    text = "THANK YOU"
    bbox = draw.textbbox((0, 0), text, font=f72)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, 120), text, fill=WHITE, font=f72)

    # Red rule
    draw.rectangle([(W - 400) // 2, 210, (W + 400) // 2, 214], fill=ACCENT)

    # "for choosing"
    f30i = font(30, italic=True)
    text = "for choosing"
    bbox = draw.textbbox((0, 0), text, font=f30i)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, 240), text, fill=WHITE, font=f30i)

    # Studio name in red
    f48 = font(48, bold=True)
    text = "YOUR STUDIO NAME"
    bbox = draw.textbbox((0, 0), text, font=f48)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, 290), text, fill=ACCENT, font=f48)

    # Silver rule
    draw.rectangle([(W - 300) // 2, 360, (W + 300) // 2, 362], fill=SILVER)

    # Review text
    f22i = font(22, italic=True)
    text = "We'd love your review"
    bbox = draw.textbbox((0, 0), text, font=f22i)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, 385), text, fill=SILVER, font=f22i)

    # QR code placeholder
    qr_size = 100
    qr_x = (W - qr_size) // 2
    qr_y = 425
    draw_outlined_rect(draw, qr_x, qr_y, qr_size, qr_size, WHITE, "[QR CODE]", WHITE, 12)

    # Handle
    f18 = font(18, bold=False)
    text = "@yourstudioname"
    bbox = draw.textbbox((0, 0), text, font=f18)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, 540), text, fill=SILVER, font=f18)

    path = OUTPUT_DIR / "branding_06_thankyou.png"
    img.save(path, "PNG")
    print(f"  Saved: {path.name} ({W}x{H})")
    return path


# ═══════════════════════════════════════════════════════
# PREVIEW GRID (3x2)
# ═══════════════════════════════════════════════════════
def build_preview_grid(paths: list[Path]) -> Path:
    print("\n[GRID] Building 3x2 preview grid...")
    cols, rows = 3, 2
    thumb_w, thumb_h = 800, 500
    pad = 40
    grid_w = cols * thumb_w + (cols + 1) * pad
    grid_h = rows * thumb_h + (rows + 1) * pad
    grid = Image.new("RGB", (grid_w, grid_h), BG)

    for idx, p in enumerate(paths):
        r, c = divmod(idx, cols)
        thumb = Image.open(p).convert("RGB")
        thumb.thumbnail((thumb_w, thumb_h), Image.LANCZOS)
        # Centre within cell
        x = pad + c * (thumb_w + pad) + (thumb_w - thumb.width) // 2
        y = pad + r * (thumb_h + pad) + (thumb_h - thumb.height) // 2
        grid.paste(thumb, (x, y))

    out = OUTPUT_DIR / "preview_grid.png"
    grid.save(out, "PNG")
    print(f"  Saved: {out.name} ({grid_w}x{grid_h})")
    return out


# ═══════════════════════════════════════════════════════
# DO SPACES UPLOAD
# ═══════════════════════════════════════════════════════
def upload_to_spaces(paths: list[Path]) -> dict[str, str]:
    """Upload files to DO Spaces. Returns {filename: url}."""
    load_dotenv("/root/NEW-AI-PROJECT/purpleocaz-canva-mcp/.env")
    s3 = boto3.client(
        "s3",
        region_name="lon1",
        endpoint_url="https://lon1.digitaloceanspaces.com",
        aws_access_key_id=os.getenv("DO_SPACES_KEY"),
        aws_secret_access_key=os.getenv("DO_SPACES_SECRET"),
    )
    bucket = "purpleocaz-assets"
    urls = {}
    for p in paths:
        key = f"branding/car-detail/{p.name}"
        print(f"  Uploading {p.name} → {key}")
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=p.read_bytes(),
            ContentType="image/png",
            ACL="public-read",
        )
        url = f"https://purpleocaz-assets.lon1.digitaloceanspaces.com/{key}"
        urls[p.name] = url
    return urls


# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════
def main():
    print("=" * 60)
    print("CAR DETAILING BRANDING KIT — 6 Templates")
    print("=" * 60)

    paths = []
    paths.append(build_bc_front())
    paths.append(build_bc_back())
    paths.append(build_letterhead())
    paths.append(build_email_signature())
    paths.append(build_invoice())
    paths.append(build_thankyou())

    grid_path = build_preview_grid(paths)
    all_paths = paths + [grid_path]

    print("\n" + "=" * 60)
    print("UPLOADING TO DO SPACES")
    print("=" * 60)
    urls = upload_to_spaces(all_paths)

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    for name, url in urls.items():
        size = Path(OUTPUT_DIR / name).stat().st_size
        print(f"  {name}: {size:,} bytes → {url}")

    return urls


if __name__ == "__main__":
    main()
