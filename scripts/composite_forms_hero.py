"""Composite tattoo forms fan onto flatlay background — v7."""

import io
import os
import sys
import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# --- Config ---
BG_PATH = "/tmp/flatlay_background_v2.png"
FORMS_DIR = "/root/NEW-AI-PROJECT/outputs/tattoo-forms"
OUTPUT_PATH = "/tmp/tattoo_client_forms_bundle_hero_v8.png"
CANVAS_SIZE = 3000
FORM_WIDTH = 715
SHADOW_OFFSET = 8
SHADOW_BLUR = 20
SHADOW_OPACITY = int(255 * 0.4)
BANNER_RATIO = 0.25
BANNER_COLOR = (139, 26, 26)  # #8B1A1A
TITLE_TEXT = "TATTOO STUDIO CLIENT FORMS BUNDLE"
SUBTITLE_TEXT = "8 PROFESSIONAL PDF TEMPLATES | INSTANT DOWNLOAD"
GOLD = (201, 169, 110)  # #C9A96E

# Fan layout
FAN_SPREAD_WIDTH = 1200  # total horizontal spread of fan
ROTATIONS = [-21, -15, -9, -3, 3, 9, 15, 21]  # degrees per form

# --- Font helpers ---
_FONT_DIRS = ["/usr/share/fonts/truetype/", "/usr/share/fonts/opentype/"]


def _find_font(keywords, size):
    for kw in keywords:
        for prefix in _FONT_DIRS:
            for root, _, files in os.walk(prefix):
                for f in files:
                    if kw.lower() in f.lower() and f.endswith((".ttf", ".otf")):
                        try:
                            return ImageFont.truetype(os.path.join(root, f), size)
                        except Exception:
                            pass
    return ImageFont.load_default(size=size)


def render_pdf_to_image(pdf_path, dpi=200):
    """Render first page of PDF to PIL Image."""
    doc = fitz.open(pdf_path)
    page = doc[0]
    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    doc.close()
    return img


def add_drop_shadow(img, offset=8, blur=20, opacity=102):
    """Add a drop shadow to a RGBA image, return new RGBA with shadow."""
    w, h = img.size
    pad = blur * 3
    shadow_canvas = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    shadow_mask = img.split()[3]
    shadow_layer = Image.new("RGBA", img.size, (0, 0, 0, opacity))
    shadow_layer.putalpha(shadow_mask)
    shadow_canvas.paste(shadow_layer, (pad + offset, pad + offset))
    shadow_canvas = shadow_canvas.filter(ImageFilter.GaussianBlur(blur))
    shadow_canvas.paste(img, (pad, pad), img)
    return shadow_canvas


def main():
    # 1. Load background, crop from y=200 downward, resize to 3000x3000
    print("Loading background...", flush=True)
    bg = Image.open(BG_PATH).convert("RGB")
    w, h = bg.size
    # Crop from y=200 downward (removes cushion at top)
    bg = bg.crop((0, 350, w, h))
    w, h = bg.size
    # Centre-crop to square
    side = min(w, h)
    left = (w - side) // 2
    top = 0  # keep top since we already cropped the cushion
    bg = bg.crop((left, top, left + side, top + side))
    bg = bg.resize((CANVAS_SIZE, CANVAS_SIZE), Image.LANCZOS)
    canvas = bg.convert("RGBA")

    # 2. Render all 8 PDFs
    print("Rendering PDFs...", flush=True)
    pdf_files = sorted([
        f for f in os.listdir(FORMS_DIR)
        if f.lower().endswith(".pdf")
    ])
    print(f"  Found {len(pdf_files)} PDFs", flush=True)

    form_images = []
    for pdf_file in pdf_files:
        path = os.path.join(FORMS_DIR, pdf_file)
        img = render_pdf_to_image(path, dpi=200)
        ratio = FORM_WIDTH / img.width
        new_h = int(img.height * ratio)
        img = img.resize((FORM_WIDTH, new_h), Image.LANCZOS)
        img = img.convert("RGBA")
        form_images.append((pdf_file, img))

    # 3. Fan layout — each form at a DIFFERENT x position spread across FAN_SPREAD_WIDTH
    num_forms = len(form_images)
    banner_top = int(CANVAS_SIZE * (1 - BANNER_RATIO))
    fan_cx = CANVAS_SIZE // 2 + 150
    # Vertical centre of the photo area (above banner)
    fan_cy = int(banner_top * 0.42) + 200

    # X positions: spread evenly across FAN_SPREAD_WIDTH, centred on canvas
    fan_left = fan_cx - FAN_SPREAD_WIDTH // 2
    x_positions = []
    for i in range(num_forms):
        x = fan_left + int(FAN_SPREAD_WIDTH * i / (num_forms - 1))
        x_positions.append(x)

    # Use specified rotations (or compute if count doesn't match)
    if num_forms == len(ROTATIONS):
        angles = ROTATIONS
    else:
        angles = [-21 + (42 * i / (num_forms - 1)) for i in range(num_forms)]

    print("Compositing fan...", flush=True)
    for i, (pdf_file, form_img) in enumerate(form_images):
        angle = angles[i]
        rotated = form_img.rotate(angle, expand=True, resample=Image.BICUBIC)
        with_shadow = add_drop_shadow(rotated, SHADOW_OFFSET, SHADOW_BLUR, SHADOW_OPACITY)
        # Place at unique x position, centred vertically at fan_cy
        paste_x = x_positions[i] - with_shadow.width // 2
        paste_y = fan_cy - with_shadow.height // 2
        canvas.paste(with_shadow, (paste_x, paste_y), with_shadow)
        rotated.close()
        with_shadow.close()
        print(f"  Placed {pdf_file} at x={x_positions[i]}, angle={angle:.0f} deg", flush=True)

    # 4. Draw banner
    print("Drawing banner...", flush=True)
    draw = ImageDraw.Draw(canvas)
    banner_h = int(CANVAS_SIZE * BANNER_RATIO)
    banner_y = CANVAS_SIZE - banner_h
    draw.rectangle([0, banner_y, CANVAS_SIZE, CANVAS_SIZE], fill=BANNER_COLOR + (255,))

    title_font = _find_font(["DejaVuSans-Bold", "Arial-Bold", "LiberationSans-Bold"], 90)
    subtitle_font = _find_font(["DejaVuSans", "Arial", "LiberationSans"], 45)

    # Centre title
    title_bbox = draw.textbbox((0, 0), TITLE_TEXT, font=title_font)
    title_w = title_bbox[2] - title_bbox[0]
    title_h = title_bbox[3] - title_bbox[1]
    title_x = (CANVAS_SIZE - title_w) // 2
    title_y = banner_y + int(banner_h * 0.30) - title_h // 2
    draw.text((title_x, title_y), TITLE_TEXT, fill=(255, 255, 255, 255), font=title_font)

    # Centre subtitle
    sub_bbox = draw.textbbox((0, 0), SUBTITLE_TEXT, font=subtitle_font)
    sub_w = sub_bbox[2] - sub_bbox[0]
    sub_h = sub_bbox[3] - sub_bbox[1]
    sub_x = (CANVAS_SIZE - sub_w) // 2
    sub_y = banner_y + int(banner_h * 0.60) - sub_h // 2
    draw.text((sub_x, sub_y), SUBTITLE_TEXT, fill=GOLD + (255,), font=subtitle_font)

    # 5. Save
    final = canvas.convert("RGB")
    final.save(OUTPUT_PATH, "PNG", optimize=True)
    print(f"Saved to {OUTPUT_PATH}", flush=True)
    canvas.close()
    final.close()

    # 6. Upload to DO Spaces
    # IMPORTANT: Credentials live in purpleocaz-canva-mcp/.env, NOT NEW-AI-PROJECT/.env
    print("Uploading to DO Spaces...", flush=True)
    import boto3
    from dotenv import load_dotenv
    load_dotenv("/root/NEW-AI-PROJECT/purpleocaz-canva-mcp/.env")

    with open(OUTPUT_PATH, "rb") as f:
        image_bytes = f.read()

    s3 = boto3.client(
        "s3",
        endpoint_url="https://lon1.digitaloceanspaces.com",
        aws_access_key_id=os.getenv("DO_SPACES_KEY"),
        aws_secret_access_key=os.getenv("DO_SPACES_SECRET"),
        region_name="lon1",
    )
    s3.put_object(
        Bucket="purpleocaz-assets",
        Key="thumbnails/tattoo_client_forms_bundle_hero_v8.png",
        Body=image_bytes,
        ContentType="image/png",
        ACL="public-read",
    )
    cdn_url = "https://purpleocaz-assets.lon1.digitaloceanspaces.com/thumbnails/tattoo_client_forms_bundle_hero_v8.png"
    print(f"Uploaded: {cdn_url}", flush=True)


if __name__ == "__main__":
    main()
