# Daily Standup

Most recent first.

---

## 2026-03-16

### What we shipped
- **SOUL.md** — co-founder principles and mission file, wired into CLAUDE.md as first-read directive
- **Etsy OAuth headless flow** — `etsy_oauth.py` rewritten for remote/Terminus use (paste-redirect-URL pattern). Tokens verified live: shop PurpleOcaz, 937 listings, 931 sales
- **Full pipeline end-to-end run** — `run_single_listing.py` all 4 phases, 100/100 quality score. Etsy draft #4472750162 created with 2 images + digital PDF at £12.99
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
1. **Appointment card** — design in Canva, export, register in design_registry.json. This is product #2 of 7 for the Tattoo Studio Bundle
2. **Validate ThumbnailPipelineTool live** — run against real Canva API to confirm editing session endpoints work end-to-end
3. **Wire ThumbnailPipelineTool into run_single_listing.py** — if registry has a matching design, use it for hero image instead of HTML/Playwright fallback
