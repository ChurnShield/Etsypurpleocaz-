#!/usr/bin/env python3
"""
Pet Business Mega Bundle — Hero Image Upgrade
Generates upgraded rank-1 hero images for 4 bundles using Ideogram flatlay + Pillow fan composite.
Pattern: composite_forms_hero.py (tattoo forms v7)

Phase A: Build + Spaces upload → print CDN URLs
Phase B (manual confirmation): Replace rank 1 on Etsy
"""
import io, json, os, sys, uuid, urllib.request, urllib.error, urllib.parse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import boto3
from dotenv import load_dotenv

PROJECT = Path("/root/NEW-AI-PROJECT")
load_dotenv(PROJECT / ".env")
load_dotenv(PROJECT / "purpleocaz-canva-mcp/.env", override=False)

IDEOGRAM_API_KEY = os.environ["IDEOGRAM_API_KEY"]
IDEOGRAM_URL     = "https://api.ideogram.ai/v1/ideogram-v3/generate"
ETSY_BASE        = "https://openapi.etsy.com/v3/application"
SHOP_ID          = "34071205"
API_KEY          = "19d2q2xcg1ccipoj4doub0ee:rj7ou7mzjq"

CANVAS_SIZE   = 3000
FORM_WIDTH    = 700
BANNER_RATIO  = 0.22
SHADOW_OFFSET = 8
SHADOW_BLUR   = 22
SHADOW_OPACITY = int(255 * 0.45)
ROTATIONS     = [-21, -15, -9, -3, 3, 9, 15, 21]
FAN_SPREAD_WIDTH = 1350
GOLD          = (201, 169, 110)

FONT_BOLD    = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# ── Bundle configs ────────────────────────────────────────────────────────────

BUNDLES = [
    {
        "name": "Dog Grooming",
        "niche": "dog-grooming",
        "listing_id": 4478726787,
        "banner_color": (13, 92, 99),        # TEAL #0D5C63
        "title_text": "DOG GROOMING BUSINESS BUNDLE",
        "subtitle_text": "33 PROFESSIONAL CANVA TEMPLATES | £39.99",
        "spaces_key": "thumbnails/pet-bundles/dog-grooming-hero-v2.png",
        "ideogram_prompt": (
            "Professional top-down flatlay photograph, grooming salon desk, "
            "white marble surface, dog brush, squeaky rubber toy, neatly folded "
            "paw print towel, small succulent plant, warm natural soft lighting, "
            "no text, clear empty centre area, photorealistic"
        ),
        "template_dirs": [
            PROJECT / "outputs/dog-grooming/branding",
            PROJECT / "outputs/dog-grooming/forms",
            PROJECT / "outputs/dog-grooming/marketing",
        ],
        "pick": [
            "DG_Business_Card_Dark.png",
            "DG_Business_Card_Light.png",
            "DG_Gift_Certificate.png",
            "DG_Price_List.png",
            "DG_Pet_Intake_Form.png",
            "DG_Grooming_Record_Card.png",
            "DG_Appointment_Card_Dark.png",
            "DG_Invoice.png",
        ],
    },
    {
        "name": "Dog Walking / Pet Sitting",
        "niche": "dog-walking",
        "listing_id": 4478742330,
        "banner_color": (45, 95, 62),         # GREEN #2D5F3E
        "title_text": "DOG WALKING & PET SITTING BUNDLE",
        "subtitle_text": "30 PROFESSIONAL CANVA TEMPLATES | £39.99",
        "spaces_key": "thumbnails/pet-bundles/dog-walking-hero-v2.png",
        "ideogram_prompt": (
            "Professional top-down flatlay photograph, wooden desk surface, "
            "dog leash coiled neatly, bright tennis ball, small treat bag, "
            "house keys, warm natural soft lighting, no text, "
            "clear empty centre area, photorealistic"
        ),
        "template_dirs": [
            PROJECT / "outputs/dog-walking/templates",
        ],
        "pick": [
            "DW_Business_Card_Dark.png",
            "DW_Business_Card_Light.png",
            "DW_Gift_Certificate.png",
            "DW_Invoice.png",
            "DW_Client_Agreement.png",
            "DW_Pet_Intake_Form.png",
            "DW_Daily_Walk_Schedule.png",
            "DW_Appointment_Card_Dark.png",
        ],
    },
    {
        "name": "Dog Training / Puppy School",
        "niche": "dog-training",
        "listing_id": 4478748731,
        "banner_color": (27, 58, 92),          # NAVY #1B3A5C
        "title_text": "DOG TRAINING & PUPPY SCHOOL BUNDLE",
        "subtitle_text": "31 PROFESSIONAL CANVA TEMPLATES | £39.99",
        "spaces_key": "thumbnails/pet-bundles/dog-training-hero-v2.png",
        "ideogram_prompt": (
            "Professional top-down flatlay photograph, training mat surface, "
            "dog training clicker, small treat pouch, rope toy, open notebook, "
            "warm natural soft lighting, no text, "
            "clear empty centre area, photorealistic"
        ),
        "template_dirs": [
            PROJECT / "outputs/dog-training/templates",
        ],
        "pick": [
            "DT_Business_Card_Dark.png",
            "DT_Business_Card_Light.png",
            "DT_Gift_Certificate.png",
            "DT_Invoice.png",
            "DT_Behaviour_Assessment.png",
            "DT_Training_Agreement.png",
            "DT_Certificate.png",
            "DT_Appointment_Card_Dark.png",
        ],
    },
    {
        "name": "Pet Photography",
        "niche": "pet-photography",
        "listing_id": 4478768783,
        "banner_color": (160, 95, 102),        # ROSE_DARK #A05F66
        "title_text": "PET PHOTOGRAPHY BUSINESS BUNDLE",
        "subtitle_text": "26 PROFESSIONAL CANVA TEMPLATES | £39.99",
        "spaces_key": "thumbnails/pet-bundles/pet-photography-hero-v2.png",
        "ideogram_prompt": (
            "Professional top-down flatlay photograph, light wood desk surface, "
            "camera lens on side, scattered polaroid photos, small white flowers, "
            "warm natural soft lighting, no text, "
            "clear empty centre area, photorealistic"
        ),
        "template_dirs": [
            PROJECT / "outputs/pet-photography/templates",
        ],
        "pick": [
            "PP_Business_Card_Dark.png",
            "PP_Business_Card_Light.png",
            "PP_Gift_Certificate.png",
            "PP_Invoice.png",
            "PP_Booking_Form.png",
            "PP_Photo_Release.png",
            "PP_Shot_List.png",
            "PP_Appointment_Card_Dark.png",
        ],
    },
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def font(size, bold=False):
    path = FONT_BOLD if bold else FONT_REGULAR
    return ImageFont.truetype(path, size)


def add_drop_shadow(img, offset=8, blur=22, opacity=115):
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


def generate_flatlay(prompt):
    """Call Ideogram v3 — return PIL Image."""
    print(f"  Calling Ideogram... ", end="", flush=True)
    payload = json.dumps({
        "prompt": prompt,
        "magic_prompt": "OFF",
        "resolution": "1024x1024",
        "rendering_speed": "QUALITY",
        "num_images": 1,
    }).encode()
    req = urllib.request.Request(IDEOGRAM_URL, data=payload, method="POST")
    req.add_header("Api-Key", IDEOGRAM_API_KEY)
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=120) as resp:
        body = json.loads(resp.read())
    image_url = body["data"][0]["url"]
    with urllib.request.urlopen(image_url, timeout=60) as r:
        img_bytes = r.read()
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    print(f"OK ({img.size[0]}x{img.size[1]})", flush=True)
    return img


def load_templates(bundle):
    """Load 8 chosen PNGs from local outputs dirs."""
    # Build lookup across all dirs
    lookup = {}
    for d in bundle["template_dirs"]:
        for p in Path(d).glob("*.png"):
            lookup[p.name] = p

    images = []
    for name in bundle["pick"]:
        path = lookup.get(name)
        if path and path.exists():
            img = Image.open(path).convert("RGBA")
            ratio = FORM_WIDTH / img.width
            new_h = int(img.height * ratio)
            img = img.resize((FORM_WIDTH, new_h), Image.LANCZOS)
            images.append((name, img))
            print(f"    loaded {name}", flush=True)
        else:
            print(f"    MISSING: {name}", flush=True)
    return images


def fan_composite(bg_img, template_images):
    """Composite template fan onto background, return RGBA canvas."""
    bg = bg_img.convert("RGB")
    # Centre-crop to square
    w, h = bg.size
    side = min(w, h)
    left, top = (w - side) // 2, (h - side) // 2
    bg = bg.crop((left, top, left + side, top + side))
    bg = bg.resize((CANVAS_SIZE, CANVAS_SIZE), Image.LANCZOS)
    canvas = bg.convert("RGBA")

    num = len(template_images)
    banner_top = int(CANVAS_SIZE * (1 - BANNER_RATIO))
    fan_cx = CANVAS_SIZE // 2 + 120
    fan_cy = int(banner_top * 0.42) + 180

    fan_left = fan_cx - FAN_SPREAD_WIDTH // 2
    x_positions = [fan_left + int(FAN_SPREAD_WIDTH * i / (num - 1)) for i in range(num)]
    angles = ROTATIONS[:num] if num == 8 else [-21 + (42 * i / (num - 1)) for i in range(num)]

    for i, (name, img) in enumerate(template_images):
        angle = angles[i]
        rotated = img.rotate(angle, expand=True, resample=Image.BICUBIC)
        with_shadow = add_drop_shadow(rotated, SHADOW_OFFSET, SHADOW_BLUR, SHADOW_OPACITY)
        paste_x = x_positions[i] - with_shadow.width // 2
        paste_y = fan_cy - with_shadow.height // 2
        canvas.paste(with_shadow, (paste_x, paste_y), with_shadow)
        rotated.close(); with_shadow.close()
        print(f"    placed {name} at x={x_positions[i]}, angle={angle}°", flush=True)
    return canvas


def draw_banner(canvas, bundle):
    """Draw bottom banner with title + subtitle."""
    draw = ImageDraw.Draw(canvas)
    banner_h = int(CANVAS_SIZE * BANNER_RATIO)
    banner_y = CANVAS_SIZE - banner_h
    bc = bundle["banner_color"]
    draw.rectangle([0, banner_y, CANVAS_SIZE, CANVAS_SIZE], fill=bc + (255,))

    # Gold rule at top of banner
    draw.rectangle([0, banner_y, CANVAS_SIZE, banner_y + 8], fill=GOLD + (255,))

    title_f = font(88, bold=True)
    sub_f   = font(50, bold=False)

    title = bundle["title_text"]
    tb = draw.textbbox((0, 0), title, font=title_f)
    tw = tb[2] - tb[0]; th = tb[3] - tb[1]
    tx = (CANVAS_SIZE - tw) // 2
    ty = banner_y + int(banner_h * 0.28) - th // 2
    draw.text((tx, ty), title, fill=(255, 255, 255, 255), font=title_f)

    sub = bundle["subtitle_text"]
    sb = draw.textbbox((0, 0), sub, font=sub_f)
    sw = sb[2] - sb[0]; sh = sb[3] - sb[1]
    sx = (CANVAS_SIZE - sw) // 2
    sy = banner_y + int(banner_h * 0.68) - sh // 2
    draw.text((sx, sy), sub, fill=GOLD + (255,), font=sub_f)
    return canvas


def upload_to_spaces(local_path, spaces_key):
    s3 = boto3.client(
        "s3",
        endpoint_url="https://lon1.digitaloceanspaces.com",
        aws_access_key_id=os.environ["DO_SPACES_KEY"],
        aws_secret_access_key=os.environ["DO_SPACES_SECRET"],
    )
    s3.upload_file(str(local_path), "purpleocaz-assets", spaces_key,
                   ExtraArgs={"ACL": "public-read", "ContentType": "image/png"})
    url = f"https://purpleocaz-assets.lon1.digitaloceanspaces.com/{spaces_key}"
    with urllib.request.urlopen(url) as r:
        assert r.status == 200, f"Spaces verify failed: {url}"
    print(f"  Uploaded → {url}", flush=True)
    return url


def get_etsy_token():
    tokens = json.loads((PROJECT / "workflows/etsy_analytics/etsy_tokens.json").read_text())
    return tokens["access_token"]


def replace_rank1_image(listing_id, img_path):
    """Delete existing rank 1, upload new image at rank 1."""
    at = get_etsy_token()
    headers_base = {"x-api-key": API_KEY, "Authorization": f"Bearer {at}"}

    # GET current images
    req = urllib.request.Request(f"{ETSY_BASE}/listings/{listing_id}/images",
                                  headers=headers_base, method="GET")
    with urllib.request.urlopen(req) as r:
        imgs = json.loads(r.read())

    # Find rank 1
    rank1 = next((im for im in imgs["results"] if im["rank"] == 1), None)
    if rank1:
        img_id = rank1["listing_image_id"]
        req = urllib.request.Request(
            f"{ETSY_BASE}/shops/{SHOP_ID}/listings/{listing_id}/images/{img_id}",
            headers=headers_base, method="DELETE")
        with urllib.request.urlopen(req) as r:
            r.read()
        print(f"  Deleted old rank 1 (image_id {img_id})", flush=True)

    # Upload new rank 1
    boundary = uuid.uuid4().hex
    img_data = open(img_path, "rb").read()
    fn = Path(img_path).name
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"rank\"\r\n\r\n1\r\n"
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; "
            f"filename=\"{fn}\"\r\nContent-Type: image/png\r\n\r\n").encode() + \
           img_data + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(
        f"{ETSY_BASE}/shops/{SHOP_ID}/listings/{listing_id}/images",
        data=body, method="POST")
    req.add_header("x-api-key", API_KEY)
    req.add_header("Authorization", f"Bearer {at}")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    with urllib.request.urlopen(req) as r:
        result = json.loads(r.read())
    print(f"  New rank 1 uploaded — image_id: {result['listing_image_id']}", flush=True)

    # Verify
    req = urllib.request.Request(f"{ETSY_BASE}/listings/{listing_id}/images",
                                  headers=headers_base, method="GET")
    with urllib.request.urlopen(req) as r:
        check = json.loads(r.read())
    print(f"  GET images → count: {check['count']}", flush=True)
    rank1_new = next((im for im in check["results"] if im["rank"] == 1), None)
    if rank1_new:
        print(f"  Rank 1 confirmed: image_id {rank1_new['listing_image_id']}", flush=True)
    return result


def build_hero(bundle):
    print(f"\n{'='*60}")
    print(f"BUILDING: {bundle['name']}")
    print(f"{'='*60}")

    out_dir = PROJECT / "outputs" / bundle["niche"] / "listing"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{bundle['niche']}_hero_v2.png"

    # Phase 1: Ideogram flatlay
    print("\n[1] Ideogram flatlay...")
    bg = generate_flatlay(bundle["ideogram_prompt"])

    # Phase 2: Load templates
    print("\n[2] Loading templates...")
    templates = load_templates(bundle)
    print(f"  {len(templates)}/8 templates loaded")

    # Phase 3: Fan composite
    print("\n[3] Fan composite...")
    canvas = fan_composite(bg, templates)

    # Phase 4: Banner
    print("\n[4] Banner...")
    canvas = draw_banner(canvas, bundle)

    # Phase 5: Save
    final = canvas.convert("RGB")
    final.save(str(out_path), "PNG", optimize=True)
    print(f"\n[5] Saved → {out_path}")
    canvas.close(); final.close()
    for _, img in templates:
        img.close()

    # Phase 6: Upload to Spaces
    print("\n[6] Uploading to Spaces...")
    url = upload_to_spaces(out_path, bundle["spaces_key"])

    return out_path, url


def main():
    print("PET BUSINESS MEGA BUNDLE — HERO IMAGE UPGRADE")
    print("Building all 4 heroes. Spaces URLs shown before any Etsy changes.\n")

    results = []
    for bundle in BUNDLES:
        out_path, url = build_hero(bundle)
        results.append((bundle, out_path, url))

    print("\n" + "="*60)
    print("PHASE A COMPLETE — ALL 4 HEROES ON SPACES")
    print("="*60)
    for bundle, out_path, url in results:
        print(f"\n  {bundle['name']} (#{bundle['listing_id']})")
        print(f"  {url}")

    print("\n" + "="*60)
    print("CONFIRM: Replacing rank 1 on all 4 Etsy listings...")
    print("="*60)

    for bundle, out_path, url in results:
        print(f"\n[Etsy] {bundle['name']} #{bundle['listing_id']}")
        replace_rank1_image(bundle["listing_id"], out_path)
        print(f"  Done.")

    print("\n" + "="*60)
    print("ALL 4 HERO UPGRADES COMPLETE")
    for bundle, out_path, url in results:
        print(f"  {bundle['name']}: {url}")
    print("="*60)


if __name__ == "__main__":
    main()
