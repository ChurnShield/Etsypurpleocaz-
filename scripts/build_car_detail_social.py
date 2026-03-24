"""
Car Detailing Social Media Pack — 20 Instagram Post Templates (1080x1080)
Built as reportlab PDFs for Canva-editable import.
"""
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os, math

OUT_DIR = "/root/NEW-AI-PROJECT/outputs/car-detail-social"
os.makedirs(OUT_DIR, exist_ok=True)

# Register fonts
pdfmetrics.registerFont(TTFont("Bold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Regular", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("SerifBold", "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Serif", "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"))

S = 1080  # canvas size in points

# Colors (reportlab 0-1)
BG      = Color(13/255, 13/255, 13/255)
RED     = Color(224/255, 32/255, 32/255)
WHITE   = Color(1, 1, 1)
SILVER  = Color(192/255, 192/255, 192/255)
DARK    = Color(26/255, 26/255, 26/255)
DGRAY   = Color(42/255, 42/255, 42/255)
MGRAY   = Color(80/255, 80/255, 80/255)
LGRAY   = Color(140/255, 140/255, 140/255)
GOLD    = Color(212/255, 175/255, 55/255)

def ry(y):
    """Convert top-down y to reportlab bottom-up y."""
    return S - y

# ── HELPER FUNCTIONS ──

def fill_bg(c, color=BG):
    c.setFillColor(color)
    c.rect(0, 0, S, S, fill=1, stroke=0)

def photo_placeholder(c, x, y_top, w, h, label="YOUR PHOTO HERE"):
    """Draw a photo placeholder (top-down coords)."""
    y = ry(y_top) - h
    c.setFillColor(DGRAY)
    c.rect(x, y, w, h, fill=1, stroke=0)
    c.setStrokeColor(MGRAY)
    c.setDash(6, 4)
    c.setLineWidth(1.5)
    c.rect(x + 4, y + 4, w - 8, h - 8, fill=0, stroke=1)
    c.setDash()
    c.setFillColor(LGRAY)
    c.setFont("Regular", 14)
    tw = c.stringWidth(label, "Regular", 14)
    c.drawString(x + (w - tw) / 2, y + h / 2 - 5, label)

def circular_photo(c, cx, cy_top, r, label="YOUR PHOTO"):
    """Draw a circular photo placeholder (top-down coords)."""
    y = ry(cy_top)
    c.setFillColor(DGRAY)
    c.circle(cx, y, r, fill=1, stroke=0)
    c.setStrokeColor(MGRAY)
    c.setDash(4, 3)
    c.setLineWidth(1)
    c.circle(cx, y, r - 4, fill=0, stroke=1)
    c.setDash()
    c.setFillColor(LGRAY)
    c.setFont("Regular", 12)
    tw = c.stringWidth(label, "Regular", 12)
    c.drawString(cx - tw / 2, y - 5, label)

def red_pill(c, cx, y_top, text, font_size=20, pad_x=24, pad_y=8):
    """Draw a red pill badge centered at cx (top-down y)."""
    y = ry(y_top)
    c.setFont("Bold", font_size)
    tw = c.stringWidth(text, "Bold", font_size)
    rx = cx - tw / 2 - pad_x
    ry_b = y - font_size / 2 - pad_y
    rw = tw + pad_x * 2
    rh = font_size + pad_y * 2
    radius = rh / 2
    c.setFillColor(RED)
    c.roundRect(rx, ry_b, rw, rh, radius, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.drawString(cx - tw / 2, y - font_size / 3, text)

def cta_button(c, cx, y_top, text, font_size=22, pad_x=40, pad_y=12):
    """Draw a CTA button (red rounded rect with white text)."""
    y = ry(y_top)
    c.setFont("Bold", font_size)
    tw = c.stringWidth(text, "Bold", font_size)
    rw = tw + pad_x * 2
    rh = font_size + pad_y * 2
    rx = cx - rw / 2
    ry_b = y - rh / 2
    c.setFillColor(RED)
    c.roundRect(rx, ry_b, rw, rh, 8, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.drawString(cx - tw / 2, y - font_size / 3, text)

def red_bar(c, y_top, h, full_width=True, x=0, w=None):
    """Draw a red horizontal bar (top-down y)."""
    if w is None:
        w = S
    y = ry(y_top) - h
    c.setFillColor(RED)
    c.rect(x, y, w, h, fill=1, stroke=0)

def dark_bar(c, y_top, h, x=0, w=None):
    if w is None:
        w = S
    y = ry(y_top) - h
    c.setFillColor(DARK)
    c.rect(x, y, w, h, fill=1, stroke=0)

def text_center(c, y_top, text, font="Bold", size=48, color=WHITE):
    """Draw centered text (top-down y)."""
    y = ry(y_top)
    c.setFont(font, size)
    c.setFillColor(color)
    tw = c.stringWidth(text, font, size)
    c.drawString((S - tw) / 2, y, text)

def text_left(c, x, y_top, text, font="Bold", size=24, color=WHITE):
    y = ry(y_top)
    c.setFont(font, size)
    c.setFillColor(color)
    c.drawString(x, y, text)

def text_right(c, x, y_top, text, font="Bold", size=24, color=WHITE):
    y = ry(y_top)
    c.setFont(font, size)
    c.setFillColor(color)
    tw = c.stringWidth(text, font, size)
    c.drawString(x - tw, y, text)

def draw_stars(c, cx, y_top, count=5, size=28, color=GOLD):
    """Draw star rating centered."""
    y = ry(y_top)
    star_char = "\u2605"
    c.setFont("Regular", size)
    c.setFillColor(color)
    full = star_char * count
    tw = c.stringWidth(full, "Regular", size)
    c.drawString(cx - tw / 2, y, full)

def checkmark_item(c, x, y_top, text, size=20):
    """Draw a checkmark bullet item."""
    y = ry(y_top)
    c.setFont("Bold", size)
    c.setFillColor(RED)
    c.drawString(x, y, "\u2713")
    c.setFillColor(WHITE)
    c.setFont("Regular", size)
    c.drawString(x + 28, y, text)

def bullet_item(c, x, y_top, text, size=18, bullet_color=RED, text_color=SILVER):
    y = ry(y_top)
    c.setFillColor(bullet_color)
    c.circle(x + 5, y + size / 3, 4, fill=1, stroke=0)
    c.setFillColor(text_color)
    c.setFont("Regular", size)
    c.drawString(x + 18, y, text)

def contact_footer(c, y_top=980, include_phone=True, include_web=True):
    """Draw a standard contact info footer."""
    y = y_top
    c.setFont("Regular", 16)
    c.setFillColor(SILVER)
    if include_phone:
        text_center(c, y, "(555) 123-4567  |  yourwebsite.com", "Regular", 16, SILVER)
    else:
        text_center(c, y, "yourwebsite.com", "Regular", 16, SILVER)

def logo_placeholder(c, cx, y_top, w=200, h=50):
    """Draw YOUR LOGO placeholder."""
    y = ry(y_top) - h
    c.setStrokeColor(MGRAY)
    c.setDash(4, 3)
    c.setLineWidth(1)
    c.rect(cx - w / 2, y, w, h, fill=0, stroke=1)
    c.setDash()
    c.setFillColor(LGRAY)
    c.setFont("Regular", 14)
    tw = c.stringWidth("YOUR LOGO", "Regular", 14)
    c.drawString(cx - tw / 2, y + h / 2 - 5, "YOUR LOGO")

def diagonal_stripe(c, y_top, h, angle=-15):
    """Draw a red diagonal stripe across canvas."""
    c.saveState()
    y_center = ry(y_top) - h / 2
    c.translate(S / 2, y_center)
    c.rotate(angle)
    c.setFillColor(RED)
    c.rect(-S, -h / 2, S * 2, h, fill=1, stroke=0)
    c.restoreState()

def price_box(c, x, y_top, w, h, tier, price, features):
    """Draw a pricing box with red outline."""
    y = ry(y_top) - h
    c.setStrokeColor(RED)
    c.setLineWidth(2)
    c.rect(x, y, w, h, fill=0, stroke=1)
    # Tier header
    c.setFillColor(RED)
    c.rect(x, y + h - 40, w, 40, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Bold", 18)
    tw = c.stringWidth(tier, "Bold", 18)
    c.drawString(x + (w - tw) / 2, y + h - 28, tier)
    # Price
    c.setFillColor(WHITE)
    c.setFont("Bold", 32)
    tw = c.stringWidth(price, "Bold", 32)
    c.drawString(x + (w - tw) / 2, y + h - 80, price)
    # Features
    c.setFont("Regular", 13)
    c.setFillColor(SILVER)
    for i, feat in enumerate(features):
        tw = c.stringWidth(feat, "Regular", 13)
        c.drawString(x + (w - tw) / 2, y + h - 110 - i * 22, feat)

def numbered_item(c, x, y_top, number, text, size=20):
    """Draw a numbered list item with red number."""
    y = ry(y_top)
    c.setFont("Bold", size + 8)
    c.setFillColor(RED)
    c.drawString(x, y - 2, str(number))
    c.setFillColor(WHITE)
    c.setFont("Regular", size)
    c.drawString(x + 30, y, text)


# ══════════════════════════════════════════════════════════════
# POST BUILDERS
# ══════════════════════════════════════════════════════════════

def post_01(c):
    """PREMIUM DETAILING — Split layout with services."""
    fill_bg(c)
    # Left half: circular photo
    c.setFillColor(DARK)
    c.rect(0, 0, S / 2, S, fill=1, stroke=0)
    circular_photo(c, S / 4, S / 2, 200, "YOUR CAR PHOTO")
    # Right half
    text_left(c, S / 2 + 40, 120, "PREMIUM", "Bold", 52, WHITE)
    text_left(c, S / 2 + 40, 175, "DETAILING", "Bold", 52, WHITE)
    red_pill(c, S / 2 + 40 + 120, 240, "OUR SERVICES", 16, 18, 6)
    services = ["Ceramic Coating", "Paint Correction", "Interior Detailing", "Engine Bay Cleaning"]
    for i, svc in enumerate(services):
        bullet_item(c, S / 2 + 50, 310 + i * 40, svc, 18, RED, SILVER)
    # Contact
    text_left(c, S / 2 + 50, 520, "YOUR STUDIO NAME", "Bold", 16, SILVER)
    text_left(c, S / 2 + 50, 545, "(555) 123-4567", "Regular", 14, LGRAY)
    text_left(c, S / 2 + 50, 565, "yourwebsite.com", "Regular", 14, LGRAY)
    cta_button(c, S * 3 / 4, 650, "BOOK NOW", 20, 36, 10)
    # Red accent lines
    red_bar(c, 0, 6)
    red_bar(c, S - 6, 6)

def post_02(c):
    """CERAMIC COATING — Diagonal stripe, price."""
    fill_bg(c)
    red_bar(c, 0, 6)
    text_center(c, 100, "CERAMIC", "Bold", 72, WHITE)
    text_center(c, 175, "COATING", "Bold", 72, WHITE)
    diagonal_stripe(c, 250, 80, -8)
    photo_placeholder(c, 60, 420, S - 120, 380, "YOUR CAR PHOTO")
    # Price
    text_center(c, 860, "$XXX", "Bold", 64, WHITE)
    text_center(c, 910, "STARTING FROM", "Regular", 18, SILVER)
    cta_button(c, S / 2, 980, "BOOK TODAY", 22, 40, 10)
    red_bar(c, S - 6, 6)
    logo_placeholder(c, S / 2, 36, 180, 40)

def post_03(c):
    """INTERIOR DETAILING — Magazine style."""
    fill_bg(c)
    # Giant watermark text
    c.setFillColor(Color(30/255, 30/255, 30/255))
    c.setFont("Bold", 120)
    c.drawString(-20, ry(400), "INTERIOR")
    # Red header bar
    red_bar(c, 0, 70)
    text_center(c, 28, "YOUR STUDIO NAME", "Bold", 28, WHITE)
    # Photo overlay
    photo_placeholder(c, 80, 140, S - 160, 450, "YOUR INTERIOR PHOTO")
    # Service list
    text_center(c, 650, "INTERIOR DETAILING", "Bold", 42, WHITE)
    services = ["Deep Clean & Vacuum", "Leather Conditioning", "Dashboard & Console Detail", "Odor Elimination"]
    for i, svc in enumerate(services):
        bullet_item(c, 240, 720 + i * 38, svc, 18, RED, SILVER)
    # Footer
    contact_footer(c, 940)
    red_bar(c, S - 6, 6)

def post_04(c):
    """PAINT CORRECTION — Before/After split."""
    fill_bg(c)
    red_bar(c, 0, 6)
    logo_placeholder(c, S / 2, 30, 180, 40)
    # Labels
    text_center(c, 110, "PAINT CORRECTION", "Bold", 48, WHITE)
    # Before side
    c.setFillColor(Color(20/255, 20/255, 20/255))
    c.rect(0, ry(180) - 600, S / 2 - 3, 600, fill=1, stroke=0)
    photo_placeholder(c, 30, 200, S / 2 - 63, 560, "BEFORE PHOTO")
    text_center(c, 800, "BEFORE", "Bold", 28, LGRAY)
    # Red divider
    c.setFillColor(RED)
    c.rect(S / 2 - 3, ry(180) - 600, 6, 600, fill=1, stroke=0)
    # After side
    c.setFillColor(Color(25/255, 25/255, 25/255))
    c.rect(S / 2 + 3, ry(180) - 600, S / 2 - 3, 600, fill=1, stroke=0)
    photo_placeholder(c, S / 2 + 33, 200, S / 2 - 63, 560, "AFTER PHOTO")
    # Fix: draw After label on right side
    y = ry(800)
    c.setFont("Bold", 28)
    c.setFillColor(WHITE)
    tw = c.stringWidth("AFTER", "Bold", 28)
    c.drawString(S * 3 / 4 - tw / 2, y, "AFTER")
    # Tagline
    text_center(c, 870, "Results You Can See", "Serif", 22, SILVER)
    red_bar(c, S - 6, 6)

def post_05(c):
    """FULL DETAIL PACKAGES — Three pricing columns."""
    fill_bg(c)
    red_bar(c, 0, 6)
    text_center(c, 80, "FULL DETAIL", "Bold", 56, WHITE)
    text_center(c, 140, "PACKAGES", "Bold", 56, WHITE)
    # Three pricing boxes
    bw = 300
    gap = 30
    start_x = (S - 3 * bw - 2 * gap) / 2
    price_box(c, start_x, 220, bw, 360, "BASIC", "$99",
              ["Exterior Wash", "Tire Shine", "Window Clean", "Air Freshener"])
    price_box(c, start_x + bw + gap, 220, bw, 360, "STANDARD", "$199",
              ["Basic Package +", "Interior Vacuum", "Dashboard Wipe", "Leather Condition"])
    price_box(c, start_x + 2 * (bw + gap), 220, bw, 360, "PREMIUM", "$349",
              ["Standard Package +", "Clay Bar Treatment", "Paint Correction", "Ceramic Coating"])
    # CTA
    cta_button(c, S / 2, 680, "BOOK YOUR DETAIL", 22, 40, 12)
    text_center(c, 760, "All packages include free pickup & delivery", "Regular", 16, SILVER)
    contact_footer(c, 840)
    red_bar(c, S - 6, 6)

def post_06(c):
    """LIMITED TIME OFFER — Percentage off."""
    fill_bg(c)
    # Dark overlay on photo bg
    photo_placeholder(c, 0, 0, S, S, "")
    c.setFillColor(Color(0, 0, 0, 0.7))
    c.rect(0, 0, S, S, fill=1, stroke=0)
    red_pill(c, S / 2, 100, "THIS MONTH ONLY", 22, 24, 10)
    text_center(c, 260, "XX%", "Bold", 160, WHITE)
    text_center(c, 350, "OFF", "Bold", 80, RED)
    text_center(c, 440, "CERAMIC COATING", "Bold", 36, WHITE)
    text_center(c, 490, "Regular price: $XXX", "Regular", 20, SILVER)
    cta_button(c, S / 2, 600, "BOOK NOW", 26, 50, 14)
    text_center(c, 700, "Offer expires: MM/DD/YYYY", "Regular", 18, LGRAY)
    # Contact
    text_center(c, 780, "YOUR STUDIO NAME", "Bold", 20, SILVER)
    contact_footer(c, 830)
    red_bar(c, 0, 6)
    red_bar(c, S - 6, 6)

def post_07(c):
    """FREE QUOTE — Clean dark design."""
    fill_bg(c)
    red_bar(c, 0, 6)
    logo_placeholder(c, S / 2, 50, 180, 40)
    text_center(c, 180, "GET YOUR", "Bold", 48, WHITE)
    text_center(c, 250, "FREE QUOTE", "Bold", 64, WHITE)
    text_center(c, 310, "TODAY", "Bold", 64, RED)
    # Divider
    c.setStrokeColor(RED)
    c.setLineWidth(2)
    c.line(S / 2 - 100, ry(370), S / 2 + 100, ry(370))
    # Checkmarks
    checks = ["Full Exterior Detail", "Interior Deep Clean", "Ceramic Coating Options"]
    for i, item in enumerate(checks):
        checkmark_item(c, 280, 430 + i * 50, item, 22)
    # CTA
    cta_button(c, S / 2, 660, "CALL TODAY", 24, 44, 12)
    text_center(c, 750, "(555) 123-4567", "Bold", 28, WHITE)
    text_center(c, 800, "yourwebsite.com", "Regular", 18, SILVER)
    red_bar(c, S - 6, 6)

def post_08(c):
    """REFERRAL OFFER — Refer a Friend."""
    fill_bg(c)
    red_bar(c, 0, 6)
    logo_placeholder(c, S / 2, 50, 180, 40)
    text_center(c, 200, "REFER A", "Bold", 56, WHITE)
    text_center(c, 275, "FRIEND", "Bold", 72, WHITE)
    # Divider
    c.setStrokeColor(RED)
    c.setLineWidth(3)
    c.line(S / 2 - 120, ry(330), S / 2 + 120, ry(330))
    text_center(c, 410, "$XX OFF", "Bold", 72, RED)
    text_center(c, 475, "YOUR NEXT DETAIL", "Bold", 28, SILVER)
    text_center(c, 550, "Share this post with a friend.", "Regular", 20, LGRAY)
    text_center(c, 580, "When they book, you both save!", "Regular", 20, LGRAY)
    cta_button(c, S / 2, 700, "TAG A FRIEND", 22, 36, 10)
    contact_footer(c, 840)
    red_bar(c, S - 6, 6)

def post_09(c):
    """SEASONAL SPECIAL — Summer Ready."""
    fill_bg(c)
    # Full bleed photo with dark overlay
    photo_placeholder(c, 0, 0, S, S, "")
    c.setFillColor(Color(0, 0, 0, 0.7))
    c.rect(0, 0, S, S, fill=1, stroke=0)
    red_bar(c, 0, 6)
    text_center(c, 140, "SUMMER", "Bold", 80, WHITE)
    text_center(c, 230, "READY?", "Bold", 80, RED)
    diagonal_stripe(c, 310, 60, -8)
    services = ["Full Exterior Wash & Wax", "Interior Steam Clean", "Tire & Wheel Detail", "UV Protection Coating"]
    for i, svc in enumerate(services):
        checkmark_item(c, 240, 440 + i * 48, svc, 22)
    cta_button(c, S / 2, 720, "BOOK NOW", 24, 44, 12)
    text_center(c, 820, "YOUR STUDIO NAME", "Bold", 20, SILVER)
    contact_footer(c, 870)
    red_bar(c, S - 6, 6)

def post_10(c):
    """5-STAR REVIEW — Customer testimonial."""
    fill_bg(c)
    red_bar(c, 0, 6)
    logo_placeholder(c, S / 2, 50, 180, 40)
    draw_stars(c, S / 2, 180, 5, 48, GOLD)
    # Quote
    c.setFont("Serif", 24)
    c.setFillColor(WHITE)
    lines = [
        '"Best detailing service in town!',
        'My car looks brand new.',
        'Highly recommend to everyone."',
    ]
    for i, line in enumerate(lines):
        tw = c.stringWidth(line, "Serif", 24)
        c.drawString((S - tw) / 2, ry(320 + i * 36), line)
    # Customer name
    text_center(c, 470, "— CUSTOMER NAME", "Bold", 18, SILVER)
    # Red accent line
    c.setStrokeColor(RED)
    c.setLineWidth(2)
    c.line(S / 2 - 60, ry(520), S / 2 + 60, ry(520))
    text_center(c, 580, "YOUR STUDIO NAME", "Bold", 24, WHITE)
    text_center(c, 620, "5-Star Rated Detailing", "Regular", 18, SILVER)
    cta_button(c, S / 2, 740, "BOOK NOW", 22, 36, 10)
    contact_footer(c, 870)
    red_bar(c, S - 6, 6)

def post_11(c):
    """BEFORE & AFTER — Cinematic split car design (HERO POST)."""
    # Monochromatic/cinematic — no red accents
    fill_bg(c, Color(18/255, 18/255, 18/255))
    # Dark header bar
    c.setFillColor(Color(10/255, 10/255, 10/255))
    c.rect(0, ry(0) - 120, S, 120, fill=1, stroke=0)
    # "Car Detailing" elegant serif centered
    text_center(c, 55, "Car Detailing", "Serif", 36, WHITE)
    # BEFORE / AFTER labels with divider
    c.setFont("Bold", 16)
    c.setFillColor(Color(180/255, 180/255, 180/255))
    c.drawString(S / 4 - 30, ry(95), "BEFORE")
    # Thin white divider between labels
    c.setStrokeColor(Color(120/255, 120/255, 120/255))
    c.setLineWidth(0.8)
    c.line(S / 2, ry(78), S / 2, ry(100))
    c.setFillColor(WHITE)
    c.setFont("Bold", 16)
    c.drawString(S * 3 / 4 - 22, ry(95), "AFTER")
    # Main car area — split
    # Left half: slightly darker (before)
    c.setFillColor(Color(28/255, 28/255, 28/255))
    c.rect(0, ry(130) - 820, S / 2, 820, fill=1, stroke=0)
    # Right half: slightly lighter (after)
    c.setFillColor(Color(45/255, 45/255, 45/255))
    c.rect(S / 2, ry(130) - 820, S / 2, 820, fill=1, stroke=0)
    # Photo placeholders in each half
    photo_placeholder(c, 40, 180, S / 2 - 80, 700, "BEFORE — YOUR CAR PHOTO")
    photo_placeholder(c, S / 2 + 40, 180, S / 2 - 80, 700, "AFTER — YOUR CAR PHOTO")
    # Thin white vertical divider line down centre
    c.setStrokeColor(Color(200/255, 200/255, 200/255))
    c.setLineWidth(1.2)
    c.line(S / 2, ry(130), S / 2, ry(950))
    # Bottom: @yourstudioname in small italic
    c.setFont("Serif", 16)
    c.setFillColor(Color(140/255, 140/255, 140/255))
    handle = "@yourstudioname"
    tw = c.stringWidth(handle, "Serif", 16)
    c.drawString((S - tw) / 2, ry(1000), handle)
    # Subtle bottom line
    c.setStrokeColor(Color(60/255, 60/255, 60/255))
    c.setLineWidth(0.5)
    c.line(0, ry(1040), S, ry(1040))

def post_12(c):
    """CUSTOMER SPOTLIGHT — Photo + review."""
    fill_bg(c)
    red_bar(c, 0, 70)
    text_center(c, 28, "ANOTHER HAPPY CLIENT", "Bold", 28, WHITE)
    photo_placeholder(c, 140, 100, S - 280, 420, "CUSTOMER + CAR PHOTO")
    # Review quote
    c.setFont("Serif", 20)
    c.setFillColor(WHITE)
    lines = ['"Absolutely amazing work! They transformed', 'my car inside and out. 100% coming back."']
    for i, line in enumerate(lines):
        tw = c.stringWidth(line, "Serif", 20)
        c.drawString((S - tw) / 2, ry(580 + i * 30), line)
    text_center(c, 670, "— CUSTOMER NAME", "Bold", 16, SILVER)
    draw_stars(c, S / 2, 720, 5, 32, GOLD)
    # Footer
    c.setStrokeColor(RED)
    c.setLineWidth(2)
    c.line(S / 2 - 80, ry(780), S / 2 + 80, ry(780))
    text_center(c, 830, "YOUR STUDIO NAME", "Bold", 20, WHITE)
    contact_footer(c, 880)
    red_bar(c, S - 6, 6)

def post_13(c):
    """HOW MANY YEARS? — Stats and trust."""
    fill_bg(c)
    red_bar(c, 0, 6)
    logo_placeholder(c, S / 2, 50, 180, 40)
    # Big stat 1
    text_center(c, 210, "X+", "Bold", 120, WHITE)
    text_center(c, 290, "YEARS IN BUSINESS", "Bold", 32, RED)
    # Divider
    c.setStrokeColor(RED)
    c.setLineWidth(2)
    c.line(S / 2 - 100, ry(340), S / 2 + 100, ry(340))
    # Big stat 2
    text_center(c, 440, "X,XXX+", "Bold", 100, WHITE)
    text_center(c, 510, "HAPPY CLIENTS", "Bold", 32, RED)
    # Divider
    c.line(S / 2 - 100, ry(560), S / 2 + 100, ry(560))
    # Big stat 3
    text_center(c, 650, "5.0", "Bold", 80, WHITE)
    draw_stars(c, S / 2, 710, 5, 36, GOLD)
    text_center(c, 770, "AVERAGE RATING", "Bold", 24, RED)
    text_center(c, 850, "YOUR STUDIO NAME", "Bold", 22, WHITE)
    contact_footer(c, 910)
    red_bar(c, S - 6, 6)

def post_14(c):
    """DID YOU KNOW? — Fact with photo."""
    fill_bg(c)
    red_bar(c, 0, 6)
    red_pill(c, S / 2, 80, "DID YOU KNOW?", 24, 28, 12)
    # Left panel text
    c.setFillColor(DARK)
    c.rect(0, ry(150) - 600, S / 2 - 20, 600, fill=1, stroke=0)
    # Fact text
    lines = [
        "Regular waxing can",
        "protect your car's",
        "paint for up to",
        "6 MONTHS",
        "",
        "Professional detailing",
        "extends your vehicle's",
        "resale value by up to",
        "15%",
    ]
    y_start = 200
    for i, line in enumerate(lines):
        if line in ("6 MONTHS", "15%"):
            text_left(c, 50, y_start + i * 36, line, "Bold", 32, RED)
        elif line == "":
            pass
        else:
            text_left(c, 50, y_start + i * 36, line, "Regular", 20, SILVER)
    # Right photo
    photo_placeholder(c, S / 2 + 20, 150, S / 2 - 40, 600, "DETAIL PHOTO")
    text_center(c, 820, "YOUR STUDIO NAME", "Bold", 20, WHITE)
    cta_button(c, S / 2, 900, "LEARN MORE", 20, 36, 10)
    red_bar(c, S - 6, 6)

def post_15(c):
    """WHY CERAMIC COATING? — 3 Reasons."""
    fill_bg(c)
    red_bar(c, 0, 6)
    text_center(c, 90, "WHY CERAMIC", "Bold", 52, WHITE)
    text_center(c, 155, "COATING?", "Bold", 52, WHITE)
    red_pill(c, S / 2, 220, "3 REASONS", 20, 24, 8)
    # Three reasons
    reasons = [
        ("Long-Lasting Protection", "Shields your paint for 2-5 years against\nUV rays, bird droppings & tree sap"),
        ("Hydrophobic Surface", "Water beads and slides off instantly,\nkeeping your car cleaner for longer"),
        ("Enhanced Gloss & Shine", "Deep mirror-like finish that makes\nyour car look showroom-new"),
    ]
    for i, (title, desc) in enumerate(reasons):
        y = 320 + i * 180
        numbered_item(c, 100, y, i + 1, title, 24)
        for j, dline in enumerate(desc.split("\n")):
            text_left(c, 130, y + 36 + j * 24, dline, "Regular", 16, SILVER)
    cta_button(c, S / 2, 880, "GET A FREE QUOTE", 20, 36, 10)
    contact_footer(c, 960)
    red_bar(c, S - 6, 6)

def post_16(c):
    """DETAILING TIP — Tip of the week."""
    fill_bg(c)
    red_bar(c, 0, 6)
    red_pill(c, S / 2, 80, "#TIP OF THE WEEK", 22, 24, 10)
    text_center(c, 200, "DETAILING", "Bold", 56, WHITE)
    text_center(c, 265, "TIP", "Bold", 56, RED)
    # Tip content area
    c.setFillColor(DARK)
    c.roundRect(80, ry(340) - 340, S - 160, 340, 12, fill=1, stroke=0)
    c.setStrokeColor(RED)
    c.setLineWidth(2)
    c.roundRect(80, ry(340) - 340, S - 160, 340, 12, fill=0, stroke=1)
    lines = [
        "Always wash your car from",
        "top to bottom. Gravity pulls",
        "dirt downward — starting at",
        "the top prevents dragging",
        "grit across clean panels.",
    ]
    for i, line in enumerate(lines):
        text_center(c, 380 + i * 42, line, "Regular", 22, SILVER)
    # Branding
    text_center(c, 770, "YOUR STUDIO NAME", "Bold", 22, WHITE)
    text_center(c, 810, "Follow for more tips!", "Regular", 18, SILVER)
    logo_placeholder(c, S / 2, 880, 160, 40)
    red_bar(c, S - 6, 6)

def post_17(c):
    """BEFORE YOU SELL YOUR CAR — Resale value tips."""
    fill_bg(c)
    red_bar(c, 0, 6)
    text_center(c, 80, "BEFORE YOU", "Bold", 48, WHITE)
    text_center(c, 140, "SELL YOUR CAR", "Bold", 52, RED)
    # Divider
    c.setStrokeColor(RED)
    c.setLineWidth(2)
    c.line(S / 2 - 100, ry(190), S / 2 + 100, ry(190))
    text_center(c, 240, "Boost your resale value with", "Regular", 20, SILVER)
    text_center(c, 270, "professional detailing:", "Regular", 20, SILVER)
    services = [
        "Full Exterior Polish & Wax",
        "Paint Correction & Scratch Removal",
        "Interior Deep Clean & Condition",
        "Engine Bay Detailing",
        "Headlight Restoration",
        "Odor Elimination Treatment",
    ]
    for i, svc in enumerate(services):
        checkmark_item(c, 200, 350 + i * 48, svc, 22)
    text_center(c, 680, "Increase your car's value by up to 15%", "Bold", 20, WHITE)
    cta_button(c, S / 2, 770, "BOOK NOW", 24, 44, 12)
    text_center(c, 860, "YOUR STUDIO NAME", "Bold", 18, SILVER)
    contact_footer(c, 910)
    red_bar(c, S - 6, 6)

def post_18(c):
    """ABOUT US — Who We Are."""
    fill_bg(c)
    red_bar(c, 0, 6)
    text_center(c, 80, "WHO WE ARE", "Bold", 52, WHITE)
    # Divider
    c.setStrokeColor(RED)
    c.setLineWidth(3)
    c.line(S / 2 - 80, ry(130), S / 2 + 80, ry(130))
    photo_placeholder(c, 300, 170, S - 600, 280, "YOUR TEAM PHOTO")
    # Value props
    props = [
        "Professional & Certified Detailers",
        "Premium Products Only",
        "100% Satisfaction Guaranteed",
    ]
    for i, prop in enumerate(props):
        checkmark_item(c, 200, 520 + i * 50, prop, 22)
    # Contact info
    text_center(c, 720, "YOUR STUDIO NAME", "Bold", 28, WHITE)
    text_center(c, 765, "Your City, State", "Regular", 18, SILVER)
    text_center(c, 800, "(555) 123-4567", "Regular", 18, SILVER)
    text_center(c, 835, "yourwebsite.com", "Regular", 18, SILVER)
    logo_placeholder(c, S / 2, 900, 160, 40)
    red_bar(c, S - 6, 6)

def post_19(c):
    """FOLLOW US — Social media."""
    fill_bg(c)
    red_bar(c, 0, 6)
    logo_placeholder(c, S / 2, 60, 200, 50)
    text_center(c, 220, "FOLLOW US", "Bold", 64, WHITE)
    text_center(c, 290, "FOR TIPS & OFFERS", "Bold", 32, RED)
    # Social media placeholders
    platforms = [
        ("Instagram", "@yourstudioname"),
        ("Facebook", "/yourstudioname"),
        ("TikTok", "@yourstudioname"),
    ]
    for i, (platform, handle) in enumerate(platforms):
        y = 400 + i * 100
        c.setFillColor(RED)
        c.roundRect(240, ry(y) - 60, S - 480, 60, 8, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Bold", 20)
        tw = c.stringWidth(f"{platform}:  {handle}", "Bold", 20)
        c.drawString((S - tw) / 2, ry(y) - 28, f"{platform}:  {handle}")
    text_center(c, 770, "Like, Follow & Share", "Regular", 22, SILVER)
    text_center(c, 820, "for exclusive deals!", "Regular", 22, SILVER)
    red_bar(c, S - 6, 6)

def post_20(c):
    """CONTACT US — Clean contact card."""
    fill_bg(c)
    red_bar(c, 0, 6)
    logo_placeholder(c, S / 2, 60, 200, 50)
    text_center(c, 190, "CONTACT US", "Bold", 56, WHITE)
    # Divider
    c.setStrokeColor(RED)
    c.setLineWidth(3)
    c.line(S / 2 - 100, ry(240), S / 2 + 100, ry(240))
    # Contact details with icons (text-based)
    items = [
        ("\u260E  PHONE", "(555) 123-4567"),
        ("\u2709  EMAIL", "hello@yourstudio.com"),
        ("\u2302  WEBSITE", "www.yourstudio.com"),
        ("\u2316  ADDRESS", "123 Main Street, Your City, ST 12345"),
    ]
    for i, (label, value) in enumerate(items):
        y = 340 + i * 110
        # Red label
        text_center(c, y, label, "Bold", 18, RED)
        # Value
        text_center(c, y + 35, value, "Regular", 22, WHITE)
        # Subtle divider
        if i < len(items) - 1:
            c.setStrokeColor(DGRAY)
            c.setLineWidth(1)
            c.line(300, ry(y + 80), S - 300, ry(y + 80))
    # Hours
    text_center(c, 810, "Mon-Sat: 8AM-6PM  |  Sun: By Appointment", "Regular", 16, SILVER)
    # Red footer
    red_bar(c, 920, 160)
    text_center(c, 980, "YOUR STUDIO NAME", "Bold", 28, WHITE)
    text_center(c, 1020, "Premium Auto Detailing", "Regular", 18, WHITE)


# ══════════════════════════════════════════════════════════════
# BUILD ALL
# ══════════════════════════════════════════════════════════════

POSTS = [
    (post_01, "post_01_premium_detailing"),
    (post_02, "post_02_ceramic_coating"),
    (post_03, "post_03_interior_detailing"),
    (post_04, "post_04_paint_correction"),
    (post_05, "post_05_full_detail_packages"),
    (post_06, "post_06_limited_time_offer"),
    (post_07, "post_07_free_quote"),
    (post_08, "post_08_referral_offer"),
    (post_09, "post_09_seasonal_special"),
    (post_10, "post_10_five_star_review"),
    (post_11, "post_11_before_after"),
    (post_12, "post_12_customer_spotlight"),
    (post_13, "post_13_years_in_business"),
    (post_14, "post_14_did_you_know"),
    (post_15, "post_15_why_ceramic_coating"),
    (post_16, "post_16_detailing_tip"),
    (post_17, "post_17_before_you_sell"),
    (post_18, "post_18_about_us"),
    (post_19, "post_19_follow_us"),
    (post_20, "post_20_contact_us"),
]

if __name__ == "__main__":
    for builder, name in POSTS:
        path = f"{OUT_DIR}/{name}.pdf"
        cv = canvas.Canvas(path, pagesize=(S, S))
        builder(cv)
        cv.save()
        size_kb = os.path.getsize(path) // 1024
        print(f"  SAVED: {name}.pdf ({size_kb}KB)")
    print(f"\nAll {len(POSTS)} posts saved to {OUT_DIR}/")
