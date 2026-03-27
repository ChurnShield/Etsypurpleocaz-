---
name: etsy-forms-bundle
description: "End-to-end workflow for building and publishing a tattoo client forms
              bundle on Etsy: PDF generation, hero thumbnail compositing, listing
              images, Etsy API publishing, and delivery PDF with Canva template link."
user-invocable: false
requires:
  - rules/etsy.md
  - rules/canva.md
  - rules/infra.md
  - skill:purpleocaz-pipeline
---

# Etsy Forms Bundle — Publishing Workflow

Tattoo Studio Client Forms Bundle — forms-specific build and publish reference.
All Etsy API rules, Canva rules, and credentials are in `.claude/rules/`. This skill
covers only the forms-specific content.

---

## 1. Forms Build (reportlab PDFs)

**Script:** `scripts/generate_tattoo_forms.py`
**Output dir:** `outputs/tattoo-forms/`
**Page size:** A4, single page per form

### Colour Palette (forms-specific — see rules/canva.md for card palette)

| Colour | Hex | Usage |
|--------|-----|-------|
| Oxblood | `#8B1A1A` | Headers, section titles, table headers, accent bars |
| Gold | `#C9A96E` | Dividers, table borders, footer text, studio name |
| Cream | `#F5F0E8` | Page backgrounds |
| Charcoal | `#1A1A1A` | Body text |
| White | `#FFFFFF` | Text on dark backgrounds, table header text |
| Light Gray | `#F5F5F5` | Alternating table row background |

### The 8 Forms

| # | Filename | Title |
|---|----------|-------|
| 1 | `01_Client_Consent_Form.pdf` | Client Consent Form |
| 2 | `02_Client_Intake_Form.pdf` | Client Intake Form |
| 3 | `03_Aftercare_Instructions.pdf` | Aftercare Instructions |
| 4 | `04_Invoice.pdf` | Invoice |
| 5 | `05_Session_Tracker.pdf` | Session Tracker |
| 6 | `06_Photo_Release.pdf` | Photo Release Form |
| 7 | `07_Cancellation_Policy.pdf` | Cancellation & Deposit Policy |
| 8 | `08_Design_Request_Form.pdf` | Flash Sheet / Design Request Form |

### Typography

| Style | Font | Size | Colour |
|-------|------|------|--------|
| FormTitle | Helvetica-Bold | 20pt | Oxblood |
| StudioName | Helvetica | 9pt | Gold |
| SectionHead | Helvetica-Bold | 12pt | Oxblood |
| Body | Helvetica | 10pt | Charcoal |
| Footer | Helvetica | 7pt | Gold |

### Layout Conventions

- **Page header**: Studio name in gold + form title in oxblood + gold divider
- **Fields**: Bold label + underscore line (`_` × 60), or two-column via `field2()`
- **Checkboxes**: Unicode `□` (U+25A1) prefix
- **Tables**: Oxblood header row, gold grid lines, alternating white/light-gray rows
- **Signature block**: Client Signature + Date two-column
- **Margins**: 18mm all sides, bottom 14mm

---

## 2. Hero Thumbnail (Ideogram + Pillow Fan Composite)

**Script:** `scripts/composite_forms_hero.py`

### Pipeline
1. Generate flatlay background via Ideogram (marble/dark surface with props)
2. Render all 8 PDF first pages to PNG via PyMuPDF (`fitz`)
3. Fan-composite forms onto background with Pillow
4. Add banner with title text
5. Upload to DO Spaces + Etsy as rank 1 image

### Parameters (v8 — proven)

| Parameter | Value |
|-----------|-------|
| Canvas size | 3000×3000 px |
| Background crop | `y=350` downward (removes distracting top props) |
| Form render DPI | 200 |
| Form width | 715 px |
| Fan spread width | 1200 px total horizontal spread |
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
- 8 forms spread evenly across 1200 px, centred on canvas
- Each form at unique x-position and rotation angle
- Forms composited back-to-front (form 1 at bottom, form 8 on top)
- Drop shadow added per form before compositing

---

## 3. Listing Images (Pillow 2000×2000)

**Script:** `scripts/rebuild_rank_images.py`

| Rank | Image | Source |
|------|-------|--------|
| 1 | Hero fan composite | `composite_forms_hero.py` |
| 2 | What's Inside (8-form grid) | `build_rank2()` — 2-col 4-row grid |
| 3 | Single form close-up | Exported form PNG from Spaces |
| 4 | Edit in Minutes / 3 Steps | `build_rank4()` — numbered circles |
| 5 | Made for Tattoo Studios | `build_rank5()` — form preview + annotations |
| 6 | Canva Basics | `DAFx_dsWpTA` page 3 |
| 7 | Please Note | `DAFx_dsWpTA` page 5 |

All images: 2000×2000 px, RGB, PNG. Consistent header bar: oxblood, cream text, gold subtitle.

---

## 4. Delivery PDF

The buyer receives a single PDF containing:
- Title: "Tattoo Studio Client Forms Bundle — Your Downloads"
- Canva template link (`/d/{shortcode}` only — see rules/canva.md)
- Instructions to copy to their own Canva account
- List of all 8 forms with descriptions
- How to Use steps
- Licence notice

**Master Canva design:** `DAHEhDX7tBE` — folder `FAHEfG4nx8Q` (Tattoo-Client-Forms)

---

## 5. Listing Spec

| Field | Value |
|-------|-------|
| Price | **£4.99** (forms bundle — not the standard £2.99) |
| taxonomy_id | `2078` (NOTE: forms bundle uses 2078, not 1874) |
| Delivery file | `Tattoo_Studio_Client_Forms_Bundle_Delivery.pdf` |

All other fields follow standard spec in `rules/etsy.md`.

**Published listing:** `4475537159` — https://www.etsy.com/listing/4475537159/
