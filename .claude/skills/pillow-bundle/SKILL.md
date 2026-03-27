---
name: pillow-bundle
description: "Pillow (PIL) template bundle build pattern — design system, PNG generators,
              Spaces upload, delivery PDF, and Etsy file attach. Use when building or
              adding templates to any niche bundle (barbershop, car detail, tattoo, etc.)."
user-invocable: false
requires:
  - rules/infra.md
  - rules/pipeline.md
  - rules/etsy.md
---

# Pillow Bundle Build Pattern

Every niche bundle follows the same structure. Document it once here; don't reinvent it per niche.

---

## PREFERRED METHOD — Use the Factory (3rd niche onwards)

> **RULE (CLAUDE.md):** After 2 niches built with per-niche scripts, ALWAYS use the factory for new niches.

```bash
# Build a new niche from a JSON config — full pipeline in one command
python3 scripts/niche_template_factory.py configs/niches/my_niche.json

# Flags
--skip-etsy    # Build PNGs + PDF only (no Etsy API calls)
--only-pdf     # Rebuild delivery PDF only (templates already on Spaces)
```

**To add a new niche:**
1. Copy `configs/niches/sample_niche.json` to `configs/niches/{slug}.json`
2. Edit: palette, brand placeholders, icon type, Etsy copy, templates list
3. Run the factory — it handles rendering, Spaces upload, delivery PDF, Etsy listing creation + activation
4. Run `python scripts/verify_listing.py {listing_id} --bundle`

**Config reference:** `configs/niches/sample_niche.json` — fully documented, shows every template type and every row spec type for `form_a4`.

**Template types supported by factory:**
`business_card`, `appointment_card`, `loyalty_card`, `referral_card`, `thank_you_card`,
`gift_certificate`, `welcome_sign`, `opening_hours_sign`, `flyer_a4`, `price_list`,
`form_a4`, `invoice`, `booking_confirmation`, `social_1080`, `certificate`, `income_tracker`, `expenses_tracker`

**Row spec types for `form_a4`:**
`section_header`, `field_single`, `field_pair`, `field_triple`, `checkbox_group`, `table`, `text_block`, `spacer`

---

## Legacy Method — Per-Niche Scripts (first 2 niches only)

The pattern below documents how the first niches were built (barbershop, car detail, pet bundles).
It remains valid for **patching or extending existing niches**. Do NOT use it to start a new niche.

---

## The Pattern

```
1. Design system file      → defines palette, fonts, shared helpers
2. N generator scripts     → each builds one template category as PNG(s)
3. Spaces upload           → every PNG gets ACL='public-read'
4. Delivery PDF            → reportlab, one page per section, /d/ links for Canva items
5. Etsy file attach        → DELETE old file, POST new file (multipart, name field required)
6. verify_listing.py       → confirm file attached, image count, tags, price
```

---

## 1. Design System File

**Purpose:** Single source of truth for the niche palette, font paths, and shared drawing helpers. Every generator script imports from it.

**Pattern:** `scripts/{niche}_design_system.py` (or inline at top of first generator)

**Barbershop example:** `scripts/barbershop_design_system.py`

```python
# Palette — define as module-level tuples
BG      = (10, 10, 10)       # #0A0A0A
PANEL   = (26, 26, 26)       # #1A1A1A
BOX     = (42, 42, 42)       # #2A2A2A
GOLD    = (201, 169, 110)    # #C9A96E
WHITE   = (255, 255, 255)
GREY    = (136, 136, 136)    # #888888

# Fonts — always DejaVu (available on Ubuntu without install)
FONT_BOLD    = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SERIF   = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"

def font(size, bold=False, italic=False):
    path = FONT_SERIF if italic else (FONT_BOLD if bold else FONT_REGULAR)
    return ImageFont.truetype(path, size)

def centred(draw, y, text, fill, f, canvas_w=None):
    w = canvas_w or draw.im.size[0]
    bbox = draw.textbbox((0, 0), text, font=f)
    tw = bbox[2] - bbox[0]
    draw.text(((w - tw) // 2, y), text, fill=fill, font=f)
```

**Car detail example:** Palette defined inline at top of `build_car_detail_branding_kit.py`:
```python
BG      = (13, 13, 13)        # #0D0D0D
ACCENT  = (224, 32, 32)       # #E02020
WHITE   = (255, 255, 255)
SILVER  = (192, 192, 192)
```

---

## 2. Generator Scripts

**Naming:** `scripts/build_{niche}_{category}.py`

**Each script:**
- Imports palette + helpers from design system (or defines inline)
- Creates `OUTPUT_DIR` with `mkdir(parents=True, exist_ok=True)`
- Defines one function per template (`def build_price_list()`, `def build_loyalty_card()`, etc.)
- Returns the local `Path` of the saved PNG
- Calls `upload_to_spaces(local_path, spaces_key)` at the end

**Standard canvas sizes:**
| Template type | Size (px) | Notes |
|---|---|---|
| US Letter print | 2550×3300 | 300 dpi |
| A4 print | 2480×3508 | 300 dpi |
| Business card | 1050×600 | landscape |
| Gift certificate | 2550×1800 | landscape |
| Instagram post | 1080×1080 | square |
| Pinterest pin | 1000×1500 | portrait |
| Flyer | 2550×3300 | same as US Letter |

**Barbershop example scripts:**
- `build_barbershop_visuals.py` — price list, gift cert, loyalty card
- `build_barbershop_forms.py` — client intake, consent, waiver
- `build_barbershop_flyers.py` — promo flyer, walk-in special
- `build_barbershop_instagram.py` — 9 social post PNGs
- `build_barbershop_stories.py` — Instagram story variants

**Car detail example scripts:**
- `build_car_detail_branding_kit.py` — business card, letterhead, email signature, thank-you card
- `build_car_detail_job_forms.py` — job order, inspection, invoice
- `generate_car_detail_forms.py` — client intake forms (reportlab)
- `generate_car_detail_price_list.py` — service price list
- `build_car_detail_social.py` — 20 social post PNGs

---

## 3. Spaces Upload

**Always include `ACL='public-read'`** — without it, GET returns 403.

```python
from dotenv import load_dotenv
load_dotenv('/root/NEW-AI-PROJECT/purpleocaz-canva-mcp/.env')  # Spaces creds here, NOT .env

import boto3, os

def upload_to_spaces(local_path: Path, spaces_key: str) -> str:
    s3 = boto3.client(
        's3',
        endpoint_url='https://lon1.digitaloceanspaces.com',
        aws_access_key_id=os.environ['DO_SPACES_KEY'],
        aws_secret_access_key=os.environ['DO_SPACES_SECRET'],
    )
    s3.upload_file(
        str(local_path),
        'purpleocaz-assets',
        spaces_key,
        ExtraArgs={'ACL': 'public-read', 'ContentType': 'image/png'},
    )
    url = f"https://purpleocaz-assets.lon1.digitaloceanspaces.com/{spaces_key}"
    # Verify immediately
    import urllib.request
    resp = urllib.request.urlopen(url)
    assert resp.status == 200, f"Spaces upload verification failed: {url}"
    print(f"  ↑ {spaces_key} → {url}")
    return url
```

**Key naming convention:**
- `templates/{niche}-{category}/{NICHE_TemplateName}.png`
- Example: `templates/car-detail-appointment-cards/CD_Appointment_Card_Dark.png`
- Example: `templates/barbershop-visuals/BS_Price_List.png`

---

## 4. Delivery PDF

**Library:** `reportlab` (`from reportlab.pdfgen import canvas as rl_canvas`)

**Structure:** One section per template category, clickable Canva links for any Canva-editable templates, plain Spaces download URLs for PDF/PNG-only assets.

**Canva links MUST use `/d/{shortcode}` format.** Never `/design/{id}/view` or `/design/{id}/edit`.

```python
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.pagesizes import A4

def generate_delivery_pdf(output_path: str, sections: list[dict]) -> None:
    """
    sections: list of {title, items: [{name, url, note}]}
    """
    c = rl_canvas.Canvas(output_path, pagesize=A4)
    W, H = A4
    # ... render cover page, then one page per section
    c.save()
```

**Barbershop delivery PDF:** `scripts/publish_barbershop_mega_bundle.py` (generates + uploads)
**Car detail delivery PDF:** `scripts/upgrade_car_detail_mega_bundle.py` (regenerates on upgrade)

---

## 5. Etsy File Attach

**Pattern:** DELETE the old file first, then POST the new one.

DELETE returns HTTP 204 with empty body — handle it:
```python
raw = resp.read()
return json.loads(raw) if raw.strip() else {}
```

POST multipart **must** include the `name` field before the `file` field:
```python
body.extend(f'Content-Disposition: form-data; name="name"\r\n\r\n{filename}\r\n'.encode())
body.extend(f"--{boundary}\r\n".encode())
body.extend(f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode())
```

Without the `name` field: Etsy returns `400 — A valid name must be provided`.

---

## 6. Verification

After attaching the file and all images:

```bash
python scripts/verify_listing.py {listing_id}
# For non-£2.99 bundles:
python scripts/verify_listing.py {listing_id} --bundle
```

Then manually GET the files endpoint and show the response:
```bash
curl -s "https://openapi.etsy.com/v3/application/shops/34071205/listings/{ID}/files" \
  -H "x-api-key: $(python3 -c \"import os; from dotenv import load_dotenv; load_dotenv('/root/NEW-AI-PROJECT/.env'); print(os.environ['ETSY_API_KEY'])\")"
```

---

## Adding a New Niche — Checklist

When starting a new niche bundle from scratch:

- [ ] Choose palette (3–4 colours max). Check existing niches for contrast — don't reuse same palette.
- [ ] Create `scripts/{niche}_design_system.py` or inline palette in first generator
- [ ] Decide template categories (forms, visuals, social, print, etc.)
- [ ] One generator script per category
- [ ] Create Spaces key prefix: `templates/{niche}-{category}/`
- [ ] Build delivery PDF listing all templates
- [ ] Create Etsy listing draft with correct price at creation (price is immutable on drafts via API)
- [ ] Upload all 7 listing images (star seller standard — see rules/pipeline.md)
- [ ] Attach delivery PDF
- [ ] Run verify_listing.py

---

## Gotchas

1. **Spaces creds are in `purpleocaz-canva-mcp/.env`**, not `NEW-AI-PROJECT/.env`.
2. **Price is immutable on drafts.** Set it at listing creation. Change it only via inventory endpoint (`PUT /listings/{id}/inventory` with `"price": 39.99` float) or Etsy dashboard.
3. **DejaVu fonts are always available** on the Ubuntu droplet. Don't install extra fonts.
4. **Photos from Unsplash source API are deprecated.** Cache photos to `assets/photos/{niche}/` on first fetch; load from cache on subsequent runs.
5. **`Image.alpha_composite` requires RGBA mode.** Convert with `.convert("RGBA")` before compositing.
6. **Preview grids** (composite of all templates in a 3×N grid) should be built last, after all individual templates are confirmed.
