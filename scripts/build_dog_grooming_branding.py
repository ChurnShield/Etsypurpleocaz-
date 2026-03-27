#!/usr/bin/env python3
"""
Dog Grooming — Branding Kit (10 templates)
1.  Business Card Dark
2.  Business Card Light
3.  Appointment Card Dark
4.  Appointment Card Light
5.  Loyalty Card (10 stamps)
6.  Gift Certificate
7.  Welcome Sign (A4)
8.  Thank You Card
9.  Referral Card
10. Opening Hours Sign (A4)
"""
import sys
from pathlib import Path

PROJECT = Path("/root/NEW-AI-PROJECT")
sys.path.insert(0, str(PROJECT / "scripts"))
from dog_grooming_design_system import (
    TEAL, GOLD, CREAM, CHARCOAL, WHITE, CREAM_ALT, TEAL_DARK,
    BCARD, GIFT_CERT, A4,
    font, centred, right, gold_rule, teal_bar,
    paw_print, a4_header, a4_footer, upload_to_spaces,
)
from PIL import Image, ImageDraw

OUTPUT = PROJECT / "outputs" / "dog-grooming" / "branding"
OUTPUT.mkdir(parents=True, exist_ok=True)

URLS = {}

# ── Helpers ───────────────────────────────────────────────────────────────────

def _bcard_dark():
    """Dark business card (1050×600)."""
    W, H = BCARD
    img = Image.new("RGB", BCARD, CHARCOAL)
    draw = ImageDraw.Draw(img)

    # Top teal bar
    draw.rectangle([0, 0, W, 10], fill=TEAL)
    # Left teal accent strip
    draw.rectangle([0, 0, 12, H], fill=TEAL)
    # Gold bottom rule
    gold_rule(draw, H - 10, thickness=10, canvas_w=W)

    # Paw print — top right
    paw_print(draw, W - 100, 100, size=55, fill=GOLD)

    # Salon name
    draw.text((60, 55), "YOUR SALON NAME", fill=GOLD, font=font(44, bold=True))
    draw.text((60, 112), "Professional Dog Grooming", fill=CREAM, font=font(28))

    # Divider
    draw.rectangle([60, 160, W - 60, 163], fill=TEAL)

    # Contact info
    y = 185
    for line in ["📍  123 High Street, Your Town",
                 "📞  07700 000000",
                 "✉   hello@yoursalon.com",
                 "🌐  www.yoursalon.com"]:
        draw.text((60, y), line, fill=WHITE, font=font(28))
        y += 52

    # Mini tagline
    draw.text((60, H - 65), "Book online or call us today!", fill=GOLD, font=font(26, bold=True))

    return img


def _bcard_light():
    """Light business card (1050×600)."""
    W, H = BCARD
    img = Image.new("RGB", BCARD, CREAM)
    draw = ImageDraw.Draw(img)

    # Teal header band
    draw.rectangle([0, 0, W, 180], fill=TEAL)
    gold_rule(draw, 180, thickness=8, canvas_w=W)

    # Paw print in header
    paw_print(draw, W - 110, 90, size=55, fill=GOLD)

    # Salon name in header
    draw.text((40, 30), "YOUR SALON NAME", fill=WHITE, font=font(44, bold=True))
    draw.text((40, 88), "Professional Dog Grooming", fill=GOLD, font=font(28))

    # Contact info on cream background
    y = 210
    for line in ["📍  123 High Street, Your Town",
                 "📞  07700 000000",
                 "✉   hello@yoursalon.com",
                 "🌐  www.yoursalon.com"]:
        draw.text((40, y), line, fill=CHARCOAL, font=font(28))
        y += 50

    draw.text((40, H - 58), "Book online or call us today!", fill=TEAL, font=font(26, bold=True))
    gold_rule(draw, H - 10, thickness=10, canvas_w=W)

    return img


def _appt_dark():
    """Dark appointment card (1050×600)."""
    W, H = BCARD
    img = Image.new("RGB", BCARD, CHARCOAL)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 10], fill=TEAL)
    draw.rectangle([0, 0, 12, H], fill=TEAL)
    gold_rule(draw, H - 10, thickness=10, canvas_w=W)

    paw_print(draw, W - 90, 85, size=45, fill=GOLD)
    draw.text((60, 30), "YOUR SALON NAME", fill=GOLD, font=font(38, bold=True))
    draw.text((60, 82), "Your Next Appointment", fill=CREAM, font=font(26))
    draw.rectangle([60, 128, W - 60, 131], fill=TEAL)

    y = 155
    for label in ["Dog's name:", "Date:", "Time:", "Groomer:", "Notes:"]:
        draw.text((60, y), label, fill=GOLD, font=font(27, bold=True))
        draw.rectangle([220 if label != "Notes:" else 140, y + 36,
                        W - 60, y + 38], fill=WHITE)
        y += 68 if label != "Notes:" else 72

    return img


def _appt_light():
    """Light appointment card (1050×600)."""
    W, H = BCARD
    img = Image.new("RGB", BCARD, CREAM)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 160], fill=TEAL)
    gold_rule(draw, 160, thickness=7, canvas_w=W)
    paw_print(draw, W - 95, 80, size=48, fill=GOLD)
    draw.text((35, 22), "YOUR SALON NAME", fill=WHITE, font=font(38, bold=True))
    draw.text((35, 80), "Your Next Appointment", fill=GOLD, font=font(26))

    y = 185
    for label in ["Dog's name:", "Date:", "Time:", "Groomer:", "Notes:"]:
        draw.text((35, y), label, fill=TEAL, font=font(27, bold=True))
        draw.rectangle([210 if label != "Notes:" else 130, y + 36,
                        W - 35, y + 38], fill=TEAL)
        y += 66 if label != "Notes:" else 70
    gold_rule(draw, H - 10, thickness=10, canvas_w=W)
    return img


def _loyalty():
    """Loyalty stamp card — 10th groom free (1050×600)."""
    W, H = BCARD
    img = Image.new("RGB", BCARD, CREAM)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 150], fill=TEAL)
    gold_rule(draw, 150, thickness=7, canvas_w=W)
    paw_print(draw, W - 90, 75, size=45, fill=GOLD)

    draw.text((35, 18), "YOUR SALON NAME", fill=WHITE, font=font(38, bold=True))
    draw.text((35, 78), "Loyalty Reward Card", fill=GOLD, font=font(28))

    centred(draw, 165, "Collect 10 stamps • 10th Groom FREE!", TEAL, font(26, bold=True), canvas_w=W)

    # 10 stamp boxes in 2 rows of 5
    box_size = 120
    gap = 22
    total_w = 5 * box_size + 4 * gap
    start_x = (W - total_w) // 2
    for row in range(2):
        for col in range(5):
            bx = start_x + col * (box_size + gap)
            by = 215 + row * (box_size + 18)
            n = row * 5 + col + 1
            draw.rectangle([bx, by, bx + box_size, by + box_size],
                           outline=TEAL, width=3, fill=WHITE)
            if n == 10:
                draw.rectangle([bx, by, bx + box_size, by + box_size],
                               fill=GOLD)
                draw.text((bx + box_size // 2, by + box_size // 2 - 18),
                          "FREE!", fill=WHITE, font=font(22, bold=True),
                          anchor="mm")
            else:
                paw_print(draw, bx + box_size // 2, by + box_size // 2,
                          size=22, fill=TEAL)
            # stamp number
            draw.text((bx + box_size - 22, by + box_size - 28), str(n),
                      fill=CHARCOAL if n != 10 else WHITE, font=font(18))

    draw.text((35, H - 55), "Name: _______________________", fill=CHARCOAL, font=font(26))
    gold_rule(draw, H - 10, thickness=10, canvas_w=W)
    return img


def _gift_cert():
    """Gift certificate (2550×1800)."""
    W, H = GIFT_CERT
    img = Image.new("RGB", GIFT_CERT, CREAM)
    draw = ImageDraw.Draw(img)

    # Decorative teal border frame
    border = 40
    draw.rectangle([0, 0, W, H], fill=TEAL)
    draw.rectangle([border, border, W - border, H - border], fill=CREAM)

    # Gold inner border
    gold_rule(draw, border + 12, x0=border + 12, x1=W - border - 12,
              thickness=4, canvas_w=W)
    gold_rule(draw, H - border - 16, x0=border + 12, x1=W - border - 12,
              thickness=4, canvas_w=W)

    # Header
    centred(draw, 110, "GIFT CERTIFICATE", TEAL, font(110, bold=True), canvas_w=W)

    # Paw prints — decorative corners
    for px, py in [(200, 160), (W - 200, 160), (200, H - 180), (W - 200, H - 180)]:
        paw_print(draw, px, py, size=45, fill=GOLD)

    gold_rule(draw, 280, x0=160, x1=W - 160, thickness=5, canvas_w=W)

    # Certificate body
    centred(draw, 340, "This certificate entitles", CHARCOAL, font(56), canvas_w=W)
    gold_rule(draw, 440, x0=300, x1=W - 300, thickness=3, canvas_w=W)
    centred(draw, 470, "RECIPIENT NAME", TEAL, font(72, bold=True), canvas_w=W)
    gold_rule(draw, 570, x0=300, x1=W - 300, thickness=3, canvas_w=W)
    centred(draw, 620, "to ONE complimentary dog grooming service worth", CHARCOAL, font(50), canvas_w=W)

    # Amount box
    draw.rectangle([W // 2 - 200, 710, W // 2 + 200, 830], fill=TEAL)
    centred(draw, 738, "£__________", WHITE, font(80, bold=True), canvas_w=W)

    centred(draw, 870, "at YOUR SALON NAME", TEAL, font(56, bold=True), canvas_w=W)

    gold_rule(draw, 960, x0=160, x1=W - 160, thickness=5, canvas_w=W)

    # From / message / expiry
    y = 990
    for label, val in [("From:", "_" * 30),
                       ("Message:", "_" * 40),
                       ("Valid until:", "_" * 20)]:
        lw = draw.textbbox((0, 0), label, font=font(44, bold=True))[2]
        draw.text((250, y), label, fill=TEAL, font=font(44, bold=True))
        draw.text((250 + lw + 20, y), val, fill=CHARCOAL, font=font(44))
        y += 90

    # Salon details
    centred(draw, 1340, "YOUR SALON NAME  |  📞 07700 000000  |  www.yoursalon.com",
            CHARCOAL, font(40), canvas_w=W)
    centred(draw, 1415, "Professional Dog Grooming", GOLD, font(38, bold=True), canvas_w=W)

    # Border paw prints on sides
    for py in [H // 2 - 60, H // 2 + 100]:
        paw_print(draw, border + 70, py, size=35, fill=GOLD)
        paw_print(draw, W - border - 70, py, size=35, fill=GOLD)

    draw.rectangle([0, H - border, W, H], fill=TEAL)
    return img


def _welcome_sign():
    """A4 Welcome Sign (2480×3508)."""
    W, H = A4
    img = Image.new("RGB", A4, CREAM)
    draw = ImageDraw.Draw(img)

    # Full teal top third
    draw.rectangle([0, 0, W, 1200], fill=TEAL)

    # Paw trail decoration in teal area
    for i, (px, py) in enumerate([(200, 200), (400, 350), (600, 220),
                                   (W - 200, 200), (W - 400, 350), (W - 600, 220)]):
        paw_print(draw, px, py, size=50, fill=GOLD)

    centred(draw, 280, "WELCOME", WHITE, font(200, bold=True), canvas_w=W)
    centred(draw, 520, "to", GOLD, font(80), canvas_w=W)
    centred(draw, 640, "YOUR SALON NAME", GOLD, font(110, bold=True), canvas_w=W)
    centred(draw, 820, "Professional Dog Grooming", WHITE, font(62), canvas_w=W)

    gold_rule(draw, 1200, thickness=10, canvas_w=W)

    # Main content block
    y = 1280
    centred(draw, y, "We're so glad you're here!", TEAL, font(72, bold=True), canvas_w=W)
    gold_rule(draw, y + 105, x0=200, x1=W - 200, thickness=6, canvas_w=W)

    rules = [
        ("🐾", "Please keep your dog on a lead at all times"),
        ("🐾", "Let our team know about any health conditions"),
        ("🐾", "We'll call you when your dog is ready"),
        ("🐾", "Please arrive on time for your appointment"),
        ("🐾", "Payment is due on collection"),
    ]
    y = 1460
    for icon, text in rules:
        draw.text((160, y), icon, fill=TEAL, font=font(52))
        draw.text((280, y + 4), text, fill=CHARCOAL, font=font(52))
        gold_rule(draw, y + 80, x0=160, x1=W - 160, thickness=3, canvas_w=W)
        y += 120

    # Large paw print centred
    paw_print(draw, W // 2, 2800, size=140, fill=TEAL)

    centred(draw, 3020, "We can't wait to make your dog look fabulous!", TEAL,
            font(58, bold=True), canvas_w=W)
    centred(draw, 3110, "Thank you for choosing us.", CHARCOAL, font(52), canvas_w=W)

    a4_footer(draw, W, H)
    return img


def _thank_you():
    """Thank you card (1050×600)."""
    W, H = BCARD
    img = Image.new("RGB", BCARD, CHARCOAL)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 12], fill=GOLD)
    gold_rule(draw, H - 12, thickness=12, canvas_w=W)
    draw.rectangle([0, 0, 12, H], fill=GOLD)
    draw.rectangle([W - 12, 0, W, H], fill=GOLD)

    # Big paw print
    paw_print(draw, 130, H // 2 - 10, size=90, fill=TEAL)

    # Text
    draw.text((280, 70), "THANK YOU!", fill=GOLD, font=font(68, bold=True))
    draw.rectangle([280, 160, W - 60, 164], fill=TEAL)
    draw.text((280, 178), "for choosing", fill=CREAM, font=font(34))
    draw.text((280, 224), "YOUR SALON NAME", fill=WHITE, font=font(40, bold=True))
    draw.text((280, 282), "We hope your dog had a wonderful", fill=CREAM, font=font(28))
    draw.text((280, 322), "experience with us today.", fill=CREAM, font=font(28))
    gold_rule(draw, 380, x0=280, canvas_w=W - 60, thickness=3)
    draw.text((280, 398), "See you next time! 🐾", fill=GOLD, font=font(32, bold=True))
    draw.text((280, 454), "📞  07700 000000", fill=CREAM, font=font(27))
    draw.text((280, 494), "🌐  www.yoursalon.com", fill=CREAM, font=font(27))
    return img


def _referral():
    """Referral card (1050×600)."""
    W, H = BCARD
    img = Image.new("RGB", BCARD, CREAM)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 170], fill=TEAL)
    gold_rule(draw, 170, thickness=8, canvas_w=W)
    paw_print(draw, W - 100, 85, size=50, fill=GOLD)

    draw.text((40, 20), "YOUR SALON NAME", fill=WHITE, font=font(38, bold=True))
    draw.text((40, 78), "Refer a Friend • Earn Rewards", fill=GOLD, font=font(26))

    centred(draw, 200, "Refer a friend and you BOTH receive:", TEAL, font(29, bold=True), canvas_w=W)
    gold_rule(draw, 248, x0=60, x1=W - 60, thickness=3, canvas_w=W)

    rewards = [
        "✓  YOU receive £10 off your next groom",
        "✓  YOUR FRIEND gets 20% off their first visit",
        "✓  No limit — refer as many as you like!",
    ]
    y = 268
    for r in rewards:
        draw.text((60, y), r, fill=CHARCOAL, font=font(28))
        y += 54

    gold_rule(draw, 445, x0=60, x1=W - 60, thickness=3, canvas_w=W)
    centred(draw, 462, "Just mention this card when booking", TEAL, font(26), canvas_w=W)
    centred(draw, 504, "📞 07700 000000   |   www.yoursalon.com", CHARCOAL, font(24), canvas_w=W)
    gold_rule(draw, H - 10, thickness=10, canvas_w=W)
    return img


def _opening_hours():
    """Opening Hours sign (A4 portrait)."""
    W, H = A4
    img = Image.new("RGB", A4, CREAM)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 700], fill=TEAL)

    paw_print(draw, 200, 280, size=90, fill=GOLD)
    paw_print(draw, W - 200, 280, size=90, fill=GOLD)

    centred(draw, 80, "OPENING HOURS", WHITE, font(150, bold=True), canvas_w=W)
    centred(draw, 290, "YOUR SALON NAME", GOLD, font(80, bold=True), canvas_w=W)
    centred(draw, 415, "Professional Dog Grooming", WHITE, font(52), canvas_w=W)
    gold_rule(draw, 700, thickness=10, canvas_w=W)

    # Hours table
    days = [
        ("Monday",    "9:00am – 5:00pm"),
        ("Tuesday",   "9:00am – 5:00pm"),
        ("Wednesday", "9:00am – 6:00pm"),
        ("Thursday",  "9:00am – 6:00pm"),
        ("Friday",    "9:00am – 5:00pm"),
        ("Saturday",  "9:00am – 4:00pm"),
        ("Sunday",    "Closed"),
    ]
    y = 760
    for i, (day, hours) in enumerate(days):
        bg = CREAM_ALT if i % 2 else CREAM
        draw.rectangle([120, y, W - 120, y + 100], fill=bg)
        gold_rule(draw, y + 98, x0=120, x1=W - 120, thickness=2, canvas_w=W)
        draw.text((160, y + 22), day, fill=TEAL if hours != "Closed" else CHARCOAL,
                  font=font(52, bold=True))
        right(draw, W - 140, y + 22, hours,
              fill=CHARCOAL if hours != "Closed" else (200, 50, 50),
              f=font(52, bold=(hours == "Closed")))
        y += 100

    # Border decorations
    for py in [1900, 2100, 2300]:
        paw_print(draw, 80, py, size=28, fill=GOLD)
        paw_print(draw, W - 80, py, size=28, fill=GOLD)

    centred(draw, 2850, "Appointments recommended — walk-ins welcome!", TEAL,
            font(54, bold=True), canvas_w=W)
    centred(draw, 2960, "📞  07700 000000   •   www.yoursalon.com", CHARCOAL,
            font(46), canvas_w=W)
    a4_footer(draw, W, H)
    return img


# ── Build & upload ────────────────────────────────────────────────────────────

TEMPLATES = {
    "DG_Business_Card_Dark.png":    (_bcard_dark,   "branding"),
    "DG_Business_Card_Light.png":   (_bcard_light,  "branding"),
    "DG_Appointment_Card_Dark.png": (_appt_dark,    "branding"),
    "DG_Appointment_Card_Light.png":(_appt_light,   "branding"),
    "DG_Loyalty_Card.png":          (_loyalty,      "branding"),
    "DG_Gift_Certificate.png":      (_gift_cert,    "branding"),
    "DG_Welcome_Sign.png":          (_welcome_sign, "branding"),
    "DG_Thank_You_Card.png":        (_thank_you,    "branding"),
    "DG_Referral_Card.png":         (_referral,     "branding"),
    "DG_Opening_Hours_Sign.png":    (_opening_hours,"branding"),
}


def build_all() -> dict:
    urls = {}
    print(f"\n{'='*60}")
    print("DOG GROOMING — BRANDING KIT (10 templates)")
    print(f"{'='*60}")
    for filename, (build_fn, category) in TEMPLATES.items():
        print(f"\n  Building {filename}...")
        img = build_fn()
        local = OUTPUT / filename
        img.save(local, "PNG", dpi=(300, 300))
        key = f"templates/dog-grooming/{category}/{filename}"
        url = upload_to_spaces(local, key)
        urls[filename] = url
    print(f"\n  ✓ Branding kit complete — {len(urls)} templates uploaded")
    return urls


if __name__ == "__main__":
    result = build_all()
    for name, url in result.items():
        print(f"  {name}: {url}")
