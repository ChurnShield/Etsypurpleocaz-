#!/usr/bin/env python3
"""
Dog Grooming — Client Forms (9 A4 templates)
1.  Client Consent Form
2.  Pre-Groom Health Assessment
3.  Pet Intake Form
4.  Grooming Record Card
5.  Matting Consent / Shave Release
6.  Photo & Video Release
7.  Cancellation & Deposit Policy
8.  Invoice
9.  Booking Confirmation
"""
import sys
from pathlib import Path

PROJECT = Path("/root/NEW-AI-PROJECT")
sys.path.insert(0, str(PROJECT / "scripts"))
from dog_grooming_design_system import (
    TEAL, GOLD, CREAM, CHARCOAL, WHITE, CREAM_ALT,
    A4, font, centred, right, gold_rule, section_head,
    field_line, field_pair, checkbox, table_row,
    paw_print, a4_header, a4_footer, upload_to_spaces,
)
from PIL import Image, ImageDraw

OUTPUT = PROJECT / "outputs" / "dog-grooming" / "forms"
OUTPUT.mkdir(parents=True, exist_ok=True)

MARGIN = 120
FIELD_W = A4[0] - MARGIN * 2


def _blank_a4(title: str):
    img = Image.new("RGB", A4, CREAM)
    draw = ImageDraw.Draw(img)
    y = a4_header(img, draw, title)
    return img, draw, y


# ── 1. Client Consent Form ────────────────────────────────────────────────────

def _consent_form():
    img, draw, y = _blank_a4("CLIENT CONSENT FORM")

    # Owner info
    y = section_head(draw, MARGIN, y, "OWNER INFORMATION", width=FIELD_W)
    y = field_pair(draw, MARGIN, y + 18, "First name:", "Last name:", total_w=FIELD_W)
    y = field_pair(draw, MARGIN, y + 12, "Phone number:", "Email address:", total_w=FIELD_W)
    y = field_line(draw, MARGIN, y + 12, "Home address:", width=FIELD_W)
    y += 12

    # Dog info
    y = section_head(draw, MARGIN, y, "DOG INFORMATION", width=FIELD_W)
    y = field_pair(draw, MARGIN, y + 18, "Dog's name:", "Breed:", total_w=FIELD_W)
    y = field_pair(draw, MARGIN, y + 12, "Date of birth / Age:", "Sex:  □ Male  □ Female  □ Neutered", total_w=FIELD_W)
    y = field_pair(draw, MARGIN, y + 12, "Coat type:", "Weight (approx):", total_w=FIELD_W)
    y = field_pair(draw, MARGIN, y + 12, "Vet name:", "Vet phone:", total_w=FIELD_W)
    y += 12

    # Consent
    y = section_head(draw, MARGIN, y, "CONSENT & AGREEMENT", width=FIELD_W)
    consents = [
        "I confirm the above dog is in good health and up to date with vaccinations.",
        "I authorise grooming services and emergency veterinary treatment if required.",
        "I understand pricing may vary based on coat condition and behaviour.",
        "I agree to the salon's cancellation and late collection policies.",
        "I accept that matted coats may require shaving for the dog's welfare.",
    ]
    y += 18
    for c in consents:
        y = checkbox(draw, MARGIN, y, c, font_size=34)
        y += 4

    y += 20
    gold_rule(draw, y, x0=MARGIN, x1=A4[0] - MARGIN, thickness=4)
    y += 28
    y = field_pair(draw, MARGIN, y, "Owner signature:", "Date:", total_w=FIELD_W)
    y = field_line(draw, MARGIN, y + 12, "Emergency contact name & phone:", width=FIELD_W)
    draw.text((MARGIN, y + 12), "Referred by:", fill=CHARCOAL, font=font(34, bold=True))
    y = checkbox(draw, MARGIN + 240, y + 6, "Friend / family     □  Social media     □  Google     □  Other",
                 font_size=32)

    a4_footer(draw, *A4)
    return img


# ── 2. Pre-Groom Health Assessment ───────────────────────────────────────────

def _health_assessment():
    img, draw, y = _blank_a4("PRE-GROOM HEALTH ASSESSMENT")

    y = section_head(draw, MARGIN, y, "BASIC INFO", width=FIELD_W)
    y = field_pair(draw, MARGIN, y + 18, "Dog's name:", "Owner name:", total_w=FIELD_W)
    y = field_pair(draw, MARGIN, y + 12, "Today's date:", "Appointment time:", total_w=FIELD_W)
    y += 12

    y = section_head(draw, MARGIN, y, "HEALTH CHECK — Please answer yes or no", width=FIELD_W)
    questions = [
        ("Is your dog up to date with vaccinations?",  "□ Yes  □ No"),
        ("Any known allergies or sensitivities?",      "□ Yes  □ No"),
        ("Any skin conditions, lumps or sores?",       "□ Yes  □ No"),
        ("Any joint pain or mobility issues?",         "□ Yes  □ No"),
        ("Is your dog on any medication?",             "□ Yes  □ No"),
        ("Has your dog had seizures or fainting?",     "□ Yes  □ No"),
        ("Any heart or breathing conditions?",         "□ Yes  □ No"),
        ("Any history of aggression towards groomers?","□ Yes  □ No"),
        ("Has your dog been groomed before?",          "□ Yes  □ No"),
        ("Any previous bad grooming experiences?",     "□ Yes  □ No"),
    ]
    y += 18
    for i, (q, ans) in enumerate(questions):
        bg = CREAM_ALT if i % 2 else CREAM
        draw.rectangle([MARGIN, y, A4[0] - MARGIN, y + 70], fill=bg)
        gold_rule(draw, y + 68, x0=MARGIN, x1=A4[0] - MARGIN, thickness=1)
        draw.text((MARGIN + 16, y + 14), q, fill=CHARCOAL, font=font(34))
        right(draw, A4[0] - MARGIN - 16, y + 14, ans, fill=TEAL, f=font(34))
        y += 70

    y += 16
    y = section_head(draw, MARGIN, y, "NOTES (IF ANY YES ANSWERS, PLEASE DETAIL BELOW)", width=FIELD_W)
    for _ in range(3):
        y = field_line(draw, MARGIN, y + 18, "", width=FIELD_W, font_size=10)

    a4_footer(draw, *A4)
    return img


# ── 3. Pet Intake Form ────────────────────────────────────────────────────────

def _pet_intake():
    img, draw, y = _blank_a4("PET INTAKE FORM")

    y = section_head(draw, MARGIN, y, "OWNER DETAILS", width=FIELD_W)
    y = field_pair(draw, MARGIN, y + 18, "Owner name:", "Phone:", total_w=FIELD_W)
    y = field_pair(draw, MARGIN, y + 12, "Email:", "Address:", total_w=FIELD_W)
    y = field_pair(draw, MARGIN, y + 12, "Emergency contact:", "Emergency phone:", total_w=FIELD_W)
    y += 12

    y = section_head(draw, MARGIN, y, "PET DETAILS", width=FIELD_W)
    y = field_pair(draw, MARGIN, y + 18, "Dog's name:", "Breed:", total_w=FIELD_W)
    y = field_pair(draw, MARGIN, y + 12, "Age:", "Weight:", total_w=FIELD_W)
    draw.text((MARGIN, y + 12), "Sex:", fill=CHARCOAL, font=font(36, bold=True))
    y = checkbox(draw, MARGIN + 100, y + 12, "Male    □  Female    □  Neutered / Spayed", font_size=34)
    y = field_pair(draw, MARGIN, y + 12, "Coat colour:", "Coat type:", total_w=FIELD_W)
    y = field_line(draw, MARGIN, y + 12, "Distinguishing marks / features:", width=FIELD_W)
    y += 12

    y = section_head(draw, MARGIN, y, "TEMPERAMENT", width=FIELD_W)
    draw.text((MARGIN, y + 18), "Temperament rating:", fill=CHARCOAL, font=font(36, bold=True))
    for i, level in enumerate(["□ Very calm", "□ Calm", "□ Average", "□ Excitable", "□ Anxious", "□ Aggressive"]):
        draw.text((MARGIN + 380 + i * 310, y + 18), level, fill=CHARCOAL, font=font(32))
    y += 64
    y = field_line(draw, MARGIN, y, "Known triggers or fears:", width=FIELD_W)
    y = field_line(draw, MARGIN, y + 12, "Handling notes for groomer:", width=FIELD_W)
    y += 12

    y = section_head(draw, MARGIN, y, "VETERINARY & HEALTH", width=FIELD_W)
    y = field_pair(draw, MARGIN, y + 18, "Vet practice name:", "Vet phone:", total_w=FIELD_W)
    y = field_line(draw, MARGIN, y + 12, "Known allergies / sensitivities:", width=FIELD_W)
    y = field_line(draw, MARGIN, y + 12, "Current medications:", width=FIELD_W)
    y = field_line(draw, MARGIN, y + 12, "Health conditions we should know about:", width=FIELD_W)

    a4_footer(draw, *A4)
    return img


# ── 4. Grooming Record Card ───────────────────────────────────────────────────

def _grooming_record():
    img, draw, y = _blank_a4("GROOMING RECORD CARD")

    y = section_head(draw, MARGIN, y, "PET DETAILS", width=FIELD_W)
    y = field_pair(draw, MARGIN, y + 18, "Dog's name:", "Breed:", total_w=FIELD_W)
    y = field_pair(draw, MARGIN, y + 12, "Owner name:", "Phone:", total_w=FIELD_W)
    y += 18

    # Session log table
    y = section_head(draw, MARGIN, y, "GROOMING SESSION LOG", width=FIELD_W)
    headers = ["Date", "Service", "Cost", "Groomer", "Notes / Observations"]
    widths = [280, 460, 220, 280, A4[0] - MARGIN * 2 - 280 - 460 - 220 - 280]
    y = table_row(draw, MARGIN, y, headers, widths, row_h=68, header=True)
    for i in range(14):
        y = table_row(draw, MARGIN, y, ["", "", "", "", ""], widths,
                      row_h=60, alt=(i % 2 == 1))

    y += 20
    y = section_head(draw, MARGIN, y, "GROOMING NOTES", width=FIELD_W)
    y = field_line(draw, MARGIN, y + 18, "Preferred style / cut:", width=FIELD_W)
    y = field_line(draw, MARGIN, y + 12, "Products used:", width=FIELD_W)
    y = field_line(draw, MARGIN, y + 12, "Ongoing concerns:", width=FIELD_W)

    a4_footer(draw, *A4)
    return img


# ── 5. Matting Consent / Shave Release ───────────────────────────────────────

def _matting_consent():
    img, draw, y = _blank_a4("MATTING CONSENT & SHAVE RELEASE")

    y = section_head(draw, MARGIN, y, "PET INFORMATION", width=FIELD_W)
    y = field_pair(draw, MARGIN, y + 18, "Dog's name:", "Breed:", total_w=FIELD_W)
    y = field_pair(draw, MARGIN, y + 12, "Owner name:", "Date:", total_w=FIELD_W)
    y += 20

    y = section_head(draw, MARGIN, y, "MATTING NOTICE", width=FIELD_W)
    notice_lines = [
        "Your dog's coat has been assessed as matted / pelted. Attempting to de-matt a severely matted coat",
        "can cause pain, skin irritation, bruising and extreme stress to your dog. In the interest of your",
        "pet's welfare, we recommend a full or partial shave-down.",
    ]
    y += 20
    for line in notice_lines:
        draw.text((MARGIN, y), line, fill=CHARCOAL, font=font(34))
        y += 52
    y += 12

    y = section_head(draw, MARGIN, y, "CONSENT OPTIONS — Please select one", width=FIELD_W)
    options = [
        "I consent to a full shave-down if required for my dog's welfare.",
        "I consent to a partial shave-down of affected areas only.",
        "I do NOT consent to shaving — I understand grooming may not be possible.",
    ]
    y += 20
    for opt in options:
        y = checkbox(draw, MARGIN, y, opt, font_size=36)
        y += 12
    y += 12

    y = section_head(draw, MARGIN, y, "ACKNOWLEDGEMENTS", width=FIELD_W)
    acks = [
        "I understand my dog's coat may look different after a shave and will re-grow.",
        "I acknowledge that skin abnormalities may become visible once coat is removed.",
        "I accept a de-matting surcharge may apply in addition to the standard groom price.",
        "I release the groomer from responsibility for coat condition resulting from matting.",
    ]
    y += 18
    for ack in acks:
        y = checkbox(draw, MARGIN, y, ack, font_size=33)
        y += 6

    y += 24
    gold_rule(draw, y, x0=MARGIN, x1=A4[0] - MARGIN, thickness=4)
    y += 28
    y = field_pair(draw, MARGIN, y, "Owner / authorised signature:", "Date:", total_w=FIELD_W)
    y = field_line(draw, MARGIN, y + 12, "Groomer name:", width=FIELD_W // 2)

    a4_footer(draw, *A4)
    return img


# ── 6. Photo & Video Release ──────────────────────────────────────────────────

def _photo_release():
    img, draw, y = _blank_a4("PHOTO & VIDEO RELEASE FORM")

    y = section_head(draw, MARGIN, y, "PET & OWNER DETAILS", width=FIELD_W)
    y = field_pair(draw, MARGIN, y + 18, "Owner name:", "Dog's name:", total_w=FIELD_W)
    y = field_pair(draw, MARGIN, y + 12, "Phone:", "Date:", total_w=FIELD_W)
    y += 20

    y = section_head(draw, MARGIN, y, "PURPOSE OF PHOTOS / VIDEOS", width=FIELD_W)
    draw.text((MARGIN, y + 18), "Images / videos of your dog may be used for:", fill=CHARCOAL, font=font(36))
    y += 62
    purposes = [
        "Social media posts (Instagram, Facebook, TikTok, etc.)",
        "Website galleries",
        "Marketing materials (flyers, leaflets, banners)",
        "Training and educational purposes",
        "Press and promotional materials",
    ]
    for p in purposes:
        y = checkbox(draw, MARGIN, y, p, font_size=34)
        y += 4
    y += 20

    y = section_head(draw, MARGIN, y, "CONSENT OPTIONS", width=FIELD_W)
    y += 18
    consents = [
        "I GIVE permission to use photos/videos of my dog for the purposes checked above.",
        "I GIVE permission but do NOT want my name associated with images.",
        "I do NOT give permission for any photos/videos of my dog to be used publicly.",
    ]
    for c in consents:
        y = checkbox(draw, MARGIN, y, c, font_size=34)
        y += 12

    y += 12
    draw.text((MARGIN, y), "Note: You may withdraw consent at any time by contacting the salon.",
              fill=TEAL, font=font(34, bold=True))
    y += 60

    y = section_head(draw, MARGIN, y, "SIGNATURE", width=FIELD_W)
    y = field_pair(draw, MARGIN, y + 18, "Owner / authorised signature:", "Date:", total_w=FIELD_W)
    y = field_line(draw, MARGIN, y + 12, "Print name:", width=FIELD_W)

    a4_footer(draw, *A4)
    return img


# ── 7. Cancellation & Deposit Policy ─────────────────────────────────────────

def _cancellation_policy():
    img, draw, y = _blank_a4("CANCELLATION & DEPOSIT POLICY")

    y = section_head(draw, MARGIN, y, "OUR BOOKING & CANCELLATION POLICY", width=FIELD_W)
    policy_sections = [
        ("Deposits", [
            "A 50% non-refundable deposit is required to secure all appointments.",
            "Deposits can be transferred once to a rescheduled appointment.",
            "Full payment is due on collection of your dog.",
        ]),
        ("Cancellations", [
            "Cancellations must be made with at least 48 hours' notice.",
            "Late cancellations (under 48 hours) will forfeit the deposit.",
            "No-shows without notice will be charged the full groom price.",
        ]),
        ("Late Arrivals", [
            "Please arrive on time. Late arrivals may reduce your dog's groom time.",
            "Arrivals more than 15 minutes late may need to be rescheduled.",
            "Rescheduled late arrivals are subject to the cancellation policy.",
        ]),
        ("Late Collection", [
            "Dogs must be collected within 30 minutes of being notified.",
            "A boarding charge of £5 per 30 minutes may apply after this time.",
            "We will contact the emergency contact if you cannot be reached.",
        ]),
    ]

    for section_title, items in policy_sections:
        y += 18
        y = section_head(draw, MARGIN, y, section_title.upper(), width=FIELD_W)
        y += 12
        for item in items:
            paw_print(draw, MARGIN + 22, y + 18, size=14, fill=TEAL)
            draw.text((MARGIN + 52, y + 4), item, fill=CHARCOAL, font=font(34))
            y += 58
    y += 18
    gold_rule(draw, y, x0=MARGIN, x1=A4[0] - MARGIN, thickness=5)
    y += 24
    y = field_pair(draw, MARGIN, y, "I have read and agree to the above policy:", "Date:", total_w=FIELD_W)
    y = field_pair(draw, MARGIN, y + 12, "Owner signature:", "Print name:", total_w=FIELD_W)

    a4_footer(draw, *A4)
    return img


# ── 8. Invoice ────────────────────────────────────────────────────────────────

def _invoice():
    W, H = A4
    img = Image.new("RGB", A4, CREAM)
    draw = ImageDraw.Draw(img)

    # Header
    draw.rectangle([0, 0, W, 340], fill=TEAL)
    paw_print(draw, 180, 170, size=80, fill=GOLD)
    draw.text((300, 60), "YOUR SALON NAME", fill=GOLD, font=font(72, bold=True))
    draw.text((300, 152), "Professional Dog Grooming", fill=CREAM, font=font(44))
    draw.text((300, 220), "📞 07700 000000  |  hello@yoursalon.com", fill=WHITE, font=font(36))
    gold_rule(draw, 340, thickness=8, canvas_w=W)

    # Invoice label
    draw.rectangle([W - 480, 50, W - 40, 200], fill=GOLD)
    centred(draw, 80, "INVOICE", CHARCOAL, font(60, bold=True), canvas_w=W - 40 - (W - 480))
    draw.text((W - 460, 88), "INVOICE", fill=CHARCOAL, font=font(56, bold=True))
    draw.text((W - 460, 156), "No:", fill=CHARCOAL, font=font(38))
    draw.rectangle([W - 380, 156, W - 60, 194], outline=CHARCOAL, width=2)

    y = 360
    # Billing info
    y = section_head(draw, MARGIN, y, "INVOICE TO", width=800)
    y = field_line(draw, MARGIN, y + 18, "Owner name:", width=800)
    y = field_line(draw, MARGIN, y + 10, "Phone:", width=800)
    y = field_pair(draw, MARGIN, y + 10, "Dog's name:", "Date:", total_w=800)
    y += 24

    # Line items table
    y = section_head(draw, MARGIN, y, "SERVICES", width=FIELD_W)
    cols = ["Service", "Description", "Qty", "Unit price", "Total"]
    widths = [360, 720, 120, 200, 200 + (FIELD_W - 360 - 720 - 120 - 200 - 200)]
    widths[-1] = FIELD_W - sum(widths[:-1])
    y = table_row(draw, MARGIN, y, cols, widths, row_h=70, header=True)
    for i in range(6):
        y = table_row(draw, MARGIN, y, ["", "", "", "", ""], widths,
                      row_h=65, alt=(i % 2 == 1))

    # Totals
    y += 12
    for label, val in [("Subtotal:", "£"), ("Discount:", "£"), ("Total:", "£")]:
        bold = "Total" in label
        draw.rectangle([W - MARGIN - 600, y, W - MARGIN, y + 68],
                       fill=TEAL if bold else CREAM_ALT)
        draw.text((W - MARGIN - 580, y + 14), label,
                  fill=WHITE if bold else CHARCOAL, font=font(40, bold=bold))
        right(draw, W - MARGIN - 20, y + 14, val,
              fill=WHITE if bold else CHARCOAL, f=font(40, bold=bold))
        gold_rule(draw, y + 66, x0=W - MARGIN - 600, x1=W - MARGIN, thickness=2)
        y += 68

    y += 20
    y = field_line(draw, MARGIN, y, "Payment method:", width=600)
    draw.text((MARGIN, y + 14), "Thank you for your custom! 🐾  We look forward to seeing you again.",
              fill=TEAL, font=font(36, bold=True))

    a4_footer(draw, W, H)
    return img


# ── 9. Booking Confirmation ───────────────────────────────────────────────────

def _booking_confirmation():
    W, H = A4
    img = Image.new("RGB", A4, CREAM)
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, W, 400], fill=TEAL)
    paw_print(draw, 200, 200, size=88, fill=GOLD)
    paw_print(draw, W - 200, 200, size=88, fill=GOLD)
    centred(draw, 50, "BOOKING CONFIRMED!", WHITE, font(110, bold=True), canvas_w=W)
    centred(draw, 200, "YOUR SALON NAME", GOLD, font(72, bold=True), canvas_w=W)
    centred(draw, 300, "Professional Dog Grooming", WHITE, font(50), canvas_w=W)
    gold_rule(draw, 400, thickness=10, canvas_w=W)

    y = 440
    centred(draw, y, "Thank you for booking with us. Your appointment details are below.",
            CHARCOAL, font(40), canvas_w=W)
    gold_rule(draw, y + 68, x0=MARGIN, x1=W - MARGIN, thickness=6)
    y = 550

    details = [
        ("Dog's name:",      "___________________________________"),
        ("Owner name:",       "___________________________________"),
        ("Service booked:",   "___________________________________"),
        ("Date:",             "___________________________________"),
        ("Time:",             "___________________________________"),
        ("Groomer:",          "___________________________________"),
        ("Estimated duration:","_____________  Estimated cost: £_____________"),
        ("Deposit paid:",     "□ Yes  □ No   Amount: £___________"),
        ("Remaining balance:","£_____________  Due on collection"),
    ]
    for label, val in details:
        lw = draw.textbbox((0, 0), label, font=font(44, bold=True))[2]
        draw.text((MARGIN, y), label, fill=TEAL, font=font(44, bold=True))
        draw.text((MARGIN + lw + 20, y), val, fill=CHARCOAL, font=font(40))
        gold_rule(draw, y + 74, x0=MARGIN, x1=W - MARGIN, thickness=2)
        y += 90

    # Policy reminder
    draw.rectangle([MARGIN, y + 20, W - MARGIN, y + 210], fill=TEAL)
    centred(draw, y + 42, "PLEASE REMEMBER", GOLD, font(52, bold=True), canvas_w=W)
    centred(draw, y + 104, "48 hours' notice required for cancellations.", WHITE, font(40), canvas_w=W)
    centred(draw, y + 158, "Please arrive on time. Contact us: 07700 000000", CREAM, font(36), canvas_w=W)

    a4_footer(draw, W, H)
    return img


# ── Build & upload ────────────────────────────────────────────────────────────

TEMPLATES = {
    "DG_Client_Consent_Form.png":       (_consent_form,         "forms"),
    "DG_PreGroom_Health_Assessment.png":(_health_assessment,    "forms"),
    "DG_Pet_Intake_Form.png":           (_pet_intake,           "forms"),
    "DG_Grooming_Record_Card.png":      (_grooming_record,      "forms"),
    "DG_Matting_Consent.png":           (_matting_consent,      "forms"),
    "DG_Photo_Video_Release.png":       (_photo_release,        "forms"),
    "DG_Cancellation_Policy.png":       (_cancellation_policy,  "forms"),
    "DG_Invoice.png":                   (_invoice,              "forms"),
    "DG_Booking_Confirmation.png":      (_booking_confirmation, "forms"),
}


def build_all() -> dict:
    urls = {}
    print(f"\n{'='*60}")
    print("DOG GROOMING — CLIENT FORMS (9 templates)")
    print(f"{'='*60}")
    for filename, (build_fn, category) in TEMPLATES.items():
        print(f"\n  Building {filename}...")
        img = build_fn()
        local = OUTPUT / filename
        img.save(local, "PNG", dpi=(300, 300))
        key = f"templates/dog-grooming/{category}/{filename}"
        url = upload_to_spaces(local, key)
        urls[filename] = url
    print(f"\n  ✓ Client forms complete — {len(urls)} templates uploaded")
    return urls


if __name__ == "__main__":
    result = build_all()
    for name, url in result.items():
        print(f"  {name}: {url}")
