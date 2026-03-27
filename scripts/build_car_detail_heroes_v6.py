from PIL import Image, ImageDraw, ImageFont
import urllib.request, io, os

BASE_URL = "https://purpleocaz-assets.lon1.digitaloceanspaces.com/templates/car-detail/previews/"
OUT_DIR = "/root/NEW-AI-PROJECT/outputs/car-detail-heroes-v6"
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

SIZE = 2000
img = Image.new("RGB", (SIZE, SIZE), BG)
draw = ImageDraw.Draw(img)

# Red top bar
draw.rectangle([(0, 0), (SIZE, 12)], fill=RED)

# Title
f_title = get_font(90, bold=True)
title = "CAR DETAILING VISUAL BUNDLE"
bbox = draw.textbbox((0, 0), title, font=f_title)
tw = bbox[2] - bbox[0]
draw.text(((SIZE - tw) // 2, 50), title, font=f_title, fill=WHITE)

# Red subtitle bar
f_sub = get_font(52, bold=True)
subtitle = "3 EDITABLE CANVA TEMPLATES"
sub_y = 170
bbox2 = draw.textbbox((0, 0), subtitle, font=f_sub)
sw = bbox2[2] - bbox2[0]
bar_pad = 30
draw.rectangle([(SIZE // 2 - sw // 2 - bar_pad, sub_y - 8),
                (SIZE // 2 + sw // 2 + bar_pad, sub_y + 62)], fill=RED)
draw.text(((SIZE - sw) // 2, sub_y), subtitle, font=f_sub, fill=WHITE)

# Load and process
print("Loading previews...")

# 1. Gift cert — rotate if portrait, force to 840x594
gift = fetch_png("preview_giftcert.png")
print("  Loaded: preview_giftcert.png")
if gift.width < gift.height:
    gift = gift.rotate(90, expand=True)
gift = gift.resize((840, 594), Image.LANCZOS)

# 2. Price list — force to 560x792
price = fetch_png("preview_pricelist.png")
print("  Loaded: preview_pricelist.png")
price = price.resize((560, 792), Image.LANCZOS)

# 3. Loyalty card — crop then force to 580x365
loyalty = fetch_png("preview_loyaltycard.png")
print("  Loaded: preview_loyaltycard.png")
w, h = loyalty.size
loyalty = loyalty.crop((int(w * 0.05), int(h * 0.30), int(w * 0.95), int(h * 0.70)))
loyalty = loyalty.resize((580, 365), Image.LANCZOS)

# Add 3px white border to each, then paste with shadow at hardcoded positions
def add_border(item, border=3):
    bordered = Image.new("RGBA", (item.width + border * 2, item.height + border * 2), (255, 255, 255, 255))
    bordered.paste(item, (border, border), item if item.mode == "RGBA" else None)
    return bordered

paste_with_shadow(img, add_border(gift), 40, 583)
paste_with_shadow(img, add_border(price), 720, 484)
paste_with_shadow(img, add_border(loyalty), 1360, 697)

# Bottom strip
strip_y = 1780
draw.rectangle([(0, strip_y), (SIZE, SIZE)], fill=DARK_STRIP)
draw.rectangle([(0, strip_y), (SIZE, strip_y + 4)], fill=RED)

callout = "GIFT CERTIFICATE  \u00b7  PRICE LIST  \u00b7  LOYALTY CARD"
f_call = get_font(40, bold=False)
bbox3 = draw.textbbox((0, 0), callout, font=f_call)
cw = bbox3[2] - bbox3[0]
draw.text(((SIZE - cw) // 2, strip_y + 40), callout, font=f_call, fill=SILVER)

checks = "\u2713 Instant Download    \u2713 Edit Free in Canva    \u2713 Print Ready"
f_check = get_font(36, bold=True)
bbox4 = draw.textbbox((0, 0), checks, font=f_check)
chw = bbox4[2] - bbox4[0]
draw.text(((SIZE - chw) // 2, strip_y + 110), checks, font=f_check, fill=WHITE)

# Red bottom bar
draw.rectangle([(0, SIZE - 12), (SIZE, SIZE)], fill=RED)

out_path = f"{OUT_DIR}/hero_visual_bundle_v6.png"
img.save(out_path, "PNG", quality=95)
size_kb = os.path.getsize(out_path) // 1024
print(f"SAVED: {out_path} ({size_kb}KB)")
