from PIL import Image, ImageDraw, ImageFont
import urllib.request, io, os

BASE_URL = "https://purpleocaz-assets.lon1.digitaloceanspaces.com/templates/car-detail/previews/"
OUT_DIR = "/root/NEW-AI-PROJECT/outputs/car-detail-heroes-v3"
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

def fix_loyalty_card(prev):
    """Rotate loyalty card to landscape if it's portrait."""
    if prev.width < prev.height:
        prev = prev.rotate(90, expand=True)
    return prev.resize((520, 328), Image.LANCZOS)

def draw_hero(filename, title, subtitle, callout, preview_files, layout="fan",
              bundle_type=None):
    SIZE = 2000
    img = Image.new("RGB", (SIZE, SIZE), BG)
    draw = ImageDraw.Draw(img)

    # Red top bar (full width, 12px)
    draw.rectangle([(0, 0), (SIZE, 12)], fill=RED)

    # Title text - large bold centred
    f_title = get_font(90, bold=True)
    f_sub = get_font(52, bold=True)

    # Title centred at y=60
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

    # Product previews area — expanded to fill more canvas
    preview_top = 240
    preview_bottom = 1750
    preview_area_h = preview_bottom - preview_top

    # Load preview images
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
        # VISUAL BUNDLE: 3 items flat side-by-side, no rotation
        # Fix loyalty card orientation
        fixed = []
        for i, prev in enumerate(previews):
            pf = preview_files[i]
            if "loyaltycard" in pf:
                fixed.append(fix_loyalty_card(prev))
            else:
                fixed.append(prev)
        previews = fixed

        # All 3 side by side, equal width, 40px gaps
        item_w = 520
        gap = 40
        total_w = 3 * item_w + 2 * gap
        x_start = (SIZE - total_w) // 2

        # Calculate heights for each item maintaining aspect ratio
        items = []
        for i, prev in enumerate(previews):
            pf = preview_files[i]
            if "loyaltycard" in pf:
                # Already fixed to 520x328
                items.append(prev.resize((item_w, 328), Image.LANCZOS))
            elif "giftcert" in pf:
                # Gift cert landscape
                h = int(item_w * prev.height / prev.width)
                items.append(prev.resize((item_w, h), Image.LANCZOS))
            else:
                # Price list portrait
                h = int(item_w * 1.414)
                items.append(prev.resize((item_w, h), Image.LANCZOS))

        # Find max height to centre group vertically
        max_h = max(it.height for it in items)
        group_y = preview_top + (preview_area_h - max_h) // 2

        for i, item in enumerate(items):
            # Add white border
            bordered = Image.new("RGBA", (item.width + 6, item.height + 6), (255, 255, 255, 255))
            bordered.paste(item, (3, 3), item if item.mode == "RGBA" else None)
            x = x_start + i * (item_w + gap)
            y = group_y + (max_h - item.height) // 2
            paste_with_shadow(img, bordered, x, y)

    elif bundle_type == "forms":
        # FORMS BUNDLE: 8 items in 4x2 grid, larger thumbnails
        cols = 4
        rows = 2
        gap = 20
        thumb_w = (SIZE - 80 - 3 * gap) // 4
        thumb_h = int(thumb_w * 1.414)
        total_grid_w = cols * thumb_w + (cols - 1) * gap
        total_grid_h = rows * thumb_h + (rows - 1) * gap
        x_start = (SIZE - total_grid_w) // 2
        y_start = preview_top + (preview_area_h - total_grid_h) // 2

        for i, prev in enumerate(previews):
            row = i // cols
            col = i % cols
            thumb = prev.resize((thumb_w, thumb_h), Image.LANCZOS)
            bordered = Image.new("RGBA", (thumb_w + 4, thumb_h + 4), (255, 255, 255, 255))
            bordered.paste(thumb, (2, 2), thumb if thumb.mode == "RGBA" else None)
            x = x_start + col * (thumb_w + gap)
            y = y_start + row * (thumb_h + gap)
            paste_with_shadow(img, bordered, x, y)

    elif bundle_type == "business":
        # BUSINESS BUNDLE: 15 items in 5x3 grid, optimised sizes
        cols = 5
        rows = 3
        gap = 20
        thumb_w = (SIZE - 80 - 4 * gap) // 5
        thumb_h = int(thumb_w * 1.2)
        total_grid_w = cols * thumb_w + (cols - 1) * gap
        total_grid_h = rows * thumb_h + (rows - 1) * gap
        x_start = (SIZE - total_grid_w) // 2
        y_start = preview_top + (preview_area_h - total_grid_h) // 2

        for i, prev in enumerate(previews):
            row = i // cols
            col = i % cols
            thumb = prev.resize((thumb_w, thumb_h), Image.LANCZOS)
            bordered = Image.new("RGBA", (thumb_w + 4, thumb_h + 4), (255, 255, 255, 255))
            bordered.paste(thumb, (2, 2), thumb if thumb.mode == "RGBA" else None)
            x = x_start + col * (thumb_w + gap)
            y = y_start + row * (thumb_h + gap)
            paste_with_shadow(img, bordered, x, y)

    elif n <= 4:
        # FLYER PACK: fanned layout with larger thumbnails
        thumb_w = min(500, (SIZE - 160) // n)
        thumb_h = int(thumb_w * 1.414)  # A4 ratio
        angles = [-8, -3, 3, 8][:n]
        total_w = n * thumb_w + (n - 1) * 30
        x_start = (SIZE - total_w) // 2
        for i, (prev, angle) in enumerate(zip(previews, angles)):
            thumb = prev.resize((thumb_w, thumb_h), Image.LANCZOS)
            # Add white border
            bordered = Image.new("RGBA", (thumb_w + 6, thumb_h + 6), (255, 255, 255, 255))
            bordered.paste(thumb, (3, 3), thumb if thumb.mode == "RGBA" else None)
            rotated = bordered.rotate(angle, expand=True, fillcolor=(13, 13, 13))
            rx, ry = rotated.size
            x = x_start + i * (thumb_w + 30) - (rx - thumb_w) // 2
            y = preview_top + (preview_area_h - ry) // 2
            # Shadow for rotated items — paste rotated directly (shadow on rotated is complex)
            paste_with_shadow(img, rotated, x, y)

    else:
        # Generic grid fallback
        cols = 5 if n >= 10 else 4 if n >= 7 else 3
        rows = -(-n // cols)
        gap = 20
        thumb_w = (SIZE - 80 - (cols - 1) * gap) // cols
        thumb_h = int(thumb_w * 1.35)
        total_grid_w = cols * thumb_w + (cols - 1) * gap
        total_grid_h = rows * thumb_h + (rows - 1) * gap
        x_start = (SIZE - total_grid_w) // 2
        y_start = preview_top + (preview_area_h - total_grid_h) // 2
        for i, prev in enumerate(previews):
            row = i // cols
            col = i % cols
            thumb = prev.resize((thumb_w, thumb_h), Image.LANCZOS)
            bordered = Image.new("RGBA", (thumb_w + 4, thumb_h + 4), (255, 255, 255, 255))
            bordered.paste(thumb, (2, 2), thumb if thumb.mode == "RGBA" else None)
            x = x_start + col * (thumb_w + gap)
            y = y_start + row * (thumb_h + gap)
            paste_with_shadow(img, bordered, x, y)

    # Bottom dark strip with callouts
    strip_y = 1820
    draw.rectangle([(0, strip_y), (SIZE, SIZE)], fill=DARK_STRIP)
    # Red rule at top of strip
    draw.rectangle([(0, strip_y), (SIZE, strip_y + 4)], fill=RED)

    # Callout text centred in strip
    f_call = get_font(40, bold=False)
    bbox3 = draw.textbbox((0, 0), callout, font=f_call)
    cw = bbox3[2] - bbox3[0]
    draw.text(((SIZE - cw) // 2, strip_y + 40), callout, font=f_call, fill=SILVER)

    # Bottom checkmarks
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


# BUILD ALL 4 HEROES
print("=== BUILDING HERO 1: FORMS BUNDLE ===")
draw_hero(
    "hero_forms_bundle_v3.png",
    "CAR DETAILING FORMS BUNDLE",
    "8 EDITABLE CANVA TEMPLATES",
    "CLIENT INTAKE  \u00b7  CONSENT  \u00b7  INVOICE  \u00b7  CHECKLIST",
    ["preview_intake.png", "preview_consent.png", "preview_agreement.png",
     "preview_invoice.png", "preview_feedback.png", "preview_booking.png",
     "preview_aftercare.png", "preview_menu.png"],
    bundle_type="forms"
)

print("\n=== BUILDING HERO 2: VISUAL BUNDLE ===")
draw_hero(
    "hero_visual_bundle_v3.png",
    "CAR DETAILING VISUAL BUNDLE",
    "3 EDITABLE CANVA TEMPLATES",
    "GIFT CERTIFICATE  \u00b7  PRICE LIST  \u00b7  LOYALTY CARD",
    ["preview_giftcert.png", "preview_pricelist.png", "preview_loyaltycard.png"],
    bundle_type="visual"
)

print("\n=== BUILDING HERO 3: FLYER PACK ===")
draw_hero(
    "hero_flyer_pack_v3.png",
    "CAR DETAILING FLYER PACK",
    "4 EDITABLE CANVA TEMPLATES",
    "PROMO  \u00b7  SEASONAL  \u00b7  MOBILE  \u00b7  WALK-IN",
    ["preview_flyer_promo.png", "preview_flyer_seasonal.png",
     "preview_flyer_mobile.png", "preview_flyer_walkin.png"],
    bundle_type="flyer"
)

print("\n=== BUILDING HERO 4: BUSINESS BUNDLE (15 templates) ===")
draw_hero(
    "hero_business_bundle_v3.png",
    "COMPLETE CAR DETAILING BUNDLE",
    "15 EDITABLE CANVA TEMPLATES",
    "FORMS  \u00b7  FLYERS  \u00b7  GIFT CERT  \u00b7  PRICE LIST  \u00b7  LOYALTY CARD",
    ["preview_intake.png", "preview_consent.png", "preview_agreement.png",
     "preview_invoice.png", "preview_feedback.png", "preview_booking.png",
     "preview_aftercare.png", "preview_menu.png",
     "preview_giftcert.png", "preview_pricelist.png", "preview_loyaltycard.png",
     "preview_flyer_promo.png", "preview_flyer_seasonal.png",
     "preview_flyer_mobile.png", "preview_flyer_walkin.png"],
    bundle_type="business"
)

print("\n=== ALL 4 HEROES BUILT ===")
import glob
for f in sorted(glob.glob(f"{OUT_DIR}/*.png")):
    print(f"  {os.path.basename(f)}: {os.path.getsize(f) // 1024}KB")
