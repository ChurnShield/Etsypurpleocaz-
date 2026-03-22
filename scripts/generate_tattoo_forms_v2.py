#!/usr/bin/env python3
"""Generate 8 professional tattoo studio client forms as single-page A4 PDFs.
V2 visual identity for A/B testing.

Palette: off-white #F5F5F5 bg, near-black #111111 text, mid-grey #888888 accents.
Fonts: Playfair Display headings, Lato body.

Forms (same content as v1, different visual identity):
  1. Client Consent Form
  2. Client Intake Form
  3. Aftercare Instructions
  4. Invoice
  5. Session Tracker
  6. Photo Release Form
  7. Cancellation & Deposit Policy
  8. Flash Sheet / Design Request Form
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
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── Font registration ────────────────────────────────────────────────
FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "fonts")

pdfmetrics.registerFont(TTFont("PlayfairDisplay", os.path.join(FONT_DIR, "PlayfairDisplay-Regular.ttf")))
pdfmetrics.registerFont(TTFont("PlayfairDisplay-Bold", os.path.join(FONT_DIR, "PlayfairDisplay-Bold.ttf")))
pdfmetrics.registerFont(TTFont("Lato", os.path.join(FONT_DIR, "Lato-Regular.ttf")))
pdfmetrics.registerFont(TTFont("Lato-Bold", os.path.join(FONT_DIR, "Lato-Bold.ttf")))
pdfmetrics.registerFont(TTFont("Lato-Italic", os.path.join(FONT_DIR, "Lato-Italic.ttf")))

pdfmetrics.registerFontFamily(
    "Lato", normal="Lato", bold="Lato-Bold", italic="Lato-Italic"
)

# ── Palette ──────────────────────────────────────────────────────────
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs", "tattoo-forms-v2")

BG = HexColor("#F5F5F5")
TEXT = HexColor("#111111")
ACCENT = HexColor("#888888")
LIGHT_ACCENT = HexColor("#D0D0D0")
TABLE_ALT = HexColor("#EEEEEE")

WIDTH, HEIGHT = A4
MARGIN = 18 * mm
CONTENT_W = WIDTH - 2 * MARGIN

CBX = "\u25a1"


def get_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        "FormTitle", parent=styles["Title"],
        fontName="PlayfairDisplay-Bold", fontSize=20,
        textColor=TEXT, spaceAfter=2, spaceBefore=0, alignment=TA_CENTER
    ))
    styles.add(ParagraphStyle(
        "StudioName", parent=styles["Normal"],
        fontName="Lato", fontSize=9,
        textColor=ACCENT, alignment=TA_CENTER, spaceAfter=1, spaceBefore=0
    ))
    styles.add(ParagraphStyle(
        "SectionHead", parent=styles["Heading2"],
        fontName="PlayfairDisplay-Bold", fontSize=12,
        textColor=TEXT, spaceBefore=10, spaceAfter=3
    ))
    styles.add(ParagraphStyle(
        "Body", parent=styles["Normal"],
        fontName="Lato", fontSize=10,
        textColor=TEXT, leading=13, spaceAfter=3
    ))
    styles.add(ParagraphStyle(
        "BodySmall", parent=styles["Normal"],
        fontName="Lato", fontSize=8,
        textColor=TEXT, leading=10, spaceAfter=2
    ))
    styles.add(ParagraphStyle(
        "Footer", parent=styles["Normal"],
        fontName="Lato", fontSize=7,
        textColor=ACCENT, alignment=TA_CENTER
    ))
    return styles


_cached_styles = None


def S():
    global _cached_styles
    if _cached_styles is None:
        _cached_styles = get_styles()
    return _cached_styles


def grey_divider():
    return HRFlowable(width="100%", thickness=1.0, color=ACCENT, spaceAfter=6, spaceBefore=2)


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
    story.append(Paragraph("YOUR STUDIO NAME", s["StudioName"]))
    story.append(Paragraph(title, s["FormTitle"]))
    story.append(grey_divider())


def section(story, title):
    story.append(Paragraph(title, S()["SectionHead"]))
    story.append(grey_divider())


def _bg_canvas(canvas, doc):
    """Draw the off-white background on every page."""
    canvas.saveState()
    canvas.setFillColor(BG)
    canvas.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)
    canvas.restoreState()


def make_doc(filename, title):
    filepath = os.path.join(OUTPUT_DIR, filename)
    doc = SimpleDocTemplate(
        filepath, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=14 * mm,
        title=title, author="PurpleOcaz Tattoo Templates"
    )
    return doc, filepath


def sig_block(story):
    story.append(field2("Client Signature", "Date"))


# ── Form 1: Client Consent Form ──────────────────────────────────────

def form_01_consent():
    doc, path = make_doc("01_Client_Consent_Form.pdf", "Client Consent Form")
    story = []
    page_header(story, "Client Consent Form")

    section(story, "Client Information")
    story.append(field2("Full Name", "Date of Birth"))
    story.append(field("Address"))
    story.append(field2("Phone", "Email"))
    story.append(field("Emergency Contact Name & Phone"))

    section(story, "Health Declaration")
    story.append(Paragraph("Do you have or have you ever had any of the following?", S()["Body"]))
    story.append(cb_row([
        "Heart condition / blood pressure", "Diabetes",
        "Epilepsy / seizures", "Skin conditions (eczema, psoriasis, keloids)",
        "Blood-borne diseases (Hepatitis, HIV)", "Allergies (latex, ink, anaesthetics)",
        "Hemophilia / clotting disorder", "Pregnant or breastfeeding",
        "Blood-thinning medication", "Under influence of alcohol / drugs",
    ], cols=2))
    story.append(field("If yes to any, provide details"))
    story.append(field("Current medications"))

    section(story, "Consent Declaration")
    for clause in [
        "I confirm I am at least 18 years of age.",
        "I confirm the above health information is accurate and complete.",
        "I understand tattooing involves risks including infection, scarring, and allergic reaction.",
        "I have been informed of the aftercare procedure and agree to follow it.",
        "I consent to the tattoo procedure and accept all associated risks.",
        "I understand tattoos are permanent and removal is difficult and costly.",
        "I consent to standard sterilisation practices. All needles/inks are single-use or sterilised.",
    ]:
        story.append(cb(clause))

    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>I have read, understood, and agree to the terms above.</b>", S()["Body"]))
    story.append(Spacer(1, 4))
    story.append(field2("Client Signature", "Date"))
    story.append(field2("Artist Name", "Artist Signature"))

    doc.build(story, onFirstPage=_bg_canvas, onLaterPages=_bg_canvas)
    return path


# ── Form 2: Client Intake Form ───────────────────────────────────────

def form_02_intake():
    doc, path = make_doc("02_Client_Intake_Form.pdf", "Client Intake Form")
    story = []
    page_header(story, "Client Intake Form")

    section(story, "Personal Details")
    story.append(field2("Full Name", "Date of Birth"))
    story.append(field2("Phone", "Email"))
    story.append(field("Address"))
    story.append(field2("Emergency Contact", "Emergency Phone"))

    section(story, "Tattoo Details")
    story.append(field("Design Description / Concept"))
    story.append(field("Placement / Body Area"))
    story.append(field2("Approximate Size", "Colour or B&W"))
    story.append(field("Preferred Style (realism, traditional, blackwork, etc.)"))
    story.append(field("Reference Images Provided"))

    section(story, "Previous Experience")
    story.append(cb_row(["First tattoo", "Have existing tattoos"], cols=2))
    story.append(field("Any adverse reactions to previous tattoos"))

    section(story, "Skin Sensitivity")
    story.append(cb_row([
        "Sensitive skin", "Keloid scarring",
        "Eczema / Psoriasis", "Allergies (latex, metals, adhesives)",
    ], cols=2))

    section(story, "How Did You Hear About Us?")
    story.append(cb_row(["Instagram", "Facebook", "Google", "Walk-in", "Referral", "Other"], cols=3))

    story.append(Spacer(1, 8))
    story.append(Paragraph("I confirm the information above is accurate and complete.", S()["Body"]))
    story.append(Spacer(1, 4))
    sig_block(story)

    doc.build(story, onFirstPage=_bg_canvas, onLaterPages=_bg_canvas)
    return path


# ── Form 3: Aftercare Instructions ───────────────────────────────────

def form_03_aftercare():
    doc, path = make_doc("03_Aftercare_Instructions.pdf", "Aftercare Instructions")
    story = []
    page_header(story, "Aftercare Instructions")
    s = S()

    story.append(Paragraph(
        "<i>Your tattoo is an open wound. Proper aftercare is essential for healing and preserving ink quality.</i>",
        s["Body"]
    ))

    section(story, "First 24 Hours")
    for t in [
        "Leave the bandage/wrap on for 2-4 hours (or as directed by your artist).",
        "Wash hands thoroughly before touching the tattoo.",
        "Gently wash with lukewarm water and fragrance-free antibacterial soap.",
        "Pat dry with a clean paper towel — never use a cloth towel.",
        "Apply a thin layer of recommended aftercare ointment.",
        "Do NOT re-bandage unless instructed by your artist.",
    ]:
        story.append(Paragraph(f"&bull;  {t}", s["Body"]))

    section(story, "Days 2-14: Healing Phase")
    for t in [
        "Wash 2-3 times daily with mild soap and lukewarm water.",
        "Apply a thin layer of fragrance-free moisturiser after each wash.",
        "Tattoo will peel and flake — this is normal. Do NOT pick or scratch.",
        "Wear loose, breathable clothing over the tattooed area.",
        "Avoid sleeping directly on the tattoo when possible.",
    ]:
        story.append(Paragraph(f"&bull;  {t}", s["Body"]))

    section(story, "What to Avoid")
    for t in [
        "Submerging in water (baths, pools, hot tubs, sea) for at least 2-3 weeks.",
        "Direct sunlight or tanning beds during the healing period.",
        "Gym workouts or heavy sweating for 48-72 hours.",
        "Tight or abrasive clothing over the tattoo.",
        "Applying alcohol, hydrogen peroxide, or Vaseline.",
    ]:
        story.append(Paragraph(f"<font color='#888888'>&times;</font>  {t}", s["Body"]))

    section(story, "Long-Term Care")
    for t in [
        "Apply SPF 30+ sunscreen to healed tattoos when exposed to sunlight.",
        "Keep skin moisturised to maintain vibrancy.",
        "Full healing takes 4-6 weeks. Deeper layers heal for up to 3 months.",
    ]:
        story.append(Paragraph(f"&bull;  {t}", s["Body"]))

    section(story, "Warning Signs — Contact Us Immediately If:")
    for t in [
        "Excessive redness, swelling, or warmth beyond 48 hours",
        "Pus, green/yellow discharge, or foul smell",
        "Fever, chills, or red streaks radiating from the tattoo",
        "Severe itching with raised bumps or blistering",
    ]:
        story.append(Paragraph(f"<font color='#111111'><b>!</b></font>  {t}", s["Body"]))

    story.append(Spacer(1, 8))
    story.append(grey_divider())
    story.append(field2("Your Artist", "Date"))
    story.append(field2("Studio Phone", "Studio Email"))

    doc.build(story, onFirstPage=_bg_canvas, onLaterPages=_bg_canvas)
    return path


# ── Form 4: Invoice ──────────────────────────────────────────────────

def form_04_invoice():
    doc, path = make_doc("04_Invoice.pdf", "Invoice")
    story = []
    page_header(story, "Invoice")
    s = S()

    story.append(field2("Invoice No", "Date"))
    story.append(Spacer(1, 3))

    section(story, "Studio Details")
    story.append(field("Studio Name"))
    story.append(field("Address"))
    story.append(field2("Phone", "Email"))

    section(story, "Client Details")
    story.append(field("Client Name"))
    story.append(field2("Phone / Email", "Address"))

    section(story, "Services Rendered")
    table_data = [["Description", "Hours", "Rate", "Amount"]]
    for _ in range(5):
        table_data.append(["", "", "", ""])
    t = Table(table_data, colWidths=[CONTENT_W * 0.48, CONTENT_W * 0.14, CONTENT_W * 0.19, CONTENT_W * 0.19])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TEXT),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Lato-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("FONTNAME", (0, 1), (-1, -1), "Lato"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, ACCENT),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, TABLE_ALT]),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t)

    totals = [
        ["", "", "Subtotal:", ""],
        ["", "", "Deposit Paid:", ""],
        ["", "", "Tax:", ""],
        ["", "", "TOTAL DUE:", ""],
    ]
    tt = Table(totals, colWidths=[CONTENT_W * 0.48, CONTENT_W * 0.14, CONTENT_W * 0.19, CONTENT_W * 0.19])
    tt.setStyle(TableStyle([
        ("FONTNAME", (2, 0), (2, -1), "Lato-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
        ("LINEABOVE", (2, -1), (-1, -1), 1.5, TEXT),
        ("TEXTCOLOR", (2, -1), (-1, -1), TEXT),
        ("FONTNAME", (2, -1), (-1, -1), "Lato-Bold"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(tt)

    story.append(Spacer(1, 6))
    section(story, "Payment Method")
    story.append(cb_row(["Cash", "Card", "Bank Transfer", "PayPal", "Other"], cols=5))
    story.append(Spacer(1, 4))
    story.append(field("Notes"))
    story.append(Paragraph("Payment is due upon completion of the session unless otherwise agreed.", s["BodySmall"]))

    doc.build(story, onFirstPage=_bg_canvas, onLaterPages=_bg_canvas)
    return path


# ── Form 5: Session Tracker ──────────────────────────────────────────

def form_05_session_tracker():
    doc, path = make_doc("05_Session_Tracker.pdf", "Session Tracker")
    story = []
    page_header(story, "Session Tracker")

    section(story, "Client & Project Details")
    story.append(field2("Client Name", "Phone / Email"))
    story.append(field("Tattoo Description"))
    story.append(field2("Placement", "Artist"))
    story.append(field2("Total Quoted", "Deposit Paid"))

    section(story, "Session Log")
    headers = ["#", "Date", "Duration", "Work Completed", "Amount", "Paid"]
    data = [headers]
    for i in range(1, 11):
        data.append([str(i), "", "", "", "", ""])

    st = Table(data, colWidths=[CONTENT_W * 0.06, CONTENT_W * 0.14, CONTENT_W * 0.12,
                                CONTENT_W * 0.36, CONTENT_W * 0.14, CONTENT_W * 0.18])
    st.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TEXT),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Lato-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("FONTNAME", (0, 1), (-1, -1), "Lato"),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, ACCENT),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, TABLE_ALT]),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(st)

    story.append(Spacer(1, 6))
    section(story, "Payment Summary")
    pay_data = [
        ["Total Estimated:", ""], ["Deposit Paid:", ""],
        ["Session Payments:", ""], ["Balance Due:", ""],
    ]
    pt = Table(pay_data, colWidths=[160, 120])
    pt.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Lato-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, -1), (-1, -1), TEXT),
        ("LINEBELOW", (0, 0), (-1, -2), 0.5, ACCENT),
        ("LINEBELOW", (0, -1), (-1, -1), 1.5, TEXT),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(pt)

    story.append(Spacer(1, 4))
    story.append(field("Notes"))

    doc.build(story, onFirstPage=_bg_canvas, onLaterPages=_bg_canvas)
    return path


# ── Form 6: Photo Release Form ───────────────────────────────────────

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
        "I hereby grant the studio, its artists, and representatives the right to photograph, film, "
        "or otherwise capture images of my tattoo(s) and the tattooing process.",
        s["Body"]
    ))
    story.append(Spacer(1, 3))
    story.append(Paragraph("These images may be used for:", s["Body"]))
    for use in [
        "Portfolio display (physical and digital) for artist and studio promotion",
        "Social media platforms (Instagram, TikTok, Facebook, Pinterest, etc.)",
        "Studio website, marketing materials, and print media",
        "Tattoo conventions, exhibitions, and industry publications",
        "Educational and training materials",
    ]:
        story.append(Paragraph(f"&bull;  {use}", s["Body"]))

    section(story, "Terms")
    for i, term in enumerate([
        "No identifying personal information will be shared alongside images without explicit written consent.",
        "I waive any right to inspect or approve the finished images or the context in which they are used.",
        "I release the studio from any claims arising from the use of these images.",
        "This consent is valid indefinitely unless revoked in writing.",
    ], 1):
        story.append(Paragraph(f"<b>{i}.</b>  {term}", s["Body"]))

    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Please select one:</b>", s["Body"]))
    story.append(cb("I CONSENT to the use of photographs/video as described above."))
    story.append(cb("I DO NOT CONSENT to the use of photographs/video."))

    story.append(Spacer(1, 10))
    story.append(field2("Client Name (Print)", "Client Signature"))
    story.append(field2("Date", "Artist Name"))
    story.append(field("Witness (if applicable)"))

    doc.build(story, onFirstPage=_bg_canvas, onLaterPages=_bg_canvas)
    return path


# ── Form 7: Cancellation & Deposit Policy ────────────────────────────

def form_07_cancellation():
    doc, path = make_doc("07_Cancellation_Policy.pdf", "Cancellation & Deposit Policy")
    story = []
    page_header(story, "Cancellation & Deposit Policy")
    s = S()

    section(story, "Deposit Policy")
    for d in [
        "A non-refundable deposit is required to secure your appointment.",
        "Standard deposit: 20% of the estimated total or a minimum of \u00a350, whichever is greater.",
        "The deposit is deducted from the final cost on the day of your appointment.",
        "Deposits are non-transferable but may be applied to a rescheduled appointment (see below).",
    ]:
        story.append(Paragraph(f"&bull;  {d}", s["Body"]))

    section(story, "Cancellation Policy")
    cancel_data = [
        ["Notice Period", "Consequence"],
        ["More than 72 hours", "Deposit transferred to new date (one time only)"],
        ["48-72 hours", "50% of deposit forfeited; remainder applied to new booking"],
        ["Less than 48 hours", "Full deposit forfeited"],
        ["No-show", "Full deposit forfeited; future bookings require double deposit"],
    ]
    ct = Table(cancel_data, colWidths=[CONTENT_W * 0.30, CONTENT_W * 0.70])
    ct.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TEXT),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Lato-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 1), (-1, -1), "Lato"),
        ("GRID", (0, 0), (-1, -1), 0.5, ACCENT),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, TABLE_ALT]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(ct)

    section(story, "Rescheduling")
    for r in [
        "You may reschedule once at no additional cost with more than 72 hours' notice.",
        "A second reschedule will be treated as a cancellation under the policy above.",
        "Rescheduled appointments must be booked within 90 days of the original date.",
    ]:
        story.append(Paragraph(f"&bull;  {r}", s["Body"]))

    section(story, "Late Arrivals")
    story.append(Paragraph(
        "Arrivals more than 15 minutes late may result in a shortened session or reschedule. "
        "Arrivals more than 30 minutes late will be treated as a no-show.",
        s["Body"]
    ))

    section(story, "Studio Cancellations")
    story.append(Paragraph(
        "If the studio cancels or reschedules, your deposit will be fully refunded or transferred "
        "to a new date of your choice. We will provide as much notice as possible.",
        s["Body"]
    ))

    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>I have read and agree to the Cancellation &amp; Deposit Policy.</b>", s["Body"]))
    story.append(Spacer(1, 4))
    story.append(field2("Client Name (Print)", "Client Signature"))
    story.append(field2("Date", "Deposit Amount Paid"))

    doc.build(story, onFirstPage=_bg_canvas, onLaterPages=_bg_canvas)
    return path


# ── Form 8: Flash Sheet / Design Request Form ────────────────────────

def form_08_design_request():
    doc, path = make_doc("08_Design_Request_Form.pdf", "Flash Sheet / Design Request Form")
    story = []
    page_header(story, "Design Request Form")
    s = S()

    section(story, "Client Information")
    story.append(field2("Full Name", "Date"))
    story.append(field2("Phone", "Email"))
    story.append(field("Preferred Artist"))

    section(story, "Design Brief")
    story.append(Paragraph("<b>Design Concept / Description:</b>", s["Body"]))
    for _ in range(3):
        story.append(Paragraph("_" * 85, s["Body"]))

    section(story, "Style Preferences")
    story.append(cb_row([
        "Traditional", "Neo-Traditional", "Realism", "Blackwork",
        "Watercolour", "Japanese", "Geometric", "Minimalist",
        "Dotwork", "Tribal", "Script/Lettering", "Other",
    ], cols=4))

    section(story, "Placement & Size")
    story.append(field("Body Area / Placement"))
    story.append(field2("Approximate Size (cm)", "Colour / B&W / Grey-wash"))

    section(story, "Reference Images")
    story.append(Paragraph("Attach or sketch reference images, mood boards, or inspiration below:", s["Body"]))
    ref_row = []
    for i in range(1, 4):
        ref_row.append(Paragraph(
            f"<br/><br/><br/><font color='#888888' size='8'>Reference {i}</font>",
            ParagraphStyle(f"ref{i}", alignment=TA_CENTER, fontSize=8, textColor=ACCENT)
        ))
    ref_table = Table([ref_row], colWidths=[CONTENT_W / 3] * 3, rowHeights=[65])
    ref_table.setStyle(TableStyle([
        ("BOX", (0, 0), (0, 0), 0.8, ACCENT),
        ("BOX", (1, 0), (1, 0), 0.8, ACCENT),
        ("BOX", (2, 0), (2, 0), 0.8, ACCENT),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    story.append(ref_table)

    section(story, "Additional Notes")
    for _ in range(2):
        story.append(Paragraph("_" * 85, s["Body"]))

    story.append(Spacer(1, 6))
    sig_block(story)

    doc.build(story, onFirstPage=_bg_canvas, onLaterPages=_bg_canvas)
    return path


# ── Main ──────────────────────────────────────────────────────────────

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    generators = [
        form_01_consent,
        form_02_intake,
        form_03_aftercare,
        form_04_invoice,
        form_05_session_tracker,
        form_06_photo_release,
        form_07_cancellation,
        form_08_design_request,
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
