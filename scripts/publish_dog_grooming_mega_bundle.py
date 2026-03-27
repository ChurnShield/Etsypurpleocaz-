#!/usr/bin/env python3
"""
Dog Grooming Mega Bundle — Publish Pipeline
Phase 4: Build delivery PDF
Phase 5: Build 7 listing images + create Etsy draft + upload images + attach PDF
"""
import json, os, sys, time, uuid, math, urllib.request, urllib.error, urllib.parse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import boto3
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.pagesizes import A4 as RL_A4
from reportlab.lib import colors
from dotenv import load_dotenv

PROJECT = Path("/root/NEW-AI-PROJECT")
sys.path.insert(0, str(PROJECT / "scripts"))
load_dotenv(PROJECT / ".env")
load_dotenv(PROJECT / "purpleocaz-canva-mcp/.env", override=False)

from dog_grooming_design_system import (
    TEAL, GOLD, CREAM, CHARCOAL, WHITE, CREAM_ALT, TEAL_DARK,
    LISTING_IMG, A4 as PIL_A4,
    font, centred, right, gold_rule, teal_bar, section_head,
    paw_print, a4_header, a4_footer, upload_to_spaces,
)

OUTPUT_DIR  = PROJECT / "outputs" / "dog-grooming" / "listing"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CDN         = "https://purpleocaz-assets.lon1.digitaloceanspaces.com"
TOKEN_FILE  = PROJECT / "workflows" / "etsy_analytics" / "etsy_tokens.json"
ETSY_BASE   = "https://openapi.etsy.com/v3/application"
API_KEY     = os.getenv("ETSY_API_KEYSTRING", "")
SECRET      = os.getenv("ETSY_SHARED_SECRET", "")
SHOP_ID     = os.getenv("ETSY_SHOP_ID", "34071205")
X_API_KEY   = f"{API_KEY}:{SECRET}"

W = H = 3000   # Listing images


# ─── Etsy helpers ──────────────────────────────────────────────────────────────

def load_tokens():
    with open(TOKEN_FILE) as f:
        return json.load(f)


def etsy_request(method, path, body=None, content_type="application/x-www-form-urlencoded",
                 retries=2):
    tokens = load_tokens()
    url = f"{ETSY_BASE}{path}"
    data = body.encode() if isinstance(body, str) else body
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("x-api-key", X_API_KEY)
    req.add_header("Authorization", f"Bearer {tokens['access_token']}")
    if body and content_type:
        req.add_header("Content-Type", content_type)
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read()
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        body_str = e.read().decode()
        if e.code == 401 and retries:
            print("  [Auth] 401 — token may have expired, retrying...")
            time.sleep(2)
            return etsy_request(method, path, body, content_type, retries - 1)
        raise RuntimeError(f"Etsy {method} {path} → {e.code}: {body_str}")


def upload_image_to_etsy(listing_id, img_path, rank):
    tokens = load_tokens()
    boundary = uuid.uuid4().hex
    with open(img_path, "rb") as f:
        img_data = f.read()
    body = b""
    body += f"--{boundary}\r\n".encode()
    body += f'Content-Disposition: form-data; name="rank"\r\n\r\n{rank}\r\n'.encode()
    body += f"--{boundary}\r\n".encode()
    body += f'Content-Disposition: form-data; name="image"; filename="{img_path.name}"\r\n'.encode()
    body += b"Content-Type: image/png\r\n\r\n"
    body += img_data
    body += f"\r\n--{boundary}--\r\n".encode()
    url = f"{ETSY_BASE}/shops/{SHOP_ID}/listings/{listing_id}/images"
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("x-api-key", X_API_KEY)
    req.add_header("Authorization", f"Bearer {tokens['access_token']}")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def upload_file_to_etsy(listing_id, pdf_path):
    tokens = load_tokens()
    boundary = uuid.uuid4().hex
    filename = pdf_path.name
    with open(pdf_path, "rb") as f:
        pdf_data = f.read()
    body = b""
    body += f"--{boundary}\r\n".encode()
    body += f'Content-Disposition: form-data; name="name"\r\n\r\n{filename}\r\n'.encode()
    body += f"--{boundary}\r\n".encode()
    body += f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode()
    body += b"Content-Type: application/pdf\r\n\r\n"
    body += pdf_data
    body += f"\r\n--{boundary}--\r\n".encode()
    url = f"{ETSY_BASE}/shops/{SHOP_ID}/listings/{listing_id}/files"
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("x-api-key", X_API_KEY)
    req.add_header("Authorization", f"Bearer {tokens['access_token']}")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


# ─── Delivery PDF ──────────────────────────────────────────────────────────────

TEAL_HEX   = colors.HexColor("#0D5C63")
GOLD_HEX   = colors.HexColor("#C9A96E")
CREAM_HEX  = colors.HexColor("#F5F0E8")
CHARCOAL_HEX = colors.HexColor("#1A1A1A")

BRANDING_ITEMS = [
    ("Business Card — Dark",          f"{CDN}/templates/dog-grooming/branding/DG_Business_Card_Dark.png"),
    ("Business Card — Light",         f"{CDN}/templates/dog-grooming/branding/DG_Business_Card_Light.png"),
    ("Appointment Card — Dark",       f"{CDN}/templates/dog-grooming/branding/DG_Appointment_Card_Dark.png"),
    ("Appointment Card — Light",      f"{CDN}/templates/dog-grooming/branding/DG_Appointment_Card_Light.png"),
    ("Loyalty Stamp Card",            f"{CDN}/templates/dog-grooming/branding/DG_Loyalty_Card.png"),
    ("Gift Certificate",              f"{CDN}/templates/dog-grooming/branding/DG_Gift_Certificate.png"),
    ("Welcome Sign (A4)",             f"{CDN}/templates/dog-grooming/branding/DG_Welcome_Sign.png"),
    ("Thank You Card",                f"{CDN}/templates/dog-grooming/branding/DG_Thank_You_Card.png"),
    ("Referral Card",                 f"{CDN}/templates/dog-grooming/branding/DG_Referral_Card.png"),
    ("Opening Hours Sign (A4)",       f"{CDN}/templates/dog-grooming/branding/DG_Opening_Hours_Sign.png"),
]
MARKETING_ITEMS = [
    ("Flyer — Services Promo (A4)",   f"{CDN}/templates/dog-grooming/marketing/DG_Flyer_Services_Promo.png"),
    ("Flyer — New Client Offer (A4)", f"{CDN}/templates/dog-grooming/marketing/DG_Flyer_New_Client.png"),
    ("Price List / Service Menu (A4)",f"{CDN}/templates/dog-grooming/marketing/DG_Price_List.png"),
    ("Social Post — Booking Reminder",f"{CDN}/templates/dog-grooming/marketing/DG_Social_Booking_Reminder.png"),
    ("Social Post — Before & After",  f"{CDN}/templates/dog-grooming/marketing/DG_Social_Before_After.png"),
    ("Social Post — Grooming Tips",   f"{CDN}/templates/dog-grooming/marketing/DG_Social_Grooming_Tips.png"),
    ("Social Post — Testimonial",     f"{CDN}/templates/dog-grooming/marketing/DG_Social_Testimonial.png"),
    ("Social Post — Seasonal Promo",  f"{CDN}/templates/dog-grooming/marketing/DG_Social_Seasonal_Promo.png"),
]
FORMS_ITEMS = [
    ("Client Consent Form",           f"{CDN}/templates/dog-grooming/forms/DG_Client_Consent_Form.png"),
    ("Pre-Groom Health Assessment",   f"{CDN}/templates/dog-grooming/forms/DG_PreGroom_Health_Assessment.png"),
    ("Pet Intake Form",               f"{CDN}/templates/dog-grooming/forms/DG_Pet_Intake_Form.png"),
    ("Grooming Record Card",          f"{CDN}/templates/dog-grooming/forms/DG_Grooming_Record_Card.png"),
    ("Matting Consent & Shave Release",f"{CDN}/templates/dog-grooming/forms/DG_Matting_Consent.png"),
    ("Photo & Video Release",         f"{CDN}/templates/dog-grooming/forms/DG_Photo_Video_Release.png"),
    ("Cancellation & Deposit Policy", f"{CDN}/templates/dog-grooming/forms/DG_Cancellation_Policy.png"),
    ("Invoice",                       f"{CDN}/templates/dog-grooming/forms/DG_Invoice.png"),
    ("Booking Confirmation",          f"{CDN}/templates/dog-grooming/forms/DG_Booking_Confirmation.png"),
]
OPS_ITEMS = [
    ("Daily Appointment Schedule",    f"{CDN}/templates/dog-grooming/operations/DG_Daily_Schedule.png"),
    ("Cleaning Checklist",            f"{CDN}/templates/dog-grooming/operations/DG_Cleaning_Checklist.png"),
    ("Tool Sanitisation Log",         f"{CDN}/templates/dog-grooming/operations/DG_Tool_Sanitisation_Log.png"),
    ("Flea Policy Notice",            f"{CDN}/templates/dog-grooming/operations/DG_Flea_Policy.png"),
    ("Expenses Tracker",              f"{CDN}/templates/dog-grooming/operations/DG_Expenses_Tracker.png"),
    ("Income Tracker",                f"{CDN}/templates/dog-grooming/operations/DG_Income_Tracker.png"),
]

SECTIONS = [
    ("BRANDING KIT",        BRANDING_ITEMS,  "(10 templates — customise with your salon name)"),
    ("MARKETING TEMPLATES", MARKETING_ITEMS, "(8 templates — edit text and print or share online)"),
    ("CLIENT FORMS",        FORMS_ITEMS,     "(9 templates — print or use digitally)"),
    ("OPERATIONS",          OPS_ITEMS,       "(6 templates — internal use and compliance)"),
]


def generate_delivery_pdf(output_path: Path):
    PW, PH = RL_A4
    c = rl_canvas.Canvas(str(output_path), pagesize=RL_A4)

    def _page_header(title, subtitle=""):
        c.setFillColor(TEAL_HEX)
        c.rect(0, PH - 90, PW, 90, fill=1, stroke=0)
        c.setFillColor(GOLD_HEX)
        c.setFont("Helvetica-Bold", 22)
        c.drawString(50, PH - 55, "PurpleOcaz  •  Dog Grooming Mega Bundle")
        c.setFillColor(colors.white)
        c.setFont("Helvetica", 12)
        c.drawRightString(PW - 50, PH - 55, title)

    def _page_footer():
        c.setFillColor(TEAL_HEX)
        c.rect(0, 0, PW, 36, fill=1, stroke=0)
        c.setFillColor(GOLD_HEX)
        c.setFont("Helvetica", 10)
        c.drawCentredString(PW / 2, 12, "© PurpleOcaz  •  purpleocaz.etsy.com  •  All templates for personal & commercial use")

    # ── Cover page ─────────────────────────────────────────────────
    c.setFillColor(TEAL_HEX)
    c.rect(0, 0, PW, PH, fill=1, stroke=0)
    c.setFillColor(GOLD_HEX)
    c.setFont("Helvetica-Bold", 42)
    c.drawCentredString(PW / 2, PH - 180, "DOG GROOMING MEGA BUNDLE")
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(PW / 2, PH - 250, "33+ Professional Templates")
    c.setFillColor(GOLD_HEX)
    c.rect(80, PH - 320, PW - 160, 4, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica", 16)
    c.drawCentredString(PW / 2, PH - 370, "Thank you for your purchase!")
    c.drawCentredString(PW / 2, PH - 410, "Below you'll find download links for all 33 templates.")

    # Summary box
    c.setFillColor(colors.HexColor("#0A4A4F"))
    c.roundRect(80, PH - 680, PW - 160, 220, 10, fill=1, stroke=0)
    c.setFillColor(GOLD_HEX)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(PW / 2, PH - 490, "WHAT'S INCLUDED")
    c.setFillColor(GOLD_HEX)
    c.rect(80, PH - 500, PW - 160, 2, fill=1, stroke=0)
    items_summary = [
        ("Branding Kit",        "10 templates  —  Business cards, appointment cards, loyalty, gift cert, signs"),
        ("Marketing Templates", "8 templates   —  Flyers, price list, 5 social media posts"),
        ("Client Forms",        "9 templates   —  Consent, intake, grooming records, invoice & more"),
        ("Operations",          "6 templates   —  Schedule, checklists, trackers, policy notices"),
    ]
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(GOLD_HEX)
    y_s = PH - 530
    for cat, desc in items_summary:
        c.drawString(120, y_s, f"•  {cat}:")
        c.setFont("Helvetica", 12)
        c.setFillColor(colors.white)
        c.drawString(300, y_s, desc)
        c.setFont("Helvetica-Bold", 13)
        c.setFillColor(GOLD_HEX)
        y_s -= 36

    # How to use
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(PW / 2, PH - 730, "HOW TO USE YOUR TEMPLATES")
    c.setFont("Helvetica", 13)
    steps = [
        "1.  Click the download link next to each template below",
        "2.  Save the PNG to your device",
        "3.  Open in Canva (upload image → use as background), Adobe, or any editor",
        "4.  Edit text, colours, and add your logo",
        "5.  Save and print, or share online!",
    ]
    y_s = PH - 775
    for step in steps:
        c.drawCentredString(PW / 2, y_s, step)
        y_s -= 30

    c.setFillColor(GOLD_HEX)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(PW / 2, PH - 930,
        "Questions? Contact us: hello@purpleocaz.com  •  etsy.com/shop/PurpleOcaz")
    _page_footer()
    c.showPage()

    # ── Content pages ──────────────────────────────────────────────
    for sec_title, items, note in SECTIONS:
        _page_header(sec_title)
        y = PH - 130

        # Section title
        c.setFillColor(TEAL_HEX)
        c.rect(50, y - 30, PW - 100, 44, fill=1, stroke=0)
        c.setFillColor(GOLD_HEX)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(66, y - 12, sec_title)
        c.setFillColor(colors.white)
        c.setFont("Helvetica", 12)
        c.drawRightString(PW - 66, y - 12, note)
        y -= 52

        for i, (name, url) in enumerate(items):
            bg = CREAM_HEX if i % 2 == 0 else colors.HexColor("#EBE4DA")
            c.setFillColor(bg)
            c.rect(50, y - 30, PW - 100, 38, fill=1, stroke=0)
            c.setFillColor(GOLD_HEX)
            c.circle(72, y - 10, 5, fill=1, stroke=0)
            c.setFillColor(CHARCOAL_HEX)
            c.setFont("Helvetica-Bold", 12)
            c.drawString(86, y - 17, name)
            c.setFillColor(TEAL_HEX)
            c.setFont("Helvetica", 10)
            c.drawRightString(PW - 60, y - 17, "Click to download →")
            c.setFillColor(TEAL_HEX)
            c.linkURL(url, (PW - 200, y - 30, PW - 50, y + 10), relative=0)
            # underline
            c.rect(PW - 200, y - 18, 140, 1, fill=1, stroke=0)
            y -= 40

            if y < 80:
                _page_footer()
                c.showPage()
                _page_header(sec_title)
                y = PH - 130

        y -= 20
        _page_footer()
        c.showPage()

    c.save()
    print(f"  Delivery PDF saved: {output_path} ({output_path.stat().st_size // 1024} KB)")


# ─── Listing images ────────────────────────────────────────────────────────────

def build_listing_image_1_hero():
    """Hero: teal/gold, big template showcase."""
    img = Image.new("RGB", (W, H), (13, 92, 99))  # TEAL
    draw = ImageDraw.Draw(img)

    # Gold outer border
    for t in [20, 26, 32]:
        draw.rectangle([t, t, W - t, H - t], outline=(201, 169, 110), width=2)

    # Paw print corners
    for px, py in [(200, 200), (W - 200, 200), (200, H - 200), (W - 200, H - 200)]:
        paw_print(draw, px, py, size=80, fill=GOLD)

    # Main headline
    centred(draw, 140, "DOG GROOMING", GOLD, font(140, bold=True), canvas_w=W)
    centred(draw, 310, "MEGA BUNDLE", WHITE, font(140, bold=True), canvas_w=W)
    gold_rule(draw, 502, x0=200, x1=W - 200, thickness=10, canvas_w=W)

    centred(draw, 545, "33+ Professional Templates", WHITE, font(80), canvas_w=W)
    centred(draw, 650, "Everything a Dog Groomer Needs", GOLD, font(70), canvas_w=W)

    # 4 category pills
    cats = [("🐾 Branding", "10"), ("📣 Marketing", "8"), ("📋 Forms", "9"), ("⚙  Operations", "6")]
    pill_w, pill_h = 580, 140
    total = len(cats) * pill_w + (len(cats) - 1) * 40
    x0 = (W - total) // 2
    for i, (name, count) in enumerate(cats):
        px = x0 + i * (pill_w + 40)
        py = 790
        draw.rectangle([px, py, px + pill_w, py + pill_h], fill=(8, 60, 65))
        gold_rule(draw, py, x0=px, x1=px + pill_w, thickness=4, canvas_w=W)
        gold_rule(draw, py + pill_h - 4, x0=px, x1=px + pill_w, thickness=4, canvas_w=W)
        centred(draw, py + 14, count, GOLD, font(60, bold=True), canvas_w=pill_w)
        draw.text((px + pill_w // 2 - 110, py + 76), name, fill=WHITE, font=font(42))

    # Mini template preview grid (6 coloured blocks with labels)
    grid_items = [
        ("Business Card", TEAL),  ("Price List", (8, 60, 65)),   ("Consent Form", TEAL),
        ("Invoice", (8, 60, 65)), ("Flyer", TEAL),               ("Daily Schedule", (8, 60, 65)),
    ]
    gw, gh = 430, 320
    gap = 40
    gx0 = (W - (3 * gw + 2 * gap)) // 2
    gy0 = 1010
    for i, (name, col) in enumerate(grid_items):
        row, col_i = divmod(i, 3)
        gx = gx0 + col_i * (gw + gap)
        gy = gy0 + row * (gh + gap)
        draw.rectangle([gx, gy, gx + gw, gy + gh], fill=col)
        gold_rule(draw, gy, x0=gx, x1=gx + gw, thickness=4, canvas_w=W)
        paw_print(draw, gx + gw // 2, gy + gh // 2 - 20, size=50, fill=GOLD)
        centred(draw, gy + gh - 80, name, WHITE, font(34, bold=True), canvas_w=gw)

    gold_rule(draw, 1760, x0=200, x1=W - 200, thickness=10, canvas_w=W)

    # Features
    feats = ["✓  Print-ready PNG files", "✓  Edit in Canva / any editor",
             "✓  Instant download", "✓  Commercial use licence"]
    fx0 = (W - 2 * 1100 - 80) // 2
    for i, feat in enumerate(feats):
        r, c_i = divmod(i, 2)
        draw.text((fx0 + c_i * 1180, 1820 + r * 100), feat,
                  fill=CREAM if i % 2 == 0 else GOLD, font=font(56, bold=True))

    # Bottom CTA
    draw.rectangle([200, 2060, W - 200, 2280], fill=(8, 60, 65))
    gold_rule(draw, 2060, x0=200, x1=W - 200, thickness=6, canvas_w=W)
    gold_rule(draw, 2280, x0=200, x1=W - 200, thickness=6, canvas_w=W)
    centred(draw, 2100, "INSTANT DOWNLOAD  •  £39.99", GOLD, font(80, bold=True), canvas_w=W)
    centred(draw, 2200, "PurpleOcaz  •  purpleocaz.etsy.com", WHITE, font(50), canvas_w=W)

    # Paw trail bottom
    for i, px in enumerate(range(300, W - 200, 280)):
        paw_print(draw, px, 2380 + (i % 2) * 80, size=35, fill=GOLD)

    centred(draw, 2540, "Professional Dog Grooming Business Kit", WHITE, font(70, bold=True), canvas_w=W)
    centred(draw, 2640, "Teal & Gold Design  •  Warm & Trustworthy Style", GOLD, font(56), canvas_w=W)
    centred(draw, 2740, "Print or edit digitally  •  No design skills needed", WHITE, font(52), canvas_w=W)
    centred(draw, 2840, "Suitable for mobile groomers, salons & home groomers", CREAM, font(46), canvas_w=W)
    return img


def build_listing_image_2_whats_inside():
    """What's inside — 4 category breakdown."""
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 260], fill=TEAL)
    gold_rule(draw, 260, thickness=10, canvas_w=W)
    paw_print(draw, 130, 130, size=70, fill=GOLD)
    paw_print(draw, W - 130, 130, size=70, fill=GOLD)
    centred(draw, 50, "WHAT'S INSIDE YOUR BUNDLE", WHITE, font(110, bold=True), canvas_w=W)
    centred(draw, 180, "33+ print-ready PNG templates across 4 categories", GOLD, font(58), canvas_w=W)

    sections = [
        ("🐾 BRANDING KIT", "10 Templates", TEAL, [
            "Business Card — Dark & Light", "Appointment Card — Dark & Light",
            "Loyalty Stamp Card", "Gift Certificate",
            "Welcome Sign (A4)", "Thank You Card",
            "Referral Card", "Opening Hours Sign (A4)"
        ]),
        ("📣 MARKETING", "8 Templates", (8, 60, 65), [
            "Flyer — Services Promo (A4)", "Flyer — New Client Offer (A4)",
            "Price List / Service Menu (A4)",
            "Social Post — Booking Reminder",
            "Social Post — Before & After",
            "Social Post — Grooming Tips",
            "Social Post — Testimonial",
            "Social Post — Seasonal Promo"
        ]),
        ("📋 CLIENT FORMS", "9 Templates", TEAL, [
            "Client Consent Form", "Pre-Groom Health Assessment",
            "Pet Intake Form", "Grooming Record Card",
            "Matting Consent & Shave Release",
            "Photo & Video Release",
            "Cancellation & Deposit Policy",
            "Invoice", "Booking Confirmation"
        ]),
        ("⚙  OPERATIONS", "6 Templates", (8, 60, 65), [
            "Daily Appointment Schedule",
            "Cleaning Checklist",
            "Tool Sanitisation Log",
            "Flea Policy Notice",
            "Expenses Tracker",
            "Income Tracker"
        ]),
    ]

    box_w = (W - 160) // 2 - 20
    box_positions = [(80, 300), (80 + box_w + 40, 300), (80, 1700), (80 + box_w + 40, 1700)]
    for i, (title, count, col, items_list) in enumerate(sections):
        bx, by = box_positions[i]
        bh = 1340
        draw.rectangle([bx, by, bx + box_w, by + bh], fill=WHITE)
        draw.rectangle([bx, by, bx + box_w, by + 120], fill=col)
        gold_rule(draw, by + 120, x0=bx, x1=bx + box_w, thickness=5, canvas_w=W)
        draw.text((bx + 24, by + 18), title, fill=WHITE, font=font(52, bold=True))
        right(draw, bx + box_w - 20, by + 22, count, fill=GOLD, f=font(48, bold=True))
        iy = by + 144
        for j, item in enumerate(items_list):
            bg2 = CREAM_ALT if j % 2 else CREAM
            draw.rectangle([bx, iy, bx + box_w, iy + 76], fill=bg2)
            paw_print(draw, bx + 36, iy + 38, size=16, fill=col)
            draw.text((bx + 66, iy + 16), item, fill=CHARCOAL, font=font(36))
            iy += 76

    gold_rule(draw, 2860, x0=80, x1=W - 80, thickness=8, canvas_w=W)
    centred(draw, 2884, "Instant Download  •  Edit in Canva or any photo editor  •  Print-ready 300 DPI",
            TEAL, font(52, bold=True), canvas_w=W)
    return img


def build_listing_image_3_lifestyle():
    """Lifestyle mockup — styled with templates on desk."""
    img = Image.new("RGB", (W, H), CHARCOAL)
    draw = ImageDraw.Draw(img)

    # Textured background suggestion
    for i in range(0, W, 80):
        draw.line([(i, 0), (i, H)], fill=(30, 30, 30), width=1)

    draw.rectangle([0, 0, W, 14], fill=GOLD)
    gold_rule(draw, H - 14, thickness=14, canvas_w=W)

    paw_print(draw, W // 2, 220, size=130, fill=TEAL)
    centred(draw, 380, "BUILT FOR DOG GROOMERS", GOLD, font(100, bold=True), canvas_w=W)
    centred(draw, 504, "BY DOG GROOMERS", WHITE, font(100, bold=True), canvas_w=W)
    gold_rule(draw, 640, x0=200, x1=W - 200, thickness=8, canvas_w=W)

    scenarios = [
        ("🐾", "Start your grooming business\nwith professional branding from Day 1"),
        ("📋", "Use client consent forms\nand intake sheets to protect yourself legally"),
        ("📣", "Market your services with\nready-made flyers and social media posts"),
        ("⚙️", "Run your salon smoothly with\nschedules, checklists, and trackers"),
    ]
    y = 700
    for icon, text in scenarios:
        draw.rectangle([180, y, W - 180, y + 240], fill=(26, 64, 68))
        gold_rule(draw, y, x0=180, x1=W - 180, thickness=4, canvas_w=W)
        draw.text((220, y + 50), icon, fill=GOLD, font=font(90))
        lines = text.split("\n")
        draw.text((380, y + 44), lines[0], fill=WHITE, font=font(60, bold=True))
        draw.text((380, y + 122), lines[1], fill=CREAM, font=font(50))
        y += 280

    gold_rule(draw, 2000, x0=200, x1=W - 200, thickness=8, canvas_w=W)

    centred(draw, 2048, "Download once. Use forever.", GOLD, font(84, bold=True), canvas_w=W)
    centred(draw, 2160, "No subscription. No design experience needed.", WHITE, font(64), canvas_w=W)
    centred(draw, 2260, "All files are yours to keep and edit.", CREAM, font(60), canvas_w=W)

    draw.rectangle([180, 2380, W - 180, 2680], fill=TEAL)
    gold_rule(draw, 2380, x0=180, x1=W - 180, thickness=6, canvas_w=W)
    gold_rule(draw, 2680, x0=180, x1=W - 180, thickness=6, canvas_w=W)
    centred(draw, 2418, "✓  Print-ready 300 DPI PNGs", GOLD, font(68, bold=True), canvas_w=W)
    centred(draw, 2510, "✓  Teal, gold & cream palette — warm & trustworthy", WHITE, font(58), canvas_w=W)
    centred(draw, 2598, "✓  Paw print accents throughout", CREAM, font(58), canvas_w=W)

    for i, px in enumerate(range(220, W - 200, 240)):
        paw_print(draw, px, 2780 + (i % 2) * 70, size=30, fill=GOLD)
    centred(draw, 2920, "Professional Dog Grooming Business Bundle", WHITE, font(64), canvas_w=W)
    return img


def build_listing_image_4_how_it_works():
    """How it works — 4 steps."""
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 260], fill=TEAL)
    gold_rule(draw, 260, thickness=10, canvas_w=W)
    paw_print(draw, 130, 130, size=70, fill=GOLD)
    paw_print(draw, W - 130, 130, size=70, fill=GOLD)
    centred(draw, 55, "HOW IT WORKS", WHITE, font(120, bold=True), canvas_w=W)
    centred(draw, 190, "Download, edit, and use your templates in minutes", GOLD, font(60), canvas_w=W)

    steps = [
        ("1", "PURCHASE & DOWNLOAD",
         "Complete your purchase on Etsy. You'll receive an\n"
         "instant download with a PDF containing links to all\n"
         "33 templates. No waiting. No email required."),
        ("2", "OPEN A TEMPLATE",
         "Click any link in your delivery PDF to download\n"
         "the PNG file. Open it in Canva (free), Adobe, or\n"
         "any photo editing app on your phone or desktop."),
        ("3", "EDIT YOUR DETAILS",
         "Add your salon name, phone number, logo and any\n"
         "other details. Change colours to match your brand.\n"
         "Every template is fully editable — no design skills needed."),
        ("4", "PRINT OR SHARE",
         "Print at home, at a local print shop, or share\n"
         "digitally on social media. Templates are 300 DPI\n"
         "so they're sharp at any size."),
    ]

    y = 320
    for i, (num, title, desc) in enumerate(steps):
        col = TEAL if i % 2 == 0 else (8, 60, 65)
        draw.rectangle([120, y, W - 120, y + 560], fill=WHITE)
        gold_rule(draw, y, x0=120, x1=W - 120, thickness=3, canvas_w=W)

        # Step number circle (simulated with rectangle)
        draw.rectangle([120, y, 260, y + 560], fill=col)
        centred(draw, y + 200, num, GOLD, font(200, bold=True), canvas_w=140)
        draw.text((140, y + 88), "Step", fill=WHITE, font=font(40))

        # Content
        draw.text((300, y + 48), title, fill=TEAL, font=font(72, bold=True))
        gold_rule(draw, y + 140, x0=300, x1=W - 140, thickness=4, canvas_w=W)
        desc_y = y + 162
        for line in desc.split("\n"):
            draw.text((300, desc_y), line, fill=CHARCOAL, font=font(48))
            desc_y += 72

        # Paw accent
        paw_print(draw, W - 200, y + 280, size=60, fill=col)
        y += 600

    gold_rule(draw, 2720, x0=120, x1=W - 120, thickness=8, canvas_w=W)
    centred(draw, 2748, "That's it! Your professional grooming brand is ready to go.", TEAL,
            font(60, bold=True), canvas_w=W)
    centred(draw, 2848, "Questions? Message us on Etsy — we reply within 24 hours.", CHARCOAL,
            font(52), canvas_w=W)
    return img


def build_listing_image_5_why_buy():
    """Why buy this."""
    img = Image.new("RGB", (W, H), CHARCOAL)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 260], fill=TEAL)
    gold_rule(draw, 260, thickness=10, canvas_w=W)
    paw_print(draw, 130, 130, size=70, fill=GOLD)
    paw_print(draw, W - 130, 130, size=70, fill=GOLD)
    centred(draw, 50, "WHY BUY THIS BUNDLE?", WHITE, font(100, bold=True), canvas_w=W)
    centred(draw, 178, "Everything you need to run and market your grooming business", GOLD, font(52), canvas_w=W)

    reasons = [
        ("💰 Save Hundreds in Design Costs",
         "A designer would charge £500+ for this. You get 33+ professional\n"
         "templates for under £40. That's less than one groom."),
        ("⏱  Ready in Minutes, Not Days",
         "No brief, no revisions, no waiting. Download, add your name,\n"
         "and your branding is done. Start using it today."),
        ("🐶 Designed for Dog Groomers",
         "Not generic templates slapped with a paw. Built specifically for\n"
         "professional dog groomers — every form, every document."),
        ("📏 Print-Ready Quality",
         "300 DPI PNG files. Sharp at any size. Print at home, at a shop,\n"
         "or use digitally — they look stunning either way."),
        ("✏️  Easy to Edit",
         "Open in Canva (free account), add your details, done. No Photoshop,\n"
         "no InDesign, no design experience required."),
        ("🔄 One Payment, Lifetime Use",
         "Buy once, use forever. No subscription. No renewal fees.\n"
         "Use for your business for as long as you like."),
    ]
    y = 300
    for i, (title, desc) in enumerate(reasons):
        col = TEAL if i % 2 == 0 else (8, 60, 65)
        draw.rectangle([80, y, W - 80, y + 310], fill=col)
        gold_rule(draw, y, x0=80, x1=W - 80, thickness=3, canvas_w=W)
        draw.text((120, y + 28), title, fill=GOLD, font=font(62, bold=True))
        gold_rule(draw, y + 102, x0=120, x1=W - 120, thickness=3, canvas_w=W)
        for j, line in enumerate(desc.split("\n")):
            draw.text((120, y + 118 + j * 72), line, fill=WHITE, font=font(46))
        y += 336

    gold_rule(draw, 2320, x0=80, x1=W - 80, thickness=8, canvas_w=W)
    draw.rectangle([80, 2348, W - 80, 2620], fill=TEAL)
    centred(draw, 2382, "Dog Grooming Mega Bundle — £39.99", GOLD, font(80, bold=True), canvas_w=W)
    centred(draw, 2480, "33+ Templates  •  Instant Download  •  Commercial Use Included", WHITE,
            font(56), canvas_w=W)
    centred(draw, 2568, "Add to basket today →", CREAM, font(60, bold=True), canvas_w=W)
    for i, px in enumerate(range(220, W - 200, 240)):
        paw_print(draw, px, 2700 + (i % 2) * 70, size=28, fill=GOLD)
    centred(draw, 2844, "PurpleOcaz  •  Professional Business Templates", GOLD, font(52, bold=True), canvas_w=W)
    return img


def build_listing_image_6_canva_basics():
    """Canva Basics — how to edit in Canva."""
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 260], fill=TEAL)
    gold_rule(draw, 260, thickness=10, canvas_w=W)
    paw_print(draw, 130, 130, size=70, fill=GOLD)
    paw_print(draw, W - 130, 130, size=70, fill=GOLD)
    centred(draw, 55, "EDITING IN CANVA", WHITE, font(120, bold=True), canvas_w=W)
    centred(draw, 190, "A free tool. No experience needed.", GOLD, font(66), canvas_w=W)

    centred(draw, 310, "Canva is a FREE online design tool.", CHARCOAL, font(66, bold=True), canvas_w=W)
    centred(draw, 400, "You can use it on your phone, tablet, or computer.", CHARCOAL, font(56), canvas_w=W)

    steps = [
        ("Visit canva.com and create a free account", "It takes 30 seconds."),
        ("Click 'Upload' and upload the PNG file", "From your downloads folder."),
        ("Click 'Use in a design'", "Choose a custom size or use as-is."),
        ("Click on any text element", "Type over it with your own details."),
        ("Download your finished design", "PNG or PDF — both work great for print."),
    ]
    y = 490
    for i, (step, tip) in enumerate(steps):
        col = TEAL if i % 2 == 0 else (8, 60, 65)
        draw.rectangle([120, y, W - 120, y + 200], fill=WHITE)
        gold_rule(draw, y, x0=120, x1=W - 120, thickness=2, canvas_w=W)
        draw.rectangle([120, y, 260, y + 200], fill=col)
        centred(draw, y + 68, str(i + 1), WHITE, font(100, bold=True), canvas_w=140)
        draw.text((286, y + 30), step, fill=CHARCOAL, font=font(56, bold=True))
        draw.text((286, y + 104), tip, fill=TEAL, font=font(46))
        y += 228

    gold_rule(draw, y + 28, x0=120, x1=W - 120, thickness=8, canvas_w=W)
    draw.rectangle([120, y + 56, W - 120, y + 300], fill=TEAL)
    centred(draw, y + 88, "Already have Adobe, Photoshop, or Affinity?", GOLD, font(60, bold=True), canvas_w=W)
    centred(draw, y + 172, "Great! These templates work perfectly in any of them too.", WHITE,
            font(54), canvas_w=W)
    centred(draw, y + 254, "Just open the PNG and edit as you would any image.", CREAM,
            font(50), canvas_w=W)

    for i, px in enumerate(range(220, W - 200, 240)):
        paw_print(draw, px, y + 368 + (i % 2) * 60, size=26, fill=GOLD)
    centred(draw, y + 504, "Any questions? Message us on Etsy — happy to help!", CHARCOAL,
            font(52, bold=True), canvas_w=W)
    return img


def build_listing_image_7_please_note():
    """Please note / terms."""
    img = Image.new("RGB", (W, H), (13, 92, 99))  # TEAL
    draw = ImageDraw.Draw(img)
    for t in [20, 26]:
        draw.rectangle([t, t, W - t, H - t], outline=GOLD, width=3)
    paw_print(draw, W // 2, 200, size=130, fill=GOLD)
    centred(draw, 364, "PLEASE NOTE", WHITE, font(130, bold=True), canvas_w=W)
    gold_rule(draw, 528, x0=200, x1=W - 200, thickness=10, canvas_w=W)

    notes = [
        ("📦 This is a DIGITAL product",
         "No physical item will be posted. After purchase, you will\n"
         "receive an instant download link via Etsy."),
        ("🎨 Colours may vary slightly",
         "Screen and print colours can differ. We recommend a test\n"
         "print before printing large quantities."),
        ("✏️  Editable text fields",
         "All text is designed to be edited. The placeholder text\n"
         "shows you exactly where to add your details."),
        ("🔒 Licence included",
         "Personal and commercial use is included. You may use these\n"
         "templates for your business. Reselling the templates is not permitted."),
        ("🔄 No refunds on digital products",
         "Due to the nature of digital downloads, we cannot offer refunds\n"
         "once the file has been accessed. Please read the description carefully."),
        ("💬 We're here to help",
         "If you have any issues accessing your files or editing templates,\n"
         "message us on Etsy. We respond within 24 hours."),
    ]
    y = 580
    for i, (title, desc) in enumerate(notes):
        col = (8, 60, 65) if i % 2 == 0 else (6, 45, 50)
        draw.rectangle([120, y, W - 120, y + 340], fill=col)
        gold_rule(draw, y, x0=120, x1=W - 120, thickness=3, canvas_w=W)
        draw.text((160, y + 24), title, fill=GOLD, font=font(64, bold=True))
        gold_rule(draw, y + 100, x0=160, x1=W - 160, thickness=3, canvas_w=W)
        for j, line in enumerate(desc.split("\n")):
            draw.text((160, y + 116 + j * 76), line, fill=WHITE, font=font(48))
        y += 368

    gold_rule(draw, y + 20, x0=120, x1=W - 120, thickness=10, canvas_w=W)
    centred(draw, y + 52, "Thank you for shopping with PurpleOcaz 🐾", GOLD, font(70, bold=True), canvas_w=W)
    centred(draw, y + 148, "We hope these templates help your business thrive!", WHITE, font(58), canvas_w=W)
    return img


# ─── Main pipeline ─────────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 60)
    print("DOG GROOMING MEGA BUNDLE — PUBLISH PIPELINE")
    print("=" * 60)

    # ── Phase 4: Delivery PDF ───────────────────────────────────────
    print("\n=== Phase 4: Delivery PDF ===")
    pdf_path = OUTPUT_DIR / "DG_Mega_Bundle_DELIVERY.pdf"
    generate_delivery_pdf(pdf_path)
    pdf_url = upload_to_spaces(pdf_path, "templates/dog-grooming/DG_Mega_Bundle_DELIVERY.pdf",
                               content_type="application/pdf")
    print(f"  PDF URL: {pdf_url}")

    # ── Phase 5a: Build 7 listing images ───────────────────────────
    print("\n=== Phase 5a: Building 7 listing images ===")
    listing_builders = [
        ("DG_listing_01_hero.png",        build_listing_image_1_hero),
        ("DG_listing_02_whats_inside.png", build_listing_image_2_whats_inside),
        ("DG_listing_03_lifestyle.png",    build_listing_image_3_lifestyle),
        ("DG_listing_04_how_it_works.png", build_listing_image_4_how_it_works),
        ("DG_listing_05_why_buy.png",      build_listing_image_5_why_buy),
        ("DG_listing_06_canva_basics.png", build_listing_image_6_canva_basics),
        ("DG_listing_07_please_note.png",  build_listing_image_7_please_note),
    ]
    listing_paths = []
    for filename, fn in listing_builders:
        print(f"  Building {filename}...")
        img = fn()
        p = OUTPUT_DIR / filename
        img.save(p, "PNG")
        listing_paths.append(p)
        print(f"    Saved ({p.stat().st_size // 1024} KB)")

    # ── Phase 5b: Create Etsy draft listing ────────────────────────
    print("\n=== Phase 5b: Creating Etsy draft listing ===")
    TITLE = ("Dog Grooming Business Bundle | 33+ Canva Templates | "
             "Business Cards Forms Price List Flyers | Pet Groomer Branding Kit | Instant Download")
    DESCRIPTION = (
        "Run your dog grooming business like a pro with this complete 33+ template bundle.\n\n"
        "Everything a professional dog groomer needs — from client intake forms to social media "
        "posts, business cards to daily schedules. All templates come as print-ready PNG files "
        "you can edit in Canva (free), Adobe, or any photo app.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "WHAT'S INCLUDED (33+ TEMPLATES)\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🐾 BRANDING KIT (10 templates)\n"
        "Business Card Dark + Light, Appointment Card Dark + Light, Loyalty Stamp Card, "
        "Gift Certificate, Welcome Sign, Thank You Card, Referral Card, Opening Hours Sign\n\n"
        "📣 MARKETING (8 templates)\n"
        "Services Promo Flyer, New Client Offer Flyer, Price List / Service Menu, "
        "Booking Reminder Social Post, Before & After Post, Grooming Tips Post, "
        "Testimonial Post, Seasonal Promo Post\n\n"
        "📋 CLIENT FORMS (9 templates)\n"
        "Client Consent Form, Pre-Groom Health Assessment, Pet Intake Form, "
        "Grooming Record Card, Matting Consent & Shave Release, Photo & Video Release, "
        "Cancellation & Deposit Policy, Invoice, Booking Confirmation\n\n"
        "⚙ OPERATIONS (6 templates)\n"
        "Daily Appointment Schedule, Cleaning Checklist, Tool Sanitisation Log, "
        "Flea Policy Notice, Expenses Tracker, Income Tracker\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "HOW IT WORKS\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "1. Purchase and download instantly\n"
        "2. Open the delivery PDF — click any template to download\n"
        "3. Open in Canva (free) or any editor\n"
        "4. Add your salon name and details\n"
        "5. Print or share digitally\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "TECHNICAL DETAILS\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "• Format: PNG (300 DPI, print-ready)\n"
        "• Sizes: A4 (forms/flyers/signs), CR80 business card, 1080×1080 social posts\n"
        "• Palette: Deep teal, warm gold, cream — professional and trustworthy\n"
        "• Licence: Personal and commercial use included\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "PLEASE NOTE\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "This is a DIGITAL download. No physical item is posted. "
        "Refunds cannot be given on digital products once accessed. "
        "If you have any issues, message us — we respond within 24 hours.\n\n"
        "Suitable for mobile groomers, grooming salons, and home groomers."
    )
    TAGS = [
        "dog grooming bundle",
        "groomer templates",
        "dog grooming forms",
        "groomer biz card",
        "grooming price list",
        "pet business bundle",
        "dog groomer branding",
        "groomer consent form",
        "pet grooming canva",
        "grooming starter kit",
        "dog salon templates",
        "pet business forms",
        "groomer marketing",
    ]
    # Validate tags
    for t in TAGS:
        assert len(t) <= 20, f"Tag too long: '{t}' ({len(t)} chars)"
    assert len(TAGS) == len(set(TAGS)), "Duplicate tags"
    assert len(TAGS) == 13, f"Expected 13 tags, got {len(TAGS)}"

    params = urllib.parse.urlencode({
        "title": TITLE,
        "description": DESCRIPTION,
        "price": 39.99,
        "quantity": 999,
        "who_made": "i_did",
        "when_made": "2020_2025",
        "taxonomy_id": 1874,
        "type": "download",
        "is_supply": "false",
        "state": "draft",
        "tags": ",".join(TAGS),
    })
    result = etsy_request("POST", f"/shops/{SHOP_ID}/listings", params)
    listing_id = result["listing_id"]
    print(f"  ✓ Draft listing created: #{listing_id}")

    # ── Phase 5c: Upload 7 images ───────────────────────────────────
    print("\n=== Phase 5c: Uploading 7 listing images ===")
    for rank, img_path in enumerate(listing_paths, start=1):
        print(f"  Uploading rank {rank}: {img_path.name}...")
        r = upload_image_to_etsy(listing_id, img_path, rank)
        print(f"    Image ID: {r.get('listing_image_id')} | rank {r.get('rank')}")
        time.sleep(0.5)

    # Verify images
    imgs = etsy_request("GET", f"/listings/{listing_id}/images")
    print(f"\n  GET images → count: {len(imgs.get('results', []))}")
    for im in imgs.get("results", []):
        print(f"    rank {im['rank']} | ID {im['listing_image_id']}")

    # ── Phase 5d: Attach delivery PDF ──────────────────────────────
    print("\n=== Phase 5d: Attaching delivery PDF ===")
    file_result = upload_file_to_etsy(listing_id, pdf_path)
    print(f"  File attached: {file_result.get('filename')} | ID {file_result.get('listing_file_id')}")

    # Verify file
    files = etsy_request("GET", f"/shops/{SHOP_ID}/listings/{listing_id}/files")
    print(f"\n  GET files → count: {len(files.get('results', []))}")
    for fi in files.get("results", []):
        print(f"    {fi['filename']} | file_id: {fi.get('listing_file_id')}")

    # ── Update registry ─────────────────────────────────────────────
    reg_path = PROJECT / "config" / "design_registry.json"
    with open(reg_path) as f:
        reg = json.load(f)
    reg["designs"]["dog_grooming"]["_meta"]["listing_id"] = str(listing_id)
    with open(reg_path, "w") as f:
        json.dump(reg, f, indent=2)
    print(f"\n  Registry updated with listing_id: {listing_id}")

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print(f"  Listing ID : {listing_id}")
    print(f"  Etsy URL   : https://www.etsy.com/listing/{listing_id}")
    print(f"  State      : draft (review before publishing)")
    print(f"  Images     : {len(listing_paths)}")
    print(f"  PDF        : {pdf_path.name}")
    print("=" * 60)
    return listing_id


if __name__ == "__main__":
    listing_id = main()
    print(f"\nRun verification:\n  python scripts/verify_listing.py {listing_id} --bundle")
