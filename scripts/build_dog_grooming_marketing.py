#!/usr/bin/env python3
"""
Dog Grooming — Marketing Templates (8 templates)
1. Flyer: Services Promo (A4)
2. Flyer: New Client Offer (A4)
3. Price List / Service Menu (A4)
4. Social: Booking Reminder (1080×1080)
5. Social: Before & After (1080×1080)
6. Social: Grooming Tips (1080×1080)
7. Social: Testimonial (1080×1080)
8. Social: Seasonal Promo (1080×1080)
"""
import sys
from pathlib import Path

PROJECT = Path("/root/NEW-AI-PROJECT")
sys.path.insert(0, str(PROJECT / "scripts"))
from dog_grooming_design_system import (
    TEAL, GOLD, CREAM, CHARCOAL, WHITE, CREAM_ALT, TEAL_DARK,
    A4, SOCIAL,
    font, centred, right, gold_rule, teal_bar, paw_print,
    a4_header, a4_footer, section_head, upload_to_spaces,
)
from PIL import Image, ImageDraw

OUTPUT = PROJECT / "outputs" / "dog-grooming" / "marketing"
OUTPUT.mkdir(parents=True, exist_ok=True)


# ── Flyers ─────────────────────────────────────────────────────────────────────

def _flyer_promo():
    """Services Promo Flyer (A4)."""
    W, H = A4
    img = Image.new("RGB", A4, CREAM)
    draw = ImageDraw.Draw(img)

    # Header
    draw.rectangle([0, 0, W, 620], fill=TEAL)
    paw_print(draw, 200, 220, size=90, fill=GOLD)
    paw_print(draw, W - 200, 220, size=90, fill=GOLD)
    centred(draw, 60, "YOUR SALON NAME", GOLD, font(90, bold=True), canvas_w=W)
    centred(draw, 200, "Professional Dog Grooming", WHITE, font(58), canvas_w=W)
    centred(draw, 300, "✂  Pamper Your Pup Today  ✂", WHITE, font(54), canvas_w=W)
    centred(draw, 420, "WHERE EVERY DOG DESERVES TO SHINE", GOLD, font(48, bold=True), canvas_w=W)
    gold_rule(draw, 620, thickness=10, canvas_w=W)

    # Services grid
    centred(draw, 660, "OUR SERVICES", TEAL, font(72, bold=True), canvas_w=W)
    gold_rule(draw, 758, x0=200, x1=W - 200, thickness=6, canvas_w=W)

    services = [
        ("Full Groom",         "Bath, dry, cut & style, nail trim, ear clean"),
        ("Bath & Dry",         "Full bath, blow dry, brush out, spritz"),
        ("Puppy Package",      "First groom introduction — gentle & calm"),
        ("Nail Trim",          "Safe, stress-free nail clip & file"),
        ("De-shedding",        "Reduce shedding by up to 90%"),
        ("Luxury Spa",         "Blueberry facial, paw balm & bandana"),
        ("Senior Dog Package", "Extra care & patience for older dogs"),
        ("Same-Day Groom",     "Subject to availability — call to book"),
    ]
    y = 790
    for i, (name, desc) in enumerate(services):
        bg = CREAM_ALT if i % 2 else CREAM
        draw.rectangle([120, y, W - 120, y + 108], fill=bg)
        gold_rule(draw, y + 106, x0=120, x1=W - 120, thickness=2, canvas_w=W)
        paw_print(draw, 170, y + 54, size=22, fill=GOLD)
        draw.text((220, y + 18), name, fill=TEAL, font=font(44, bold=True))
        draw.text((220, y + 66), desc, fill=CHARCOAL, font=font(34))
        y += 108

    # CTA
    draw.rectangle([120, y + 40, W - 120, y + 220], fill=TEAL)
    centred(draw, y + 68, "BOOK YOUR APPOINTMENT TODAY", WHITE, font(60, bold=True), canvas_w=W)
    centred(draw, y + 148, "📞  07700 000000   |   🌐  www.yoursalon.com", GOLD, font(44), canvas_w=W)
    a4_footer(draw, W, H)
    return img


def _flyer_new_client():
    """New Client Offer Flyer (A4)."""
    W, H = A4
    img = Image.new("RGB", A4, CHARCOAL)
    draw = ImageDraw.Draw(img)

    # Teal accent border
    draw.rectangle([0, 0, W, 16], fill=TEAL)
    draw.rectangle([0, H - 16, W, H], fill=TEAL)
    draw.rectangle([0, 0, 16, H], fill=TEAL)
    draw.rectangle([W - 16, 0, W, H], fill=TEAL)

    # Top section
    centred(draw, 80, "NEW CLIENTS", GOLD, font(140, bold=True), canvas_w=W)
    centred(draw, 258, "WELCOME OFFER", WHITE, font(90, bold=True), canvas_w=W)
    gold_rule(draw, 390, x0=200, x1=W - 200, thickness=8, canvas_w=W)

    # Offer circle — simulated with rectangle
    draw.rectangle([W // 2 - 480, 430, W // 2 + 480, 930], fill=TEAL)
    gold_rule(draw, 430, x0=W // 2 - 480, x1=W // 2 + 480, thickness=6, canvas_w=W)
    gold_rule(draw, 930, x0=W // 2 - 480, x1=W // 2 + 480, thickness=6, canvas_w=W)

    centred(draw, 460, "20% OFF", GOLD, font(200, bold=True), canvas_w=W)
    centred(draw, 690, "YOUR FIRST FULL GROOM", WHITE, font(60, bold=True), canvas_w=W)
    centred(draw, 780, "Bath • Cut • Dry • Nails • Ears", CREAM, font(46), canvas_w=W)
    centred(draw, 855, "at YOUR SALON NAME", GOLD, font(42, bold=True), canvas_w=W)

    gold_rule(draw, 968, x0=160, x1=W - 160, thickness=6, canvas_w=W)

    # Paw prints
    for px, py in [(180, 1050), (W - 180, 1050)]:
        paw_print(draw, px, py, size=70, fill=GOLD)

    centred(draw, 1000, "What's included:", GOLD, font(58, bold=True), canvas_w=W)
    items = [
        "✓  Full bath with premium shampoo & conditioner",
        "✓  Blow dry & professional brush out",
        "✓  Full body cut & styling to breed standard",
        "✓  Nail trim & file",
        "✓  Ear clean",
        "✓  Complimentary bandana or bow",
    ]
    y = 1110
    for item in items:
        centred(draw, y, item, CREAM, font(42), canvas_w=W)
        y += 72

    gold_rule(draw, y + 30, x0=160, x1=W - 160, thickness=6, canvas_w=W)
    centred(draw, y + 68, "T&Cs: New clients only. One per household.", CREAM, font(34), canvas_w=W)
    centred(draw, y + 118, "Valid for 3 months. Mention when booking.", CREAM, font(34), canvas_w=W)

    # Contact CTA
    draw.rectangle([160, y + 200, W - 160, y + 400], fill=TEAL)
    centred(draw, y + 240, "CALL OR BOOK ONLINE NOW", WHITE, font(60, bold=True), canvas_w=W)
    centred(draw, y + 316, "📞  07700 000000   |   🌐  www.yoursalon.com", GOLD, font(46), canvas_w=W)

    a4_footer(draw, W, H)
    return img


def _price_list():
    """Service Price List / Menu (A4)."""
    W, H = A4
    img = Image.new("RGB", A4, CREAM)
    draw = ImageDraw.Draw(img)

    y = a4_header(img, draw, "SERVICE PRICE LIST")

    # Intro line
    centred(draw, y, "All prices include bath, dry & finishing touches", CHARCOAL,
            font(38), canvas_w=W)
    y += 70

    categories = [
        ("FULL GROOM PACKAGES", [
            ("Small breeds (e.g. Bichon, Shih Tzu)",  "£45 – £55"),
            ("Medium breeds (e.g. Cocker Spaniel)",   "£55 – £65"),
            ("Large breeds (e.g. Golden Retriever)",  "£65 – £80"),
            ("Giant breeds (e.g. St Bernard)",         "£80 – £100+"),
        ]),
        ("BATH & DRY", [
            ("Small breeds",   "£30 – £40"),
            ("Medium breeds",  "£40 – £50"),
            ("Large breeds",   "£50 – £65"),
        ]),
        ("ADD-ONS & EXTRAS", [
            ("Nail trim only",            "£12"),
            ("Teeth brushing",            "£8"),
            ("Paw balm & massage",        "£10"),
            ("Blueberry facial",          "£12"),
            ("De-shedding treatment",     "£15 – £25"),
            ("Flea & tick treatment",     "£10"),
            ("Anal gland expression",     "£12"),
        ]),
        ("PUPPY PACKAGES", [
            ("Puppy intro groom (1st visit)",  "£30"),
            ("Puppy package (under 6 months)", "£35 – £45"),
        ]),
    ]

    for cat_name, items in categories:
        if y > H - 800:
            break
        y = section_head(draw, 120, y, cat_name, width=W - 240, canvas_w=W)
        for i, (service, price) in enumerate(items):
            bg = CREAM_ALT if i % 2 else CREAM
            draw.rectangle([120, y, W - 120, y + 80], fill=bg)
            gold_rule(draw, y + 78, x0=120, x1=W - 120, thickness=1)
            paw_print(draw, 160, y + 40, size=18, fill=GOLD)
            draw.text((200, y + 18), service, fill=CHARCOAL, font=font(36))
            right(draw, W - 140, y + 22, price, fill=TEAL, f=font(36, bold=True))
            y += 80
        y += 24

    # Note
    gold_rule(draw, y, x0=120, x1=W - 120, thickness=5, canvas_w=W)
    draw.text((120, y + 20), "* Prices may vary depending on coat condition and temperament.",
              fill=CHARCOAL, font=font(34))
    draw.text((120, y + 65), "* A de-matting surcharge may apply. We'll always discuss this with you first.",
              fill=CHARCOAL, font=font(34))

    a4_footer(draw, W, H)
    return img


# ── Social posts ───────────────────────────────────────────────────────────────

def _social_base(bg_color):
    img = Image.new("RGB", SOCIAL, bg_color)
    draw = ImageDraw.Draw(img)
    return img, draw


def _social_booking():
    """1080×1080 — Booking Reminder."""
    img, draw = _social_base(TEAL)
    W = H = 1080

    # Cream frame
    draw.rectangle([30, 30, W - 30, H - 30], outline=CREAM, width=6)
    gold_rule(draw, 58, x0=58, x1=W - 58, thickness=4, canvas_w=W)
    gold_rule(draw, H - 62, x0=58, x1=W - 58, thickness=4, canvas_w=W)

    paw_print(draw, W // 2, 220, size=100, fill=GOLD)
    centred(draw, 360, "Time to Book Your", CREAM, font(58), canvas_w=W)
    centred(draw, 440, "NEXT GROOM!", WHITE, font(95, bold=True), canvas_w=W)

    gold_rule(draw, 570, x0=120, x1=W - 120, thickness=5, canvas_w=W)

    centred(draw, 602, "Is your dog due for a trim?", CREAM, font(50), canvas_w=W)
    centred(draw, 672, "Regular grooming keeps your", CREAM, font(44), canvas_w=W)
    centred(draw, 728, "pup healthy & happy! 🐶", CREAM, font(44), canvas_w=W)

    gold_rule(draw, 808, x0=120, x1=W - 120, thickness=5, canvas_w=W)

    draw.rectangle([100, 835, W - 100, 940], fill=GOLD)
    centred(draw, 862, "BOOK NOW  •  07700 000000", CHARCOAL, font(50, bold=True), canvas_w=W)

    centred(draw, 960, "YOUR SALON NAME", WHITE, font(40, bold=True), canvas_w=W)
    centred(draw, 1010, "www.yoursalon.com", GOLD, font(34), canvas_w=W)
    return img


def _social_before_after():
    """1080×1080 — Before & After placeholder."""
    img, draw = _social_base(CHARCOAL)
    W = H = 1080

    draw.rectangle([0, 0, W, 8], fill=GOLD)
    gold_rule(draw, H - 8, thickness=8, canvas_w=W)

    centred(draw, 38, "YOUR SALON NAME  🐾", GOLD, font(42, bold=True), canvas_w=W)
    gold_rule(draw, 100, x0=80, x1=W - 80, thickness=4, canvas_w=W)

    centred(draw, 120, "BEFORE & AFTER", WHITE, font(90, bold=True), canvas_w=W)
    centred(draw, 232, "The transformation is REAL 😍", CREAM, font(48), canvas_w=W)
    gold_rule(draw, 302, x0=80, x1=W - 80, thickness=4, canvas_w=W)

    # Two photo placeholder boxes
    for i, (label, x0) in enumerate([("BEFORE", 60), ("AFTER", W // 2 + 20)]):
        draw.rectangle([x0, 330, x0 + W // 2 - 80, 750], fill=TEAL)
        paw_print(draw, x0 + (W // 2 - 80) // 2, 530, size=80, fill=GOLD)
        centred_x = x0 + (W // 2 - 80) // 2
        draw.text((centred_x - 60, 660), label, fill=WHITE, font=font(52, bold=True))
        draw.text((centred_x - 100, 718), "Add your photo", fill=CREAM, font=font(36))

    draw.rectangle([60, 756, W - 60, 758], fill=GOLD)

    centred(draw, 778, "Every dog deserves to look their best!", CREAM, font(42), canvas_w=W)
    centred(draw, 840, "Book a transformation today →", GOLD, font(44, bold=True), canvas_w=W)
    draw.rectangle([100, 900, W - 100, 1000], fill=TEAL)
    centred(draw, 928, "📞  07700 000000  |  www.yoursalon.com", WHITE, font(42), canvas_w=W)
    return img


def _social_tips():
    """1080×1080 — Grooming Tips."""
    img, draw = _social_base(CREAM)
    W = H = 1080

    draw.rectangle([0, 0, W, 240], fill=TEAL)
    paw_print(draw, 110, 120, size=55, fill=GOLD)
    paw_print(draw, W - 110, 120, size=55, fill=GOLD)
    centred(draw, 20, "PRO GROOMING TIPS", WHITE, font(72, bold=True), canvas_w=W)
    centred(draw, 116, "from YOUR SALON NAME 🐾", GOLD, font(42), canvas_w=W)
    gold_rule(draw, 240, thickness=8, canvas_w=W)

    tips = [
        ("1", "Brush your dog 2-3x per week to prevent matting"),
        ("2", "Check ears weekly for redness or odour"),
        ("3", "Trim nails every 4-6 weeks"),
        ("4", "Bath every 4-8 weeks (or as needed)"),
        ("5", "Book regular grooms — don't let coats get out of control!"),
    ]
    y = 268
    for num, tip in tips:
        draw.rectangle([60, y, W - 60, y + 108], fill=WHITE)
        draw.rectangle([60, y, 130, y + 108], fill=TEAL)
        gold_rule(draw, y + 106, x0=60, x1=W - 60, thickness=2)
        centred(draw, y + 28, num, WHITE, font(52, bold=True), canvas_w=130)
        draw.text((148, y + 22), tip, fill=CHARCOAL, font=font(38))
        y += 120

    gold_rule(draw, y + 20, x0=60, x1=W - 60, thickness=5, canvas_w=W)
    centred(draw, y + 42, "Need a professional groom? Call us today!", TEAL,
            font(42, bold=True), canvas_w=W)
    draw.rectangle([100, y + 110, W - 100, y + 210], fill=TEAL)
    centred(draw, y + 138, "07700 000000  •  www.yoursalon.com", WHITE, font(42), canvas_w=W)
    return img


def _social_testimonial():
    """1080×1080 — Testimonial layout."""
    img, draw = _social_base(CHARCOAL)
    W = H = 1080

    draw.rectangle([0, 0, W, 10], fill=GOLD)
    gold_rule(draw, H - 10, thickness=10, canvas_w=W)
    draw.rectangle([0, 0, 10, H], fill=GOLD)
    draw.rectangle([W - 10, 0, W, H], fill=GOLD)

    paw_print(draw, W // 2, 120, size=75, fill=GOLD)
    centred(draw, 234, "★ ★ ★ ★ ★", GOLD, font(64), canvas_w=W)
    gold_rule(draw, 318, x0=100, x1=W - 100, thickness=5, canvas_w=W)

    # Quote
    draw.text((80, 348), '"', fill=TEAL, font=font(160, bold=True))
    quote_lines = [
        "Absolutely love this salon!",
        "My cockapoo looks incredible",
        "every single time. The team",
        "are so gentle and caring.",
        "Would recommend to everyone!",
    ]
    y = 380
    for line in quote_lines:
        centred(draw, y, line, WHITE, font(50), canvas_w=W)
        y += 72

    draw.text((W - 120, y - 80), '"', fill=TEAL, font=font(160, bold=True))
    gold_rule(draw, y + 20, x0=100, x1=W - 100, thickness=5, canvas_w=W)

    centred(draw, y + 44, "— Happy Customer  🐾", GOLD, font(44, bold=True), canvas_w=W)
    centred(draw, y + 110, "YOUR SALON NAME", WHITE, font(46, bold=True), canvas_w=W)
    centred(draw, y + 168, "Share your experience! Tag us in your photos", CREAM, font(36), canvas_w=W)
    return img


def _social_seasonal():
    """1080×1080 — Seasonal Promo."""
    img, draw = _social_base(TEAL)
    W = H = 1080

    draw.rectangle([30, 30, W - 30, H - 30], outline=GOLD, width=8)
    draw.rectangle([46, 46, W - 46, H - 46], outline=CREAM, width=3)

    centred(draw, 68, "🐾  SPECIAL OFFER  🐾", GOLD, font(54, bold=True), canvas_w=W)
    gold_rule(draw, 140, x0=80, x1=W - 80, thickness=5, canvas_w=W)

    centred(draw, 168, "SEASONAL GROOM", WHITE, font(88, bold=True), canvas_w=W)
    centred(draw, 280, "PACKAGE", GOLD, font(100, bold=True), canvas_w=W)
    gold_rule(draw, 408, x0=80, x1=W - 80, thickness=5, canvas_w=W)

    paw_print(draw, W // 2, 510, size=110, fill=GOLD)

    centred(draw, 656, "This season, treat your pup to", CREAM, font(48), canvas_w=W)
    centred(draw, 720, "our special pamper package", CREAM, font(48), canvas_w=W)

    draw.rectangle([100, 800, W - 100, 900], fill=GOLD)
    centred(draw, 826, "SAVE £15 — Limited Time Only!", CHARCOAL, font(52, bold=True), canvas_w=W)

    gold_rule(draw, 920, x0=80, x1=W - 80, thickness=5, canvas_w=W)
    centred(draw, 944, "📞  07700 000000", WHITE, font(50), canvas_w=W)
    centred(draw, 1005, "YOUR SALON NAME", GOLD, font(42, bold=True), canvas_w=W)
    return img


# ── Build & upload ────────────────────────────────────────────────────────────

TEMPLATES = {
    "DG_Flyer_Services_Promo.png":    (_flyer_promo,       "marketing"),
    "DG_Flyer_New_Client.png":        (_flyer_new_client,  "marketing"),
    "DG_Price_List.png":              (_price_list,        "marketing"),
    "DG_Social_Booking_Reminder.png": (_social_booking,    "marketing"),
    "DG_Social_Before_After.png":     (_social_before_after,"marketing"),
    "DG_Social_Grooming_Tips.png":    (_social_tips,       "marketing"),
    "DG_Social_Testimonial.png":      (_social_testimonial,"marketing"),
    "DG_Social_Seasonal_Promo.png":   (_social_seasonal,   "marketing"),
}


def build_all() -> dict:
    urls = {}
    print(f"\n{'='*60}")
    print("DOG GROOMING — MARKETING TEMPLATES (8 templates)")
    print(f"{'='*60}")
    for filename, (build_fn, category) in TEMPLATES.items():
        print(f"\n  Building {filename}...")
        img = build_fn()
        local = OUTPUT / filename
        img.save(local, "PNG", dpi=(300, 300))
        key = f"templates/dog-grooming/{category}/{filename}"
        url = upload_to_spaces(local, key)
        urls[filename] = url
    print(f"\n  ✓ Marketing templates complete — {len(urls)} uploaded")
    return urls


if __name__ == "__main__":
    result = build_all()
    for name, url in result.items():
        print(f"  {name}: {url}")
