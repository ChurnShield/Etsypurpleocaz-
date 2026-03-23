# Wins

Successful patterns captured automatically after each significant task.
Most recent first. Read this to repeat what works.

---

### 2026-03-23 12:31 — Tattoo Price List Canva template

**Pattern:** Built A4 portrait price list PDF with 3 pricing boxes, Unsplash photo, serif title. Imported into Canva as DAHExFlw-yg, moved to Tattoo Masters. Delivery shortlink: /d/PQFnv85iHnoc_gv. Registered in design_registry.json.

---

### 2026-03-23 12:11 — Tattoo Gift Certificate Canva template

**Pattern:** Imported approved PDF into Canva via import-design-from-url. Design DAHEw2AXYFw in Tattoo Masters folder. Delivery shortlink: /d/YgKBSHN1dZ_U8qf. PDF hosted on Spaces. Registered in design_registry.json.

---

### 2026-03-23 10:11 — swap_card_images tool

**Pattern:** Built swap-card-images.ts in purpleocaz-canva-mcp. Two-step flow: REST API uploads image as Canva asset, MCP tools do the editing transaction. Successfully tested update_fill on DAHD07F9MsY circular frame element PBwdJPdRSxNJvVSz-LBdTn8WTgTDmwTJt. Token auto-refresh on 401 works. Cancelled test transaction to preserve master.

---

### 2026-03-23 09:42 — Tattoo Gift Certificate PDF

**Pattern:** Unsplash photo fetch + reportlab PDF generation pipeline works end-to-end. Full-bleed photo background with dark overlay, gold border, white minimal typography, 4 form fields. Cache-first fetch_niche_photo.py avoids repeat API calls.

---

### 2026-03-23 08:03 — Starter bundle hero price update

**Pattern:** Regenerated all 5 starter bundle hero thumbnails with £9.99 (down from £19.99). Used Pillow to match existing bold minimal dark design. Uploaded to Etsy, deleted old R1 images, verified all 5 listings show 3 images with correct rank order. All PASS.

---

### 2026-03-23 06:46 — Price update to GBP 9.99 on all 5 starter bundles

**Pattern:** Used PUT /listings/{id}/inventory endpoint — the only way to update price on existing listings. PATCH price is silently ignored on both draft and active listings. All 5 GET-verified at 9.99.

---

### 2026-03-23 06:35 — 4 niche starter bundles at GBP 19.99 each

**Pattern:** Barbershop #4476249863, Nail Tech #4476259024, Lash Tech #4476259070, Hair Salon #4476249947. All at GBP 19.99 with bold minimal hero (huge price as focal point), delivery PDF with /d/ shortlinks, forms ZIP. Published via single Python script — 4 listings created, uploaded, activated, verified in one run. Factory pattern fully proven across 5 niches at 2 price tiers (4.99 forms + 19.99 starter).

---

### 2026-03-23 06:15 — Tattoo Studio Starter Bundle at GBP 19.99

**Pattern:** First premium bundle. Combined 8 client forms + business card templates (dark/light) + appointment card templates (dark/light) into single ZIP with branded delivery PDF containing /d/ shortlinks. Listing #4476255084 at GBP 19.99 — 4x the individual forms price. Performance data shows top performer is Tattoo Studio Branding Kit at 24.95 with 1,973 views — this bundle targets the same premium buyer. Market data confirms price ladder gap: most tattoo bundles under 10, premium 20+ range is open.

---

### 2026-03-23 06:09 — Deleted 2 dead listings (939d + 817d, 0 views)

**Pattern:** DELETE endpoint returns 204, GET confirms 'not found'. Listings 1538873834 (Nail Tech Appt Card, Aug 2023) and 1629878924 (Valentine Flower Shop, Dec 2023) removed. Both had 0 views, 0 sales, 0 favs after 2+ years. Frees up listing slots and cleans shop metrics.

---

### 2026-03-22 22:25 — Hair Salon Client Forms Bundle — fourth niche

**Pattern:** 8 forms with hair salon terminology (colour patch test, hair history, colour formula record in appointment tracker, hair consultation form). Listing #4476124434 live at GBP 4.99. 2,956 competitors. All 5 researched niches now have live listings.

---

### 2026-03-22 22:25 — Lash Tech Client Forms Bundle — third niche

**Pattern:** 8 forms with lash-specific terminology (eye & skin check, patch test record, lash style request with curl/length options). Listing #4476113851 live at GBP 4.99. 1,705 competitors.

---

### 2026-03-22 22:03 — Nail Tech Client Forms Bundle — second niche expansion

**Pattern:** Factory pattern proven: barbershop → nail tech took one pass. All 8 forms restyled with nail-specific terminology (nail & skin check, nail shape preferences, gel/acrylic aftercare, nail design request). Listing #4476116442 live at GBP 4.99 with 3 images + ZIP. 1,526 competitors vs 212 barbershop — moderate competition, forms bundles still under-represented.

---

### 2026-03-22 21:52 — Barbershop Client Forms Bundle — first niche expansion

**Pattern:** Restyled all 8 tattoo forms for barbershop (scalp & skin check, style request, appointment tracker). Generated hero 3000x3000. Published listing #4476104249 at GBP 4.99 with 3 images + ZIP. Only 212 competitors in this niche vs 16k tattoo. Cross-niche factory pattern works: same form structure, different terminology and branding. Total time from market data to live listing: single session.

---

### 2026-03-22 21:42 — Market research — 5 niche bundle keywords

**Pattern:** Etsy public listings search needs OAuth token, not just API key (403 without it). Token refresh required mid-session. Pulled 100 listings across 5 niches. Averages skewed by whole-shop listings — always use median for price analysis.

---

### 2026-03-22 21:15 — Square 3000x3000 hero on both forms listings

**Pattern:** Regenerated at 3000x3000 with larger PDF pages filling the square canvas. Both #4475861685 and #4476074218 swapped and GET-verified with all 3 ranks intact (R1 hero, R2 Canva Basics, R3 Please Note).

---

### 2026-03-22 21:03 — 8-page hero thumbnail on both forms listings

**Pattern:** Pillow 3000x2250, two rows of 4 fanned pages showing all 8 form titles. Dark bg, gold borders/accents, badge pills, branded footer. Swapped on #4475861685 (1 image) and #4476074218 (3 images, ranks 1-2-3 preserved). Upload-first-delete-old pattern clean on both.

---

### 2026-03-22 20:55 — Dark flat-lay hero on both forms bundle listings

**Pattern:** Pillow-generated 3000x2250 dark hero (#1A1A1A bg, gold accents, 4 fanned white PDF pages with gold borders, badge pills). Uploaded to both #4475861685 (v1, 1 image) and #4476074218 (v2, 3 images) as rank 1 using upload-first-then-delete pattern. Both GET-verified. Parallel uploads worked — no token expiry mid-flight.

---

### 2026-03-22 20:46 — Hero swap on v1 listing #4475861685

**Pattern:** Reused cached DAFqlkXJ1jg page 1 export from previous task. Upload-first-then-delete pattern worked cleanly. Old 1024x1024 replaced with 3000x2250.

---

### 2026-03-22 20:44 — Canva hero swap on listing #4476074218

**Pattern:** Exported DAFqlkXJ1jg page 1 at width=3000 (3000x2250, 4:3 ratio). Cannot delete last image on active listing — upload replacement first, then delete old. Correct sequence: upload new hero R1, delete old hero, upload R2, upload R3.

---

### 2026-03-22 20:34 — V2 hero thumbnail swap on listing #4476074218

**Pattern:** Generated 3000x3000 hero with Pillow matching v2 PDF palette (#F5F5F5/#111111/#888888). Deleted old hero, uploaded new as rank 1. Had to delete and re-upload rank 2+3 images because deleting rank 1 caused rank collision. Lesson: when replacing rank 1, delete all images first then re-upload in order to avoid rank conflicts.

---

### 2026-03-22 20:27 — Tattoo Forms Bundle v2 published to Etsy

**Pattern:** Full SOP checklist run before publish. Listing #4476074218 live at GBP 4.99 with 3 images (hero, Canva Basics, Please Note) and ZIP of 8 PDFs. Token refreshed on 401 before starting. Used shop-scoped PATCH endpoint for activation (non-scoped returned 404). GET-verified all uploads. Distinct tags with zero overlap against existing forms listing #4475861685.

---

### 2026-03-22 20:18 — Learning loop system

**Pattern:** Shell hooks that auto-append to WINS.md and LESSONS.md — keeps institutional memory growing without manual effort

---
