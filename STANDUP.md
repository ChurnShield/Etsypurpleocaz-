# Daily Standup

Most recent first.

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
