#!/usr/bin/env python3
"""
Pet Photography Mega Bundle — Full Build + Publish Pipeline
28 templates. Dusty rose #C4878E, gold #C9A96E, cream #F5F0E8, charcoal #1A1A1A
"""
import json, os, sys, time, uuid, urllib.request, urllib.error, urllib.parse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import boto3
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.pagesizes import A4 as RL_A4
from reportlab.lib import colors
from dotenv import load_dotenv

PROJECT = Path("/root/NEW-AI-PROJECT")
sys.path.insert(0, str(PROJECT / "scripts"))
load_dotenv(PROJECT / ".env")
load_dotenv(PROJECT / "purpleocaz-canva-mcp/.env", override=False)

# ── Palette ──────────────────────────────────────────────────────────────────
ROSE      = (196, 135, 142)    # #C4878E
ROSE_DARK = (160, 95, 102)     # deeper rose
GOLD      = (201, 169, 110)    # #C9A96E
CREAM     = (245, 240, 232)    # #F5F0E8
CHARCOAL  = (26, 26, 26)       # #1A1A1A
WHITE     = (255, 255, 255)
CREAM_ALT = (235, 228, 218)
BLUSH     = (240, 220, 220)    # very light rose bg

A4        = (2480, 3508)
BCARD     = (1050, 600)
GIFT_CERT = (2550, 1800)
SOCIAL    = (1080, 1080)
W = H     = 3000

FONT_BOLD    = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SERIF   = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_SERIFB  = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

def font(size, bold=False, serif=False, serifbold=False):
    if serifbold: return ImageFont.truetype(FONT_SERIFB, size)
    if serif:     return ImageFont.truetype(FONT_SERIF,  size)
    if bold:      return ImageFont.truetype(FONT_BOLD,   size)
    return ImageFont.truetype(FONT_REGULAR, size)

def centred(draw, y, text, fill, f, canvas_w=None):
    w = canvas_w or draw.im.size[0]
    bb = draw.textbbox((0,0), text, font=f); tw = bb[2]-bb[0]
    draw.text(((w-tw)//2, y), text, fill=fill, font=f)

def right(draw, x_right, y, text, fill, f):
    bb = draw.textbbox((0,0), text, font=f); tw = bb[2]-bb[0]
    draw.text((x_right-tw, y), text, fill=fill, font=f)

def gold_rule(draw, y, x0=0, x1=None, thickness=6, canvas_w=None):
    if x1 is None: x1 = canvas_w or draw.im.size[0]
    draw.rectangle([x0, y, x1, y+thickness], fill=GOLD)

def rose_bar(draw, y, h, x0=0, x1=None, canvas_w=None):
    if x1 is None: x1 = canvas_w or draw.im.size[0]
    draw.rectangle([x0, y, x1, y+h], fill=ROSE)

def section_head(draw, x, y, text, width=None, canvas_w=None):
    w = width or (canvas_w or draw.im.size[0]) - x
    draw.rectangle([x, y, x+w, y+72], fill=ROSE)
    draw.text((x+24, y+14), text, fill=WHITE, font=font(42, bold=True))
    return y+72

def field_line(draw, x, y, label, width=2240, font_size=36):
    draw.text((x, y), label, fill=CHARCOAL, font=font(font_size, bold=True))
    y += 58; draw.rectangle([x, y, x+width, y+3], fill=ROSE)
    return y+52

def field_pair(draw, x, y, label1, label2, total_w=2240, font_size=36):
    half = (total_w-60)//2
    draw.text((x, y), label1, fill=CHARCOAL, font=font(font_size, bold=True))
    draw.text((x+half+60, y), label2, fill=CHARCOAL, font=font(font_size, bold=True))
    y2 = y+58
    draw.rectangle([x, y2, x+half, y2+3], fill=ROSE)
    draw.rectangle([x+half+60, y2, x+total_w, y2+3], fill=ROSE)
    return y2+52

def field_triple(draw, x, y, labels, total_w=2240, font_size=34):
    w3 = (total_w-80)//3
    for i, lbl in enumerate(labels[:3]):
        xoff = x + i*(w3+40)
        draw.text((xoff, y), lbl, fill=CHARCOAL, font=font(font_size, bold=True))
        y2 = y+54; draw.rectangle([xoff, y2, xoff+w3, y2+3], fill=ROSE)
    return y+54+50

def checkbox(draw, x, y, label, font_size=34):
    draw.rectangle([x, y+4, x+36, y+40], outline=ROSE, width=3)
    draw.text((x+52, y+4), label, fill=CHARCOAL, font=font(font_size))
    return y+50

def table_row(draw, x, y, cols, widths, row_h=60, alt=False, header=False):
    bg = ROSE if header else (CREAM_ALT if alt else WHITE)
    fg = WHITE if header else CHARCOAL
    total_w = sum(widths)
    draw.rectangle([x, y, x+total_w, y+row_h], fill=bg)
    draw.rectangle([x, y, x+total_w, y+row_h], outline=GOLD, width=1)
    cx = x
    for i, (col, w2) in enumerate(zip(cols, widths)):
        draw.text((cx+12, y+12), str(col), fill=fg, font=font(34 if not header else 36, bold=header))
        if i < len(cols)-1: draw.line([(cx+w2, y),(cx+w2, y+row_h)], fill=GOLD, width=1)
        cx += w2
    return y+row_h

def paw_print(draw, cx_, cy_, size=60, fill=GOLD):
    pad_w = int(size*1.0); pad_h = int(size*1.15)
    draw.ellipse([cx_-pad_w, cy_-pad_h//2, cx_+pad_w, cy_+pad_h+pad_h//2], fill=fill)
    tr = int(size*0.38); toe_y = int(size*1.55)
    for tx,ty in [(cx_-int(size*0.95),cy_-toe_y+int(tr*0.3)),(cx_-int(size*0.38),cy_-toe_y-int(tr*0.4)),
                  (cx_+int(size*0.38),cy_-toe_y-int(tr*0.4)),(cx_+int(size*0.95),cy_-toe_y+int(tr*0.3))]:
        draw.ellipse([tx-tr, ty-tr, tx+tr, ty+tr], fill=fill)

def camera_icon(draw, cx, cy, size=60, fill=GOLD):
    """Simple camera outline shape."""
    bw=int(size*2.2); bh=int(size*1.6)
    draw.rectangle([cx-bw//2,cy-bh//2+int(size*0.2),cx+bw//2,cy+bh//2+int(size*0.2)],
                   outline=fill, width=max(3,size//15))
    draw.ellipse([cx-size//2,cy-size//2+int(size*0.2),cx+size//2,cy+size//2+int(size*0.2)],
                 outline=fill, width=max(3,size//15))
    draw.rectangle([cx-int(size*0.2),cy-bh//2,cx+int(size*0.4),cy-bh//2+int(size*0.35)],fill=fill)

def a4_header(img, draw, title, subtitle="Professional Pet Photography"):
    W2 = img.width
    draw.rectangle([0,0,W2,420], fill=ROSE)
    camera_icon(draw, 180, 210, size=75, fill=GOLD)
    draw.text((300,80), "YOUR BUSINESS NAME", fill=GOLD, font=font(56,bold=True))
    draw.text((300,155), subtitle, fill=CREAM, font=font(38))
    centred(draw, 255, title, WHITE, font(66,bold=True), canvas_w=W2)
    gold_rule(draw, 420, thickness=8, canvas_w=W2)
    return 460

def a4_footer(draw, canvas_w, canvas_h):
    draw.rectangle([0,canvas_h-100,canvas_w,canvas_h], fill=ROSE)
    gold_rule(draw, canvas_h-100, thickness=6, canvas_w=canvas_w)
    centred(draw, canvas_h-76, "© PurpleOcaz — purpleocaz.etsy.com", CREAM, font(30), canvas_w=canvas_w)

def upload_to_spaces(local_path, spaces_key, content_type="image/png"):
    load_dotenv("/root/NEW-AI-PROJECT/purpleocaz-canva-mcp/.env")
    s3 = boto3.client("s3", endpoint_url="https://lon1.digitaloceanspaces.com",
        aws_access_key_id=os.environ["DO_SPACES_KEY"],
        aws_secret_access_key=os.environ["DO_SPACES_SECRET"])
    s3.upload_file(str(local_path), "purpleocaz-assets", spaces_key,
        ExtraArgs={"ACL":"public-read","ContentType":content_type})
    url = f"https://purpleocaz-assets.lon1.digitaloceanspaces.com/{spaces_key}"
    resp = urllib.request.urlopen(url)
    assert resp.status == 200
    print(f"  ↑ {spaces_key} → HTTP 200")
    return url

OUT     = PROJECT / "outputs/pet-photography"
TMPL    = OUT / "templates"
LISTING = OUT / "listing"
for d in [TMPL, LISTING]: d.mkdir(parents=True, exist_ok=True)

CDN        = "https://purpleocaz-assets.lon1.digitaloceanspaces.com"
TOKEN_FILE = PROJECT / "workflows/etsy_analytics/etsy_tokens.json"
ETSY_BASE  = "https://openapi.etsy.com/v3/application"
API_KEY    = os.getenv("ETSY_API_KEYSTRING","")
SECRET     = os.getenv("ETSY_SHARED_SECRET","")
SHOP_ID    = os.getenv("ETSY_SHOP_ID","34071205")
X_API_KEY  = f"{API_KEY}:{SECRET}"
NICHE, PFX = "pet-photography", "PP"


# ── Etsy helpers ──────────────────────────────────────────────────────────────

def load_tokens():
    with open(TOKEN_FILE) as f: return json.load(f)

def etsy_request(method, path, body=None, content_type="application/x-www-form-urlencoded", retries=2):
    tokens = load_tokens()
    data = body.encode() if isinstance(body, str) else body
    req = urllib.request.Request(f"{ETSY_BASE}{path}", data=data, method=method)
    req.add_header("x-api-key", X_API_KEY)
    req.add_header("Authorization", f"Bearer {tokens['access_token']}")
    if body and content_type: req.add_header("Content-Type", content_type)
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read(); return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        body_str = e.read().decode()
        if e.code == 401 and retries:
            time.sleep(2); return etsy_request(method, path, body, content_type, retries-1)
        raise RuntimeError(f"Etsy {method} {path} -> {e.code}: {body_str}")

def upload_image_to_etsy(listing_id, img_path, rank):
    tokens = load_tokens(); boundary = uuid.uuid4().hex
    img_data = open(img_path,"rb").read()
    body  = f"--{boundary}\r\nContent-Disposition: form-data; name=\"rank\"\r\n\r\n{rank}\r\n".encode()
    body += f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{img_path.name}\"\r\nContent-Type: image/png\r\n\r\n".encode()
    body += img_data + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(f"{ETSY_BASE}/shops/{SHOP_ID}/listings/{listing_id}/images",data=body,method="POST")
    req.add_header("x-api-key",X_API_KEY); req.add_header("Authorization",f"Bearer {tokens['access_token']}")
    req.add_header("Content-Type",f"multipart/form-data; boundary={boundary}")
    with urllib.request.urlopen(req) as resp: return json.loads(resp.read())

def upload_file_to_etsy(listing_id, pdf_path):
    tokens = load_tokens(); boundary = uuid.uuid4().hex; filename = pdf_path.name
    pdf_data = open(pdf_path,"rb").read()
    body  = f"--{boundary}\r\nContent-Disposition: form-data; name=\"name\"\r\n\r\n{filename}\r\n".encode()
    body += f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{filename}\"\r\nContent-Type: application/pdf\r\n\r\n".encode()
    body += pdf_data + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(f"{ETSY_BASE}/shops/{SHOP_ID}/listings/{listing_id}/files",data=body,method="POST")
    req.add_header("x-api-key",X_API_KEY); req.add_header("Authorization",f"Bearer {tokens['access_token']}")
    req.add_header("Content-Type",f"multipart/form-data; boundary={boundary}")
    with urllib.request.urlopen(req) as resp: return json.loads(resp.read())

def save_upload(img, filename, spaces_key):
    path = TMPL/filename; img.save(path,"PNG")
    upload_to_spaces(path, spaces_key); return path


# ══════════════════════════════════════════════════════════════════════════════
# BRANDING (8)
# ══════════════════════════════════════════════════════════════════════════════

def build_business_card_dark():
    W2,H2=BCARD; img=Image.new("RGB",(W2,H2),CHARCOAL); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W2,18],fill=GOLD); d.rectangle([0,H2-18,W2,H2],fill=GOLD)
    d.rectangle([0,18,12,H2-18],fill=ROSE)
    camera_icon(d,W2-130,130,size=52,fill=ROSE)
    d.text((60,70),"YOUR BUSINESS NAME",fill=GOLD,font=font(52,bold=True))
    d.text((60,140),"Professional Pet Photography",fill=CREAM,font=font(34))
    gold_rule(d,195,x0=60,x1=W2-60,thickness=3)
    d.text((60,215),"yourname@email.com",fill=WHITE,font=font(30))
    d.text((60,260),"07700 000000",fill=WHITE,font=font(30))
    d.text((60,305),"www.yourwebsite.co.uk",fill=WHITE,font=font(30))
    d.text((60,370),"@YourInstagram",fill=GOLD,font=font(28,bold=True))
    return save_upload(img,f"{PFX}_Business_Card_Dark.png",f"templates/{NICHE}/branding/{PFX}_Business_Card_Dark.png")

def build_business_card_light():
    W2,H2=BCARD; img=Image.new("RGB",(W2,H2),CREAM); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W2,18],fill=ROSE); d.rectangle([0,H2-18,W2,H2],fill=ROSE)
    d.rectangle([0,18,12,H2-18],fill=GOLD)
    camera_icon(d,W2-130,130,size=52,fill=ROSE)
    d.text((60,70),"YOUR BUSINESS NAME",fill=ROSE,font=font(52,bold=True))
    d.text((60,140),"Professional Pet Photography",fill=CHARCOAL,font=font(34))
    gold_rule(d,195,x0=60,x1=W2-60,thickness=3)
    d.text((60,215),"yourname@email.com",fill=CHARCOAL,font=font(30))
    d.text((60,260),"07700 000000",fill=CHARCOAL,font=font(30))
    d.text((60,305),"www.yourwebsite.co.uk",fill=CHARCOAL,font=font(30))
    d.text((60,370),"@YourInstagram",fill=ROSE,font=font(28,bold=True))
    return save_upload(img,f"{PFX}_Business_Card_Light.png",f"templates/{NICHE}/branding/{PFX}_Business_Card_Light.png")

def build_appointment_card_dark():
    W2,H2=BCARD; img=Image.new("RGB",(W2,H2),CHARCOAL); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W2,18],fill=GOLD); d.rectangle([0,H2-18,W2,H2],fill=GOLD)
    d.rectangle([0,18,12,H2-18],fill=ROSE)
    d.text((60,55),"YOUR BUSINESS NAME",fill=GOLD,font=font(42,bold=True))
    d.text((60,110),"SESSION BOOKING CONFIRMED",fill=WHITE,font=font(34,bold=True))
    gold_rule(d,158,x0=60,x1=W2-60,thickness=3)
    for label,yy in [("Date:",175),("Time:",218),("Package:",261),("Location:",304)]:
        d.text((60,yy),label,fill=CREAM,font=font(30,bold=True))
        d.rectangle([60+len(label)*18,yy+23,720,yy+25],fill=GOLD)
    d.text((60,370),"07700 000000  |  yourwebsite.co.uk",fill=GOLD,font=font(26))
    return save_upload(img,f"{PFX}_Appointment_Card_Dark.png",f"templates/{NICHE}/branding/{PFX}_Appointment_Card_Dark.png")

def build_appointment_card_light():
    W2,H2=BCARD; img=Image.new("RGB",(W2,H2),CREAM); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W2,18],fill=ROSE); d.rectangle([0,H2-18,W2,H2],fill=ROSE)
    d.rectangle([0,18,12,H2-18],fill=GOLD)
    d.text((60,55),"YOUR BUSINESS NAME",fill=ROSE,font=font(42,bold=True))
    d.text((60,110),"SESSION BOOKING CONFIRMED",fill=CHARCOAL,font=font(34,bold=True))
    gold_rule(d,158,x0=60,x1=W2-60,thickness=3)
    for label,yy in [("Date:",175),("Time:",218),("Package:",261),("Location:",304)]:
        d.text((60,yy),label,fill=CHARCOAL,font=font(30,bold=True))
        d.rectangle([60+len(label)*18,yy+23,720,yy+25],fill=ROSE)
    d.text((60,370),"07700 000000  |  yourwebsite.co.uk",fill=ROSE,font=font(26))
    return save_upload(img,f"{PFX}_Appointment_Card_Light.png",f"templates/{NICHE}/branding/{PFX}_Appointment_Card_Light.png")

def build_gift_certificate():
    W2,H2=GIFT_CERT; img=Image.new("RGB",(W2,H2),CREAM); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W2,40],fill=ROSE); d.rectangle([0,H2-40,W2,H2],fill=ROSE)
    d.rectangle([0,40,40,H2-40],fill=ROSE); d.rectangle([W2-40,40,W2,H2-40],fill=ROSE)
    d.rectangle([55,55,W2-55,H2-55],outline=GOLD,width=4)
    camera_icon(d,140,150,size=60,fill=GOLD); camera_icon(d,W2-140,150,size=60,fill=GOLD)
    paw_print(d,140,H2-150,size=50,fill=GOLD); paw_print(d,W2-140,H2-150,size=50,fill=GOLD)
    centred(d,90,"GIFT CERTIFICATE",ROSE,font(90,bold=True),canvas_w=W2)
    gold_rule(d,210,x0=100,x1=W2-100,thickness=4)
    centred(d,235,"Professional Pet Photography Session",CHARCOAL,font(52),canvas_w=W2)
    gold_rule(d,310,x0=100,x1=W2-100,thickness=4)
    centred(d,360,"This certificate entitles",CHARCOAL,font(44),canvas_w=W2)
    d.rectangle([300,450,W2-300,453],fill=ROSE)
    centred(d,465,"(Recipient Name)",CHARCOAL,font(34),canvas_w=W2)
    centred(d,530,"to a",CHARCOAL,font(44),canvas_w=W2)
    d.rectangle([300,600,W2-300,603],fill=ROSE)
    centred(d,615,"(Package / Session Type)",CHARCOAL,font(34),canvas_w=W2)
    centred(d,680,"with",CHARCOAL,font(40),canvas_w=W2)
    centred(d,740,"YOUR BUSINESS NAME",ROSE,font(64,bold=True),canvas_w=W2)
    gold_rule(d,840,x0=100,x1=W2-100,thickness=3)
    d.text((150,890),"Valid until: _________________",CHARCOAL,font=font(38))
    d.text((150,945),"Certificate #: _______________",CHARCOAL,font=font(38))
    right(d,W2-150,890,"Signed: _________________",CHARCOAL,font(38))
    right(d,W2-150,945,"Date:   _________________",CHARCOAL,font(38))
    centred(d,1030,"07700 000000  |  www.yourwebsite.co.uk",CHARCOAL,font(36),canvas_w=W2)
    centred(d,1080,"@YourInstagram  |  yourwebsite.co.uk",ROSE,font(32),canvas_w=W2)
    return save_upload(img,f"{PFX}_Gift_Certificate.png",f"templates/{NICHE}/branding/{PFX}_Gift_Certificate.png")

def build_welcome_sign():
    W2,H2=A4; img=Image.new("RGB",(W2,H2),CREAM); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W2,340],fill=ROSE); d.rectangle([0,H2-180,W2,H2],fill=ROSE)
    gold_rule(d,340,thickness=10,canvas_w=W2); gold_rule(d,H2-180,thickness=10,canvas_w=W2)
    camera_icon(d,160,170,size=80,fill=GOLD); camera_icon(d,W2-160,170,size=80,fill=GOLD)
    centred(d,55,"WELCOME!", WHITE,font(120,bold=True),canvas_w=W2)
    centred(d,195,"YOUR BUSINESS NAME",GOLD,font(60,bold=True),canvas_w=W2)
    centred(d,270,"Professional Pet Photography",CREAM,font(44),canvas_w=W2)
    centred(d,395,"So excited to capture your pet's personality!",CHARCOAL,font(50),canvas_w=W2)
    gold_rule(d,480,x0=120,x1=W2-120,thickness=4)
    y=520
    for line in ["Your Name:","Pet Name(s):","Session type:","Special requests:","Parking / access notes:"]:
        d.text((120,y),line,CHARCOAL,font=font(42,bold=True))
        d.rectangle([120,y+58,W2-120,y+62],fill=ROSE); y+=120
    gold_rule(d,H2-240,x0=120,x1=W2-120,thickness=4)
    centred(d,H2-210,"07700 000000  |  www.yourwebsite.co.uk",WHITE,font(38),canvas_w=W2)
    centred(d,H2-155,"@YourInstagram",GOLD,font(36),canvas_w=W2)
    centred(d,H2-100,"© PurpleOcaz — purpleocaz.etsy.com",CREAM,font(30),canvas_w=W2)
    return save_upload(img,f"{PFX}_Welcome_Sign.png",f"templates/{NICHE}/branding/{PFX}_Welcome_Sign.png")

def build_thank_you_card():
    W2,H2=BCARD; img=Image.new("RGB",(W2,H2),ROSE); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W2,16],fill=GOLD); d.rectangle([0,H2-16,W2,H2],fill=GOLD)
    camera_icon(d,W2-110,100,size=48,fill=GOLD)
    centred(d,38,"THANK YOU!",GOLD,font(70,bold=True),canvas_w=W2)
    centred(d,128,"for booking your pet photography session.",CREAM,font(28),canvas_w=W2)
    gold_rule(d,175,x0=60,x1=W2-60,thickness=3)
    centred(d,195,"Your gallery will be ready within",WHITE,font(28),canvas_w=W2)
    centred(d,235,"[X] days. We hope you love every shot!",CREAM,font(26),canvas_w=W2)
    gold_rule(d,280,x0=60,x1=W2-60,thickness=3)
    d.text((60,300),"YOUR BUSINESS NAME",fill=GOLD,font=font(32,bold=True))
    d.text((60,345),"07700 000000",fill=CREAM,font=font(28))
    d.text((60,385),"@YourInstagram",fill=CREAM,font=font(28))
    d.text((60,430),"Tag us in your favourites!",fill=GOLD,font=font(26,bold=True))
    return save_upload(img,f"{PFX}_Thank_You_Card.png",f"templates/{NICHE}/branding/{PFX}_Thank_You_Card.png")

def build_referral_card():
    W2,H2=BCARD; img=Image.new("RGB",(W2,H2),CHARCOAL); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W2,16],fill=ROSE); d.rectangle([0,H2-16,W2,H2],fill=ROSE)
    camera_icon(d,W2-110,110,size=48,fill=ROSE)
    centred(d,32,"REFER A FRIEND",GOLD,font(60,bold=True),canvas_w=W2)
    centred(d,105,"& EARN A FREE PRINT!",WHITE,font(38,bold=True),canvas_w=W2)
    gold_rule(d,158,x0=60,x1=W2-60,thickness=3)
    centred(d,178,"Refer a friend who books a session",CREAM,font(26),canvas_w=W2)
    centred(d,212,"and YOU receive a free 10x8 print!",CREAM,font(26),canvas_w=W2)
    gold_rule(d,256,x0=60,x1=W2-60,thickness=3)
    d.text((60,276),"Referred by:",fill=CREAM,font=font(28,bold=True))
    d.rectangle([240,300,700,303],fill=GOLD)
    d.text((60,325),"Referee name:",fill=CREAM,font=font(28,bold=True))
    d.rectangle([280,350,700,353],fill=GOLD)
    d.text((60,372),"YOUR BUSINESS NAME",fill=ROSE,font=font(30,bold=True))
    d.text((60,412),"07700 000000",fill=GOLD,font=font(28))
    d.text((60,452),"Ts&Cs apply. One per booking.",fill=WHITE,font=font(24))
    return save_upload(img,f"{PFX}_Referral_Card.png",f"templates/{NICHE}/branding/{PFX}_Referral_Card.png")


# ══════════════════════════════════════════════════════════════════════════════
# MARKETING (7)
# ══════════════════════════════════════════════════════════════════════════════

def build_flyer_mini_session():
    W2,H2=A4; img=Image.new("RGB",(W2,H2),CREAM); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W2,480],fill=ROSE); d.rectangle([0,H2-160,W2,H2],fill=ROSE)
    gold_rule(d,480,thickness=10,canvas_w=W2); gold_rule(d,H2-160,thickness=10,canvas_w=W2)
    camera_icon(d,140,240,size=90,fill=GOLD); camera_icon(d,W2-140,240,size=90,fill=GOLD)
    centred(d,55,"YOUR BUSINESS NAME",GOLD,font(72,bold=True),canvas_w=W2)
    centred(d,155,"MINI SESSION EVENT",CREAM,font(58,bold=True),canvas_w=W2)
    centred(d,245,"Professional Pet Photography",WHITE,font(42),canvas_w=W2)
    centred(d,315,"[Date]  |  [Location]",CREAM,font(38),canvas_w=W2)
    y=530
    items=[("Session Length","20 minutes with your pet"),
           ("Digital Images","5 fully edited high-res photos"),
           ("Turnaround","Gallery delivered within [X] days"),
           ("What to bring","Your pet, their favourite treat & lead"),
           ("Price","£XX.00 per session — book in advance")]
    for k,v in items:
        d.rectangle([80,y,W2-80,y+140],fill=WHITE,outline=GOLD,width=2)
        camera_icon(d,145,y+70,size=28,fill=ROSE)
        d.text((210,y+20),k+":",fill=ROSE,font=font(46,bold=True))
        d.text((210,y+78),v,fill=CHARCOAL,font=font(36))
        y+=155
    gold_rule(d,y+10,x0=80,x1=W2-80,thickness=4)
    centred(d,y+30,"Spaces strictly limited — book today!",CHARCOAL,font(42,bold=True),canvas_w=W2)
    centred(d,H2-130,"07700 000000  |  www.yourwebsite.co.uk  |  @YourInstagram",CREAM,font(36),canvas_w=W2)
    centred(d,H2-80,"© PurpleOcaz — purpleocaz.etsy.com",CREAM,font(28),canvas_w=W2)
    return save_upload(img,f"{PFX}_Flyer_Mini_Session.png",f"templates/{NICHE}/marketing/{PFX}_Flyer_Mini_Session.png")

def build_flyer_seasonal():
    W2,H2=A4; img=Image.new("RGB",(W2,H2),CHARCOAL); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W2,420],fill=ROSE); d.rectangle([0,H2-160,W2,H2],fill=ROSE)
    gold_rule(d,420,thickness=10,canvas_w=W2); gold_rule(d,H2-160,thickness=10,canvas_w=W2)
    camera_icon(d,W2-160,210,size=80,fill=GOLD)
    centred(d,55,"SEASONAL SPECIAL",GOLD,font(90,bold=True),canvas_w=W2)
    centred(d,168,"YOUR BUSINESS NAME",CREAM,font(52),canvas_w=W2)
    centred(d,248,"Professional Pet Photography",WHITE,font(42),canvas_w=W2)
    d.rectangle([80,460,W2-80,670],fill=ROSE,outline=GOLD,width=4)
    centred(d,490,"[SEASON/EVENT]",GOLD,font(72,bold=True),canvas_w=W2)
    centred(d,575,"PHOTO SESSIONS",WHITE,font(68,bold=True),canvas_w=W2)
    centred(d,655,"Now booking — limited availability!",CREAM,font(36),canvas_w=W2)
    y=710
    for b in ["✔  Themed backdrop & props included",
              "✔  5 fully edited digital images delivered",
              "✔  Perfect for Christmas cards & gifts",
              "✔  Outdoor or studio — your choice",
              "✔  All breeds & sizes welcome"]:
        d.text((120,y),b,fill=WHITE,font=font(38)); y+=68
    gold_rule(d,y+20,x0=80,x1=W2-80,thickness=4)
    centred(d,y+50,"Book before [DATE] for early bird pricing!",GOLD,font(40,bold=True),canvas_w=W2)
    centred(d,H2-130,"07700 000000  |  www.yourwebsite.co.uk",CREAM,font(38),canvas_w=W2)
    centred(d,H2-80,"© PurpleOcaz — purpleocaz.etsy.com",CREAM,font(28),canvas_w=W2)
    return save_upload(img,f"{PFX}_Flyer_Seasonal.png",f"templates/{NICHE}/marketing/{PFX}_Flyer_Seasonal.png")

def build_pricing_guide():
    W2,H2=A4; img=Image.new("RGB",(W2,H2),CREAM); d=ImageDraw.Draw(img)
    y=a4_header(img,d,"PRICING GUIDE","Professional Pet Photography")
    y=section_head(d,80,y,"MINI SESSIONS",width=W2-160); y+=10
    hdr=["Package","Includes","Price"]
    wids=[500,1060,560]
    y=table_row(d,80,y,hdr,wids,header=True)
    for i,row in enumerate([
        ("Mini Session","20 min  •  5 edited images  •  online gallery","£XX.00"),
        ("Standard Session","45 min  •  15 edited images  •  online gallery","£XX.00"),
        ("Extended Session","90 min  •  30 edited images  •  online gallery","£XX.00"),
    ]):
        y=table_row(d,80,y,row,wids,alt=bool(i%2),row_h=85)
    y+=20
    y=section_head(d,80,y,"PACKAGES",width=W2-160); y+=10
    wids2=[500,1060,560]
    y=table_row(d,80,y,["Package","Includes","Price"],wids2,header=True)
    for i,row in enumerate([
        ("Starter Package","30 min  •  10 images  •  1 x A4 print","£XX.00"),
        ("Premium Package","60 min  •  20 images  •  canvas print","£XX.00"),
        ("Family Pets Package","90 min  •  30 images  •  photo book","£XX.00"),
        ("Annual Package","4 sessions (quarterly)  •  20 images each","£XX.00"),
    ]):
        y=table_row(d,80,y,row,wids2,alt=bool(i%2),row_h=85)
    y+=20
    y=section_head(d,80,y,"PRINT PRODUCTS (ADD-ONS)",width=W2-160); y+=10
    wids3=[700,920,500]
    y=table_row(d,80,y,["Product","Specification","Price"],wids3,header=True)
    for i,row in enumerate([
        ("Digital image (single)","Full-res download","£XX.00"),
        ("A4 print","Lustre finish, professionally printed","£XX.00"),
        ("A3 print","Lustre finish, professionally printed","£XX.00"),
        ("Canvas 12x16","Gallery-wrap canvas","£XX.00"),
        ("Photo book (20 pages)","Hardcover, lay-flat","£XX.00"),
    ]):
        y=table_row(d,80,y,row,wids3,alt=bool(i%2),row_h=80)
    y+=20
    d.text((80,y),"* All prices editable. Travel fees may apply outside [radius]. Contact for quotes.",
           fill=CHARCOAL,font=font(30))
    a4_footer(d,W2,H2)
    return save_upload(img,f"{PFX}_Pricing_Guide.png",f"templates/{NICHE}/marketing/{PFX}_Pricing_Guide.png")

def _social_base(bg,accent):
    S=SOCIAL[0]; img=Image.new("RGB",SOCIAL,bg); d=ImageDraw.Draw(img)
    d.rectangle([0,0,S,16],fill=accent); d.rectangle([0,S-16,S,S],fill=accent)
    d.rectangle([0,16,16,S-16],fill=accent); d.rectangle([S-16,16,S,S-16],fill=accent)
    return img,d,S

def build_social_booking():
    img,d,S=_social_base(ROSE,GOLD)
    camera_icon(d,S-100,100,size=55,fill=GOLD)
    paw_print(d,100,S-100,size=40,fill=GOLD)
    centred(d,78,"SESSIONS NOW BOOKING",GOLD,font(72,bold=True),canvas_w=S)
    centred(d,170,"Limited spaces available!",WHITE,font(52),canvas_w=S)
    gold_rule(d,255,x0=80,x1=S-80,thickness=5)
    centred(d,295,"Mini Sessions",CREAM,font(46),canvas_w=S)
    centred(d,360,"Full Portrait Sessions",CREAM,font(46),canvas_w=S)
    centred(d,425,"Seasonal & Themed Sessions",CREAM,font(46),canvas_w=S)
    d.rectangle([80,510,S-80,660],fill=GOLD,outline=WHITE,width=3)
    centred(d,540,"Book your FREE consultation",ROSE,font(54,bold=True),canvas_w=S)
    centred(d,610,"today →",CHARCOAL,font(46,bold=True),canvas_w=S)
    centred(d,715,"YOUR BUSINESS NAME",GOLD,font(52,bold=True),canvas_w=S)
    centred(d,780,"Professional Pet Photography",WHITE,font(40),canvas_w=S)
    centred(d,848,"07700 000000",CREAM,font(44),canvas_w=S)
    centred(d,925,"Follow for portfolio & offers!",CREAM,font(36),canvas_w=S)
    return save_upload(img,f"{PFX}_Social_Booking.png",f"templates/{NICHE}/marketing/{PFX}_Social_Booking.png")

def build_social_portfolio():
    img,d,S=_social_base(CHARCOAL,ROSE)
    d.rectangle([0,0,S,130],fill=ROSE)
    camera_icon(d,80,65,size=45,fill=GOLD); camera_icon(d,S-80,65,size=45,fill=GOLD)
    centred(d,22,"PORTFOLIO SHOWCASE",GOLD,font(62,bold=True),canvas_w=S)
    centred(d,92,"Recent work we're proud of",WHITE,font(40),canvas_w=S)
    # Photo placeholder grid
    pad=30; cell=(S-pad*3)//2
    for row in range(2):
        for col in range(2):
            bx=pad+col*(cell+pad); by=155+row*(cell+pad)
            d.rectangle([bx,by,bx+cell,by+cell],fill=ROSE,outline=GOLD,width=3)
            centred(d,by+cell//2-30,"Add your photo",CREAM,font(36),canvas_w=cell)
            centred(d,by+cell//2+10,"here",CREAM,font(36),canvas_w=cell)
    y=155+2*(cell+pad)+20
    gold_rule(d,y,x0=40,x1=S-40,thickness=4)
    centred(d,y+30,"Swipe for more →",CREAM,font(40,bold=True),canvas_w=S)
    centred(d,y+90,"YOUR BUSINESS NAME",GOLD,font(52,bold=True),canvas_w=S)
    centred(d,y+155,"07700 000000  |  @YourInstagram",CREAM,font(38),canvas_w=S)
    return save_upload(img,f"{PFX}_Social_Portfolio.png",f"templates/{NICHE}/marketing/{PFX}_Social_Portfolio.png")

def build_social_bts():
    img,d,S=_social_base(CREAM,ROSE)
    d.rectangle([0,0,S,130],fill=CHARCOAL)
    centred(d,25,"BEHIND THE LENS",GOLD,font(68,bold=True),canvas_w=S)
    centred(d,95,"A peek into a pet photo session",CREAM,font(40),canvas_w=S)
    gold_rule(d,140,x0=60,x1=S-60,thickness=5)
    steps=[("Getting comfortable","We always start with play time —",
            "a relaxed pet = a happy pet = great shots!"),
           ("Finding the light","Natural light at golden hour is magic","for warm, dreamy pet portraits."),
           ("The magic moment","Patience is everything. We wait for",
            "the ears-perked, eyes-bright moment.")]
    y=165
    for title,l1,l2 in steps:
        d.rectangle([60,y,S-60,y+210],fill=ROSE,outline=GOLD,width=2)
        camera_icon(d,120,y+105,size=42,fill=GOLD)
        d.text((195,y+25),title,fill=WHITE,font=font(52,bold=True))
        d.text((195,y+90),l1,fill=CREAM,font=font(36))
        d.text((195,y+138),l2,fill=CREAM,font=font(36))
        y+=230
    d.rectangle([60,y+10,S-60,y+140],fill=CHARCOAL)
    centred(d,y+40,"YOUR BUSINESS NAME",GOLD,font(52,bold=True),canvas_w=S)
    centred(d,y+95,"Professional Pet Photography  |  @YourInstagram",CREAM,font(36),canvas_w=S)
    return save_upload(img,f"{PFX}_Social_BTS.png",f"templates/{NICHE}/marketing/{PFX}_Social_BTS.png")

def build_social_testimonial():
    img,d,S=_social_base(CREAM,ROSE)
    camera_icon(d,S//2,115,size=60,fill=ROSE)
    centred(d,195,"\u201cAbsolutely stunning photos!\u201d",CHARCOAL,font(56,serifbold=True),canvas_w=S)
    gold_rule(d,278,x0=100,x1=S-100,thickness=4)
    centred(d,312,"\u201cI couldn\u2019t believe how well she captured",CHARCOAL,font(40,serif=True),canvas_w=S)
    centred(d,368,"my dog\u2019s personality. Every shot is perfect.",CHARCOAL,font(40,serif=True),canvas_w=S)
    centred(d,424,"We have them all over our walls!\u201d",CHARCOAL,font(40,serif=True),canvas_w=S)
    gold_rule(d,502,x0=100,x1=S-100,thickness=4)
    centred(d,538,"— Emma & Coco, Happy Client",ROSE,font(40,bold=True),canvas_w=S)
    d.rectangle([80,630,S-80,650],fill=GOLD)
    centred(d,682,"\u2b50\u2b50\u2b50\u2b50\u2b50  5-Star Review",CHARCOAL,font(44,bold=True),canvas_w=S)
    d.rectangle([80,772,S-80,892],fill=ROSE)
    centred(d,805,"YOUR BUSINESS NAME",GOLD,font(54,bold=True),canvas_w=S)
    centred(d,858,"Professional Pet Photography",WHITE,font(38),canvas_w=S)
    centred(d,940,"07700 000000  |  @YourInstagram",CHARCOAL,font(34),canvas_w=S)
    return save_upload(img,f"{PFX}_Social_Testimonial.png",f"templates/{NICHE}/marketing/{PFX}_Social_Testimonial.png")

def build_social_seasonal_promo():
    img,d,S=_social_base(ROSE,GOLD)
    paw_print(d,S-120,120,size=65,fill=GOLD); paw_print(d,120,S-120,size=50,fill=GOLD)
    centred(d,60,"[SEASON] SESSIONS",GOLD,font(80,bold=True),canvas_w=S)
    centred(d,160,"NOW BOOKING",WHITE,font(68,bold=True),canvas_w=S)
    gold_rule(d,248,x0=80,x1=S-80,thickness=5)
    centred(d,282,"Perfect for Christmas cards,",CREAM,font(46),canvas_w=S)
    centred(d,342,"gifts and memories that last forever.",CREAM,font(46),canvas_w=S)
    d.rectangle([80,415,S-80,640],fill=GOLD)
    centred(d,440,"BOOK 5 SESSIONS",ROSE,font(58,bold=True),canvas_w=S)
    centred(d,510,"GET THE 6TH FREE",CHARCOAL,font(68,bold=True),canvas_w=S)
    centred(d,590,"Themed backdrops & props included",CHARCOAL,font(38,bold=True),canvas_w=S)
    gold_rule(d,665,x0=80,x1=S-80,thickness=5)
    centred(d,700,"Valid until: [DATE]",CREAM,font(44),canvas_w=S)
    centred(d,760,"Quote: [CODE] when booking",CREAM,font(40),canvas_w=S)
    centred(d,832,"YOUR BUSINESS NAME",CREAM,font(52,bold=True),canvas_w=S)
    centred(d,898,"07700 000000",WHITE,font(44),canvas_w=S)
    centred(d,972,"Book today — strictly limited!",GOLD,font(44,bold=True),canvas_w=S)
    return save_upload(img,f"{PFX}_Social_Seasonal_Promo.png",f"templates/{NICHE}/marketing/{PFX}_Social_Seasonal_Promo.png")


# ══════════════════════════════════════════════════════════════════════════════
# CLIENT FORMS (7)
# ══════════════════════════════════════════════════════════════════════════════

def build_booking_form():
    W2,H2=A4; img=Image.new("RGB",(W2,H2),WHITE); d=ImageDraw.Draw(img)
    y=a4_header(img,d,"PHOTOGRAPHY BOOKING FORM")
    y=section_head(d,80,y+10,"CLIENT DETAILS",width=W2-160); y+=14
    y=field_pair(d,120,y,"Client Full Name:","Phone:",total_w=2240)
    y=field_pair(d,120,y,"Email Address:","Address:",total_w=2240)
    y=field_pair(d,120,y,"How did you hear about us?","Referred by (if applicable):",total_w=2240)
    y+=8
    y=section_head(d,80,y,"PET DETAILS",width=W2-160); y+=14
    y=field_triple(d,120,y,["Pet Name:","Species/Breed:","Age:"],total_w=2240)
    y=field_triple(d,120,y,["Gender:","Colour:","Neutered?"],total_w=2240)
    y=field_line(d,120,y,"Any quirks, fears or things we should know?",width=2240)
    y+=8
    y=section_head(d,80,y,"SESSION DETAILS",width=W2-160); y+=14
    y=field_pair(d,120,y,"Session type / package:","Price agreed: £",total_w=2240)
    y=field_pair(d,120,y,"Date requested:","Time:",total_w=2240)
    y=field_pair(d,120,y,"Location:","Backup date:",total_w=2240)
    y=field_line(d,120,y,"Props / themes / specific shots requested:",width=2240)
    y+=8
    y=section_head(d,80,y,"BOOKING TERMS",width=W2-160); y+=14
    for term in [
        "A 25% non-refundable deposit is required to secure the date.",
        "Remaining balance is due 48 hours before the session.",
        "Cancellation within 48 hours forfeits the deposit.",
        "Photographer may reschedule due to severe weather.",
        "Images will be delivered via online gallery within [X] days.",
        "Client grants permission to use images for portfolio/marketing unless opted out below.",
    ]:
        paw_print(d,110,y+18,size=14,fill=ROSE)
        d.text((145,y),term,fill=CHARCOAL,font=font(30)); y+=50
    y+=8
    y=checkbox(d,120,y,"I opt OUT of my pet's images being used in marketing",font_size=32)
    y+=20
    d.text((120,y),"Client Signature:",CHARCOAL,font=font(36,bold=True))
    d.rectangle([120,y+58,1100,y+61],fill=ROSE)
    d.text((120,y+80),"Date:",CHARCOAL,font=font(36,bold=True))
    d.rectangle([220,y+138,700,y+141],fill=ROSE)
    d.text((1200,y),"Photographer Signature:",CHARCOAL,font=font(36,bold=True))
    d.rectangle([1200,y+58,2300,y+61],fill=ROSE)
    a4_footer(d,W2,H2)
    return save_upload(img,f"{PFX}_Booking_Form.png",f"templates/{NICHE}/forms/{PFX}_Booking_Form.png")

def build_shot_list():
    W2,H2=A4; img=Image.new("RGB",(W2,H2),WHITE); d=ImageDraw.Draw(img)
    y=a4_header(img,d,"SESSION SHOT LIST")
    y+=10
    d.text((120,y),"Client:",CHARCOAL,font=font(38,bold=True)); d.rectangle([235,y+55,1100,y+58],fill=ROSE)
    d.text((1200,y),"Date:",CHARCOAL,font=font(38,bold=True)); d.rectangle([1320,y+55,2300,y+58],fill=ROSE)
    y+=120
    y=section_head(d,80,y,"MUST-HAVE SHOTS",width=W2-160); y+=10
    hdr=["#","Shot description","Setup notes","✓"]
    wids=[80,820,1040,100]
    y=table_row(d,80,y,hdr,wids,header=True)
    for i in range(10):
        y=table_row(d,80,y,[str(i+1),"","",""],wids,alt=bool(i%2),row_h=90)
    y+=10
    y=section_head(d,80,y,"NICE-TO-HAVE SHOTS",width=W2-160); y+=10
    y=table_row(d,80,y,hdr,wids,header=True)
    for i in range(6):
        y=table_row(d,80,y,[str(i+1),"","",""],wids,alt=bool(i%2),row_h=90)
    y+=10
    y=section_head(d,80,y,"PROPS & NOTES",width=W2-160); y+=14
    y=field_line(d,120,y,"Props to bring:",width=2240)
    y=field_line(d,120,y,"Backdrop colour / theme:",width=2240)
    y=field_line(d,120,y,"Lighting preference (natural/studio/golden hour):",width=2240)
    y=field_line(d,120,y,"Post-processing style (vibrant/natural/moody/B&W):",width=2240)
    a4_footer(d,W2,H2)
    return save_upload(img,f"{PFX}_Shot_List.png",f"templates/{NICHE}/forms/{PFX}_Shot_List.png")

def build_pet_intake():
    W2,H2=A4; img=Image.new("RGB",(W2,H2),WHITE); d=ImageDraw.Draw(img)
    y=a4_header(img,d,"PET INTAKE FORM")
    y=section_head(d,80,y+10,"PET PROFILE",width=W2-160); y+=14
    y=field_pair(d,120,y,"Pet Name:","Nickname:",total_w=2240)
    y=field_triple(d,120,y,["Species:","Breed:","Age:"],total_w=2240)
    y=field_triple(d,120,y,["Gender:","Colour:","Neutered?"],total_w=2240)
    y+=8
    y=section_head(d,80,y,"TEMPERAMENT",width=W2-160); y+=14
    y=field_line(d,120,y,"General temperament (friendly/nervous/excitable):",width=2240)
    y=field_line(d,120,y,"How does pet react to strangers?",width=2240)
    y=field_line(d,120,y,"Known fears or triggers (cameras/lights/sounds)?",width=2240)
    y=field_pair(d,120,y,"Good with other animals? Y/N","Good with children? Y/N",total_w=2240)
    y+=8
    y=section_head(d,80,y,"HANDLING NOTES",width=W2-160); y+=14
    y=field_line(d,120,y,"How does pet like to be approached?",width=2240)
    y=field_line(d,120,y,"Favourite treats / rewards to use on shoot:",width=2240)
    y=field_line(d,120,y,"Commands pet responds to:",width=2240)
    y=field_line(d,120,y,"Anything that upsets or stresses your pet?",width=2240)
    y+=8
    y=section_head(d,80,y,"HEALTH NOTES",width=W2-160); y+=14
    y=field_line(d,120,y,"Health conditions relevant to session:",width=2240)
    y=field_pair(d,120,y,"Vet Name:","Vet Phone:",total_w=2240)
    a4_footer(d,W2,H2)
    return save_upload(img,f"{PFX}_Pet_Intake.png",f"templates/{NICHE}/forms/{PFX}_Pet_Intake.png")

def build_photo_release():
    W2,H2=A4; img=Image.new("RGB",(W2,H2),WHITE); d=ImageDraw.Draw(img)
    y=a4_header(img,d,"PHOTO & VIDEO RELEASE FORM")
    y=section_head(d,80,y+10,"CLIENT DETAILS",width=W2-160); y+=14
    y=field_pair(d,120,y,"Client Name:","Pet Name:",total_w=2240)
    y=field_pair(d,120,y,"Date of session:","Package:",total_w=2240)
    y+=10
    y=section_head(d,80,y,"USAGE RIGHTS GRANTED",width=W2-160); y+=14
    d.text((120,y),"I grant permission to use photographs/videos of my pet for:",CHARCOAL,font=font(36,bold=True)); y+=60
    for perm in ["Portfolio website / online gallery","Social media (Instagram, Facebook, TikTok, Pinterest)",
                 "Marketing materials (flyers, brochures, adverts)","Press / editorial use",
                 "Educational content / workshops"]:
        d.rectangle([120,y+4,164,y+48],outline=ROSE,width=3)
        d.text((180,y),perm,fill=CHARCOAL,font=font(36)); y+=60
    y+=10
    d.text((120,y),"I do NOT give permission for any of the above.",CHARCOAL,font=font(36))
    d.rectangle([120,y+4,164,y+48],outline=ROSE,width=3); y+=80
    y=section_head(d,80,y,"PHOTOGRAPHER OBLIGATIONS",width=W2-160); y+=14
    for ob in ["Images will not be sold to third parties without explicit written consent.",
               "Client's full name will not be published without additional permission.",
               "This consent may be withdrawn at any time by written request to the photographer."]:
        paw_print(d,110,y+18,size=14,fill=ROSE)
        d.text((145,y),ob,fill=CHARCOAL,font=font(32)); y+=52
    y+=10
    y=section_head(d,80,y,"DIGITAL FILES & PRINT RIGHTS",width=W2-160); y+=14
    for dr in ["Client receives full personal use rights to all delivered images.",
               "Client may print images for personal and commercial use of their own business.",
               "Client may not resell the images or license them to third parties.",
               "Photographer retains the copyright to all images."]:
        paw_print(d,110,y+18,size=14,fill=ROSE)
        d.text((145,y),dr,fill=CHARCOAL,font=font(32)); y+=52
    y+=20
    d.text((120,y),"Client Signature:",CHARCOAL,font=font(36,bold=True))
    d.rectangle([120,y+58,1100,y+61],fill=ROSE)
    d.text((120,y+80),"Date:",CHARCOAL,font=font(36,bold=True))
    d.rectangle([220,y+138,700,y+141],fill=ROSE)
    d.text((1200,y),"Photographer Signature:",CHARCOAL,font=font(36,bold=True))
    d.rectangle([1200,y+58,2300,y+61],fill=ROSE)
    a4_footer(d,W2,H2)
    return save_upload(img,f"{PFX}_Photo_Release.png",f"templates/{NICHE}/forms/{PFX}_Photo_Release.png")

def build_model_release():
    W2,H2=A4; img=Image.new("RGB",(W2,H2),WHITE); d=ImageDraw.Draw(img)
    y=a4_header(img,d,"MODEL RELEASE FORM")
    y=section_head(d,80,y+10,"SUBJECT DETAILS",width=W2-160); y+=14
    d.text((120,y),"This release covers: (tick all that apply)",CHARCOAL,font=font(36,bold=True)); y+=60
    for opt in ["Pet only","Owner in frame","Children in frame","Third parties in frame"]:
        d.rectangle([120,y+4,164,y+48],outline=ROSE,width=3)
        d.text((180,y),opt,fill=CHARCOAL,font=font(36)); y+=60
    y+=10
    y=field_pair(d,120,y,"Subject/Pet Name:","Owner Name:",total_w=2240)
    y=field_pair(d,120,y,"Date of session:","Location:",total_w=2240)
    y+=10
    y=section_head(d,80,y,"GRANT OF RIGHTS",width=W2-160); y+=14
    for right_ in [
        "I grant to YOUR BUSINESS NAME and its assigns permission to use any photographs,",
        "videos or digital images featuring the above subject(s), taken at the above session.",
        "","This grant is worldwide, royalty-free, and perpetual.",
        "","Permitted uses include but are not limited to: portfolio, social media, advertising,",
        "press, educational content, and marketing materials.",
    ]:
        if right_:
            paw_print(d,110,y+18,size=14,fill=ROSE)
            d.text((145,y),right_,fill=CHARCOAL,font=font(32)); y+=50
        else: y+=20
    y+=10
    y=section_head(d,80,y,"RESTRICTIONS (IF ANY)",width=W2-160); y+=14
    for _ in range(3):
        d.rectangle([120,y+40,2360,y+43],fill=ROSE); y+=70
    y+=20
    y=section_head(d,80,y,"SIGNATURE",width=W2-160); y+=14
    d.text((120,y),"Print name:",CHARCOAL,font=font(36,bold=True)); d.rectangle([340,y+55,1200,y+58],fill=ROSE)
    d.text((1300,y),"Date:",CHARCOAL,font=font(36,bold=True)); d.rectangle([1430,y+55,2300,y+58],fill=ROSE)
    y+=100
    d.text((120,y),"Signature:",CHARCOAL,font=font(36,bold=True)); d.rectangle([300,y+55,1200,y+58],fill=ROSE)
    d.text((1300,y),"Parent/guardian if under 18:",CHARCOAL,font=font(30,bold=True))
    d.rectangle([1300,y+55,2300,y+58],fill=ROSE)
    a4_footer(d,W2,H2)
    return save_upload(img,f"{PFX}_Model_Release.png",f"templates/{NICHE}/forms/{PFX}_Model_Release.png")

def build_invoice():
    W2,H2=A4; img=Image.new("RGB",(W2,H2),WHITE); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W2,260],fill=ROSE); gold_rule(d,260,thickness=10,canvas_w=W2)
    camera_icon(d,160,130,size=70,fill=GOLD)
    d.text((280,60),"YOUR BUSINESS NAME",fill=GOLD,font=font(64,bold=True))
    d.text((280,140),"Professional Pet Photography",fill=CREAM,font=font(40))
    d.text((280,195),"07700 000000  |  yourname@email.com",fill=WHITE,font=font(32))
    centred(d,300,"INVOICE",CHARCOAL,font(80,bold=True),canvas_w=W2)
    d.text((120,420),"Invoice #:",CHARCOAL,font=font(38,bold=True)); d.rectangle([310,460,900,463],fill=ROSE)
    d.text((120,485),"Date:",CHARCOAL,font=font(38,bold=True)); d.rectangle([225,525,900,528],fill=ROSE)
    d.text((120,550),"Due:",CHARCOAL,font=font(38,bold=True)); d.rectangle([210,590,900,593],fill=ROSE)
    d.text((1200,420),"Bill To:",CHARCOAL,font=font(38,bold=True))
    for yy in [460,525,590]: d.rectangle([1200,yy,2300,yy+3],fill=ROSE)
    y=660
    hdr=["Date","Session / Product","Qty","Rate","Total"]
    wids=[300,720,180,350,370]
    y=table_row(d,80,y,hdr,wids,header=True)
    for i in range(8): y=table_row(d,80,y,[""]*5,wids,alt=bool(i%2),row_h=85)
    d.rectangle([1680,y+10,2300,y+80],fill=CREAM_ALT)
    d.text((1700,y+20),"Subtotal:",CHARCOAL,font=font(36,bold=True))
    right(d,2280,y+20,"£",CHARCOAL,font(36,bold=True)); y+=80
    d.rectangle([1680,y+10,2300,y+80],fill=ROSE)
    d.text((1700,y+20),"TOTAL DUE:",WHITE,font=font(40,bold=True))
    right(d,2280,y+20,"£",GOLD,font(40,bold=True)); y+=100
    d.text((120,y),"Payment: Bank Transfer / Card / PayPal",CHARCOAL,font=font(34))
    d.text((120,y+50),"Sort code: XX-XX-XX  |  Account: XXXXXXXX",CHARCOAL,font=font(34))
    d.text((120,y+100),"Thank you for booking with us!",ROSE,font=font(36,bold=True))
    a4_footer(d,W2,H2)
    return save_upload(img,f"{PFX}_Invoice.png",f"templates/{NICHE}/forms/{PFX}_Invoice.png")

def build_booking_confirmation():
    W2,H2=A4; img=Image.new("RGB",(W2,H2),WHITE); d=ImageDraw.Draw(img)
    y=a4_header(img,d,"BOOKING CONFIRMATION")
    y=section_head(d,80,y+10,"CLIENT & SESSION DETAILS",width=W2-160); y+=14
    y=field_pair(d,120,y,"Client Name:","Phone:",total_w=2240)
    y=field_pair(d,120,y,"Pet Name(s):","Email:",total_w=2240)
    y=field_pair(d,120,y,"Session type:","Date:",total_w=2240)
    y=field_pair(d,120,y,"Time:","Location:",total_w=2240)
    y=field_line(d,120,y,"Special requests / notes:",width=2240)
    y+=10
    y=section_head(d,80,y,"PAYMENT SUMMARY",width=W2-160); y+=14
    hdr=["Item","Price","Paid","Balance"]
    wids=[1000,400,400,320]
    y=table_row(d,80,y,hdr,wids,header=True)
    for i in range(4): y=table_row(d,80,y,[""]*4,wids,alt=bool(i%2),row_h=80)
    d.rectangle([1300,y+10,2220,y+70],fill=ROSE)
    d.text((1320,y+18),"BALANCE DUE:",WHITE,font=font(42,bold=True))
    right(d,2200,y+18,"£",GOLD,font(42,bold=True)); y+=100
    centred(d,y,"Gallery delivered within [X] days of session.",CHARCOAL,font(34),canvas_w=W2)
    centred(d,y+50,"48-hour cancellation notice required.",CHARCOAL,font(34),canvas_w=W2)
    centred(d,y+120,"We're so excited to photograph your pet!",ROSE,font(38,bold=True),canvas_w=W2)
    a4_footer(d,W2,H2)
    return save_upload(img,f"{PFX}_Booking_Confirmation.png",f"templates/{NICHE}/forms/{PFX}_Booking_Confirmation.png")


# ══════════════════════════════════════════════════════════════════════════════
# OPERATIONS (4)
# ══════════════════════════════════════════════════════════════════════════════

def build_session_schedule():
    W2,H2=A4; img=Image.new("RGB",(W2,H2),WHITE); d=ImageDraw.Draw(img)
    y=a4_header(img,d,"SESSION SCHEDULE")
    y+=10
    d.text((120,y),"Date:",CHARCOAL,font=font(38,bold=True)); d.rectangle([235,y+55,800,y+58],fill=ROSE)
    d.text((900,y),"Location:",CHARCOAL,font=font(38,bold=True)); d.rectangle([1100,y+55,2300,y+58],fill=ROSE)
    y+=120
    hdr=["Time","Client","Pet","Package","Duration","Status","Notes"]
    wids=[200,360,280,340,200,200,220]
    y=table_row(d,80,y,hdr,wids,header=True)
    times=["08:00","09:00","10:00","11:00","12:00","13:00","14:00",
           "15:00","16:00","17:00","18:00","19:00"]
    for i,t in enumerate(times):
        y=table_row(d,80,y,[t,"","","","","",""],wids,alt=bool(i%2),row_h=80)
    y+=10
    d.text((120,y),"Total sessions:",CHARCOAL,font=font(36,bold=True)); d.rectangle([400,y+52,800,y+55],fill=ROSE)
    d.text((900,y),"Total income:",CHARCOAL,font=font(36,bold=True)); d.rectangle([1140,y+52,1800,y+55],fill=ROSE)
    a4_footer(d,W2,H2)
    return save_upload(img,f"{PFX}_Session_Schedule.png",f"templates/{NICHE}/operations/{PFX}_Session_Schedule.png")

def build_editing_tracker():
    W2,H2=A4; img=Image.new("RGB",(W2,H2),WHITE); d=ImageDraw.Draw(img)
    y=a4_header(img,d,"EDITING TRACKER")
    y+=10
    d.text((120,y),"Month:",CHARCOAL,font=font(38,bold=True)); d.rectangle([270,y+55,900,y+58],fill=ROSE)
    y+=120
    hdr=["Client","Session date","# Raw","Culled","Edited","Gallery sent","Printed","Archived"]
    wids=[350,280,120,120,120,240,120,110]
    y=table_row(d,80,y,hdr,wids,header=True)
    for i in range(18):
        y=table_row(d,80,y,[""]*8,wids,alt=bool(i%2),row_h=80)
    y+=10
    d.text((120,y),"Editing software:",CHARCOAL,font=font(36,bold=True)); d.rectangle([460,y+52,1200,y+55],fill=ROSE)
    d.text((1300,y),"Export preset:",CHARCOAL,font=font(36,bold=True)); d.rectangle([1620,y+52,2300,y+55],fill=ROSE)
    y+=80
    d.text((120,y),"Notes:",CHARCOAL,font=font(36,bold=True)); d.rectangle([120,y+55,2300,y+58],fill=ROSE)
    a4_footer(d,W2,H2)
    return save_upload(img,f"{PFX}_Editing_Tracker.png",f"templates/{NICHE}/operations/{PFX}_Editing_Tracker.png")

def build_expenses_tracker():
    W2,H2=A4; img=Image.new("RGB",(W2,H2),WHITE); d=ImageDraw.Draw(img)
    y=a4_header(img,d,"BUSINESS EXPENSES TRACKER")
    y+=10
    d.text((120,y),"Month/Year:",CHARCOAL,font=font(38,bold=True)); d.rectangle([380,y+55,1100,y+58],fill=ROSE)
    y+=120
    hdr=["Date","Description","Category","Supplier","Amount","Receipt"]
    wids=[220,560,380,380,220,180]
    y=table_row(d,80,y,hdr,wids,header=True)
    cats=["Camera gear","Editing software","Props/backdrops","Marketing","Insurance",
          "Travel/fuel","Printing","Website","Training/CPD","Other","","","","","","","","","",""]
    for i in range(20):
        cat=cats[i] if i<len(cats) else ""
        y=table_row(d,80,y,["","",cat,"","",""],wids,alt=bool(i%2),row_h=70)
    d.rectangle([80,y+10,2300,y+80],fill=CREAM_ALT,outline=GOLD,width=1)
    d.text((100,y+22),"TOTAL:",ROSE,font=font(44,bold=True))
    right(d,2280,y+22,"£",CHARCOAL,font(44,bold=True)); y+=100
    d.text((120,y),"Notes:",CHARCOAL,font=font(36,bold=True)); d.rectangle([120,y+55,2300,y+58],fill=ROSE)
    a4_footer(d,W2,H2)
    return save_upload(img,f"{PFX}_Expenses_Tracker.png",f"templates/{NICHE}/operations/{PFX}_Expenses_Tracker.png")

def build_income_tracker():
    W2,H2=A4; img=Image.new("RGB",(W2,H2),WHITE); d=ImageDraw.Draw(img)
    y=a4_header(img,d,"INCOME TRACKER")
    y+=10
    d.text((120,y),"Month/Year:",CHARCOAL,font=font(38,bold=True)); d.rectangle([380,y+55,1100,y+58],fill=ROSE)
    y+=120
    hdr=["Date","Client","Session type","Images sold","Session fee","Print sales","Total","Paid?"]
    wids=[200,380,320,200,240,240,200,100]
    y=table_row(d,80,y,hdr,wids,header=True)
    for i in range(20): y=table_row(d,80,y,[""]*8,wids,alt=bool(i%2),row_h=72)
    d.rectangle([80,y+10,2300,y+80],fill=ROSE)
    d.text((100,y+20),"TOTAL INCOME:",WHITE,font=font(44,bold=True))
    right(d,2280,y+20,"£",GOLD,font(44,bold=True)); y+=100
    d.rectangle([80,y+10,1100,y+80],fill=CREAM_ALT,outline=GOLD,width=1)
    d.text((100,y+22),"Total Expenses:",CHARCOAL,font=font(34))
    right(d,1080,y+22,"£",CHARCOAL,font(34))
    d.rectangle([1160,y+10,2300,y+80],fill=CREAM_ALT,outline=ROSE,width=2)
    d.text((1180,y+22),"NET PROFIT:",ROSE,font=font(40,bold=True))
    right(d,2280,y+22,"£",CHARCOAL,font(40,bold=True)); y+=100
    d.text((120,y),"Notes:",CHARCOAL,font=font(36,bold=True)); d.rectangle([120,y+55,2300,y+58],fill=ROSE)
    a4_footer(d,W2,H2)
    return save_upload(img,f"{PFX}_Income_Tracker.png",f"templates/{NICHE}/operations/{PFX}_Income_Tracker.png")


# ══════════════════════════════════════════════════════════════════════════════
# DELIVERY PDF
# ══════════════════════════════════════════════════════════════════════════════

SECTIONS = [
    ("BRANDING (8 templates)", [
        ("Business Card — Dark",      f"{CDN}/templates/{NICHE}/branding/{PFX}_Business_Card_Dark.png"),
        ("Business Card — Light",     f"{CDN}/templates/{NICHE}/branding/{PFX}_Business_Card_Light.png"),
        ("Appointment Card — Dark",   f"{CDN}/templates/{NICHE}/branding/{PFX}_Appointment_Card_Dark.png"),
        ("Appointment Card — Light",  f"{CDN}/templates/{NICHE}/branding/{PFX}_Appointment_Card_Light.png"),
        ("Gift Certificate",          f"{CDN}/templates/{NICHE}/branding/{PFX}_Gift_Certificate.png"),
        ("Welcome Sign (A4)",         f"{CDN}/templates/{NICHE}/branding/{PFX}_Welcome_Sign.png"),
        ("Thank You Card",            f"{CDN}/templates/{NICHE}/branding/{PFX}_Thank_You_Card.png"),
        ("Referral Card (free print)",f"{CDN}/templates/{NICHE}/branding/{PFX}_Referral_Card.png"),
    ]),
    ("MARKETING (7 templates)", [
        ("Flyer — Mini Session",      f"{CDN}/templates/{NICHE}/marketing/{PFX}_Flyer_Mini_Session.png"),
        ("Flyer — Seasonal Special",  f"{CDN}/templates/{NICHE}/marketing/{PFX}_Flyer_Seasonal.png"),
        ("Pricing Guide (A4)",        f"{CDN}/templates/{NICHE}/marketing/{PFX}_Pricing_Guide.png"),
        ("Social — Now Booking",      f"{CDN}/templates/{NICHE}/marketing/{PFX}_Social_Booking.png"),
        ("Social — Portfolio Showcase",f"{CDN}/templates/{NICHE}/marketing/{PFX}_Social_Portfolio.png"),
        ("Social — Behind the Lens",  f"{CDN}/templates/{NICHE}/marketing/{PFX}_Social_BTS.png"),
        ("Social — Client Testimonial",f"{CDN}/templates/{NICHE}/marketing/{PFX}_Social_Testimonial.png"),
        ("Social — Seasonal Promo",   f"{CDN}/templates/{NICHE}/marketing/{PFX}_Social_Seasonal_Promo.png"),
    ]),
    ("CLIENT FORMS (7 templates)", [
        ("Photography Booking Form",  f"{CDN}/templates/{NICHE}/forms/{PFX}_Booking_Form.png"),
        ("Session Shot List",         f"{CDN}/templates/{NICHE}/forms/{PFX}_Shot_List.png"),
        ("Pet Intake Form",           f"{CDN}/templates/{NICHE}/forms/{PFX}_Pet_Intake.png"),
        ("Photo & Video Release",     f"{CDN}/templates/{NICHE}/forms/{PFX}_Photo_Release.png"),
        ("Model Release Form",        f"{CDN}/templates/{NICHE}/forms/{PFX}_Model_Release.png"),
        ("Invoice",                   f"{CDN}/templates/{NICHE}/forms/{PFX}_Invoice.png"),
        ("Booking Confirmation",      f"{CDN}/templates/{NICHE}/forms/{PFX}_Booking_Confirmation.png"),
    ]),
    ("OPERATIONS (4 templates)", [
        ("Session Schedule",          f"{CDN}/templates/{NICHE}/operations/{PFX}_Session_Schedule.png"),
        ("Editing Tracker",           f"{CDN}/templates/{NICHE}/operations/{PFX}_Editing_Tracker.png"),
        ("Expenses Tracker",          f"{CDN}/templates/{NICHE}/operations/{PFX}_Expenses_Tracker.png"),
        ("Income Tracker",            f"{CDN}/templates/{NICHE}/operations/{PFX}_Income_Tracker.png"),
    ]),
]


def build_delivery_pdf():
    pdf_path = LISTING / "PP_Mega_Bundle_DELIVERY.pdf"
    c = rl_canvas.Canvas(str(pdf_path), pagesize=RL_A4)
    W2, H2 = RL_A4
    ROSE_RL  = colors.HexColor("#C4878E")
    GOLD_RL  = colors.HexColor("#C9A96E")
    CREAM_RL = colors.HexColor("#F5F0E8")
    CHAR_RL  = colors.HexColor("#1A1A1A")
    WHITE_RL = colors.HexColor("#FFFFFF")
    c.setFillColor(ROSE_RL); c.rect(0,0,W2,H2,fill=1,stroke=0)
    c.setFillColor(GOLD_RL); c.setFont("Helvetica-Bold",44)
    c.drawCentredString(W2/2,H2-100,"PET PHOTOGRAPHY")
    c.drawCentredString(W2/2,H2-155,"MEGA BUSINESS BUNDLE")
    c.setFillColor(WHITE_RL); c.setFont("Helvetica",26)
    c.drawCentredString(W2/2,H2-210,"26 Canva Templates — Fully Editable")
    c.setFillColor(GOLD_RL); c.rect(50,H2-250,W2-100,3,fill=1,stroke=0)
    c.setFillColor(WHITE_RL); c.setFont("Helvetica",20)
    y=H2-300
    for line in ["Thank you for your purchase!","",
                 "This bundle contains 26 fully editable PNG templates.",
                 "Download each template from the links below.","",
                 "Included categories:","  • Branding (8 templates)","  • Marketing (7 templates)",
                 "  • Client Forms (7 templates)","  • Operations (4 templates)","",
                 "Questions? Message us on Etsy — we reply within 24 hours."]:
        c.drawString(60,y,line); y-=28
    c.setFillColor(GOLD_RL); c.rect(50,60,W2-100,3,fill=1,stroke=0)
    c.setFillColor(WHITE_RL); c.setFont("Helvetica",16)
    c.drawCentredString(W2/2,35,"PurpleOcaz — purpleocaz.etsy.com")
    c.showPage()
    for section_title,items in SECTIONS:
        c.setFillColor(CREAM_RL); c.rect(0,0,W2,H2,fill=1,stroke=0)
        c.setFillColor(ROSE_RL); c.rect(0,H2-80,W2,80,fill=1,stroke=0)
        c.setFillColor(GOLD_RL); c.setFont("Helvetica-Bold",28)
        c.drawCentredString(W2/2,H2-52,section_title)
        y2=H2-120
        for name,url in items:
            c.setFont("Helvetica-Bold",18); c.setFillColor(CHAR_RL)
            c.drawString(60,y2,f"• {name}")
            c.setFont("Helvetica",14); c.setFillColor(ROSE_RL)
            c.drawString(80,y2-22,url)
            c.linkURL(url,(80,y2-30,min(80+len(url)*7,W2-60),y2-10))
            y2-=65
            if y2<80:
                c.setFillColor(ROSE_RL); c.rect(0,0,W2,40,fill=1,stroke=0)
                c.setFillColor(WHITE_RL); c.setFont("Helvetica",12)
                c.drawCentredString(W2/2,14,"PurpleOcaz — purpleocaz.etsy.com")
                c.showPage()
                c.setFillColor(CREAM_RL); c.rect(0,0,W2,H2,fill=1,stroke=0)
                y2=H2-60
        c.setFillColor(ROSE_RL); c.rect(0,0,W2,40,fill=1,stroke=0)
        c.setFillColor(WHITE_RL); c.setFont("Helvetica",12)
        c.drawCentredString(W2/2,14,"PurpleOcaz — purpleocaz.etsy.com")
        c.showPage()
    c.save()
    print(f"  Delivery PDF: {pdf_path}")
    upload_to_spaces(pdf_path,f"templates/{NICHE}/PP_Mega_Bundle_DELIVERY.pdf",content_type="application/pdf")
    return pdf_path


# ══════════════════════════════════════════════════════════════════════════════
# 7 LISTING IMAGES
# ══════════════════════════════════════════════════════════════════════════════

def build_listing_images():
    imgs=[]

    # 1 Hero
    img=Image.new("RGB",(W,H),ROSE); d=ImageDraw.Draw(img)
    d.rectangle([0,H//2+80,W,H],fill=CHARCOAL); gold_rule(d,H//2+80,thickness=16,canvas_w=W)
    camera_icon(d,200,280,size=120,fill=GOLD); camera_icon(d,W-200,280,size=120,fill=GOLD)
    centred(d,160,"PET PHOTOGRAPHY",GOLD,font(160,bold=True),canvas_w=W)
    centred(d,350,"BUSINESS BUNDLE",WHITE,font(130,bold=True),canvas_w=W)
    gold_rule(d,530,x0=200,x1=W-200,thickness=8)
    centred(d,560,"26 Professional Templates — Fully Editable in Canva",WHITE,font(60),canvas_w=W)
    gold_rule(d,670,x0=200,x1=W-200,thickness=8)
    badges=["Branding Kit","Marketing","Client Forms","Operations","Social Media"]
    bw=500; total=bw*len(badges)+40*(len(badges)-1); bx=(W-total)//2
    for badge in badges:
        d.rectangle([bx,730,bx+bw,830],fill=GOLD)
        bb=d.textbbox((0,0),badge,font=font(48,bold=True)); tw=bb[2]-bb[0]
        d.text((bx+(bw-tw)//2,758),badge,fill=CHARCOAL,font=font(48,bold=True))
        bx+=bw+40
    centred(d,890,"Dusty rose palette  |  Print-ready 300 DPI  |  Canva Free",CREAM,font(52),canvas_w=W)
    centred(d,H//2+140,"Everything you need to run a",WHITE,font(70),canvas_w=W)
    centred(d,H//2+240,"professional pet photography",WHITE,font(70),canvas_w=W)
    centred(d,H//2+340,"business from day one.",GOLD,font(90,bold=True),canvas_w=W)
    centred(d,H//2+480,"£39.99  •  Instant Download  •  Canva Free Account Works",CREAM,font(50),canvas_w=W)
    p=LISTING/"PP_listing_01_hero.png"; img.save(p,"PNG"); print(f"  Saved {p.name}"); imgs.append(p)

    # 2 What's inside
    img=Image.new("RGB",(W,H),CREAM); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W,220],fill=ROSE); gold_rule(d,220,thickness=10,canvas_w=W)
    centred(d,58,"WHAT'S INSIDE YOUR BUNDLE",GOLD,font(100,bold=True),canvas_w=W)
    centred(d,160,"26 fully editable professional templates",CREAM,font(50),canvas_w=W)
    cats=[
        ("BRANDING","8 templates",ROSE,[
            "Business Card Dark & Light","Appointment Card Dark & Light",
            "Gift Certificate","Welcome Sign (A4)","Thank You Card","Referral Card"]),
        ("MARKETING","7 templates",ROSE,[
            "Mini Session Flyer","Seasonal Special Flyer","Pricing Guide",
            "Social — Now Booking","Social — Portfolio Showcase",
            "Social — Behind the Lens","Social — Testimonial"]),
        ("CLIENT FORMS","7 templates",CHARCOAL,[
            "Photography Booking Form","Session Shot List",
            "Pet Intake Form","Photo & Video Release",
            "Model Release Form","Invoice","Booking Confirmation"]),
        ("OPERATIONS","4 templates",CHARCOAL,[
            "Session Schedule","Editing Tracker",
            "Expenses Tracker","Income Tracker"]),
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
            d.text((cx+60,iy),item,fill=WHITE if bg!=CREAM else CHARCOAL,font=font(36)); iy+=56
    p=LISTING/"PP_listing_02_whats_inside.png"; img.save(p,"PNG"); print(f"  Saved {p.name}"); imgs.append(p)

    # 3 Lifestyle
    img=Image.new("RGB",(W,H),CHARCOAL); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W,240],fill=ROSE); gold_rule(d,240,thickness=10,canvas_w=W)
    centred(d,68,"MADE FOR PET PHOTOGRAPHERS",GOLD,font(100,bold=True),canvas_w=W)
    centred(d,185,"by someone who gets it",WHITE,font(58),canvas_w=W)
    feats=[("LOOK PROFESSIONAL","from your very first session","Branded cards, booking slips & welcome signs"),
           ("PROTECT YOUR WORK","with proper release forms","Photo release, model release & booking agreements"),
           ("STAY ORGANISED","session to session","Shot lists, editing tracker & session schedules"),
           ("GROW YOUR BUSINESS","with smart marketing","Social posts, flyers & seasonal promo templates")]
    y=300
    for title,sub,detail in feats:
        d.rectangle([80,y,W-80,y+190],fill=ROSE,outline=GOLD,width=3)
        camera_icon(d,160,y+95,size=50,fill=GOLD)
        d.text((270,y+28),title,fill=GOLD,font=font(68,bold=True))
        d.text((270,y+108),sub,fill=CREAM,font=font(46))
        d.text((270,y+155),detail,fill=WHITE,font=font(36))
        y+=210
    gold_rule(d,y+20,x0=80,x1=W-80,thickness=6)
    centred(d,y+50,"Fully editable in Canva — free account works perfectly",CREAM,font(54),canvas_w=W)
    d.rectangle([80,y+160,W-80,y+300],fill=GOLD)
    centred(d,y+195,"26 TEMPLATES  •  £39.99  •  INSTANT DOWNLOAD",CHARCOAL,font(62,bold=True),canvas_w=W)
    p=LISTING/"PP_listing_03_lifestyle.png"; img.save(p,"PNG"); print(f"  Saved {p.name}"); imgs.append(p)

    # 4 How it works
    img=Image.new("RGB",(W,H),CREAM); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W,220],fill=ROSE); gold_rule(d,220,thickness=10,canvas_w=W)
    centred(d,65,"HOW IT WORKS",GOLD,font(110,bold=True),canvas_w=W)
    centred(d,160,"Three simple steps to a professional photography business",WHITE,font(50),canvas_w=W)
    steps=[("1","PURCHASE & DOWNLOAD","Buy on Etsy and open the delivery PDF.","Every template link is inside, ready to click."),
           ("2","OPEN IN CANVA","Click any link to open the template in Canva.","A free Canva account is all you need."),
           ("3","CUSTOMISE & SEND","Add your name, logo and brand colours.","Download as PDF or PNG and send to clients.")]
    y=280
    for num,title,l1,l2 in steps:
        d.ellipse([100,y,300,y+200],fill=ROSE)
        centred(d,y+50,num,WHITE,font(120,bold=True),canvas_w=200)
        d.text((350,y+22),title,fill=ROSE,font=font(72,bold=True))
        d.text((350,y+108),l1,fill=CHARCOAL,font=font(46))
        d.text((350,y+164),l2,fill=CHARCOAL,font=font(44))
        gold_rule(d,y+220,x0=80,x1=W-80,thickness=4); y+=280
    y+=20
    d.rectangle([80,y,W-80,y+420],fill=ROSE,outline=GOLD,width=4)
    centred(d,y+30,"WHAT YOU'LL NEED",GOLD,font(70,bold=True),canvas_w=W)
    centred(d,y+120,"✓  A free Canva account (canva.com)",WHITE,font(52),canvas_w=W)
    centred(d,y+190,"✓  A printer or PDF viewer",WHITE,font(52),canvas_w=W)
    centred(d,y+260,"✓  5 minutes to add your business details",WHITE,font(52),canvas_w=W)
    centred(d,y+340,"No design experience needed!",GOLD,font(54,bold=True),canvas_w=W)
    p=LISTING/"PP_listing_04_how_it_works.png"; img.save(p,"PNG"); print(f"  Saved {p.name}"); imgs.append(p)

    # 5 Why buy
    img=Image.new("RGB",(W,H),ROSE); d=ImageDraw.Draw(img)
    d.rectangle([0,H-200,W,H],fill=CHARCOAL); gold_rule(d,H-200,thickness=10,canvas_w=W)
    centred(d,58,"WHY CHOOSE THIS BUNDLE?",GOLD,font(100,bold=True),canvas_w=W)
    gold_rule(d,188,x0=100,x1=W-100,thickness=6)
    reasons=[("26 templates in one purchase","Save hours — everything you need, bought once."),
             ("Built for pet photographers","Shot lists, model releases, editing tracker — the works."),
             ("Photo & model release forms included","Legal protection built in. No hunting for templates."),
             ("Print-ready at 300 DPI","Works perfectly at your local print shop."),
             ("Dusty rose palette — stand out","Warm, beautiful, feminine — memorable for your clients."),
             ("One-off purchase, yours forever","No subscriptions. Buy once, use indefinitely.")]
    y=228
    for title,desc in reasons:
        d.rectangle([80,y,W-80,y+200],fill=WHITE,outline=GOLD,width=2)
        camera_icon(d,160,y+100,size=50,fill=ROSE)
        d.text((270,y+28),title,fill=ROSE,font=font(64,bold=True))
        d.text((270,y+112),desc,fill=CHARCOAL,font=font(42))
        y+=220
    centred(d,H-160,"Instant download. No waiting. No subscriptions.",CREAM,font(54),canvas_w=W)
    centred(d,H-90,"26 templates  •  £39.99  •  Yours forever",GOLD,font(58,bold=True),canvas_w=W)
    p=LISTING/"PP_listing_05_why_buy.png"; img.save(p,"PNG"); print(f"  Saved {p.name}"); imgs.append(p)

    # 6 Canva basics
    img=Image.new("RGB",(W,H),CREAM); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W,240],fill=ROSE); gold_rule(d,240,thickness=10,canvas_w=W)
    centred(d,65,"NEW TO CANVA?",GOLD,font(110,bold=True),canvas_w=W)
    centred(d,165,"It's free and incredibly easy to use",WHITE,font(58),canvas_w=W)
    steps6=[("Go to canva.com","Sign up for a free account — 60 seconds"),
            ("Click the template link","Opens your template directly in Canva"),
            ("Click any text to edit","Type your business name and details"),
            ("Change colours if you like","Click any shape → colour picker → your brand"),
            ("Download when finished","File → Download → PDF Print or PNG"),
            ("Print or share","Home printer, print shop, or email to clients")]
    y=280
    for i,(step,desc) in enumerate(steps6):
        d.rectangle([80,y,W-80,y+170],fill=WHITE if i%2==0 else CREAM_ALT,outline=GOLD,width=2)
        d.rectangle([80,y,220,y+170],fill=ROSE)
        centred(d,y+55,str(i+1),WHITE,font(90,bold=True),canvas_w=140)
        d.text((240,y+22),step,fill=ROSE,font=font(62,bold=True))
        d.text((240,y+100),desc,fill=CHARCOAL,font=font(44))
        y+=190
    d.rectangle([80,y+20,W-80,y+200],fill=ROSE,outline=GOLD,width=4)
    centred(d,y+55,"Canva is free and works on any device —",CREAM,font(52),canvas_w=W)
    centred(d,y+120,"phone, tablet, or laptop!",GOLD,font(62,bold=True),canvas_w=W)
    p=LISTING/"PP_listing_06_canva_basics.png"; img.save(p,"PNG"); print(f"  Saved {p.name}"); imgs.append(p)

    # 7 Please note
    img=Image.new("RGB",(W,H),CHARCOAL); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W,240],fill=ROSE); gold_rule(d,240,thickness=10,canvas_w=W)
    centred(d,65,"PLEASE NOTE",GOLD,font(110,bold=True),canvas_w=W)
    centred(d,165,"Important information about your purchase",WHITE,font(52),canvas_w=W)
    notes=[("Digital Download Only","No physical items posted — you receive PNG template files."),
           ("Instant Delivery","Delivery PDF arrives via Etsy immediately after purchase."),
           ("Canva Free Account","All templates work with a free Canva account — no paid plan."),
           ("Personal & Business Use","Use for your own pet photography business only."),
           ("No Reselling","Please do not resell or redistribute these templates."),
           ("Copyright","Photographer retains image copyright. Templates are for admin use."),
           ("Questions?","Message us on Etsy — we reply within 24 hours, 7 days a week.")]
    y=280
    for title,desc in notes:
        d.rectangle([80,y,W-80,y+185],fill=WHITE,outline=GOLD,width=2)
        camera_icon(d,160,y+90,size=44,fill=ROSE)
        d.text((270,y+28),title,fill=ROSE,font=font(62,bold=True))
        d.text((270,y+108),desc,fill=CHARCOAL,font=font(42))
        y+=205
    p=LISTING/"PP_listing_07_please_note.png"; img.save(p,"PNG"); print(f"  Saved {p.name}"); imgs.append(p)

    return imgs


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("="*60)
    print("PET PHOTOGRAPHY MEGA BUNDLE — BUILD PIPELINE")
    print("="*60)

    print("\n=== Phase 1: Building 26 Templates ===")
    print("\n  [BRANDING — 8]")
    build_business_card_dark(); build_business_card_light()
    build_appointment_card_dark(); build_appointment_card_light()
    build_gift_certificate(); build_welcome_sign()
    build_thank_you_card(); build_referral_card()

    print("\n  [MARKETING — 7 + social]")
    build_flyer_mini_session(); build_flyer_seasonal(); build_pricing_guide()
    build_social_booking(); build_social_portfolio(); build_social_bts()
    build_social_testimonial(); build_social_seasonal_promo()

    print("\n  [CLIENT FORMS — 7]")
    build_booking_form(); build_shot_list(); build_pet_intake()
    build_photo_release(); build_model_release()
    build_invoice(); build_booking_confirmation()

    print("\n  [OPERATIONS — 4]")
    build_session_schedule(); build_editing_tracker()
    build_expenses_tracker(); build_income_tracker()

    print("\n  ✓ All templates built and uploaded.")

    print("\n=== Phase 2: Delivery PDF ===")
    pdf_path = build_delivery_pdf()

    print("\n=== Phase 3: 7 Listing Images ===")
    listing_imgs = build_listing_images()

    print("\n=== Phase 4: Creating Etsy Draft ===")
    title = "Pet Photography Business Bundle | 26 Canva Templates | Booking Forms Photo Release Invoice"
    description = """Pet Photography Business Bundle — 26 Professional Canva Templates

Everything you need to run a professional pet photography business.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT'S INCLUDED (26 templates)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📸 BRANDING (8 templates)
• Business Card — Dark & Light
• Appointment Card — Dark & Light
• Gift Certificate
• Welcome Sign (A4)
• Thank You Card
• Referral Card (earn a free print)

📣 MARKETING (8 templates)
• Mini Session Flyer (A4)
• Seasonal Special Flyer (A4)
• Pricing Guide (A4)
• Social — Now Booking
• Social — Portfolio Showcase
• Social — Behind the Lens
• Social — Client Testimonial
• Social — Seasonal Promo

📋 CLIENT FORMS (7 templates)
• Photography Booking Form
• Session Shot List Template
• Pet Intake Form
• Photo & Video Release
• Model Release Form
• Invoice
• Booking Confirmation

🗂️ OPERATIONS (4 templates)
• Session Schedule
• Editing Tracker
• Expenses Tracker
• Income Tracker

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HOW IT WORKS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Purchase and open your delivery PDF
2. Click any template link to open in Canva (free account works)
3. Edit with your business details
4. Download and use

✅ Built specifically for pet photographers
✅ Photo & model release forms included — legal protection built in
✅ Dusty rose palette — warm, beautiful, memorable
✅ Print-ready at 300 DPI
✅ Canva free account is all you need
✅ One-off purchase — use forever

DIGITAL DOWNLOAD only — no physical items posted
For your own pet photography business only — no reselling
Questions? Message us on Etsy — reply within 24 hours"""

    tags = [
        "pet photo bundle",
        "pet photo forms",
        "photo release form",
        "model release form",
        "pet photographer kit",
        "photography canva",
        "photo booking form",
        "pet photo business",
        "photographer invoice",
        "shot list template",
        "pet photo branding",
        "editing tracker",
        "pet photo marketing",
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
    print(f"BUNDLE 3 COMPLETE — Draft #{listing_id}")
    print(f"URL: https://www.etsy.com/listing/{listing_id}")
    print(f"{'='*60}")
    return listing_id

if __name__ == "__main__":
    listing_id = main()
