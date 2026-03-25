#!/usr/bin/env python3
"""
Barbershop Mega Bundle — full publish pipeline.

Steps:
  1. Generate delivery PDF (27 Canva /view links, by category)
  2. Build 5 listing images (hero + what's inside + how it works + why buy + lifestyle)
  3. Create Etsy listing (draft)
  4. Upload images (ranks 1–7)
  5. Upload delivery PDF
  6. Activate listing
  7. Verify

Price: £14.99
"""

import json, os, sys, time, math, urllib.request, urllib.error, urllib.parse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import boto3
from dotenv import load_dotenv

PROJECT = Path("/root/NEW-AI-PROJECT")
sys.path.insert(0, str(PROJECT))
load_dotenv(PROJECT / ".env")
load_dotenv(PROJECT / "purpleocaz-canva-mcp/.env", override=False)

OUTPUT_DIR = PROJECT / "outputs" / "barbershop" / "listing"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FONT_BOLD  = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG   = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_SERIFB= "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

BG    = (26, 26, 26)
DARK  = (10, 10, 10)
PANEL = (38, 38, 38)
GOLD  = (201, 169, 110)
WHITE = (255, 255, 255)
GREY  = (136, 136, 136)

W = H = 3000   # All listing images 3000×3000

TOKEN_FILE = PROJECT / "workflows" / "etsy_analytics" / "etsy_tokens.json"
ETSY_BASE  = "https://openapi.etsy.com/v3/application"
API_KEY    = os.getenv("ETSY_API_KEYSTRING", "")
SECRET     = os.getenv("ETSY_SHARED_SECRET", "")
SHOP_ID    = os.getenv("ETSY_SHOP_ID", "34071205")
X_API_KEY  = f"{API_KEY}:{SECRET}"


# ─── Registry ─────────────────────────────────────────────────────────────────

def load_registry():
    with open(PROJECT / "config" / "design_registry.json") as f:
        return json.load(f)


# ─── Font / draw helpers ───────────────────────────────────────────────────────

def font(size, bold=False, serif=False, serifbold=False):
    if serifbold: return ImageFont.truetype(FONT_SERIFB, size)
    if serif:     return ImageFont.truetype(FONT_SERIF,  size)
    if bold:      return ImageFont.truetype(FONT_BOLD,   size)
    return ImageFont.truetype(FONT_REG, size)


def cx(draw, y, text, fill, f, w=W):
    bb = draw.textbbox((0, 0), text, font=f)
    draw.text(((w - (bb[2] - bb[0])) // 2, y), text, fill=fill, font=f)


def gbar(draw, y, h=6, x0=0, x1=W):
    draw.rectangle([x0, y, x1, y + h], fill=GOLD)


def scissors(draw, x, y, size=50):
    draw.line([(x - size, y - size // 2), (x + size, y + size // 2)], fill=GOLD, width=10)
    draw.line([(x + size, y - size // 2), (x - size, y + size // 2)], fill=GOLD, width=10)
    for ex, ey in [(x - size, y - size // 2), (x + size, y - size // 2),
                   (x - size, y + size // 2), (x + size, y + size // 2)]:
        draw.ellipse([ex - 14, ey - 14, ex + 14, ey + 14], outline=GOLD, width=5)


def save(img, name):
    out = OUTPUT_DIR / name
    img.save(str(out), "PNG")
    print(f"  Saved: {name}")
    return out


# ─── LISTING IMAGE 1: Hero ────────────────────────────────────────────────────

def build_hero():
    """Dark luxury hero — 27 templates badge, four category panels."""
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Border
    gbar(draw, 0, h=14)
    gbar(draw, H - 14, h=14)
    draw.rectangle([14, 14, W - 14, H - 14], outline=GOLD, width=6)

    # Top shop identity
    scissors(draw, W // 2, 130, size=55)
    cx(draw, 215, "BARBERSHOP MEGA BUNDLE", GOLD, font(110, bold=True))
    cx(draw, 345, "27 CANVA TEMPLATES · FULLY EDITABLE", WHITE, font(58, bold=True))
    gbar(draw, 440, h=5, x0=120, x1=W - 120)

    # Four category panels (2×2 grid)
    cats = [
        ("PRINT",          "5 templates",  "Business Cards\nAppointment · Thank You\nRefer a Friend"),
        ("INSTAGRAM POSTS","12 templates", "Brand · Services · Book Now\nOffers · Reviews · Tips\nBefore & After · Hours"),
        ("STORIES",        "6 templates",  "Flash Deal · Availability\nTip of Day · Shoutout\nWeekend Special"),
        ("UTILITY CARDS",  "4 templates",  "Google Review Card\nGrooming Tip Guide\nPrice List · Aftercare"),
    ]

    pad = 90
    gap = 40
    cell_w = (W - pad * 2 - gap) // 2
    cell_h = 820
    grid_top = 500

    for i, (cat, count, items) in enumerate(cats):
        row, col = divmod(i, 2)
        cx_pos = pad + col * (cell_w + gap)
        cy_pos = grid_top + row * (cell_h + gap)

        draw.rounded_rectangle([cx_pos, cy_pos, cx_pos + cell_w, cy_pos + cell_h],
                                radius=24, fill=PANEL, outline=GOLD, width=4)

        # Gold top strip
        draw.rounded_rectangle([cx_pos, cy_pos, cx_pos + cell_w, cy_pos + 14],
                                radius=0, fill=GOLD)

        # Category name
        bb = draw.textbbox((0, 0), cat, font=font(52, bold=True))
        draw.text((cx_pos + (cell_w - (bb[2] - bb[0])) // 2, cy_pos + 40),
                  cat, fill=GOLD, font=font(52, bold=True))

        # Count badge
        badge_text = count
        bb2 = draw.textbbox((0, 0), badge_text, font=font(38, bold=True))
        bw = bb2[2] - bb2[0] + 60
        bx = cx_pos + (cell_w - bw) // 2
        draw.rounded_rectangle([bx, cy_pos + 118, bx + bw, cy_pos + 178],
                                radius=30, fill=GOLD)
        draw.text((bx + 30, cy_pos + 126), badge_text, fill=DARK, font=font(38, bold=True))

        # Item lines
        for j, line in enumerate(items.split("\n")):
            bb3 = draw.textbbox((0, 0), line, font=font(36))
            draw.text((cx_pos + (cell_w - (bb3[2] - bb3[0])) // 2, cy_pos + 230 + j * 80),
                      line, fill=WHITE, font=font(36))

        # Scissors icon
        scissors(draw, cx_pos + cell_w // 2, cy_pos + cell_h - 120, size=30)

    # Bottom CTA strip
    bottom_y = grid_top + 2 * (cell_h + gap) + 40
    gbar(draw, bottom_y, h=5, x0=120, x1=W - 120)
    cx(draw, bottom_y + 30, "Editable in free Canva  ·  Instant download  ·  Personal & commercial use", GREY, font(50))
    cx(draw, bottom_y + 110, "PurpleOcaz", GOLD, font(46, bold=True))

    return save(img, "barber_listing_01_hero.png")


# ─── LISTING IMAGE 2: What's Inside ──────────────────────────────────────────

def build_whats_inside():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    gbar(draw, 0, h=14)
    gbar(draw, H - 14, h=14)
    draw.rectangle([14, 14, W - 14, H - 14], outline=GOLD, width=6)

    cx(draw, 55, "WHAT'S INSIDE", WHITE, font(120, bold=True))
    cx(draw, 200, "BARBERSHOP MEGA BUNDLE · 27 TEMPLATES", GOLD, font(58, bold=True))
    gbar(draw, 298, h=5, x0=120, x1=W - 120)

    sections = [
        ("PRINT ESSENTIALS", "5 templates", [
            "Business Card — front (CR80)",
            "Business Card — back (CR80)",
            "Appointment Card (CR80)",
            "Thank You Card (A6 landscape)",
            "Refer a Friend Card (A6 landscape)",
        ]),
        ("INSTAGRAM POSTS  1080×1080", "12 templates", [
            "Brand Welcome · Services Menu · Book Now CTA",
            "New Client Offer · Customer Testimonial",
            "Tip of the Week · Before & After",
            "Meet the Barber · Opening Hours",
            "Loyalty Program · Referral Offer · Seasonal Promo",
        ]),
        ("INSTAGRAM STORIES  1080×1920", "6 templates", [
            "Book Now · Today's Availability · Flash Deal",
            "Tip of the Day · Client Shoutout · Weekend Special",
        ]),
        ("UTILITY CARDS", "4 templates", [
            "Google Review Card (A6) — QR placeholder included",
            "Grooming Tip Guide (A5 portrait)",
            "Price List Card (A5 portrait)",
            "Aftercare Advice Card (A6) — rebook prompt + QR",
        ]),
    ]

    sy = 338
    for title, count, items in sections:
        # Section header row
        draw.rectangle([60, sy, W - 60, sy + 90], fill=PANEL)
        gbar(draw, sy, h=5, x0=60, x1=W - 60)

        bb = draw.textbbox((0, 0), title, font=font(52, bold=True))
        draw.text((90, sy + 18), title, fill=GOLD, font=font(52, bold=True))

        # Count badge right
        bb2 = draw.textbbox((0, 0), count, font=font(42, bold=True))
        draw.text((W - 90 - (bb2[2] - bb2[0]), sy + 22), count, fill=WHITE, font=font(42, bold=True))
        sy += 100

        for item in items:
            draw.ellipse([82, sy + 14, 106, sy + 38], fill=GOLD)
            draw.text((122, sy + 8), item, fill=WHITE, font=font(42))
            sy += 64

        sy += 30

    gbar(draw, sy + 10, h=4, x0=120, x1=W - 120)
    cx(draw, sy + 36, "Every template: fully editable in free Canva · Instant download", GREY, font(48))

    return save(img, "barber_listing_02_whats_inside.png")


# ─── LISTING IMAGE 3: Lifestyle / Mockup feel ─────────────────────────────────

def build_lifestyle():
    """Shows the templates 'in use' — device mockup placeholder + use cases."""
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    gbar(draw, 0, h=14)
    gbar(draw, H - 14, h=14)

    # Split: left dark panel, right cream
    draw.rectangle([0, 0, W // 2, H], fill=DARK)
    draw.rectangle([W // 2, 0, W, H], fill=(240, 236, 225))

    # Left: main hook
    scissors(draw, W // 4, 280, size=60)
    for i, line in enumerate(["YOUR SHOP.", "YOUR BRAND.", "YOUR TEMPLATES."]):
        colour = GOLD if i == 2 else WHITE
        cx(draw, 400 + i * 160, line, colour, font(88, bold=True), W // 2)

    gbar(draw, 900, h=4, x0=60, x1=W // 2 - 60)

    use_cases = [
        "Hand business cards to every client",
        "Post 12 Instagram templates weekly",
        "Reply to Stories for bookings",
        "Display price list at the counter",
        "Send Google review card post-cut",
        "Give aftercare card with every visit",
    ]
    uy = 940
    for uc in use_cases:
        draw.ellipse([80, uy + 12, 110, uy + 42], fill=GOLD)
        draw.text((136, uy + 6), uc, fill=WHITE, font=font(50))
        uy += 80

    gbar(draw, uy + 20, h=4, x0=60, x1=W // 2 - 60)
    cx(draw, uy + 46, "27 templates.", WHITE, font(64, bold=True), W // 2)
    cx(draw, uy + 130, "One purchase. Use forever.", GOLD, font(50), W // 2)

    # Gold divider
    draw.rectangle([W // 2 - 3, 60, W // 2 + 3, H - 60], fill=GOLD)

    # Right: benefits panel
    cx_r = W // 2
    rw   = W // 2

    benefits_title = "DESIGNED FOR"
    cx(draw, 120, benefits_title, DARK, font(70, bold=True), rw)
    cx(draw, 210, "BARBERSHOP OWNERS", DARK, font(60, bold=True), rw)

    gbar(draw, 310, h=4, x0=W // 2 + 60, x1=W - 60)

    benefits = [
        ("PRINT READY",       "A6 cards — take to any print shop"),
        ("SOCIAL READY",      "1080×1080 and 1080×1920 formats"),
        ("FULLY EDITABLE",    "Change every word, colour, photo"),
        ("FREE CANVA",        "No subscription needed"),
        ("INSTANT DOWNLOAD",  "Access in minutes after purchase"),
        ("COMMERCIAL USE",    "Use for your business — no extra fee"),
    ]

    by = 370
    for label, desc in benefits:
        draw.rounded_rectangle([W // 2 + 60, by, W - 60, by + 110],
                               radius=14, fill=WHITE, outline=(201, 169, 110), width=3)
        draw.text((W // 2 + 100, by + 12), label, fill=(26, 26, 26), font=font(46, bold=True))
        draw.text((W // 2 + 100, by + 62), desc, fill=(100, 100, 100), font=font(38))
        by += 136

    gbar(draw, by + 20, h=4, x0=W // 2 + 60, x1=W - 60)
    cx(draw, by + 46, "PurpleOcaz", (26, 26, 26), font(52, bold=True), rw)
    cx(draw, by + 120, "Professional barbershop templates", (100, 100, 100), font(40), rw)

    return save(img, "barber_listing_03_lifestyle.png")


# ─── LISTING IMAGE 4: How It Works ────────────────────────────────────────────

def build_how_it_works():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    gbar(draw, 0, h=14)
    gbar(draw, H - 14, h=14)
    draw.rectangle([14, 14, W - 14, H - 14], outline=GOLD, width=6)

    scissors(draw, W // 2, 130, size=55)
    cx(draw, 218, "HOW IT WORKS", WHITE, font(110, bold=True))
    cx(draw, 358, "UP AND RUNNING IN UNDER 10 MINUTES", GOLD, font(60, bold=True))
    gbar(draw, 460, h=5, x0=120, x1=W - 120)

    steps = [
        ("01", "PURCHASE",         "Buy this listing. You'll receive a PDF\ndelivery file instantly from Etsy."),
        ("02", "OPEN THE PDF",     "Open your delivery PDF. You'll find\n27 Canva links — one per template."),
        ("03", "CLICK A LINK",     "Click any link. It opens in your browser.\nSelect File → Make a copy."),
        ("04", "EDIT YOUR COPY",   "Change your shop name, phone number,\nservices, prices and photos. Free account."),
        ("05", "DOWNLOAD & USE",   "Export as PNG or PDF. Print cards,\nschedule Instagram posts, display in-shop."),
    ]

    step_top = 510
    step_h   = 430
    icon_r   = 90

    for i, (num, title, body) in enumerate(steps):
        sy = step_top + i * step_h

        # Connector line (except last)
        if i < len(steps) - 1:
            draw.rectangle([W // 2 - 4, sy + icon_r * 2, W // 2 + 4, sy + step_h],
                           fill=(60, 60, 60))

        # Circle
        draw.ellipse([W // 2 - icon_r, sy, W // 2 + icon_r, sy + icon_r * 2],
                     fill=GOLD, outline=GOLD)
        bb = draw.textbbox((0, 0), num, font=font(70, bold=True))
        draw.text((W // 2 - (bb[2] - bb[0]) // 2, sy + icon_r - 38), num,
                  fill=DARK, font=font(70, bold=True))

        # Right: title + body
        tx = W // 2 + icon_r + 60
        draw.text((tx, sy + 10), title, fill=GOLD, font=font(62, bold=True))
        for j, line in enumerate(body.split("\n")):
            draw.text((tx, sy + 90 + j * 68), line, fill=WHITE, font=font(48))

        # Left: step label
        lx = W // 2 - icon_r - 60
        bb2 = draw.textbbox((0, 0), f"Step {i+1}", font=font(44))
        draw.text((lx - (bb2[2] - bb2[0]), sy + icon_r - 22), f"Step {i+1}",
                  fill=GREY, font=font(44))

    footer_y = step_top + len(steps) * step_h + 20
    gbar(draw, footer_y, h=4, x0=120, x1=W - 120)
    cx(draw, footer_y + 30, "Questions? Message us on Etsy — we reply within 24 hours.", WHITE, font(50))

    return save(img, "barber_listing_04_how_it_works.png")


# ─── LISTING IMAGE 5: Why Buy This ────────────────────────────────────────────

def build_why_buy():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    gbar(draw, 0, h=14)
    gbar(draw, H - 14, h=14)
    draw.rectangle([14, 14, W - 14, H - 14], outline=GOLD, width=6)

    cx(draw, 60, "WHY THIS BUNDLE", WHITE, font(110, bold=True))
    cx(draw, 200, "27 TEMPLATES · £14.99 · INSTANT DOWNLOAD", GOLD, font(58, bold=True))
    gbar(draw, 300, h=5, x0=120, x1=W - 120)

    # Comparison table header
    col1_x = 120
    col2_x = W // 2 - 100
    col3_x = W - 500

    draw.rectangle([col1_x, 340, W - col1_x, 440], fill=PANEL)
    draw.text((col1_x + 30, 356), "WHAT YOU GET", fill=GOLD, font=font(52, bold=True))
    cx(draw, 356, "THIS BUNDLE", GOLD, font(52, bold=True))

    rows = [
        ("5 Print templates (cards)",             "✓"),
        ("12 Instagram Post templates",           "✓"),
        ("6 Instagram Story templates",           "✓"),
        ("4 Utility cards (review, tip, price)",  "✓"),
        ("Editable in free Canva",                "✓"),
        ("Instant digital download",              "✓"),
        ("Personal & commercial use",             "✓"),
        ("Consistent dark/gold design system",    "✓"),
        ("Print-ready A6 card sizes",             "✓"),
        ("Story & post sizes pre-set",            "✓"),
    ]

    ry = 460
    for i, (label, check) in enumerate(rows):
        bg = (38, 38, 38) if i % 2 == 0 else BG
        draw.rectangle([col1_x, ry, W - col1_x, ry + 84], fill=bg)
        draw.text((col1_x + 30, ry + 20), label, fill=WHITE, font=font(46))

        # Check badge
        bb = draw.textbbox((0, 0), check, font=font(56, bold=True))
        cx_check = W - 300
        draw.text((cx_check, ry + 14), check, fill=GOLD, font=font(56, bold=True))
        ry += 84

        gbar(draw, ry, h=1, x0=col1_x, x1=W - col1_x)

    gbar(draw, ry + 16, h=4, x0=120, x1=W - 120)

    cx(draw, ry + 40, "Every barbershop needs this.", WHITE, font(70, bold=True))
    cx(draw, ry + 132, "Buy once. Use for years.", GOLD, font(58))

    return save(img, "barber_listing_05_why_buy.png")


# ─── DELIVERY PDF ─────────────────────────────────────────────────────────────

def build_delivery_pdf(registry):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib.colors import HexColor, black
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT

    GOLD_C = HexColor("#C9A96E")
    DARK_C = HexColor("#1A1A1A")
    GREY_C = HexColor("#888888")

    out_path = str(OUTPUT_DIR / "Barbershop-Mega-Bundle-DELIVERY.pdf")
    doc = SimpleDocTemplate(out_path, pagesize=A4,
                            leftMargin=20*mm, rightMargin=20*mm,
                            topMargin=20*mm, bottomMargin=20*mm)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("Title1", fontName="Helvetica-Bold", fontSize=22,
                              textColor=DARK_C, spaceAfter=4, alignment=TA_CENTER))
    styles.add(ParagraphStyle("Sub",    fontName="Helvetica",      fontSize=12,
                              textColor=GREY_C, spaceAfter=10, alignment=TA_CENTER))
    styles.add(ParagraphStyle("CatHead",fontName="Helvetica-Bold", fontSize=13,
                              textColor=GOLD_C, spaceBefore=14, spaceAfter=4))
    styles.add(ParagraphStyle("Body",   fontName="Helvetica",      fontSize=10,
                              textColor=DARK_C, spaceAfter=5, leading=14))
    styles.add(ParagraphStyle("Note",   fontName="Helvetica-Oblique", fontSize=8,
                              textColor=GREY_C, spaceAfter=3, alignment=TA_CENTER))
    styles.add(ParagraphStyle("Step",   fontName="Helvetica-Bold",  fontSize=10,
                              textColor=DARK_C, spaceAfter=3, leading=14))

    b = registry["designs"]["barbershop"]

    story = [
        Paragraph("Barbershop Mega Bundle", styles["Title1"]),
        Paragraph("27 Canva Templates · Your Delivery File", styles["Sub"]),
        Spacer(1, 4),
        Paragraph("Thank you for your purchase.", styles["Body"]),
        Paragraph(
            "Below are 27 Canva template links — one per design, organised by category.",
            styles["Body"]),
        Spacer(1, 6),
        Paragraph("How to edit your templates", styles["CatHead"]),
        Paragraph("1. Click any link below — it opens in your browser.", styles["Step"]),
        Paragraph("2. Select <b>File → Make a copy</b> to create your own editable version.", styles["Step"]),
        Paragraph("3. Replace the placeholder text (shop name, phone, prices, address).", styles["Step"]),
        Paragraph("4. Swap in your own photos via Canva's free image library.", styles["Step"]),
        Paragraph("5. Download as PDF (print) or PNG (social media) — done.", styles["Step"]),
        Spacer(1, 4),
        Paragraph(
            "You need a free Canva account. No paid subscription required.",
            styles["Note"]),
        Spacer(1, 8),
    ]

    categories = [
        ("PRINT ESSENTIALS (5 templates)", "print", {
            "business_card_front": "Business Card — Front (CR80)",
            "business_card_back":  "Business Card — Back (CR80)",
            "appointment_card":    "Appointment Card (CR80)",
            "thank_you_card":      "Thank You Card (A6 landscape)",
            "refer_a_friend":      "Refer a Friend Card (A6 landscape)",
        }),
        ("INSTAGRAM POSTS — 1080×1080 (12 templates)", "instagram", {
            "brand_welcome":    "01 — Brand Welcome",
            "services_menu":    "02 — Services Menu",
            "book_now":         "03 — Book Now CTA",
            "new_client_offer": "04 — New Client Offer",
            "testimonial":      "05 — Customer Testimonial",
            "tip_of_week":      "06 — Tip of the Week",
            "before_after":     "07 — Before & After",
            "meet_the_barber":  "08 — Meet the Barber",
            "opening_hours":    "09 — Opening Hours",
            "loyalty_program":  "10 — Loyalty Program",
            "referral":         "11 — Referral Offer",
            "seasonal_promo":   "12 — Seasonal Promo",
        }),
        ("INSTAGRAM STORIES — 1080×1920 (6 templates)", "stories", {
            "book_now":        "01 — Book Now",
            "availability":    "02 — Today's Availability",
            "flash_deal":      "03 — Flash Deal",
            "tip_of_day":      "04 — Tip of the Day",
            "client_shoutout": "05 — Client Shoutout",
            "weekend_special": "06 — Weekend Special",
        }),
        ("UTILITY CARDS (4 templates)", "utility", {
            "google_review": "Google Review Card (A6 landscape)",
            "tip_guide":     "Grooming Tip Guide (A5 portrait)",
            "price_list":    "Price List Card (A5 portrait)",
            "aftercare":     "Aftercare Advice Card (A6 landscape)",
        }),
    ]

    for cat_title, cat_key, items in categories:
        story.append(Paragraph(cat_title, styles["CatHead"]))
        for key, label in items.items():
            entry = b[cat_key].get(key, {})
            url   = entry.get("view_url", "")
            story.append(Paragraph(
                f'<b>{label}:</b> <a href="{url}" color="#C9A96E">{url}</a>',
                styles["Body"]))

    story.extend([
        Spacer(1, 14),
        Paragraph("Need help?", styles["CatHead"]),
        Paragraph(
            "Message us through Etsy — we reply within 24 hours. "
            "Include your order number and which template you need help with.",
            styles["Body"]),
        Spacer(1, 20),
        Paragraph(
            "PurpleOcaz · Personal and commercial use permitted · Resale of templates not permitted.",
            styles["Note"]),
    ])

    doc.build(story)
    print(f"  Delivery PDF: {out_path}")
    return out_path


# ─── Spaces upload ────────────────────────────────────────────────────────────

def upload_spaces(local_path, key, content_type="image/png"):
    s3 = boto3.client("s3",
        endpoint_url="https://lon1.digitaloceanspaces.com",
        aws_access_key_id=os.getenv("DO_SPACES_KEY"),
        aws_secret_access_key=os.getenv("DO_SPACES_SECRET"),
        region_name="lon1",
    )
    s3.upload_file(str(local_path), "purpleocaz-assets", key,
                   ExtraArgs={"ACL": "public-read", "ContentType": content_type})
    url = f"https://purpleocaz-assets.lon1.digitaloceanspaces.com/{key}"
    print(f"  Spaces: {url}")
    return url


# ─── Etsy helpers ─────────────────────────────────────────────────────────────

def load_tokens():
    with open(TOKEN_FILE) as f:
        return json.load(f)


def refresh_token(tokens):
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "client_id": API_KEY,
        "refresh_token": tokens["refresh_token"],
    }).encode()
    req = urllib.request.Request(
        "https://api.etsy.com/v3/public/oauth/token",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    resp = urllib.request.urlopen(req)
    new_tokens = json.loads(resp.read())
    with open(TOKEN_FILE, "w") as f:
        json.dump(new_tokens, f, indent=2)
    print(f"  Token refreshed, expires {new_tokens.get('expires_in')}s")
    return new_tokens


def etsy(method, endpoint, tokens, body=None, ct="application/x-www-form-urlencoded"):
    url = f"{ETSY_BASE}{endpoint}"
    data = urllib.parse.urlencode(body).encode() if body and ct == "application/x-www-form-urlencoded" else body
    req  = urllib.request.Request(url, data=data, method=method)
    req.add_header("x-api-key", X_API_KEY)
    req.add_header("Authorization", f"Bearer {tokens['access_token']}")
    if ct and method != "GET":
        req.add_header("Content-Type", ct)
    try:
        return json.loads(urllib.request.urlopen(req).read())
    except urllib.error.HTTPError as e:
        body_txt = e.read().decode()
        if e.code == 401:
            tokens.update(refresh_token(tokens))
            req.remove_header("Authorization")
            req.add_header("Authorization", f"Bearer {tokens['access_token']}")
            return json.loads(urllib.request.urlopen(req).read())
        print(f"  HTTP {e.code}: {body_txt[:300]}")
        raise


def upload_image(tokens, lid, image_path, rank):
    boundary = "----PurpleOcazBoundary"
    filename  = os.path.basename(image_path)
    with open(image_path, "rb") as f:
        data = f.read()
    body = bytearray()
    body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"rank\"\r\n\r\n{rank}\r\n".encode())
    body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{filename}\"\r\nContent-Type: image/png\r\n\r\n".encode())
    body.extend(data + b"\r\n" + f"--{boundary}--\r\n".encode())
    req = urllib.request.Request(
        f"{ETSY_BASE}/shops/{SHOP_ID}/listings/{lid}/images",
        data=bytes(body), method="POST")
    req.add_header("x-api-key", X_API_KEY)
    req.add_header("Authorization", f"Bearer {tokens['access_token']}")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    try:
        result = json.loads(urllib.request.urlopen(req).read())
        print(f"  Image rank {rank}: {filename}")
        return result
    except urllib.error.HTTPError as e:
        print(f"  Image upload error {e.code}: {e.read().decode()[:200]}")
        raise


def upload_file(tokens, lid, file_path, filename):
    boundary = "----PurpleOcazFileBoundary"
    with open(file_path, "rb") as f:
        data = f.read()
    body = bytearray()
    body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"name\"\r\n\r\n{filename}\r\n".encode())
    body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{filename}\"\r\nContent-Type: application/pdf\r\n\r\n".encode())
    body.extend(data + b"\r\n" + f"--{boundary}--\r\n".encode())
    req = urllib.request.Request(
        f"{ETSY_BASE}/shops/{SHOP_ID}/listings/{lid}/files",
        data=bytes(body), method="POST")
    req.add_header("x-api-key", X_API_KEY)
    req.add_header("Authorization", f"Bearer {tokens['access_token']}")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    try:
        result = json.loads(urllib.request.urlopen(req).read())
        print(f"  File: {filename}")
        return result
    except urllib.error.HTTPError as e:
        print(f"  File upload error {e.code}: {e.read().decode()[:200]}")
        raise


def verify(tokens, lid):
    listing = etsy("GET", f"/listings/{lid}", tokens)
    images  = etsy("GET", f"/listings/{lid}/images", tokens)
    files   = etsy("GET", f"/shops/{SHOP_ID}/listings/{lid}/files", tokens)
    n_img   = len(images.get("results", []))
    n_files = len(files.get("results", []))
    state   = listing.get("state")
    price   = float(listing["price"]["amount"]) / listing["price"]["divisor"]
    tags    = listing.get("tags", [])
    print(f"  VERIFY: state={state} | images={n_img} | files={n_files} | price=£{price:.2f} | tags={len(tags)}")
    for t in tags:
        if len(t) > 20:
            print(f"  WARNING tag too long ({len(t)}): {t}")
    dups = [t for t in tags if tags.count(t) > 1]
    if dups:
        print(f"  WARNING duplicate tags: {dups}")
    return n_img, n_files, state


# ─── Listing copy ─────────────────────────────────────────────────────────────

TITLE = (
    "Barbershop Mega Bundle | 27 Canva Templates | Business Cards "
    "Instagram Posts Stories Price List | Digital Download"
)

TAGS = [
    "barbershop bundle",
    "barber canva",
    "barbershop canva",
    "barber templates",
    "barber marketing",
    "barber social media",
    "barbershop social",
    "barber instagram",
    "barber price list",
    "barber business card",
    "barber appointment",
    "mens grooming",
    "barber digital kit",
]

DESC = """\
27 BARBERSHOP CANVA TEMPLATES — PRINT, SOCIAL MEDIA AND UTILITY CARDS

Everything a barbershop needs to look professional on paper and online. Edit every template in Canva (free account). Change your shop name, phone number, prices and photos in minutes.

------------------------------

WHAT'S INCLUDED (27 templates)

PRINT ESSENTIALS — 5 templates
- Business Card front (CR80)
- Business Card back (CR80)
- Appointment Card (CR80)
- Thank You Card (A6 landscape) — includes 10% discount offer
- Refer a Friend Card (A6 landscape) — includes referral form fields

INSTAGRAM POSTS — 12 templates (1080×1080)
Brand Welcome · Services Menu · Book Now CTA · New Client Offer
Customer Testimonial · Tip of the Week · Before & After
Meet the Barber · Opening Hours · Loyalty Program
Referral Offer · Seasonal Promo

INSTAGRAM STORIES — 6 templates (1080×1920)
Book Now · Today's Availability · Flash Deal
Tip of the Day · Client Shoutout · Weekend Special

UTILITY CARDS — 4 templates
- Google Review Card (A6) — QR code placeholder, step-by-step scan instructions
- Grooming Tip Guide (A5) — daily, weekly and monthly care sections
- Price List Card (A5) — 4 service categories with dot-leader pricing
- Aftercare Advice Card (A6) — rebook prompt and QR placeholder

------------------------------

HOW TO USE

1. Purchase and download your delivery PDF instantly from Etsy
2. Open the PDF — 27 Canva links, one per template
3. Click any link. Select File → Make a copy to start editing
4. Replace placeholder text with your shop name, number and prices
5. Download as PDF (print) or PNG (social media)

------------------------------

PLEASE NOTE

- DIGITAL DOWNLOAD — nothing is shipped
- Free Canva account needed to edit (no paid plan required)
- Colour accuracy varies between screens and print
- Personal and commercial use permitted
- Resale of the templates is not permitted

Questions? Message us on Etsy — we reply within 24 hours.

PurpleOcaz — Barbershop templates built by barbers, for barbers.\
"""


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n=== BARBERSHOP MEGA BUNDLE — PUBLISH PIPELINE ===\n")

    registry = load_registry()
    tokens   = load_tokens()
    tokens   = refresh_token(tokens)

    # Validate tags
    assert len(TAGS) == 13, f"Tag count: {len(TAGS)}"
    assert len(set(TAGS)) == 13, "Duplicate tags detected"
    for t in TAGS:
        assert len(t) <= 20, f"Tag too long ({len(t)}): {t}"
    print("  Tags validated: 13 unique, all ≤20 chars ✓")

    # ── 1. Listing images ──────────────────────────────────────────────────────
    print("\n[1] Building listing images...")
    hero       = build_hero()
    whats_in   = build_whats_inside()
    lifestyle  = build_lifestyle()
    how_it     = build_how_it_works()
    why_buy    = build_why_buy()
    canva_p3   = PROJECT / "outputs" / "listing-pages" / "canva_basics_p3.png"
    please_p5  = PROJECT / "outputs" / "listing-pages" / "please_note_p5.png"

    assert canva_p3.exists(),  f"Missing: {canva_p3}"
    assert please_p5.exists(), f"Missing: {please_p5}"
    print(f"  Using existing generic pages: canva_basics_p3, please_note_p5 ✓")

    images = [
        (str(hero),      1),
        (str(whats_in),  2),
        (str(lifestyle), 3),
        (str(how_it),    4),
        (str(why_buy),   5),
        (str(canva_p3),  6),
        (str(please_p5), 7),
    ]

    # ── 2. Delivery PDF ────────────────────────────────────────────────────────
    print("\n[2] Building delivery PDF...")
    pdf_path = build_delivery_pdf(registry)

    # ── 3. Create Etsy listing ─────────────────────────────────────────────────
    print("\n[3] Creating Etsy listing (draft)...")
    listing = etsy("POST", f"/shops/{SHOP_ID}/listings", tokens, {
        "title":       TITLE,
        "description": DESC,
        "tags":        ",".join(TAGS),
        "price":       "14.99",
        "quantity":    "999",
        "who_made":    "i_did",
        "when_made":   "2020_2025",
        "taxonomy_id": "1874",
        "type":        "download",
        "is_supply":   "false",
        "is_digital":  "true",
    })
    lid = listing["listing_id"]
    print(f"  Listing created: {lid}")
    print(f"  URL: https://www.etsy.com/listing/{lid}")

    # ── 4. Upload images ───────────────────────────────────────────────────────
    print("\n[4] Uploading images (ranks 1–7)...")
    for img_path, rank in images:
        upload_image(tokens, lid, img_path, rank)
        time.sleep(1)

    # Verify image count
    imgs = etsy("GET", f"/listings/{lid}/images", tokens)
    n = len(imgs.get("results", []))
    print(f"  GET /listings/{lid}/images → count={n}")
    assert n == 7, f"Expected 7 images, got {n}"

    # ── 5. Upload delivery PDF ─────────────────────────────────────────────────
    print("\n[5] Uploading delivery PDF...")
    upload_file(tokens, lid, pdf_path, "Barbershop-Mega-Bundle-DELIVERY.pdf")

    # Verify file attached
    files = etsy("GET", f"/shops/{SHOP_ID}/listings/{lid}/files", tokens)
    n_files = len(files.get("results", []))
    print(f"  GET /shops/{SHOP_ID}/listings/{lid}/files → count={n_files}")
    assert n_files == 1, f"Expected 1 file, got {n_files}"

    # ── 6. Activate listing ────────────────────────────────────────────────────
    print("\n[6] Activating listing...")
    etsy("PATCH", f"/shops/{SHOP_ID}/listings/{lid}", tokens, {"state": "active"})
    print(f"  PATCH state=active sent")

    # ── 7. Final verification ──────────────────────────────────────────────────
    print("\n[7] Final verification...")
    n_img, n_files, state = verify(tokens, lid)

    assert state   == "active", f"State not active: {state}"
    assert n_img   == 7,        f"Image count wrong: {n_img}"
    assert n_files == 1,        f"File count wrong: {n_files}"

    print(f"\n{'='*55}")
    print(f"  LISTING LIVE ✓")
    print(f"  ID:    {lid}")
    print(f"  URL:   https://www.etsy.com/listing/{lid}")
    print(f"  Price: £14.99  |  Images: {n_img}/7  |  Files: {n_files}")
    print(f"{'='*55}\n")

    # Save listing ID
    ids_file = OUTPUT_DIR / "etsy_listing_id.json"
    with open(ids_file, "w") as f:
        json.dump({"barbershop_mega_bundle": lid, "url": f"https://www.etsy.com/listing/{lid}"}, f, indent=2)
    print(f"  ID saved: {ids_file}")
