from PIL import Image, ImageDraw, ImageFont
import urllib.request, io, os

BASE_URL = "https://purpleocaz-assets.lon1.digitaloceanspaces.com/templates/car-detail/previews/"
OUT_DIR = "/root/NEW-AI-PROJECT/outputs/car-detail-heroes-v9"
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

def add_border(item, border=3):
    bordered = Image.new("RGBA", (item.width + border * 2, item.height + border * 2), WHITE + (255,))
    bordered.paste(item, (border, border), item if item.mode == "RGBA" else None)
    return bordered

def paste_with_shadow(canvas, thumb, x, y, shadow_offset=15):
    # Create a temp RGBA layer for shadow + image
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    # Shadow
    shadow = Image.new("RGBA", (thumb.width, thumb.height), (0, 0, 0, 160))
    layer.paste(shadow, (x + shadow_offset, y + shadow_offset), shadow)
    # Image
    if thumb.mode == "RGBA":
        layer.paste(thumb, (x, y), thumb)
    else:
        layer.paste(thumb, (x, y))
    # Composite onto canvas
    canvas_rgba = canvas.convert("RGBA")
    result = Image.alpha_composite(canvas_rgba, layer)
    canvas.paste(result.convert("RGB"))

SIZE = 2000
img = Image.new("RGB", (SIZE, SIZE), BG)
draw = ImageDraw.Draw(img)

# HEADER
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
draw.rectangle([(SIZE // 2 - sw // 2 - bar_pad, 135 - 8),
                (SIZE // 2 + sw // 2 + bar_pad, 135 + 62)], fill=RED)
draw.text(((SIZE - sw) // 2, 135), subtitle, font=f_sub, fill=WHITE)

print("Loading previews...")

# LAYER 1 — Gift cert (back layer, full width landscape)
gift = fetch_png("preview_giftcert.png")
print("  Loaded: preview_giftcert.png")
if gift.width < gift.height:
    gift = gift.rotate(90, expand=True)
gift = gift.resize((1800, 640), Image.LANCZOS)
gift_bordered = add_border(gift)
paste_with_shadow(img, gift_bordered, 100, 350)

# LAYER 2 — Price list (middle layer, cropped, rotated -5 deg)
price = fetch_png("preview_pricelist.png")
print("  Loaded: preview_pricelist.png")
w, h = price.size
price = price.crop((0, int(h * 0.40), w, h))
price = price.resize((520, 720), Image.LANCZOS)
price_bordered = add_border(price)
price_rotated = price_bordered.rotate(-5, expand=True, fillcolor=(0, 0, 0, 0))
paste_with_shadow(img, price_rotated, 180, 580)

# LAYER 3 — Loyalty card (top layer, cropped, rotated +4 deg)
loyalty = fetch_png("preview_loyaltycard.png")
print("  Loaded: preview_loyaltycard.png")
w, h = loyalty.size
loyalty = loyalty.crop((int(w * 0.05), int(h * 0.30), int(w * 0.95), int(h * 0.70)))
loyalty = loyalty.resize((680, 428), Image.LANCZOS)
loyalty_bordered = add_border(loyalty)
loyalty_rotated = loyalty_bordered.rotate(4, expand=True, fillcolor=(0, 0, 0, 0))
paste_with_shadow(img, loyalty_rotated, 1100, 900)

# BOTTOM STRIP
draw = ImageDraw.Draw(img)
draw.rectangle([(0, 1780), (SIZE, SIZE)], fill=DARK_STRIP)
draw.rectangle([(0, 1780), (SIZE, 1784)], fill=RED)

callout = "GIFT CERTIFICATE  \u00b7  PRICE LIST  \u00b7  LOYALTY CARD"
f_call = get_font(40, bold=False)
bbox3 = draw.textbbox((0, 0), callout, font=f_call)
cw = bbox3[2] - bbox3[0]
draw.text(((SIZE - cw) // 2, 1810), callout, font=f_call, fill=SILVER)

checks = "\u2713 Instant Download    \u2713 Edit Free in Canva    \u2713 Print Ready"
f_check = get_font(36, bold=True)
bbox4 = draw.textbbox((0, 0), checks, font=f_check)
chw = bbox4[2] - bbox4[0]
draw.text(((SIZE - chw) // 2, 1900), checks, font=f_check, fill=WHITE)

draw.rectangle([(0, 1988), (SIZE, SIZE)], fill=RED)

out_path = f"{OUT_DIR}/hero_visual_bundle_v9.png"
img.save(out_path, "PNG", quality=95)
size_kb = os.path.getsize(out_path) // 1024
print(f"SAVED: {out_path} ({size_kb}KB)")
