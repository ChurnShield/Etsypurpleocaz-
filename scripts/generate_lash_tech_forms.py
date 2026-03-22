#!/usr/bin/env python3
"""Generate 8 lash tech client forms as single-page A4 PDFs."""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, white
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT

OUTPUT_DIR = "/root/NEW-AI-PROJECT/outputs/lash-tech-forms"
DARK = HexColor("#1A1A1A"); GOLD = HexColor("#C9A96E"); LIGHT_GRAY = HexColor("#F5F5F5"); DARK_GRAY = HexColor("#333333"); MID_GRAY = HexColor("#999999")
WIDTH, HEIGHT = A4; MARGIN = 18*mm; CONTENT_W = WIDTH - 2*MARGIN; CBX = "\u25a1"

def get_styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle("FormTitle",parent=s["Title"],fontName="Helvetica-Bold",fontSize=20,textColor=DARK,spaceAfter=2,spaceBefore=0,alignment=TA_CENTER))
    s.add(ParagraphStyle("StudioName",parent=s["Normal"],fontName="Helvetica",fontSize=9,textColor=GOLD,alignment=TA_CENTER,spaceAfter=1,spaceBefore=0))
    s.add(ParagraphStyle("SectionHead",parent=s["Heading2"],fontName="Helvetica-Bold",fontSize=12,textColor=DARK,spaceBefore=10,spaceAfter=3))
    s.add(ParagraphStyle("Body",parent=s["Normal"],fontName="Helvetica",fontSize=10,textColor=DARK_GRAY,leading=13,spaceAfter=3))
    s.add(ParagraphStyle("BodySmall",parent=s["Normal"],fontName="Helvetica",fontSize=8,textColor=DARK_GRAY,leading=10,spaceAfter=2))
    return s
_cs = None
def S():
    global _cs
    if _cs is None: _cs = get_styles()
    return _cs
def gold_divider(): return HRFlowable(width="100%",thickness=1.2,color=GOLD,spaceAfter=6,spaceBefore=2)
def field(l): return Paragraph(f"<b>{l}:</b>  {'_'*60}",S()["Body"])
def field2(a,b):
    s=S()["Body"]; d=[[Paragraph(f"<b>{a}:</b>  {'_'*24}",s),Paragraph(f"<b>{b}:</b>  {'_'*24}",s)]]
    t=Table(d,colWidths=[CONTENT_W/2]*2); t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),3),("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0)])); return t
def cb(t): return Paragraph(f"{CBX}  {t}",S()["Body"])
def cb_row(items,cols=3):
    s=S()["Body"]; cw=CONTENT_W/cols; rows=[]
    for i in range(0,len(items),cols):
        ch=items[i:i+cols]; r=[Paragraph(f"{CBX}  {x}",s) for x in ch]
        while len(r)<cols: r.append(Paragraph("",s))
        rows.append(r)
    t=Table(rows,colWidths=[cw]*cols); t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("TOPPADDING",(0,0),(-1,-1),1),("BOTTOMPADDING",(0,0),(-1,-1),1),("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0)])); return t
def page_header(st,title): s=S(); st.append(Paragraph("YOUR SALON NAME",s["StudioName"])); st.append(Paragraph(title,s["FormTitle"])); st.append(gold_divider())
def section(st,title): st.append(Paragraph(title,S()["SectionHead"])); st.append(gold_divider())
def make_doc(fn,title):
    fp=os.path.join(OUTPUT_DIR,fn); return SimpleDocTemplate(fp,pagesize=A4,leftMargin=MARGIN,rightMargin=MARGIN,topMargin=MARGIN,bottomMargin=14*mm,title=title,author="PurpleOcaz Lash Tech Templates"),fp
def sig_block(st): st.append(field2("Client Signature","Date"))

def form_01():
    doc,path=make_doc("01_Client_Consent_Form.pdf","Client Consent Form"); st=[]; page_header(st,"Client Consent Form")
    section(st,"Client Information"); st.append(field2("Full Name","Date of Birth")); st.append(field("Address")); st.append(field2("Phone","Email")); st.append(field("Emergency Contact Name & Phone"))
    section(st,"Eye & Skin Check")
    st.append(Paragraph("Do you have or have you ever had any of the following?",S()["Body"]))
    st.append(cb_row(["Eye infections or styes (current or recent)","Allergies (adhesive, latex, cyanoacrylate)","Blepharitis or dry eye syndrome","Eczema / Dermatitis around eyes","Recent eye surgery (LASIK, cataract)","Conjunctivitis (pink eye)","Alopecia or lash loss treatment","Pregnant or breastfeeding","Contact lens wearer","Currently on retinoids or Accutane"],cols=2))
    st.append(field("If yes to any, provide details")); st.append(field("Current medications"))
    section(st,"Patch Test Record")
    st.append(field2("Patch Test Date","Patch Test Result")); st.append(Paragraph("A patch test must be completed at least 24 hours before the first treatment.",S()["Body"]))
    section(st,"Consent Declaration")
    for c in ["I confirm I am at least 16 years of age (or have parental consent).","I confirm the above health information is accurate and complete.","I understand lash treatments involve adhesives and tools near the eye area.","I have informed the technician of any allergies or sensitivities.","I consent to the treatment and accept all associated risks.","I understand results may vary depending on natural lash condition and aftercare.","I consent to standard hygiene practices. All tools are sterilised between clients."]:
        st.append(cb(c))
    st.append(Spacer(1,6)); st.append(Paragraph("<b>I have read, understood, and agree to the terms above.</b>",S()["Body"]))
    st.append(Spacer(1,4)); st.append(field2("Client Signature","Date")); st.append(field2("Technician Name","Technician Signature"))
    doc.build(st); return path

def form_02():
    doc,path=make_doc("02_Client_Intake_Form.pdf","Client Intake Form"); st=[]; page_header(st,"Client Intake Form")
    section(st,"Personal Details"); st.append(field2("Full Name","Date of Birth")); st.append(field2("Phone","Email")); st.append(field("Address")); st.append(field2("Emergency Contact","Emergency Phone"))
    section(st,"Service Details")
    st.append(field("Service Requested (classic, hybrid, volume, mega volume, lift & tint, etc.)"))
    st.append(field("Preferred Lash Style / Look")); st.append(field2("Lash Curl Preference","Lash Length")); st.append(field("Any specific look or reference images"))
    section(st,"Previous Experience")
    st.append(cb_row(["First lash treatment","Regular lash client","Previous extensions"],cols=3))
    st.append(field("Any adverse reactions to previous lash treatments"))
    section(st,"Eye & Skin Sensitivity")
    st.append(cb_row(["Sensitive eyes","Watery eyes","Contact lenses","Allergies (adhesive, tape, gel pads)"],cols=2))
    section(st,"How Did You Hear About Us?")
    st.append(cb_row(["Instagram","Facebook","Google","Walk-in","Referral","Other"],cols=3))
    st.append(Spacer(1,8)); st.append(Paragraph("I confirm the information above is accurate and complete.",S()["Body"])); st.append(Spacer(1,4)); sig_block(st)
    doc.build(st); return path

def form_03():
    doc,path=make_doc("03_Aftercare_Instructions.pdf","Aftercare Instructions"); st=[]; page_header(st,"Aftercare Instructions"); s=S()
    st.append(Paragraph("<i>Proper aftercare keeps your lashes looking full and extends the life of your extensions.</i>",s["Body"]))
    section(st,"First 24 Hours")
    for t in ["Avoid getting lashes wet for 24 hours after application.","Do not touch, rub, or pull at your lash extensions.","Avoid steam, saunas, and hot showers (direct steam on face).","Do not apply mascara or eyeliner to the lash line.","Sleep on your back or side to avoid crushing lashes."]:
        st.append(Paragraph(f"&bull;  {t}",s["Body"]))
    section(st,"Ongoing Maintenance")
    for t in ["Gently brush lashes daily with a clean spoolie.","Cleanse lash line daily with an oil-free lash cleanser.","Avoid oil-based products near the eye area (makeup remover, moisturiser).","Do not use waterproof mascara or mechanical eyelash curlers.","Book infill appointments every 2-3 weeks to maintain fullness."]:
        st.append(Paragraph(f"&bull;  {t}",s["Body"]))
    section(st,"What to Avoid")
    for t in ["Pulling, picking, or attempting to remove extensions yourself.","Oil-based cleansers, serums, or makeup removers near eyes.","Rubbing eyes or sleeping face-down on the pillow.","Cotton pads or cotton buds near extensions (fibres catch on lashes)."]:
        st.append(Paragraph(f"<font color='#1A1A1A'>&times;</font>  {t}",s["Body"]))
    section(st,"Warning Signs — Contact Us If:")
    for t in ["Persistent redness, itching, or swelling around the eyes","Allergic reaction (swollen lids, burning sensation)","Excessive lash shedding or bald patches","Pain or discomfort when blinking"]:
        st.append(Paragraph(f"<font color='#1A1A1A'><b>!</b></font>  {t}",s["Body"]))
    st.append(Spacer(1,8)); st.append(gold_divider()); st.append(field2("Your Technician","Date")); st.append(field2("Salon Phone","Salon Email"))
    doc.build(st); return path

def form_04():
    doc,path=make_doc("04_Invoice.pdf","Invoice"); st=[]; page_header(st,"Invoice"); s=S()
    st.append(field2("Invoice No","Date")); st.append(Spacer(1,3))
    section(st,"Salon Details"); st.append(field("Salon Name")); st.append(field("Address")); st.append(field2("Phone","Email"))
    section(st,"Client Details"); st.append(field("Client Name")); st.append(field2("Phone / Email","Address"))
    section(st,"Services Rendered")
    td=[["Description","Qty","Rate","Amount"]]+[["","","",""] for _ in range(5)]
    t=Table(td,colWidths=[CONTENT_W*0.48,CONTENT_W*0.14,CONTENT_W*0.19,CONTENT_W*0.19])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),DARK),("TEXTCOLOR",(0,0),(-1,0),white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,0),9),("FONTNAME",(0,1),(-1,-1),"Helvetica"),("FONTSIZE",(0,1),(-1,-1),9),("GRID",(0,0),(-1,-1),0.5,GOLD),("ROWBACKGROUNDS",(0,1),(-1,-1),[white,LIGHT_GRAY]),("ALIGN",(1,0),(-1,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
    st.append(t)
    tt=Table([["","","Subtotal:",""],["","","Products:",""],["","","Tax:",""],["","","TOTAL DUE:",""]],colWidths=[CONTENT_W*0.48,CONTENT_W*0.14,CONTENT_W*0.19,CONTENT_W*0.19])
    tt.setStyle(TableStyle([("FONTNAME",(2,0),(2,-1),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),10),("ALIGN",(2,0),(-1,-1),"RIGHT"),("LINEABOVE",(2,-1),(-1,-1),1.5,DARK),("TEXTCOLOR",(2,-1),(-1,-1),DARK),("FONTNAME",(2,-1),(-1,-1),"Helvetica-Bold"),("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
    st.append(tt); st.append(Spacer(1,6))
    section(st,"Payment Method"); st.append(cb_row(["Cash","Card","Bank Transfer","PayPal","Other"],cols=5))
    st.append(Spacer(1,4)); st.append(field("Notes")); st.append(Paragraph("Payment is due upon completion of the service unless otherwise agreed.",s["BodySmall"]))
    doc.build(st); return path

def form_05():
    doc,path=make_doc("05_Appointment_Tracker.pdf","Appointment Tracker"); st=[]; page_header(st,"Appointment Tracker")
    section(st,"Client Details"); st.append(field2("Client Name","Phone / Email")); st.append(field("Preferred Service / Usual Treatment")); st.append(field2("Preferred Technician","Frequency"))
    section(st,"Appointment Log")
    hd=["#","Date","Service","Technician","Amount","Paid"]; d=[hd]+[[str(i),"","","","",""] for i in range(1,11)]
    t=Table(d,colWidths=[CONTENT_W*0.06,CONTENT_W*0.14,CONTENT_W*0.26,CONTENT_W*0.22,CONTENT_W*0.14,CONTENT_W*0.18])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),DARK),("TEXTCOLOR",(0,0),(-1,0),white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,0),8),("FONTNAME",(0,1),(-1,-1),"Helvetica"),("FONTSIZE",(0,1),(-1,-1),8),("GRID",(0,0),(-1,-1),0.5,GOLD),("ROWBACKGROUNDS",(0,1),(-1,-1),[white,LIGHT_GRAY]),("ALIGN",(0,0),(0,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
    st.append(t); st.append(Spacer(1,6)); section(st,"Notes")
    for _ in range(2): st.append(Paragraph("_"*85,S()["Body"]))
    doc.build(st); return path

def form_06():
    doc,path=make_doc("06_Photo_Release.pdf","Photo Release Form"); st=[]; page_header(st,"Photo Release Form"); s=S()
    section(st,"Client Information"); st.append(field2("Full Name","Date")); st.append(field2("Phone","Email"))
    section(st,"Consent for Photography & Media Use")
    st.append(Paragraph("I hereby grant the salon, its technicians, and representatives the right to photograph, film, or otherwise capture images of my lash treatment and finished results.",s["Body"]))
    st.append(Spacer(1,3)); st.append(Paragraph("These images may be used for:",s["Body"]))
    for u in ["Portfolio display (physical and digital) for technician and salon promotion","Social media platforms (Instagram, TikTok, Facebook, Pinterest, etc.)","Salon website, marketing materials, and print media","Industry publications, competitions, and exhibitions","Educational and training materials"]:
        st.append(Paragraph(f"&bull;  {u}",s["Body"]))
    section(st,"Terms")
    for i,t in enumerate(["No identifying personal information will be shared alongside images without explicit written consent.","I waive any right to inspect or approve the finished images or the context in which they are used.","I release the salon from any claims arising from the use of these images.","This consent is valid indefinitely unless revoked in writing."],1):
        st.append(Paragraph(f"<b>{i}.</b>  {t}",s["Body"]))
    st.append(Spacer(1,6)); st.append(Paragraph("<b>Please select one:</b>",s["Body"]))
    st.append(cb("I CONSENT to the use of photographs/video as described above.")); st.append(cb("I DO NOT CONSENT to the use of photographs/video."))
    st.append(Spacer(1,10)); st.append(field2("Client Name (Print)","Client Signature")); st.append(field2("Date","Technician Name")); st.append(field("Witness (if applicable)"))
    doc.build(st); return path

def form_07():
    doc,path=make_doc("07_Cancellation_Policy.pdf","Cancellation & Deposit Policy"); st=[]; page_header(st,"Cancellation & Deposit Policy"); s=S()
    section(st,"Deposit Policy")
    for d in ["A deposit is required to secure all lash appointments.","Standard deposit: a minimum of \u00a310 or as agreed at booking.","The deposit is deducted from the final cost on the day of your appointment.","Deposits are non-transferable but may be applied to a rescheduled appointment (see below)."]:
        st.append(Paragraph(f"&bull;  {d}",s["Body"]))
    section(st,"Cancellation Policy")
    cd=[["Notice Period","Consequence"],["More than 24 hours","Deposit transferred to new date (one time only)"],["12-24 hours","50% of deposit forfeited; remainder applied to new booking"],["Less than 12 hours","Full deposit forfeited"],["No-show","Full deposit forfeited; future bookings require deposit upfront"]]
    ct=Table(cd,colWidths=[CONTENT_W*0.30,CONTENT_W*0.70])
    ct.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),DARK),("TEXTCOLOR",(0,0),(-1,0),white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),9),("FONTNAME",(0,1),(-1,-1),"Helvetica"),("GRID",(0,0),(-1,-1),0.5,GOLD),("ROWBACKGROUNDS",(0,1),(-1,-1),[white,LIGHT_GRAY]),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
    st.append(ct)
    section(st,"Rescheduling")
    for r in ["You may reschedule once at no additional cost with more than 24 hours' notice.","A second reschedule will be treated as a cancellation under the policy above.","Rescheduled appointments must be booked within 30 days of the original date."]:
        st.append(Paragraph(f"&bull;  {r}",s["Body"]))
    section(st,"Late Arrivals"); st.append(Paragraph("Arrivals more than 10 minutes late may result in a shortened service or reschedule. Arrivals more than 20 minutes late will be treated as a no-show.",s["Body"]))
    section(st,"Salon Cancellations"); st.append(Paragraph("If the salon cancels or reschedules, your deposit will be fully refunded or transferred to a new date of your choice. We will provide as much notice as possible.",s["Body"]))
    st.append(Spacer(1,10)); st.append(Paragraph("<b>I have read and agree to the Cancellation &amp; Deposit Policy.</b>",S()["Body"]))
    st.append(Spacer(1,4)); st.append(field2("Client Name (Print)","Client Signature")); st.append(field2("Date","Deposit Amount Paid"))
    doc.build(st); return path

def form_08():
    doc,path=make_doc("08_Lash_Style_Request.pdf","Lash Style Request Form"); st=[]; page_header(st,"Lash Style Request Form"); s=S()
    section(st,"Client Information"); st.append(field2("Full Name","Date")); st.append(field2("Phone","Email")); st.append(field("Preferred Technician"))
    section(st,"Style Brief"); st.append(Paragraph("<b>Describe the look you want:</b>",s["Body"]))
    for _ in range(3): st.append(Paragraph("_"*85,s["Body"]))
    section(st,"Lash Style Preferences")
    st.append(cb_row(["Natural","Cat Eye","Doll Eye","Wispy","Kim K","Hybrid","Volume","Mega Volume","Classic","Wet Look","Open Eye","Other"],cols=4))
    section(st,"Details")
    st.append(field("Service Type (classic, hybrid, volume, mega volume, lift & tint, etc.)"))
    st.append(field2("Curl Type (J, B, C, CC, D, L)","Length Range (mm)"))
    st.append(field("Thickness / Diameter Preference"))
    section(st,"Reference Images")
    st.append(Paragraph("Attach or show reference images, screenshots, or inspiration below:",s["Body"]))
    rr=[]
    for i in range(1,4): rr.append(Paragraph(f"<br/><br/><br/><font color='#999999' size='8'>Reference {i}</font>",ParagraphStyle(f"ref{i}",alignment=TA_CENTER,fontSize=8,textColor=MID_GRAY)))
    rt=Table([rr],colWidths=[CONTENT_W/3]*3,rowHeights=[65])
    rt.setStyle(TableStyle([("BOX",(0,0),(0,0),0.8,GOLD),("BOX",(1,0),(1,0),0.8,GOLD),("BOX",(2,0),(2,0),0.8,GOLD),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("ALIGN",(0,0),(-1,-1),"CENTER")]))
    st.append(rt)
    section(st,"Additional Notes")
    for _ in range(2): st.append(Paragraph("_"*85,s["Body"]))
    st.append(Spacer(1,6)); sig_block(st)
    doc.build(st); return path

def main():
    os.makedirs(OUTPUT_DIR,exist_ok=True)
    for gen in [form_01,form_02,form_03,form_04,form_05,form_06,form_07,form_08]:
        p=gen(); print(f"  Created: {os.path.basename(p)}")
    print(f"\nAll 8 forms generated in {OUTPUT_DIR}")

if __name__=="__main__": main()
