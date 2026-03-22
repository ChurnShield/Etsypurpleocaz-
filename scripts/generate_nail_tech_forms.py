#!/usr/bin/env python3
"""Generate 8 nail tech client forms as single-page A4 PDFs."""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, white
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

OUTPUT_DIR = "/root/NEW-AI-PROJECT/outputs/nail-tech-forms"

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
    styles.add(ParagraphStyle("FormTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=20, textColor=DARK, spaceAfter=2, spaceBefore=0, alignment=TA_CENTER))
    styles.add(ParagraphStyle("StudioName", parent=styles["Normal"], fontName="Helvetica", fontSize=9, textColor=GOLD, alignment=TA_CENTER, spaceAfter=1, spaceBefore=0))
    styles.add(ParagraphStyle("SectionHead", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12, textColor=DARK, spaceBefore=10, spaceAfter=3))
    styles.add(ParagraphStyle("Body", parent=styles["Normal"], fontName="Helvetica", fontSize=10, textColor=DARK_GRAY, leading=13, spaceAfter=3))
    styles.add(ParagraphStyle("BodySmall", parent=styles["Normal"], fontName="Helvetica", fontSize=8, textColor=DARK_GRAY, leading=10, spaceAfter=2))
    styles.add(ParagraphStyle("Footer", parent=styles["Normal"], fontName="Helvetica", fontSize=7, textColor=GOLD, alignment=TA_CENTER))
    return styles

_cached_styles = None
def S():
    global _cached_styles
    if _cached_styles is None: _cached_styles = get_styles()
    return _cached_styles

def gold_divider(): return HRFlowable(width="100%", thickness=1.2, color=GOLD, spaceAfter=6, spaceBefore=2)
def field(label): return Paragraph(f"<b>{label}:</b>  {'_' * 60}", S()["Body"])
def field2(l1, l2):
    s = S()["Body"]
    data = [[Paragraph(f"<b>{l1}:</b>  {'_' * 24}", s), Paragraph(f"<b>{l2}:</b>  {'_' * 24}", s)]]
    t = Table(data, colWidths=[CONTENT_W / 2] * 2)
    t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),3),("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0)]))
    return t
def cb(text): return Paragraph(f"{CBX}  {text}", S()["Body"])
def cb_row(items, cols=3):
    s = S()["Body"]; col_w = CONTENT_W / cols; rows = []
    for i in range(0, len(items), cols):
        chunk = items[i:i+cols]; row = [Paragraph(f"{CBX}  {it}", s) for it in chunk]
        while len(row) < cols: row.append(Paragraph("", s))
        rows.append(row)
    t = Table(rows, colWidths=[col_w]*cols)
    t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("TOPPADDING",(0,0),(-1,-1),1),("BOTTOMPADDING",(0,0),(-1,-1),1),("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0)]))
    return t
def page_header(story, title):
    s = S(); story.append(Paragraph("YOUR SALON NAME", s["StudioName"])); story.append(Paragraph(title, s["FormTitle"])); story.append(gold_divider())
def section(story, title): story.append(Paragraph(title, S()["SectionHead"])); story.append(gold_divider())
def make_doc(filename, title):
    filepath = os.path.join(OUTPUT_DIR, filename)
    return SimpleDocTemplate(filepath, pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN, bottomMargin=14*mm, title=title, author="PurpleOcaz Nail Tech Templates"), filepath
def sig_block(story): story.append(field2("Client Signature", "Date"))


def form_01_consent():
    doc, path = make_doc("01_Client_Consent_Form.pdf", "Client Consent Form")
    story = []; page_header(story, "Client Consent Form")
    section(story, "Client Information")
    story.append(field2("Full Name", "Date of Birth")); story.append(field("Address"))
    story.append(field2("Phone", "Email")); story.append(field("Emergency Contact Name & Phone"))
    section(story, "Nail & Skin Check")
    story.append(Paragraph("Do you have or have you ever had any of the following?", S()["Body"]))
    story.append(cb_row([
        "Fungal nail infection", "Allergies (acrylic, gel, adhesives, latex)",
        "Eczema / Psoriasis on hands or feet", "Warts or verrucas on hands or feet",
        "Diabetes / poor circulation", "Open wounds, cuts, or sores on hands",
        "Nail lifting or onycholysis", "Pregnant or breastfeeding",
        "Skin sensitivity / dermatitis", "Currently on blood-thinning medication",
    ], cols=2))
    story.append(field("If yes to any, provide details")); story.append(field("Current medications"))
    section(story, "Consent Declaration")
    for c in [
        "I confirm I am at least 16 years of age (or have parental consent).",
        "I confirm the above health information is accurate and complete.",
        "I understand nail treatments involve chemicals and tools with associated risks.",
        "I have informed the technician of any allergies or sensitivities.",
        "I consent to the treatment and accept all associated risks.",
        "I understand results may vary depending on nail condition and aftercare.",
        "I consent to standard hygiene practices. All tools are sterilised between clients.",
    ]: story.append(cb(c))
    story.append(Spacer(1, 6)); story.append(Paragraph("<b>I have read, understood, and agree to the terms above.</b>", S()["Body"]))
    story.append(Spacer(1, 4)); story.append(field2("Client Signature", "Date")); story.append(field2("Technician Name", "Technician Signature"))
    doc.build(story); return path


def form_02_intake():
    doc, path = make_doc("02_Client_Intake_Form.pdf", "Client Intake Form")
    story = []; page_header(story, "Client Intake Form")
    section(story, "Personal Details")
    story.append(field2("Full Name", "Date of Birth")); story.append(field2("Phone", "Email"))
    story.append(field("Address")); story.append(field2("Emergency Contact", "Emergency Phone"))
    section(story, "Service Details")
    story.append(field("Service Requested (gel, acrylic, manicure, pedicure, etc.)"))
    story.append(field("Preferred Style / Design"))
    story.append(field2("Nail Shape Preference", "Nail Length"))
    story.append(field("Colour / Design References"))
    section(story, "Previous Experience")
    story.append(cb_row(["First nail treatment", "Regular nail client", "Previous gel/acrylic"], cols=3))
    story.append(field("Any adverse reactions to previous nail treatments"))
    section(story, "Nail & Skin Sensitivity")
    story.append(cb_row(["Sensitive cuticles", "Brittle or peeling nails", "Eczema / Dermatitis", "Allergies (products, fragrances, latex)"], cols=2))
    section(story, "How Did You Hear About Us?")
    story.append(cb_row(["Instagram", "Facebook", "Google", "Walk-in", "Referral", "Other"], cols=3))
    story.append(Spacer(1, 8)); story.append(Paragraph("I confirm the information above is accurate and complete.", S()["Body"]))
    story.append(Spacer(1, 4)); sig_block(story)
    doc.build(story); return path


def form_03_aftercare():
    doc, path = make_doc("03_Aftercare_Instructions.pdf", "Aftercare Instructions")
    story = []; page_header(story, "Aftercare Instructions"); s = S()
    story.append(Paragraph("<i>Proper aftercare keeps your nails looking fresh and protects your natural nail underneath.</i>", s["Body"]))
    section(story, "First 24 Hours")
    for t in ["Avoid submerging nails in water for extended periods (baths, swimming, washing up without gloves).",
        "Do not pick, peel, or bite at your nails or enhancements.",
        "Avoid heavy impact or using nails as tools.",
        "Apply cuticle oil to hydrate the nail bed and surrounding skin.",
        "If a nail lifts, do not glue it yourself — contact us for a repair."]:
        story.append(Paragraph(f"&bull;  {t}", s["Body"]))
    section(story, "Ongoing Maintenance")
    for t in ["Apply cuticle oil daily to maintain flexibility and prevent dryness.",
        "Wear rubber gloves when cleaning, washing dishes, or using chemicals.",
        "Avoid using nails to open, scratch, or pry objects.",
        "Keep nails at a manageable length to prevent breakage.",
        "Book infill/maintenance appointments every 2-3 weeks."]:
        story.append(Paragraph(f"&bull;  {t}", s["Body"]))
    section(story, "What to Avoid")
    for t in ["Using acetone-based removers on gel or acrylic nails.",
        "Picking or forcing off enhancements — this damages the natural nail.",
        "Exposing nails to harsh chemicals without gloves.",
        "Filing or buffing enhancements at home unless advised."]:
        story.append(Paragraph(f"<font color='#1A1A1A'>&times;</font>  {t}", s["Body"]))
    section(story, "Warning Signs — Contact Us If:")
    for t in ["Nail lifting, greenish discolouration, or unusual odour",
        "Pain, redness, or swelling around the nail or cuticle",
        "Allergic reaction (itching, rash, blistering around the nails)",
        "A broken or cracked enhancement exposing the natural nail"]:
        story.append(Paragraph(f"<font color='#1A1A1A'><b>!</b></font>  {t}", s["Body"]))
    story.append(Spacer(1, 8)); story.append(gold_divider())
    story.append(field2("Your Technician", "Date")); story.append(field2("Salon Phone", "Salon Email"))
    doc.build(story); return path


def form_04_invoice():
    doc, path = make_doc("04_Invoice.pdf", "Invoice")
    story = []; page_header(story, "Invoice"); s = S()
    story.append(field2("Invoice No", "Date")); story.append(Spacer(1, 3))
    section(story, "Salon Details"); story.append(field("Salon Name")); story.append(field("Address")); story.append(field2("Phone", "Email"))
    section(story, "Client Details"); story.append(field("Client Name")); story.append(field2("Phone / Email", "Address"))
    section(story, "Services Rendered")
    table_data = [["Description", "Qty", "Rate", "Amount"]]
    for _ in range(5): table_data.append(["", "", "", ""])
    t = Table(table_data, colWidths=[CONTENT_W*0.48, CONTENT_W*0.14, CONTENT_W*0.19, CONTENT_W*0.19])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),DARK),("TEXTCOLOR",(0,0),(-1,0),white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,0),9),("FONTNAME",(0,1),(-1,-1),"Helvetica"),("FONTSIZE",(0,1),(-1,-1),9),("GRID",(0,0),(-1,-1),0.5,GOLD),("ROWBACKGROUNDS",(0,1),(-1,-1),[white,LIGHT_GRAY]),("ALIGN",(1,0),(-1,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
    story.append(t)
    totals = [["","","Subtotal:",""],["","","Products:",""],["","","Tax:",""],["","","TOTAL DUE:",""]]
    tt = Table(totals, colWidths=[CONTENT_W*0.48, CONTENT_W*0.14, CONTENT_W*0.19, CONTENT_W*0.19])
    tt.setStyle(TableStyle([("FONTNAME",(2,0),(2,-1),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),10),("ALIGN",(2,0),(-1,-1),"RIGHT"),("LINEABOVE",(2,-1),(-1,-1),1.5,DARK),("TEXTCOLOR",(2,-1),(-1,-1),DARK),("FONTNAME",(2,-1),(-1,-1),"Helvetica-Bold"),("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
    story.append(tt); story.append(Spacer(1, 6))
    section(story, "Payment Method"); story.append(cb_row(["Cash", "Card", "Bank Transfer", "PayPal", "Other"], cols=5))
    story.append(Spacer(1, 4)); story.append(field("Notes"))
    story.append(Paragraph("Payment is due upon completion of the service unless otherwise agreed.", s["BodySmall"]))
    doc.build(story); return path


def form_05_appointment_tracker():
    doc, path = make_doc("05_Appointment_Tracker.pdf", "Appointment Tracker")
    story = []; page_header(story, "Appointment Tracker")
    section(story, "Client Details")
    story.append(field2("Client Name", "Phone / Email")); story.append(field("Preferred Service / Usual Treatment"))
    story.append(field2("Preferred Technician", "Frequency"))
    section(story, "Appointment Log")
    headers = ["#", "Date", "Service", "Technician", "Amount", "Paid"]
    data = [headers]
    for i in range(1, 11): data.append([str(i), "", "", "", "", ""])
    st = Table(data, colWidths=[CONTENT_W*0.06, CONTENT_W*0.14, CONTENT_W*0.26, CONTENT_W*0.22, CONTENT_W*0.14, CONTENT_W*0.18])
    st.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),DARK),("TEXTCOLOR",(0,0),(-1,0),white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,0),8),("FONTNAME",(0,1),(-1,-1),"Helvetica"),("FONTSIZE",(0,1),(-1,-1),8),("GRID",(0,0),(-1,-1),0.5,GOLD),("ROWBACKGROUNDS",(0,1),(-1,-1),[white,LIGHT_GRAY]),("ALIGN",(0,0),(0,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
    story.append(st); story.append(Spacer(1, 6))
    section(story, "Notes")
    for _ in range(2): story.append(Paragraph("_" * 85, S()["Body"]))
    doc.build(story); return path


def form_06_photo_release():
    doc, path = make_doc("06_Photo_Release.pdf", "Photo Release Form")
    story = []; page_header(story, "Photo Release Form"); s = S()
    section(story, "Client Information"); story.append(field2("Full Name", "Date")); story.append(field2("Phone", "Email"))
    section(story, "Consent for Photography & Media Use")
    story.append(Paragraph("I hereby grant the salon, its technicians, and representatives the right to photograph, film, or otherwise capture images of my nail treatment and finished results.", s["Body"]))
    story.append(Spacer(1, 3)); story.append(Paragraph("These images may be used for:", s["Body"]))
    for use in ["Portfolio display (physical and digital) for technician and salon promotion", "Social media platforms (Instagram, TikTok, Facebook, Pinterest, etc.)", "Salon website, marketing materials, and print media", "Industry publications, competitions, and exhibitions", "Educational and training materials"]:
        story.append(Paragraph(f"&bull;  {use}", s["Body"]))
    section(story, "Terms")
    for i, term in enumerate(["No identifying personal information will be shared alongside images without explicit written consent.", "I waive any right to inspect or approve the finished images or the context in which they are used.", "I release the salon from any claims arising from the use of these images.", "This consent is valid indefinitely unless revoked in writing."], 1):
        story.append(Paragraph(f"<b>{i}.</b>  {term}", s["Body"]))
    story.append(Spacer(1, 6)); story.append(Paragraph("<b>Please select one:</b>", s["Body"]))
    story.append(cb("I CONSENT to the use of photographs/video as described above."))
    story.append(cb("I DO NOT CONSENT to the use of photographs/video."))
    story.append(Spacer(1, 10)); story.append(field2("Client Name (Print)", "Client Signature"))
    story.append(field2("Date", "Technician Name")); story.append(field("Witness (if applicable)"))
    doc.build(story); return path


def form_07_cancellation():
    doc, path = make_doc("07_Cancellation_Policy.pdf", "Cancellation & Deposit Policy")
    story = []; page_header(story, "Cancellation & Deposit Policy"); s = S()
    section(story, "Deposit Policy")
    for d in ["A deposit may be required to secure appointments for nail art, sets, or premium services.", "Standard deposit: a minimum of \u00a310 or as agreed at booking.", "The deposit is deducted from the final cost on the day of your appointment.", "Deposits are non-transferable but may be applied to a rescheduled appointment (see below)."]:
        story.append(Paragraph(f"&bull;  {d}", s["Body"]))
    section(story, "Cancellation Policy")
    cancel_data = [["Notice Period", "Consequence"], ["More than 24 hours", "Deposit transferred to new date (one time only)"], ["12-24 hours", "50% of deposit forfeited; remainder applied to new booking"], ["Less than 12 hours", "Full deposit forfeited"], ["No-show", "Full deposit forfeited; future bookings require deposit upfront"]]
    ct = Table(cancel_data, colWidths=[CONTENT_W*0.30, CONTENT_W*0.70])
    ct.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),DARK),("TEXTCOLOR",(0,0),(-1,0),white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),9),("FONTNAME",(0,1),(-1,-1),"Helvetica"),("GRID",(0,0),(-1,-1),0.5,GOLD),("ROWBACKGROUNDS",(0,1),(-1,-1),[white,LIGHT_GRAY]),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
    story.append(ct)
    section(story, "Rescheduling")
    for r in ["You may reschedule once at no additional cost with more than 24 hours' notice.", "A second reschedule will be treated as a cancellation under the policy above.", "Rescheduled appointments must be booked within 30 days of the original date."]:
        story.append(Paragraph(f"&bull;  {r}", s["Body"]))
    section(story, "Late Arrivals")
    story.append(Paragraph("Arrivals more than 10 minutes late may result in a shortened service or reschedule. Arrivals more than 20 minutes late will be treated as a no-show.", s["Body"]))
    section(story, "Salon Cancellations")
    story.append(Paragraph("If the salon cancels or reschedules, your deposit will be fully refunded or transferred to a new date of your choice. We will provide as much notice as possible.", s["Body"]))
    story.append(Spacer(1, 10)); story.append(Paragraph("<b>I have read and agree to the Cancellation &amp; Deposit Policy.</b>", S()["Body"]))
    story.append(Spacer(1, 4)); story.append(field2("Client Name (Print)", "Client Signature")); story.append(field2("Date", "Deposit Amount Paid"))
    doc.build(story); return path


def form_08_design_request():
    doc, path = make_doc("08_Nail_Design_Request.pdf", "Nail Design Request Form")
    story = []; page_header(story, "Nail Design Request Form"); s = S()
    section(story, "Client Information"); story.append(field2("Full Name", "Date")); story.append(field2("Phone", "Email")); story.append(field("Preferred Technician"))
    section(story, "Design Brief"); story.append(Paragraph("<b>Describe the look you want:</b>", s["Body"]))
    for _ in range(3): story.append(Paragraph("_" * 85, s["Body"]))
    section(story, "Nail Shape Preferences")
    story.append(cb_row(["Square", "Round", "Oval", "Almond", "Coffin / Ballerina", "Stiletto", "Squoval", "Lipstick", "Short Natural", "Extra Long", "Medium Length", "Other"], cols=4))
    section(story, "Service & Finish")
    story.append(field("Service Type (gel, acrylic, BIAB, dip powder, natural mani, etc.)"))
    story.append(field2("Finish (glossy / matte)", "Colour / Theme"))
    story.append(field("Nail Art Details (French tip, ombre, gems, foils, stamping, etc.)"))
    section(story, "Reference Images")
    story.append(Paragraph("Attach or show reference images, screenshots, or inspiration below:", s["Body"]))
    ref_row = []
    for i in range(1, 4):
        ref_row.append(Paragraph(f"<br/><br/><br/><font color='#999999' size='8'>Reference {i}</font>", ParagraphStyle(f"ref{i}", alignment=TA_CENTER, fontSize=8, textColor=MID_GRAY)))
    ref_table = Table([ref_row], colWidths=[CONTENT_W/3]*3, rowHeights=[65])
    ref_table.setStyle(TableStyle([("BOX",(0,0),(0,0),0.8,GOLD),("BOX",(1,0),(1,0),0.8,GOLD),("BOX",(2,0),(2,0),0.8,GOLD),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("ALIGN",(0,0),(-1,-1),"CENTER")]))
    story.append(ref_table)
    section(story, "Additional Notes")
    for _ in range(2): story.append(Paragraph("_" * 85, s["Body"]))
    story.append(Spacer(1, 6)); sig_block(story)
    doc.build(story); return path


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    generators = [form_01_consent, form_02_intake, form_03_aftercare, form_04_invoice, form_05_appointment_tracker, form_06_photo_release, form_07_cancellation, form_08_design_request]
    for gen in generators:
        p = gen(); print(f"  Created: {os.path.basename(p)}")
    print(f"\nAll 8 forms generated in {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
