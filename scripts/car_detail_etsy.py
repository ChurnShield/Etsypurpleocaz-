#!/usr/bin/env python3
"""Create 4 Etsy listings for Car Detailing niche.

Listing 1: Forms Bundle (8 forms) - £4.99
Listing 2: Visual Bundle (gift cert + price list + loyalty card) - £4.99
Listing 3: Flyer Pack (4 flyers) - £4.99
Listing 4: Starter Bundle (all 15) - £9.99
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
import urllib.parse

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT)

# ── Config ────────────────────────────────────────────────────────────────────
from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT, ".env"))

TOKEN_FILE = os.path.join(PROJECT, "workflows", "etsy_analytics", "etsy_tokens.json")
ETSY_BASE = "https://openapi.etsy.com/v3/application"

API_KEYSTRING = os.getenv("ETSY_API_KEYSTRING", "")
SHARED_SECRET = os.getenv("ETSY_SHARED_SECRET", "")
SHOP_ID = os.getenv("ETSY_SHOP_ID", "")
X_API_KEY = f"{API_KEYSTRING}:{SHARED_SECRET}"


def load_tokens():
    with open(TOKEN_FILE) as f:
        return json.load(f)


def refresh_token(tokens):
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "client_id": API_KEYSTRING,
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
    print(f"  Token refreshed, expires in {new_tokens.get('expires_in', '?')}s")
    return new_tokens


def etsy_request(method, endpoint, tokens, body=None, content_type="application/x-www-form-urlencoded"):
    url = f"{ETSY_BASE}{endpoint}"
    if body and content_type == "application/x-www-form-urlencoded":
        data = urllib.parse.urlencode(body).encode()
    elif body:
        data = body
    else:
        data = None

    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("x-api-key", X_API_KEY)
    req.add_header("Authorization", f"Bearer {tokens['access_token']}")
    if content_type and method != "GET":
        req.add_header("Content-Type", content_type)

    try:
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        if e.code == 401:
            print("  401 — refreshing token...")
            tokens.update(refresh_token(tokens))
            req.remove_header("Authorization")
            req.add_header("Authorization", f"Bearer {tokens['access_token']}")
            resp = urllib.request.urlopen(req)
            return json.loads(resp.read())
        print(f"  HTTP {e.code}: {error_body}")
        raise


def create_listing(tokens, title, description, tags, price):
    body = {
        "title": title,
        "description": description,
        "tags": ",".join(tags),
        "price": str(price),
        "quantity": "999",
        "who_made": "i_did",
        "when_made": "2020_2025",
        "taxonomy_id": "1874",
        "type": "download",
        "is_supply": "false",
        "is_digital": "true",
    }
    result = etsy_request("POST", f"/shops/{SHOP_ID}/listings", tokens, body)
    listing_id = result.get("listing_id")
    print(f"  Created listing {listing_id}: {title[:60]}...")
    return result


def upload_image(tokens, listing_id, image_path, rank=1):
    """Upload image via multipart form."""
    import mimetypes
    boundary = "----PurpleOcazBoundary"
    filename = os.path.basename(image_path)
    mime = mimetypes.guess_type(image_path)[0] or "image/png"

    with open(image_path, "rb") as f:
        file_data = f.read()

    body = bytearray()
    # rank field
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(f'Content-Disposition: form-data; name="rank"\r\n\r\n{rank}\r\n'.encode())
    # image field
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'.encode())
    body.extend(f"Content-Type: {mime}\r\n\r\n".encode())
    body.extend(file_data)
    body.extend(b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode())

    url = f"{ETSY_BASE}/shops/{SHOP_ID}/listings/{listing_id}/images"
    req = urllib.request.Request(url, data=bytes(body), method="POST")
    req.add_header("x-api-key", X_API_KEY)
    req.add_header("Authorization", f"Bearer {tokens['access_token']}")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")

    try:
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read())
        print(f"  Image rank {rank}: {filename}")
        return result
    except urllib.error.HTTPError as e:
        print(f"  Image upload error {e.code}: {e.read().decode()[:200]}")
        raise


def upload_file(tokens, listing_id, file_path, filename=None):
    """Upload digital file."""
    boundary = "----PurpleOcazFileBoundary"
    if not filename:
        filename = os.path.basename(file_path)

    with open(file_path, "rb") as f:
        file_data = f.read()

    body = bytearray()
    # name field
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(f'Content-Disposition: form-data; name="name"\r\n\r\n{filename}\r\n'.encode())
    # file field
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode())
    body.extend(b"Content-Type: application/pdf\r\n\r\n")
    body.extend(file_data)
    body.extend(b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode())

    url = f"{ETSY_BASE}/shops/{SHOP_ID}/listings/{listing_id}/files"
    req = urllib.request.Request(url, data=bytes(body), method="POST")
    req.add_header("x-api-key", X_API_KEY)
    req.add_header("Authorization", f"Bearer {tokens['access_token']}")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")

    try:
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read())
        print(f"  File uploaded: {filename}")
        return result
    except urllib.error.HTTPError as e:
        print(f"  File upload error {e.code}: {e.read().decode()[:200]}")
        raise


def verify_listing(tokens, listing_id):
    result = etsy_request("GET", f"/listings/{listing_id}", tokens)
    images = etsy_request("GET", f"/listings/{listing_id}/images", tokens)
    img_count = len(images.get("results", []))
    state = result.get("state", "unknown")
    price_raw = result.get("price", {})
    price = float(price_raw.get("amount", 0)) / int(price_raw.get("divisor", 100))
    tags = result.get("tags", [])
    print(f"  Verified: state={state}, images={img_count}, price=£{price:.2f}, tags={len(tags)}")
    # Check tags
    for t in tags:
        if len(t) > 20:
            print(f"  WARNING: Tag too long ({len(t)}): {t}")
    return result


# ── Delivery PDF Generator ────────────────────────────────────────────────────
def generate_delivery_pdf(output_path, title, links_dict):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib.colors import HexColor
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.enums import TA_CENTER

    RED = HexColor("#E02020")
    DARK = HexColor("#0D0D0D")

    doc = SimpleDocTemplate(output_path, pagesize=A4,
                           leftMargin=25*mm, rightMargin=25*mm,
                           topMargin=25*mm, bottomMargin=25*mm)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("DTitle", parent=styles["Title"],
                              fontName="Times-Italic", fontSize=22,
                              textColor=DARK, spaceAfter=6))
    styles.add(ParagraphStyle("DH", parent=styles["Heading2"],
                              fontName="Helvetica-Bold", fontSize=12,
                              textColor=RED, spaceBefore=14, spaceAfter=4))
    styles.add(ParagraphStyle("DB", parent=styles["Normal"],
                              fontName="Helvetica", fontSize=10,
                              textColor=DARK, spaceAfter=6, leading=14))

    story = [
        Paragraph(title, styles["DTitle"]),
        Paragraph("Delivery Instructions", styles["DTitle"]),
        Spacer(1, 10),
        Paragraph("Thank You for Your Purchase!", styles["DH"]),
        Paragraph(
            "You now have access to professional car detailing templates. "
            "Every template is fully editable in Canva (free account).",
            styles["DB"]),
        Paragraph("How to Edit Your Templates", styles["DH"]),
        Paragraph("1. Click any Canva link below to open the template.", styles["DB"]),
        Paragraph("2. Click 'Use this template' to create your own copy.", styles["DB"]),
        Paragraph("3. Edit text, colours, photos and fonts to match your brand.", styles["DB"]),
        Paragraph("4. Download as PDF or PNG for print or digital use.", styles["DB"]),
        Paragraph("Your Canva Template Links", styles["DH"]),
    ]
    for name, link in links_dict.items():
        story.append(Paragraph(
            f'<b>{name}:</b> <a href="{link}" color="#E02020">{link}</a>',
            styles["DB"]))
    story.extend([
        Paragraph("Need Help?", styles["DH"]),
        Paragraph("Message us through Etsy. We respond within 24 hours.", styles["DB"]),
        Spacer(1, 20),
        Paragraph(
            "PurpleOcaz — Personal/commercial use permitted. Resale of templates not permitted.",
            ParagraphStyle("Foot", parent=styles["Normal"],
                          fontName="Helvetica", fontSize=7,
                          textColor=HexColor("#999999"), alignment=TA_CENTER)),
    ])
    doc.build(story)
    print(f"  Delivery PDF: {output_path}")
    return output_path


# ── Listings ──────────────────────────────────────────────────────────────────
OUTPUTS = os.path.join(PROJECT, "outputs")

# Load design registry for shortlinks
with open(os.path.join(PROJECT, "config", "design_registry.json")) as f:
    registry = json.load(f)
cd = registry["designs"]["car_detail"]


def listing_1_forms(tokens):
    """Forms Bundle — 8 forms — £4.99"""
    print("\n=== LISTING 1: Forms Bundle ===")

    title = "Car Detailing Client Forms Bundle | 8 Editable Canva Templates | Digital Download"
    tags = [
        "car detail forms",
        "auto detailing form",
        "car detailer forms",
        "detailing consent",
        "vehicle intake form",
        "car detail bundle",
        "auto detail canva",
        "detailing invoice",
        "car wash forms",
        "detailing waiver",
        "canva car detail",
        "auto business form",
        "detailing templates",
    ]
    desc = """8 PROFESSIONAL CAR DETAILING FORMS — FULLY EDITABLE IN CANVA

Everything you need to run a professional car detailing business. Edit every template in Canva (free account) with your business name, logo and branding.

------------------------------

WHAT'S INCLUDED

1. Vehicle Intake Form — customer details, vehicle info, service requested, pre-existing damage notes
2. Consent & Liability Waiver — pre-existing damage disclaimer, liability limits, signature block
3. Service Agreement — services included, exclusions, payment terms, cancellation policy
4. Invoice Template — itemised services, subtotal, VAT, total, payment method
5. Customer Feedback Form — star rating, improvement areas, recommendation question
6. Appointment Booking Form — customer contact, vehicle details, preferred date/time
7. Aftercare Instructions — 24hr no-wash rule, wax care tips, interior maintenance
8. Detailing Package Menu — Bronze, Silver, Gold tiers with price placeholders

------------------------------

HOW TO USE

1. Purchase and download instantly
2. Click the Canva link in your delivery PDF
3. Click 'Use this template' to create your own copy
4. Edit with your business name, logo and details
5. Download as PDF — ready to print or share digitally

------------------------------

PLEASE NOTE

- This is a DIGITAL DOWNLOAD — no physical items shipped
- You need a free Canva account to edit
- Colours may vary slightly between screens and print
- Templates are for personal and commercial use
- Resale of the templates is not permitted

Questions? Message us — we respond within 24 hours.

PurpleOcaz — Designed for car detailing professionals"""

    listing = create_listing(tokens, title, desc, tags, 4.99)
    lid = listing["listing_id"]

    # Generate delivery PDF
    form_links = {}
    for key, data in cd["forms"].items():
        form_links[data["design_title"].replace("Car Detail - ", "")] = data["delivery_shortlink"]
    delivery_path = os.path.join(OUTPUTS, "car-detail-forms", "Delivery_Forms_Bundle.pdf")
    generate_delivery_pdf(delivery_path, "Car Detailing Forms Bundle", form_links)

    # Upload hero image
    hero = os.path.join(OUTPUTS, "car-detail-forms", "hero_forms_bundle.png")
    upload_image(tokens, lid, hero, rank=1)
    time.sleep(1)

    # Upload delivery PDF
    upload_file(tokens, lid, delivery_path, "Car-Detailing-Forms-Bundle-DELIVERY.pdf")

    verify_listing(tokens, lid)
    return lid


def listing_2_visual(tokens):
    """Visual Bundle — gift cert + price list + loyalty card — £4.99"""
    print("\n=== LISTING 2: Visual Bundle ===")

    title = "Car Detailing Gift Certificate Price List Loyalty Card | Editable Canva Templates | Digital Download"
    tags = [
        "car detail gift cert",
        "car detailing bundle",
        "auto detail canva",
        "car detail pricelist",
        "detailing loyalty",
        "car wash gift card",
        "auto detailer bundle",
        "car detail template",
        "detailing price list",
        "canva auto detail",
        "car gift certificate",
        "detailing business",
        "car wash template",
    ]
    desc = """3 PREMIUM CAR DETAILING TEMPLATES — FULLY EDITABLE IN CANVA

Three essential visual templates for your car detailing business. Edit everything in Canva in minutes.

------------------------------

WHAT'S INCLUDED

1. Gift Certificate (A4 Landscape) — professional design with photo strip, TO/FROM/AMOUNT fields, 12-month validity
2. Price List (A4 Portrait) — three boxed sections for Exterior, Interior and Full Packages with price placeholders
3. Loyalty Card (Credit Card Size) — book 5 details get next free, 10 stamp circles, professional dark design

------------------------------

HOW TO USE

1. Purchase and download instantly
2. Click the Canva link in your delivery PDF
3. Click 'Use this template' to create your own copy
4. Edit with your business details, photos and prices
5. Download and print or share digitally

------------------------------

PLEASE NOTE

- DIGITAL DOWNLOAD — no physical items shipped
- Free Canva account needed to edit
- Personal and commercial use permitted
- Resale of templates not permitted

Questions? Message us — we respond within 24 hours.

PurpleOcaz — Designed for car detailing professionals"""

    listing = create_listing(tokens, title, desc, tags, 4.99)
    lid = listing["listing_id"]

    visual_links = {
        "Gift Certificate": cd["gift_certificate"]["delivery_shortlink"],
        "Price List": cd["price_list"]["delivery_shortlink"],
        "Loyalty Card": cd["loyalty_card"]["delivery_shortlink"],
    }
    delivery_path = os.path.join(OUTPUTS, "car-detail-forms", "Delivery_Visual_Bundle.pdf")
    generate_delivery_pdf(delivery_path, "Car Detailing Visual Bundle", visual_links)

    hero = os.path.join(OUTPUTS, "car-detail-forms", "hero_visual_bundle.png")
    upload_image(tokens, lid, hero, rank=1)
    time.sleep(1)
    upload_file(tokens, lid, delivery_path, "Car-Detailing-Visual-Bundle-DELIVERY.pdf")

    verify_listing(tokens, lid)
    return lid


def listing_3_flyers(tokens):
    """Flyer Pack — 4 flyers — £4.99"""
    print("\n=== LISTING 3: Flyer Pack ===")

    title = "Car Detailing Flyer Bundle | 4 Editable Canva Templates | Promo Mobile Seasonal Booking | Digital Download"
    tags = [
        "car detail flyer",
        "auto detailing flyer",
        "car wash flyer canva",
        "detailing promo",
        "mobile detailing",
        "car detail marketing",
        "auto business flyer",
        "canva car wash",
        "detailing advert",
        "car wash marketing",
        "car detail bundle",
        "mobile valet flyer",
        "auto detailer flyer",
    ]
    desc = """4 READY-TO-EDIT FLYER TEMPLATES FOR CAR DETAILERS — FULLY EDITABLE IN CANVA

Four professional marketing flyers to promote your car detailing business. Edit in Canva, print or post online.

------------------------------

WHAT'S INCLUDED

1. Promotional Discount Flyer — dark design with photo, promo percentage box, bold typography
2. Seasonal Special Flyer — full photo with dark overlay, seasonal offer placeholder
3. Mobile Detailing Flyer — split layout with dark panel and photo, service list, book now CTA
4. Walk-In/Booking Flyer — full bleed photo with overlay, services list, contact details

------------------------------

HOW TO USE

1. Purchase and download instantly
2. Click the Canva link in your delivery PDF
3. Click 'Use this template' to create your own copy
4. Edit text, photos and colours for your brand
5. Download as PDF or PNG — print or share online

------------------------------

PLEASE NOTE

- DIGITAL DOWNLOAD — no physical items shipped
- Free Canva account needed to edit
- Personal and commercial use permitted
- Resale of templates not permitted

Questions? Message us — we respond within 24 hours.

PurpleOcaz — Designed for car detailing professionals"""

    listing = create_listing(tokens, title, desc, tags, 4.99)
    lid = listing["listing_id"]

    flyer_links = {
        "Promotional Flyer": cd["flyer_promo"]["delivery_shortlink"],
        "Seasonal Flyer": cd["flyer_seasonal"]["delivery_shortlink"],
        "Mobile Detailing Flyer": cd["flyer_mobile"]["delivery_shortlink"],
        "Walk-In Flyer": cd["flyer_walkin"]["delivery_shortlink"],
    }
    delivery_path = os.path.join(OUTPUTS, "car-detail-forms", "Delivery_Flyer_Pack.pdf")
    generate_delivery_pdf(delivery_path, "Car Detailing Flyer Pack", flyer_links)

    hero = os.path.join(OUTPUTS, "car-detail-forms", "hero_flyer_pack.png")
    upload_image(tokens, lid, hero, rank=1)
    time.sleep(1)
    upload_file(tokens, lid, delivery_path, "Car-Detailing-Flyer-Pack-DELIVERY.pdf")

    verify_listing(tokens, lid)
    return lid


def listing_4_starter(tokens):
    """Starter Bundle — all 15 — £9.99"""
    print("\n=== LISTING 4: Starter Bundle ===")

    title = "Car Detailing Business Bundle | 15 Editable Canva Templates | Forms Flyers Price List | Digital Download"
    tags = [
        "car detail bundle",
        "auto detail bundle",
        "car wash biz kit",
        "detailing business",
        "car detail canva",
        "auto detail canva",
        "detailing forms",
        "car wash kit canva",
        "mobile detailing kit",
        "car detailer bundle",
        "auto business bundle",
        "detailing marketing",
        "car wash canva pack",
    ]
    desc = """COMPLETE CAR DETAILING BUSINESS BUNDLE — 15 EDITABLE CANVA TEMPLATES

Everything you need to run a professional detailing business. 8 client forms, gift certificate, price list, loyalty card and 4 marketing flyers. Edit in Canva, print or share digitally.

------------------------------

WHAT'S INCLUDED

8 CLIENT FORMS
- Vehicle Intake Form
- Consent & Liability Waiver
- Service Agreement
- Invoice Template
- Customer Feedback Form
- Appointment Booking Form
- Aftercare Instructions
- Detailing Package Menu

3 VISUAL DOCUMENTS
- Gift Certificate (A4 Landscape)
- Price List (A4 Portrait)
- Loyalty Card (Credit Card Size)

4 MARKETING FLYERS
- Promotional Discount Flyer
- Seasonal Special Flyer
- Mobile Detailing Flyer
- Walk-In/Booking Flyer

------------------------------

HOW TO USE

1. Purchase and download instantly
2. Click any Canva link in your delivery PDF
3. Click 'Use this template' to create your own copy
4. Edit everything — text, photos, colours, fonts
5. Download as PDF or PNG — print or share digitally

------------------------------

WHY THIS BUNDLE

- Save over 40% compared to buying separately
- Consistent professional branding across all templates
- Edit everything in free Canva
- Print-ready A4 designs
- Credit card size loyalty card
- 4 marketing flyers for different promotions

------------------------------

PLEASE NOTE

- DIGITAL DOWNLOAD — no physical items shipped
- Free Canva account needed to edit
- Personal and commercial use permitted
- Resale of templates not permitted

Questions? Message us — we respond within 24 hours.

PurpleOcaz — Designed for car detailing professionals"""

    listing = create_listing(tokens, title, desc, tags, 9.99)
    lid = listing["listing_id"]

    # All 15 links
    all_links = {}
    for key, data in cd["forms"].items():
        all_links[data["design_title"].replace("Car Detail - ", "")] = data["delivery_shortlink"]
    all_links["Gift Certificate"] = cd["gift_certificate"]["delivery_shortlink"]
    all_links["Price List"] = cd["price_list"]["delivery_shortlink"]
    all_links["Loyalty Card"] = cd["loyalty_card"]["delivery_shortlink"]
    all_links["Promo Flyer"] = cd["flyer_promo"]["delivery_shortlink"]
    all_links["Seasonal Flyer"] = cd["flyer_seasonal"]["delivery_shortlink"]
    all_links["Mobile Detailing Flyer"] = cd["flyer_mobile"]["delivery_shortlink"]
    all_links["Walk-In Flyer"] = cd["flyer_walkin"]["delivery_shortlink"]

    delivery_path = os.path.join(OUTPUTS, "car-detail-forms", "Delivery_Starter_Bundle.pdf")
    generate_delivery_pdf(delivery_path, "Car Detailing Complete Bundle", all_links)

    hero = os.path.join(OUTPUTS, "car-detail-forms", "hero_starter_bundle.png")
    upload_image(tokens, lid, hero, rank=1)
    time.sleep(1)
    upload_file(tokens, lid, delivery_path, "Car-Detailing-Complete-Bundle-DELIVERY.pdf")

    verify_listing(tokens, lid)
    return lid


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    os.chdir(PROJECT)

    tokens = load_tokens()
    # Refresh token proactively
    tokens = refresh_token(tokens)

    results = {}
    results["forms_bundle"] = listing_1_forms(tokens)
    results["visual_bundle"] = listing_2_visual(tokens)
    results["flyer_pack"] = listing_3_flyers(tokens)
    results["starter_bundle"] = listing_4_starter(tokens)

    print("\n=== ALL LISTINGS CREATED ===")
    for name, lid in results.items():
        print(f"  {name}: {lid}")

    # Save listing IDs
    ids_path = os.path.join(OUTPUTS, "car-detail-forms", "etsy_listing_ids.json")
    with open(ids_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nListing IDs saved: {ids_path}")
