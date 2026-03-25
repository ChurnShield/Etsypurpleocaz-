#!/usr/bin/env python3
"""
Barbershop Utility Cards — 4 templates.
Design system: #1A1A1A bg, #C9A96E gold, #FFFFFF white, #888888 grey.

Cards:
 01 — Google Review Card     A6 landscape 1240x874  (print & hand to customer)
 02 — Grooming Tip Guide     A5 portrait  874x1240  (take-home / display)
 03 — Price List Card        A5 portrait  874x1240  (counter display / printable)
 04 — Aftercare Advice Card  A6 landscape 1240x874  (hand out after every cut)
"""

import os, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import boto3
from dotenv import load_dotenv

PROJECT_ROOT = Path("/root/NEW-AI-PROJECT")
OUTPUT_DIR   = PROJECT_ROOT / "outputs" / "barbershop" / "utility"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FONT_BOLD   = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG    = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SERIF  = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_SERIFB = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

BG    = (26, 26, 26)
DARK  = (10, 10, 10)
PANEL = (38, 38, 38)
GOLD  = (201, 169, 110)
WHITE = (255, 255, 255)
GREY  = (136, 136, 136)
CREAM = (255, 253, 245)
DARK_TEXT = (26, 26, 26)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def font(size, bold=False, serif=False, serifbold=False):
    if serifbold: return ImageFont.truetype(FONT_SERIFB, size)
    if serif:     return ImageFont.truetype(FONT_SERIF,  size)
    if bold:      return ImageFont.truetype(FONT_BOLD,   size)
    return ImageFont.truetype(FONT_REG, size)


def cx(draw, y, text, fill, f, canvas_w=None):
    if canvas_w is None:
        # auto-detect from draw image — fallback to large number
        canvas_w = 9999
    bb = draw.textbbox((0, 0), text, font=f)
    draw.text(((canvas_w - (bb[2] - bb[0])) // 2, y), text, fill=fill, font=f)


def gold_bar(draw, y, h=3, x0=0, x1=None, canvas_w=None):
    if x1 is None:
        x1 = canvas_w or 9999
    draw.rectangle([x0, y, x1, y + h], fill=GOLD)


def scissors(draw, x, y, size=30):
    draw.line([(x - size, y - size // 2), (x + size, y + size // 2)],
              fill=GOLD, width=6)
    draw.line([(x + size, y - size // 2), (x - size, y + size // 2)],
              fill=GOLD, width=6)
    for ex, ey in [(x - size, y - size // 2), (x + size, y - size // 2),
                   (x - size, y + size // 2), (x + size, y + size // 2)]:
        draw.ellipse([ex - 8, ey - 8, ex + 8, ey + 8], outline=GOLD, width=3)


def star_row(draw, cx_pos, y, count=5, r=18):
    spacing = r * 2 + 10
    total = count * (r * 2) + (count - 1) * 10
    sx = cx_pos - total // 2
    for i in range(count):
        sc = sx + i * (r * 2 + 10) + r
        pts = []
        for p in range(10):
            angle = math.pi * p / 5 - math.pi / 2
            rr = r if p % 2 == 0 else r // 2
            pts.append((sc + rr * math.cos(angle), y + rr * math.sin(angle)))
        draw.polygon(pts, fill=GOLD)


def qr_placeholder(draw, x, y, size, label="QR Code"):
    """Draw a QR-code placeholder box."""
    draw.rectangle([x, y, x + size, y + size], fill=CREAM, outline=GOLD, width=3)
    # Corner squares (QR style)
    sq = size // 6
    for cx2, cy2 in [(x + 10, y + 10), (x + size - 10 - sq * 2, y + 10),
                     (x + 10, y + size - 10 - sq * 2)]:
        draw.rectangle([cx2, cy2, cx2 + sq * 2, cy2 + sq * 2],
                       fill=DARK_TEXT, outline=DARK_TEXT)
        draw.rectangle([cx2 + 6, cy2 + 6, cx2 + sq * 2 - 6, cy2 + sq * 2 - 6],
                       fill=CREAM)
    # Dots grid
    dot_s = size // 16
    for row in range(3, 11):
        for col in range(3, 11):
            if (row + col) % 2 == 0:
                dx2 = x + col * (size // 12)
                dy2 = y + row * (size // 12)
                draw.rectangle([dx2, dy2, dx2 + dot_s, dy2 + dot_s],
                                fill=DARK_TEXT)
    # Label
    bb = draw.textbbox((0, 0), label, font=font(12))
    draw.text((x + (size - (bb[2] - bb[0])) // 2, y + size + 8),
              label, fill=GREY, font=font(12))


def save(img, name):
    out = OUTPUT_DIR / name
    img.save(str(out), "PNG")
    print(f"  Saved: {out.name}")
    return out


# ─── CARD 01 — Google Review Card  (A6 landscape 1240x874) ───────────────────

def card_01_google_review():
    W, H = 1240, 874
    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Gold top & bottom bars
    draw.rectangle([0, 0, W, 6], fill=GOLD)
    draw.rectangle([0, H - 6, W, H], fill=GOLD)
    draw.rectangle([12, 12, W - 12, H - 12], outline=GOLD, width=2)

    # Left column — ask content
    col_split = 740
    lx = 50

    # Shop identity
    scissors(draw, lx + 30, 70, size=22)
    draw.text((lx + 65, 50), "YOUR BARBERSHOP NAME", fill=GOLD,
              font=font(18, bold=True))
    draw.text((lx + 65, 78), "Master Barbers · Est. 2015", fill=GREY, font=font(13))
    gold_bar(draw, 110, x0=lx, x1=col_split - 20, canvas_w=W)

    # Stars
    star_row(draw, (lx + col_split - 20) // 2, 138, count=5, r=22)

    draw.text((lx, 195), "Enjoyed your visit?", fill=WHITE, font=font(24, bold=True))
    draw.text((lx, 228), "Please leave us a", fill=WHITE, font=font(22))

    # "5-star review" highlight
    highlight_y = 264
    draw.rounded_rectangle([lx, highlight_y, lx + 360, highlight_y + 52],
                            radius=10, fill=GOLD)
    draw.text((lx + 20, highlight_y + 12), "5-STAR GOOGLE REVIEW",
              fill=DARK, font=font(20, bold=True))

    draw.text((lx, 334), "It takes less than 60 seconds", fill=GREY, font=font(16))
    draw.text((lx, 360), "and means the world to us.", fill=GREY, font=font(16))

    gold_bar(draw, 400, x0=lx, x1=col_split - 20, canvas_w=W)

    steps = [
        "1. Open your camera & scan the QR code",
        "2. Tap the Google review link",
        "3. Leave an honest review — thank you!",
    ]
    sy = 416
    for step in steps:
        draw.ellipse([lx, sy + 4, lx + 14, sy + 18], fill=GOLD)
        draw.text((lx + 24, sy), step, fill=WHITE, font=font(15))
        sy += 36

    gold_bar(draw, sy + 14, x0=lx, x1=col_split - 20, canvas_w=W)
    draw.text((lx, sy + 30), "+1 (555) 000-0000", fill=WHITE, font=font(16))
    draw.text((lx, sy + 56), "www.yourbarbershop.com", fill=GOLD, font=font(15))
    draw.text((lx, sy + 80), "@yourbarbershop", fill=GREY, font=font(14))

    # Divider
    draw.rectangle([col_split, 30, col_split + 2, H - 30], fill=GOLD)

    # Right column — QR code
    rx = col_split + 30
    rw = W - col_split - 50
    qr_size = 200
    qr_x = rx + (rw - qr_size) // 2
    qr_y = 60

    draw.text((rx, qr_y), "SCAN TO REVIEW", fill=WHITE, font=font(16, bold=True))
    qr_placeholder(draw, qr_x - 10, qr_y + 30, qr_size,
                   label="Paste your Google review link")

    # Google logo placeholder
    logo_y = qr_y + qr_size + 80
    draw.rounded_rectangle([rx, logo_y, W - 30, logo_y + 60],
                            radius=8, fill=PANEL, outline=GREY, width=1)
    draw.text((rx + 14, logo_y + 16), "G  Google Reviews", fill=WHITE,
              font=font(18, bold=True))

    draw.text((rx, logo_y + 80), "Replace QR above with your", fill=GREY, font=font(13))
    draw.text((rx, logo_y + 100), "actual Google review QR code.", fill=GREY, font=font(13))

    # Thank you
    ty_y = logo_y + 150
    gold_bar(draw, ty_y, x0=rx, x1=W - 30, canvas_w=W)
    draw.text((rx, ty_y + 14), "Thank you for", fill=WHITE, font=font(16))
    draw.text((rx, ty_y + 38), "your support!", fill=GOLD, font=font(18, bold=True))

    return save(img, "barber_util_01_google_review.png")


# ─── CARD 02 — Grooming Tip Guide  (A5 portrait 874x1240) ────────────────────

def card_02_tip_guide():
    W, H = 874, 1240
    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, W, 6], fill=GOLD)
    draw.rectangle([0, H - 6, W, H], fill=GOLD)
    draw.rectangle([14, 14, W - 14, H - 14], outline=GOLD, width=2)

    # Header
    scissors(draw, W // 2, 68, size=28)
    cx(draw, 112, "GROOMING GUIDE", WHITE, font(32, bold=True), W)
    cx(draw, 156, "YOUR BARBERSHOP NAME", GOLD, font(16, bold=True), W)
    gold_bar(draw, 192, x0=40, x1=W - 40)

    # Sections
    sections = [
        {
            "title": "DAILY ROUTINE",
            "colour": GOLD,
            "tips": [
                ("Brush",   "Use a soft-bristle brush to train\nhair direction & remove product."),
                ("Moisturise", "Apply a light face moisturiser\ndaily — healthy skin = better fades."),
                ("Style",   "Matte clay for textured looks.\nPomade for shine. Less is more."),
            ],
        },
        {
            "title": "WEEKLY CARE",
            "colour": WHITE,
            "tips": [
                ("Shampoo", "Wash 2–3x per week max.\nOver-washing strips natural oils."),
                ("Condition", "Use conditioner on hair only,\nnot the scalp. Rinse thoroughly."),
                ("Scalp oil", "Massage in a light scalp oil\nto prevent dryness & flaking."),
            ],
        },
        {
            "title": "MONTHLY MAINTENANCE",
            "colour": GOLD,
            "tips": [
                ("Trim",    "Book every 2–3 weeks to\nkeep your fade looking sharp."),
                ("Beard",   "Shape your beard monthly\nor ask us to tidy it each visit."),
            ],
        },
    ]

    ty = 212
    for sec in sections:
        # Section heading
        draw.rounded_rectangle([36, ty, W - 36, ty + 40],
                                radius=6, fill=PANEL)
        draw.text((52, ty + 8), sec["title"], fill=sec["colour"],
                  font=font(18, bold=True))
        ty += 50

        for icon_label, body in sec["tips"]:
            # Label pill
            draw.rounded_rectangle([52, ty, 180, ty + 32],
                                    radius=6, fill=GOLD)
            bb = draw.textbbox((0, 0), icon_label, font=font(14, bold=True))
            draw.text((52 + (128 - (bb[2] - bb[0])) // 2, ty + 7),
                      icon_label, fill=DARK, font=font(14, bold=True))
            # Body
            for j, line in enumerate(body.split("\n")):
                draw.text((196, ty + 2 + j * 22), line, fill=WHITE, font=font(14))
            ty += 66
            gold_bar(draw, ty - 8, h=1, x0=52, x1=W - 52)

        ty += 14

    gold_bar(draw, ty, x0=36, x1=W - 36)
    cx(draw, ty + 14, "Products recommended in-shop · Ask your barber", GREY, font(14), W)

    # Footer
    footer_y = H - 90
    gold_bar(draw, footer_y, x0=36, x1=W - 36)
    cx(draw, footer_y + 14, "YOUR BARBERSHOP NAME", WHITE, font(16, bold=True), W)
    cx(draw, footer_y + 40, "+1 (555) 000-0000  ·  www.yourbarbershop.com", GOLD, font(13), W)

    return save(img, "barber_util_02_tip_guide.png")


# ─── CARD 03 — Price List Card  (A5 portrait 874x1240) ───────────────────────

def card_03_price_list():
    W, H = 874, 1240
    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, W, 6], fill=GOLD)
    draw.rectangle([0, H - 6, W, H], fill=GOLD)
    draw.rectangle([14, 14, W - 14, H - 14], outline=GOLD, width=2)

    # Header
    scissors(draw, W // 2, 66, size=28)
    cx(draw, 110, "PRICE LIST", WHITE, font(38, bold=True), W)
    cx(draw, 160, "YOUR BARBERSHOP NAME", GOLD, font(16, bold=True), W)
    draw.text((36, 196), "Est. 2015  ·  Master Barbers", fill=GREY, font=font(13))
    draw.text((W - 36 - draw.textbbox((0, 0), "Updated 2025", font=font(13))[2],
               196), "Updated 2025", fill=GREY, font=font(13))
    gold_bar(draw, 218, x0=36, x1=W - 36)

    categories = [
        {
            "name": "HAIRCUTS",
            "items": [
                ("Classic Haircut",         "£18"),
                ("Skin Fade / Taper Fade",  "£22"),
                ("Shape-Up / Line-Up",      "£10"),
                ("Kid's Cut (under 12)",    "£14"),
                ("Senior Cut (60+)",        "£14"),
            ],
        },
        {
            "name": "BEARD & SHAVE",
            "items": [
                ("Beard Trim & Shape",      "£12"),
                ("Hot Towel Wet Shave",     "£20"),
                ("Beard Design",            "£15"),
            ],
        },
        {
            "name": "COMBOS",
            "items": [
                ("Cut & Beard Trim",        "£28"),
                ("Cut & Hot Towel Shave",   "£36"),
                ("Full Groom Package",      "£45"),
            ],
        },
        {
            "name": "TREATMENTS",
            "items": [
                ("Scalp Treatment",         "£15"),
                ("Grey Blending",           "£20"),
                ("Hair Design / Art",       "from £8"),
            ],
        },
    ]

    cy = 234
    for cat in categories:
        # Category header
        draw.rectangle([36, cy, W - 36, cy + 36], fill=PANEL)
        draw.text((50, cy + 8), cat["name"], fill=GOLD, font=font(16, bold=True))
        cy += 44

        for name, price in cat["items"]:
            # Dotted rule between label and price
            draw.text((50, cy + 4), name, fill=WHITE, font=font(17))
            bb = draw.textbbox((0, 0), price, font=font(17, bold=True))
            draw.text((W - 50 - (bb[2] - bb[0]), cy + 4),
                      price, fill=GOLD, font=font(17, bold=True))
            # Dot leader
            name_bb = draw.textbbox((0, 0), name, font=font(17))
            price_bb = draw.textbbox((0, 0), price, font=font(17, bold=True))
            lx2 = 50 + (name_bb[2] - name_bb[0]) + 8
            rx2 = W - 50 - (price_bb[2] - price_bb[0]) - 8
            dot_x = lx2
            while dot_x < rx2 - 6:
                draw.rectangle([dot_x, cy + 16, dot_x + 3, cy + 17], fill=GREY)
                dot_x += 10
            cy += 36

        gold_bar(draw, cy + 2, h=1, x0=36, x1=W - 36)
        cy += 16

    # Note
    cx(draw, cy + 4, "Prices from — may vary by length & style", GREY, font(13), W)
    cx(draw, cy + 24, "Prices correct as of 2025 · Subject to change", GREY, font(12), W)

    # Walk-in / booking section
    wb_y = cy + 56
    draw.rounded_rectangle([36, wb_y, W - 36, wb_y + 80],
                            radius=10, fill=PANEL, outline=GOLD, width=2)
    cx(draw, wb_y + 10, "Walk-ins Welcome  ·  Appointments Preferred",
       WHITE, font(15, bold=True), W)
    cx(draw, wb_y + 38, "Book: +1 (555) 000-0000  ·  @yourbarbershop",
       GOLD, font(14), W)

    # Footer
    footer_y = H - 80
    gold_bar(draw, footer_y, x0=36, x1=W - 36)
    cx(draw, footer_y + 14, "123 Main Street, Your City", WHITE, font(14), W)
    cx(draw, footer_y + 40, "www.yourbarbershop.com", GOLD, font(13), W)

    return save(img, "barber_util_03_price_list.png")


# ─── CARD 04 — Aftercare Advice Card  (A6 landscape 1240x874) ────────────────

def card_04_aftercare():
    W, H = 1240, 874
    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, W, 6], fill=GOLD)
    draw.rectangle([0, H - 6, W, H], fill=GOLD)
    draw.rectangle([12, 12, W - 12, H - 12], outline=GOLD, width=2)

    # Left col: content
    col_split = 720
    lx = 44

    # Header
    scissors(draw, lx + 28, 62, size=20)
    draw.text((lx + 60, 44), "AFTERCARE ADVICE", fill=WHITE, font=font(20, bold=True))
    draw.text((lx + 60, 74), "YOUR BARBERSHOP NAME", fill=GOLD, font=font(13, bold=True))
    gold_bar(draw, 106, x0=lx, x1=col_split - 20)

    cx_left = (lx + col_split - 20) // 2
    draw.text((lx, 120), "Your fresh cut deserves the right care.", fill=WHITE,
              font=font(16))
    draw.text((lx, 146), "Follow these steps to keep it sharp:", fill=GREY,
              font=font(14))

    gold_bar(draw, 176, h=1, x0=lx, x1=col_split - 20)

    tips = [
        ("TODAY",      [
            "Avoid touching your hair excessively",
            "No heavy products for 24 hours",
            "Keep scalp dry if possible",
        ]),
        ("THIS WEEK",  [
            "Brush in the direction of your style",
            "Use light product only (matte clay)",
            "Wash 2–3x max — not daily",
        ]),
        ("ONGOING",    [
            "Moisturise your scalp 2–3x per week",
            "Book your next trim in 2–3 weeks",
            "DM us with any questions anytime",
        ]),
    ]

    ty = 192
    for period, items in tips:
        draw.rounded_rectangle([lx, ty, lx + 120, ty + 26],
                                radius=6, fill=GOLD)
        bb = draw.textbbox((0, 0), period, font=font(13, bold=True))
        draw.text((lx + (120 - (bb[2] - bb[0])) // 2, ty + 5),
                  period, fill=DARK, font=font(13, bold=True))
        ty += 34
        for item in items:
            draw.ellipse([lx + 2, ty + 5, lx + 14, ty + 17], fill=GOLD)
            draw.text((lx + 22, ty + 2), item, fill=WHITE, font=font(14))
            ty += 30
        ty += 10
        gold_bar(draw, ty, h=1, x0=lx, x1=col_split - 20)
        ty += 12

    # Footer left
    gold_bar(draw, ty + 10, h=2, x0=lx, x1=col_split - 20)
    draw.text((lx, ty + 22), "Book again:", fill=GREY, font=font(13))
    draw.text((lx, ty + 44), "+1 (555) 000-0000", fill=WHITE, font=font(15, bold=True))
    draw.text((lx, ty + 68), "@yourbarbershop", fill=GOLD, font=font(14))

    # Divider
    draw.rectangle([col_split, 28, col_split + 2, H - 28], fill=GOLD)

    # Right col: rebook prompt + QR
    rx = col_split + 30
    rw = W - col_split - 50

    draw.text((rx, 44), "REBOOK YOUR", fill=WHITE, font=font(18, bold=True))
    draw.text((rx, 74), "NEXT CUT", fill=GOLD, font=font(22, bold=True))
    gold_bar(draw, 110, x0=rx, x1=W - 28)

    draw.text((rx, 126), "Keep your fade fresh —", fill=WHITE, font=font(14))
    draw.text((rx, 150), "book 2–3 weeks ahead.", fill=GREY, font=font(14))
    draw.text((rx, 176), "Scan to book online:", fill=WHITE, font=font(14))

    qr_size = 180
    qr_x = rx + (rw - qr_size) // 2
    qr_y = 206
    qr_placeholder(draw, qr_x, qr_y, qr_size, label="Booking QR")

    # Rating ask
    rate_y = qr_y + qr_size + 60
    draw.text((rx, rate_y), "Loved your cut?", fill=WHITE, font=font(15, bold=True))
    star_row(draw, rx + rw // 2, rate_y + 30, count=5, r=16)
    draw.text((rx, rate_y + 64), "Leave us a 5-star review!", fill=GOLD,
              font=font(14, bold=True))
    draw.text((rx, rate_y + 88), "Link on Google · @yourbarbershop", fill=GREY,
              font=font(12))

    # Thank you note
    gold_bar(draw, rate_y + 118, x0=rx, x1=W - 28)
    draw.text((rx, rate_y + 130), "Thank you for", fill=WHITE, font=font(14))
    draw.text((rx, rate_y + 154), "visiting us today!", fill=GOLD,
              font=font(16, bold=True))

    return save(img, "barber_util_04_aftercare.png")


# ─── PREVIEW GRID ─────────────────────────────────────────────────────────────

def build_preview_grid(files):
    print("Building preview grid...")
    thumb_w = 800
    padding = 40
    gap     = 30
    cols    = 2
    rows    = -(-len(files) // cols)

    # All thumbs normalised to thumb_w wide (keep AR)
    thumbs = []
    for f in files:
        im = Image.open(f)
        w, h = im.size
        th = int(h * thumb_w / w)
        thumbs.append(im.resize((thumb_w, th), Image.LANCZOS))

    # max height per row
    row_heights = []
    for r in range(rows):
        row_th = thumbs[r * cols:(r + 1) * cols]
        row_heights.append(max(t.size[1] for t in row_th) if row_th else 0)

    grid_w = padding * 2 + thumb_w * cols + gap * (cols - 1)
    grid_h = padding * 2 + sum(row_heights) + gap * (rows - 1)
    grid = Image.new("RGB", (grid_w, grid_h), DARK)

    idx = 0
    y = padding
    for r in range(rows):
        x = padding
        for c in range(cols):
            if idx < len(thumbs):
                grid.paste(thumbs[idx], (x, y))
                idx += 1
            x += thumb_w + gap
        y += row_heights[r] + gap

    out = OUTPUT_DIR / "preview_grid.png"
    grid.save(str(out), "PNG")
    print(f"  Saved: {out.name}")
    return out


# ─── UPLOAD ───────────────────────────────────────────────────────────────────

def upload(local_path, key):
    load_dotenv("/root/NEW-AI-PROJECT/purpleocaz-canva-mcp/.env", override=True)
    s3 = boto3.client("s3",
        endpoint_url="https://lon1.digitaloceanspaces.com",
        aws_access_key_id=os.getenv("DO_SPACES_KEY"),
        aws_secret_access_key=os.getenv("DO_SPACES_SECRET"),
        region_name="lon1",
    )
    s3.upload_file(str(local_path), "purpleocaz-assets", key,
                   ExtraArgs={"ACL": "public-read", "ContentType": "image/png"})
    url = f"https://purpleocaz-assets.lon1.digitaloceanspaces.com/{key}"
    print(f"  Uploaded → {url}")
    return url


# ─── MAIN ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    files = [
        card_01_google_review(),
        card_02_tip_guide(),
        card_03_price_list(),
        card_04_aftercare(),
    ]
    grid = build_preview_grid(files)

    print("\nUploading to Spaces...")
    for f in files:
        upload(f, f"barbershop/utility/{f.name}")
    grid_url = upload(grid, "barbershop/utility/preview_grid.png")

    print("\nVerifying uploads...")
    import urllib.request
    all_ok = True
    for f in files:
        url = f"https://purpleocaz-assets.lon1.digitaloceanspaces.com/barbershop/utility/{f.name}"
        try:
            code = urllib.request.urlopen(url).getcode()
            print(f"  {f.name}: HTTP {code}")
        except Exception as e:
            print(f"  {f.name}: FAILED — {e}")
            all_ok = False

    print(f"\nPreview grid: {grid_url}")
    print(f"Done. 4 utility cards uploaded. All OK: {all_ok}")
