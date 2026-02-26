# PurpleOcaz — Master AI Session Prompt

> **Paste this at the start of every new Claude session working on this project.**
> Last updated: 2026-02-21

---

## 1. WHO I AM

I'm **Andy Nosworthy**, owner of **PurpleOcaz** — a UK-based Etsy shop (Shop ID: `34071205`) selling **937+ digital Canva template listings** in GBP. I'm a Star Seller with 920+ sales. My strongest niche is **tattoo** (79 listings generating 16.4% of revenue from 8.4% of inventory — 2x efficiency vs other niches).

**My expectation:** I want hands-off automation. I don't want to touch anything manually but I'm happy to approve actions you take for me. I expect expert-level execution, not experiments. If you're unsure, research first, then present options.

---

## 2. THE PROJECT

**Project root:** `C:\Users\andyn\OneDrive\Desktop\NEW AI PROJECT`
**Python:** `/c/Python314/python`
**GitHub:** `https://github.com/ChurnShield/Etsypurpleocaz` (private)

This is a **3-Layer Dual Learning Agentic AI System** (Orchestrator + SmallBrain + BigBrain) that automates my Etsy business. Read `CLAUDE.md` at the project root for the full architecture rules — they are mandatory.

### Completed Workflows
| Workflow | Path | What It Does |
|----------|------|-------------|
| **Etsy Analytics Dashboard** | `workflows/etsy_analytics/` | Fetches all 937 listings + shop stats + per-listing sales via OAuth → Google Sheets (3 tabs) |
| **SEO Tag Optimizer** | `workflows/seo_tag_optimizer/` | Scans listings for duplicate/weak tags, generates better keywords via Claude |
| **Tattoo Trend Monitor** | `workflows/tattoo_trend_monitor/` | Monitors tattoo trends from multiple sources, suggests product ideas → Sheets |
| **Auto Listing Creator** | `workflows/auto_listing_creator/` | Loads trend opportunities → generates listing content → creates product images → publishes Etsy drafts + Sheets |

### Key Config & Credentials
- **Etsy API keys:** `.env` (`ETSY_API_KEYSTRING`, `ETSY_SHARED_SECRET`, `ETSY_SHOP_ID`)
- **Etsy x-api-key header format:** `keystring:shared_secret` (BOTH parts required)
- **Etsy OAuth tokens:** `workflows/etsy_analytics/etsy_tokens.json` (scopes: `shops_r transactions_r listings_r listings_w listings_d`)
- **Canva OAuth tokens:** `workflows/auto_listing_creator/canva_tokens.json`
- **Google Sheets service account:** `google-credentials.json`
- **Spreadsheet ID:** `1pRzSABpw5hDQXId7MPfMH0IgSnnKYWqpyyHYI9t_AoE`

---

## 3. ETSY API — CRITICAL RULES (LEARNED THE HARD WAY)

| Rule | Detail |
|------|--------|
| `x-api-key` header | Must be `keystring:shared_secret` — NOT just the keystring |
| `createDraftListing` | Uses `application/x-www-form-urlencoded`, NOT `application/json` |
| Image upload | `multipart/form-data` with boundary, `POST /shops/{id}/listings/{id}/images` |
| Digital file upload | `multipart/form-data`, `POST /shops/{id}/listings/{id}/files` |
| Tags | Max 13 tags, each max 20 chars — truncate with `t[:20]` |
| Taxonomy ID | **1874** (Paper & Party Supplies > Paper > Stationery > Templates) |
| Listing type | `type=download`, `who_made=i_did`, `when_made=2020_2025`, `is_supply=false` |
| Delete listing | Needs `listings_d` scope |
| OAuth refresh | Tokens expire in 3600s, auto-refresh via refresh_token |

---

## 4. MY STORE'S VISUAL BRAND & PRODUCT FORMAT

### This is the most critical section. Every automated listing MUST match this standard.

### 4a. Product Delivery Format
- **Every listing delivers 1 PDF file** as the digital download
- The PDF contains **clickable links to Canva templates** (the customer opens them in Canva to edit)
- The PDF also includes a **"Your Template Links"** branded page with the PurpleOcaz logo, thank-you message, and instructional video links
- Many products include a **print layout sheet** (US Letter/A4) so customers can print 3-up
- Many products include a bonus **"Canva Basics" e-book**
- Templates are available in **both A4 and US Letter sizes**

### 4b. Listing Image Sequence (5 images per listing)
Every listing follows this EXACT 5-image sequence:

| Image # | Content | Key Elements |
|---------|---------|-------------|
| **1 - Hero** | Product showcase on beige linen background | Device mockups (iMac + iPad + iPhone) showing the template. Printed templates fanned around devices. Real lifestyle props (plants, coffee). Product title in bold serif on colored band at bottom. Black circular "EDIT IN CANVA" badge. Tagline underneath. |
| **2 - What's Included** | Bundle contents checklist | Same mockup scene at top (smaller). "EDITABLE IN CANVA" dark pennant badge. "A4 & LETTER SIZES" oval badge. Checkmark list of everything included. |
| **3 - Canva Basics Bonus** | Free e-book promotion | Fanned e-book pages on beige background with pens, plants. "EDIT IN CANVA" badge. Text: "Includes a free e-book to help you with Canva editing basics!" |
| **4 - Print at Home** | Printing instructions | Overhead shot of printer printing the template. Coffee cup, leaves. "PRINT AT HOME" circular badge. Canva print settings dialog shown. Text about PDF/JPG download with bleed + crop marks. |
| **5 - Please Note** | Digital download disclaimer | Beige linen background. Script font "Please note" with heart. PurpleOcaz family cartoon logo (circular). Three bullets: digital product, no physical shipping, print yourself. |

### 4c. Visual Style Details
- **Primary brand colour:** `#6B2189` (deep plum purple) — used in accent bands, badges, highlights
- **Background:** Beige/linen texture (#E6E5E1 area) — universal across all listing photos
- **Typography:** Playfair Display (serif) for headlines, Montserrat (sans-serif) for body, script/calligraphy for decorative headings
- **Mockup devices:** iMac (center), iPad (right side), iPhone (far right) — showing the actual template
- **Props:** Real succulents, eucalyptus leaves, coffee cups, wicker trays, pink crystals, marble pens, stationery
- **Badges:** Black circular "EDIT IN CANVA", "PRINT AT HOME" circular, dark pennant "EDITABLE IN CANVA", oval "A4 & LETTER SIZES"
- **Bottom band:** Bold product title on the listing's accent colour, with tagline below

### 4d. Template Design Style (The Actual Product)
The templates themselves (what customers edit in Canva) use:
- Real stock photography relevant to the niche (tattoo photos, model shots, studio images)
- Professional layout with the brand's accent colour as header/divider bands
- Placeholder fields: "[YOUR BUSINESS NAME]", "To:", "From:", "Amount:", "Expires:"
- Contact footer: email, phone, address, website with matching icons
- Clean, printable design that looks professional when printed at home

---

## 5. THE UNSOLVED CHALLENGE — AUTOMATED PRODUCT CREATION

### What Works Now
The pipeline successfully: discovers trends → generates listing content with Claude → creates Etsy drafts → uploads images → saves to Google Sheets.

### What Doesn't Work
**The product images and digital files are not production quality.** Specifically:

1. **Listing images** generated via HTML+Playwright look like generic graphic design posters, NOT like professional product photography with device mockups and lifestyle props
2. **No digital download file** is being created or uploaded — the customer would receive nothing after purchase
3. **All products look identical** — same layout, different text. Real products each have unique visual identity

### What's Been Tried & Failed
| Approach | Result |
|----------|--------|
| Canva API: Create designs programmatically | API cannot add content/elements to designs |
| Canva API: Clone/duplicate designs | "asset_id must belong to an image asset" |
| Canva API: Brand template autofill | Enterprise-only feature |
| Canva API: Design content manipulation | Endpoint doesn't exist |
| Claude generating full HTML pages | Unreliable — blank renders, doesn't fill canvas |
| HTML template + Claude JSON content | Renders consistently but looks nothing like real store listings |

### What's Installed & Available
- **Playwright** + Chromium (headless browser, HTML→PNG rendering)
- **Pillow** (image manipulation, compositing)
- **Canva API** (can search designs, export existing designs as PNG/PDF, create blank designs)
- **Etsy API** (full CRUD on listings, image upload, digital file upload)
- **Claude API** (content generation, can generate HTML/CSS)

### The Real Options (Prioritized)
1. **Canva search + export existing designs** — match new products to similar existing Canva designs, export them as images/PDFs. This gives REAL product quality but may not have perfect matches.
2. **Hybrid: Reuse boilerplate images 2-5 from existing exports** + generate unique hero image with product-specific content. Images 3/4/5 ("Canva Basics", "Print at Home", "Please Note") are IDENTICAL across all products.
3. **Playwright + Pillow compositing** — render unique template designs via HTML, then composite them into mockup frames with beige backgrounds, device bezels, and badge overlays using Pillow.
4. **Browser automation** — use Playwright to interact with Canva's web UI, duplicate an existing template, modify text/images.

### What Needs to Happen for a "Perfect" Listing
- [ ] Unique product template design (specific to the product type)
- [ ] 5 listing images matching the store's exact visual sequence
- [ ] 1 PDF digital download file (with Canva template links or printable content)
- [ ] PDF uploaded to Etsy as a digital file (not just images)
- [ ] The listing must be indistinguishable from existing handcrafted listings

---

## 6. CODING CONVENTIONS (FROM CLAUDE.md)

- **Always** use `ExecutionLogger` with `try/finally` + `flush()`
- **Always** extend `BaseTool` / `BaseValidator` for new tools/validators
- **Always** import config from `config.py`, never hardcode
- **Always** use `SQLiteClient` query builder, never raw sqlite3
- **Never** modify base classes without permission
- **Never** add dependencies without approval (Playwright + Pillow already approved)
- See full `CLAUDE.md` at project root for complete rules

---

## 7. PRICING & PRODUCT STRUCTURE

| Product Type | Price Range (GBP) | Typical Bundle |
|-------------|-------------------|----------------|
| Single template (gift cert) | £4.50-6.00 | 1 template, A4+Letter |
| Template bundle (3-5 designs) | £8.00-12.99 | Multiple style variants |
| Mega branding kit | £19.95-24.95 | 15-20+ templates + website + e-book |

---

## 8. HOW I WANT YOU TO WORK

1. **Research before building** — look at my existing code, existing listings, and existing exports BEFORE writing new code
2. **Test with 1 listing first** — get one perfect before scaling to 16
3. **Show me the output** — render images and show them to me for approval before publishing
4. **Match the store aesthetic** — if it doesn't look like my existing listings, it's not ready
5. **Include digital files** — every listing needs an actual downloadable PDF
6. **Clean up after failures** — delete bad drafts, don't leave mess on my Etsy shop
7. **Commit and push** — save all work to GitHub after successful changes
8. **Update memory** — save key learnings to the Claude memory directory so future sessions benefit

---

## 9. CURRENT STATE & NEXT STEPS

**Pipeline status:** Functional end-to-end but product quality not production-ready.

**Immediate priority:** Get ONE perfect listing that matches the store's visual standard, including:
- Professional listing images (matching the 5-image sequence)
- A downloadable PDF digital file
- Uploaded to Etsy as a draft for my review

**After that:** Scale to the full pipeline with consistent quality.
