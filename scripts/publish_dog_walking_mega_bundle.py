#!/usr/bin/env python3
"""
Dog Walking & Pet Sitting Mega Bundle — Full Build + Publish Pipeline
Builds 30 templates, delivery PDF, 7 listing images, Etsy draft listing.
Palette: Forest green #2D5F3E, warm gold #C9A96E, cream #F5F0E8, charcoal #1A1A1A
"""
import json, os, sys, time, uuid, urllib.request, urllib.error, urllib.parse
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

from dog_walking_design_system import (
    GREEN, GOLD, CREAM, CHARCOAL, WHITE, CREAM_ALT, GREEN_DARK,
    A4 as PIL_A4, BCARD, GIFT_CERT, SOCIAL, LISTING_IMG,
    font, centred, right, gold_rule, green_bar, section_head,
    field_line, field_pair, field_triple, checkbox, table_row,
    paw_print, a4_header, a4_footer, upload_to_spaces,
)

OUT       = PROJECT / "outputs" / "dog-walking"
TMPL      = OUT / "templates"
LISTING   = OUT / "listing"
for d in [TMPL, LISTING]:
    d.mkdir(parents=True, exist_ok=True)

CDN        = "https://purpleocaz-assets.lon1.digitaloceanspaces.com"
TOKEN_FILE = PROJECT / "workflows" / "etsy_analytics" / "etsy_tokens.json"
ETSY_BASE  = "https://openapi.etsy.com/v3/application"
API_KEY    = os.getenv("ETSY_API_KEYSTRING", "")
SECRET     = os.getenv("ETSY_SHARED_SECRET", "")
SHOP_ID    = os.getenv("ETSY_SHOP_ID", "34071205")
X_API_KEY  = f"{API_KEY}:{SECRET}"

NICHE = "dog-walking"
PFX   = "DW"  # filename prefix

W = H = 3000  # listing image canvas


# ══════════════════════════════════════════════════════════════════════════════
# ETSY HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def load_tokens():
    with open(TOKEN_FILE) as f:
        return json.load(f)


def etsy_request(method, path, body=None, content_type="application/x-www-form-urlencoded", retries=2):
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
            print("  [Auth] 401 — retrying...")
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


# ══════════════════════════════════════════════════════════════════════════════
# BRANDING TEMPLATES (9)
# ══════════════════════════════════════════════════════════════════════════════

def save_upload(img, filename, spaces_key):
    path = TMPL / filename
    img.save(path, "PNG")
    upload_to_spaces(path, spaces_key)
    return path


def build_business_card_dark():
    W, H = BCARD
    img = Image.new("RGB", (W, H), CHARCOAL)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, H], fill=CHARCOAL)
    # Gold top + bottom bars
    draw.rectangle([0, 0, W, 18], fill=GOLD)
    draw.rectangle([0, H - 18, W, H], fill=GOLD)
    # Green side accent
    draw.rectangle([0, 18, 12, H - 18], fill=GREEN)
    # Paw prints
    paw_print(draw, W - 130, 130, size=55, fill=GREEN)
    paw_print(draw, W - 200, 210, size=35, fill=(45, 95, 62, 180))
    # Text
    draw.text((60, 70), "YOUR BUSINESS NAME", fill=GOLD, font=font(52, bold=True))
    draw.text((60, 140), "Dog Walking & Pet Sitting", fill=CREAM, font=font(34))
    gold_rule(draw, 195, x0=60, x1=W - 60, thickness=3)
    draw.text((60, 215), "yourname@email.com", fill=WHITE, font=font(30))
    draw.text((60, 260), "07700 000000", fill=WHITE, font=font(30))
    draw.text((60, 305), "www.yourwebsite.co.uk", fill=WHITE, font=font(30))
    draw.text((60, 370), "Insured & DBS Checked", fill=GOLD, font=font(28, bold=True))
    return save_upload(img, f"{PFX}_Business_Card_Dark.png",
                       f"templates/{NICHE}/branding/{PFX}_Business_Card_Dark.png")


def build_business_card_light():
    W, H = BCARD
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 18], fill=GREEN)
    draw.rectangle([0, H - 18, W, H], fill=GREEN)
    draw.rectangle([0, 18, 12, H - 18], fill=GOLD)
    paw_print(draw, W - 130, 130, size=55, fill=GREEN)
    draw.text((60, 70), "YOUR BUSINESS NAME", fill=GREEN, font=font(52, bold=True))
    draw.text((60, 140), "Dog Walking & Pet Sitting", fill=CHARCOAL, font=font(34))
    gold_rule(draw, 195, x0=60, x1=W - 60, thickness=3)
    draw.text((60, 215), "yourname@email.com", fill=CHARCOAL, font=font(30))
    draw.text((60, 260), "07700 000000", fill=CHARCOAL, font=font(30))
    draw.text((60, 305), "www.yourwebsite.co.uk", fill=CHARCOAL, font=font(30))
    draw.text((60, 370), "Insured & DBS Checked", fill=GREEN, font=font(28, bold=True))
    return save_upload(img, f"{PFX}_Business_Card_Light.png",
                       f"templates/{NICHE}/branding/{PFX}_Business_Card_Light.png")


def build_appointment_card_dark():
    W, H = BCARD
    img = Image.new("RGB", (W, H), CHARCOAL)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 18], fill=GOLD)
    draw.rectangle([0, H - 18, W, H], fill=GOLD)
    draw.rectangle([0, 18, 12, H - 18], fill=GREEN)
    draw.text((60, 55), "YOUR BUSINESS NAME", fill=GOLD, font=font(42, bold=True))
    draw.text((60, 110), "APPOINTMENT CONFIRMED", fill=WHITE, font=font(36, bold=True))
    gold_rule(draw, 158, x0=60, x1=W - 60, thickness=3)
    draw.text((60, 175), "Date:", fill=CREAM, font=font(30, bold=True))
    draw.rectangle([160, 198, 540, 200], fill=GOLD)
    draw.text((60, 218), "Time:", fill=CREAM, font=font(30, bold=True))
    draw.rectangle([160, 241, 540, 243], fill=GOLD)
    draw.text((60, 261), "Service:", fill=CREAM, font=font(30, bold=True))
    draw.rectangle([210, 284, 700, 286], fill=GOLD)
    draw.text((60, 304), "Walker:", fill=CREAM, font=font(30, bold=True))
    draw.rectangle([195, 327, 700, 329], fill=GOLD)
    draw.text((60, 370), "Contact: 07700 000000", fill=GOLD, font=font(28))
    paw_print(draw, W - 120, H // 2, size=50, fill=GREEN)
    return save_upload(img, f"{PFX}_Appointment_Card_Dark.png",
                       f"templates/{NICHE}/branding/{PFX}_Appointment_Card_Dark.png")


def build_appointment_card_light():
    W, H = BCARD
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 18], fill=GREEN)
    draw.rectangle([0, H - 18, W, H], fill=GREEN)
    draw.rectangle([0, 18, 12, H - 18], fill=GOLD)
    draw.text((60, 55), "YOUR BUSINESS NAME", fill=GREEN, font=font(42, bold=True))
    draw.text((60, 110), "APPOINTMENT CONFIRMED", fill=CHARCOAL, font=font(36, bold=True))
    gold_rule(draw, 158, x0=60, x1=W - 60, thickness=3)
    draw.text((60, 175), "Date:", fill=CHARCOAL, font=font(30, bold=True))
    draw.rectangle([160, 198, 540, 200], fill=GREEN)
    draw.text((60, 218), "Time:", fill=CHARCOAL, font=font(30, bold=True))
    draw.rectangle([160, 241, 540, 243], fill=GREEN)
    draw.text((60, 261), "Service:", fill=CHARCOAL, font=font(30, bold=True))
    draw.rectangle([210, 284, 700, 286], fill=GREEN)
    draw.text((60, 304), "Walker:", fill=CHARCOAL, font=font(30, bold=True))
    draw.rectangle([195, 327, 700, 329], fill=GREEN)
    draw.text((60, 370), "Contact: 07700 000000", fill=GREEN, font=font(28))
    paw_print(draw, W - 120, H // 2, size=50, fill=GOLD)
    return save_upload(img, f"{PFX}_Appointment_Card_Light.png",
                       f"templates/{NICHE}/branding/{PFX}_Appointment_Card_Light.png")


def build_loyalty_card():
    W, H = BCARD
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 18], fill=GREEN)
    draw.rectangle([0, H - 18, W, H], fill=GREEN)
    draw.text((W // 2 - 250, 40), "LOYALTY REWARD CARD", fill=GREEN,
              font=font(40, bold=True))
    draw.text((W // 2 - 210, 90), "5th Walk FREE!", fill=GOLD, font=font(34, bold=True))
    gold_rule(draw, 138, x0=60, x1=W - 60, thickness=3)
    # 5 paw stamp boxes
    box_y = 170
    spacing = (W - 120) // 5
    for i in range(5):
        bx = 60 + i * spacing
        draw.rectangle([bx + 10, box_y, bx + spacing - 20, box_y + 200],
                       outline=GREEN, width=3)
        paw_print(draw, bx + (spacing - 20) // 2 + 10, box_y + 100,
                  size=40, fill=CREAM_ALT)
        centred(draw, box_y + 160, str(i + 1), CHARCOAL, font(28), canvas_w=spacing)
    draw.text((60, 390), "Client: _________________________", fill=CHARCOAL, font=font(28))
    draw.text((60, 435), "Phone:  _________________________", fill=CHARCOAL, font=font(28))
    draw.text((60, 480), "YOUR BUSINESS NAME", fill=GREEN, font=font(26, bold=True))
    draw.text((60, 510), "07700 000000", fill=CHARCOAL, font=font(26))
    return save_upload(img, f"{PFX}_Loyalty_Card.png",
                       f"templates/{NICHE}/branding/{PFX}_Loyalty_Card.png")


def build_gift_certificate():
    W, H = GIFT_CERT
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    # Green border
    draw.rectangle([0, 0, W, 40], fill=GREEN)
    draw.rectangle([0, H - 40, W, H], fill=GREEN)
    draw.rectangle([0, 40, 40, H - 40], fill=GREEN)
    draw.rectangle([W - 40, 40, W, H - 40], fill=GREEN)
    # Gold inner border
    draw.rectangle([55, 55, W - 55, H - 55], outline=GOLD, width=4)
    # Paw prints corners
    paw_print(draw, 110, 150, size=50, fill=GOLD)
    paw_print(draw, W - 110, 150, size=50, fill=GOLD)
    paw_print(draw, 110, H - 150, size=50, fill=GOLD)
    paw_print(draw, W - 110, H - 150, size=50, fill=GOLD)
    # Title
    centred(draw, 90, "GIFT CERTIFICATE", GREEN, font(90, bold=True), canvas_w=W)
    gold_rule(draw, 210, x0=100, x1=W - 100, thickness=4)
    centred(draw, 235, "Dog Walking & Pet Sitting Services", CHARCOAL, font(52), canvas_w=W)
    gold_rule(draw, 310, x0=100, x1=W - 100, thickness=4)
    centred(draw, 360, "This certificate entitles", CHARCOAL, font(44), canvas_w=W)
    # Fill lines
    draw.rectangle([300, 450, W - 300, 453], fill=GREEN)
    centred(draw, 465, "(Recipient Name)", CHARCOAL, font(34), canvas_w=W)
    centred(draw, 530, "to a", CHARCOAL, font(44), canvas_w=W)
    draw.rectangle([300, 600, W - 300, 603], fill=GREEN)
    centred(draw, 615, "(Service / Value)", CHARCOAL, font(34), canvas_w=W)
    centred(draw, 680, "provided by", CHARCOAL, font(40), canvas_w=W)
    centred(draw, 740, "YOUR BUSINESS NAME", GREEN, font(64, bold=True), canvas_w=W)
    gold_rule(draw, 840, x0=100, x1=W - 100, thickness=3)
    # Validity + signature
    draw.text((150, 890), "Valid until: _________________", CHARCOAL, font=font(38))
    draw.text((150, 945), "Certificate #: _______________", CHARCOAL, font=font(38))
    right(draw, W - 150, 890, "Signed: _________________", CHARCOAL, font(38))
    right(draw, W - 150, 945, "Date: ___________________", CHARCOAL, font(38))
    centred(draw, 1030, "07700 000000  |  www.yourwebsite.co.uk", CHARCOAL, font(36), canvas_w=W)
    centred(draw, 1080, "Insured & DBS Checked", GREEN, font(32, bold=True), canvas_w=W)
    return save_upload(img, f"{PFX}_Gift_Certificate.png",
                       f"templates/{NICHE}/branding/{PFX}_Gift_Certificate.png")


def build_welcome_sign():
    W, H = PIL_A4
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 340], fill=GREEN)
    draw.rectangle([0, H - 180, W, H], fill=GREEN)
    gold_rule(draw, 340, thickness=10, canvas_w=W)
    gold_rule(draw, H - 180, thickness=10, canvas_w=W)
    paw_print(draw, 160, 170, size=80, fill=GOLD)
    paw_print(draw, W - 160, 170, size=80, fill=GOLD)
    centred(draw, 60, "WELCOME!", WHITE, font(120, bold=True), canvas_w=W)
    centred(draw, 200, "YOUR BUSINESS NAME", GOLD, font(60, bold=True), canvas_w=W)
    centred(draw, 275, "Dog Walking & Pet Sitting", CREAM, font(44), canvas_w=W)
    # Body
    centred(draw, 400, "We're so happy to be caring for your", CHARCOAL, font(52), canvas_w=W)
    centred(draw, 470, "beloved pet!", CHARCOAL, font(52), canvas_w=W)
    gold_rule(draw, 560, x0=120, x1=W - 120, thickness=4)
    draw.text((120, 610), "YOUR DETAILS:", GREEN, font=font(46, bold=True))
    y = 680
    for line in ["Name:", "Address:", "Emergency Contact:", "Vet:", "Notes:"]:
        draw.text((120, y), line, CHARCOAL, font=font(42, bold=True))
        draw.rectangle([120, y + 58, W - 120, y + 62], fill=GREEN)
        y += 120
    gold_rule(draw, H - 240, x0=120, x1=W - 120, thickness=4)
    centred(draw, H - 210, "Insured & DBS Checked  |  07700 000000", WHITE, font(38), canvas_w=W)
    centred(draw, H - 155, "www.yourwebsite.co.uk", GOLD, font(36), canvas_w=W)
    centred(draw, H - 100, "© PurpleOcaz — purpleocaz.etsy.com", CREAM, font(30), canvas_w=W)
    return save_upload(img, f"{PFX}_Welcome_Sign.png",
                       f"templates/{NICHE}/branding/{PFX}_Welcome_Sign.png")


def build_thank_you_card():
    W, H = BCARD
    img = Image.new("RGB", (W, H), GREEN)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 16], fill=GOLD)
    draw.rectangle([0, H - 16, W, H], fill=GOLD)
    paw_print(draw, W - 110, 100, size=48, fill=GOLD)
    centred(draw, 40, "THANK YOU!", GOLD, font(70, bold=True), canvas_w=W)
    centred(draw, 130, "for choosing us to care for your pet.", CREAM, font(30), canvas_w=W)
    gold_rule(draw, 178, x0=60, x1=W - 60, thickness=3)
    centred(draw, 198, "We hope your pet had a wonderful time!", WHITE, font(28), canvas_w=W)
    centred(draw, 240, "We'd love a review — it really helps!", CREAM, font(26), canvas_w=W)
    gold_rule(draw, 285, x0=60, x1=W - 60, thickness=3)
    draw.text((60, 305), "YOUR BUSINESS NAME", fill=GOLD, font=font(32, bold=True))
    draw.text((60, 350), "07700 000000", fill=CREAM, font=font(28))
    draw.text((60, 390), "www.yourwebsite.co.uk", fill=CREAM, font=font(28))
    draw.text((60, 435), "Insured & DBS Checked", fill=GOLD, font=font(26, bold=True))
    return save_upload(img, f"{PFX}_Thank_You_Card.png",
                       f"templates/{NICHE}/branding/{PFX}_Thank_You_Card.png")


def build_referral_card():
    W, H = BCARD
    img = Image.new("RGB", (W, H), CHARCOAL)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 16], fill=GREEN)
    draw.rectangle([0, H - 16, W, H], fill=GREEN)
    paw_print(draw, W - 110, 110, size=48, fill=GREEN)
    centred(draw, 35, "REFER A FRIEND", GOLD, font(60, bold=True), canvas_w=W)
    centred(draw, 110, "& EARN A FREE WALK!", WHITE, font(38, bold=True), canvas_w=W)
    gold_rule(draw, 162, x0=60, x1=W - 60, thickness=3)
    centred(draw, 182, "For every friend you refer who books 3+", CREAM, font(26), canvas_w=W)
    centred(draw, 216, "sessions, YOU get a FREE 30-min walk!", CREAM, font(26), canvas_w=W)
    gold_rule(draw, 260, x0=60, x1=W - 60, thickness=3)
    draw.text((60, 280), "Referred by:", fill=CREAM, font=font(28, bold=True))
    draw.rectangle([230, 305, 700, 308], fill=GOLD)
    draw.text((60, 328), "Referee name:", fill=CREAM, font=font(28, bold=True))
    draw.rectangle([280, 353, 700, 356], fill=GOLD)
    draw.text((60, 375), "YOUR BUSINESS NAME", fill=GREEN, font=font(30, bold=True))
    draw.text((60, 415), "07700 000000", fill=GOLD, font=font(28))
    draw.text((60, 455), "Ts&Cs apply. Contact us for details.", fill=WHITE, font=font(24))
    return save_upload(img, f"{PFX}_Referral_Card.png",
                       f"templates/{NICHE}/branding/{PFX}_Referral_Card.png")


# ══════════════════════════════════════════════════════════════════════════════
# MARKETING TEMPLATES (8)
# ══════════════════════════════════════════════════════════════════════════════

def build_flyer_services():
    W, H = PIL_A4
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 480], fill=GREEN)
    draw.rectangle([0, H - 160, W, H], fill=GREEN)
    gold_rule(draw, 480, thickness=10, canvas_w=W)
    gold_rule(draw, H - 160, thickness=10, canvas_w=W)
    paw_print(draw, 140, 240, size=90, fill=GOLD)
    paw_print(draw, W - 140, 240, size=90, fill=GOLD)
    centred(draw, 60, "YOUR BUSINESS NAME", GOLD, font(72, bold=True), canvas_w=W)
    centred(draw, 160, "Dog Walking & Pet Sitting", CREAM, font(52), canvas_w=W)
    centred(draw, 240, "Professional  |  Insured  |  DBS Checked", WHITE, font(38), canvas_w=W)
    centred(draw, 320, "Serving [Your Area]", CREAM, font(36), canvas_w=W)
    # Services grid
    y = 530
    services = [
        ("Dog Walking", "30 or 60 min group & solo walks"),
        ("Puppy Visits", "Pop-in visits while you're at work"),
        ("Pet Sitting", "Daily drop-in care at your home"),
        ("Holiday Cover", "Full day care while you travel"),
        ("Feeding Visits", "Morning & evening feeds + check-in"),
        ("Overnight Sitting", "Peace of mind — we stay with them"),
    ]
    for name, desc in services:
        draw.rectangle([80, y, W - 80, y + 140], fill=WHITE, outline=GOLD, width=2)
        paw_print(draw, 145, y + 70, size=30, fill=GREEN)
        draw.text((210, y + 22), name, fill=GREEN, font=font(46, bold=True))
        draw.text((210, y + 82), desc, fill=CHARCOAL, font=font(34))
        y += 155
    gold_rule(draw, y + 10, x0=80, x1=W - 80, thickness=4)
    centred(draw, y + 30, "Book now — spaces are limited!", CHARCOAL, font(44, bold=True), canvas_w=W)
    centred(draw, H - 130, "07700 000000  |  www.yourwebsite.co.uk", CREAM, font(38), canvas_w=W)
    centred(draw, H - 80, "© PurpleOcaz — purpleocaz.etsy.com", CREAM, font(28), canvas_w=W)
    return save_upload(img, f"{PFX}_Flyer_Services.png",
                       f"templates/{NICHE}/marketing/{PFX}_Flyer_Services.png")


def build_flyer_new_client():
    W, H = PIL_A4
    img = Image.new("RGB", (W, H), CHARCOAL)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 420], fill=GREEN)
    draw.rectangle([0, H - 160, W, H], fill=GREEN)
    gold_rule(draw, 420, thickness=10, canvas_w=W)
    gold_rule(draw, H - 160, thickness=10, canvas_w=W)
    paw_print(draw, W - 160, 210, size=80, fill=GOLD)
    centred(draw, 60, "NEW CLIENT OFFER", GOLD, font(80, bold=True), canvas_w=W)
    centred(draw, 170, "YOUR BUSINESS NAME", CREAM, font(52), canvas_w=W)
    centred(draw, 250, "Dog Walking & Pet Sitting", WHITE, font(40), canvas_w=W)
    centred(draw, 310, "Insured & DBS Checked", GOLD, font(34), canvas_w=W)
    # Offer box
    draw.rectangle([80, 470, W - 80, 730], fill=GREEN, outline=GOLD, width=4)
    centred(draw, 510, "YOUR FIRST WALK", GOLD, font(68, bold=True), canvas_w=W)
    centred(draw, 590, "IS ON US!", WHITE, font(90, bold=True), canvas_w=W)
    centred(draw, 690, "Book 4 sessions and get your 1st FREE", CREAM, font(36), canvas_w=W)
    # Benefits
    y = 770
    for benefit in [
        "✔  GPS tracked walks — live updates to your phone",
        "✔  Fully insured & DBS checked for your peace of mind",
        "✔  Post-walk report with photos every single time",
        "✔  Flexible booking — mornings, afternoons, weekends",
        "✔  No extra charge for multiple dogs",
    ]:
        draw.text((120, y), benefit, fill=WHITE, font=font(38))
        y += 72
    gold_rule(draw, y + 20, x0=80, x1=W - 80, thickness=4)
    centred(draw, y + 50, "Limited spaces — book your free meet & greet today!", GOLD,
            font(40, bold=True), canvas_w=W)
    centred(draw, H - 130, "07700 000000  |  www.yourwebsite.co.uk", CREAM, font(38), canvas_w=W)
    centred(draw, H - 80, "© PurpleOcaz — purpleocaz.etsy.com", CREAM, font(28), canvas_w=W)
    return save_upload(img, f"{PFX}_Flyer_New_Client.png",
                       f"templates/{NICHE}/marketing/{PFX}_Flyer_New_Client.png")


def build_price_list():
    W, H = PIL_A4
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    y = a4_header(img, draw, "SERVICES & PRICE LIST", "Dog Walking & Pet Sitting")
    # Price table
    y = section_head(draw, 80, y, "DOG WALKING", width=W - 160, canvas_w=W)
    y += 10
    headers = ["Service", "Duration", "Price (solo)", "Price (group)"]
    widths  = [740, 380, 500, 500]
    y = table_row(draw, 80, y, headers, widths, header=True)
    rows = [
        ("Morning Walk", "30 min", "£XX.00", "£XX.00"),
        ("Afternoon Walk", "60 min", "£XX.00", "£XX.00"),
        ("Weekend Walk", "60 min", "£XX.00", "£XX.00"),
        ("Bank Holiday Walk", "60 min", "£XX.00", "£XX.00"),
    ]
    for i, row in enumerate(rows):
        y = table_row(draw, 80, y, row, widths, alt=bool(i % 2))
    y += 20
    y = section_head(draw, 80, y, "PET SITTING & VISITS", width=W - 160, canvas_w=W)
    y += 10
    widths2 = [840, 540, 740]
    y = table_row(draw, 80, y, ["Service", "Duration", "Price"], widths2, header=True)
    rows2 = [
        ("Drop-in Visit", "30 min", "£XX.00"),
        ("Half-day Sitting", "4 hrs", "£XX.00"),
        ("Full-day Sitting", "8 hrs", "£XX.00"),
        ("Overnight Sit", "Eve–Morning", "£XX.00"),
        ("Holiday Cover (daily)", "Full day", "£XX.00"),
    ]
    for i, row in enumerate(rows2):
        y = table_row(draw, 80, y, row, widths2, alt=bool(i % 2))
    y += 20
    y = section_head(draw, 80, y, "ADDITIONAL SERVICES", width=W - 160, canvas_w=W)
    y += 10
    y = table_row(draw, 80, y, ["Service", "Price"], [1680, 440], header=True)
    for i, row in enumerate([
        ("Extra dog (same household)", "+£X.00"),
        ("Admin / booking fee", "Free"),
        ("Meet & greet", "Free"),
    ]):
        y = table_row(draw, 80, y, row, [1680, 440], alt=bool(i % 2))
    y += 30
    draw.text((80, y), "* Prices are editable. All services subject to availability.",
              fill=CHARCOAL, font=font(30))
    a4_footer(draw, W, H)
    return save_upload(img, f"{PFX}_Price_List.png",
                       f"templates/{NICHE}/marketing/{PFX}_Price_List.png")


def _social_base(bg, accent):
    S = SOCIAL[0]
    img = Image.new("RGB", SOCIAL, bg)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, S, 16], fill=accent)
    draw.rectangle([0, S - 16, S, S], fill=accent)
    draw.rectangle([0, 16, 16, S - 16], fill=accent)
    draw.rectangle([S - 16, 16, S, S - 16], fill=accent)
    return img, draw, S


def build_social_booking():
    img, draw, S = _social_base(GREEN, GOLD)
    paw_print(draw, S - 100, 100, size=55, fill=GOLD)
    paw_print(draw, 100, S - 100, size=40, fill=GOLD)
    centred(draw, 80, "BOOKING NOW OPEN", GOLD, font(72, bold=True), canvas_w=S)
    centred(draw, 175, "Spaces are filling fast!", WHITE, font(52), canvas_w=S)
    gold_rule(draw, 260, x0=80, x1=S - 80, thickness=5)
    centred(draw, 300, "Solo & group walks", CREAM, font(46), canvas_w=S)
    centred(draw, 360, "Pet sitting & drop-in visits", CREAM, font(46), canvas_w=S)
    centred(draw, 420, "Holiday cover available", CREAM, font(46), canvas_w=S)
    draw.rectangle([80, 510, S - 80, 660], fill=GOLD, outline=WHITE, width=3)
    centred(draw, 540, "FREE Meet & Greet", GREEN, font(60, bold=True), canvas_w=S)
    centred(draw, 615, "Book yours today →", CHARCOAL, font(46, bold=True), canvas_w=S)
    centred(draw, 710, "YOUR BUSINESS NAME", GOLD, font(52, bold=True), canvas_w=S)
    centred(draw, 775, "Insured & DBS Checked", WHITE, font(40), canvas_w=S)
    centred(draw, 840, "07700 000000", CREAM, font(44), canvas_w=S)
    centred(draw, 920, "Follow for pet tips & updates", CREAM, font(36), canvas_w=S)
    return save_upload(img, f"{PFX}_Social_Booking.png",
                       f"templates/{NICHE}/marketing/{PFX}_Social_Booking.png")


def build_social_testimonial():
    img, draw, S = _social_base(CREAM, GREEN)
    paw_print(draw, S // 2, 115, size=60, fill=GREEN)
    centred(draw, 200, "\u201cWe couldn\u2019t be happier!\u201d", CHARCOAL,
            font(58, serifbold=True), canvas_w=S)
    gold_rule(draw, 285, x0=100, x1=S - 100, thickness=4)
    centred(draw, 320, "\u201cOur dog absolutely loves his daily walks.", CHARCOAL,
            font(40, serif=True), canvas_w=S)
    centred(draw, 375, "We get photos and updates every time.", CHARCOAL,
            font(40, serif=True), canvas_w=S)
    centred(draw, 430, "Wouldn\u2019t use anyone else!\u201d", CHARCOAL,
            font(40, serif=True), canvas_w=S)
    gold_rule(draw, 510, x0=100, x1=S - 100, thickness=4)
    centred(draw, 545, "— Sarah & Bruno, Happy Client", GREEN, font(40, bold=True), canvas_w=S)
    draw.rectangle([80, 640, S - 80, 660], fill=GOLD)
    centred(draw, 690, "⭐⭐⭐⭐⭐  5-Star Review", CHARCOAL, font(44, bold=True), canvas_w=S)
    draw.rectangle([80, 780, S - 80, 900], fill=GREEN)
    centred(draw, 815, "YOUR BUSINESS NAME", GOLD, font(54, bold=True), canvas_w=S)
    centred(draw, 870, "Dog Walking & Pet Sitting", WHITE, font(38), canvas_w=S)
    centred(draw, 945, "07700 000000  |  Insured & DBS", CHARCOAL, font(34), canvas_w=S)
    return save_upload(img, f"{PFX}_Social_Testimonial.png",
                       f"templates/{NICHE}/marketing/{PFX}_Social_Testimonial.png")


def build_social_tips():
    img, draw, S = _social_base(CHARCOAL, GOLD)
    paw_print(draw, 120, 120, size=55, fill=GREEN)
    centred(draw, 65, "PET CARE TIP OF THE WEEK", GOLD, font(54, bold=True), canvas_w=S)
    gold_rule(draw, 155, x0=60, x1=S - 60, thickness=5)
    centred(draw, 190, "#1: Daily Exercise", WHITE, font(62, bold=True), canvas_w=S)
    centred(draw, 275, "Dogs need 30–60 minutes of exercise", CREAM, font(42), canvas_w=S)
    centred(draw, 330, "daily for good physical and mental health.", CREAM, font(42), canvas_w=S)
    centred(draw, 410, "Signs your dog needs more walks:", GOLD, font(44, bold=True), canvas_w=S)
    tips = ["Destructive behaviour at home",
            "Excessive barking or whining",
            "Weight gain or lethargy",
            "Pulling hard on the lead"]
    y = 470
    for tip in tips:
        paw_print(draw, 95, y + 20, size=18, fill=GREEN)
        draw.text((130, y), tip, fill=WHITE, font=font(38))
        y += 58
    draw.rectangle([60, 740, S - 60, 880], fill=GREEN, outline=GOLD, width=3)
    centred(draw, 770, "We can help!", GOLD, font(58, bold=True), canvas_w=S)
    centred(draw, 840, "Professional walks from £XX/session", WHITE, font(40), canvas_w=S)
    centred(draw, 940, "YOUR BUSINESS NAME", GOLD, font(50, bold=True), canvas_w=S)
    centred(draw, 1000, "07700 000000", CREAM, font(40), canvas_w=S)
    return save_upload(img, f"{PFX}_Social_Tips.png",
                       f"templates/{NICHE}/marketing/{PFX}_Social_Tips.png")


def build_social_seasonal():
    img, draw, S = _social_base(GREEN, GOLD)
    paw_print(draw, S - 120, 120, size=65, fill=GOLD)
    paw_print(draw, 120, S - 120, size=50, fill=GOLD)
    centred(draw, 65, "SUMMER SPECIAL OFFER", GOLD, font(64, bold=True), canvas_w=S)
    centred(draw, 148, "Keep your dog cool & happy", WHITE, font(46), canvas_w=S)
    gold_rule(draw, 220, x0=80, x1=S - 80, thickness=5)
    centred(draw, 260, "BOOK 5 WALKS", CREAM, font(54, bold=True), canvas_w=S)
    centred(draw, 325, "GET 1 FREE", GOLD, font(90, bold=True), canvas_w=S)
    gold_rule(draw, 440, x0=80, x1=S - 80, thickness=5)
    centred(draw, 480, "Early morning & evening walks", CREAM, font(42), canvas_w=S)
    centred(draw, 535, "available to beat the heat", CREAM, font(42), canvas_w=S)
    draw.rectangle([80, 620, S - 80, 760], fill=GOLD)
    centred(draw, 650, "Valid until: [DATE]", GREEN, font(48, bold=True), canvas_w=S)
    centred(draw, 710, "Quote: SUMMER25 when booking", CHARCOAL, font(40, bold=True), canvas_w=S)
    centred(draw, 820, "YOUR BUSINESS NAME", CREAM, font(52, bold=True), canvas_w=S)
    centred(draw, 885, "07700 000000", WHITE, font(44), canvas_w=S)
    centred(draw, 960, "Spaces limited — book today!", GOLD, font(42, bold=True), canvas_w=S)
    return save_upload(img, f"{PFX}_Social_Seasonal.png",
                       f"templates/{NICHE}/marketing/{PFX}_Social_Seasonal.png")


def build_social_pet_of_week():
    img, draw, S = _social_base(CREAM, GREEN)
    draw.rectangle([0, 0, S, 130], fill=GREEN)
    paw_print(draw, 80, 65, size=45, fill=GOLD)
    paw_print(draw, S - 80, 65, size=45, fill=GOLD)
    centred(draw, 25, "PET OF THE WEEK", GOLD, font(68, bold=True), canvas_w=S)
    centred(draw, 100, "Meet our star client!", WHITE, font(40), canvas_w=S)
    # Photo placeholder
    draw.rectangle([140, 160, S - 140, 660], fill=CREAM_ALT, outline=GOLD, width=4)
    centred(draw, 380, "ADD YOUR PET PHOTO HERE", CHARCOAL, font(44), canvas_w=S)
    gold_rule(draw, 680, x0=80, x1=S - 80, thickness=5)
    draw.text((80, 710), "Name:", CHARCOAL, font=font(44, bold=True))
    draw.rectangle([230, 755, S - 80, 758], fill=GREEN)
    draw.text((80, 775), "Breed:", CHARCOAL, font=font(44, bold=True))
    draw.rectangle([240, 820, S - 80, 823], fill=GREEN)
    draw.text((80, 840), "Fave walk:", CHARCOAL, font=font(44, bold=True))
    draw.rectangle([330, 885, S - 80, 888], fill=GREEN)
    draw.rectangle([80, 935, S - 80, 1030], fill=GREEN)
    centred(draw, 960, "YOUR BUSINESS NAME | 07700 000000", GOLD, font(40, bold=True), canvas_w=S)
    centred(draw, 1010, "Tag us to be featured! #YourBusinessName", WHITE, font(34), canvas_w=S)
    return save_upload(img, f"{PFX}_Social_Pet_Of_Week.png",
                       f"templates/{NICHE}/marketing/{PFX}_Social_Pet_Of_Week.png")


# ══════════════════════════════════════════════════════════════════════════════
# CLIENT FORMS (8)
# ══════════════════════════════════════════════════════════════════════════════

def build_client_agreement():
    W, H = PIL_A4
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)
    y = a4_header(img, draw, "CLIENT SERVICE AGREEMENT")
    y = section_head(draw, 80, y + 10, "CLIENT DETAILS", width=W - 160)
    y += 14
    y = field_pair(draw, 120, y, "Client Full Name:", "Phone Number:", total_w=2240)
    y = field_pair(draw, 120, y, "Email Address:", "Address:", total_w=2240)
    y = field_pair(draw, 120, y, "Emergency Contact:", "Emergency Phone:", total_w=2240)
    y += 8
    y = section_head(draw, 80, y, "PET DETAILS", width=W - 160)
    y += 14
    y = field_pair(draw, 120, y, "Pet Name:", "Breed / Age:", total_w=2240)
    y = field_pair(draw, 120, y, "Vet Name:", "Vet Phone:", total_w=2240)
    y = field_line(draw, 120, y, "Known Health Conditions / Allergies:", width=2240)
    y = field_line(draw, 120, y, "Medications:", width=2240)
    y += 8
    y = section_head(draw, 80, y, "SERVICE & AGREEMENT TERMS", width=W - 160)
    y += 14
    terms = [
        "All services are subject to a meet & greet assessment at no charge.",
        "Payment is due within 24 hours of invoice. Late fees of £X/day apply.",
        "24-hour cancellation required or 50% of the session fee is charged.",
        "Walker is authorised to seek veterinary care in an emergency.",
        "Client confirms their pet is up to date with vaccinations and flea treatment.",
        "Photos/videos of the pet may be used for marketing unless opted out below.",
    ]
    for term in terms:
        paw_print(draw, 110, y + 22, size=16, fill=GREEN)
        draw.text((145, y), term, fill=CHARCOAL, font=font(30))
        y += 52
    y += 10
    y = checkbox(draw, 120, y, "I opt OUT of having my pet's photos used in marketing", font_size=32)
    y += 20
    y = section_head(draw, 80, y, "SIGNATURES", width=W - 160)
    y += 20
    draw.text((120, y), "Client Signature:", CHARCOAL, font=font(36, bold=True))
    draw.rectangle([120, y + 58, 1100, y + 61], fill=GREEN)
    draw.text((120, y + 80), "Date:", CHARCOAL, font=font(36, bold=True))
    draw.rectangle([220, y + 138, 700, y + 141], fill=GREEN)
    draw.text((1200, y), "Walker Signature:", CHARCOAL, font=font(36, bold=True))
    draw.rectangle([1200, y + 58, 2300, y + 61], fill=GREEN)
    a4_footer(draw, W, H)
    return save_upload(img, f"{PFX}_Client_Agreement.png",
                       f"templates/{NICHE}/forms/{PFX}_Client_Agreement.png")


def build_pet_info_sheet():
    W, H = PIL_A4
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)
    y = a4_header(img, draw, "PET INFORMATION SHEET")
    y = section_head(draw, 80, y + 10, "PET PROFILE", width=W - 160)
    y += 14
    y = field_pair(draw, 120, y, "Pet Name:", "Nickname:", total_w=2240)
    y = field_triple(draw, 120, y, ["Breed:", "Age:", "Gender:"], total_w=2240)
    y = field_triple(draw, 120, y, ["Colour / Markings:", "Weight:", "Neutered?"], total_w=2240)
    y = field_line(draw, 120, y, "Microchip Number:", width=2240)
    y += 8
    y = section_head(draw, 80, y, "TEMPERAMENT", width=W - 160)
    y += 14
    y = field_line(draw, 120, y, "Temperament (friendly / nervous / reactive / other):", width=2240)
    y = field_line(draw, 120, y, "Good with other dogs?  Y / N   Notes:", width=2240)
    y = field_line(draw, 120, y, "Good with children?  Y / N   Notes:", width=2240)
    y = field_line(draw, 120, y, "Known triggers / fears:", width=2240)
    y += 8
    y = section_head(draw, 80, y, "HEALTH & VET", width=W - 160)
    y += 14
    y = field_pair(draw, 120, y, "Vet Practice Name:", "Vet Phone:", total_w=2240)
    y = field_line(draw, 120, y, "Health Conditions / Allergies:", width=2240)
    y = field_line(draw, 120, y, "Current Medications (name & dose):", width=2240)
    y = field_pair(draw, 120, y, "Vaccinations up to date? Y / N", "Last flea/wormed:", total_w=2240)
    y += 8
    y = section_head(draw, 80, y, "FEEDING & ROUTINE", width=W - 160)
    y += 14
    y = field_triple(draw, 120, y, ["Food Brand:", "Amount:", "Times per day:"], total_w=2240)
    y = field_line(draw, 120, y, "Feeding instructions / restrictions:", width=2240)
    y = field_line(draw, 120, y, "Favourite treats (if walker may give):", width=2240)
    y = field_line(draw, 120, y, "Favourite toys / comforters:", width=2240)
    a4_footer(draw, W, H)
    return save_upload(img, f"{PFX}_Pet_Info_Sheet.png",
                       f"templates/{NICHE}/forms/{PFX}_Pet_Info_Sheet.png")


def build_walk_log():
    W, H = PIL_A4
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)
    y = a4_header(img, draw, "DAILY WALK LOG")
    y += 10
    draw.text((120, y), "Client:", CHARCOAL, font=font(38, bold=True))
    draw.rectangle([230, y + 55, 1100, y + 58], fill=GREEN)
    draw.text((1200, y), "Pet Name:", CHARCOAL, font=font(38, bold=True))
    draw.rectangle([1430, y + 55, 2300, y + 58], fill=GREEN)
    draw.text((120, y + 80), "Month:", CHARCOAL, font=font(38, bold=True))
    draw.rectangle([240, y + 135, 900, y + 138], fill=GREEN)
    y += 180
    # Walk log table
    hdrs  = ["Date", "Time Out", "Time In", "Duration", "Route/Notes", "Toilet", "Initials"]
    wids  = [220, 220, 220, 200, 760, 160, 160]
    y = table_row(draw, 80, y, hdrs, wids, header=True, row_h=68)
    for i in range(18):
        y = table_row(draw, 80, y, [""] * 7, wids, alt=bool(i % 2), row_h=80)
    a4_footer(draw, W, H)
    return save_upload(img, f"{PFX}_Walk_Log.png",
                       f"templates/{NICHE}/forms/{PFX}_Walk_Log.png")


def build_feeding_schedule():
    W, H = PIL_A4
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)
    y = a4_header(img, draw, "FEEDING SCHEDULE")
    y += 10
    draw.text((120, y), "Pet Name:", CHARCOAL, font=font(38, bold=True))
    draw.rectangle([320, y + 55, 1100, y + 58], fill=GREEN)
    draw.text((1200, y), "Owner:", CHARCOAL, font=font(38, bold=True))
    draw.rectangle([1380, y + 55, 2300, y + 58], fill=GREEN)
    y += 140
    y = section_head(draw, 80, y, "FOOD DETAILS", width=W - 160)
    y += 14
    y = field_pair(draw, 120, y, "Dry Food Brand & Amount:", "Wet Food Brand & Amount:", total_w=2240)
    y = field_pair(draw, 120, y, "Treats Allowed? Y / N", "Treat Brand/Type:", total_w=2240)
    y = field_line(draw, 120, y, "Dietary restrictions / allergies:", width=2240)
    y += 10
    y = section_head(draw, 80, y, "DAILY FEEDING SCHEDULE", width=W - 160)
    y += 10
    hdrs = ["Meal", "Time", "Food & Amount", "Notes"]
    wids = [240, 280, 900, 700]
    y = table_row(draw, 80, y, hdrs, wids, header=True)
    meals = ["Morning", "Midday", "Afternoon", "Evening", "Late Night"]
    for i, meal in enumerate(meals):
        y = table_row(draw, 80, y, [meal, "", "", ""], wids, alt=bool(i % 2), row_h=90)
    y += 10
    y = section_head(draw, 80, y, "WATER & SUPPLEMENTS", width=W - 160)
    y += 14
    y = field_line(draw, 120, y, "Water: always available Y / N   Refresh every:", width=2240)
    y = field_line(draw, 120, y, "Supplements (name, dose, timing):", width=2240)
    y = field_line(draw, 120, y, "Medications with food (name, dose, timing):", width=2240)
    a4_footer(draw, W, H)
    return save_upload(img, f"{PFX}_Feeding_Schedule.png",
                       f"templates/{NICHE}/forms/{PFX}_Feeding_Schedule.png")


def build_emergency_contact_card():
    W, H = BCARD
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 18], fill=GREEN)
    draw.rectangle([0, H - 18, W, H], fill=GREEN)
    draw.rectangle([0, 0, W, 80], fill=GREEN)
    centred(draw, 20, "EMERGENCY CONTACT CARD", WHITE, font(36, bold=True), canvas_w=W)
    draw.text((40, 100), "Pet:", CHARCOAL, font=font(30, bold=True))
    draw.rectangle([110, 132, 500, 135], fill=GREEN)
    draw.text((40, 155), "Owner:", CHARCOAL, font=font(30, bold=True))
    draw.rectangle([160, 187, 500, 190], fill=GREEN)
    draw.text((40, 210), "Phone:", CHARCOAL, font=font(30, bold=True))
    draw.rectangle([160, 242, 500, 245], fill=GREEN)
    draw.text((40, 265), "Alt Phone:", CHARCOAL, font=font(30, bold=True))
    draw.rectangle([220, 297, 500, 300], fill=GREEN)
    draw.line([(550, 90), (550, H - 30)], fill=GOLD, width=3)
    draw.text((570, 100), "Vet:", CHARCOAL, font=font(30, bold=True))
    draw.rectangle([630, 132, 1010, 135], fill=GREEN)
    draw.text((570, 155), "Vet Ph:", CHARCOAL, font=font(30, bold=True))
    draw.rectangle([700, 187, 1010, 190], fill=GREEN)
    draw.text((570, 210), "Walker:", CHARCOAL, font=font(30, bold=True))
    draw.rectangle([710, 242, 1010, 245], fill=GREEN)
    draw.text((570, 265), "W. Ph:", CHARCOAL, font=font(30, bold=True))
    draw.rectangle([690, 297, 1010, 300], fill=GREEN)
    draw.text((40, 330), "Allergies:", CHARCOAL, font=font(30, bold=True))
    draw.rectangle([220, 362, 1010, 365], fill=GREEN)
    draw.text((40, 385), "Insurance:", CHARCOAL, font=font(30, bold=True))
    draw.rectangle([240, 417, 1010, 420], fill=GREEN)
    return save_upload(img, f"{PFX}_Emergency_Contact_Card.png",
                       f"templates/{NICHE}/forms/{PFX}_Emergency_Contact_Card.png")


def build_key_handover_form():
    W, H = PIL_A4
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)
    y = a4_header(img, draw, "KEY HANDOVER FORM")
    y += 10
    y = section_head(draw, 80, y, "CLIENT & PROPERTY DETAILS", width=W - 160)
    y += 14
    y = field_pair(draw, 120, y, "Client Name:", "Phone:", total_w=2240)
    y = field_line(draw, 120, y, "Property Address:", width=2240)
    y = field_pair(draw, 120, y, "Alarm Code:", "Code pad location:", total_w=2240)
    y = field_line(draw, 120, y, "Entry instructions (lockbox / keysafe / doorbell):", width=2240)
    y += 10
    y = section_head(draw, 80, y, "KEY DETAILS", width=W - 160)
    y += 14
    hdrs = ["Key Ref", "Description", "Copied?", "Date Given", "Date Returned"]
    wids = [220, 640, 200, 340, 340]
    y = table_row(draw, 80, y, hdrs, wids, header=True)
    for i in range(6):
        y = table_row(draw, 80, y, [""] * 5, wids, alt=bool(i % 2), row_h=80)
    y += 16
    y = section_head(draw, 80, y, "HANDOVER AGREEMENT", width=W - 160)
    y += 14
    terms = [
        "Keys are held securely and used only during booked service periods.",
        "Keys will be returned immediately upon request or service termination.",
        "Walker accepts responsibility for the safe-keeping of keys whilst in their care.",
        "Walker will not copy keys without written permission from the client.",
    ]
    for t in terms:
        paw_print(draw, 110, y + 18, size=14, fill=GREEN)
        draw.text((145, y), t, CHARCOAL, font=font(32))
        y += 52
    y += 20
    draw.text((120, y), "Client Signature:", CHARCOAL, font=font(36, bold=True))
    draw.rectangle([120, y + 58, 1100, y + 61], fill=GREEN)
    draw.text((120, y + 80), "Date:", CHARCOAL, font=font(36, bold=True))
    draw.rectangle([220, y + 138, 700, y + 141], fill=GREEN)
    draw.text((1200, y), "Walker Signature:", CHARCOAL, font=font(36, bold=True))
    draw.rectangle([1200, y + 58, 2300, y + 61], fill=GREEN)
    a4_footer(draw, W, H)
    return save_upload(img, f"{PFX}_Key_Handover_Form.png",
                       f"templates/{NICHE}/forms/{PFX}_Key_Handover_Form.png")


def build_invoice():
    W, H = PIL_A4
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 260], fill=GREEN)
    gold_rule(draw, 260, thickness=10, canvas_w=W)
    paw_print(draw, 160, 130, size=70, fill=GOLD)
    draw.text((280, 60), "YOUR BUSINESS NAME", fill=GOLD, font=font(64, bold=True))
    draw.text((280, 140), "Dog Walking & Pet Sitting", fill=CREAM, font=font(40))
    draw.text((280, 195), "07700 000000  |  yourname@email.com", fill=WHITE, font=font(32))
    centred(draw, 300, "INVOICE", CHARCOAL, font(80, bold=True), canvas_w=W)
    # Invoice meta
    draw.text((120, 420), "Invoice #:", CHARCOAL, font=font(38, bold=True))
    draw.rectangle([310, 460, 900, 463], fill=GREEN)
    draw.text((120, 485), "Date:", CHARCOAL, font=font(38, bold=True))
    draw.rectangle([225, 525, 900, 528], fill=GREEN)
    draw.text((120, 550), "Due:", CHARCOAL, font=font(38, bold=True))
    draw.rectangle([210, 590, 900, 593], fill=GREEN)
    draw.text((1200, 420), "Bill To:", CHARCOAL, font=font(38, bold=True))
    draw.rectangle([1200, 460, 2300, 463], fill=GREEN)
    draw.rectangle([1200, 525, 2300, 528], fill=GREEN)
    draw.rectangle([1200, 590, 2300, 593], fill=GREEN)
    # Items table
    y = 660
    hdrs = ["Date", "Service", "Duration", "Rate", "Total"]
    wids = [300, 720, 280, 350, 270]
    y = table_row(draw, 80, y, hdrs, wids, header=True)
    for i in range(8):
        y = table_row(draw, 80, y, [""] * 5, wids, alt=bool(i % 2), row_h=85)
    # Totals
    draw.rectangle([1680, y + 10, 2300, y + 80], fill=CREAM_ALT)
    draw.text((1700, y + 20), "Subtotal:", CHARCOAL, font=font(36, bold=True))
    right(draw, 2280, y + 20, "£", CHARCOAL, font(36, bold=True))
    y += 80
    draw.rectangle([1680, y + 10, 2300, y + 80], fill=GREEN)
    draw.text((1700, y + 20), "TOTAL DUE:", WHITE, font=font(40, bold=True))
    right(draw, 2280, y + 20, "£", GOLD, font(40, bold=True))
    y += 100
    draw.text((120, y), "Payment: Bank Transfer / Cash / Card", CHARCOAL, font=font(34))
    draw.text((120, y + 50), "Sort code: XX-XX-XX  |  Account: XXXXXXXX", CHARCOAL, font=font(34))
    draw.text((120, y + 100), "Thank you for your business!", GREEN, font=font(36, bold=True))
    a4_footer(draw, W, H)
    return save_upload(img, f"{PFX}_Invoice.png",
                       f"templates/{NICHE}/forms/{PFX}_Invoice.png")


def build_booking_confirmation():
    W, H = PIL_A4
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)
    y = a4_header(img, draw, "BOOKING CONFIRMATION")
    y += 10
    y = section_head(draw, 80, y, "CLIENT DETAILS", width=W - 160)
    y += 14
    y = field_pair(draw, 120, y, "Client Name:", "Phone:", total_w=2240)
    y = field_pair(draw, 120, y, "Pet Name(s):", "Address:", total_w=2240)
    y += 10
    y = section_head(draw, 80, y, "BOOKING DETAILS", width=W - 160)
    y += 14
    y = field_pair(draw, 120, y, "Service:", "Walker:", total_w=2240)
    y = field_pair(draw, 120, y, "Date:", "Time:", total_w=2240)
    y = field_pair(draw, 120, y, "Duration:", "Location:", total_w=2240)
    y = field_line(draw, 120, y, "Special Instructions:", width=2240)
    y += 10
    y = section_head(draw, 80, y, "PAYMENT SUMMARY", width=W - 160)
    y += 14
    hdrs = ["Service", "Rate", "Qty", "Total"]
    wids = [1100, 400, 200, 420]
    y = table_row(draw, 80, y, hdrs, wids, header=True)
    for i in range(4):
        y = table_row(draw, 80, y, [""] * 4, wids, alt=bool(i % 2), row_h=80)
    draw.rectangle([1300, y + 10, 2220, y + 70], fill=GREEN)
    draw.text((1320, y + 18), "TOTAL:", WHITE, font=font(42, bold=True))
    right(draw, 2200, y + 18, "£", GOLD, font(42, bold=True))
    y += 100
    centred(draw, y, "Cancellation: 24-hour notice required.", CHARCOAL, font(34), canvas_w=W)
    centred(draw, y + 50, "Late cancellations may incur a 50% charge.", CHARCOAL, font(34), canvas_w=W)
    centred(draw, y + 120, "Thank you for booking with us! We can't wait to meet your pet.",
            GREEN, font(38, bold=True), canvas_w=W)
    a4_footer(draw, W, H)
    return save_upload(img, f"{PFX}_Booking_Confirmation.png",
                       f"templates/{NICHE}/forms/{PFX}_Booking_Confirmation.png")


# ══════════════════════════════════════════════════════════════════════════════
# OPERATIONS TEMPLATES (4)
# ══════════════════════════════════════════════════════════════════════════════

def build_daily_walk_schedule():
    W, H = PIL_A4
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)
    y = a4_header(img, draw, "DAILY WALK SCHEDULE")
    y += 10
    draw.text((120, y), "Date:", CHARCOAL, font=font(38, bold=True))
    draw.rectangle([230, y + 55, 700, y + 58], fill=GREEN)
    draw.text((800, y), "Walker:", CHARCOAL, font=font(38, bold=True))
    draw.rectangle([960, y + 55, 1600, y + 58], fill=GREEN)
    draw.text((1700, y), "Vehicle:", CHARCOAL, font=font(38, bold=True))
    draw.rectangle([1880, y + 55, 2360, y + 58], fill=GREEN)
    y += 120
    hdrs = ["Time", "Client", "Pet", "Service", "Duration", "Notes", "Done"]
    wids = [200, 380, 280, 340, 200, 540, 100]
    y = table_row(draw, 80, y, hdrs, wids, header=True)
    for i in range(20):
        y = table_row(draw, 80, y, [""] * 7, wids, alt=bool(i % 2), row_h=74)
    y += 10
    draw.text((120, y), "Total walks:", CHARCOAL, font=font(36, bold=True))
    draw.rectangle([320, y + 52, 600, y + 55], fill=GREEN)
    draw.text((700, y), "Total km:", CHARCOAL, font=font(36, bold=True))
    draw.rectangle([870, y + 52, 1200, y + 55], fill=GREEN)
    draw.text((1300, y), "Notes:", CHARCOAL, font=font(36, bold=True))
    draw.rectangle([1440, y + 52, 2360, y + 55], fill=GREEN)
    a4_footer(draw, W, H)
    return save_upload(img, f"{PFX}_Daily_Walk_Schedule.png",
                       f"templates/{NICHE}/operations/{PFX}_Daily_Walk_Schedule.png")


def build_incident_report():
    W, H = PIL_A4
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)
    y = a4_header(img, draw, "INCIDENT REPORT FORM")
    y = section_head(draw, 80, y + 10, "INCIDENT DETAILS", width=W - 160)
    y += 14
    y = field_pair(draw, 120, y, "Date of Incident:", "Time:", total_w=2240)
    y = field_pair(draw, 120, y, "Location:", "Walker Name:", total_w=2240)
    y = field_pair(draw, 120, y, "Pet Name:", "Client Name:", total_w=2240)
    y += 10
    y = section_head(draw, 80, y, "INCIDENT TYPE", width=W - 160)
    y += 14
    cols = 2
    types = ["Dog bite / nip", "Dog fight / altercation", "Escape / off-lead incident",
             "Road traffic incident", "Injury (dog)", "Injury (walker)",
             "Property damage", "Theft / loss", "Vet visit required", "Other"]
    for i, t in enumerate(types):
        xoff = 120 if i % 2 == 0 else 1300
        if i % 2 == 0 and i > 0:
            y += 52
        y_this = y if i % 2 != 0 else y
        checkbox(draw, xoff, y_this, t, font_size=34)
    y += 52
    y += 10
    y = section_head(draw, 80, y, "DESCRIPTION", width=W - 160)
    y += 14
    for _ in range(6):
        draw.rectangle([120, y + 50, 2360, y + 53], fill=GREEN)
        y += 80
    y += 10
    y = section_head(draw, 80, y, "ACTION TAKEN & FOLLOW-UP", width=W - 160)
    y += 14
    for _ in range(4):
        draw.rectangle([120, y + 50, 2360, y + 53], fill=GREEN)
        y += 80
    y += 10
    y = field_pair(draw, 120, y, "Client Notified? Y / N   Time:", "Vet Contacted? Y / N", total_w=2240)
    draw.text((120, y), "Walker Signature:", CHARCOAL, font=font(36, bold=True))
    draw.rectangle([120, y + 58, 1100, y + 61], fill=GREEN)
    draw.text((1200, y), "Date:", CHARCOAL, font=font(36, bold=True))
    draw.rectangle([1320, y + 58, 2300, y + 61], fill=GREEN)
    a4_footer(draw, W, H)
    return save_upload(img, f"{PFX}_Incident_Report.png",
                       f"templates/{NICHE}/operations/{PFX}_Incident_Report.png")


def build_expenses_tracker():
    W, H = PIL_A4
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)
    y = a4_header(img, draw, "BUSINESS EXPENSES TRACKER")
    y += 10
    draw.text((120, y), "Month/Year:", CHARCOAL, font=font(38, bold=True))
    draw.rectangle([380, y + 55, 1100, y + 58], fill=GREEN)
    y += 120
    hdrs = ["Date", "Description", "Category", "Supplier", "Amount", "Receipt"]
    wids = [220, 560, 380, 380, 220, 180]
    y = table_row(draw, 80, y, hdrs, wids, header=True)
    cats = ["Fuel", "Insurance", "Equipment", "Marketing", "Software", "Training",
            "Phone", "Other", "", "", "", "", "", "", "", "", "", "", "", ""]
    for i in range(20):
        cat = cats[i] if i < len(cats) else ""
        y = table_row(draw, 80, y, ["", "", cat, "", "", ""], wids, alt=bool(i % 2), row_h=70)
    draw.rectangle([80, y + 10, 2300, y + 80], fill=CREAM_ALT, outline=GOLD, width=1)
    draw.text((100, y + 22), "TOTAL:", GREEN, font=font(44, bold=True))
    right(draw, 2280, y + 22, "£", CHARCOAL, font(44, bold=True))
    y += 100
    draw.text((120, y), "Notes:", CHARCOAL, font=font(36, bold=True))
    draw.rectangle([120, y + 55, 2300, y + 58], fill=GREEN)
    a4_footer(draw, W, H)
    return save_upload(img, f"{PFX}_Expenses_Tracker.png",
                       f"templates/{NICHE}/operations/{PFX}_Expenses_Tracker.png")


def build_income_tracker():
    W, H = PIL_A4
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)
    y = a4_header(img, draw, "INCOME TRACKER")
    y += 10
    draw.text((120, y), "Month/Year:", CHARCOAL, font=font(38, bold=True))
    draw.rectangle([380, y + 55, 1100, y + 58], fill=GREEN)
    y += 120
    hdrs = ["Date", "Client", "Service", "Sessions", "Rate", "Total", "Paid?"]
    wids = [210, 460, 380, 190, 200, 250, 150]
    y = table_row(draw, 80, y, hdrs, wids, header=True)
    for i in range(20):
        y = table_row(draw, 80, y, [""] * 7, wids, alt=bool(i % 2), row_h=72)
    draw.rectangle([80, y + 10, 2300, y + 80], fill=GREEN)
    draw.text((100, y + 20), "TOTAL INCOME:", WHITE, font=font(44, bold=True))
    right(draw, 2280, y + 20, "£", GOLD, font(44, bold=True))
    y += 100
    draw.rectangle([80, y + 10, 1100, y + 80], fill=CREAM_ALT, outline=GOLD, width=1)
    draw.text((100, y + 22), "Total Expenses (from Expenses Tracker):", CHARCOAL, font=font(34))
    right(draw, 1080, y + 22, "£", CHARCOAL, font(34))
    draw.rectangle([1160, y + 10, 2300, y + 80], fill=CREAM_ALT, outline=GREEN, width=2)
    draw.text((1180, y + 22), "NET PROFIT:", GREEN, font=font(40, bold=True))
    right(draw, 2280, y + 22, "£", CHARCOAL, font(40, bold=True))
    y += 100
    draw.text((120, y), "Notes:", CHARCOAL, font=font(36, bold=True))
    draw.rectangle([120, y + 55, 2300, y + 58], fill=GREEN)
    a4_footer(draw, W, H)
    return save_upload(img, f"{PFX}_Income_Tracker.png",
                       f"templates/{NICHE}/operations/{PFX}_Income_Tracker.png")


# ══════════════════════════════════════════════════════════════════════════════
# DELIVERY PDF
# ══════════════════════════════════════════════════════════════════════════════

GREEN_RL   = colors.HexColor("#2D5F3E")
GOLD_RL    = colors.HexColor("#C9A96E")
CREAM_RL   = colors.HexColor("#F5F0E8")
CHAR_RL    = colors.HexColor("#1A1A1A")
WHITE_RL   = colors.HexColor("#FFFFFF")

SECTIONS = [
    ("BRANDING (9 templates)", [
        ("Business Card — Dark",        f"{CDN}/templates/dog-walking/branding/DW_Business_Card_Dark.png"),
        ("Business Card — Light",       f"{CDN}/templates/dog-walking/branding/DW_Business_Card_Light.png"),
        ("Appointment Card — Dark",     f"{CDN}/templates/dog-walking/branding/DW_Appointment_Card_Dark.png"),
        ("Appointment Card — Light",    f"{CDN}/templates/dog-walking/branding/DW_Appointment_Card_Light.png"),
        ("Loyalty Reward Card",         f"{CDN}/templates/dog-walking/branding/DW_Loyalty_Card.png"),
        ("Gift Certificate",            f"{CDN}/templates/dog-walking/branding/DW_Gift_Certificate.png"),
        ("Welcome Sign (A4)",           f"{CDN}/templates/dog-walking/branding/DW_Welcome_Sign.png"),
        ("Thank You Card",              f"{CDN}/templates/dog-walking/branding/DW_Thank_You_Card.png"),
        ("Referral Card",               f"{CDN}/templates/dog-walking/branding/DW_Referral_Card.png"),
    ]),
    ("MARKETING (8 templates)", [
        ("Flyer — Services Promo",      f"{CDN}/templates/dog-walking/marketing/DW_Flyer_Services.png"),
        ("Flyer — New Client Offer",    f"{CDN}/templates/dog-walking/marketing/DW_Flyer_New_Client.png"),
        ("Price List / Service Menu",   f"{CDN}/templates/dog-walking/marketing/DW_Price_List.png"),
        ("Social — Booking Open",       f"{CDN}/templates/dog-walking/marketing/DW_Social_Booking.png"),
        ("Social — Client Testimonial", f"{CDN}/templates/dog-walking/marketing/DW_Social_Testimonial.png"),
        ("Social — Pet Care Tips",      f"{CDN}/templates/dog-walking/marketing/DW_Social_Tips.png"),
        ("Social — Seasonal Offer",     f"{CDN}/templates/dog-walking/marketing/DW_Social_Seasonal.png"),
        ("Social — Pet of the Week",    f"{CDN}/templates/dog-walking/marketing/DW_Social_Pet_Of_Week.png"),
    ]),
    ("CLIENT FORMS (8 templates)", [
        ("Client Service Agreement",    f"{CDN}/templates/dog-walking/forms/DW_Client_Agreement.png"),
        ("Pet Information Sheet",       f"{CDN}/templates/dog-walking/forms/DW_Pet_Info_Sheet.png"),
        ("Daily Walk Log",              f"{CDN}/templates/dog-walking/forms/DW_Walk_Log.png"),
        ("Feeding Schedule",            f"{CDN}/templates/dog-walking/forms/DW_Feeding_Schedule.png"),
        ("Emergency Contact Card",      f"{CDN}/templates/dog-walking/forms/DW_Emergency_Contact_Card.png"),
        ("Key Handover Form",           f"{CDN}/templates/dog-walking/forms/DW_Key_Handover_Form.png"),
        ("Invoice",                     f"{CDN}/templates/dog-walking/forms/DW_Invoice.png"),
        ("Booking Confirmation",        f"{CDN}/templates/dog-walking/forms/DW_Booking_Confirmation.png"),
    ]),
    ("OPERATIONS (4 templates)", [
        ("Daily Walk Schedule",         f"{CDN}/templates/dog-walking/operations/DW_Daily_Walk_Schedule.png"),
        ("Incident Report Form",        f"{CDN}/templates/dog-walking/operations/DW_Incident_Report.png"),
        ("Expenses Tracker",            f"{CDN}/templates/dog-walking/operations/DW_Expenses_Tracker.png"),
        ("Income Tracker",              f"{CDN}/templates/dog-walking/operations/DW_Income_Tracker.png"),
    ]),
]


def build_delivery_pdf():
    pdf_path = LISTING / "DW_Mega_Bundle_DELIVERY.pdf"
    c = rl_canvas.Canvas(str(pdf_path), pagesize=RL_A4)
    W, H = RL_A4

    # Cover page
    c.setFillColor(GREEN_RL); c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(GOLD_RL)
    c.setFont("Helvetica-Bold", 44)
    c.drawCentredString(W / 2, H - 100, "DOG WALKING & PET SITTING")
    c.drawCentredString(W / 2, H - 155, "MEGA BUSINESS BUNDLE")
    c.setFillColor(WHITE_RL)
    c.setFont("Helvetica", 26)
    c.drawCentredString(W / 2, H - 210, "30 Canva Templates — Fully Editable")
    c.setFillColor(GOLD_RL)
    c.rect(50, H - 250, W - 100, 3, fill=1, stroke=0)
    c.setFillColor(WHITE_RL)
    c.setFont("Helvetica", 20)
    y = H - 300
    for line in [
        "Thank you for your purchase!",
        "",
        "This bundle contains 30 fully editable PNG templates.",
        "Download each template from the links below.",
        "Open in Canva (free account works fine) and edit to match your brand.",
        "",
        "Included categories:",
        "  • Branding (9 templates)",
        "  • Marketing (8 templates)",
        "  • Client Forms (8 templates)",
        "  • Operations (4 templates)",
        "",
        "Tip: Right-click any link below and choose 'Open Link'",
        "or copy the URL into your browser.",
        "",
        "Questions? Message us on Etsy — we reply within 24 hours.",
    ]:
        c.drawString(60, y, line)
        y -= 28
    c.setFillColor(GOLD_RL)
    c.rect(50, 60, W - 100, 3, fill=1, stroke=0)
    c.setFillColor(WHITE_RL)
    c.setFont("Helvetica", 16)
    c.drawCentredString(W / 2, 35, "PurpleOcaz — purpleocaz.etsy.com")
    c.showPage()

    # Section pages
    for section_title, items in SECTIONS:
        c.setFillColor(CREAM_RL); c.rect(0, 0, W, H, fill=1, stroke=0)
        c.setFillColor(GREEN_RL); c.rect(0, H - 80, W, 80, fill=1, stroke=0)
        c.setFillColor(GOLD_RL)
        c.setFont("Helvetica-Bold", 28)
        c.drawCentredString(W / 2, H - 52, section_title)
        y = H - 120
        c.setFillColor(CHAR_RL)
        for name, url in items:
            c.setFont("Helvetica-Bold", 18)
            c.setFillColor(CHAR_RL)
            c.drawString(60, y, f"• {name}")
            c.setFont("Helvetica", 14)
            c.setFillColor(GREEN_RL)
            c.drawString(80, y - 22, url)
            c.linkURL(url, (80, y - 30, min(80 + len(url) * 7, W - 60), y - 10))
            y -= 65
            if y < 80:
                c.setFillColor(GREEN_RL)
                c.rect(0, 0, W, 40, fill=1, stroke=0)
                c.setFillColor(WHITE_RL)
                c.setFont("Helvetica", 12)
                c.drawCentredString(W / 2, 14, "PurpleOcaz — purpleocaz.etsy.com")
                c.showPage()
                c.setFillColor(CREAM_RL); c.rect(0, 0, W, H, fill=1, stroke=0)
                y = H - 60
        c.setFillColor(GREEN_RL)
        c.rect(0, 0, W, 40, fill=1, stroke=0)
        c.setFillColor(WHITE_RL)
        c.setFont("Helvetica", 12)
        c.drawCentredString(W / 2, 14, "PurpleOcaz — purpleocaz.etsy.com")
        c.showPage()

    c.save()
    print(f"  Delivery PDF saved: {pdf_path}")
    upload_to_spaces(pdf_path, "templates/dog-walking/DW_Mega_Bundle_DELIVERY.pdf",
                     content_type="application/pdf")
    return pdf_path


# ══════════════════════════════════════════════════════════════════════════════
# 7 LISTING IMAGES
# ══════════════════════════════════════════════════════════════════════════════

def build_listing_hero():
    img = Image.new("RGB", (W, H), GREEN)
    draw = ImageDraw.Draw(img)
    # Background pattern
    for i in range(0, W, 200):
        paw_print(draw, i, H // 4, size=30, fill=GREEN_DARK)
        paw_print(draw, i + 100, H * 3 // 4, size=20, fill=GREEN_DARK)
    draw.rectangle([0, 0, W, H // 2 + 100], fill=GREEN)
    draw.rectangle([0, H // 2 + 100, W, H], fill=CHARCOAL)
    gold_rule(draw, H // 2 + 100, thickness=16, canvas_w=W)
    # Large paw accents
    paw_print(draw, 200, 300, size=120, fill=GOLD)
    paw_print(draw, W - 200, 300, size=120, fill=GOLD)
    # Main text
    centred(draw, 180, "DOG WALKING", GOLD, font(180, bold=True), canvas_w=W)
    centred(draw, 380, "& PET SITTING", WHITE, font(130, bold=True), canvas_w=W)
    gold_rule(draw, 560, x0=200, x1=W - 200, thickness=8)
    centred(draw, 590, "MEGA BUSINESS BUNDLE", CREAM, font(90, bold=True), canvas_w=W)
    centred(draw, 710, "30 Professional Templates — Fully Editable in Canva", WHITE, font(60), canvas_w=W)
    gold_rule(draw, 810, x0=200, x1=W - 200, thickness=8)
    # Feature badges
    badges = ["Branding Kit", "Marketing Flyers", "Client Forms", "Operations", "Social Media"]
    bw = 500
    total = bw * len(badges) + 40 * (len(badges) - 1)
    bx = (W - total) // 2
    for badge in badges:
        draw.rectangle([bx, 860, bx + bw, 960], fill=GOLD)
        centred(draw, 888, badge, CHARCOAL, font(48, bold=True), canvas_w=bw)
        draw.text((bx, 888), "", fill=CHARCOAL, font=font(48, bold=True))
        # Fix: use absolute positioning
        bb = draw.textbbox((0, 0), badge, font=font(48, bold=True))
        tw = bb[2] - bb[0]
        draw.text((bx + (bw - tw) // 2, 888), badge, fill=CHARCOAL, font=font(48, bold=True))
        bx += bw + 40
    centred(draw, 1020, "Insured  |  DBS Checked  |  Professional", CREAM, font(56), canvas_w=W)
    # Bottom section
    centred(draw, H // 2 + 160, "Everything you need to run a", WHITE, font(70), canvas_w=W)
    centred(draw, H // 2 + 260, "professional dog walking business", WHITE, font(70), canvas_w=W)
    centred(draw, H // 2 + 380, "from day one.", GOLD, font(90, bold=True), canvas_w=W)
    centred(draw, H // 2 + 520, "£39.99  •  Instant Download  •  Canva Free Account Works", CREAM, font(50), canvas_w=W)
    path = LISTING / "DW_listing_01_hero.png"
    img.save(path, "PNG")
    print(f"  Saved {path.name}")
    return path


def build_listing_whats_inside():
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 220], fill=GREEN)
    gold_rule(draw, 220, thickness=10, canvas_w=W)
    centred(draw, 60, "WHAT'S INSIDE YOUR BUNDLE", GOLD, font(100, bold=True), canvas_w=W)
    centred(draw, 165, "30 fully editable professional templates", CREAM, font(50), canvas_w=W)
    categories = [
        ("BRANDING KIT", "9 templates", GREEN, [
            "Business Card (Dark)", "Business Card (Light)",
            "Appointment Card (Dark)", "Appointment Card (Light)",
            "Loyalty Reward Card", "Gift Certificate",
            "Welcome Sign", "Thank You Card", "Referral Card",
        ]),
        ("MARKETING", "8 templates", GREEN, [
            "Services Promo Flyer", "New Client Offer Flyer",
            "Price List / Service Menu", "Social — Booking Open",
            "Social — Testimonial", "Social — Pet Care Tips",
            "Social — Seasonal Offer", "Social — Pet of the Week",
        ]),
        ("CLIENT FORMS", "8 templates", CHARCOAL, [
            "Client Service Agreement", "Pet Information Sheet",
            "Daily Walk Log", "Feeding Schedule",
            "Emergency Contact Card", "Key Handover Form",
            "Invoice", "Booking Confirmation",
        ]),
        ("OPERATIONS", "4 templates", CHARCOAL, [
            "Daily Walk Schedule", "Incident Report Form",
            "Expenses Tracker", "Income Tracker",
        ]),
    ]
    col_w = W // 2 - 40
    positions = [(30, 260), (W // 2 + 10, 260), (30, H // 2 + 30), (W // 2 + 10, H // 2 + 30)]
    for (cx, cy), (cat_title, count, bg, items) in zip(positions, categories):
        draw.rectangle([cx, cy, cx + col_w, cy + H // 2 - 60], fill=bg, outline=GOLD, width=3)
        draw.rectangle([cx, cy, cx + col_w, cy + 100], fill=GOLD)
        bb = draw.textbbox((0, 0), cat_title, font=font(52, bold=True))
        tw = bb[2] - bb[0]
        draw.text((cx + (col_w - tw) // 2, cy + 14), cat_title, fill=CHARCOAL, font=font(52, bold=True))
        bb2 = draw.textbbox((0, 0), count, font=font(38))
        tw2 = bb2[2] - bb2[0]
        draw.text((cx + (col_w - tw2) // 2, cy + 58), count, fill=CHARCOAL, font=font(38))
        iy = cy + 118
        for item in items:
            paw_print(draw, cx + 34, iy + 22, size=14, fill=GOLD)
            draw.text((cx + 60, iy), item, fill=WHITE if bg != CREAM else CHARCOAL, font=font(36))
            iy += 56
    path = LISTING / "DW_listing_02_whats_inside.png"
    img.save(path, "PNG")
    print(f"  Saved {path.name}")
    return path


def build_listing_lifestyle():
    img = Image.new("RGB", (W, H), CHARCOAL)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 240], fill=GREEN)
    gold_rule(draw, 240, thickness=10, canvas_w=W)
    centred(draw, 70, "MADE FOR DOG WALKERS", GOLD, font(110, bold=True), canvas_w=W)
    centred(draw, 190, "by someone who gets it", WHITE, font(58), canvas_w=W)
    features = [
        ("LOOK PROFESSIONAL", "from your very first client", "Branded cards, flyers & welcome signs"),
        ("PROTECT YOUR BUSINESS", "with solid paperwork", "Client agreements, key forms & incident logs"),
        ("STAY ORGANISED", "day in, day out", "Walk schedules, logs & income trackers"),
        ("GROW YOUR CLIENTELE", "with smart marketing", "Social posts, referral cards & seasonal offers"),
    ]
    y = 300
    for title, subtitle, detail in features:
        draw.rectangle([80, y, W - 80, y + 190], fill=GREEN, outline=GOLD, width=3)
        paw_print(draw, 160, y + 95, size=50, fill=GOLD)
        draw.text((260, y + 28), title, fill=GOLD, font=font(68, bold=True))
        draw.text((260, y + 108), subtitle, fill=CREAM, font=font(46))
        draw.text((260, y + 155), detail, fill=WHITE, font=font(36))
        y += 210
    gold_rule(draw, y + 20, x0=80, x1=W - 80, thickness=6)
    centred(draw, y + 50, "Fully editable in Canva — free account works perfectly", CREAM,
            font(54), canvas_w=W)
    centred(draw, y + 130, "No design skills required. Just add your name and go.", WHITE,
            font(50), canvas_w=W)
    draw.rectangle([80, y + 220, W - 80, y + 360], fill=GOLD)
    centred(draw, y + 255, "30 TEMPLATES  •  £39.99  •  INSTANT DOWNLOAD", CHARCOAL,
            font(62, bold=True), canvas_w=W)
    path = LISTING / "DW_listing_03_lifestyle.png"
    img.save(path, "PNG")
    print(f"  Saved {path.name}")
    return path


def build_listing_how_it_works():
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 220], fill=GREEN)
    gold_rule(draw, 220, thickness=10, canvas_w=W)
    centred(draw, 65, "HOW IT WORKS", GOLD, font(110, bold=True), canvas_w=W)
    centred(draw, 165, "Three simple steps to a professional business", WHITE, font(52), canvas_w=W)
    steps = [
        ("1", "PURCHASE & DOWNLOAD",
         "Buy on Etsy and open the delivery PDF.",
         "Every template link is inside, ready to go."),
        ("2", "OPEN IN CANVA",
         "Click any link to open the template in Canva.",
         "A free Canva account is all you need."),
        ("3", "CUSTOMISE & PRINT",
         "Replace the placeholder text with your details.",
         "Download as PDF or PNG and print or share online."),
    ]
    y = 280
    for num, title, line1, line2 in steps:
        # Number circle
        draw.ellipse([100, y, 300, y + 200], fill=GREEN)
        centred(draw, y + 50, num, WHITE, font(120, bold=True), canvas_w=200)
        draw.text((350, y + 22), title, fill=GREEN, font=font(72, bold=True))
        draw.text((350, y + 108), line1, fill=CHARCOAL, font=font(46))
        draw.text((350, y + 164), line2, fill=CHARCOAL, font=font(44))
        gold_rule(draw, y + 220, x0=80, x1=W - 80, thickness=4)
        y += 280
    # Canva basics box
    y += 20
    draw.rectangle([80, y, W - 80, y + 420], fill=GREEN, outline=GOLD, width=4)
    centred(draw, y + 30, "WHAT YOU'LL NEED", GOLD, font(70, bold=True), canvas_w=W)
    centred(draw, y + 120, "✓  A free Canva account (canva.com)", WHITE, font(52), canvas_w=W)
    centred(draw, y + 190, "✓  A printer (or use a local print shop)", WHITE, font(52), canvas_w=W)
    centred(draw, y + 260, "✓  5 minutes to personalise each template", WHITE, font(52), canvas_w=W)
    centred(draw, y + 340, "That's it. No design experience needed!", GOLD, font(54, bold=True), canvas_w=W)
    path = LISTING / "DW_listing_04_how_it_works.png"
    img.save(path, "PNG")
    print(f"  Saved {path.name}")
    return path


def build_listing_why_buy():
    img = Image.new("RGB", (W, H), GREEN)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, H - 200, W, H], fill=CHARCOAL)
    gold_rule(draw, H - 200, thickness=10, canvas_w=W)
    centred(draw, 60, "WHY CHOOSE THIS BUNDLE?", GOLD, font(100, bold=True), canvas_w=W)
    gold_rule(draw, 190, x0=100, x1=W - 100, thickness=6)
    reasons = [
        ("30 templates in one bundle", "Save hours. Get everything you need in a single purchase."),
        ("Built for dog walkers specifically", "Not generic — every form, card and flyer is pet-business focused."),
        ("Canva free account works", "No paid subscriptions. Download, edit, print — done."),
        ("Print-ready at 300 DPI", "Take to any print shop or print at home. Always looks professional."),
        ("Covers every area of your business", "Branding, marketing, client management, and daily operations."),
        ("One-off purchase, use forever", "Buy once. Use for as long as you run your business."),
    ]
    y = 230
    for title, desc in reasons:
        draw.rectangle([80, y, W - 80, y + 200], fill=WHITE, outline=GOLD, width=2)
        paw_print(draw, 160, y + 100, size=50, fill=GREEN)
        draw.text((270, y + 28), title, fill=GREEN, font=font(64, bold=True))
        draw.text((270, y + 112), desc, fill=CHARCOAL, font=font(42))
        y += 220
    centred(draw, H - 160, "Instant download. No waiting. No subscriptions.", CREAM,
            font(54), canvas_w=W)
    centred(draw, H - 90, "30 templates  •  £39.99  •  Yours forever", GOLD,
            font(58, bold=True), canvas_w=W)
    path = LISTING / "DW_listing_05_why_buy.png"
    img.save(path, "PNG")
    print(f"  Saved {path.name}")
    return path


def build_listing_canva_basics():
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 240], fill=GREEN)
    gold_rule(draw, 240, thickness=10, canvas_w=W)
    centred(draw, 65, "NEW TO CANVA?", GOLD, font(110, bold=True), canvas_w=W)
    centred(draw, 165, "Don't worry — it's incredibly easy", WHITE, font(58), canvas_w=W)
    steps = [
        ("Go to canva.com", "Create a free account (takes 60 seconds)"),
        ("Click the template link", "Each template link opens directly in Canva"),
        ("Click any text to edit it", "Just click, type your details, done"),
        ("Change colours if you like", "Click any shape → Colour picker → your brand colour"),
        ("Download when finished", "File → Download → PDF Print or PNG"),
        ("Print or share", "Print at home, local print shop, or share digitally"),
    ]
    y = 280
    for i, (step, desc) in enumerate(steps):
        draw.rectangle([80, y, W - 80, y + 170], fill=WHITE if i % 2 == 0 else CREAM_ALT,
                       outline=GOLD, width=2)
        draw.rectangle([80, y, 220, y + 170], fill=GREEN)
        centred(draw, y + 55, str(i + 1), WHITE, font(90, bold=True), canvas_w=140)
        draw.text((240, y + 22), step, fill=GREEN, font=font(62, bold=True))
        draw.text((240, y + 100), desc, fill=CHARCOAL, font=font(44))
        y += 190
    draw.rectangle([80, y + 20, W - 80, y + 200], fill=GREEN, outline=GOLD, width=4)
    centred(draw, y + 55, "Canva is free and works on any device —", CREAM, font(52), canvas_w=W)
    centred(draw, y + 120, "phone, tablet, or laptop!", GOLD, font(62, bold=True), canvas_w=W)
    path = LISTING / "DW_listing_06_canva_basics.png"
    img.save(path, "PNG")
    print(f"  Saved {path.name}")
    return path


def build_listing_please_note():
    img = Image.new("RGB", (W, H), CHARCOAL)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 240], fill=GREEN)
    gold_rule(draw, 240, thickness=10, canvas_w=W)
    centred(draw, 65, "PLEASE NOTE", GOLD, font(110, bold=True), canvas_w=W)
    centred(draw, 165, "Important information about your purchase", WHITE, font(52), canvas_w=W)
    notes = [
        ("Digital Download Only", "No physical items will be posted. You receive PNG files."),
        ("Instant Delivery", "Your delivery PDF arrives via Etsy immediately after purchase."),
        ("Canva Free Account", "All templates work with a free Canva account — no paid plan needed."),
        ("Personal & Business Use", "Use these templates for your own dog walking business."),
        ("No Reselling", "Please do not resell or redistribute the templates themselves."),
        ("Colour & Font Editable", "All text, colours and logos can be changed in Canva."),
        ("Questions?", "Message us on Etsy — we reply within 24 hours, 7 days a week."),
    ]
    y = 280
    for title, desc in notes:
        draw.rectangle([80, y, W - 80, y + 185], fill=WHITE, outline=GOLD, width=2)
        paw_print(draw, 160, y + 90, size=44, fill=GREEN)
        draw.text((270, y + 28), title, fill=GREEN, font=font(62, bold=True))
        draw.text((270, y + 108), desc, fill=CHARCOAL, font=font(42))
        y += 205
    path = LISTING / "DW_listing_07_please_note.png"
    img.save(path, "PNG")
    print(f"  Saved {path.name}")
    return path


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("DOG WALKING & PET SITTING MEGA BUNDLE — BUILD PIPELINE")
    print("=" * 60)

    # ── Phase 1: Build all 30 templates ──────────────────────────────
    print("\n=== Phase 1: Building 30 Templates ===")

    print("\n  [BRANDING — 9 templates]")
    build_business_card_dark()
    build_business_card_light()
    build_appointment_card_dark()
    build_appointment_card_light()
    build_loyalty_card()
    build_gift_certificate()
    build_welcome_sign()
    build_thank_you_card()
    build_referral_card()

    print("\n  [MARKETING — 8 templates]")
    build_flyer_services()
    build_flyer_new_client()
    build_price_list()
    build_social_booking()
    build_social_testimonial()
    build_social_tips()
    build_social_seasonal()
    build_social_pet_of_week()

    print("\n  [CLIENT FORMS — 8 templates]")
    build_client_agreement()
    build_pet_info_sheet()
    build_walk_log()
    build_feeding_schedule()
    build_emergency_contact_card()
    build_key_handover_form()
    build_invoice()
    build_booking_confirmation()

    print("\n  [OPERATIONS — 4 templates]")
    build_daily_walk_schedule()
    build_incident_report()
    build_expenses_tracker()
    build_income_tracker()

    print("\n  ✓ All 30 templates built and uploaded.")

    # ── Phase 2: Delivery PDF ─────────────────────────────────────────
    print("\n=== Phase 2: Building Delivery PDF ===")
    pdf_path = build_delivery_pdf()

    # ── Phase 3: 7 Listing Images ─────────────────────────────────────
    print("\n=== Phase 3: Building 7 Listing Images ===")
    listing_imgs = [
        build_listing_hero(),
        build_listing_whats_inside(),
        build_listing_lifestyle(),
        build_listing_how_it_works(),
        build_listing_why_buy(),
        build_listing_canva_basics(),
        build_listing_please_note(),
    ]

    # ── Phase 4: Create Etsy Draft ────────────────────────────────────
    print("\n=== Phase 4: Creating Etsy Draft Listing ===")
    title = "Dog Walking Business Bundle | 30 Canva Templates | Pet Sitting Client Forms Invoice"
    description = """Dog Walking & Pet Sitting Business Bundle — 30 Professional Canva Templates

Everything you need to launch and run a professional dog walking or pet sitting business from day one.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT'S INCLUDED (30 templates)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🐾 BRANDING KIT (9 templates)
• Business Card — Dark & Light versions
• Appointment Card — Dark & Light versions
• Loyalty Reward Card (5th walk FREE)
• Gift Certificate
• Welcome Sign (A4)
• Thank You Card
• Referral Card

📣 MARKETING (8 templates)
• Services Promo Flyer (A4)
• New Client Offer Flyer (A4)
• Price List / Service Menu (A4)
• Social Post — Booking Open
• Social Post — Client Testimonial
• Social Post — Pet Care Tips
• Social Post — Seasonal Offer
• Social Post — Pet of the Week

📋 CLIENT FORMS (8 templates)
• Client Service Agreement
• Pet Information Sheet (breed/temperament/vet/allergies/feeding)
• Daily Walk Log
• Feeding Schedule
• Emergency Contact Card
• Key Handover Form
• Invoice
• Booking Confirmation

🗂️ OPERATIONS (4 templates)
• Daily Walk Schedule
• Incident Report Form
• Expenses Tracker
• Income Tracker

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HOW IT WORKS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Purchase and open your delivery PDF
2. Click any template link to open in Canva (free account works)
3. Edit the placeholder text with your business details
4. Download as PDF or PNG and print or share

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHY BUY THIS BUNDLE?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Built specifically for dog walkers and pet sitters
✅ Covers every area of your business in one purchase
✅ Forest green palette — calm, professional, pet-friendly feel
✅ Print-ready at 300 DPI — home printer or print shop
✅ Fully editable — change all text, colours, and logos
✅ Canva free account is all you need
✅ One-off purchase — use for the lifetime of your business

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PLEASE NOTE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• This is a DIGITAL DOWNLOAD — no physical items are posted
• You receive PNG template files accessible via the delivery PDF
• Templates are for your own dog walking/pet sitting business only
• Please do not resell or redistribute the templates
• Questions? Message us on Etsy — we reply within 24 hours

Thank you for your purchase! We hope this bundle helps your business grow."""

    tags = [
        "dog walking bundle",
        "pet sitting forms",
        "dog walker templates",
        "pet sitter business",
        "dog walk log sheet",
        "pet business canva",
        "dog walker invoice",
        "pet sitting bundle",
        "dog walker branding",
        "client agreement",
        "pet care forms",
        "dog business forms",
        "key handover form",
    ]
    # Validate tags
    for tag in tags:
        assert len(tag) <= 20, f"Tag too long: '{tag}' ({len(tag)} chars)"
    assert len(tags) == 13
    assert len(tags) == len(set(tags)), "Duplicate tags found"

    body = urllib.parse.urlencode({
        "title": title,
        "description": description,
        "price": "39.99",
        "quantity": "999",
        "who_made": "i_did",
        "when_made": "2020_2025",
        "taxonomy_id": "1874",
        "type": "download",
        "is_supply": "false",
        "tags": ",".join(tags),
        "state": "draft",
    })
    result = etsy_request("POST", f"/shops/{SHOP_ID}/listings", body)
    listing_id = result["listing_id"]
    print(f"  ✓ Draft created: #{listing_id}")

    # ── Phase 5: Upload 7 Images ──────────────────────────────────────
    print("\n=== Phase 5: Uploading 7 Listing Images ===")
    for rank, img_path in enumerate(listing_imgs, 1):
        res = upload_image_to_etsy(listing_id, img_path, rank)
        print(f"  rank {rank} — Image ID: {res['listing_image_id']}")

    # Verify images
    imgs = etsy_request("GET", f"/listings/{listing_id}/images")
    print(f"\n  GET images → count: {imgs['count']}")
    for im in imgs["results"]:
        print(f"    rank {im['rank']} | ID {im['listing_image_id']}")

    # ── Phase 6: Attach PDF ───────────────────────────────────────────
    print("\n=== Phase 6: Attaching Delivery PDF ===")
    file_result = upload_file_to_etsy(listing_id, pdf_path)
    print(f"  File attached: {file_result.get('filename')} | ID {file_result.get('listing_file_id')}")

    files = etsy_request("GET", f"/shops/{SHOP_ID}/listings/{listing_id}/files")
    print(f"\n  GET files → count: {files['count']}")
    for fi in files.get("results", []):
        print(f"    {fi['filename']} | {fi['filesize']} | file_id: {fi.get('listing_file_id')}")

    print(f"\n{'=' * 60}")
    print(f"BUNDLE 1 COMPLETE — Draft #{listing_id}")
    print(f"URL: https://www.etsy.com/listing/{listing_id}")
    print(f"{'=' * 60}")
    return listing_id


if __name__ == "__main__":
    listing_id = main()
