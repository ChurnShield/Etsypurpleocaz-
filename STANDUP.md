# Daily Standup

Most recent first.

---

## 2026-03-27

### Dog Grooming Mega Bundle — DRAFT LISTING CREATED #4478726787

- **Draft listing #4478726787** — https://www.etsy.com/listing/4478726787
- 33+ Canva templates across 6 categories (branding, marketing, forms, operations, social, print)
- 7 listing images uploaded (ranks 1–7), all verified via GET
- Delivery PDF attached: DG_Mega_Bundle_DELIVERY.pdf (18.8 KB)
- Price: £39.99 | Tags: 13 valid | State: draft (pending activation)
- verify_listing.py: 8/9 PASSED (price check is false positive — mega bundle at £39.99, not £2.99)
- Bug fixed: publish script now uses `listing_file_id` not `file_id` for file verification print

**Next for this listing:**
1. Activate: PATCH state=active
2. Update STANDUP once live

### Car Detailing Mega Bundle — UPGRADED to 53 templates, £39.99

- **Listing #4476909005 updated** — https://www.etsy.com/listing/4476909005
- Added 3 new templates: Appointment Card Dark, Appointment Card Light, Welcome Sign (A4)
- Built with Pillow — uploaded to DO Spaces (`templates/car-detail-appointment-cards/`, `templates/car-detail-welcome-sign/`)
- Delivery PDF regenerated: 53 templates, 8 sections, 11 pages with all Canva /d/ shortlinks
- Price: £34.99 → £39.99 (via PUT inventory endpoint with float price)
- Title updated: "Car Detailing Business Bundle | 53 Canva Templates | ..."
- Description updated to reflect all 8 categories
- verify_listing.py: 9/9 PASSED | state=active | 7 images | 1 file attached

**New Spaces URLs:**
- Dark card: https://purpleocaz-assets.lon1.digitaloceanspaces.com/templates/car-detail-appointment-cards/CD_Appointment_Card_Dark.png
- Light card: https://purpleocaz-assets.lon1.digitaloceanspaces.com/templates/car-detail-appointment-cards/CD_Appointment_Card_Light.png
- Welcome sign: https://purpleocaz-assets.lon1.digitaloceanspaces.com/templates/car-detail-welcome-sign/CD_Welcome_Sign.png

**Lesson learned:** Inventory price update requires PUT /listings/{id}/inventory with `"price": 39.99` (float), not PATCH /listings or PATCH /shops/{id}/listings.

### Tattoo Business Card Listing #2 — LIVE

- **Draft #4478348991 published** — https://www.etsy.com/listing/4478348991/tattoo-studio-business-card-template
- Design: DAHD6ICQCWU (3-page Etsy listing image set, 3000×2250 landscape)
- Images: 7/7 (3 from DAHD6ICQCWU + Canva Basics + Please Note from Spaces + 2 generic from existing listing #4472977919)
- Delivery PDF: dark=`/d/e21A6ZQJ3XcCIq-`, light=`/d/vyaBAtIupW1g7zH`
- Price: £2.99 | Tags: 13 valid | verify_listing.py: 9/9 PASSED | State: active

### Tomorrow's priority
1. Tier 3 branding kits — nail tech, lash tech, hair salon (tattoo + barbershop already done)
2. Tier 4 mega bundles — combine all tiers per niche at £39.99
3. Upgrade listing images — swap /view links for /d/ shortlinks when Canva Share menu available

---

## 2026-03-25

### Barbershop Mega Bundle — in progress

**TASK 1 — Canva token auto-refresh ✅**
- `scripts/refresh_canva_token.py` — reads refresh token, POSTs to Canva OAuth, updates .env + canva_tokens.json. Tested: `Token refreshed. Expires: 14400s`
- `/etc/cron.d/canva-refresh` — runs every 3h
- `hooks/session_start.sh` — calls refresh at every session start
- LESSONS.md: CC auth — `ANTHROPIC_API_KEY=sk-ant-... claude --strict-mcp-config`

**TASK 2 — Barbershop Mega Bundle (25+ templates)**

| Category | Templates | Status |
|----------|-----------|--------|
| Print Essentials (CR80 + A6) | Business card F+B, Appointment, Thank You, Refer A Friend | ✅ Built (prior session) |
| Instagram Posts 1080×1080 | 12 posts: brand, services, book now, offer, testimonial, tip, before/after, meet the barber, hours, loyalty, referral, seasonal | ✅ Built + Spaces verified |
| Instagram Stories 1080×1920 | 6 stories: book now, availability, flash deal, tip, shoutout, weekend special | ✅ Built + Spaces verified |
| Utility Cards | Google review card, tip guide, price list card, aftercare card | ✅ Built + Spaces verified |

**Running total: 25 templates** (4 print + 12 IG posts + 6 stories + 4 utility) — all on Spaces

**Barbershop Mega Bundle LIVE ✓**
- Listing #4477586457 — https://www.etsy.com/listing/4477586457
- Price: £14.99 | Images: 7/7 | Files: 1 | State: active
- Delivery PDF: 27 links with File → Make a copy instruction
- 27 designs in Canva folder FAHE94J3odE, all registered in design_registry.json

### Tomorrow's priority
1. **Tier 3 branding kits** — nail tech, lash tech, hair salon (tattoo + barbershop already done)
2. **Tier 4 mega bundles** — combine all tiers per niche at £39.99
3. **Upgrade listing images** — swap /view links for /d/ shortlinks when Canva Share menu available

---

## 2026-03-24

### Car Detailing Niche — LIVE
- **8 listings published** with approved hero images, 7 images each, delivery PDFs attached
  - Forms Bundle (8 forms) £4.99 — #4476619120 — https://www.etsy.com/listing/4476619120
  - Visual Bundle (gift cert + price list + loyalty card) £4.99 — #4476619282 — https://www.etsy.com/listing/4476619282
  - Flyer Pack (4 flyers) £4.99 — #4476619330 — https://www.etsy.com/listing/4476619330
  - Business Bundle (all 15 templates) £9.99 — #4476610441 — https://www.etsy.com/listing/4476610441
  - Branding Kit (6 templates) £6.99 — #4476893828 — https://www.etsy.com/listing/4476893828
  - Email Templates (6 templates) £5.99 — #4476891933 — https://www.etsy.com/listing/4476891933
  - Job Forms (3 templates) £4.99 — #4476913230 — https://www.etsy.com/listing/4476913230
  - **MEGA BUNDLE (50+ templates) £34.99 — #4476909005 — https://www.etsy.com/listing/4476909005**
- **Mega Bundle**: 10-page delivery PDF covering all 7 categories with 50 Canva /d/ shortlinks
- **15 Canva templates imported** across Car-Detail-Branding, Car-Detail-Email, and Car-Detail-Job-Forms folders
- **All verified**: 7/7 images per listing, state=active, delivery PDFs confirmed

### Product ladder (car detail) — COMPLETE
| Tier | Product | Price | Status |
|------|---------|-------|--------|
| 1 | Client Forms Bundle (8 PDFs) | £4.99 | LIVE #4476619120 |
| 1 | Visual Bundle (3 templates) | £4.99 | LIVE #4476619282 |
| 1 | Flyer Pack (4 flyers) | £4.99 | LIVE #4476619330 |
| 2 | Business Bundle (all 15) | £9.99 | LIVE #4476610441 |
| 3 | Branding Kit (6 templates) | £6.99 | LIVE #4476893828 |
| 3 | Email Templates (6 templates) | £5.99 | LIVE #4476891933 |
| 3 | Job Forms (3 templates) | £4.99 | LIVE #4476913230 |
| **4** | **MEGA BUNDLE (50+ templates)** | **£34.99** | **LIVE #4476909005** |

### Tomorrow's priority
1. **Deduplicate ideas_backlog.md** — consolidate repeated Mac Mini / agent entries
2. **Tier 3 branding kits** — build for barbershop, nail tech, lash tech, hair salon (tattoo already exists at £24.95)
3. **Tier 4 mega bundles** — combine all tiers per niche at £39.99

---

## 2026-03-23 (overnight)

### Car Detailing Niche — Full Build
- **15 products built**: 8 client forms, gift certificate, price list, loyalty card, 4 marketing flyers (promo, seasonal, mobile, walk-in)
- **All 15 PDFs uploaded to DO Spaces** under templates/car-detail-*/
- **All 15 imported to Canva** in CAR DETAIL folder (FAFN0i-UFTI) with /d/ shortlinks
- **Design registry updated** — car_detail section with all design IDs, shortlinks, Spaces URLs
- **4 Etsy listings created (draft)**:
  - Forms Bundle (8 forms) £4.99 — #4476619120
  - Visual Bundle (gift cert + price list + loyalty card) £4.99 — #4476619282
  - Flyer Pack (4 flyers) £4.99 — #4476619330
  - Starter Bundle (all 15) £9.99 — #4476610441
- **4 hero images** (forms grid, visual fan, flyer fan, starter collage) — 3000x3000 PNG
- **4 delivery PDFs** with Canva shortlinks per bundle
- **Scripts created**: car_detail_pipeline.py (previews/heroes/uploads), car_detail_etsy.py (listings)

---

## 2026-03-23

### What we shipped today
- **6 forms bundles published at £4.99 each** — tattoo x2 (#4475861685, #4476074218), barbershop (#4476104249), nail tech (#4476116442), lash tech (#4476113851), hair salon (#4476124434). Each has 8 niche-specific PDFs, 3000x3000 hero, 3 listing images, ZIP delivery.
- **5 starter bundles published at £9.99 each** — tattoo (#4476255084), barbershop (#4476249863), nail tech (#4476259024), lash tech (#4476259070), hair salon (#4476249947). Each combines 8 forms + business card + appointment card Canva templates with branded delivery PDF.
- **Price correction £19.99 → £9.99** on all 5 starter bundles via PUT /listings/{id}/inventory endpoint. PATCH price is silently ignored on all listing states.
- **2 dead listings deleted** — #1538873834 (939 days, 0 views), #1629878924 (817 days, 0 views). Confirmed gone via GET.
- **Market research** — 5 niche keywords (tattoo, barbershop, nail tech, lash tech, hair salon). Barbershop widest open at 212 listings.
- **Performance pipeline tested** — weekly_performance_check.py + digest_performance.py both run clean. PERFORMANCE_INSIGHTS.md generated.
- **Learning loop system** — hooks/on_task_complete.sh and hooks/on_task_fail.sh auto-append to WINS.md and LESSONS.md. 16 wins logged this session.
- **Skills created** — skills/design.md (design rules), skills/sop.md (publishing checklist)
- **UFW hardened** — removed plain ALLOW on port 22, LIMIT rule only

### Performance snapshot
- 945 active listings (943 after 2 deletions)
- £6,678.75 total revenue, 886 sales, 70,542 views
- Top performer: Tattoo Studio Branding Kit — 1,973 views, 102 favs, £24.95
- 209 underperformers (<10 views) — 22% of shop

### New lessons
- Price PATCH silently ignored on ALL listing states — must use PUT /listings/{id}/inventory
- Hero thumbnails must be 3000x3000 square — Etsy crops to square in search
- Cannot delete last image on active listing — upload replacement first
- Canva-first for heroes — check existing assets before generating with Pillow
- Hero must show ALL bundle items, not a subset
- After image swap, verify all 3 ranks exist (R1, R2, R3) not just R1

### Product ladder (per niche)
| Tier | Product | Price | Status |
|------|---------|-------|--------|
| 1 | Client Forms Bundle (8 PDFs) | £4.99 | LIVE — all 5 niches |
| 2 | Starter Bundle (forms + cards) | £9.99 | LIVE — all 5 niches |
| 3 | Branding Kit (full template set) | £24.95 | EXISTS for tattoo only |
| 4 | Mega Bundle (all products) | £39.99 | TO BUILD |

### What's blocked
- ideas_backlog.md has duplicate entries from YouTube digests — needs deduplication
- 6 generic listing images (How It Works, What's Included) still need manual Canva redesign

### Tomorrow's priority
1. **Deduplicate ideas_backlog.md** — consolidate repeated Mac Mini / agent entries
2. **Tier 3 branding kits** — build for barbershop, nail tech, lash tech, hair salon (tattoo already exists at £24.95)
3. **Tier 4 mega bundles** — combine all tiers per niche at £39.99
4. **Update STANDUP.md → Sunday strategy session** — repurpose bundle ladder planning, Tier 1+2 done, focus on Tier 3/4
5. **Underperformer audit** — review the 209 listings with <10 views, batch update tags/titles or delete

---

## 2026-03-18

### What we shipped today
- **Bundle #1508908772 PDF upgraded** — deleted old 2023 PDF, uploaded new 2-page delivery PDF with 13 clickable Canva `/d/` template links across all 7 product types (business card dark/light, appointment card dark/light, loyalty card purple/black, flyer purple/black, price list purple/black, gift certificate purple, scan-to-pay purple/black)
- **Full inventory audit** — pulled all 16 active tattoo listings via Etsy API, confirmed all 7 bundle product types already exist. Nothing needs building from scratch.
- **Market research** — tattoo price list templates on Etsy. PurpleOcaz already has 4 variants live + dominates search results. Competitor (FlourishTemplatesCo) sells 25-page bloated guide at higher price.
- **LESSONS.md updated** — `generate-design` cannot produce custom branded listing images (ignores colour instructions, defaults to blue). Must build manually in Canva.
- **verify_listing.py --bundle flag** — skips £2.99 price check for bundle listings with different price expectations
- **Both new listings confirmed** — #4472977919 (business card) and #4473444461 (appointment card) each have 7 images, PDFs attached, all tags valid

### What's blocked
- 6 generic listing images (How It Works, What's Included, etc.) need manual Canva redesign — AI generation can't produce on-brand results

### Tomorrow's priority
1. **Refresh bundle listing images** — swap in new dark/gold designs alongside originals to modernise the hero images
2. **Build 4 card mockup images for business card listing** (dark front, dark back, light front, light back)
3. **A4 print layout mockup image** — cards arranged in grid with cut lines
4. **Google Drive PDF folder** — auto-save delivery PDFs

---

## 2026-03-16

### What we shipped
- **SOUL.md** — co-founder principles and mission file, wired into CLAUDE.md as first-read directive
- **Etsy OAuth headless flow** — `etsy_oauth.py` rewritten for remote/Terminus use (paste-redirect-URL pattern). Tokens verified live: shop PurpleOcaz, 937 listings, 931 sales
- **Full pipeline end-to-end run** — `run_single_listing.py` all 4 phases, 100/100 quality score. Etsy draft #4472750162 created with 2 images + digital PDF at £2.99
- **Proactive Etsy token refresh** — built in `publish_listings_tool.py`, 16/16 tests passing
- **Hero thumbnail card swap** — DAFx_dsWpTA page 1: dark card (DAHD07F9MsY) and light card (DAHD15IcxRs) swapped via Canva MCP editing API. One transaction per operation, both committed
- **ThumbnailPipelineTool** — autonomous thumbnail generator reading from design registry, Canva REST editing API, Pillow shadow compositing (ETSY_CARD_SHADOW_PRESET), Spaces upload. 20 new tests, 47/47 total passing
- **Design registry** (`config/design_registry.json`) — tattoo/business_card entry with confirmed-unlocked element IDs, card variants, text elements, shadow preset
- **Terminus mobile SSH** — password auth configured, UFW port 22 open
- **CHANGELOG.md v1.0.0** — Canva MCP pipeline work packaged as release. Comparison links fixed to ChurnShield/Etsypurpleocaz-

### What's blocked
- Canva editing REST API endpoint paths need validation — current ThumbnailPipelineTool uses assumed paths from MCP tool behaviour, not confirmed against Canva REST docs
- Canva access token expires hourly — auto-refresh works but no proactive refresh before expiry

### Tomorrow's priority
1. **A4 print layout mockup** — Build a standard A4 print layout mockup image showing business cards arranged in a grid ready for cutting. Layout: 10 cards per A4 (2 columns x 5 rows) with dotted cut lines. Dark card version on left column, light card version on right column. Small footer text: "Print at home or take to your local print shop". PurpleOcaz logo bottom right. Save as a reusable generic Canva template that works for all card niches — just swap the card images. Register in design_registry.json as `standard_print_layout_mockup`.
2. **Appointment card** — design in Canva, export, register in design_registry.json. This is product #2 of 7 for the Tattoo Studio Bundle
3. **Validate ThumbnailPipelineTool live** — run against real Canva API to confirm editing session endpoints work end-to-end
4. **Wire ThumbnailPipelineTool into run_single_listing.py** — if registry has a matching design, use it for hero image instead of HTML/Playwright fallback
5. **Agentic AI research session** — explore agentic AI frameworks (Manus, Perplexity deep research, Twitter/X build-in-public accounts) for sub-agent architecture ideas that reduce Andy's manual orchestration. Goal: identify what we can adopt or adapt for PurpleOcaz pipeline. Add findings to ideas_backlog.md.
6. **Verification agent step** — design and implement automatic GET verification after every upload/API call. Based on Manus architecture. No task marked done without confirmation.
7. **TODO.md per session** — CC creates task list at session start, ticks off as it goes, audit trail at end.
8. **Evaluate Manus for weekly niche research** — automated Monday morning runs, drops findings to Google Sheet.
9. **Long-term vision doc** — write up the overnight pipeline goal: Andy approves niche on phone → pipeline runs overnight → draft listing ready for review next morning. Zero manual steps.
10. **Google Drive PDF auto-save** — Save every delivery PDF to Google Drive folder PurpleOcaz/Delivery PDFs automatically as part of the listing pipeline — so Andy can access any PDF instantly when a buyer asks. Build google_drive_pdf_save step into the pipeline after PDF generation.
11. **Canva folder organisation** — Canva folders now organised: PurpleOcaz/Tattoo-Masters, PurpleOcaz/Listing-Templates-Generic, PurpleOcaz/Thumbnails-Hero. Folder IDs saved to design_registry.json: root=FAHENpMANrQ, tattoo-masters=FAHENuO2Vkc, listing-templates=FAHENvJko1A, thumbnails-hero=FAHENqKrgvk. Future designs must be moved to correct folder immediately after creation.
