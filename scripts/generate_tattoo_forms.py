#!/usr/bin/env python3
"""Generate 8 professional tattoo studio client forms as PDFs."""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.units import mm, inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs", "tattoo-forms")

OXBLOOD = HexColor("#8B1A1A")
GOLD = HexColor("#C9A96E")
LIGHT_GRAY = HexColor("#F5F5F5")
DARK_GRAY = HexColor("#333333")

WIDTH, HEIGHT = A4


def get_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        "FormTitle", parent=styles["Title"],
        fontName="Helvetica-Bold", fontSize=22,
        textColor=OXBLOOD, spaceAfter=4, alignment=TA_CENTER
    ))
    styles.add(ParagraphStyle(
        "StudioName", parent=styles["Normal"],
        fontName="Helvetica", fontSize=10,
        textColor=GOLD, alignment=TA_CENTER, spaceAfter=2
    ))
    styles.add(ParagraphStyle(
        "SectionHead", parent=styles["Heading2"],
        fontName="Helvetica-Bold", fontSize=13,
        textColor=OXBLOOD, spaceBefore=14, spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        "BodyText2", parent=styles["Normal"],
        fontName="Helvetica", fontSize=10,
        textColor=DARK_GRAY, leading=14, spaceAfter=4
    ))
    styles.add(ParagraphStyle(
        "SmallText", parent=styles["Normal"],
        fontName="Helvetica", fontSize=8,
        textColor=DARK_GRAY, leading=10, spaceAfter=2
    ))
    styles.add(ParagraphStyle(
        "FieldLabel", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=9,
        textColor=DARK_GRAY, spaceAfter=2
    ))
    styles.add(ParagraphStyle(
        "Footer", parent=styles["Normal"],
        fontName="Helvetica", fontSize=7,
        textColor=GOLD, alignment=TA_CENTER
    ))
    return styles


def gold_divider():
    return HRFlowable(width="100%", thickness=1.5, color=GOLD, spaceAfter=10, spaceBefore=4)


def field_line(label, width_pct="100%"):
    """A labeled blank line for form fill-in."""
    return Paragraph(
        f"<b>{label}:</b> _______________________________________________",
        get_styles()["BodyText2"]
    )


def checkbox(text, styles):
    return Paragraph(f"&#9744;  {text}", styles["BodyText2"])


def build_header(story, title, styles):
    story.append(Paragraph("INK & SOUL TATTOO STUDIO", styles["StudioName"]))
    story.append(Paragraph(title, styles["FormTitle"]))
    story.append(gold_divider())


def make_doc(filename, title):
    filepath = os.path.join(OUTPUT_DIR, filename)
    doc = SimpleDocTemplate(
        filepath, pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=18*mm, bottomMargin=18*mm,
        title=title, author="Ink & Soul Tattoo Studio"
    )
    return doc, filepath


# ── Form 1: Client Intake ──────────────────────────────────────────

def form_01_client_intake():
    styles = get_styles()
    doc, path = make_doc("01-client-intake-form.pdf", "Client Intake Form")
    story = []
    build_header(story, "Client Intake Form", styles)

    story.append(Paragraph("Personal Information", styles["SectionHead"]))
    story.append(gold_divider())
    for label in ["Full Name", "Date of Birth", "Phone Number", "Email Address",
                  "Emergency Contact Name", "Emergency Contact Phone", "Address"]:
        story.append(field_line(label))
        story.append(Spacer(1, 6))

    story.append(Paragraph("Medical History", styles["SectionHead"]))
    story.append(gold_divider())
    story.append(Paragraph("Please check all that apply:", styles["BodyText2"]))
    conditions = [
        "Heart condition or pacemaker", "Diabetes (Type 1 or Type 2)",
        "Hemophilia or blood clotting disorder", "Epilepsy or seizure disorder",
        "Skin conditions (eczema, psoriasis, keloids)", "HIV / Hepatitis",
        "Currently pregnant or nursing", "Immune system disorder",
        "Allergies to latex, adhesives, or metals", "Currently taking blood thinners"
    ]
    for c in conditions:
        story.append(checkbox(c, styles))

    story.append(Spacer(1, 6))
    story.append(field_line("Other medical conditions or allergies"))
    story.append(Spacer(1, 6))
    story.append(field_line("Current medications"))

    story.append(Paragraph("Tattoo Details", styles["SectionHead"]))
    story.append(gold_divider())
    for label in ["Desired tattoo description", "Placement / body location",
                  "Approximate size (inches/cm)", "Preferred style (e.g., realism, traditional, blackwork)",
                  "Reference images provided"]:
        story.append(field_line(label))
        story.append(Spacer(1, 6))

    story.append(checkbox("First tattoo", styles))
    story.append(checkbox("Have existing tattoos", styles))

    story.append(Spacer(1, 14))
    story.append(Paragraph("I confirm that the information provided above is accurate and complete.", styles["BodyText2"]))
    story.append(Spacer(1, 10))
    story.append(field_line("Client Signature"))
    story.append(Spacer(1, 6))
    story.append(field_line("Date"))

    doc.build(story)
    return path


# ── Form 2: Consent Waiver ─────────────────────────────────────────

def form_02_consent_waiver():
    styles = get_styles()
    doc, path = make_doc("02-consent-waiver.pdf", "Consent & Waiver Form")
    story = []
    build_header(story, "Consent & Waiver Form", styles)

    story.append(Paragraph("Acknowledgement of Risks", styles["SectionHead"]))
    story.append(gold_divider())

    clauses = [
        "I acknowledge that tattooing involves piercing the skin with needles and depositing ink beneath the surface. I understand this process carries inherent risks including, but not limited to, infection, allergic reaction, scarring, and keloid formation.",
        "I confirm that I am at least 18 years of age and am not under the influence of alcohol or drugs. I have disclosed all relevant medical conditions, allergies, and medications on my intake form.",
        "I understand that variations in colour, size, and exact placement may occur due to the nature of the tattooing process. Minor adjustments may be made by the artist to ensure the best possible result.",
        "I understand that the final outcome depends on proper aftercare. I have received and agree to follow all aftercare instructions provided by the studio.",
        "I release Ink & Soul Tattoo Studio, its owners, artists, and employees from any and all liability, claims, or damages arising from the tattoo procedure, including but not limited to infection, allergic reaction, scarring, or dissatisfaction with the final result.",
        "I consent to the use of standard sterilisation and hygiene practices employed by the studio. I understand that all needles and inks used are single-use or properly sterilised.",
        "I acknowledge that tattoos are permanent. Touch-up sessions, if needed, are subject to the studio's touch-up policy."
    ]
    for i, clause in enumerate(clauses, 1):
        story.append(Paragraph(f"<b>{i}.</b> {clause}", styles["BodyText2"]))
        story.append(Spacer(1, 4))

    story.append(Paragraph("Assumption of Risk", styles["SectionHead"]))
    story.append(gold_divider())
    story.append(Paragraph(
        "I voluntarily assume full responsibility for any risks, injuries, or damages that may occur "
        "before, during, or after the tattoo procedure. I agree to hold harmless and indemnify Ink & Soul "
        "Tattoo Studio against any claims, suits, or actions of any kind.",
        styles["BodyText2"]
    ))

    story.append(Spacer(1, 14))
    story.append(Paragraph("I have read, understood, and agree to the terms above.", styles["BodyText2"]))
    story.append(Spacer(1, 10))
    for label in ["Client Full Name (Print)", "Client Signature", "Date",
                  "Artist Name", "Artist Signature", "Witness (if applicable)"]:
        story.append(field_line(label))
        story.append(Spacer(1, 6))

    doc.build(story)
    return path


# ── Form 3: Aftercare Instructions ─────────────────────────────────

def form_03_aftercare():
    styles = get_styles()
    doc, path = make_doc("03-aftercare-instructions.pdf", "Aftercare Instructions")
    story = []
    build_header(story, "Aftercare Instructions", styles)

    story.append(Paragraph("Your tattoo is an open wound. Proper aftercare is essential for healing and preserving the quality of your ink.", styles["BodyText2"]))
    story.append(Spacer(1, 6))

    story.append(Paragraph("First 24 Hours", styles["SectionHead"]))
    story.append(gold_divider())
    steps_24 = [
        "Leave the bandage/wrap on for 2-4 hours after your session (or as directed by your artist).",
        "Wash your hands thoroughly before touching the tattoo.",
        "Gently remove the bandage and wash the tattoo with lukewarm water and a mild, fragrance-free antibacterial soap.",
        "Pat dry with a clean paper towel — never use a cloth towel.",
        "Apply a thin layer of the recommended aftercare ointment (e.g., Hustle Butter, Aquaphor, or coconut oil).",
        "Do NOT re-bandage unless instructed by your artist."
    ]
    for s in steps_24:
        story.append(Paragraph(f"&bull;  {s}", styles["BodyText2"]))

    story.append(Paragraph("Days 2-14: Healing Phase", styles["SectionHead"]))
    story.append(gold_divider())
    steps_heal = [
        "Wash the tattoo 2-3 times daily with mild soap and lukewarm water.",
        "Apply a thin layer of fragrance-free moisturiser after each wash.",
        "Your tattoo will begin to peel and flake — this is normal. Do NOT pick or scratch.",
        "Wear loose, breathable clothing over the tattooed area.",
        "Avoid sleeping directly on the tattoo when possible."
    ]
    for s in steps_heal:
        story.append(Paragraph(f"&bull;  {s}", styles["BodyText2"]))

    story.append(Paragraph("What to Avoid", styles["SectionHead"]))
    story.append(gold_divider())
    avoids = [
        "Submerging the tattoo in water (baths, pools, hot tubs, sea) for at least 2-3 weeks.",
        "Direct sunlight or tanning beds during the healing period.",
        "Gym workouts or heavy sweating for 48-72 hours.",
        "Tight or abrasive clothing over the tattoo.",
        "Applying alcohol-based products, hydrogen peroxide, or Vaseline to the tattoo."
    ]
    for a in avoids:
        story.append(Paragraph(f"&bull;  {a}", styles["BodyText2"]))

    story.append(Paragraph("Long-Term Care", styles["SectionHead"]))
    story.append(gold_divider())
    longterm = [
        "Always apply SPF 30+ sunscreen to healed tattoos when exposed to sunlight.",
        "Keep the skin moisturised to maintain vibrancy.",
        "Full healing takes 4-6 weeks. Deeper layers continue healing for up to 3 months."
    ]
    for l in longterm:
        story.append(Paragraph(f"&bull;  {l}", styles["BodyText2"]))

    story.append(Paragraph("When to Contact Us", styles["SectionHead"]))
    story.append(gold_divider())
    story.append(Paragraph(
        "If you experience excessive redness, swelling, pus, prolonged pain, or signs of allergic reaction "
        "(severe itching, raised bumps, blistering), contact us immediately or seek medical attention.",
        styles["BodyText2"]
    ))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Studio: info@inkandsoul.com  |  Phone: (555) 123-4567", styles["SmallText"]))

    doc.build(story)
    return path


# ── Form 4: Photo Release ──────────────────────────────────────────

def form_04_photo_release():
    styles = get_styles()
    doc, path = make_doc("04-photo-release.pdf", "Photo Release Form")
    story = []
    build_header(story, "Photo Release Form", styles)

    story.append(Paragraph("Consent for Photography & Media Use", styles["SectionHead"]))
    story.append(gold_divider())

    story.append(Paragraph(
        "I hereby grant Ink & Soul Tattoo Studio, its artists, and representatives the right and permission "
        "to photograph, film, or otherwise capture images of my tattoo(s) and the tattooing process.",
        styles["BodyText2"]
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "I understand that these images may be used for the following purposes:",
        styles["BodyText2"]
    ))

    uses = [
        "Portfolio display (physical and digital) for artist and studio promotion",
        "Social media platforms (Instagram, TikTok, Facebook, Pinterest, etc.)",
        "Studio website and marketing materials",
        "Print media, including brochures, flyers, and business cards",
        "Tattoo conventions, exhibitions, and industry publications",
        "Educational and training materials"
    ]
    for u in uses:
        story.append(Paragraph(f"&bull;  {u}", styles["BodyText2"]))

    story.append(Spacer(1, 6))
    story.append(Paragraph("Terms", styles["SectionHead"]))
    story.append(gold_divider())
    terms = [
        "I understand that no identifying personal information (full name, address, etc.) will be shared alongside images without my explicit written consent.",
        "I waive any right to inspect or approve the finished images or the context in which they are used.",
        "I release Ink & Soul Tattoo Studio from any claims arising from the use of these images.",
        "This consent is valid indefinitely unless revoked in writing."
    ]
    for i, t in enumerate(terms, 1):
        story.append(Paragraph(f"<b>{i}.</b> {t}", styles["BodyText2"]))
        story.append(Spacer(1, 4))

    story.append(Spacer(1, 6))
    story.append(Paragraph("Please select one:", styles["BodyText2"]))
    story.append(checkbox("I CONSENT to the use of photographs/video as described above.", styles))
    story.append(checkbox("I DO NOT CONSENT to the use of photographs/video.", styles))

    story.append(Spacer(1, 14))
    for label in ["Client Full Name (Print)", "Client Signature", "Date",
                  "Artist Name", "Witness (if applicable)"]:
        story.append(field_line(label))
        story.append(Spacer(1, 6))

    doc.build(story)
    return path


# ── Form 5: Invoice ────────────────────────────────────────────────

def form_05_invoice():
    styles = get_styles()
    doc, path = make_doc("05-invoice.pdf", "Invoice")
    story = []
    build_header(story, "Invoice", styles)

    # Studio + client info side by side
    story.append(Paragraph("Studio Details", styles["SectionHead"]))
    story.append(gold_divider())
    studio_info = [
        "Ink & Soul Tattoo Studio",
        "123 High Street, London, EC1A 1BB",
        "Phone: (555) 123-4567",
        "Email: info@inkandsoul.com",
        "VAT No: GB 123 4567 89"
    ]
    for line in studio_info:
        story.append(Paragraph(line, styles["SmallText"]))

    story.append(Spacer(1, 8))
    story.append(Paragraph("Client Details", styles["SectionHead"]))
    story.append(gold_divider())
    for label in ["Client Name", "Email / Phone", "Invoice Number", "Invoice Date"]:
        story.append(field_line(label))
        story.append(Spacer(1, 4))

    story.append(Spacer(1, 8))
    story.append(Paragraph("Services Rendered", styles["SectionHead"]))
    story.append(gold_divider())

    table_data = [
        ["Description", "Hours", "Rate", "Amount"],
        ["", "", "", ""],
        ["", "", "", ""],
        ["", "", "", ""],
        ["", "", "", ""],
        ["", "", "", ""],
    ]
    t = Table(table_data, colWidths=[240, 60, 80, 80])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), OXBLOOD),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, GOLD),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_GRAY]),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t)

    story.append(Spacer(1, 8))
    totals = [
        ["", "", "Subtotal:", ""],
        ["", "", "Deposit Paid:", ""],
        ["", "", "Discount:", ""],
        ["", "", "VAT (20%):", ""],
        ["", "", "TOTAL DUE:", ""],
    ]
    tt = Table(totals, colWidths=[240, 60, 80, 80])
    tt.setStyle(TableStyle([
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
        ("LINEABOVE", (2, -1), (-1, -1), 1.5, OXBLOOD),
        ("TEXTCOLOR", (2, -1), (-1, -1), OXBLOOD),
        ("FONTNAME", (2, -1), (-1, -1), "Helvetica-Bold"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(tt)

    story.append(Spacer(1, 14))
    story.append(Paragraph("Payment Methods", styles["SectionHead"]))
    story.append(gold_divider())
    methods = ["Cash", "Card (Visa / Mastercard / Amex)", "Bank Transfer", "PayPal: payments@inkandsoul.com"]
    for m in methods:
        story.append(Paragraph(f"&bull;  {m}", styles["BodyText2"]))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Payment is due upon completion of the tattoo session unless otherwise agreed.", styles["SmallText"]))
    story.append(Paragraph("Thank you for choosing Ink & Soul Tattoo Studio.", styles["SmallText"]))

    doc.build(story)
    return path


# ── Form 6: Cancellation Policy ────────────────────────────────────

def form_06_cancellation():
    styles = get_styles()
    doc, path = make_doc("06-cancellation-policy.pdf", "Cancellation & Deposit Policy")
    story = []
    build_header(story, "Cancellation & Deposit Policy", styles)

    story.append(Paragraph("Deposit Policy", styles["SectionHead"]))
    story.append(gold_divider())
    deposits = [
        "A non-refundable deposit is required to secure your appointment. The deposit amount varies depending on the size and complexity of the tattoo.",
        "Standard deposit: 20% of the estimated total or a minimum of £50, whichever is greater.",
        "The deposit is deducted from the final cost of your tattoo on the day of your appointment.",
        "Deposits are non-transferable to other clients but may be applied to a rescheduled appointment (subject to the rescheduling policy below)."
    ]
    for d in deposits:
        story.append(Paragraph(f"&bull;  {d}", styles["BodyText2"]))
        story.append(Spacer(1, 2))

    story.append(Paragraph("Cancellation Policy", styles["SectionHead"]))
    story.append(gold_divider())

    cancel_data = [
        ["Notice Period", "Consequence"],
        ["More than 72 hours", "Deposit transferred to new date (one time only)"],
        ["48-72 hours", "50% of deposit forfeited; remainder applied to new booking"],
        ["Less than 48 hours", "Full deposit forfeited"],
        ["No-show", "Full deposit forfeited; future bookings require double deposit"],
    ]
    ct = Table(cancel_data, colWidths=[140, 320])
    ct.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), OXBLOOD),
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

    story.append(Paragraph("Rescheduling", styles["SectionHead"]))
    story.append(gold_divider())
    reschedule = [
        "You may reschedule your appointment once at no additional cost with more than 72 hours' notice.",
        "A second reschedule will be treated as a cancellation under the policy above.",
        "Rescheduled appointments must be booked within 90 days of the original date."
    ]
    for r in reschedule:
        story.append(Paragraph(f"&bull;  {r}", styles["BodyText2"]))
        story.append(Spacer(1, 2))

    story.append(Paragraph("Late Arrivals", styles["SectionHead"]))
    story.append(gold_divider())
    story.append(Paragraph(
        "If you arrive more than 15 minutes late, we may need to shorten your session or reschedule depending "
        "on the artist's availability. Arrivals more than 30 minutes late will be treated as a no-show.",
        styles["BodyText2"]
    ))

    story.append(Paragraph("Studio Cancellations", styles["SectionHead"]))
    story.append(gold_divider())
    story.append(Paragraph(
        "In the rare event that we need to cancel or reschedule your appointment, your deposit will be "
        "fully refunded or transferred to a new date of your choice. We will provide as much notice as possible.",
        styles["BodyText2"]
    ))

    story.append(Spacer(1, 14))
    story.append(Paragraph("I have read and agree to the Cancellation & Deposit Policy.", styles["BodyText2"]))
    story.append(Spacer(1, 10))
    for label in ["Client Full Name (Print)", "Client Signature", "Date", "Deposit Amount Paid"]:
        story.append(field_line(label))
        story.append(Spacer(1, 6))

    doc.build(story)
    return path


# ── Form 7: Session Tracker ────────────────────────────────────────

def form_07_session_tracker():
    styles = get_styles()
    doc, path = make_doc("07-session-tracker.pdf", "Session Tracker")
    story = []
    build_header(story, "Session Tracker", styles)

    story.append(Paragraph("Client Information", styles["SectionHead"]))
    story.append(gold_divider())
    for label in ["Client Name", "Phone / Email", "Tattoo Description", "Placement", "Artist"]:
        story.append(field_line(label))
        story.append(Spacer(1, 4))

    story.append(Paragraph("Session Log", styles["SectionHead"]))
    story.append(gold_divider())

    session_headers = ["Session", "Date", "Duration", "Work Completed", "Amount", "Notes"]
    session_data = [session_headers]
    for i in range(1, 9):
        session_data.append([str(i), "", "", "", "", ""])

    st = Table(session_data, colWidths=[45, 65, 55, 130, 60, 105])
    st.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), OXBLOOD),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, GOLD),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_GRAY]),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(st)

    story.append(Spacer(1, 10))
    story.append(Paragraph("Payment Summary", styles["SectionHead"]))
    story.append(gold_divider())

    pay_data = [
        ["Total Estimated Cost:", ""],
        ["Deposit Paid:", ""],
        ["Session Payments:", ""],
        ["Balance Remaining:", ""],
    ]
    pt = Table(pay_data, colWidths=[180, 120])
    pt.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, -1), (-1, -1), OXBLOOD),
        ("LINEBELOW", (0, 0), (-1, -2), 0.5, GOLD),
        ("LINEBELOW", (0, -1), (-1, -1), 1.5, OXBLOOD),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(pt)

    story.append(Spacer(1, 10))
    story.append(Paragraph("Touch-Up Notes", styles["SectionHead"]))
    story.append(gold_divider())
    story.append(field_line("Touch-up date"))
    story.append(Spacer(1, 4))
    story.append(field_line("Areas addressed"))
    story.append(Spacer(1, 4))
    story.append(field_line("Additional notes"))

    doc.build(story)
    return path


# ── Form 8: Aftercare Card ─────────────────────────────────────────

def form_08_aftercare_card():
    styles = get_styles()
    doc, path = make_doc("08-aftercare-card.pdf", "Aftercare Quick Reference Card")
    story = []
    build_header(story, "Aftercare Quick Reference Card", styles)

    story.append(Paragraph(
        "Congratulations on your new tattoo! Follow these steps to ensure a beautiful heal.",
        styles["BodyText2"]
    ))
    story.append(Spacer(1, 6))

    sections = [
        ("Day 1", [
            "Remove bandage after 2-4 hours",
            "Wash gently with lukewarm water and fragrance-free soap",
            "Pat dry with clean paper towel",
            "Apply thin layer of recommended ointment",
        ]),
        ("Days 2-7", [
            "Wash 2-3 times daily, moisturise after each wash",
            "Expect redness, slight swelling, and ink weeping — this is normal",
            "Wear loose clothing over the tattoo",
        ]),
        ("Days 7-14", [
            "Peeling and flaking will begin — DO NOT pick or scratch",
            "Continue moisturising regularly",
            "Itching is normal — tap gently, never scratch",
        ]),
        ("Weeks 3-6", [
            "Tattoo enters deep healing phase",
            "Skin may appear cloudy or milky — this clears as it heals",
            "Continue applying sunscreen when outdoors",
        ]),
    ]

    for title, items in sections:
        story.append(Paragraph(title, styles["SectionHead"]))
        story.append(gold_divider())
        for item in items:
            story.append(Paragraph(f"&bull;  {item}", styles["BodyText2"]))
        story.append(Spacer(1, 4))

    story.append(Paragraph("DO NOT", styles["SectionHead"]))
    story.append(gold_divider())
    donts = [
        "Soak in water (baths, pools, ocean) for 2-3 weeks",
        "Expose to direct sunlight or tanning beds",
        "Pick, scratch, or peel flaking skin",
        "Apply alcohol, peroxide, or Vaseline",
        "Let pets or dirty surfaces contact the tattoo",
    ]
    for d in donts:
        story.append(Paragraph(f"&#10005;  {d}", styles["BodyText2"]))

    story.append(Spacer(1, 10))
    story.append(gold_divider())
    story.append(Paragraph("Your Artist: ________________________    Date: ________________________", styles["BodyText2"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Touch-Up Policy: Free touch-ups within 90 days of your session (by appointment only).", styles["SmallText"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Ink & Soul Tattoo Studio  |  (555) 123-4567  |  info@inkandsoul.com  |  @inkandsoul", styles["Footer"]))

    doc.build(story)
    return path


# ── Main ────────────────────────────────────────────────────────────

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    generators = [
        form_01_client_intake,
        form_02_consent_waiver,
        form_03_aftercare,
        form_04_photo_release,
        form_05_invoice,
        form_06_cancellation,
        form_07_session_tracker,
        form_08_aftercare_card,
    ]
    paths = []
    for gen in generators:
        path = gen()
        paths.append(path)
        print(f"  Created: {os.path.basename(path)}")
    print(f"\nAll {len(paths)} forms generated in {OUTPUT_DIR}")
    return paths


if __name__ == "__main__":
    main()
