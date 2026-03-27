#!/usr/bin/env python3
"""
Dog Training & Puppy School Mega Bundle — Full Build + Publish Pipeline
35 templates. Navy #1B3A5C, gold #C9A96E, cream #F5F0E8, charcoal #1A1A1A
"""
import json, os, sys, time, uuid, urllib.request, urllib.error, urllib.parse
from pathlib import Path
from PIL import Image, ImageDraw
import boto3
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.pagesizes import A4 as RL_A4
from reportlab.lib import colors
from dotenv import load_dotenv

PROJECT = Path("/root/NEW-AI-PROJECT")
sys.path.insert(0, str(PROJECT / "scripts"))
load_dotenv(PROJECT / ".env")
load_dotenv(PROJECT / "purpleocaz-canva-mcp/.env", override=False)

from dog_training_design_system import (
    NAVY, GOLD, CREAM, CHARCOAL, WHITE, CREAM_ALT, NAVY_DARK,
    A4 as PIL_A4, BCARD, GIFT_CERT, SOCIAL, LISTING_IMG,
    font, centred, right, gold_rule, navy_bar, section_head,
    field_line, field_pair, field_triple, checkbox, table_row,
    paw_print, a4_header, a4_footer, upload_to_spaces,
)

OUT     = PROJECT / "outputs" / "dog-training"
TMPL    = OUT / "templates"
LISTING = OUT / "listing"
for d in [TMPL, LISTING]:
    d.mkdir(parents=True, exist_ok=True)

CDN        = "https://purpleocaz-assets.lon1.digitaloceanspaces.com"
TOKEN_FILE = PROJECT / "workflows" / "etsy_analytics" / "etsy_tokens.json"
ETSY_BASE  = "https://openapi.etsy.com/v3/application"
API_KEY    = os.getenv("ETSY_API_KEYSTRING", "")
SECRET     = os.getenv("ETSY_SHARED_SECRET", "")
SHOP_ID    = os.getenv("ETSY_SHOP_ID", "34071205")
X_API_KEY  = f"{API_KEY}:{SECRET}"
NICHE, PFX = "dog-training", "DT"
W = H = 3000


# ── Etsy helpers ──────────────────────────────────────────────────────────────

def load_tokens():
    with open(TOKEN_FILE) as f: return json.load(f)

def etsy_request(method, path, body=None, content_type="application/x-www-form-urlencoded", retries=2):
    tokens = load_tokens()
    data = body.encode() if isinstance(body, str) else body
    req = urllib.request.Request(f"{ETSY_BASE}{path}", data=data, method=method)
    req.add_header("x-api-key", X_API_KEY)
    req.add_header("Authorization", f"Bearer {tokens['access_token']}")
    if body and content_type:
        req.add_header("Content-Type", content_type)
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read(); return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        body_str = e.read().decode()
        if e.code == 401 and retries:
            time.sleep(2); return etsy_request(method, path, body, content_type, retries-1)
        raise RuntimeError(f"Etsy {method} {path} → {e.code}: {body_str}")

def upload_image_to_etsy(listing_id, img_path, rank):
    tokens = load_tokens(); boundary = uuid.uuid4().hex
    img_data = open(img_path,"rb").read()
    body  = f"--{boundary}\r\nContent-Disposition: form-data; name=\"rank\"\r\n\r\n{rank}\r\n".encode()
    body += f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{img_path.name}\"\r\nContent-Type: image/png\r\n\r\n".encode()
    body += img_data + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(f"{ETSY_BASE}/shops/{SHOP_ID}/listings/{listing_id}/images", data=body, method="POST")
    req.add_header("x-api-key", X_API_KEY)
    req.add_header("Authorization", f"Bearer {tokens['access_token']}")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    with urllib.request.urlopen(req) as resp: return json.loads(resp.read())

def upload_file_to_etsy(listing_id, pdf_path):
    tokens = load_tokens(); boundary = uuid.uuid4().hex; filename = pdf_path.name
    pdf_data = open(pdf_path,"rb").read()
    body  = f"--{boundary}\r\nContent-Disposition: form-data; name=\"name\"\r\n\r\n{filename}\r\n".encode()
    body += f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{filename}\"\r\nContent-Type: application/pdf\r\n\r\n".encode()
    body += pdf_data + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(f"{ETSY_BASE}/shops/{SHOP_ID}/listings/{listing_id}/files", data=body, method="POST")
    req.add_header("x-api-key", X_API_KEY)
    req.add_header("Authorization", f"Bearer {tokens['access_token']}")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    with urllib.request.urlopen(req) as resp: return json.loads(resp.read())

def save_upload(img, filename, spaces_key):
    path = TMPL / filename; img.save(path, "PNG")
    upload_to_spaces(path, spaces_key); return path


# ══════════════════════════════════════════════════════════════════════════════
# BRANDING (9)
# ══════════════════════════════════════════════════════════════════════════════

def build_business_card_dark():
    W2,H2=BCARD; img=Image.new("RGB",(W2,H2),CHARCOAL); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W2,18],fill=GOLD); d.rectangle([0,H2-18,W2,H2],fill=GOLD)
    d.rectangle([0,18,12,H2-18],fill=NAVY)
    paw_print(d,W2-130,130,size=55,fill=NAVY)
    d.text((60,70),"YOUR BUSINESS NAME",fill=GOLD,font=font(52,bold=True))
    d.text((60,140),"Dog Training & Puppy School",fill=CREAM,font=font(34))
    gold_rule(d,195,x0=60,x1=W2-60,thickness=3)
    d.text((60,215),"yourname@email.com",fill=WHITE,font=font(30))
    d.text((60,260),"07700 000000",fill=WHITE,font=font(30))
    d.text((60,305),"www.yourwebsite.co.uk",fill=WHITE,font=font(30))
    d.text((60,370),"APDT Member  |  Fully Insured",fill=GOLD,font=font(28,bold=True))
    return save_upload(img,f"{PFX}_Business_Card_Dark.png",f"templates/{NICHE}/branding/{PFX}_Business_Card_Dark.png")

def build_business_card_light():
    W2,H2=BCARD; img=Image.new("RGB",(W2,H2),CREAM); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W2,18],fill=NAVY); d.rectangle([0,H2-18,W2,H2],fill=NAVY)
    d.rectangle([0,18,12,H2-18],fill=GOLD)
    paw_print(d,W2-130,130,size=55,fill=NAVY)
    d.text((60,70),"YOUR BUSINESS NAME",fill=NAVY,font=font(52,bold=True))
    d.text((60,140),"Dog Training & Puppy School",fill=CHARCOAL,font=font(34))
    gold_rule(d,195,x0=60,x1=W2-60,thickness=3)
    d.text((60,215),"yourname@email.com",fill=CHARCOAL,font=font(30))
    d.text((60,260),"07700 000000",fill=CHARCOAL,font=font(30))
    d.text((60,305),"www.yourwebsite.co.uk",fill=CHARCOAL,font=font(30))
    d.text((60,370),"APDT Member  |  Fully Insured",fill=NAVY,font=font(28,bold=True))
    return save_upload(img,f"{PFX}_Business_Card_Light.png",f"templates/{NICHE}/branding/{PFX}_Business_Card_Light.png")

def build_appointment_card_dark():
    W2,H2=BCARD; img=Image.new("RGB",(W2,H2),CHARCOAL); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W2,18],fill=GOLD); d.rectangle([0,H2-18,W2,H2],fill=GOLD)
    d.rectangle([0,18,12,H2-18],fill=NAVY)
    d.text((60,55),"YOUR BUSINESS NAME",fill=GOLD,font=font(42,bold=True))
    d.text((60,110),"SESSION CONFIRMED",fill=WHITE,font=font(36,bold=True))
    gold_rule(d,158,x0=60,x1=W2-60,thickness=3)
    for label,yy in [("Date:",175),("Time:",218),("Session type:",261),("Trainer:",304)]:
        d.text((60,yy),label,fill=CREAM,font=font(30,bold=True))
        d.rectangle([60+len(label)*18,yy+23,700,yy+25],fill=GOLD)
    d.text((60,370),"Contact: 07700 000000",fill=GOLD,font=font(28))
    paw_print(d,W2-120,H2//2,size=50,fill=NAVY)
    return save_upload(img,f"{PFX}_Appointment_Card_Dark.png",f"templates/{NICHE}/branding/{PFX}_Appointment_Card_Dark.png")

def build_appointment_card_light():
    W2,H2=BCARD; img=Image.new("RGB",(W2,H2),CREAM); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W2,18],fill=NAVY); d.rectangle([0,H2-18,W2,H2],fill=NAVY)
    d.rectangle([0,18,12,H2-18],fill=GOLD)
    d.text((60,55),"YOUR BUSINESS NAME",fill=NAVY,font=font(42,bold=True))
    d.text((60,110),"SESSION CONFIRMED",fill=CHARCOAL,font=font(36,bold=True))
    gold_rule(d,158,x0=60,x1=W2-60,thickness=3)
    for label,yy in [("Date:",175),("Time:",218),("Session type:",261),("Trainer:",304)]:
        d.text((60,yy),label,fill=CHARCOAL,font=font(30,bold=True))
        d.rectangle([60+len(label)*18,yy+23,700,yy+25],fill=NAVY)
    d.text((60,370),"Contact: 07700 000000",fill=NAVY,font=font(28))
    paw_print(d,W2-120,H2//2,size=50,fill=GOLD)
    return save_upload(img,f"{PFX}_Appointment_Card_Light.png",f"templates/{NICHE}/branding/{PFX}_Appointment_Card_Light.png")

def build_loyalty_card():
    W2,H2=BCARD; img=Image.new("RGB",(W2,H2),CREAM); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W2,18],fill=NAVY); d.rectangle([0,H2-18,W2,H2],fill=NAVY)
    centred(d,35,"LOYALTY REWARD CARD",NAVY,font(40,bold=True),canvas_w=W2)
    centred(d,85,"5th Session FREE!",GOLD,font(34,bold=True),canvas_w=W2)
    gold_rule(d,130,x0=60,x1=W2-60,thickness=3)
    spacing=(W2-120)//5
    for i in range(5):
        bx=60+i*spacing
        d.rectangle([bx+10,155,bx+spacing-20,355],outline=NAVY,width=3)
        paw_print(d,bx+(spacing-20)//2+10,255,size=40,fill=CREAM_ALT)
        centred(d,320,str(i+1),CHARCOAL,font(28),canvas_w=spacing)
    d.text((60,380),"Client: _________________________",fill=CHARCOAL,font=font(28))
    d.text((60,425),"Phone:  _________________________",fill=CHARCOAL,font=font(28))
    d.text((60,470),"YOUR BUSINESS NAME",fill=NAVY,font=font(26,bold=True))
    d.text((60,505),"07700 000000",fill=CHARCOAL,font=font(26))
    return save_upload(img,f"{PFX}_Loyalty_Card.png",f"templates/{NICHE}/branding/{PFX}_Loyalty_Card.png")

def build_gift_certificate():
    W2,H2=GIFT_CERT; img=Image.new("RGB",(W2,H2),CREAM); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W2,40],fill=NAVY); d.rectangle([0,H2-40,W2,H2],fill=NAVY)
    d.rectangle([0,40,40,H2-40],fill=NAVY); d.rectangle([W2-40,40,W2,H2-40],fill=NAVY)
    d.rectangle([55,55,W2-55,H2-55],outline=GOLD,width=4)
    paw_print(d,110,150,size=50,fill=GOLD); paw_print(d,W2-110,150,size=50,fill=GOLD)
    paw_print(d,110,H2-150,size=50,fill=GOLD); paw_print(d,W2-110,H2-150,size=50,fill=GOLD)
    centred(d,90,"GIFT CERTIFICATE",NAVY,font(90,bold=True),canvas_w=W2)
    gold_rule(d,210,x0=100,x1=W2-100,thickness=4)
    centred(d,235,"Dog Training & Puppy School Services",CHARCOAL,font(52),canvas_w=W2)
    gold_rule(d,310,x0=100,x1=W2-100,thickness=4)
    centred(d,360,"This certificate entitles",CHARCOAL,font(44),canvas_w=W2)
    d.rectangle([300,450,W2-300,453],fill=NAVY)
    centred(d,465,"(Recipient Name)",CHARCOAL,font(34),canvas_w=W2)
    centred(d,530,"to a",CHARCOAL,font(44),canvas_w=W2)
    d.rectangle([300,600,W2-300,603],fill=NAVY)
    centred(d,615,"(Session / Package / Value)",CHARCOAL,font(34),canvas_w=W2)
    centred(d,680,"provided by",CHARCOAL,font(40),canvas_w=W2)
    centred(d,740,"YOUR BUSINESS NAME",NAVY,font(64,bold=True),canvas_w=W2)
    gold_rule(d,840,x0=100,x1=W2-100,thickness=3)
    d.text((150,890),"Valid until: _________________",CHARCOAL,font=font(38))
    d.text((150,945),"Certificate #: _______________",CHARCOAL,font=font(38))
    right(d,W2-150,890,"Signed: _________________",CHARCOAL,font(38))
    right(d,W2-150,945,"Date:   _________________",CHARCOAL,font(38))
    centred(d,1030,"07700 000000  |  www.yourwebsite.co.uk",CHARCOAL,font(36),canvas_w=W2)
    centred(d,1080,"APDT Member  |  Fully Insured",NAVY,font(32,bold=True),canvas_w=W2)
    return save_upload(img,f"{PFX}_Gift_Certificate.png",f"templates/{NICHE}/branding/{PFX}_Gift_Certificate.png")

def build_welcome_sign():
    W2,H2=PIL_A4; img=Image.new("RGB",(W2,H2),CREAM); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W2,340],fill=NAVY); d.rectangle([0,H2-180,W2,H2],fill=NAVY)
    gold_rule(d,340,thickness=10,canvas_w=W2); gold_rule(d,H2-180,thickness=10,canvas_w=W2)
    paw_print(d,160,170,size=80,fill=GOLD); paw_print(d,W2-160,170,size=80,fill=GOLD)
    centred(d,55,"WELCOME!", WHITE, font(120,bold=True),canvas_w=W2)
    centred(d,195,"YOUR BUSINESS NAME",GOLD,font(60,bold=True),canvas_w=W2)
    centred(d,270,"Dog Training & Puppy School",CREAM,font(44),canvas_w=W2)
    centred(d,395,"We're so excited to be training your dog!", CHARCOAL,font(52),canvas_w=W2)
    gold_rule(d,480,x0=120,x1=W2-120,thickness=4)
    y=520
    for line in ["Your Name:","Dog's Name:","Contact Number:","Emergency Contact:","Vet Practice:"]:
        d.text((120,y),line,CHARCOAL,font=font(42,bold=True))
        d.rectangle([120,y+58,W2-120,y+62],fill=NAVY); y+=120
    gold_rule(d,H2-240,x0=120,x1=W2-120,thickness=4)
    centred(d,H2-210,"APDT Member  |  Fully Insured  |  07700 000000",WHITE,font(38),canvas_w=W2)
    centred(d,H2-155,"www.yourwebsite.co.uk",GOLD,font(36),canvas_w=W2)
    centred(d,H2-100,"© PurpleOcaz — purpleocaz.etsy.com",CREAM,font(30),canvas_w=W2)
    return save_upload(img,f"{PFX}_Welcome_Sign.png",f"templates/{NICHE}/branding/{PFX}_Welcome_Sign.png")

def build_thank_you_card():
    W2,H2=BCARD; img=Image.new("RGB",(W2,H2),NAVY); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W2,16],fill=GOLD); d.rectangle([0,H2-16,W2,H2],fill=GOLD)
    paw_print(d,W2-110,100,size=48,fill=GOLD)
    centred(d,38,"THANK YOU!",GOLD,font(70,bold=True),canvas_w=W2)
    centred(d,128,"for training with us.",CREAM,font(32),canvas_w=W2)
    gold_rule(d,175,x0=60,x1=W2-60,thickness=3)
    centred(d,195,"Keep practising your homework —",WHITE,font(28),canvas_w=W2)
    centred(d,235,"consistency is the key to great results!",CREAM,font(26),canvas_w=W2)
    gold_rule(d,280,x0=60,x1=W2-60,thickness=3)
    d.text((60,300),"YOUR BUSINESS NAME",fill=GOLD,font=font(32,bold=True))
    d.text((60,345),"07700 000000",fill=CREAM,font=font(28))
    d.text((60,385),"www.yourwebsite.co.uk",fill=CREAM,font=font(28))
    d.text((60,430),"APDT Member  |  Fully Insured",fill=GOLD,font=font(26,bold=True))
    return save_upload(img,f"{PFX}_Thank_You_Card.png",f"templates/{NICHE}/branding/{PFX}_Thank_You_Card.png")

def build_referral_card():
    W2,H2=BCARD; img=Image.new("RGB",(W2,H2),CHARCOAL); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W2,16],fill=NAVY); d.rectangle([0,H2-16,W2,H2],fill=NAVY)
    paw_print(d,W2-110,110,size=48,fill=NAVY)
    centred(d,32,"REFER A FRIEND",GOLD,font(60,bold=True),canvas_w=W2)
    centred(d,105,"& EARN A FREE SESSION!",WHITE,font(38,bold=True),canvas_w=W2)
    gold_rule(d,158,x0=60,x1=W2-60,thickness=3)
    centred(d,178,"Refer a friend who books 4+ sessions",CREAM,font(26),canvas_w=W2)
    centred(d,212,"and YOU get a FREE training session!",CREAM,font(26),canvas_w=W2)
    gold_rule(d,256,x0=60,x1=W2-60,thickness=3)
    d.text((60,276),"Referred by:",fill=CREAM,font=font(28,bold=True))
    d.rectangle([240,300,700,303],fill=GOLD)
    d.text((60,325),"Referee name:",fill=CREAM,font=font(28,bold=True))
    d.rectangle([280,350,700,353],fill=GOLD)
    d.text((60,372),"YOUR BUSINESS NAME",fill=NAVY,font=font(30,bold=True))
    d.text((60,412),"07700 000000",fill=GOLD,font=font(28))
    d.text((60,452),"Ts&Cs apply.",fill=WHITE,font=font(24))
    return save_upload(img,f"{PFX}_Referral_Card.png",f"templates/{NICHE}/branding/{PFX}_Referral_Card.png")


# ══════════════════════════════════════════════════════════════════════════════
# MARKETING (8)
# ══════════════════════════════════════════════════════════════════════════════

def build_flyer_group_classes():
    W2,H2=PIL_A4; img=Image.new("RGB",(W2,H2),CREAM); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W2,480],fill=NAVY); d.rectangle([0,H2-160,W2,H2],fill=NAVY)
    gold_rule(d,480,thickness=10,canvas_w=W2); gold_rule(d,H2-160,thickness=10,canvas_w=W2)
    paw_print(d,140,240,size=90,fill=GOLD); paw_print(d,W2-140,240,size=90,fill=GOLD)
    centred(d,55,"YOUR BUSINESS NAME",GOLD,font(72,bold=True),canvas_w=W2)
    centred(d,155,"GROUP TRAINING CLASSES",CREAM,font(58,bold=True),canvas_w=W2)
    centred(d,245,"APDT Member  |  Force-Free Methods  |  Fully Insured",WHITE,font(38),canvas_w=W2)
    centred(d,315,"Serving [Your Area]",CREAM,font(36),canvas_w=W2)
    y=530
    classes=[
        ("Puppy Foundation (8 wks)","For pups aged 8–16 weeks. Socialisation, sit, down, recall."),
        ("Beginner Obedience","Basic manners: loose lead, sit, stay, leave it."),
        ("Intermediate Skills","Building reliability: distance, duration, distraction."),
        ("Advanced Obedience","Off-lead work, complex commands, real-world scenarios."),
        ("Reactive Dog Workshop","Specialist class — limited spaces, calm environment."),
    ]
    for name,desc in classes:
        d.rectangle([80,y,W2-80,y+145],fill=WHITE,outline=GOLD,width=2)
        paw_print(d,145,y+72,size=30,fill=NAVY)
        d.text((210,y+20),name,fill=NAVY,font=font(48,bold=True))
        d.text((210,y+82),desc,fill=CHARCOAL,font=font(34))
        y+=160
    gold_rule(d,y+10,x0=80,x1=W2-80,thickness=4)
    centred(d,y+30,"Classes run weekly — book your free assessment today!",CHARCOAL,font(40,bold=True),canvas_w=W2)
    centred(d,H2-130,"07700 000000  |  www.yourwebsite.co.uk",CREAM,font(38),canvas_w=W2)
    centred(d,H2-80,"© PurpleOcaz — purpleocaz.etsy.com",CREAM,font(28),canvas_w=W2)
    return save_upload(img,f"{PFX}_Flyer_Group_Classes.png",f"templates/{NICHE}/marketing/{PFX}_Flyer_Group_Classes.png")

def build_flyer_1to1():
    W2,H2=PIL_A4; img=Image.new("RGB",(W2,H2),CHARCOAL); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W2,420],fill=NAVY); d.rectangle([0,H2-160,W2,H2],fill=NAVY)
    gold_rule(d,420,thickness=10,canvas_w=W2); gold_rule(d,H2-160,thickness=10,canvas_w=W2)
    paw_print(d,W2-160,210,size=80,fill=GOLD)
    centred(d,55,"1-TO-1 TRAINING",GOLD,font(90,bold=True),canvas_w=W2)
    centred(d,170,"YOUR BUSINESS NAME",CREAM,font(52),canvas_w=W2)
    centred(d,248,"Tailored to your dog. At your pace.",WHITE,font(44),canvas_w=W2)
    centred(d,310,"APDT Member  |  Force-Free  |  Fully Insured",GOLD,font(34),canvas_w=W2)
    d.rectangle([80,460,W2-80,680],fill=NAVY,outline=GOLD,width=4)
    centred(d,490,"FIRST SESSION",GOLD,font(68,bold=True),canvas_w=W2)
    centred(d,570,"HALF PRICE!",WHITE,font(90,bold=True),canvas_w=W2)
    centred(d,660,"Mention this flyer when booking",CREAM,font(36),canvas_w=W2)
    y=720
    for b in ["✔  In-home sessions — train where the problems actually happen",
              "✔  Reactive, anxious, or over-excited dogs welcome",
              "✔  Separation anxiety, lead pulling, recall — any issue",
              "✔  Written homework plan after every session",
              "✔  WhatsApp support between sessions"]:
        d.text((120,y),b,fill=WHITE,font=font(38)); y+=68
    gold_rule(d,y+20,x0=80,x1=W2-80,thickness=4)
    centred(d,y+50,"Message us today — limited spaces available!",GOLD,font(40,bold=True),canvas_w=W2)
    centred(d,H2-130,"07700 000000  |  www.yourwebsite.co.uk",CREAM,font(38),canvas_w=W2)
    centred(d,H2-80,"© PurpleOcaz — purpleocaz.etsy.com",CREAM,font(28),canvas_w=W2)
    return save_upload(img,f"{PFX}_Flyer_1to1.png",f"templates/{NICHE}/marketing/{PFX}_Flyer_1to1.png")

def build_price_list():
    W2,H2=PIL_A4; img=Image.new("RGB",(W2,H2),CREAM); d=ImageDraw.Draw(img)
    y=a4_header(img,d,"SERVICES & PRICE LIST","Dog Training & Puppy School")
    y=section_head(d,80,y,"GROUP CLASSES",width=W2-160,canvas_w=W2); y+=10
    hdr=["Class","Duration","Per session","Block (6)"]
    wids=[700,360,480,480]
    y=table_row(d,80,y,hdr,wids,header=True)
    for i,row in enumerate([
        ("Puppy Foundation","50 min","£XX.00","£XX.00"),
        ("Beginner Obedience","50 min","£XX.00","£XX.00"),
        ("Intermediate","50 min","£XX.00","£XX.00"),
        ("Advanced","50 min","£XX.00","£XX.00"),
        ("Reactive Dog Workshop","60 min","£XX.00","N/A"),
    ]):
        y=table_row(d,80,y,row,wids,alt=bool(i%2))
    y+=20
    y=section_head(d,80,y,"1-TO-1 SESSIONS",width=W2-160,canvas_w=W2); y+=10
    wids2=[840,540,740]
    y=table_row(d,80,y,["Session","Duration","Price"],wids2,header=True)
    for i,row in enumerate([
        ("Initial Assessment","60 min","£XX.00"),
        ("Standard Session","45 min","£XX.00"),
        ("Extended Session","90 min","£XX.00"),
        ("Block of 4 sessions","45 min ea.","£XX.00"),
        ("Block of 8 sessions","45 min ea.","£XX.00"),
    ]):
        y=table_row(d,80,y,row,wids2,alt=bool(i%2))
    y+=20
    y=section_head(d,80,y,"PACKAGES",width=W2-160,canvas_w=W2); y+=10
    y=table_row(d,80,y,["Package","Includes","Price"],[700,920,500],header=True)
    for i,row in enumerate([
        ("Puppy Starter","6 group classes + 1x 1-to-1","£XX.00"),
        ("Total Transformation","8x 1-to-1 sessions + progress report","£XX.00"),
    ]):
        y=table_row(d,80,y,row,[700,920,500],alt=bool(i%2),row_h=85)
    y+=20
    d.text((80,y),"* All prices editable. Free assessment before any 1-to-1 package.",fill=CHARCOAL,font=font(30))
    a4_footer(d,W2,H2)
    return save_upload(img,f"{PFX}_Price_List.png",f"templates/{NICHE}/marketing/{PFX}_Price_List.png")

def _social_base(bg,accent):
    S=SOCIAL[0]; img=Image.new("RGB",SOCIAL,bg); d=ImageDraw.Draw(img)
    d.rectangle([0,0,S,16],fill=accent); d.rectangle([0,S-16,S,S],fill=accent)
    d.rectangle([0,16,16,S-16],fill=accent); d.rectangle([S-16,16,S,S-16],fill=accent)
    return img,d,S

def build_social_booking():
    img,d,S=_social_base(NAVY,GOLD)
    paw_print(d,S-100,100,size=55,fill=GOLD); paw_print(d,100,S-100,size=40,fill=GOLD)
    centred(d,80,"CLASSES NOW BOOKING",GOLD,font(72,bold=True),canvas_w=S)
    centred(d,170,"Spaces are filling fast!",WHITE,font(52),canvas_w=S)
    gold_rule(d,255,x0=80,x1=S-80,thickness=5)
    for txt in ["Puppy Foundation","Beginner & Intermediate","Advanced & Reactive"]:
        centred(d,295+(["Puppy Foundation","Beginner & Intermediate","Advanced & Reactive"].index(txt))*65,txt,CREAM,font(46),canvas_w=S)
    d.rectangle([80,525,S-80,670],fill=GOLD,outline=WHITE,width=3)
    centred(d,555,"FREE Assessment Session",NAVY,font(58,bold=True),canvas_w=S)
    centred(d,625,"Book yours today →",CHARCOAL,font(46,bold=True),canvas_w=S)
    centred(d,720,"YOUR BUSINESS NAME",GOLD,font(52,bold=True),canvas_w=S)
    centred(d,785,"APDT Member  |  Force-Free",WHITE,font(40),canvas_w=S)
    centred(d,850,"07700 000000",CREAM,font(44),canvas_w=S)
    centred(d,930,"Follow for training tips!",CREAM,font(36),canvas_w=S)
    return save_upload(img,f"{PFX}_Social_Booking.png",f"templates/{NICHE}/marketing/{PFX}_Social_Booking.png")

def build_social_testimonial():
    img,d,S=_social_base(CREAM,NAVY)
    paw_print(d,S//2,115,size=60,fill=NAVY)
    centred(d,195,"\u201cAbsolutely transformed!\u201d",CHARCOAL,font(58,serifbold=True),canvas_w=S)
    gold_rule(d,280,x0=100,x1=S-100,thickness=4)
    centred(d,315,"\u201cBuddy used to pull like a train and bark",CHARCOAL,font(40,serif=True),canvas_w=S)
    centred(d,370,"at every dog. After 6 sessions he walks",CHARCOAL,font(40,serif=True),canvas_w=S)
    centred(d,425,"calmly past anything. Incredible!\u201d",CHARCOAL,font(40,serif=True),canvas_w=S)
    gold_rule(d,505,x0=100,x1=S-100,thickness=4)
    centred(d,540,"— James & Buddy, Happy Client",NAVY,font(40,bold=True),canvas_w=S)
    d.rectangle([80,635,S-80,655],fill=GOLD)
    centred(d,685,"\u2b50\u2b50\u2b50\u2b50\u2b50  5-Star Review",CHARCOAL,font(44,bold=True),canvas_w=S)
    d.rectangle([80,775,S-80,895],fill=NAVY)
    centred(d,808,"YOUR BUSINESS NAME",GOLD,font(54,bold=True),canvas_w=S)
    centred(d,860,"Dog Training & Puppy School",WHITE,font(38),canvas_w=S)
    centred(d,940,"07700 000000  |  APDT Member",CHARCOAL,font(34),canvas_w=S)
    return save_upload(img,f"{PFX}_Social_Testimonial.png",f"templates/{NICHE}/marketing/{PFX}_Social_Testimonial.png")

def build_social_training_tip():
    img,d,S=_social_base(CHARCOAL,GOLD)
    paw_print(d,120,120,size=55,fill=NAVY)
    centred(d,60,"TRAINING TIP OF THE WEEK",GOLD,font(54,bold=True),canvas_w=S)
    gold_rule(d,150,x0=60,x1=S-60,thickness=5)
    centred(d,185,"#1: The 3Ds of Dog Training",WHITE,font(62,bold=True),canvas_w=S)
    centred(d,268,"To get reliable behaviour you must",CREAM,font(42),canvas_w=S)
    centred(d,323,"train across three dimensions:",CREAM,font(42),canvas_w=S)
    for i,(title,desc) in enumerate([
        ("DURATION","How long can they hold the behaviour?"),
        ("DISTANCE","How far away can you be?"),
        ("DISTRACTION","Can they do it with the world going on?"),
    ]):
        y=400+i*130
        d.rectangle([60,y,S-60,y+115],fill=NAVY,outline=GOLD,width=2)
        d.text((90,y+14),title,fill=GOLD,font=font(48,bold=True))
        d.text((90,y+68),desc,fill=CREAM,font=font(36))
    d.rectangle([60,800,S-60,920],fill=GOLD)
    centred(d,832,"Work on one D at a time!",NAVY,font(58,bold=True),canvas_w=S)
    centred(d,960,"YOUR BUSINESS NAME",GOLD,font(50,bold=True),canvas_w=S)
    centred(d,1018,"07700 000000",CREAM,font(40),canvas_w=S)
    return save_upload(img,f"{PFX}_Social_Training_Tip.png",f"templates/{NICHE}/marketing/{PFX}_Social_Training_Tip.png")

def build_social_before_after():
    img,d,S=_social_base(CREAM,NAVY)
    d.rectangle([0,0,S,130],fill=NAVY)
    paw_print(d,80,65,size=45,fill=GOLD); paw_print(d,S-80,65,size=45,fill=GOLD)
    centred(d,22,"BEFORE & AFTER TRAINING",GOLD,font(62,bold=True),canvas_w=S)
    centred(d,92,"Real results from real clients",WHITE,font(40),canvas_w=S)
    # Two columns
    mid=S//2
    d.rectangle([40,155,mid-20,640],fill=CREAM_ALT,outline=NAVY,width=3)
    d.rectangle([mid+20,155,S-40,640],fill=NAVY,outline=GOLD,width=3)
    centred(d,175,"BEFORE",CHARCOAL,font(56,bold=True),canvas_w=mid-60)
    d.rectangle([40,230,mid-20,235],fill=GOLD)
    before=["Pulling on lead","Jumping up","Ignoring recall","Barking at dogs","Can't sit still"]
    y=250
    for txt in before:
        d.text((60,y),"✗  "+txt,fill=CHARCOAL,font=font(38)); y+=58
    tx=mid+40
    centred(d,175,"AFTER",GOLD,font(56,bold=True),canvas_w=mid-60)
    d.rectangle([mid+20,230,S-40,235],fill=GOLD)
    after=["Walks nicely","Four paws on floor","Solid recall","Calm & focused","Rock-solid sit-stay"]
    y=250
    for txt in after:
        d.text((tx,y),"✓  "+txt,fill=WHITE,font=font(38)); y+=58
    gold_rule(d,660,x0=40,x1=S-40,thickness=5)
    centred(d,690,"Add your own before/after story here!",CHARCOAL,font(40),canvas_w=S)
    centred(d,760,"[Replace with your client's photo]",CHARCOAL,font(36),canvas_w=S)
    d.rectangle([80,850,S-80,980],fill=NAVY)
    centred(d,882,"YOUR BUSINESS NAME",GOLD,font(52,bold=True),canvas_w=S)
    centred(d,934,"Dog Training & Puppy School",WHITE,font(38),canvas_w=S)
    centred(d,1010,"07700 000000  |  Force-Free Methods",CHARCOAL,font(36),canvas_w=S)
    return save_upload(img,f"{PFX}_Social_Before_After.png",f"templates/{NICHE}/marketing/{PFX}_Social_Before_After.png")

def build_social_puppy_promo():
    img,d,S=_social_base(NAVY,GOLD)
    paw_print(d,S-120,120,size=65,fill=GOLD); paw_print(d,120,S-120,size=50,fill=GOLD)
    centred(d,60,"PUPPY SCHOOL",GOLD,font(90,bold=True),canvas_w=S)
    centred(d,165,"NOW ENROLLING",WHITE,font(68,bold=True),canvas_w=S)
    gold_rule(d,255,x0=80,x1=S-80,thickness=5)
    centred(d,290,"For pups aged 8–16 weeks",CREAM,font(46),canvas_w=S)
    centred(d,350,"The critical socialisation window — don't miss it!",CREAM,font(40),canvas_w=S)
    d.rectangle([80,420,S-80,660],fill=GOLD)
    centred(d,445,"What puppies learn:",CHARCOAL,font(52,bold=True),canvas_w=S)
    for i,txt in enumerate(["Sit, down, stand & stay","Name recall & focus",
                             "Loose lead foundations","Bite inhibition & socialisation"]):
        centred(d,510+i*52,"✓  "+txt,CHARCOAL,font(38),canvas_w=S)
    gold_rule(d,685,x0=80,x1=S-80,thickness=5)
    centred(d,720,"Places strictly limited — 6 puppies max",CREAM,font(44),canvas_w=S)
    centred(d,790,"YOUR BUSINESS NAME",GOLD,font(56,bold=True),canvas_w=S)
    centred(d,858,"07700 000000",WHITE,font(48),canvas_w=S)
    centred(d,940,"Register today — classes fill fast!",GOLD,font(44,bold=True),canvas_w=S)
    return save_upload(img,f"{PFX}_Social_Puppy_Promo.png",f"templates/{NICHE}/marketing/{PFX}_Social_Puppy_Promo.png")


# ══════════════════════════════════════════════════════════════════════════════
# CLIENT FORMS (9)
# ══════════════════════════════════════════════════════════════════════════════

def build_training_agreement():
    W2,H2=PIL_A4; img=Image.new("RGB",(W2,H2),WHITE); d=ImageDraw.Draw(img)
    y=a4_header(img,d,"TRAINING AGREEMENT")
    y=section_head(d,80,y+10,"CLIENT & DOG DETAILS",width=W2-160); y+=14
    y=field_pair(d,120,y,"Client Full Name:","Phone:",total_w=2240)
    y=field_pair(d,120,y,"Email Address:","Address:",total_w=2240)
    y=field_pair(d,120,y,"Dog's Name:","Breed / Age:",total_w=2240)
    y=field_pair(d,120,y,"Vet Name:","Vet Phone:",total_w=2240)
    y=field_line(d,120,y,"Known health issues / medications:",width=2240)
    y+=8
    y=section_head(d,80,y,"SERVICE SELECTED",width=W2-160); y+=14
    y=field_pair(d,120,y,"Service / Package:","Start date:",total_w=2240)
    y=field_pair(d,120,y,"Number of sessions:","Fee agreed: £",total_w=2240)
    y+=8
    y=section_head(d,80,y,"AGREEMENT TERMS",width=W2-160); y+=14
    for term in [
        "Client confirms their dog is vaccinated, flea-treated and in good health.",
        "Trainer uses force-free, reward-based methods only.",
        "24-hour cancellation notice required. Late cancellations charged at 50%.",
        "Client is responsible for their dog's behaviour at all times.",
        "Results depend on consistent practice at home between sessions.",
        "Trainer may photograph/video the dog for educational purposes unless opted out.",
        "Client confirms they are 18+ and the legal owner of the dog.",
    ]:
        paw_print(d,110,y+18,size=14,fill=NAVY)
        d.text((145,y),term,fill=CHARCOAL,font=font(30)); y+=50
    y+=8
    y=checkbox(d,120,y,"I opt OUT of my dog being photographed/filmed",font_size=32)
    y+=20
    d.text((120,y),"Client Signature:",CHARCOAL,font=font(36,bold=True))
    d.rectangle([120,y+58,1100,y+61],fill=NAVY)
    d.text((120,y+80),"Date:",CHARCOAL,font=font(36,bold=True))
    d.rectangle([220,y+138,700,y+141],fill=NAVY)
    d.text((1200,y),"Trainer Signature:",CHARCOAL,font=font(36,bold=True))
    d.rectangle([1200,y+58,2300,y+61],fill=NAVY)
    a4_footer(d,W2,H2)
    return save_upload(img,f"{PFX}_Training_Agreement.png",f"templates/{NICHE}/forms/{PFX}_Training_Agreement.png")

def build_behaviour_assessment():
    W2,H2=PIL_A4; img=Image.new("RGB",(W2,H2),WHITE); d=ImageDraw.Draw(img)
    y=a4_header(img,d,"BEHAVIOUR ASSESSMENT FORM")
    y=section_head(d,80,y+10,"DOG PROFILE",width=W2-160); y+=14
    y=field_pair(d,120,y,"Dog's Name:","Breed:",total_w=2240)
    y=field_triple(d,120,y,["Age:","Gender:","Neutered?"],total_w=2240)
    y=field_pair(d,120,y,"How long owned:","Where from (breeder/rescue/other):",total_w=2240)
    y+=8
    y=section_head(d,80,y,"PRESENTING ISSUES",width=W2-160); y+=14
    issues=["Pulling on lead","Jumping up","Barking / reactivity","Aggression (dog)","Aggression (people)",
            "Recall problems","Separation anxiety","Destructive behaviour","Biting / mouthing","Other"]
    for i,iss in enumerate(issues):
        xoff=120 if i%2==0 else 1300
        if i%2==0 and i>0: y+=52
        checkbox(d,xoff,y,iss,font_size=34)
    y+=60
    y=field_line(d,120,y,"Main issue you'd like help with (in your own words):",width=2240)
    for _ in range(2):
        d.rectangle([120,y+40,2360,y+43],fill=NAVY); y+=70
    y+=8
    y=section_head(d,80,y,"TRAINING HISTORY",width=W2-160); y+=14
    y=field_line(d,120,y,"Previous training attended (if any):",width=2240)
    y=field_line(d,120,y,"Methods used previously:",width=2240)
    y=field_line(d,120,y,"What has/hasn't worked:",width=2240)
    y+=8
    y=section_head(d,80,y,"MOTIVATION & REWARDS",width=W2-160); y+=14
    y=field_line(d,120,y,"Favourite food rewards:",width=2240)
    y=field_line(d,120,y,"Favourite toy / play rewards:",width=2240)
    y=field_line(d,120,y,"Goal / what success looks like for you:",width=2240)
    a4_footer(d,W2,H2)
    return save_upload(img,f"{PFX}_Behaviour_Assessment.png",f"templates/{NICHE}/forms/{PFX}_Behaviour_Assessment.png")

def build_session_tracker():
    W2,H2=PIL_A4; img=Image.new("RGB",(W2,H2),WHITE); d=ImageDraw.Draw(img)
    y=a4_header(img,d,"SESSION PROGRESS TRACKER")
    y+=10
    d.text((120,y),"Dog:",CHARCOAL,font=font(38,bold=True))
    d.rectangle([230,y+55,1000,y+58],fill=NAVY)
    d.text((1100,y),"Trainer:",CHARCOAL,font=font(38,bold=True))
    d.rectangle([1290,y+55,2300,y+58],fill=NAVY)
    y+=120
    hdr=["Session","Date","Skill worked","Progress","Homework set","✓"]
    wids=[160,240,600,520,560,100]
    y=table_row(d,80,y,hdr,wids,header=True)
    for i in range(12):
        y=table_row(d,80,y,[str(i+1),"","","","",""],wids,alt=bool(i%2),row_h=100)
    y+=10
    y=section_head(d,80,y,"OVERALL NOTES",width=W2-160); y+=14
    for _ in range(4):
        d.rectangle([120,y+40,2360,y+43],fill=NAVY); y+=72
    a4_footer(d,W2,H2)
    return save_upload(img,f"{PFX}_Session_Tracker.png",f"templates/{NICHE}/forms/{PFX}_Session_Tracker.png")

def build_vaccination_record():
    W2,H2=PIL_A4; img=Image.new("RGB",(W2,H2),WHITE); d=ImageDraw.Draw(img)
    y=a4_header(img,d,"VACCINATION & HEALTH RECORD")
    y=section_head(d,80,y+10,"DOG DETAILS",width=W2-160); y+=14
    y=field_pair(d,120,y,"Dog's Name:","Breed:",total_w=2240)
    y=field_triple(d,120,y,["DOB:","Microchip #:","Pet insurance:"],total_w=2240)
    y+=8
    y=section_head(d,80,y,"VACCINATION RECORD",width=W2-160); y+=10
    hdr=["Vaccine","Date given","Due next","Batch #","Vet"]
    wids=[500,320,320,300,680]
    y=table_row(d,80,y,hdr,wids,header=True)
    for i,vax in enumerate(["Primary course (1st)","Primary course (2nd)","Annual booster",
                             "Kennel cough","Rabies (if applicable)","Other"]):
        y=table_row(d,80,y,[vax,"","","",""],wids,alt=bool(i%2),row_h=80)
    y+=10
    y=section_head(d,80,y,"FLEA, TICK & WORMING",width=W2-160); y+=10
    hdr2=["Treatment","Product used","Date treated","Due next","Notes"]
    wids2=[380,460,300,300,680]
    y=table_row(d,80,y,hdr2,wids2,header=True)
    for i,trt in enumerate(["Flea treatment","Tick treatment","Worming","Heartworm"]):
        y=table_row(d,80,y,[trt,"","","",""],wids2,alt=bool(i%2),row_h=80)
    y+=10
    y=section_head(d,80,y,"HEALTH NOTES",width=W2-160); y+=14
    y=field_line(d,120,y,"Known allergies / conditions:",width=2240)
    y=field_line(d,120,y,"Current medications:",width=2240)
    y=field_line(d,120,y,"Vet practice name & phone:",width=2240)
    a4_footer(d,W2,H2)
    return save_upload(img,f"{PFX}_Vaccination_Record.png",f"templates/{NICHE}/forms/{PFX}_Vaccination_Record.png")

def build_progress_report():
    W2,H2=PIL_A4; img=Image.new("RGB",(W2,H2),WHITE); d=ImageDraw.Draw(img)
    y=a4_header(img,d,"PROGRESS REPORT CARD")
    y+=10
    d.text((120,y),"Dog:",CHARCOAL,font=font(38,bold=True))
    d.rectangle([230,y+55,900,y+58],fill=NAVY)
    d.text((1000,y),"Date:",CHARCOAL,font=font(38,bold=True))
    d.rectangle([1120,y+55,1700,y+58],fill=NAVY)
    d.text((1800,y),"Session #:",CHARCOAL,font=font(38,bold=True))
    d.rectangle([2060,y+55,2360,y+58],fill=NAVY)
    y+=120
    y=section_head(d,80,y,"SKILLS ASSESSED",width=W2-160); y+=10
    hdr=["Skill","Grade (1-5)","Notes"]
    wids=[700,320,1100]
    y=table_row(d,80,y,hdr,wids,header=True)
    skills=["Sit","Down","Stay","Come (recall)","Loose lead walking",
            "Leave it","Focus / eye contact","Greeting calmly","Other"]
    for i,sk in enumerate(skills):
        y=table_row(d,80,y,[sk,"",""],wids,alt=bool(i%2),row_h=80)
    y+=10
    y=section_head(d,80,y,"TRAINER COMMENTS",width=W2-160); y+=14
    for _ in range(5):
        d.rectangle([120,y+40,2360,y+43],fill=NAVY); y+=70
    y+=10
    y=section_head(d,80,y,"HOMEWORK FOR NEXT SESSION",width=W2-160); y+=14
    for i in range(4):
        d.text((120,y),f"{i+1}.",CHARCOAL,font=font(36,bold=True))
        d.rectangle([175,y+48,2360,y+51],fill=NAVY); y+=75
    d.text((120,y),"Next session date:",CHARCOAL,font=font(36,bold=True))
    d.rectangle([460,y+52,1200,y+55],fill=NAVY)
    d.text((1300,y),"Trainer signature:",CHARCOAL,font=font(36,bold=True))
    d.rectangle([1660,y+52,2360,y+55],fill=NAVY)
    a4_footer(d,W2,H2)
    return save_upload(img,f"{PFX}_Progress_Report.png",f"templates/{NICHE}/forms/{PFX}_Progress_Report.png")

def build_homework_sheet():
    W2,H2=PIL_A4; img=Image.new("RGB",(W2,H2),WHITE); d=ImageDraw.Draw(img)
    y=a4_header(img,d,"HOMEWORK SHEET")
    y+=10
    d.text((120,y),"Dog:",CHARCOAL,font=font(38,bold=True))
    d.rectangle([230,y+55,900,y+58],fill=NAVY)
    d.text((1000,y),"Week commencing:",CHARCOAL,font=font(38,bold=True))
    d.rectangle([1480,y+55,2360,y+58],fill=NAVY)
    y+=120
    for i in range(4):
        y=section_head(d,80,y,f"EXERCISE {i+1}",width=W2-160); y+=14
        y=field_line(d,120,y,"Skill / command:",width=2240)
        y=field_line(d,120,y,"How to do it (step by step):",width=2240)
        y=field_pair(d,120,y,"Sessions per day:","Duration:",total_w=2240)
        y=field_line(d,120,y,"Reward to use:",width=2240)
        y+=10
    y=section_head(d,80,y,"DAILY PRACTICE LOG",width=W2-160); y+=10
    hdr=["Day","Ex 1 done","Ex 2 done","Ex 3 done","Ex 4 done","Notes"]
    wids=[200,320,320,320,320,640]
    y=table_row(d,80,y,hdr,wids,header=True)
    for day in ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]:
        y=table_row(d,80,y,[day,"□","□","□","□",""],wids,row_h=72)
    a4_footer(d,W2,H2)
    return save_upload(img,f"{PFX}_Homework_Sheet.png",f"templates/{NICHE}/forms/{PFX}_Homework_Sheet.png")

def build_photo_release():
    W2,H2=PIL_A4; img=Image.new("RGB",(W2,H2),WHITE); d=ImageDraw.Draw(img)
    y=a4_header(img,d,"PHOTO & VIDEO RELEASE FORM")
    y=section_head(d,80,y+10,"CONSENT DETAILS",width=W2-160); y+=14
    y=field_pair(d,120,y,"Client Name:","Dog Name:",total_w=2240)
    y=field_pair(d,120,y,"Date:","Session type:",total_w=2240)
    y+=10
    y=section_head(d,80,y,"CONSENT OPTIONS",width=W2-160); y+=14
    d.text((120,y),"I give permission for the following use of photos/videos of my dog:",CHARCOAL,font=font(36,bold=True)); y+=60
    permissions=[
        "Social media posts (Instagram, Facebook, TikTok)",
        "Website / portfolio",
        "Marketing materials (flyers, brochures)",
        "Training educational content",
        "Press / media",
    ]
    for perm in permissions:
        d.rectangle([120,y+4,164,y+48],outline=NAVY,width=3)
        d.text((180,y),perm,fill=CHARCOAL,font=font(36)); y+=60
    y+=20
    d.text((120,y),"I do NOT give permission for any of the above.",CHARCOAL,font=font(36))
    d.rectangle([120,y+4,164,y+48],outline=NAVY,width=3); y+=80
    y=section_head(d,80,y,"CONDITIONS",width=W2-160); y+=14
    for cond in [
        "Images will not be sold to third parties.",
        "Client name will not be used without additional written consent.",
        "This consent can be withdrawn at any time by written request.",
    ]:
        paw_print(d,110,y+18,size=14,fill=NAVY)
        d.text((145,y),cond,fill=CHARCOAL,font=font(32)); y+=52
    y+=20
    d.text((120,y),"Client Signature:",CHARCOAL,font=font(36,bold=True))
    d.rectangle([120,y+58,1100,y+61],fill=NAVY)
    d.text((120,y+80),"Date:",CHARCOAL,font=font(36,bold=True))
    d.rectangle([220,y+138,700,y+141],fill=NAVY)
    d.text((1200,y),"Trainer Signature:",CHARCOAL,font=font(36,bold=True))
    d.rectangle([1200,y+58,2300,y+61],fill=NAVY)
    a4_footer(d,W2,H2)
    return save_upload(img,f"{PFX}_Photo_Release.png",f"templates/{NICHE}/forms/{PFX}_Photo_Release.png")

def build_invoice():
    W2,H2=PIL_A4; img=Image.new("RGB",(W2,H2),WHITE); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W2,260],fill=NAVY); gold_rule(d,260,thickness=10,canvas_w=W2)
    paw_print(d,160,130,size=70,fill=GOLD)
    d.text((280,60),"YOUR BUSINESS NAME",fill=GOLD,font=font(64,bold=True))
    d.text((280,140),"Dog Training & Puppy School",fill=CREAM,font=font(40))
    d.text((280,195),"07700 000000  |  yourname@email.com",fill=WHITE,font=font(32))
    centred(d,300,"INVOICE",CHARCOAL,font(80,bold=True),canvas_w=W2)
    d.text((120,420),"Invoice #:",CHARCOAL,font=font(38,bold=True)); d.rectangle([310,460,900,463],fill=NAVY)
    d.text((120,485),"Date:",CHARCOAL,font=font(38,bold=True)); d.rectangle([225,525,900,528],fill=NAVY)
    d.text((120,550),"Due:",CHARCOAL,font=font(38,bold=True)); d.rectangle([210,590,900,593],fill=NAVY)
    d.text((1200,420),"Bill To:",CHARCOAL,font=font(38,bold=True))
    for yy in [460,525,590]: d.rectangle([1200,yy,2300,yy+3],fill=NAVY)
    y=660
    hdr=["Date","Session / Service","Duration","Rate","Total"]
    wids=[300,720,280,350,270]
    y=table_row(d,80,y,hdr,wids,header=True)
    for i in range(8): y=table_row(d,80,y,[""]*5,wids,alt=bool(i%2),row_h=85)
    d.rectangle([1680,y+10,2300,y+80],fill=CREAM_ALT)
    d.text((1700,y+20),"Subtotal:",CHARCOAL,font=font(36,bold=True))
    right(d,2280,y+20,"£",CHARCOAL,font(36,bold=True)); y+=80
    d.rectangle([1680,y+10,2300,y+80],fill=NAVY)
    d.text((1700,y+20),"TOTAL DUE:",WHITE,font=font(40,bold=True))
    right(d,2280,y+20,"£",GOLD,font(40,bold=True)); y+=100
    d.text((120,y),"Payment: Bank Transfer / Cash / Card",CHARCOAL,font=font(34))
    d.text((120,y+50),"Sort code: XX-XX-XX  |  Account: XXXXXXXX",CHARCOAL,font=font(34))
    d.text((120,y+100),"Thank you for training with us!",NAVY,font=font(36,bold=True))
    a4_footer(d,W2,H2)
    return save_upload(img,f"{PFX}_Invoice.png",f"templates/{NICHE}/forms/{PFX}_Invoice.png")

def build_booking_confirmation():
    W2,H2=PIL_A4; img=Image.new("RGB",(W2,H2),WHITE); d=ImageDraw.Draw(img)
    y=a4_header(img,d,"BOOKING CONFIRMATION")
    y=section_head(d,80,y+10,"CLIENT DETAILS",width=W2-160); y+=14
    y=field_pair(d,120,y,"Client Name:","Phone:",total_w=2240)
    y=field_pair(d,120,y,"Dog Name(s):","Address:",total_w=2240)
    y+=10
    y=section_head(d,80,y,"SESSION DETAILS",width=W2-160); y+=14
    y=field_pair(d,120,y,"Service / Class:","Trainer:",total_w=2240)
    y=field_pair(d,120,y,"Date:","Time:",total_w=2240)
    y=field_pair(d,120,y,"Location:","Duration:",total_w=2240)
    y=field_line(d,120,y,"Special notes / requirements:",width=2240)
    y+=10
    y=section_head(d,80,y,"PAYMENT SUMMARY",width=W2-160); y+=14
    hdr=["Service","Rate","Qty","Total"]
    wids=[1100,400,200,420]
    y=table_row(d,80,y,hdr,wids,header=True)
    for i in range(4): y=table_row(d,80,y,[""]*4,wids,alt=bool(i%2),row_h=80)
    d.rectangle([1300,y+10,2220,y+70],fill=NAVY)
    d.text((1320,y+18),"TOTAL:",WHITE,font=font(42,bold=True))
    right(d,2200,y+18,"£",GOLD,font(42,bold=True)); y+=100
    centred(d,y,"24-hour cancellation notice required.",CHARCOAL,font(34),canvas_w=W2)
    centred(d,y+50,"Late cancellations may incur a charge.",CHARCOAL,font(34),canvas_w=W2)
    centred(d,y+120,"We look forward to training with you and your dog!",NAVY,font(38,bold=True),canvas_w=W2)
    a4_footer(d,W2,H2)
    return save_upload(img,f"{PFX}_Booking_Confirmation.png",f"templates/{NICHE}/forms/{PFX}_Booking_Confirmation.png")


# ══════════════════════════════════════════════════════════════════════════════
# OPERATIONS (5)
# ══════════════════════════════════════════════════════════════════════════════

def build_weekly_class_schedule():
    W2,H2=PIL_A4; img=Image.new("RGB",(W2,H2),WHITE); d=ImageDraw.Draw(img)
    y=a4_header(img,d,"WEEKLY CLASS SCHEDULE")
    y+=10
    d.text((120,y),"Week commencing:",CHARCOAL,font=font(38,bold=True))
    d.rectangle([500,y+55,1400,y+58],fill=NAVY)
    d.text((1500,y),"Trainer:",CHARCOAL,font=font(38,bold=True))
    d.rectangle([1700,y+55,2360,y+58],fill=NAVY)
    y+=120
    hdr=["Time","Class","Level","Venue","Dogs","Spaces left","Notes"]
    wids=[200,380,260,340,140,220,300]
    y=table_row(d,80,y,hdr,wids,header=True)
    times=["08:00","09:00","10:00","11:00","13:00","14:00","15:00",
           "16:00","17:00","18:00","19:00","20:00"]
    for i,t in enumerate(times):
        y=table_row(d,80,y,[t,"","","","","",""],wids,alt=bool(i%2),row_h=80)
    y+=10
    d.text((120,y),"Total classes this week:",CHARCOAL,font=font(36,bold=True))
    d.rectangle([560,y+52,900,y+55],fill=NAVY)
    d.text((1000,y),"Total dogs trained:",CHARCOAL,font=font(36,bold=True))
    d.rectangle([1380,y+52,1800,y+55],fill=NAVY)
    a4_footer(d,W2,H2)
    return save_upload(img,f"{PFX}_Weekly_Class_Schedule.png",f"templates/{NICHE}/operations/{PFX}_Weekly_Class_Schedule.png")

def build_incident_report():
    W2,H2=PIL_A4; img=Image.new("RGB",(W2,H2),WHITE); d=ImageDraw.Draw(img)
    y=a4_header(img,d,"INCIDENT REPORT FORM")
    y=section_head(d,80,y+10,"INCIDENT DETAILS",width=W2-160); y+=14
    y=field_pair(d,120,y,"Date:","Time:",total_w=2240)
    y=field_pair(d,120,y,"Location:","Trainer:",total_w=2240)
    y=field_pair(d,120,y,"Dog involved:","Owner:",total_w=2240)
    y+=10
    y=section_head(d,80,y,"INCIDENT TYPE",width=W2-160); y+=14
    types=["Dog bite / nip","Dog fight","Injury (dog)","Injury (person)","Property damage",
           "Equipment failure","Medical emergency","Complaint raised","Other"]
    for i,t in enumerate(types):
        xoff=120 if i%2==0 else 1300
        if i%2==0 and i>0: y+=52
        checkbox(d,xoff,y,t,font_size=34)
    y+=60
    y=section_head(d,80,y,"DESCRIPTION OF INCIDENT",width=W2-160); y+=14
    for _ in range(7):
        d.rectangle([120,y+44,2360,y+47],fill=NAVY); y+=74
    y+=10
    y=section_head(d,80,y,"ACTION TAKEN",width=W2-160); y+=14
    for _ in range(4):
        d.rectangle([120,y+44,2360,y+47],fill=NAVY); y+=74
    y+=10
    y=field_pair(d,120,y,"Owner notified? Y / N   Time:","Vet contacted? Y / N",total_w=2240)
    d.text((120,y),"Trainer Signature:",CHARCOAL,font=font(36,bold=True))
    d.rectangle([120,y+58,1100,y+61],fill=NAVY)
    d.text((1200,y),"Date:",CHARCOAL,font=font(36,bold=True))
    d.rectangle([1320,y+58,2300,y+61],fill=NAVY)
    a4_footer(d,W2,H2)
    return save_upload(img,f"{PFX}_Incident_Report.png",f"templates/{NICHE}/operations/{PFX}_Incident_Report.png")

def build_expenses_tracker():
    W2,H2=PIL_A4; img=Image.new("RGB",(W2,H2),WHITE); d=ImageDraw.Draw(img)
    y=a4_header(img,d,"BUSINESS EXPENSES TRACKER")
    y+=10
    d.text((120,y),"Month/Year:",CHARCOAL,font=font(38,bold=True))
    d.rectangle([380,y+55,1100,y+58],fill=NAVY); y+=120
    hdr=["Date","Description","Category","Supplier","Amount","Receipt"]
    wids=[220,560,380,380,220,180]
    y=table_row(d,80,y,hdr,wids,header=True)
    cats=["Training equipment","Insurance","Venue hire","Marketing","Software",
          "Training/CPD","Phone","Fuel","Other","","","","","","","","","","",""]
    for i in range(20):
        cat=cats[i] if i<len(cats) else ""
        y=table_row(d,80,y,["","",cat,"","",""],wids,alt=bool(i%2),row_h=70)
    d.rectangle([80,y+10,2300,y+80],fill=CREAM_ALT,outline=GOLD,width=1)
    d.text((100,y+22),"TOTAL:",NAVY,font=font(44,bold=True))
    right(d,2280,y+22,"£",CHARCOAL,font(44,bold=True)); y+=100
    d.text((120,y),"Notes:",CHARCOAL,font=font(36,bold=True))
    d.rectangle([120,y+55,2300,y+58],fill=NAVY)
    a4_footer(d,W2,H2)
    return save_upload(img,f"{PFX}_Expenses_Tracker.png",f"templates/{NICHE}/operations/{PFX}_Expenses_Tracker.png")

def build_income_tracker():
    W2,H2=PIL_A4; img=Image.new("RGB",(W2,H2),WHITE); d=ImageDraw.Draw(img)
    y=a4_header(img,d,"INCOME TRACKER")
    y+=10
    d.text((120,y),"Month/Year:",CHARCOAL,font=font(38,bold=True))
    d.rectangle([380,y+55,1100,y+58],fill=NAVY); y+=120
    hdr=["Date","Client","Service","Sessions","Rate","Total","Paid?"]
    wids=[210,460,380,190,200,250,150]
    y=table_row(d,80,y,hdr,wids,header=True)
    for i in range(20): y=table_row(d,80,y,[""]*7,wids,alt=bool(i%2),row_h=72)
    d.rectangle([80,y+10,2300,y+80],fill=NAVY)
    d.text((100,y+20),"TOTAL INCOME:",WHITE,font=font(44,bold=True))
    right(d,2280,y+20,"£",GOLD,font(44,bold=True)); y+=100
    d.rectangle([80,y+10,1100,y+80],fill=CREAM_ALT,outline=GOLD,width=1)
    d.text((100,y+22),"Total Expenses:",CHARCOAL,font=font(34))
    right(d,1080,y+22,"£",CHARCOAL,font(34))
    d.rectangle([1160,y+10,2300,y+80],fill=CREAM_ALT,outline=NAVY,width=2)
    d.text((1180,y+22),"NET PROFIT:",NAVY,font=font(40,bold=True))
    right(d,2280,y+22,"£",CHARCOAL,font(40,bold=True)); y+=100
    d.text((120,y),"Notes:",CHARCOAL,font=font(36,bold=True))
    d.rectangle([120,y+55,2300,y+58],fill=NAVY)
    a4_footer(d,W2,H2)
    return save_upload(img,f"{PFX}_Income_Tracker.png",f"templates/{NICHE}/operations/{PFX}_Income_Tracker.png")

def build_certificate():
    W2,H2=PIL_A4; img=Image.new("RGB",(W2,H2),CREAM); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W2,50],fill=NAVY); d.rectangle([0,H2-50,W2,H2],fill=NAVY)
    d.rectangle([0,50,50,H2-50],fill=NAVY); d.rectangle([W2-50,50,W2,H2-50],fill=NAVY)
    d.rectangle([65,65,W2-65,H2-65],outline=GOLD,width=5)
    paw_print(d,160,200,size=70,fill=GOLD); paw_print(d,W2-160,200,size=70,fill=GOLD)
    paw_print(d,160,H2-200,size=70,fill=GOLD); paw_print(d,W2-160,H2-200,size=70,fill=GOLD)
    centred(d,110,"CERTIFICATE OF COMPLETION",NAVY,font(100,bold=True),canvas_w=W2)
    gold_rule(d,260,x0=120,x1=W2-120,thickness=6)
    centred(d,300,"This is to certify that",CHARCOAL,font(52),canvas_w=W2)
    d.rectangle([300,385,W2-300,388],fill=NAVY)
    centred(d,400,"(Dog's Name)",CHARCOAL,font(38),canvas_w=W2)
    centred(d,470,"accompanied by",CHARCOAL,font(52),canvas_w=W2)
    d.rectangle([300,555,W2-300,558],fill=NAVY)
    centred(d,570,"(Owner's Name)",CHARCOAL,font(38),canvas_w=W2)
    centred(d,640,"has successfully completed",CHARCOAL,font(52),canvas_w=W2)
    d.rectangle([200,730,W2-200,733],fill=GOLD)
    centred(d,748,"(Course Name)",CHARCOAL,font(38),canvas_w=W2)
    centred(d,820,"at",CHARCOAL,font(52),canvas_w=W2)
    centred(d,890,"YOUR BUSINESS NAME",NAVY,font(72,bold=True),canvas_w=W2)
    gold_rule(d,990,x0=120,x1=W2-120,thickness=4)
    d.text((200,1040),"Date: _________________________",CHARCOAL,font=font(44))
    d.text((200,1110),"Trainer: ______________________",CHARCOAL,font=font(44))
    right(d,W2-200,1040,"Grade: ________________",CHARCOAL,font(44))
    right(d,W2-200,1110,"Signed: _______________",CHARCOAL,font(44))
    centred(d,H2-130,"Congratulations! Keep up the great work.",NAVY,font(44,bold=True),canvas_w=W2)
    centred(d,H2-175,"© PurpleOcaz — purpleocaz.etsy.com",CREAM,font(30),canvas_w=W2)
    return save_upload(img,f"{PFX}_Certificate.png",f"templates/{NICHE}/operations/{PFX}_Certificate.png")


# ══════════════════════════════════════════════════════════════════════════════
# DELIVERY PDF
# ══════════════════════════════════════════════════════════════════════════════

SECTIONS = [
    ("BRANDING (9 templates)", [
        ("Business Card — Dark",      f"{CDN}/templates/{NICHE}/branding/{PFX}_Business_Card_Dark.png"),
        ("Business Card — Light",     f"{CDN}/templates/{NICHE}/branding/{PFX}_Business_Card_Light.png"),
        ("Appointment Card — Dark",   f"{CDN}/templates/{NICHE}/branding/{PFX}_Appointment_Card_Dark.png"),
        ("Appointment Card — Light",  f"{CDN}/templates/{NICHE}/branding/{PFX}_Appointment_Card_Light.png"),
        ("Loyalty Card (5th free)",   f"{CDN}/templates/{NICHE}/branding/{PFX}_Loyalty_Card.png"),
        ("Gift Certificate",          f"{CDN}/templates/{NICHE}/branding/{PFX}_Gift_Certificate.png"),
        ("Welcome Sign (A4)",         f"{CDN}/templates/{NICHE}/branding/{PFX}_Welcome_Sign.png"),
        ("Thank You Card",            f"{CDN}/templates/{NICHE}/branding/{PFX}_Thank_You_Card.png"),
        ("Referral Card",             f"{CDN}/templates/{NICHE}/branding/{PFX}_Referral_Card.png"),
    ]),
    ("MARKETING (8 templates)", [
        ("Flyer — Group Classes",     f"{CDN}/templates/{NICHE}/marketing/{PFX}_Flyer_Group_Classes.png"),
        ("Flyer — 1-to-1 Training",   f"{CDN}/templates/{NICHE}/marketing/{PFX}_Flyer_1to1.png"),
        ("Price List / Class Schedule",f"{CDN}/templates/{NICHE}/marketing/{PFX}_Price_List.png"),
        ("Social — Booking Open",     f"{CDN}/templates/{NICHE}/marketing/{PFX}_Social_Booking.png"),
        ("Social — Testimonial",      f"{CDN}/templates/{NICHE}/marketing/{PFX}_Social_Testimonial.png"),
        ("Social — Training Tip",     f"{CDN}/templates/{NICHE}/marketing/{PFX}_Social_Training_Tip.png"),
        ("Social — Before & After",   f"{CDN}/templates/{NICHE}/marketing/{PFX}_Social_Before_After.png"),
        ("Social — Puppy School Promo",f"{CDN}/templates/{NICHE}/marketing/{PFX}_Social_Puppy_Promo.png"),
    ]),
    ("CLIENT FORMS (9 templates)", [
        ("Training Agreement",        f"{CDN}/templates/{NICHE}/forms/{PFX}_Training_Agreement.png"),
        ("Behaviour Assessment Form", f"{CDN}/templates/{NICHE}/forms/{PFX}_Behaviour_Assessment.png"),
        ("Session Progress Tracker",  f"{CDN}/templates/{NICHE}/forms/{PFX}_Session_Tracker.png"),
        ("Vaccination & Health Record",f"{CDN}/templates/{NICHE}/forms/{PFX}_Vaccination_Record.png"),
        ("Progress Report Card",      f"{CDN}/templates/{NICHE}/forms/{PFX}_Progress_Report.png"),
        ("Homework Sheet",            f"{CDN}/templates/{NICHE}/forms/{PFX}_Homework_Sheet.png"),
        ("Photo & Video Release",     f"{CDN}/templates/{NICHE}/forms/{PFX}_Photo_Release.png"),
        ("Invoice",                   f"{CDN}/templates/{NICHE}/forms/{PFX}_Invoice.png"),
        ("Booking Confirmation",      f"{CDN}/templates/{NICHE}/forms/{PFX}_Booking_Confirmation.png"),
    ]),
    ("OPERATIONS (5 templates)", [
        ("Weekly Class Schedule",     f"{CDN}/templates/{NICHE}/operations/{PFX}_Weekly_Class_Schedule.png"),
        ("Incident Report Form",      f"{CDN}/templates/{NICHE}/operations/{PFX}_Incident_Report.png"),
        ("Expenses Tracker",          f"{CDN}/templates/{NICHE}/operations/{PFX}_Expenses_Tracker.png"),
        ("Income Tracker",            f"{CDN}/templates/{NICHE}/operations/{PFX}_Income_Tracker.png"),
        ("Certificate of Completion", f"{CDN}/templates/{NICHE}/operations/{PFX}_Certificate.png"),
    ]),
]


def build_delivery_pdf():
    pdf_path = LISTING / "DT_Mega_Bundle_DELIVERY.pdf"
    c = rl_canvas.Canvas(str(pdf_path), pagesize=RL_A4)
    W2, H2 = RL_A4
    NAVY_RL  = colors.HexColor("#1B3A5C")
    GOLD_RL  = colors.HexColor("#C9A96E")
    CREAM_RL = colors.HexColor("#F5F0E8")
    CHAR_RL  = colors.HexColor("#1A1A1A")
    WHITE_RL = colors.HexColor("#FFFFFF")
    # Cover
    c.setFillColor(NAVY_RL); c.rect(0,0,W2,H2,fill=1,stroke=0)
    c.setFillColor(GOLD_RL); c.setFont("Helvetica-Bold",44)
    c.drawCentredString(W2/2,H2-100,"DOG TRAINING & PUPPY SCHOOL")
    c.drawCentredString(W2/2,H2-155,"MEGA BUSINESS BUNDLE")
    c.setFillColor(WHITE_RL); c.setFont("Helvetica",26)
    c.drawCentredString(W2/2,H2-210,"31 Canva Templates — Fully Editable")
    c.setFillColor(GOLD_RL); c.rect(50,H2-250,W2-100,3,fill=1,stroke=0)
    c.setFillColor(WHITE_RL); c.setFont("Helvetica",20)
    y=H2-300
    for line in ["Thank you for your purchase!","",
                 "This bundle contains 31 fully editable PNG templates.",
                 "Download each template from the links below.",
                 "Open in Canva (free account works fine) and edit to match your brand.","",
                 "Included categories:","  • Branding (9 templates)","  • Marketing (8 templates)",
                 "  • Client Forms (9 templates)","  • Operations (5 templates)","",
                 "Questions? Message us on Etsy — we reply within 24 hours."]:
        c.drawString(60,y,line); y-=28
    c.setFillColor(GOLD_RL); c.rect(50,60,W2-100,3,fill=1,stroke=0)
    c.setFillColor(WHITE_RL); c.setFont("Helvetica",16)
    c.drawCentredString(W2/2,35,"PurpleOcaz — purpleocaz.etsy.com")
    c.showPage()
    for section_title,items in SECTIONS:
        c.setFillColor(CREAM_RL); c.rect(0,0,W2,H2,fill=1,stroke=0)
        c.setFillColor(NAVY_RL); c.rect(0,H2-80,W2,80,fill=1,stroke=0)
        c.setFillColor(GOLD_RL); c.setFont("Helvetica-Bold",28)
        c.drawCentredString(W2/2,H2-52,section_title)
        y2=H2-120
        for name,url in items:
            c.setFont("Helvetica-Bold",18); c.setFillColor(CHAR_RL)
            c.drawString(60,y2,f"• {name}")
            c.setFont("Helvetica",14); c.setFillColor(NAVY_RL)
            c.drawString(80,y2-22,url)
            c.linkURL(url,(80,y2-30,min(80+len(url)*7,W2-60),y2-10))
            y2-=65
            if y2<80:
                c.setFillColor(NAVY_RL); c.rect(0,0,W2,40,fill=1,stroke=0)
                c.setFillColor(WHITE_RL); c.setFont("Helvetica",12)
                c.drawCentredString(W2/2,14,"PurpleOcaz — purpleocaz.etsy.com")
                c.showPage()
                c.setFillColor(CREAM_RL); c.rect(0,0,W2,H2,fill=1,stroke=0)
                y2=H2-60
        c.setFillColor(NAVY_RL); c.rect(0,0,W2,40,fill=1,stroke=0)
        c.setFillColor(WHITE_RL); c.setFont("Helvetica",12)
        c.drawCentredString(W2/2,14,"PurpleOcaz — purpleocaz.etsy.com")
        c.showPage()
    c.save()
    print(f"  Delivery PDF: {pdf_path}")
    upload_to_spaces(pdf_path,"templates/dog-training/DT_Mega_Bundle_DELIVERY.pdf",content_type="application/pdf")
    return pdf_path


# ══════════════════════════════════════════════════════════════════════════════
# 7 LISTING IMAGES
# ══════════════════════════════════════════════════════════════════════════════

def build_listing_images():
    imgs = []

    # 1 — Hero
    img=Image.new("RGB",(W,H),NAVY); d=ImageDraw.Draw(img)
    d.rectangle([0,H//2+80,W,H],fill=CHARCOAL)
    gold_rule(d,H//2+80,thickness=16,canvas_w=W)
    paw_print(d,200,280,size=120,fill=GOLD); paw_print(d,W-200,280,size=120,fill=GOLD)
    centred(d,160,"DOG TRAINING",GOLD,font(180,bold=True),canvas_w=W)
    centred(d,360,"& PUPPY SCHOOL",WHITE,font(130,bold=True),canvas_w=W)
    gold_rule(d,540,x0=200,x1=W-200,thickness=8)
    centred(d,570,"MEGA BUSINESS BUNDLE",CREAM,font(90,bold=True),canvas_w=W)
    centred(d,690,"31 Professional Templates — Fully Editable in Canva",WHITE,font(60),canvas_w=W)
    gold_rule(d,790,x0=200,x1=W-200,thickness=8)
    badges=["Branding Kit","Group Classes","1-to-1 Training","Client Forms","Operations"]
    bw=500; total=bw*len(badges)+40*(len(badges)-1); bx=(W-total)//2
    for badge in badges:
        d.rectangle([bx,840,bx+bw,940],fill=GOLD)
        bb=d.textbbox((0,0),badge,font=font(48,bold=True)); tw=bb[2]-bb[0]
        d.text((bx+(bw-tw)//2,868),badge,fill=CHARCOAL,font=font(48,bold=True))
        bx+=bw+40
    centred(d,1000,"APDT Member  |  Force-Free Methods  |  Fully Insured",CREAM,font(56),canvas_w=W)
    centred(d,H//2+140,"The complete toolkit for",WHITE,font(70),canvas_w=W)
    centred(d,H//2+240,"professional dog trainers",WHITE,font(70),canvas_w=W)
    centred(d,H//2+360,"and puppy school owners.",GOLD,font(90,bold=True),canvas_w=W)
    centred(d,H//2+500,"£39.99  •  Instant Download  •  Canva Free Account Works",CREAM,font(50),canvas_w=W)
    p=LISTING/"DT_listing_01_hero.png"; img.save(p,"PNG"); print(f"  Saved {p.name}"); imgs.append(p)

    # 2 — What's inside
    img=Image.new("RGB",(W,H),CREAM); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W,220],fill=NAVY); gold_rule(d,220,thickness=10,canvas_w=W)
    centred(d,58,"WHAT'S INSIDE YOUR BUNDLE",GOLD,font(100,bold=True),canvas_w=W)
    centred(d,160,"31 fully editable professional templates",CREAM,font(50),canvas_w=W)
    cats=[
        ("BRANDING","9 templates",NAVY,[
            "Business Card Dark & Light","Appointment Card Dark & Light",
            "Loyalty Card (5th session free)","Gift Certificate",
            "Welcome Sign","Thank You Card","Referral Card"]),
        ("MARKETING","8 templates",NAVY,[
            "Group Classes Flyer","1-to-1 Training Flyer",
            "Price List / Class Schedule","Social — Booking Open",
            "Social — Testimonial","Social — Training Tip",
            "Social — Before & After","Social — Puppy School Promo"]),
        ("CLIENT FORMS","9 templates",CHARCOAL,[
            "Training Agreement","Behaviour Assessment Form",
            "Session Progress Tracker","Vaccination & Health Record",
            "Progress Report Card","Homework Sheet",
            "Photo & Video Release","Invoice","Booking Confirmation"]),
        ("OPERATIONS","5 templates",CHARCOAL,[
            "Weekly Class Schedule","Incident Report Form",
            "Expenses Tracker","Income Tracker","Certificate of Completion"]),
    ]
    col_w=W//2-40
    positions=[(30,260),(W//2+10,260),(30,H//2+30),(W//2+10,H//2+30)]
    for (cx,cy),(cat_title,count,bg,items) in zip(positions,cats):
        d.rectangle([cx,cy,cx+col_w,cy+H//2-60],fill=bg,outline=GOLD,width=3)
        d.rectangle([cx,cy,cx+col_w,cy+100],fill=GOLD)
        bb=d.textbbox((0,0),cat_title,font=font(52,bold=True)); tw=bb[2]-bb[0]
        d.text((cx+(col_w-tw)//2,cy+14),cat_title,fill=CHARCOAL,font=font(52,bold=True))
        bb2=d.textbbox((0,0),count,font=font(38)); tw2=bb2[2]-bb2[0]
        d.text((cx+(col_w-tw2)//2,cy+58),count,fill=CHARCOAL,font=font(38))
        iy=cy+118
        for item in items:
            paw_print(d,cx+34,iy+22,size=14,fill=GOLD)
            d.text((cx+60,iy),item,fill=WHITE if bg!=CREAM else CHARCOAL,font=font(36))
            iy+=56
    p=LISTING/"DT_listing_02_whats_inside.png"; img.save(p,"PNG"); print(f"  Saved {p.name}"); imgs.append(p)

    # 3 — Lifestyle
    img=Image.new("RGB",(W,H),CHARCOAL); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W,240],fill=NAVY); gold_rule(d,240,thickness=10,canvas_w=W)
    centred(d,68,"MADE FOR TRAINERS",GOLD,font(110,bold=True),canvas_w=W)
    centred(d,188,"by someone who gets it",WHITE,font(58),canvas_w=W)
    feats=[("LOOK PROFESSIONAL","from your very first client","Branded cards, appointment slips & welcome signs"),
           ("PROTECT YOUR BUSINESS","with watertight paperwork","Agreements, release forms & behaviour assessments"),
           ("TRACK EVERY CLIENT","session by session","Progress reports, homework sheets & session logs"),
           ("GROW YOUR SCHOOL","with targeted marketing","Social posts, flyers & referral cards that convert")]
    y=300
    for title,sub,detail in feats:
        d.rectangle([80,y,W-80,y+190],fill=NAVY,outline=GOLD,width=3)
        paw_print(d,160,y+95,size=50,fill=GOLD)
        d.text((260,y+28),title,fill=GOLD,font=font(68,bold=True))
        d.text((260,y+108),sub,fill=CREAM,font=font(46))
        d.text((260,y+155),detail,fill=WHITE,font=font(36))
        y+=210
    gold_rule(d,y+20,x0=80,x1=W-80,thickness=6)
    centred(d,y+50,"Fully editable in Canva — free account works perfectly",CREAM,font(54),canvas_w=W)
    d.rectangle([80,y+160,W-80,y+300],fill=GOLD)
    centred(d,y+195,"31 TEMPLATES  •  £39.99  •  INSTANT DOWNLOAD",CHARCOAL,font(62,bold=True),canvas_w=W)
    p=LISTING/"DT_listing_03_lifestyle.png"; img.save(p,"PNG"); print(f"  Saved {p.name}"); imgs.append(p)

    # 4 — How it works
    img=Image.new("RGB",(W,H),CREAM); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W,220],fill=NAVY); gold_rule(d,220,thickness=10,canvas_w=W)
    centred(d,65,"HOW IT WORKS",GOLD,font(110,bold=True),canvas_w=W)
    centred(d,160,"Three simple steps to a professional training business",WHITE,font(50),canvas_w=W)
    steps=[("1","PURCHASE & DOWNLOAD","Buy on Etsy and open the delivery PDF.","Every template link is inside, ready to go."),
           ("2","OPEN IN CANVA","Click any link to open the template in Canva.","A free Canva account is all you need."),
           ("3","CUSTOMISE & USE","Replace placeholder text with your details.","Print, share online, or send to clients.")]
    y=280
    for num,title,l1,l2 in steps:
        d.ellipse([100,y,300,y+200],fill=NAVY)
        centred(d,y+50,num,WHITE,font(120,bold=True),canvas_w=200)
        d.text((350,y+22),title,fill=NAVY,font=font(72,bold=True))
        d.text((350,y+108),l1,fill=CHARCOAL,font=font(46))
        d.text((350,y+164),l2,fill=CHARCOAL,font=font(44))
        gold_rule(d,y+220,x0=80,x1=W-80,thickness=4); y+=280
    y+=20
    d.rectangle([80,y,W-80,y+420],fill=NAVY,outline=GOLD,width=4)
    centred(d,y+30,"WHAT YOU'LL NEED",GOLD,font(70,bold=True),canvas_w=W)
    centred(d,y+120,"✓  A free Canva account (canva.com)",WHITE,font(52),canvas_w=W)
    centred(d,y+190,"✓  A printer or PDF viewer",WHITE,font(52),canvas_w=W)
    centred(d,y+260,"✓  5 minutes to add your business name",WHITE,font(52),canvas_w=W)
    centred(d,y+340,"No design experience needed!",GOLD,font(54,bold=True),canvas_w=W)
    p=LISTING/"DT_listing_04_how_it_works.png"; img.save(p,"PNG"); print(f"  Saved {p.name}"); imgs.append(p)

    # 5 — Why buy
    img=Image.new("RGB",(W,H),NAVY); d=ImageDraw.Draw(img)
    d.rectangle([0,H-200,W,H],fill=CHARCOAL); gold_rule(d,H-200,thickness=10,canvas_w=W)
    centred(d,58,"WHY CHOOSE THIS BUNDLE?",GOLD,font(100,bold=True),canvas_w=W)
    gold_rule(d,188,x0=100,x1=W-100,thickness=6)
    reasons=[("31 templates in one purchase","Save hours — everything you need, bought once."),
             ("Built for dog trainers specifically","Training agreements, homework sheets, progress reports."),
             ("Certificate of completion included","Print and hand out after every course — adds real value."),
             ("Print-ready at 300 DPI","Professional results from any printer or print shop."),
             ("Covers every area of your business","Branding, marketing, admin, and client management."),
             ("One-off purchase, yours forever","No subscriptions. Buy once, use for the life of your business.")]
    y=228
    for title,desc in reasons:
        d.rectangle([80,y,W-80,y+200],fill=WHITE,outline=GOLD,width=2)
        paw_print(d,160,y+100,size=50,fill=NAVY)
        d.text((270,y+28),title,fill=NAVY,font=font(64,bold=True))
        d.text((270,y+112),desc,fill=CHARCOAL,font=font(42))
        y+=220
    centred(d,H-160,"Instant download. No waiting. No subscriptions.",CREAM,font(54),canvas_w=W)
    centred(d,H-90,"31 templates  •  £39.99  •  Yours forever",GOLD,font(58,bold=True),canvas_w=W)
    p=LISTING/"DT_listing_05_why_buy.png"; img.save(p,"PNG"); print(f"  Saved {p.name}"); imgs.append(p)

    # 6 — Canva basics
    img=Image.new("RGB",(W,H),CREAM); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W,240],fill=NAVY); gold_rule(d,240,thickness=10,canvas_w=W)
    centred(d,65,"NEW TO CANVA?",GOLD,font(110,bold=True),canvas_w=W)
    centred(d,165,"Don't worry — it takes 5 minutes",WHITE,font(58),canvas_w=W)
    steps6=[("Go to canva.com","Create a free account in 60 seconds"),
            ("Click the template link","Opens directly in Canva — no searching"),
            ("Click any text to edit","Just type your business name and details"),
            ("Change colours if you like","Click a shape → colour picker → your brand"),
            ("Download when finished","File → Download → PDF Print or PNG"),
            ("Print or share online","Home printer, print shop, or send digitally")]
    y=280
    for i,(step,desc) in enumerate(steps6):
        d.rectangle([80,y,W-80,y+170],fill=WHITE if i%2==0 else CREAM_ALT,outline=GOLD,width=2)
        d.rectangle([80,y,220,y+170],fill=NAVY)
        centred(d,y+55,str(i+1),WHITE,font(90,bold=True),canvas_w=140)
        d.text((240,y+22),step,fill=NAVY,font=font(62,bold=True))
        d.text((240,y+100),desc,fill=CHARCOAL,font=font(44))
        y+=190
    d.rectangle([80,y+20,W-80,y+200],fill=NAVY,outline=GOLD,width=4)
    centred(d,y+55,"Canva is free and works on any device —",CREAM,font(52),canvas_w=W)
    centred(d,y+120,"phone, tablet, or laptop!",GOLD,font(62,bold=True),canvas_w=W)
    p=LISTING/"DT_listing_06_canva_basics.png"; img.save(p,"PNG"); print(f"  Saved {p.name}"); imgs.append(p)

    # 7 — Please note
    img=Image.new("RGB",(W,H),CHARCOAL); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W,240],fill=NAVY); gold_rule(d,240,thickness=10,canvas_w=W)
    centred(d,65,"PLEASE NOTE",GOLD,font(110,bold=True),canvas_w=W)
    centred(d,165,"Important information about your purchase",WHITE,font(52),canvas_w=W)
    notes=[("Digital Download Only","No physical items posted. You receive PNG template files."),
           ("Instant Delivery","Delivery PDF arrives via Etsy immediately after purchase."),
           ("Canva Free Account","All templates work with a free Canva account."),
           ("Personal & Business Use","Use these for your own dog training business only."),
           ("No Reselling","Please do not resell or redistribute the templates."),
           ("Fully Editable","All text, colours and logos are changeable in Canva."),
           ("Questions?","Message us on Etsy — we reply within 24 hours, 7 days a week.")]
    y=280
    for title,desc in notes:
        d.rectangle([80,y,W-80,y+185],fill=WHITE,outline=GOLD,width=2)
        paw_print(d,160,y+90,size=44,fill=NAVY)
        d.text((270,y+28),title,fill=NAVY,font=font(62,bold=True))
        d.text((270,y+108),desc,fill=CHARCOAL,font=font(42))
        y+=205
    p=LISTING/"DT_listing_07_please_note.png"; img.save(p,"PNG"); print(f"  Saved {p.name}"); imgs.append(p)

    return imgs


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("="*60)
    print("DOG TRAINING & PUPPY SCHOOL MEGA BUNDLE — BUILD PIPELINE")
    print("="*60)

    print("\n=== Phase 1: Building 31 Templates ===")
    print("\n  [BRANDING — 9]")
    build_business_card_dark(); build_business_card_light()
    build_appointment_card_dark(); build_appointment_card_light()
    build_loyalty_card(); build_gift_certificate()
    build_welcome_sign(); build_thank_you_card(); build_referral_card()

    print("\n  [MARKETING — 8]")
    build_flyer_group_classes(); build_flyer_1to1(); build_price_list()
    build_social_booking(); build_social_testimonial(); build_social_training_tip()
    build_social_before_after(); build_social_puppy_promo()

    print("\n  [CLIENT FORMS — 9]")
    build_training_agreement(); build_behaviour_assessment(); build_session_tracker()
    build_vaccination_record(); build_progress_report(); build_homework_sheet()
    build_photo_release(); build_invoice(); build_booking_confirmation()

    print("\n  [OPERATIONS — 5]")
    build_weekly_class_schedule(); build_incident_report()
    build_expenses_tracker(); build_income_tracker(); build_certificate()

    print("\n  ✓ All 31 templates built and uploaded.")

    print("\n=== Phase 2: Delivery PDF ===")
    pdf_path = build_delivery_pdf()

    print("\n=== Phase 3: 7 Listing Images ===")
    listing_imgs = build_listing_images()

    print("\n=== Phase 4: Creating Etsy Draft ===")
    title = "Dog Training Business Bundle | 31 Canva Templates | Puppy School Client Forms Invoice"
    description = """Dog Training & Puppy School Business Bundle — 31 Professional Canva Templates

Everything you need to launch and run a professional dog training or puppy school business.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT'S INCLUDED (31 templates)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🐾 BRANDING KIT (9 templates)
• Business Card — Dark & Light
• Appointment Card — Dark & Light
• Loyalty Card (5th session FREE)
• Gift Certificate
• Welcome Sign (A4)
• Thank You Card
• Referral Card

📣 MARKETING (8 templates)
• Group Classes Flyer (A4)
• 1-to-1 Training Flyer (A4)
• Price List / Class Schedule (A4)
• Social Post — Booking Open
• Social Post — Client Testimonial
• Social Post — Training Tip (3Ds)
• Social Post — Before & After
• Social Post — Puppy School Promo

📋 CLIENT FORMS (9 templates)
• Training Agreement
• Behaviour Assessment Form
• Session Progress Tracker
• Puppy Vaccination & Health Record
• Progress Report Card
• Homework Sheet
• Photo & Video Release Form
• Invoice
• Booking Confirmation

🗂️ OPERATIONS (5 templates)
• Weekly Class Schedule
• Incident Report Form
• Expenses Tracker
• Income Tracker
• Certificate of Completion

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HOW IT WORKS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Purchase and open your delivery PDF
2. Click any template link to open in Canva (free account works)
3. Edit placeholder text with your business details
4. Download as PDF or PNG and print or share

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHY BUY THIS BUNDLE?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Built specifically for dog trainers and puppy school owners
✅ Certificate of completion template — print after every course
✅ Navy blue palette — authoritative, professional, trust-building
✅ Print-ready at 300 DPI
✅ Fully editable — change all text, colours, logos
✅ Canva free account is all you need
✅ One-off purchase — use forever

• DIGITAL DOWNLOAD only — no physical items posted
• For your own dog training business only — no reselling
• Questions? Message us on Etsy — we reply within 24 hours"""

    tags = [
        "dog training bundle",
        "puppy school forms",
        "trainer templates",
        "puppy class canva",
        "dog training forms",
        "trainer business kit",
        "puppy school bundle",
        "dog trainer invoice",
        "behaviour assessment",
        "training agreement",
        "dog trainer branding",
        "puppy training canva",
        "dog class schedule",
    ]
    for tag in tags:
        assert len(tag) <= 20, f"Tag too long: '{tag}' ({len(tag)})"
    assert len(tags) == 13 and len(tags) == len(set(tags))

    body = urllib.parse.urlencode({
        "title": title, "description": description, "price": "39.99",
        "quantity": "999", "who_made": "i_did", "when_made": "2020_2025",
        "taxonomy_id": "1874", "type": "download", "is_supply": "false",
        "tags": ",".join(tags), "state": "draft",
    })
    result = etsy_request("POST", f"/shops/{SHOP_ID}/listings", body)
    listing_id = result["listing_id"]
    print(f"  ✓ Draft created: #{listing_id}")

    print("\n=== Phase 5: Uploading 7 Images ===")
    for rank, img_path in enumerate(listing_imgs, 1):
        res = upload_image_to_etsy(listing_id, img_path, rank)
        print(f"  rank {rank} — ID: {res['listing_image_id']}")

    imgs_check = etsy_request("GET", f"/listings/{listing_id}/images")
    print(f"\n  GET images → count: {imgs_check['count']}")
    for im in imgs_check["results"]:
        print(f"    rank {im['rank']} | ID {im['listing_image_id']}")

    print("\n=== Phase 6: Attaching PDF ===")
    fr = upload_file_to_etsy(listing_id, pdf_path)
    print(f"  File: {fr.get('filename')} | ID {fr.get('listing_file_id')}")

    files = etsy_request("GET", f"/shops/{SHOP_ID}/listings/{listing_id}/files")
    print(f"  GET files → count: {files['count']}")
    for fi in files.get("results", []):
        print(f"    {fi['filename']} | {fi['filesize']} | ID: {fi.get('listing_file_id')}")

    print(f"\n{'='*60}")
    print(f"BUNDLE 2 COMPLETE — Draft #{listing_id}")
    print(f"URL: https://www.etsy.com/listing/{listing_id}")
    print(f"{'='*60}")
    return listing_id

if __name__ == "__main__":
    listing_id = main()
