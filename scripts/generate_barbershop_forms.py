#!/usr/bin/env python3
"""Generate 8 barbershop client forms as single-page A4 PDFs.
Adapted from tattoo studio forms with barbershop-specific terminology.
Palette: #F5F5F5 bg, #1A1A1A headers, #C9A96E gold dividers.
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

OUTPUT_DIR = "/root/NEW-AI-PROJECT/outputs/barbershop-forms"

DARK = HexColor("#1A1A1A")
GOLD = HexColor("#C9A96E")
LIGHT_GRAY = HexColor("#F5F5F5")
DARK_GRAY = HexColor("#333333")
MID_GRAY = HexColor("#999999")

WIDTH, HEIGHT = A4
MARGIN = 18 * mm
CONTENT_W = WIDTH - 2 * MARGIN
CBX = "\u25a1"


def get_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        "FormTitle", parent=styles["Title"],
        fontName="Helvetica-Bold", fontSize=20,
        textColor=DARK, spaceAfter=2, spaceBefore=0, alignment=TA_CENTER
    ))
    styles.add(ParagraphStyle(
        "StudioName", parent=styles["Normal"],
        fontName="Helvetica", fontSize=9,
        textColor=GOLD, alignment=TA_CENTER, spaceAfter=1, spaceBefore=0
    ))
    styles.add(ParagraphStyle(
        "SectionHead", parent=styles["Heading2"],
        fontName="Helvetica-Bold", fontSize=12,
        textColor=DARK, spaceBefore=10, spaceAfter=3
    ))
    styles.add(ParagraphStyle(
        "Body", parent=styles["Normal"],
        fontName="Helvetica", fontSize=10,
        textColor=DARK_GRAY, leading=13, spaceAfter=3
    ))
    styles.add(ParagraphStyle(
        "BodySmall", parent=styles["Normal"],
        fontName="Helvetica", fontSize=8,
        textColor=DARK_GRAY, leading=10, spaceAfter=2
    ))
    styles.add(ParagraphStyle(
        "Footer", parent=styles["Normal"],
        fontName="Helvetica", fontSize=7,
        textColor=GOLD, alignment=TA_CENTER
    ))
    return styles


_cached_styles = None


def S():
    global _cached_styles
    if _cached_styles is None:
        _cached_styles = get_styles()
    return _cached_styles


def gold_divider():
    return HRFlowable(width="100%", thickness=1.2, color=GOLD, spaceAfter=6, spaceBefore=2)


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
    story.append(Paragraph("YOUR BARBERSHOP NAME", s["StudioName"]))
    story.append(Paragraph(title, s["FormTitle"]))
    story.append(gold_divider())


def section(story, title):
    story.append(Paragraph(title, S()["SectionHead"]))
    story.append(gold_divider())


def make_doc(filename, title):
    filepath = os.path.join(OUTPUT_DIR, filename)
    doc = SimpleDocTemplate(
        filepath, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=14 * mm,
        title=title, author="PurpleOcaz Barbershop Templates"
    )
    return doc, filepath


def sig_block(story):
    story.append(field2("Client Signature", "Date"))


# ── Form 1: Client Consent Form ──

def form_01_consent():
    doc, path = make_doc("01_Client_Consent_Form.pdf", "Client Consent Form")
    story = []
    page_header(story, "Client Consent Form")

    section(story, "Client Information")
    story.append(field2("Full Name", "Date of Birth"))
    story.append(field("Address"))
    story.append(field2("Phone", "Email"))
    story.append(field("Emergency Contact Name & Phone"))

    section(story, "Scalp & Skin Check")
    story.append(Paragraph("Do you have or have you ever had any of the following?", S()["Body"]))
    story.append(cb_row([
        "Scalp conditions (psoriasis, eczema, ringworm)", "Allergies (hair products, dyes, latex)",
        "Sensitive skin / contact dermatitis", "Open cuts, sores, or infections on scalp",
        "Blood-borne diseases (Hepatitis, HIV)", "Lice or fungal infections (current or recent)",
        "Alopecia / hair loss treatment", "Skin condition requiring medication",
    ], cols=2))
    story.append(field("If yes to any, provide details"))
    story.append(field("Current medications"))

    section(story, "Consent Declaration")
    for clause in [
        "I confirm I am at least 16 years of age (or have parental consent).",
        "I confirm the above health information is accurate and complete.",
        "I understand barbering involves sharp tools and chemical products with associated risks.",
        "I have informed the barber of any allergies or sensitivities.",
        "I consent to the service and accept all associated risks.",
        "I understand results may vary and I have discussed my expectations with the barber.",
        "I consent to standard hygiene practices. All tools are sterilised between clients.",
    ]:
        story.append(cb(clause))

    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>I have read, understood, and agree to the terms above.</b>", S()["Body"]))
    story.append(Spacer(1, 4))
    story.append(field2("Client Signature", "Date"))
    story.append(field2("Barber Name", "Barber Signature"))

    doc.build(story)
    return path


# ── Form 2: Client Intake Form ──

def form_02_intake():
    doc, path = make_doc("02_Client_Intake_Form.pdf", "Client Intake Form")
    story = []
    page_header(story, "Client Intake Form")

    section(story, "Personal Details")
    story.append(field2("Full Name", "Date of Birth"))
    story.append(field2("Phone", "Email"))
    story.append(field("Address"))
    story.append(field2("Emergency Contact", "Emergency Phone"))

    section(story, "Service Details")
    story.append(field("Service Requested (cut, fade, beard trim, shave, etc.)"))
    story.append(field("Preferred Style / Reference"))
    story.append(field2("Hair Type / Texture", "Preferred Length"))
    story.append(field("Previous Styles / Notes"))

    section(story, "Previous Experience")
    story.append(cb_row(["First visit to this barbershop", "Regular client"], cols=2))
    story.append(field("Any adverse reactions to previous cuts, dyes, or products"))

    section(story, "Scalp & Skin Sensitivity")
    story.append(cb_row([
        "Sensitive scalp", "Dandruff / flaking",
        "Eczema / Psoriasis", "Allergies (products, fragrances, latex)",
    ], cols=2))

    section(story, "How Did You Hear About Us?")
    story.append(cb_row(["Instagram", "Facebook", "Google", "Walk-in", "Referral", "Other"], cols=3))

    story.append(Spacer(1, 8))
    story.append(Paragraph("I confirm the information above is accurate and complete.", S()["Body"]))
    story.append(Spacer(1, 4))
    sig_block(story)

    doc.build(story)
    return path


# ── Form 3: Aftercare Instructions ──

def form_03_aftercare():
    doc, path = make_doc("03_Aftercare_Instructions.pdf", "Aftercare Instructions")
    story = []
    page_header(story, "Aftercare Instructions")
    s = S()

    story.append(Paragraph(
        "<i>Following these steps will keep your cut looking sharp and your scalp healthy between visits.</i>",
        s["Body"]
    ))

    section(story, "First 24 Hours")
    for t in [
        "Avoid touching or rubbing the freshly cut area with unwashed hands.",
        "If a razor was used, avoid applying cologne or alcohol-based products to shaved areas.",
        "Keep the area clean and dry for the first few hours.",
        "Apply a gentle aftershave balm or moisturiser if the skin feels irritated.",
        "Avoid swimming pools, saunas, or steam rooms for 24 hours after a close shave.",
    ]:
        story.append(Paragraph(f"&bull;  {t}", s["Body"]))

    section(story, "Days 2-7: Maintaining Your Cut")
    for t in [
        "Wash hair with a gentle, sulphate-free shampoo.",
        "Apply styling products sparingly — less is more for a clean look.",
        "Brush or comb in the direction of growth to train the hair.",
        "Use a moisturiser or beard oil for facial hair maintenance.",
        "Sleep on a satin pillowcase to reduce friction (curly/textured hair).",
    ]:
        story.append(Paragraph(f"&bull;  {t}", s["Body"]))

    section(story, "What to Avoid")
    for t in [
        "Scratching or picking at razor bumps — this causes scarring.",
        "Over-washing the scalp, which strips natural oils.",
        "Using harsh chemical products on freshly cut or shaved skin.",
        "Exposing a fresh shave to direct sunlight without SPF protection.",
    ]:
        story.append(Paragraph(f"<font color='#1A1A1A'>&times;</font>  {t}", s["Body"]))

    section(story, "Ongoing Maintenance")
    for t in [
        "Schedule your next appointment every 2-4 weeks to maintain shape.",
        "Use SPF on exposed scalp areas (especially fades and shaved heads).",
        "Keep beard and neckline tidy between appointments with a trimmer.",
    ]:
        story.append(Paragraph(f"&bull;  {t}", s["Body"]))

    section(story, "Warning Signs — Contact Us If:")
    for t in [
        "Persistent redness, swelling, or warmth beyond 48 hours",
        "Signs of infection (pus, spreading redness, heat)",
        "Severe razor bumps that worsen or become painful",
        "Allergic reaction to any product used during the service",
    ]:
        story.append(Paragraph(f"<font color='#1A1A1A'><b>!</b></font>  {t}", s["Body"]))

    story.append(Spacer(1, 8))
    story.append(gold_divider())
    story.append(field2("Your Barber", "Date"))
    story.append(field2("Barbershop Phone", "Barbershop Email"))

    doc.build(story)
    return path


# ── Form 4: Invoice ──

def form_04_invoice():
    doc, path = make_doc("04_Invoice.pdf", "Invoice")
    story = []
    page_header(story, "Invoice")
    s = S()

    story.append(field2("Invoice No", "Date"))
    story.append(Spacer(1, 3))

    section(story, "Barbershop Details")
    story.append(field("Barbershop Name"))
    story.append(field("Address"))
    story.append(field2("Phone", "Email"))

    section(story, "Client Details")
    story.append(field("Client Name"))
    story.append(field2("Phone / Email", "Address"))

    section(story, "Services Rendered")
    table_data = [["Description", "Qty", "Rate", "Amount"]]
    for _ in range(5):
        table_data.append(["", "", "", ""])
    t = Table(table_data, colWidths=[CONTENT_W * 0.48, CONTENT_W * 0.14, CONTENT_W * 0.19, CONTENT_W * 0.19])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, GOLD),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_GRAY]),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t)

    totals = [
        ["", "", "Subtotal:", ""],
        ["", "", "Products:", ""],
        ["", "", "Tax:", ""],
        ["", "", "TOTAL DUE:", ""],
    ]
    tt = Table(totals, colWidths=[CONTENT_W * 0.48, CONTENT_W * 0.14, CONTENT_W * 0.19, CONTENT_W * 0.19])
    tt.setStyle(TableStyle([
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
        ("LINEABOVE", (2, -1), (-1, -1), 1.5, DARK),
        ("TEXTCOLOR", (2, -1), (-1, -1), DARK),
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
    story.append(Paragraph("Payment is due upon completion of the service unless otherwise agreed.", s["BodySmall"]))

    doc.build(story)
    return path


# ── Form 5: Appointment Tracker ──

def form_05_appointment_tracker():
    doc, path = make_doc("05_Appointment_Tracker.pdf", "Appointment Tracker")
    story = []
    page_header(story, "Appointment Tracker")

    section(story, "Client Details")
    story.append(field2("Client Name", "Phone / Email"))
    story.append(field("Preferred Style / Usual Service"))
    story.append(field2("Preferred Barber", "Frequency"))

    section(story, "Appointment Log")
    headers = ["#", "Date", "Service", "Barber", "Amount", "Paid"]
    data = [headers]
    for i in range(1, 11):
        data.append([str(i), "", "", "", "", ""])

    st = Table(data, colWidths=[CONTENT_W * 0.06, CONTENT_W * 0.14, CONTENT_W * 0.26,
                                CONTENT_W * 0.22, CONTENT_W * 0.14, CONTENT_W * 0.18])
    st.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, GOLD),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_GRAY]),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(st)

    story.append(Spacer(1, 6))
    section(story, "Notes")
    for _ in range(2):
        story.append(Paragraph("_" * 85, S()["Body"]))

    doc.build(story)
    return path


# ── Form 6: Photo Release Form ──

def form_06_photo_release():
    doc, path = make_doc("06_Photo_Release.pdf", "Photo Release Form")
    story = []
    page_header(story, "Photo Release Form")
    s = S()

    section(story, "Client Information")
    story.append(field2("Full Name", "Date"))
    story.append(field2("Phone", "Email"))

    section(story, "Consent for Photography & Media Use")
    story.append(Paragraph(
        "I hereby grant the barbershop, its barbers, and representatives the right to photograph, film, "
        "or otherwise capture images of my haircut, styling, or grooming service.",
        s["Body"]
    ))
    story.append(Spacer(1, 3))
    story.append(Paragraph("These images may be used for:", s["Body"]))
    for use in [
        "Portfolio display (physical and digital) for barber and shop promotion",
        "Social media platforms (Instagram, TikTok, Facebook, Pinterest, etc.)",
        "Barbershop website, marketing materials, and print media",
        "Industry publications, competitions, and exhibitions",
        "Educational and training materials",
    ]:
        story.append(Paragraph(f"&bull;  {use}", s["Body"]))

    section(story, "Terms")
    for i, term in enumerate([
        "No identifying personal information will be shared alongside images without explicit written consent.",
        "I waive any right to inspect or approve the finished images or the context in which they are used.",
        "I release the barbershop from any claims arising from the use of these images.",
        "This consent is valid indefinitely unless revoked in writing.",
    ], 1):
        story.append(Paragraph(f"<b>{i}.</b>  {term}", s["Body"]))

    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Please select one:</b>", s["Body"]))
    story.append(cb("I CONSENT to the use of photographs/video as described above."))
    story.append(cb("I DO NOT CONSENT to the use of photographs/video."))

    story.append(Spacer(1, 10))
    story.append(field2("Client Name (Print)", "Client Signature"))
    story.append(field2("Date", "Barber Name"))
    story.append(field("Witness (if applicable)"))

    doc.build(story)
    return path


# ── Form 7: Cancellation & Deposit Policy ──

def form_07_cancellation():
    doc, path = make_doc("07_Cancellation_Policy.pdf", "Cancellation & Deposit Policy")
    story = []
    page_header(story, "Cancellation & Deposit Policy")
    s = S()

    section(story, "Deposit Policy")
    for d in [
        "A deposit may be required to secure premium appointments (e.g. bridal, event grooming).",
        "Standard deposit: a minimum of \u00a310 or as agreed at booking.",
        "The deposit is deducted from the final cost on the day of your appointment.",
        "Deposits are non-transferable but may be applied to a rescheduled appointment (see below).",
    ]:
        story.append(Paragraph(f"&bull;  {d}", s["Body"]))

    section(story, "Cancellation Policy")
    cancel_data = [
        ["Notice Period", "Consequence"],
        ["More than 24 hours", "Deposit transferred to new date (one time only)"],
        ["12-24 hours", "50% of deposit forfeited; remainder applied to new booking"],
        ["Less than 12 hours", "Full deposit forfeited"],
        ["No-show", "Full deposit forfeited; future bookings require deposit upfront"],
    ]
    ct = Table(cancel_data, colWidths=[CONTENT_W * 0.30, CONTENT_W * 0.70])
    ct.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("GRID", (0, 0), (-1, -1), 0.5, GOLD),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_GRAY]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(ct)

    section(story, "Rescheduling")
    for r in [
        "You may reschedule once at no additional cost with more than 24 hours' notice.",
        "A second reschedule will be treated as a cancellation under the policy above.",
        "Rescheduled appointments must be booked within 30 days of the original date.",
    ]:
        story.append(Paragraph(f"&bull;  {r}", s["Body"]))

    section(story, "Late Arrivals")
    story.append(Paragraph(
        "Arrivals more than 10 minutes late may result in a shortened service or reschedule. "
        "Arrivals more than 20 minutes late will be treated as a no-show.",
        s["Body"]
    ))

    section(story, "Barbershop Cancellations")
    story.append(Paragraph(
        "If the barbershop cancels or reschedules, your deposit will be fully refunded or transferred "
        "to a new date of your choice. We will provide as much notice as possible.",
        s["Body"]
    ))

    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>I have read and agree to the Cancellation &amp; Deposit Policy.</b>", S()["Body"]))
    story.append(Spacer(1, 4))
    story.append(field2("Client Name (Print)", "Client Signature"))
    story.append(field2("Date", "Deposit Amount Paid"))

    doc.build(story)
    return path


# ── Form 8: Style Request Form ──

def form_08_style_request():
    doc, path = make_doc("08_Style_Request_Form.pdf", "Style Request Form")
    story = []
    page_header(story, "Style Request Form")
    s = S()

    section(story, "Client Information")
    story.append(field2("Full Name", "Date"))
    story.append(field2("Phone", "Email"))
    story.append(field("Preferred Barber"))

    section(story, "Style Brief")
    story.append(Paragraph("<b>Describe the look you want:</b>", s["Body"]))
    for _ in range(3):
        story.append(Paragraph("_" * 85, s["Body"]))

    section(story, "Cut & Style Preferences")
    story.append(cb_row([
        "Skin Fade", "Low Fade", "Mid Fade", "High Fade",
        "Taper", "Buzz Cut", "Crew Cut", "Side Part",
        "Textured Crop", "Pompadour", "Beard Trim", "Other",
    ], cols=4))

    section(story, "Details")
    story.append(field("Top Length Preference"))
    story.append(field2("Sides / Back (guard #)", "Beard Style"))
    story.append(field("Product Preferences (matte, gloss, none)"))

    section(story, "Reference Images")
    story.append(Paragraph("Attach or show reference images, screenshots, or inspiration below:", s["Body"]))
    ref_row = []
    for i in range(1, 4):
        ref_row.append(Paragraph(
            f"<br/><br/><br/><font color='#999999' size='8'>Reference {i}</font>",
            ParagraphStyle(f"ref{i}", alignment=TA_CENTER, fontSize=8, textColor=MID_GRAY)
        ))
    ref_table = Table([ref_row], colWidths=[CONTENT_W / 3] * 3, rowHeights=[65])
    ref_table.setStyle(TableStyle([
        ("BOX", (0, 0), (0, 0), 0.8, GOLD),
        ("BOX", (1, 0), (1, 0), 0.8, GOLD),
        ("BOX", (2, 0), (2, 0), 0.8, GOLD),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    story.append(ref_table)

    section(story, "Additional Notes")
    for _ in range(2):
        story.append(Paragraph("_" * 85, s["Body"]))

    story.append(Spacer(1, 6))
    sig_block(story)

    doc.build(story)
    return path


# ── Main ──

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    generators = [
        form_01_consent,
        form_02_intake,
        form_03_aftercare,
        form_04_invoice,
        form_05_appointment_tracker,
        form_06_photo_release,
        form_07_cancellation,
        form_08_style_request,
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
