#!/usr/bin/env python3
"""
hero_pipeline_v3.py — "Wow" hero image builder.

Layers (back to front):
  1. Ideogram lifestyle background (3000×3000)
  2. iPad device mockup — A4 form / price list on screen
  3. Phone device mockup — social post on screen
  4. Printed cards with perspective transform + contact shadows
  5. Dark gradient bar fading into solid banner
  6. Title text + subtitle + price badge

Usage:
    python3 scripts/hero_pipeline_v3.py \\
        --niche dog_grooming \\
        --templates-dir outputs/dog-grooming/ \\
        --output outputs/dog-grooming/listing/hero_v3.png

Flags:
    --listing-id 4478726787   also replaces rank 1 on Etsy after upload
    --skip-ideogram           reuse cached background from /tmp/hero_bg_{niche}.png
    --accent "13,92,99"       banner RGB (default: teal)
    --price "£39.99"          price badge text
"""

import argparse, glob, io, json, os, sys, urllib.request, uuid
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import boto3
from dotenv import load_dotenv

PROJECT = Path(__file__).parent.parent
load_dotenv(PROJECT / ".env")
load_dotenv(PROJECT / "purpleocaz-canva-mcp/.env", override=False)

# ── Constants ────────────────────────────────────────────────────────────────

CANVAS       = 3000
FONT_BOLD    = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG     = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
GOLD         = (201, 169, 110)
DEVICE_COL   = (30, 30, 35)      # device bezel colour
SCREEN_BG    = (10, 10, 14)      # screen background before template loads
SHOP_ID      = "34071205"
API_KEY      = "19d2q2xcg1ccipoj4doub0ee:rj7ou7mzjq"
ETSY_BASE    = "https://openapi.etsy.com/v3/application"
IDEOGRAM_URL = "https://api.ideogram.ai/v1/ideogram-v3/generate"

# Each entry is (prompt, negative_prompt).
# negative_prompt prevents cross-niche contamination (e.g. pet elements bleeding into food niches).
NICHE_PROMPTS = {
    "dog_grooming":    (
        "Professional top-down flatlay, grooming salon desk, white marble surface, dog brush, squeaky toy, paw print towel, warm soft lighting, no text, photorealistic",
        "food, menu, coffee, restaurant, text, watermark",
    ),
    "dog_walking":     (
        "Professional top-down flatlay, wooden desk, dog leash coiled neatly, tennis ball, treat bag, house keys, warm soft lighting, no text, photorealistic",
        "food, menu, coffee, restaurant, text, watermark",
    ),
    "dog_training":    (
        "Professional top-down flatlay, training mat surface, dog clicker, treat pouch, rope toy, open notebook, warm soft lighting, no text, photorealistic",
        "food, menu, coffee, restaurant, text, watermark",
    ),
    "pet_photography": (
        "Professional top-down flatlay, light wood desk, camera lens, scattered polaroid photos, small white flowers, warm soft lighting, no text, photorealistic",
        "food, menu, coffee, restaurant, text, watermark",
    ),
    "car_detail":      (
        "Professional top-down flatlay, dark concrete surface, microfiber cloth, spray bottle, detailing brush, warm lighting, no text, photorealistic",
        "animals, pets, paws, food, text, watermark",
    ),
    "tattoo":          (
        "Professional top-down flatlay, white marble surface, tattoo machine, ink pot, succulent, warm soft lighting, no text, photorealistic",
        "animals, pets, paws, food, text, watermark",
    ),
    "barbershop":      (
        "Professional top-down flatlay, marble barbershop counter, straight razor, comb, scissors, warm soft lighting, no text, photorealistic",
        "animals, pets, paws, food, text, watermark",
    ),
    "generic":         (
        "Professional top-down flatlay, white marble desk, coffee cup, green plant, notebook, warm soft lighting, no text, photorealistic",
        "animals, pets, paws, text, watermark",
    ),
    "restaurant_cafe": (
        "Professional top-down flatlay, rustic dark wooden restaurant table, single espresso cup with foam art, folded linen napkin, silver cutlery, small glass vase with herb sprig, scattered whole coffee beans, warm amber candlelight, rich warm tones, appetising, no text, photorealistic, no animals",
        "animal, pet, dog, cat, paw, paw print, bird, fur, leash, collar, collar tag, text, watermark, logo",
    ),
}

EXCLUDE_NAMES = {"listing", "preview", "hero", "grid", "eval"}

# ── Font + shadow helpers ─────────────────────────────────────────────────────

def f(size, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


def drop_shadow(img: Image.Image, offset=(12, 16), blur=26, opacity=155) -> Image.Image:
    """Composite soft drop shadow behind img. Returns larger RGBA image."""
    img = img.convert("RGBA")
    pad = blur * 3
    out = Image.new("RGBA", (img.width + pad*2, img.height + pad*2), (0,0,0,0))
    sh = Image.new("RGBA", img.size, (0, 0, 0, opacity))
    sh.putalpha(img.split()[3])
    out.paste(sh, (pad + offset[0], pad + offset[1]))
    out = out.filter(ImageFilter.GaussianBlur(blur))
    out.paste(img, (pad, pad), img)
    return out


# ── Device frame builders ─────────────────────────────────────────────────────

def draw_ipad(tmpl: Image.Image, fw=800, fh=1050) -> Image.Image:
    """iPad portrait frame with template on screen. Returns RGBA."""
    bv, bt, bb = 44, 58, 74          # bezel: side, top, bottom
    frame = Image.new("RGBA", (fw, fh), (0,0,0,0))
    d = ImageDraw.Draw(frame)
    d.rounded_rectangle([0, 0, fw-1, fh-1], radius=64, fill=DEVICE_COL)
    sx, sy, sw, sh = bv, bt, fw-bv*2, fh-bt-bb
    d.rectangle([sx, sy, sx+sw, sy+sh], fill=SCREEN_BG)
    # front camera dot
    cx = fw // 2
    d.ellipse([cx-6, sy+14, cx+6, sy+26], fill=(20, 20, 26))
    # home indicator bar
    bw = 130
    d.rounded_rectangle([(fw-bw)//2, fh-bb//2-4, (fw+bw)//2, fh-bb//2+4], radius=4, fill=(72,72,80))
    # template on screen
    t = tmpl.convert("RGBA").resize((sw, sh), Image.LANCZOS)
    frame.paste(t, (sx, sy), t)
    return frame


def draw_phone(tmpl: Image.Image, fw=400, fh=820) -> Image.Image:
    """Phone portrait frame with template on screen. Returns RGBA."""
    bv, bt, bb = 26, 58, 44
    frame = Image.new("RGBA", (fw, fh), (0,0,0,0))
    d = ImageDraw.Draw(frame)
    d.rounded_rectangle([0, 0, fw-1, fh-1], radius=52, fill=DEVICE_COL)
    sx, sy, sw, sh = bv, bt, fw-bv*2, fh-bt-bb
    d.rounded_rectangle([sx, sy, sx+sw, sy+sh], radius=14, fill=SCREEN_BG)
    # dynamic island
    niw, nih = 90, 26
    nix, niy = (fw-niw)//2, sy+10
    d.rounded_rectangle([nix, niy, nix+niw, niy+nih], radius=13, fill=DEVICE_COL)
    # home bar
    bw = 100
    d.rounded_rectangle([(fw-bw)//2, fh-bb//2-3, (fw+bw)//2, fh-bb//2+3], radius=3, fill=(72,72,80))
    # template — scale to fill screen width, centre vertically
    t = tmpl.convert("RGBA")
    scale = sw / t.width
    nw, nh = sw, int(t.height * scale)
    if nh > sh:
        scale = sh / t.height
        nw, nh = int(t.width * scale), sh
    t = t.resize((nw, nh), Image.LANCZOS)
    frame.paste(t, (sx + (sw-nw)//2, sy + (sh-nh)//2), t)
    return frame


# ── Perspective card transform ────────────────────────────────────────────────

def _persp_coeffs(src, dst):
    """PIL PERSPECTIVE coefficients: output(x,y) → source(X,Y)."""
    A, b = [], []
    for (X, Y), (x, y) in zip(src, dst):
        A += [[x,y,1,0,0,0,-X*x,-X*y], [0,0,0,x,y,1,-Y*x,-Y*y]]
        b += [X, Y]
    c, *_ = np.linalg.lstsq(np.array(A, dtype=np.float64),
                             np.array(b, dtype=np.float64), rcond=None)
    return c.tolist()


def warp_card(card: Image.Image, quad: list) -> Image.Image:
    """Return CANVAS×CANVAS RGBA with card perspective-warped to quad corners (TL,TR,BR,BL)."""
    w, h = card.size
    coeffs = _persp_coeffs([(0,0),(w,0),(w,h),(0,h)], quad)
    return card.convert("RGBA").transform(
        (CANVAS, CANVAS), Image.PERSPECTIVE, coeffs, Image.BICUBIC)


def card_contact_shadow(warped: Image.Image, offset=(20,28), blur=26, opacity=120) -> Image.Image:
    """Soft contact shadow from a perspective-warped card on the canvas."""
    alpha = warped.split()[3]
    shifted = Image.new("L", (CANVAS, CANVAS), 0)
    shifted.paste(alpha, (offset[0], offset[1]))
    shadow = Image.new("RGBA", (CANVAS, CANVAS), (0,0,0,0))
    dark   = Image.new("RGBA", (CANVAS, CANVAS), (0,0,0,opacity))
    dark.putalpha(shifted)
    dark = dark.filter(ImageFilter.GaussianBlur(blur))
    shadow.paste(dark, (0,0), dark)
    return shadow


# ── Template picker ───────────────────────────────────────────────────────────

def pick_templates(templates_dir: Path):
    """Classify PNGs by aspect ratio, return (ipad_path, phone_path, [card_paths])."""
    portrait, square, landscape = [], [], []
    for p in sorted(Path(p) for p in glob.glob(str(templates_dir) + "/**/*.png", recursive=True)):
        if any(x in p.name.lower() for x in EXCLUDE_NAMES):
            continue
        try:
            with Image.open(p) as img:
                r = img.width / img.height
        except Exception:
            continue
        if   r < 0.80:         portrait.append(p)
        elif r > 1.20:         landscape.append(p)
        elif 0.88 < r < 1.12:  square.append(p)

    def rank_ipad(p):
        n = p.name.lower()
        for i, kw in enumerate(["price_list","invoice","record","intake","form","assessment","schedule","checklist"]):
            if kw in n: return i
        return 99

    def rank_card(p):
        n = p.name.lower()
        for i, kw in enumerate(["business_card","appointment","loyalty","referral","thank"]):
            if kw in n: return i
        return 99

    portrait.sort(key=rank_ipad)
    landscape.sort(key=rank_card)

    ipad  = portrait[0]   if portrait   else (landscape[0] if landscape else None)
    phone = square[0]     if square     else None
    cards = landscape[:3] if landscape  else portrait[:3]

    return ipad, phone, cards


# ── Ideogram ──────────────────────────────────────────────────────────────────

def generate_background(niche: str, skip: bool) -> Image.Image:
    cache = Path(f"/tmp/hero_bg_{niche}.png")
    if skip and cache.exists():
        print(f"  [BG] Loading cached background ({cache})")
        return Image.open(cache).convert("RGB")
    print("  [BG] Calling Ideogram...", end=" ", flush=True)
    prompt_entry = NICHE_PROMPTS.get(niche, NICHE_PROMPTS["generic"])
    if isinstance(prompt_entry, tuple):
        prompt, negative_prompt = prompt_entry
    else:
        prompt, negative_prompt = prompt_entry, "text, watermark"
    payload_dict = {"prompt": prompt, "negative_prompt": negative_prompt,
                    "magic_prompt": "OFF", "resolution": "1024x1024",
                    "rendering_speed": "QUALITY", "num_images": 1}
    payload = json.dumps(payload_dict).encode()
    req = urllib.request.Request(IDEOGRAM_URL, data=payload, method="POST")
    req.add_header("Api-Key", os.environ["IDEOGRAM_API_KEY"])
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=120) as r:
        url = json.loads(r.read())["data"][0]["url"]
    with urllib.request.urlopen(url, timeout=60) as r:
        img = Image.open(io.BytesIO(r.read())).convert("RGB")
    img.save(str(cache))   # cache for --skip-ideogram on next run
    print(f"OK ({img.size[0]}×{img.size[1]}) — cached to {cache}", flush=True)
    return img


# ── Spaces + Etsy ─────────────────────────────────────────────────────────────

def upload_to_spaces(local_path: Path, spaces_key: str) -> str:
    s3 = boto3.client("s3", endpoint_url="https://lon1.digitaloceanspaces.com",
                      aws_access_key_id=os.environ["DO_SPACES_KEY"],
                      aws_secret_access_key=os.environ["DO_SPACES_SECRET"])
    s3.upload_file(str(local_path), "purpleocaz-assets", spaces_key,
                   ExtraArgs={"ACL": "public-read", "ContentType": "image/png"})
    url = f"https://purpleocaz-assets.lon1.digitaloceanspaces.com/{spaces_key}"
    assert urllib.request.urlopen(url).status == 200, f"Spaces verify failed: {url}"
    print(f"  [Spaces] {url}", flush=True)
    return url


def replace_rank1(listing_id: int, img_path: Path):
    at = json.loads((PROJECT / "workflows/etsy_analytics/etsy_tokens.json").read_text())["access_token"]
    hdrs = {"x-api-key": API_KEY, "Authorization": f"Bearer {at}"}
    imgs = json.loads(urllib.request.urlopen(
        urllib.request.Request(f"{ETSY_BASE}/listings/{listing_id}/images", headers=hdrs)
    ).read())["results"]
    rank1 = next((i for i in imgs if i["rank"] == 1), None)
    if rank1:
        req = urllib.request.Request(
            f"{ETSY_BASE}/shops/{SHOP_ID}/listings/{listing_id}/images/{rank1['listing_image_id']}",
            headers=hdrs, method="DELETE")
        urllib.request.urlopen(req).read()
        print(f"  [Etsy] Deleted old rank 1 (id {rank1['listing_image_id']})", flush=True)
    boundary = uuid.uuid4().hex
    img_bytes = img_path.read_bytes()
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"rank\"\r\n\r\n1\r\n"
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; "
            f"filename=\"{img_path.name}\"\r\nContent-Type: image/png\r\n\r\n").encode() + \
           img_bytes + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(f"{ETSY_BASE}/shops/{SHOP_ID}/listings/{listing_id}/images",
                                  data=body, method="POST")
    req.add_header("x-api-key", API_KEY)
    req.add_header("Authorization", f"Bearer {at}")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    result = json.loads(urllib.request.urlopen(req).read())
    print(f"  [Etsy] New rank 1 → image_id {result['listing_image_id']}", flush=True)


# ── Main compositor ───────────────────────────────────────────────────────────

# Where each device/card sits on the 3000×3000 canvas.
# Tune here without changing compositing logic.
LAYOUT = {
    "ipad_center":  (790,  960),   # iPad  centre (x, y)
    "ipad_rot":     -6,            # degrees
    "phone_center": (2280, 820),   # Phone centre (x, y)
    "phone_rot":    10,            # degrees
    # Card quads: TL, TR, BR, BL in canvas coords — paint left→right (back→front)
    "card_quads": [
        [(480, 2000), (1060, 1978), (1068, 2238), (482, 2258)],   # left
        [(960, 2100), (1560, 2082), (1565, 2345), (962, 2362)],   # centre
        [(1560, 2000), (2150, 2018), (2156, 2278), (1562, 2258)], # right
    ],
}


def build_hero(niche: str, templates_dir: Path, output: Path,
               skip_ideogram: bool = False,
               accent: tuple = (13, 92, 99),
               price: str = "£39.99") -> Path:

    print(f"\n{'='*60}")
    print(f"HERO V3 — {niche}")
    print(f"{'='*60}")

    # ── Layer 1: Background ──────────────────────────────────────────────────
    bg = generate_background(niche, skip_ideogram)
    w, h = bg.size
    side = min(w, h)
    bg = bg.crop(((w-side)//2, (h-side)//2, (w+side)//2, (h+side)//2))
    bg = bg.resize((CANVAS, CANVAS), Image.LANCZOS)
    canvas = bg.convert("RGBA")

    # ── Pick templates ───────────────────────────────────────────────────────
    ipad_path, phone_path, card_paths = pick_templates(templates_dir)
    print(f"\n  Templates selected:")
    print(f"    iPad  : {ipad_path.name if ipad_path else 'none'}")
    print(f"    Phone : {phone_path.name if phone_path else 'none'}")
    print(f"    Cards : {[p.name for p in card_paths]}")

    # ── Layer 2: iPad device ─────────────────────────────────────────────────
    if ipad_path:
        print("\n  [iPad] Building frame...", flush=True)
        ipad_frame = draw_ipad(Image.open(ipad_path), fw=800, fh=1050)
        ipad_img   = drop_shadow(ipad_frame, offset=(14,18), blur=28, opacity=170)
        ipad_rot   = ipad_img.rotate(LAYOUT["ipad_rot"], expand=True, resample=Image.BICUBIC)
        cx, cy     = LAYOUT["ipad_center"]
        canvas.paste(ipad_rot, (cx - ipad_rot.width//2, cy - ipad_rot.height//2), ipad_rot)
        print(f"    Pasted (centre {cx},{cy}, rot {LAYOUT['ipad_rot']}°)", flush=True)

    # ── Layer 3: Phone device ────────────────────────────────────────────────
    if phone_path:
        print("\n  [Phone] Building frame...", flush=True)
        phone_frame = draw_phone(Image.open(phone_path), fw=400, fh=820)
        phone_img   = drop_shadow(phone_frame, offset=(10,14), blur=22, opacity=155)
        phone_rot   = phone_img.rotate(LAYOUT["phone_rot"], expand=True, resample=Image.BICUBIC)
        cx, cy      = LAYOUT["phone_center"]
        canvas.paste(phone_rot, (cx - phone_rot.width//2, cy - phone_rot.height//2), phone_rot)
        print(f"    Pasted (centre {cx},{cy}, rot {LAYOUT['phone_rot']}°)", flush=True)

    # ── Layer 4: Perspective cards ───────────────────────────────────────────
    if card_paths:
        print("\n  [Cards] Perspective transforms...", flush=True)
        quads = LAYOUT["card_quads"]
        for i, card_path in enumerate(card_paths[:len(quads)]):
            quad = quads[i]
            card = Image.open(card_path).convert("RGBA")
            # Resize to ≈580px wide preserving aspect ratio
            target_w = 580
            card = card.resize((target_w, int(card.height * target_w / card.width)), Image.LANCZOS)
            warped = warp_card(card, quad)
            shadow = card_contact_shadow(warped, offset=(18,26), blur=24, opacity=130)
            canvas.paste(shadow, (0,0), shadow)
            canvas.paste(warped,  (0,0), warped)
            print(f"    Card {i+1}: {card_path.name}", flush=True)

    # ── Layer 5: Gradient + solid banner ────────────────────────────────────
    draw = ImageDraw.Draw(canvas)
    banner_h  = 210
    gradient_h = 280
    banner_y   = CANVAS - banner_h
    grad_y     = banner_y - gradient_h

    # Gradient (transparent → dark, easing in)
    for row in range(gradient_h):
        a = int(185 * (row / gradient_h) ** 1.5)
        draw.rectangle([0, grad_y+row, CANVAS, grad_y+row+1], fill=(0,0,0,a))

    # Solid banner
    draw.rectangle([0, banner_y, CANVAS, CANVAS], fill=accent+(255,))
    # Gold rule at top of banner
    draw.rectangle([0, banner_y, CANVAS, banner_y+7], fill=GOLD+(255,))

    # ── Layer 6: Text ────────────────────────────────────────────────────────
    count = sum(
        1 for p in (Path(p) for p in glob.glob(str(templates_dir) + "/**/*.png", recursive=True))
        if not any(x in p.name.lower() for x in EXCLUDE_NAMES)
    )
    niche_label = niche.replace("_", " ").title()
    title    = f"{count} Professional Canva Templates"
    subtitle = f"{niche_label}  •  Editable in Canva Free  •  Instant Download"

    title_f   = f(88, bold=True)
    sub_f     = f(48, bold=False)
    price_f   = f(72, bold=True)

    # Title — centred
    tb = draw.textbbox((0,0), title, font=title_f)
    tw, th = tb[2]-tb[0], tb[3]-tb[1]
    tx = (CANVAS - tw) // 2
    ty = banner_y + 26
    draw.text((tx, ty), title, fill=(255,255,255,255), font=title_f)

    # Subtitle — centred below title
    sb = draw.textbbox((0,0), subtitle, font=sub_f)
    sw = sb[2]-sb[0]
    draw.text(((CANVAS-sw)//2, ty+th+12), subtitle, fill=GOLD+(255,), font=sub_f)

    # Price badge — right-aligned, vertically centred in banner
    pb  = draw.textbbox((0,0), price, font=price_f)
    pw, ph = pb[2]-pb[0], pb[3]-pb[1]
    pad = 22
    bx  = CANVAS - pw - pad*2 - 50
    by  = banner_y + (banner_h - ph) // 2 - pad//2
    draw.rounded_rectangle([bx-pad, by-pad//2, bx+pw+pad, by+ph+pad//2],
                            radius=16, fill=(255,255,255,45))
    draw.text((bx, by), price, fill=(255,255,255,255), font=price_f)

    # ── Save ─────────────────────────────────────────────────────────────────
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(str(output), "PNG", optimize=True)
    print(f"\n  Saved → {output}", flush=True)
    return output


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Hero pipeline v3")
    ap.add_argument("--niche",          required=True)
    ap.add_argument("--templates-dir",  required=True, type=Path)
    ap.add_argument("--output",         required=True, type=Path)
    ap.add_argument("--listing-id",     type=int, default=None)
    ap.add_argument("--skip-ideogram",  action="store_true",
                    help="Reuse cached /tmp/hero_bg_{niche}.png if present")
    ap.add_argument("--accent",         default="13,92,99",
                    help="Banner RGB e.g. '13,92,99'")
    ap.add_argument("--price",          default="£39.99")
    args = ap.parse_args()

    accent = tuple(int(x) for x in args.accent.split(","))

    hero_path = build_hero(
        niche=args.niche,
        templates_dir=args.templates_dir,
        output=args.output,
        skip_ideogram=args.skip_ideogram,
        accent=accent,
        price=args.price,
    )

    # Upload to Spaces
    spaces_key = f"thumbnails/heroes/{args.niche}-hero-v3.png"
    url = upload_to_spaces(hero_path, spaces_key)
    print(f"\n{'='*60}")
    print(f"SPACES URL (review before replacing on Etsy):")
    print(f"  {url}")
    print(f"{'='*60}")

    if args.listing_id:
        input(f"\nPress Enter to replace rank 1 on listing #{args.listing_id}, or Ctrl-C to cancel...")
        replace_rank1(args.listing_id, hero_path)
        # Verify
        at = json.loads((PROJECT / "workflows/etsy_analytics/etsy_tokens.json").read_text())["access_token"]
        hdrs = {"x-api-key": API_KEY, "Authorization": f"Bearer {at}"}
        check = json.loads(urllib.request.urlopen(
            urllib.request.Request(f"{ETSY_BASE}/listings/{args.listing_id}/images", headers=hdrs)
        ).read())
        print(f"  GET images → count: {check['count']}")
        r1 = next((i for i in check["results"] if i["rank"] == 1), None)
        print(f"  Rank 1 confirmed: image_id {r1['listing_image_id']}" if r1 else "  WARN: rank 1 not found")
    else:
        print("\n  No --listing-id supplied. Review the Spaces URL above, then run with --listing-id to push to Etsy.")

    print("\n  DONE.")


if __name__ == "__main__":
    main()
