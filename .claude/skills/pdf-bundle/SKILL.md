---
name: pdf-bundle
description: "Tattoo client forms PDF generation with reportlab — colour palette, layout
              conventions, typography, and form structure. Use when building or modifying
              the 8-form tattoo studio PDF bundle."
user-invocable: false
requires:
  - rules/infra.md
  - rules/pipeline.md
---

# PDF Bundle — Tattoo Client Forms

Reference for generating the 8-form tattoo studio client forms bundle.

---

## Overview

- **Script:** `scripts/generate_tattoo_forms.py`
- **Output dir:** `outputs/tattoo-forms/`
- **Library:** `reportlab` (Python)
- **Page size:** A4, single page per form
- **Author metadata:** "PurpleOcaz Tattoo Templates"

---

## Colour Palette

| Name | Hex | Usage |
|------|-----|-------|
| Oxblood | `#8B1A1A` | Headers, section titles, table headers, accents |
| Gold | `#C9A96E` | Dividers, table borders, footer text, studio name |
| White | `#FFFFFF` | Background, table header text |
| Light Gray | `#F5F5F5` | Alternating table row background |
| Dark Gray | `#333333` | Body text |
| Mid Gray | `#999999` | Reference image placeholders |

---

## The 8 Forms

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

---

## Layout Conventions

- **Page header:** Studio name placeholder ("YOUR STUDIO NAME" in gold) + form title (oxblood) + gold divider
- **Sections:** Bold oxblood heading + gold divider
- **Fields:** Bold label + underscore line (`_` × 60), or two-column via `field2()`
- **Checkboxes:** Unicode `□` (U+25A1) prefix
- **Tables:** Oxblood header row, gold grid lines, alternating white/light-gray rows
- **Signature block:** Client Signature + Date two-column field
- **Margins:** 18mm all sides, bottom 14mm

---

## Typography

| Style | Font | Size | Colour |
|-------|------|------|--------|
| FormTitle | Helvetica-Bold | 20pt | Oxblood |
| StudioName | Helvetica | 9pt | Gold |
| SectionHead | Helvetica-Bold | 12pt | Oxblood |
| Body | Helvetica | 10pt | Dark Gray |
| BodySmall | Helvetica | 8pt | Dark Gray |
| Footer | Helvetica | 7pt | Gold |

---

## Running the Generator

```bash
python scripts/generate_tattoo_forms.py
```

Outputs all 8 PDFs to `outputs/tattoo-forms/`. Creates a ZIP at `outputs/tattoo-forms/Tattoo_Studio_Client_Forms_Bundle.zip` if bundling is enabled.

---

## Modifying Forms

- Each form is a standalone function (`form_01_consent()` through `form_08_design_request()`).
- Shared helpers: `field()`, `field2()`, `cb()`, `cb_row()`, `gold_divider()`, `section()`, `page_header()`, `sig_block()`.
- Styles are cached via `S()` — call once per process.
- Add new forms by creating a new function and appending to the `generators` list in `main()`.
