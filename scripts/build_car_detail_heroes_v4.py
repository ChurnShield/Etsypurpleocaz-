from PIL import Image, ImageDraw, ImageFont
import urllib.request, io, os

BASE_URL = "https://purpleocaz-assets.lon1.digitaloceanspaces.com/templates/car-detail/previews/"
OUT_DIR = "/root/NEW-AI-PROJECT/outputs/car-detail-heroes-v4"
os.makedirs(OUT_DIR, exist_ok=True)

# Colours
BG = (13, 13, 13)        # #0D0D0D
RED = (224, 32, 32)      # #E02020
WHITE = (255, 255, 255)
DARK_STRIP = (26, 26, 26) # #1A1A1A
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

def paste_with_shadow(img, thumb, x, y, shadow_offset=8, shadow_color=(0, 0, 0)):
    """Paste a thumbnail onto img with a drop shadow behind it."""
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

# FIX 2: Crop loyalty card from A4 page to just the card area
def crop_loyalty_card(img):
    w, h = img.size
    left = int(w * 0.05)
    top = int(h * 0.30)
    right = int(w * 0.95)
    bottom = int(h * 0.72)
    return img.crop((left, top, right, bottom)).resize((520, 327), Image.LANCZOS)

# FIX 3: Rotate gift cert to landscape, crop margins, resize
def crop_gift_cert(img):
    if img.width < img.height:
        img = img.rotate(90, expand=True)
    w, h = img.size
    left = int(w * 0.03)
    top = int(h * 0.03)
    right = int(w * 0.97)
    bottom = int(h * 0.97)
    return img.crop((left, top, right, bottom)).resize((640, 452), Image.LANCZOS)

def draw_hero(filename, title, subtitle, callout, preview_files, bundle_type=None):
    SIZE = 2000
    img = Image.new("RGB", (SIZE, SIZE), BG)
    draw = ImageDraw.Draw(img)

    # Red top bar
    draw.rectangle([(0, 0), (SIZE, 12)], fill=RED)

    # Title
    f_title = get_font(90, bold=True)
    f_sub = get_font(52, bold=True)
    bbox = draw.textbbox((0, 0), title, font=f_title)
    tw = bbox[2] - bbox[0]
    draw.text(((SIZE - tw) // 2, 50), title, font=f_title, fill=WHITE)

    # Red subtitle bar
    sub_y = 170
    bbox2 = draw.textbbox((0, 0), subtitle, font=f_sub)
    sw = bbox2[2] - bbox2[0]
    bar_pad = 30
    draw.rectangle([(SIZE // 2 - sw // 2 - bar_pad, sub_y - 8),
                    (SIZE // 2 + sw // 2 + bar_pad, sub_y + 62)], fill=RED)
    draw.text(((SIZE - sw) // 2, sub_y), subtitle, font=f_sub, fill=WHITE)

    # Preview area
    preview_top = 240
    preview_bottom = 1750
    preview_area_h = preview_bottom - preview_top

    # Load previews
    previews = []
    for pf in preview_files:
        try:
            previews.append(fetch_png(pf))
            print(f"  Loaded: {pf}")
        except Exception as e:
            print(f"  FAILED to load {pf}: {e}")

    n = len(previews)
    if n == 0:
        print("No previews loaded!")

    elif bundle_type == "visual":
        # VISUAL BUNDLE: gift cert (landscape) + price list (portrait) + loyalty card (landscape)
        items = []
        for i, prev in enumerate(previews):
            pf = preview_files[i]
            if "loyaltycard" in pf:
                items.append(crop_loyalty_card(prev))
            elif "giftcert" in pf:
                items.append(crop_gift_cert(prev))
            else:
                # Price list — portrait A4
                pw = 520
                ph = int(pw * 1.414)
                items.append(prev.resize((pw, ph), Image.LANCZOS))

        gap = 40
        total_w = sum(it.width for it in items) + (len(items) - 1) * gap
        x_start = (SIZE - total_w) // 2
        max_h = max(it.height for it in items)
        group_y = preview_top + (preview_area_h - max_h) // 2

        cx = x_start
        for item in items:
            bordered = Image.new("RGBA", (item.width + 6, item.height + 6), (255, 255, 255, 255))
            bordered.paste(item, (3, 3), item if item.mode == "RGBA" else None)
            y = group_y + (max_h - item.height) // 2
            paste_with_shadow(img, bordered, cx, y)
            cx += item.width + gap

    elif bundle_type == "flyer":
        # FIX 1: FLYER PACK — flat side by side, NO rotation, 4 columns
        gap = 40
        thumb_w = (SIZE - 120 - 3 * gap) // 4  # = 460
        thumb_h = int(thumb_w * 1.414)           # = 651 (A4 portrait)
        total_w = 4 * thumb_w + 3 * gap
        x_start = (SIZE - total_w) // 2
        y_start = preview_top + (preview_area_h - thumb_h) // 2

        for i, prev in enumerate(previews[:4]):
            thumb = prev.resize((thumb_w, thumb_h), Image.LANCZOS)
            bordered = Image.new("RGBA", (thumb_w + 6, thumb_h + 6), (255, 255, 255, 255))
            bordered.paste(thumb, (3, 3), thumb if thumb.mode == "RGBA" else None)
            x = x_start + i * (thumb_w + gap)
            paste_with_shadow(img, bordered, x, y_start)

    # Bottom dark strip
    strip_y = 1820
    draw.rectangle([(0, strip_y), (SIZE, SIZE)], fill=DARK_STRIP)
    draw.rectangle([(0, strip_y), (SIZE, strip_y + 4)], fill=RED)

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

    out_path = f"{OUT_DIR}/{filename}"
    img.save(out_path, "PNG", quality=95)
    size_kb = os.path.getsize(out_path) // 1024
    print(f"SAVED: {out_path} ({size_kb}KB)")
    return out_path


# BUILD ONLY THE 2 HEROES THAT NEED FIXES
print("=== BUILDING HERO: FLYER PACK v4 ===")
draw_hero(
    "hero_flyer_pack_v4.png",
    "CAR DETAILING FLYER PACK",
    "4 EDITABLE CANVA TEMPLATES",
    "PROMO  \u00b7  SEASONAL  \u00b7  MOBILE  \u00b7  WALK-IN",
    ["preview_flyer_promo.png", "preview_flyer_seasonal.png",
     "preview_flyer_mobile.png", "preview_flyer_walkin.png"],
    bundle_type="flyer"
)

print("\n=== BUILDING HERO: VISUAL BUNDLE v4 ===")
draw_hero(
    "hero_visual_bundle_v4.png",
    "CAR DETAILING VISUAL BUNDLE",
    "3 EDITABLE CANVA TEMPLATES",
    "GIFT CERTIFICATE  \u00b7  PRICE LIST  \u00b7  LOYALTY CARD",
    ["preview_giftcert.png", "preview_pricelist.png", "preview_loyaltycard.png"],
    bundle_type="visual"
)

print("\n=== DONE — 2 heroes rebuilt ===")
for f in sorted(os.listdir(OUT_DIR)):
    if f.endswith(".png"):
        print(f"  {f}: {os.path.getsize(os.path.join(OUT_DIR, f)) // 1024}KB")
