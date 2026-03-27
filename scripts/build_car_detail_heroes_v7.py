from PIL import Image, ImageDraw, ImageFont
import urllib.request, io, os

BASE_URL = "https://purpleocaz-assets.lon1.digitaloceanspaces.com/templates/car-detail/previews/"
OUT_DIR = "/root/NEW-AI-PROJECT/outputs/car-detail-heroes-v7"
os.makedirs(OUT_DIR, exist_ok=True)

BG = (13, 13, 13)
RED = (224, 32, 32)
WHITE = (255, 255, 255)
DARK_STRIP = (26, 26, 26)
SILVER = (192, 192, 192)

def fetch_png(filename):
    url = BASE_URL + filename
    with urllib.request.urlopen(url) as r:
        return Image.open(io.BytesIO(r.read())).convert("RGBA")

def get_font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def paste_with_shadow(img, thumb, x, y, shadow_offset=10, shadow_color=(40, 40, 40)):
    shadow = Image.new("RGBA", (thumb.width + shadow_offset * 2,
                                 thumb.height + shadow_offset * 2), (0, 0, 0, 0))
    draw_s = ImageDraw.Draw(shadow)
    draw_s.rectangle([(shadow_offset, shadow_offset),
                       (thumb.width + shadow_offset, thumb.height + shadow_offset)],
                      fill=shadow_color + (180,))
    img.paste(shadow.convert("RGB"), (x - shadow_offset, y - shadow_offset))
    if thumb.mode == "RGBA":
        img.paste(thumb, (x, y), thumb)
    else:
        img.paste(thumb, (x, y))

def add_border(item, border=3):
    bordered = Image.new("RGBA", (item.width + border * 2, item.height + border * 2), WHITE + (255,))
    bordered.paste(item, (border, border), item if item.mode == "RGBA" else None)
    return bordered

SIZE = 2000
img = Image.new("RGB", (SIZE, SIZE), BG)
draw = ImageDraw.Draw(img)

# ZONE 1 — Header
draw.rectangle([(0, 0), (SIZE, 12)], fill=RED)

f_title = get_font(85, bold=True)
title = "CAR DETAILING VISUAL BUNDLE"
bbox = draw.textbbox((0, 0), title, font=f_title)
tw = bbox[2] - bbox[0]
draw.text(((SIZE - tw) // 2, 20), title, font=f_title, fill=WHITE)

f_sub = get_font(52, bold=True)
subtitle = "3 EDITABLE CANVA TEMPLATES"
bbox2 = draw.textbbox((0, 0), subtitle, font=f_sub)
sw = bbox2[2] - bbox2[0]
bar_pad = 30
draw.rectangle([(SIZE // 2 - sw // 2 - bar_pad, 130 - 8),
                (SIZE // 2 + sw // 2 + bar_pad, 130 + 62)], fill=RED)
draw.text(((SIZE - sw) // 2, 130), subtitle, font=f_sub, fill=WHITE)

# ZONE 2 — Products
print("Loading previews...")

# TOP ROW: Gift cert full width landscape
gift = fetch_png("preview_giftcert.png")
print("  Loaded: preview_giftcert.png")
if gift.width < gift.height:
    gift = gift.rotate(90, expand=True)
gift = gift.resize((1900, 700), Image.LANCZOS)
paste_with_shadow(img, add_border(gift), 50, 240)

# MIDDLE ROW: Price list (left) + Loyalty card (right)
price = fetch_png("preview_pricelist.png")
print("  Loaded: preview_pricelist.png")
price = price.resize((900, 700), Image.LANCZOS)
paste_with_shadow(img, add_border(price), 50, 980)

loyalty = fetch_png("preview_loyaltycard.png")
print("  Loaded: preview_loyaltycard.png")
w, h = loyalty.size
loyalty = loyalty.crop((int(w * 0.05), int(h * 0.30), int(w * 0.95), int(h * 0.70)))
loyalty = loyalty.resize((900, 567), Image.LANCZOS)
paste_with_shadow(img, add_border(loyalty), 1000, 1100)

# ZONE 3 — Bottom strip
draw.rectangle([(0, 1800), (SIZE, SIZE)], fill=DARK_STRIP)
draw.rectangle([(0, 1800), (SIZE, 1804)], fill=RED)

callout = "GIFT CERTIFICATE  \u00b7  PRICE LIST  \u00b7  LOYALTY CARD"
f_call = get_font(40, bold=False)
bbox3 = draw.textbbox((0, 0), callout, font=f_call)
cw = bbox3[2] - bbox3[0]
draw.text(((SIZE - cw) // 2, 1830), callout, font=f_call, fill=SILVER)

checks = "\u2713 Instant Download    \u2713 Edit Free in Canva    \u2713 Print Ready"
f_check = get_font(36, bold=True)
bbox4 = draw.textbbox((0, 0), checks, font=f_check)
chw = bbox4[2] - bbox4[0]
draw.text(((SIZE - chw) // 2, 1900), checks, font=f_check, fill=WHITE)

draw.rectangle([(0, 1988), (SIZE, SIZE)], fill=RED)

out_path = f"{OUT_DIR}/hero_visual_bundle_v7.png"
img.save(out_path, "PNG", quality=95)
size_kb = os.path.getsize(out_path) // 1024
print(f"SAVED: {out_path} ({size_kb}KB)")
