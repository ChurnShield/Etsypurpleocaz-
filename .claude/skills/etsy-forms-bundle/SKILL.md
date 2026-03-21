---
name: etsy-forms-bundle
description: "End-to-end workflow for building and publishing a tattoo client forms
              bundle on Etsy: PDF generation, hero thumbnail compositing, listing
              images, Etsy API publishing, and delivery PDF with Canva template link."
user-invocable: false
---

# Etsy Forms Bundle — Publishing Workflow

Complete reference for the Tattoo Studio Client Forms Bundle listing.
Covers form PDF creation, hero image compositing, listing image generation,
Etsy API publishing, and delivery PDF assembly.

---

## 1. FORMS BUILD (reportlab PDFs)

### Colour Palette
| Colour | Hex | Usage |
|--------|-----|-------|
| Oxblood / Dark Red | `#8B1A1A` | Headers, accent bars, numbered circles |
| Cream | `#F5F0E8` | Page backgrounds |
| Gold | `#C9A96E` | Dividers, subtitles, decorative elements |
| Charcoal | `#1A1A1A` | Body text |
| White | `#FFFFFF` | Text on dark backgrounds |

### File Naming Convention
```
01_Client_Consent_Form.pdf
02_Client_Intake_Form.pdf
03_Aftercare_Instructions.pdf
04_Invoice.pdf
05_Session_Tracker.pdf
06_Photo_Release.pdf
07_Cancellation_Policy.pdf
08_Design_Request_Form.pdf
```

### Location
- Individual PDFs: `/root/NEW-AI-PROJECT/outputs/tattoo-forms/`
- Bundle ZIP: `/root/NEW-AI-PROJECT/outputs/tattoo-forms/Tattoo_Studio_Client_Forms_Bundle.zip`

### The 8 Forms
| # | Form | Content |
|---|------|---------|
| 1 | Client Consent Form | Health declaration, risk acknowledgement, consent signatures |
| 2 | Client Intake Form | Personal details, tattoo details, skin sensitivity, referral source |
| 3 | Aftercare Instructions | Healing guide day 1 through week 6, warning signs |
| 4 | Invoice | Itemised billing, service table, totals, payment methods |
| 5 | Session Tracker | Multi-session project log, payment summary, running balance |
| 6 | Photo & Video Release | Photography/media consent, opt-in/out terms |
| 7 | Cancellation & Deposit Policy | Deposit terms, cancellation table, rescheduling, late arrival |
| 8 | Design Request Form | Custom tattoo brief, style checkboxes, reference image areas |

---

## 2. HERO THUMBNAIL (Ideogram + Pillow fan composite)

### Pipeline
1. Generate flatlay background via Ideogram (marble/dark surface with props)
2. Render all 8 PDF first pages to PNG via PyMuPDF (`fitz`)
3. Fan-composite forms onto background with Pillow
4. Add banner with title text
5. Upload to DO Spaces + Etsy as rank 1 image

### Script
`scripts/composite_forms_hero.py`

### Parameters That Worked (v8)
| Parameter | Value |
|-----------|-------|
| Canvas size | 3000x3000 px |
| Background crop | `y=350` downward (removes cushion/top props) |
| Form render DPI | 200 |
| Form width | 715 px |
| Fan spread width | 1200 px (total horizontal spread) |
| Fan centre offset | `cx = canvas/2 + 150` (slightly right) |
| Rotation angles | `-21, -15, -9, -3, +3, +9, +15, +21` degrees |
| Drop shadow offset | 8 px |
| Drop shadow blur | 20 px |
| Drop shadow opacity | 40% (`int(255 * 0.4)`) |
| Banner ratio | 25% of canvas height (bottom) |
| Banner colour | `#8B1A1A` (oxblood) |
| Title font size | 90 (DejaVuSans-Bold) |
| Subtitle font size | 45 (DejaVuSans) |

### Fan Layout Logic
- 8 forms spread evenly across `FAN_SPREAD_WIDTH` (1200px), centred on canvas
- Each form at a unique x-position and rotation angle
- Forms composited back-to-front (form 1 at bottom, form 8 on top)
- Drop shadow added per form before compositing onto canvas

---

## 3. LISTING IMAGES (Pillow 2000x2000)

### Scripts
| Script | Purpose |
|--------|---------|
| `scripts/rebuild_rank_images.py` | Builds ranks 2, 4, 5, 6, 7 listing images |

### Image Ranks
| Rank | Image | Source |
|------|-------|--------|
| 1 | Hero fan composite | `scripts/composite_forms_hero.py` |
| 2 | What's Inside Your Bundle | `build_rank2()` — 2-column, 4-row grid of all 8 forms |
| 3 | Single form close-up | Exported form PNG from DO Spaces |
| 4 | Edit in Minutes / 3 Steps | `build_rank4()` — numbered circles with arrows |
| 5 | Made for Tattoo Studios | `build_rank5()` — form preview with annotation arrows |
| 6 | Everything Included | `build_rank6()` — checklist with gold checkboxes |
| 7 | Please Note / Digital | `build_rank7()` — disclaimer bullets |

### Rebuild Command
```bash
# Ensure Spaces credentials are available
export $(grep -v '^#' /root/NEW-AI-PROJECT/purpleocaz-canva-mcp/.env | xargs)
python3 /root/NEW-AI-PROJECT/scripts/rebuild_rank_images.py
```

### Design Rules
- All images: 2000x2000 px, RGB, PNG
- Font stack: DejaVuSans-Bold, DejaVuSerif-Bold (system fonts)
- Consistent header bar: oxblood `#8B1A1A`, cream text, gold subtitle
- Consistent footer: thin 18px oxblood bar at bottom
- Gold separator lines between sections (`width=1200-1600`)
- "PURPLEOCAZ" brand text in gold near bottom

---

## 4. ETSY LISTING (API structure)

### Listing Creation
```
POST /v3/application/shops/34071205/listings
Content-Type: application/x-www-form-urlencoded

title=...
description=...
price=4.99              # price in pounds (API handles conversion)
quantity=999
who_made=i_did
when_made=2020_2026
taxonomy_id=2078         # NOTE: forms bundle uses 2078, not 1874
type=download
is_supply=false
tags=tattoo consent form,tattoo studio forms,...   # comma-separated, max 13, each max 20 chars
```

### Price
- Forms bundle: **£4.99** (= `499` in API `price.amount` with `divisor: 100`)
- Standard single product: £2.99
- Price must be set at creation — PATCH on drafts is silently ignored

### Auth Headers
```
x-api-key: {ETSY_API_KEYSTRING}:{ETSY_SHARED_SECRET}
Authorization: Bearer {access_token}
```

### Token Location
`workflows/etsy_analytics/etsy_tokens.json`

Token refresh:
```
POST https://api.etsy.com/v3/public/oauth/token
grant_type=refresh_token
client_id={ETSY_API_KEYSTRING}
refresh_token={refresh_token}
```

### Image Upload Order
Upload images sequentially, rank 1 first:
```
POST /v3/application/shops/34071205/listings/{id}/images
Content-Type: multipart/form-data
Fields: image (file), rank (integer 1-7)
```

### Tags Validation
- Max 13 tags per listing
- Each tag max 20 characters
- No duplicate tags (API returns 400)
- Split across: core product, format/modifier, buyer intent, adjacent niche

---

## 5. DELIVERY PDF (fpdf2 / reportlab)

### What the Buyer Gets
A single delivery PDF containing:
1. Title: "Tattoo Studio Client Forms Bundle — Your Downloads"
2. Canva view link (template link) for buyer to edit forms
3. Instructions to copy to their own Canva account
4. List of all 8 forms included with descriptions
5. How to Use steps
6. Usage rights / licence notice

### Canva Link Format
**CRITICAL:** Use `/d/{shortcode}` view links ONLY.
- Get via Canva MCP `get-design` → `urls.view_url`
- Never use `/design/{id}/edit` (gives buyer write access to master)
- Never use `/design/{id}/view` (exposes master design URL)

### Master Canva Design
| Field | Value |
|-------|-------|
| Design ID | `DAHEhDX7tBE` |
| Canva folder | `Tattoo-Client-Forms` (`FAHEfG4nx8Q`) |

### Upload
```
POST /v3/application/shops/34071205/listings/{id}/files
Content-Type: multipart/form-data
Fields: file (PDF), name (filename string)
```

### Verification (NEVER skip)
```
GET /v3/application/shops/34071205/listings/{id}/files
```
Confirm: `count >= 1`, filename matches, `size_bytes > 0`.

---

## 6. KEY LESSONS

### DO Spaces Credentials
- Credentials are in `purpleocaz-canva-mcp/.env`, **NOT** `NEW-AI-PROJECT/.env`
- Keys: `DO_SPACES_KEY`, `DO_SPACES_SECRET`, `DO_SPACES_ENDPOINT`, `DO_SPACES_REGION`, `DO_SPACES_BUCKET`
- Load with: `load_dotenv('/root/NEW-AI-PROJECT/purpleocaz-canva-mcp/.env')`

### ACL public-read
- **Every** `s3.put_object()` call MUST include `ACL='public-read'`
- Without it, uploaded images return 403 when accessed via CDN URL
- This caused repeated failures across v5-v8 of the hero image

### One Transaction per Canva Operation
- Canva editing: one transaction per logical change, commit before starting next
- Multi-page designs: one transaction per page side (front, then back)
- Cascading failures occur if you batch multiple operations into one transaction

### Etsy API Gotchas
- Always PATCH, never PUT (PUT returns 404)
- Verify every upload with a GET call before reporting success
- Token auto-refresh on 401 during upload loops
- Tags: validate length (<= 20 chars) and uniqueness before submission

### Hero Image Pipeline
- Programmatic shadows (Pillow/Sharp) always look fake on form documents
- Fan composite with per-form drop shadow + real flatlay background looks professional
- Background crop at `y=350` was key to removing distracting props from Ideogram output

---

## 7. LISTING DETAILS (for reference)

### Draft Listing (2026-03-21)
| Field | Value |
|-------|-------|
| Listing ID | `4475537159` |
| URL | `https://www.etsy.com/listing/4475537159/` |
| Title | Tattoo Studio Client Forms Bundle \| 8 Professional PDF Templates \| Editable in Canva \| Consent Form Aftercare Invoice Session Tracker |
| Price | £4.99 |
| State | draft |
| Delivery file | `Tattoo_Studio_Client_Forms_Bundle_Delivery.pdf` |

### Etsy Shop
| Field | Value |
|-------|-------|
| Shop ID | `34071205` |
| Shop name | PurpleOcaz |
