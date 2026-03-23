#!/usr/bin/env python3
"""Generate 8 professional car detailing client forms as single-page A4 PDFs.
Palette: white background, red #E02020 headers, dark #0D0D0D footer.

Forms:
  1. Vehicle Intake Form
  2. Detailing Consent & Liability Waiver
  3. Service Agreement
  4. Invoice Template
  5. Customer Feedback Form
  6. Appointment Booking Form
  7. Aftercare Instructions
  8. Detailing Package Menu
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, white
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs", "car-detail-forms")

RED = HexColor("#E02020")
DARK = HexColor("#0D0D0D")
LIGHT_GRAY = HexColor("#F5F5F5")
MID_GRAY = HexColor("#999999")
WHITE = HexColor("#FFFFFF")

WIDTH, HEIGHT = A4
MARGIN = 18 * mm
CONTENT_W = WIDTH - 2 * MARGIN

CBX = "\u25a1"


def get_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        "FormTitle", parent=styles["Title"],
        fontName="Times-Italic", fontSize=20,
        textColor=DARK, spaceAfter=2, spaceBefore=0, alignment=TA_CENTER
    ))
    styles.add(ParagraphStyle(
        "StudioName", parent=styles["Normal"],
        fontName="Helvetica", fontSize=9,
        textColor=RED, alignment=TA_CENTER, spaceAfter=1, spaceBefore=0
    ))
    styles.add(ParagraphStyle(
        "SectionHead", parent=styles["Heading2"],
        fontName="Helvetica-Bold", fontSize=12,
        textColor=RED, spaceBefore=10, spaceAfter=3
    ))
    styles.add(ParagraphStyle(
        "Body", parent=styles["Normal"],
        fontName="Helvetica", fontSize=10,
        textColor=DARK, leading=13, spaceAfter=3
    ))
    styles.add(ParagraphStyle(
        "BodySmall", parent=styles["Normal"],
        fontName="Helvetica", fontSize=8,
        textColor=DARK, leading=10, spaceAfter=2
    ))
    styles.add(ParagraphStyle(
        "Footer", parent=styles["Normal"],
        fontName="Helvetica", fontSize=7,
        textColor=WHITE, alignment=TA_CENTER
    ))
    return styles


_cached_styles = None


def S():
    global _cached_styles
    if _cached_styles is None:
        _cached_styles = get_styles()
    return _cached_styles


def red_divider():
    return HRFlowable(width="100%", thickness=1.2, color=RED, spaceAfter=6, spaceBefore=2)


def field(label):
    return Paragraph(f"<b>{label}:</b>  {'_' * 60}", S()["Body"])


def field2(l1, l2):
    s = S()["Body"]
    data = [[Paragraph(f"<b>{l1}:</b>  {'_' * 24}", s),
             Paragraph(f"<b>{l2}:</b>  {'_' * 24}", s)]]
    t = Table(data, colWidths=[CONTENT_W / 2] * 2)
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    return t


def cb(text):
    return Paragraph(f"{CBX}  {text}", S()["Body"])


def cb_row(items, cols=3):
    s = S()["Body"]
    col_w = CONTENT_W / cols
    rows = []
    for i in range(0, len(items), cols):
        chunk = items[i:i + cols]
        row = [Paragraph(f"{CBX}  {it}", s) for it in chunk]
        while len(row) < cols:
            row.append(Paragraph("", s))
        rows.append(row)
    t = Table(rows, colWidths=[col_w] * cols)
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    return t


def page_header(story, title):
    s = S()
    story.append(Paragraph("Y O U R   D E T A I L I N G   S T U D I O", s["StudioName"]))
    story.append(Paragraph(title, s["FormTitle"]))
    story.append(red_divider())


def section(story, title):
    story.append(Paragraph(title, S()["SectionHead"]))
    story.append(red_divider())


def make_doc(filename, title):
    filepath = os.path.join(OUTPUT_DIR, filename)
    doc = SimpleDocTemplate(
        filepath, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=14 * mm,
        title=title, author="PurpleOcaz Car Detail Templates"
    )
    return doc, filepath


def sig_block(story):
    story.append(field2("Customer Signature", "Date"))


def text_area(story, label, lines=4):
    story.append(Paragraph(f"<b>{label}:</b>", S()["Body"]))
    for _ in range(lines):
        story.append(Paragraph("_" * 85, S()["Body"]))


# ── Form 1: Vehicle Intake Form ──────────────────────────────────────

def form_01_vehicle_intake():
    doc, path = make_doc("Vehicle_Intake_Form.pdf", "Vehicle Intake Form")
    story = []
    page_header(story, "Vehicle Intake Form")

    section(story, "Customer Information")
    story.append(field("Customer Name"))
    story.append(field2("Phone", "Email"))

    section(story, "Vehicle Details")
    story.append(field2("Make / Model", "Year"))
    story.append(field2("Registration", "Colour"))
    story.append(field("Mileage"))

    section(story, "Service Requested")
    story.append(cb_row([
        "Exterior Wash", "Full Exterior Detail", "Interior Valet",
        "Full Interior Detail", "Machine Polish", "Ceramic Coating",
        "Paint Correction", "Engine Bay Clean", "Other"
    ], cols=3))
    story.append(field("Special Instructions"))

    section(story, "Pre-Existing Damage Notes")
    text_area(story, "Please note any scratches, dents, chips or other damage", lines=5)

    story.append(Spacer(1, 6))
    sig_block(story)

    doc.build(story)
    return path


# ── Form 2: Consent & Liability Waiver ───────────────────────────────

def form_02_consent():
    doc, path = make_doc("Consent_Liability_Waiver.pdf", "Detailing Consent & Liability Waiver")
    story = []
    page_header(story, "Consent & Liability Waiver")
    s = S()

    section(story, "Pre-Existing Damage Disclaimer")
    story.append(Paragraph(
        "The detailing studio will inspect and photograph the vehicle before commencing work. "
        "Any pre-existing damage (scratches, dents, paint chips, stone chips, swirl marks, trim damage) "
        "will be documented on the Vehicle Intake Form. The studio accepts no responsibility for "
        "damage that existed prior to the detailing service.",
        s["Body"]
    ))

    section(story, "Liability Limitations")
    for clause in [
        "The studio exercises reasonable care during all detailing procedures.",
        "The studio is not liable for damage caused by pre-existing paint defects, clear coat failure, aftermarket wraps, or poorly applied PPF.",
        "Machine polishing may reveal defects previously hidden by dirt, wax, or sealant buildup.",
        "The studio is not responsible for personal items left inside the vehicle.",
        "Maximum liability is limited to the cost of the detailing service provided.",
    ]:
        story.append(Paragraph(f"&bull;  {clause}", s["Body"]))

    section(story, "Customer Acknowledgement")
    for ack in [
        "I confirm I am the registered owner or authorised representative of the vehicle.",
        "I have disclosed all known damage and mechanical issues.",
        "I understand the nature of the services to be performed.",
        "I accept the terms and limitations described above.",
        "I authorise the studio to carry out the agreed detailing services.",
    ]:
        story.append(cb(ack))

    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>I have read, understood, and agree to the terms above.</b>", s["Body"]))
    story.append(Spacer(1, 4))
    story.append(field2("Customer Name (Print)", "Customer Signature"))
    story.append(field2("Date", "Vehicle Registration"))

    doc.build(story)
    return path


# ── Form 3: Service Agreement ─────────────────────────────────────────

def form_03_service_agreement():
    doc, path = make_doc("Service_Agreement.pdf", "Service Agreement")
    story = []
    page_header(story, "Service Agreement")
    s = S()

    section(story, "Services Included")
    story.append(Paragraph(
        "The following services have been agreed between the customer and the detailing studio:",
        s["Body"]
    ))
    for _ in range(4):
        story.append(Paragraph("_" * 85, s["Body"]))

    section(story, "Exclusions")
    story.append(Paragraph(
        "The following are NOT included unless explicitly agreed in writing:",
        s["Body"]
    ))
    for exc in [
        "Mechanical repairs or diagnostics",
        "Paint correction beyond agreed scope",
        "Removal of permanent stains, burns, or pet hair damage",
        "Headlight restoration (unless specified)",
    ]:
        story.append(Paragraph(f"&bull;  {exc}", s["Body"]))

    section(story, "Payment Terms")
    for term in [
        "Payment is due upon completion of services unless otherwise agreed.",
        "Accepted methods: Cash, Card, Bank Transfer.",
        "A deposit may be required for premium packages — see invoice for details.",
        "Late payment may incur additional charges at the studio's discretion.",
    ]:
        story.append(Paragraph(f"&bull;  {term}", s["Body"]))

    section(story, "Cancellation Policy")
    for cancel in [
        "Cancellations with 24+ hours notice: full refund of any deposit.",
        "Cancellations with less than 24 hours notice: deposit forfeited.",
        "No-shows: deposit forfeited and future bookings require full prepayment.",
    ]:
        story.append(Paragraph(f"&bull;  {cancel}", s["Body"]))

    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>Both parties agree to the terms set out in this agreement.</b>", s["Body"]))
    story.append(Spacer(1, 4))
    story.append(field2("Customer Signature", "Date"))
    story.append(field2("Studio Representative", "Date"))

    doc.build(story)
    return path


# ── Form 4: Invoice Template ─────────────────────────────────────────

def form_04_invoice():
    doc, path = make_doc("Invoice_Template.pdf", "Invoice")
    story = []
    page_header(story, "Invoice")
    s = S()

    story.append(field2("Invoice No", "Date"))
    story.append(Spacer(1, 3))

    section(story, "Business Details")
    story.append(field("Business Name"))
    story.append(field("Address"))
    story.append(field2("Phone", "Email"))

    section(story, "Customer Details")
    story.append(field("Customer Name"))
    story.append(field2("Phone / Email", "Vehicle Reg"))

    section(story, "Services")
    table_data = [["Description", "Qty", "Unit Price", "Amount"]]
    for _ in range(5):
        table_data.append(["", "", "", ""])
    t = Table(table_data, colWidths=[CONTENT_W * 0.48, CONTENT_W * 0.12, CONTENT_W * 0.20, CONTENT_W * 0.20])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), RED),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, RED),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_GRAY]),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t)

    totals = [
        ["", "", "Subtotal:", ""],
        ["", "", "VAT (20%):", ""],
        ["", "", "TOTAL DUE:", ""],
    ]
    tt = Table(totals, colWidths=[CONTENT_W * 0.48, CONTENT_W * 0.12, CONTENT_W * 0.20, CONTENT_W * 0.20])
    tt.setStyle(TableStyle([
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
        ("LINEABOVE", (2, -1), (-1, -1), 1.5, RED),
        ("TEXTCOLOR", (2, -1), (-1, -1), RED),
        ("FONTNAME", (2, -1), (-1, -1), "Helvetica-Bold"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(tt)

    story.append(Spacer(1, 6))
    section(story, "Payment Method")
    story.append(cb_row(["Cash", "Card", "Bank Transfer", "PayPal", "Other"], cols=5))
    story.append(Spacer(1, 4))
    story.append(field("Notes"))

    doc.build(story)
    return path


# ── Form 5: Customer Feedback Form ───────────────────────────────────

def form_05_feedback():
    doc, path = make_doc("Customer_Feedback_Form.pdf", "Customer Feedback Form")
    story = []
    page_header(story, "Customer Feedback Form")
    s = S()

    section(story, "Service Details")
    story.append(field2("Customer Name", "Date of Service"))
    story.append(field("Service Received"))
    story.append(field("Vehicle Make / Model"))

    section(story, "Overall Rating")
    story.append(Paragraph("Please rate your experience (circle one):", s["Body"]))
    stars = "     ".join([f"{'*' * i}  ({i})" for i in range(1, 6)])
    story.append(Paragraph(
        "<font size='11'>\u2606  1  &nbsp;&nbsp;  \u2606\u2606  2  &nbsp;&nbsp;  "
        "\u2606\u2606\u2606  3  &nbsp;&nbsp;  \u2606\u2606\u2606\u2606  4  &nbsp;&nbsp;  "
        "\u2606\u2606\u2606\u2606\u2606  5</font>",
        s["Body"]
    ))

    section(story, "Feedback")
    text_area(story, "What did we do well?", lines=4)
    story.append(Spacer(1, 4))
    text_area(story, "What could we improve?", lines=4)

    section(story, "Recommendation")
    story.append(Paragraph("Would you recommend us to a friend or colleague?", s["Body"]))
    story.append(cb_row(["Definitely", "Probably", "Not sure", "Unlikely"], cols=4))

    story.append(Spacer(1, 4))
    story.append(field("Email (for follow-up, optional)"))

    story.append(Spacer(1, 6))
    story.append(Paragraph("<i>Thank you for your feedback. It helps us improve our service.</i>", s["BodySmall"]))

    doc.build(story)
    return path


# ── Form 6: Appointment Booking Form ─────────────────────────────────

def form_06_appointment():
    doc, path = make_doc("Appointment_Booking_Form.pdf", "Appointment Booking Form")
    story = []
    page_header(story, "Appointment Booking Form")

    section(story, "Customer Details")
    story.append(field("Customer Name"))
    story.append(field2("Phone", "Email"))

    section(story, "Vehicle Details")
    story.append(field2("Make / Model", "Year"))
    story.append(field2("Registration", "Colour"))

    section(story, "Appointment Details")
    story.append(field2("Preferred Date", "Preferred Time"))
    story.append(field("Alternative Date / Time"))

    section(story, "Service Type")
    story.append(cb_row([
        "Exterior Wash", "Full Exterior Detail",
        "Interior Valet", "Full Interior Detail",
        "Machine Polish", "Ceramic Coating",
        "Bronze Package", "Silver Package", "Gold Package",
    ], cols=3))

    section(story, "How Did You Hear About Us?")
    story.append(cb_row([
        "Google", "Instagram", "Facebook",
        "Referral", "Drive-by", "Other"
    ], cols=3))

    story.append(Spacer(1, 4))
    story.append(field("Special Requests"))

    story.append(Spacer(1, 8))
    sig_block(story)

    doc.build(story)
    return path


# ── Form 7: Aftercare Instructions ───────────────────────────────────

def form_07_aftercare():
    doc, path = make_doc("Aftercare_Instructions.pdf", "Aftercare Instructions")
    story = []
    page_header(story, "Aftercare Instructions")
    s = S()

    story.append(Paragraph(
        "<i>Follow these guidelines to maintain your vehicle's finish and protect your investment.</i>",
        s["Body"]
    ))

    section(story, "First 24 Hours")
    for t in [
        "Do NOT wash or rinse the vehicle for at least 24 hours after detailing.",
        "Avoid parking under trees or near construction sites.",
        "If wax or sealant was applied, allow 24 hours to fully cure.",
        "Do not use automated car washes for at least 2 weeks.",
    ]:
        story.append(Paragraph(f"&bull;  {t}", s["Body"]))

    section(story, "Wax & Sealant Care")
    for t in [
        "Use pH-neutral car shampoo only — avoid dish soap or harsh detergents.",
        "Wash using the two-bucket method to prevent swirl marks.",
        "Dry with a clean microfibre drying towel — never air dry.",
        "Reapply wax or sealant every 2-3 months for lasting protection.",
        "Use a spray detailer between washes to maintain gloss and hydrophobic properties.",
    ]:
        story.append(Paragraph(f"&bull;  {t}", s["Body"]))

    section(story, "Interior Maintenance")
    for t in [
        "Vacuum regularly to prevent dirt buildup in carpets and seats.",
        "Wipe leather surfaces with a dedicated leather conditioner monthly.",
        "Use UV protectant on dashboard and trim to prevent fading and cracking.",
        "Avoid eating or drinking in the vehicle where possible.",
        "Clean spills immediately to prevent staining.",
    ]:
        story.append(Paragraph(f"&bull;  {t}", s["Body"]))

    section(story, "Product Recommendations")
    story.append(Paragraph(
        "Ask your detailer for recommended products suited to your vehicle's finish. "
        "Using the wrong products can damage paint protection or interior surfaces.",
        s["Body"]
    ))

    story.append(Spacer(1, 8))
    story.append(red_divider())
    story.append(field2("Your Detailer", "Date"))
    story.append(field2("Studio Phone", "Studio Email"))

    doc.build(story)
    return path


# ── Form 8: Detailing Package Menu ───────────────────────────────────

def form_08_package_menu():
    doc, path = make_doc("Detailing_Package_Menu.pdf", "Detailing Package Menu")
    story = []
    page_header(story, "Detailing Package Menu")
    s = S()

    packages = [
        {
            "name": "BRONZE PACKAGE",
            "time": "Approx. 1-2 hours",
            "items": [
                ("Exterior hand wash & dry", ""),
                ("Wheel & tyre clean", ""),
                ("Tyre shine applied", ""),
                ("Window clean (exterior)", ""),
            ],
            "price": "\u00a3___",
        },
        {
            "name": "SILVER PACKAGE",
            "time": "Approx. 2-3 hours",
            "items": [
                ("Everything in Bronze, plus:", ""),
                ("Full interior vacuum", ""),
                ("Dashboard & trim wipe down", ""),
                ("Interior window clean", ""),
                ("Air freshener", ""),
            ],
            "price": "\u00a3___",
        },
        {
            "name": "GOLD PACKAGE",
            "time": "Approx. 4-6 hours",
            "items": [
                ("Everything in Silver, plus:", ""),
                ("Machine polish (single stage)", ""),
                ("Wax / sealant application", ""),
                ("Full interior detail & shampoo", ""),
                ("Leather clean & condition", ""),
                ("Engine bay clean", ""),
            ],
            "price": "\u00a3___",
        },
    ]

    for pkg in packages:
        section(story, pkg["name"])
        story.append(Paragraph(f"<i>{pkg['time']}</i>", s["BodySmall"]))
        story.append(Spacer(1, 2))

        for item, _ in pkg["items"]:
            story.append(Paragraph(f"\u2713  {item}", s["Body"]))

        story.append(Spacer(1, 2))
        story.append(Paragraph(
            f"<b>Price: {pkg['price']}</b>",
            ParagraphStyle("PkgPrice", parent=s["Body"], fontSize=12, textColor=RED)
        ))
        story.append(Spacer(1, 4))

    story.append(red_divider())
    story.append(Paragraph(
        "<i>Prices may vary depending on vehicle size and condition. "
        "Contact us for a personalised quote.</i>",
        s["BodySmall"]
    ))
    story.append(Spacer(1, 4))
    story.append(field2("Studio Phone", "Studio Email"))

    doc.build(story)
    return path


# ── Main ──────────────────────────────────────────────────────────────

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    generators = [
        form_01_vehicle_intake,
        form_02_consent,
        form_03_service_agreement,
        form_04_invoice,
        form_05_feedback,
        form_06_appointment,
        form_07_aftercare,
        form_08_package_menu,
    ]
    paths = []
    for gen in generators:
        p = gen()
        paths.append(p)
        print(f"  Created: {os.path.basename(p)}")
    print(f"\nAll {len(paths)} forms generated in {OUTPUT_DIR}")
    return paths


if __name__ == "__main__":
    main()
