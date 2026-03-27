# Lessons Learned

A living document updated every session. Most recent entries first.

---

### 2026-03-27 — Etsy price update: use PUT /listings/{id}/inventory with float price

**Rule:** To update the price of an active listing, use:
`PUT /listings/{listing_id}/inventory` with `Content-Type: application/json` and body:
`{"products": [{"sku": "", "property_values": [], "offerings": [{"price": 39.99, "quantity": 999, "is_enabled": true}]}]}`

**Why:** PATCH `/listings/{id}` returns 404. PATCH `/shops/{id}/listings/{id}` accepts but silently ignores the price field. The inventory endpoint with a float price value is the only way to update price via API on active listings.

**How to apply:** Whenever a listing price needs updating, go via the inventory endpoint with `"price": <float>`. Not `{"amount": 3999, "divisor": 100}` — that returns "Expected float value".

---

### 2026-03-25 — CC auth: use ANTHROPIC_API_KEY if claude.ai OAuth expired

**Rule:** If claude.ai browser OAuth session expires, launch Claude Code with:
`ANTHROPIC_API_KEY=sk-ant-... claude --strict-mcp-config`

**Why:** claude.ai OAuth tokens expire. ANTHROPIC_API_KEY env var bypasses browser auth entirely and works from any terminal session.

**How to apply:** If `claude` fails with auth errors, set the env var explicitly before launching. Keep the key handy in a secure note.

---

### 2026-03-24 — [WIN] Car detailing niche launched

4 listings live, 15 templates, delivery PDFs with /d/ shortlinks, 7 images each.

**Pipeline:** render PDFs to PNG → Spaces → PIL composite hero → Etsy upload → activate

**Key learnings from this build:**
- Etsy GET images endpoint uses `/listings/{id}/images` (no shops prefix), but POST upload and PATCH activate use `/shops/{shop_id}/listings/{id}/...`
- Listings had 0 images despite earlier session creating them — always verify image state before assuming prior work survived
- Full 7-image Star Seller standard enforced: hero + whats_inside + lifestyle + how_it_works + why_buy + canva_basics + please_note

---

### 2026-03-23 06:46 — Price PATCH silently ignored on active listings

**Rule:** PATCH price=9.99 on active listings returned 200 but price stayed at 19.99

**Why:** Etsy v3 PATCH on listings endpoint ignores price field for ALL listing states, not just drafts. LESSONS.md only documented this for drafts.

**How to apply:** Use PUT /listings/{id}/inventory endpoint with products[].offerings[].price instead. Format: JSON body, no product_id in payload, sku as empty string.

---

### 2026-03-21 — DO Spaces Credentials and ACL

**Rule:** DO Spaces credentials (`DO_SPACES_KEY`, `DO_SPACES_SECRET`) are in `purpleocaz-canva-mcp/.env`, NOT `NEW-AI-PROJECT/.env`. Always load from `purpleocaz-canva-mcp/.env` for any Spaces operation. Always include `ACL='public-read'` in every `s3.put_object()` call.

**Why:** Every Spaces upload this session (v5 through v8) required a manual `put_object_acl` fix because the ACL snippet was loading credentials from the wrong `.env` file (which had no Spaces keys), causing auth failures. The script itself was correct but manual fixes kept using the wrong path.

**How to apply:** Any Python script or one-liner that touches DO Spaces must `load_dotenv('/root/NEW-AI-PROJECT/purpleocaz-canva-mcp/.env')` and use `os.getenv('DO_SPACES_KEY')` / `os.getenv('DO_SPACES_SECRET')`. Every `s3.put_object()` must include `ACL='public-read'`. Also applies to TypeScript/Node uploads via the MCP pipeline.

---

### 2026-03-18 — generate-design Cannot Produce Custom Branded Listing Images

**Rule:** Do NOT use Canva `generate-design` for custom branded listing images (e.g. "How It Works", "What's Included", etc.). It defaults to generic blue templates regardless of colour/style instructions in the prompt.

**Why:** Attempted to redesign all 6 generic listing images (DAHETZyqPRg, DAHETWTJrnk, DAHETe4GcEQ, DAHETY_tjdM, DAHETeT3RNE, DAHETV-CqGU) with a white #FFFFFF / near-black #1A1A1A / warm gold #C9A96E colour scheme. All 24 candidates (4 per design × 6 designs) came back with Canva's default blue palette, ignoring the hex codes and "NO blue anywhere" instructions entirely.

**How to apply:** Custom branded listing images must be built manually in Canva UI or commissioned from a designer. `generate-design` is only useful as an aesthetic base for card-type designs that get fully restyled via editing transactions — it cannot produce on-brand infographics or listing pages.

---

### 2026-03-17 — Canva Links in Delivery PDFs: VIEW not EDIT

**Rule:** Always use Canva VIEW links (`/d/` shortlinks) in delivery PDFs, never edit links (`/design/.../edit`). Edit links give buyers write access to master designs — they can modify or delete the original template.

**Why:** The first appointment card PDF was generated with `/design/.../view` links which look safe but are still Canva design URLs that could expose the master. The correct format is `/d/{shortcode}` — these are buyer template links that force "Use this template" (creates a copy) and never expose the original.

**How to apply:** When generating any delivery PDF with Canva template links:
- Use format: `https://www.canva.com/d/{shortcode}`
- Never use: `https://www.canva.com/design/{designId}/view` or `/edit`
- Get the shortcode from Canva's "Share > Template link" feature
- Verify by clicking the link yourself — it should show "Use this template", not open the editor

**Fixed listings:**
- #4473444461 (appointment card): dark=`/d/Mol3iFDMHAATbQt`, light=`/d/UvTaJitKspzs1da`
- #4472977919 (business card): already correct — dark=`/d/e21A6ZQJ3XcCIq-`, light=`/d/vyaBAtIupW1g7zH`

---

### 2026-03-17 — Appointment Card Listing: End-to-End Publish

**Worked:**
- Reusing the hero thumbnail template (DAHDc0gyebE) that already had appointment card images swapped in from the design session — no edits needed, just export + post-process + upload. Previous session work carries forward cleanly.
- Generic listing pages (Canva Basics p3, Please Note p5) from DAFx_dsWpTA exported at width=3000 — reusable across all listings. Same URLs work for any product.
- Etsy PATCH `state: active` on a draft with images + files works cleanly. No additional fields required beyond the state change.
- Token auto-refresh on 401 during upload sequence — the upload loop handles expired tokens mid-flight without losing progress.
- reportlab PDF generation for delivery files is fast and reliable — clickable Canva links, professional layout, branded footer.

**Failed:**
- First publish attempt used PUT instead of PATCH — Etsy v3 API returns 404 for PUT on listings endpoint. Always use PATCH for listing updates.

**Next:**
- Build 4 individual card mockup images for the business card listing (dark front, dark back, light front, light back) — these increase dwell time and conversion.
- A4 print layout mockup showing cards arranged in a grid with cut lines.
- Start product 3/7: Tattoo Price List.

---

### 2026-03-17 — Appointment Card: generate-design + restyle approach

**Worked:**
- Using Canva `generate-design` with `business_card` type to get a professionally designed aesthetic base, then restyling text elements via `replace_text`, `format_text`, `resize_element`, and `position_element` to convert it into an appointment card with form fields. This bypasses the limitation that Canva AI can't generate appointment/booking card layouts directly.
- One transaction per page side, commit between. Front and back edited separately — prevents cascading failures.
- The light variant naturally had more text elements (7 vs 4 on back page) because Canva generated separate Phone/Email/Address label+value pairs. This allowed more granular aftercare tip mapping (one tip per element) instead of cramming multiple tips into one element.
- Requesting a highly specific aesthetic in the generate prompt (color hex codes, "botanical/floral tattoo illustration", "cream/off-white background") produces designs that match the existing brand palette closely enough to use as-is after text replacement.
- Exporting to Spaces CDN for Andy to review on phone before any editing — prevents wasted edit cycles on a rejected base design.

**Failed:**
- First batch of `generate-design` candidates all produced standard personal business cards (artist name + title) despite requesting "appointment card with form fields". The AI interprets `business_card` design type literally — it doesn't understand "appointment booking card" as a layout concept.
- Canva preview thumbnail URLs (`design.canva.ai/*`) redirect through auth-gated endpoints — `WebFetch` gets 403. Must use `start-editing-transaction` + `get-design-thumbnail` to see candidates, or save-then-inspect.
- First text replacement on the front inherited the original heading font size (large serif), causing the appointment fields to overflow the card. Always `format_text` with explicit `font_size` immediately after `replace_text` when repurposing a heading element for body content.

**Key Design IDs:**
- Dark appointment card: `DAHENCEJGjk` (black/gold/botanical) — APPROVED
- Light appointment card: `DAHENKnCBoM` (cream/charcoal/gold/botanical) — APPROVED
- Both registered in `config/design_registry.json` under `tattoo/appointment_card/dark` and `tattoo/appointment_card/light`

**The pattern for future products:**
1. `generate-design` with detailed aesthetic prompt (colors, style, illustration type)
2. Save candidate → export to Spaces → Andy reviews on phone
3. If approved, `start-editing-transaction` → `replace_text` all elements → `format_text` + `resize_element` + `position_element` to fix layout → commit
4. One transaction per page, commit between
5. Export final PNGs to Spaces, register in `design_registry.json`

**Next:**
- Build Etsy listing for the appointment card (title, description, tags, PDF with Canva template links)
- Create hero thumbnail using the DAHDc0gyebE template with appointment card images swapped in
- Product 3/7: Price list card

---

### 2026-03-16 — Etsy Listing Pipeline: Complete Learnings

**Design page sources — know which pages live where:**
- `DAHDc0gyebE` has only 1 page — the hero thumbnail. No pages 2/3 exist.
- `DAFx_dsWpTA` is the 5-page listing design containing the generic pages used across all listings:
  - Page 3: "Canva Basics" — Includes a free e-book to help you with Canva editing basics
  - Page 5: "Please Note" — Digital product disclaimer with PurpleOcaz branding
- Correct image sources for any tattoo listing:
  - Rank 1: `DAHDc0gyebE` page 1 (hero thumbnail with black banner post-processing)
  - Rank 2: `DAFx_dsWpTA` page 3 (Canva Basics)
  - Rank 3: `DAFx_dsWpTA` page 5 (Please Note)

**Approved hero thumbnail URL:** `https://purpleocaz-assets.lon1.digitaloceanspaces.com/thumbnails/tattoo_business_card_hero_APPROVED_1773687738456.png`

**Etsy API rules learned the hard way:**
- Tags have a hard 20-character maximum — always validate lengths before submitting. API returns 400 if any tag exceeds 20 chars.
- Duplicate tags are rejected — API returns 400 "You may have duplicate tags."
- Cloning/copying listings is NOT supported in Etsy v3 API — no `copy_listing` or `clone` endpoint exists.
- Price changes via PATCH are silently ignored on draft listings — must set price at creation time or change manually in dashboard.
- Digital PDF upload via `POST /shops/{id}/listings/{id}/files` is confirmed working. Verified on listing #4472977919.

**Verification rule — NEVER skip this:**
- Always verify uploads with a GET API call before reporting success. Never assume an upload worked based on the POST response alone.
- Run `GET /listings/{id}/images` and `GET /shops/{id}/listings/{id}/files` after every upload and show the raw response.
- Do not mark a task as done without API confirmation.

---

### 2026-03-16 — Hero Thumbnail: Approved Pipeline (End-to-End)

**The approved flow for tattoo/business_card hero thumbnail:**
1. Open `DAHDc0gyebE` editing transaction
2. `update_fill` front card element with dark card export asset
3. `update_fill` back card element with light card export asset
4. `replace_text` headline + subtext as needed
5. `position_element` / `resize_element` banner shape to full width (left=0, width=1587)
6. Commit transaction
7. Export at native dimensions (no width override = 1587x2245; or width=3000 for high-res = 3000x4243)
8. **Post-export**: Sharp pixel swap — all dark pixels (brightness < 180) below y=82% of image height → black #000000. This changes the crimson banner to black while preserving white text.
9. Upload to Spaces + Etsy listing as rank 1 image

**Why post-processing for the banner color?**
- Canva MCP `update_fill` on SHAPE elements returns "shape does not contain an editable fill" — only works on image/video containers
- `insert_fill` creates new image elements that always go on TOP of the z-stack, covering the text elements. No z-order control via API.
- The only reliable approach: keep the original shape (preserves z-order under text), export, then swap colors in the PNG via Sharp pixel manipulation.

**Key assets:**
- Black PNG asset `MAHEIi_EfxE` uploaded for future use if Canva adds z-order control
- Approved hero CDN: `thumbnails/tattoo_business_card_hero_APPROVED_1773687738456.png`
- Etsy draft: #4472947789

---

### 2026-03-16 — Hero Thumbnail: Shadow Approach That Works

**Worked:**
- Design `DAHDc0gyebE` is the correct base thumbnail template for tattoo/business_card. It has a flatlay background with natural shadow and depth built into the Canva design — no Pillow/Sharp shadow processing needed.
- `update_fill` on the existing card element containers swaps the card image while preserving the template's built-in shadow and rotation. Element IDs: front card `PB7y4RXXMjNRSBxN-LBzNYh3QYlcjmnDQ`, back card `PB7y4RXXMjNRSBxN-LBQPQW8s9ZqqhvZc`.
- Text elements confirmed working: headline `PB7y4RXXMjNRSBxN-LBnzshp3wwmD5XxT`, subtext `PB7y4RXXMjNRSBxN-LBL801k0tMcMCblR`.
- Export without specifying width gets native 1587x2245 dimensions — no black borders. Specifying `width: 2000` on a non-matching aspect ratio causes letterboxing.
- `position_element` successfully shifts card containers to fix cropping issues.

**Failed:**
- Pillow/Sharp shadow compositing approach: creating shadow rect → gaussian blur → composite card on top. Even with large padding (120px), high blur sigma (20-30), and varying opacity (0.6-0.95), the result looked like a hard black rectangle, not a natural shadow. Root cause: the shadow rect has sharp edges that gaussian blur softens but never makes look organic — real shadows have irregular falloff affected by the surface texture.
- Uploading pre-shadowed card PNGs via `update_fill` to Canva containers: Canva's internal crop/zoom eats the shadow padding, making it invisible. The container is sized to the card, not the card+shadow.
- Canva REST editing API (`/designs/{id}/editing_sessions`) returns 404 — this endpoint doesn't exist. Must use Canva MCP tools (`start-editing-transaction`, `perform-editing-operations`, `commit-editing-transaction`) for all design editing.
- Exporting at a width that doesn't match the design's aspect ratio adds black borders/letterboxing.

**Key Rule:** For thumbnails with natural shadows, use a Canva template that has the shadow built into the design (flatlay photo background with positioned card containers). Never try to synthesize shadows programmatically — it always looks fake. The template IS the shadow system.

**Next:**
- Register `DAHDc0gyebE` element IDs for other niches (nail, hair, beauty, spa) — clone the template and swap card designs per niche.
- Add the thumbnail template step to the automated listing pipeline: export cards → `update_fill` into `DAHDc0gyebE` → export → upload to Spaces.

---

## AI Brain Principles

- **Give Claude tools shaped to its abilities** — not the easiest to implement. A well-designed tool that the model understands beats a quick hack it struggles with.
- **Progressive disclosure** — skill files that reference other files recursively beats a bloated system prompt. Let the agent discover context layer by layer instead of front-loading everything.
- **Revisit tool design as model capabilities improve** — what helped before can become a constraint. TodoWrite kept early models on track but later made them rigid; it was replaced with Tasks.
- **Always use the right tool for the job** — Canva MCP for layout, Python for data, Claude for reasoning. Match the tool to the domain rather than forcing one tool to do everything.

---

### 2026-03-16 — ThumbnailPipelineTool & Design Registry

**Worked:**
- Design registry JSON (`config/design_registry.json`) decouples Canva design IDs from code — adding a new niche/product_type is a JSON edit, not a code change. Stores confirmed-unlocked element IDs, card variant asset IDs, shadow preset, and Spaces config in one file.
- Canva REST editing API works from Python via `urllib.request` — start session, perform operation, commit. One transaction per operation is the hard rule. Two separate element swaps on DAFx_dsWpTA page 1 confirmed working: front card `PBYdP0fP9tx4c7Hw-LBStl4Tz3Wf18JQg` and back card `PBYdP0fP9tx4c7Hw-LBYSdstM3fGX4Vqg`.
- Shadow compositing ported from TypeScript Sharp to Python Pillow: create shadow rect at opacity → paste at offset on transparent canvas → GaussianBlur → composite original on top. Identical visual result. Asymmetric padding (extra_right=80, extra_bottom=40) keeps card clear of EDIT IN CANVA badge.
- Reusing `get_valid_token()` from `canva_token_manager.py` keeps token management DRY — no duplicate refresh logic.
- Spaces upload via boto3 with creds loaded from MCP `.env` — same source as TypeScript pipeline, no duplication.

**Failed:**
- First attempt to identify card elements on DAFx_dsWpTA was by guessing from position/size — got the right elements but Andy flagged that the visual result didn't look swapped. Root cause: Canva `update_fill` replaces the image but internal crop/zoom may differ from the original. Need to verify visually after every swap, not just check the API response.
- Canva design ID `DAHDc0gyebE` referenced but not found anywhere in the codebase — likely from a session that wasn't persisted. Always register design IDs in the registry immediately after creating them.

**Next:**
- Add more niches to the registry: nail, hair, beauty, spa — each needs a base listing design with confirmed element IDs.
- Wire ThumbnailPipelineTool into `run_single_listing.py` as an optional Phase 3 enhancement — if registry has a matching design, use it for the hero image instead of HTML/Playwright.
- Test the Canva editing API endpoint paths — the session/operations/commit flow needs validation against the actual REST API (current implementation uses assumed endpoint structure from MCP tools).
- Consider adding a `clone_design` step before editing so the base design is never modified — currently edits the base directly.

---

### 2026-03-16 — Terminus Mobile SSH Access

**Worked:**
- SSH into droplet from phone: use Terminus app, password auth, root@167.99.90.58 port 22. UFW must have port 22 open - if SSH times out run: `sudo ufw allow 22` from the DO web console.

---

### 2026-03-15 — purpleocaz-canva-mcp Pipeline: Spaces, OAuth, Shadow Tools

**Worked:**
- DigitalOcean Spaces via `@aws-sdk/client-s3` with S3-compatible endpoint works perfectly. CDN base: `https://purpleocaz-assets.lon1.digitaloceanspaces.com/`. Upload with `ACL: "public-read"` for permanent public URLs.
- Canva OAuth PKCE flow on headless server: created `canva_oauth_headless.py` — shows auth URL, user authorizes in browser, pastes redirect URL back. No local callback server needed. Tokens auto-saved to both `canva_tokens.json` and MCP project `.env`.
- Canva export API: `POST /exports` with `format.width: 2100` gets full-resolution business card PNGs (2100x1200). Without explicit width, defaults to tiny 336x192.
- Canva asset upload API uses binary `application/octet-stream` with `Asset-Upload-Metadata` header containing base64-encoded name. NOT JSON body. Asset name max 50 chars.
- Sharp shadow compositing pipeline: create shadow rect → place on transparent canvas at offset → blur → composite original on top. Transparent RGBA PNG output. Works cleanly for both flat and angled variants.
- Shadow preset iteration: started at blur=8/opacity=0.35, went through blur=4/0.6, settled on blur=12/opacity=0.75/offset=15,15/padding=40 as the Canva-native match (`ETSY_CARD_SHADOW_PRESET` in `config/niches.ts`).
- Asymmetric padding (extra_right_padding=80, extra_bottom_padding=40) keeps card away from EDIT IN CANVA badge in listing templates. Total: T40/R120/B80/L40.
- `applyShadowToBuffer()` shared helper with per-side padding (`pad_top/right/bottom/left`) used by all three shadow tools — no code duplication.

**Failed:**
- First Canva export API attempt used `quality: "pro"` (wrong field) and assumed response shape `job.result.urls[0].url`. Actual shape is `job.urls[0]` (plain string array directly on job). Always debug-dump the actual API response before building parsers.
- First asset upload used JSON body with `upload_ref.type: "url"` — returned 400 "Unsupported content type". Canva asset upload requires binary body + octet-stream header.
- Asset name >50 chars causes 400 "Invalid upload metadata header" — truncated with `.slice(-50)`.

**Proven Design IDs:**
- `DAHD07F9MsY` — dark business card (page 1)
- `DAHD15IcxRs` — light business card (page 1)
- Spaces keys: `designs/{designId}/full_page1_{timestamp}.png`

**Next:**
- Wire `/export-full-card` and `/etsy-shadow` slash commands into the full listing creation pipeline so new designs auto-export with shadows.
- Build token refresh flow — current access token expires; `canva_oauth_headless.py` saves refresh token but no auto-refresh yet.
- Test `/etsy-angled` (-5 degree rotation) variant for lifestyle mockup images.
- Consider batch tool: export all pages of a multi-page design in one call.

---

### 2026-03-13 — Etsy Thumbnails

**Worked:**
- Canva MCP `get-design-thumbnail` returns real card artwork usable directly in Python — no screenshot hacks needed
- Canva `generate-design` produces good layout candidates when given detailed prompts with exact dimensions, colors, and element placement
- Existing 2+ year old Etsy listing designs are the right base — clone and swap card images rather than building from scratch
- Canva brand gradient confirmed: `#00C4CC` to `#7D2AE8` left to right

**Failed:**
- Python/Pillow card cropping is fragile — Canva exports both pages side by side so crops give wrong dimensions without careful math
- Iterating PIL compositing is slow — Canva native editing is faster and more accurate for layout work
- Rebuilding thumbnails from scratch wastes hours when proven designs already exist

**Next:**
- Open existing proven listing design (`DAFx_dsWpTA` or `DAFxukwKaiA`) in Canva MCP
- Clone it, swap card images with real dark `DAHD07F9MsY` and light `DAHD15IcxRs` designs
- Complete all 6 listing thumbnails using clone-and-swap method only

---

### 2026-03-13 — Light Business Card & Delivery PDF Pipeline

**Worked:**
- Canva MCP `generate-design` with highly specific layout prompts (exact element positions, colors, font styles) produces much better results than vague descriptions. Including negative instructions ("no geometric shapes, no patterns") is critical.
- Two-step Ideogram + Pillow composite for circle photos: Ideogram generates the photo (1:1 ratio), Pillow crops to circle mask, draws gold border ring, composites onto HTML-rendered card. Clean separation of concerns.
- Multi-product `template_links` dict with named keys (`business_card`, `business_card_light`) scales cleanly — `create_pdf()` renders one link box per product with proper labels and fallback to legacy format.
- Canva MCP grouped element IDs (triple-segment like `page-group-element`) work with `find_and_replace_text` even when `replace_text` fails with "not_found" on the same element.

**Failed:**
- First Canva `generate-design` round produced geometric/abstract designs with no tattoo relevance despite requesting "tattoo studio". Needed a second round with explicit negative constraints and style references ("Shoreditch/Brooklyn luxury meets ink artistry").
- Canva MCP has no clone/duplicate design tool — wasted time looking for it. Must generate fresh or user copies manually in Canva UI.
- `replace_text` on grouped elements returns "not_found" when using the 2-segment page-element ID format. Must use the full 3-segment page-group-element ID from the richtexts response.

**Next:**
- Build a prompt template library for Canva `generate-design` by niche (tattoo, nail, hair, etc.) with proven layout descriptions that work first time.
- Wire the light card PDF into Etsy digital file uploads alongside the dark version — buyers get both colour variants.
- Consider auto-generating both dark and light Canva designs in a single pipeline run using the `generate-design` → `create-design-from-candidate` → `start-editing-transaction` flow.

---

### 2026-03-11 — Canva MCP Integration & Design Editing

**Worked:**
- Applying gold color scheme to an existing template (DAHCEgOLAtA) in one bulk operation across both pages — 15 text elements formatted in a single transaction. Start from a solid structure and restyle, don't rebuild.
- Uploading assets via `upload-asset-from-url` to bring external images into a design when `update_fill` fails due to missing media bundles.
- `insert_fill` with explicit width/height/position creates clean new image elements without the cropping issues that `update_fill` + resize causes on existing containers.
- One transaction per logical change, commit before next — prevents cascading failures and makes rollback trivial.

**Failed:**
- Repurposing curved text elements — the curve is baked into the element container, not the text. Replacing text doesn't straighten it. Wasted multiple transactions discovering this.
- `update_fill` on existing image containers causes internal cropping that can't be controlled via the API. The fill zoom/offset is set internally by Canva.
- Trying to build a complex appointment card layout with only 3 text elements. The API cannot insert new text elements — only images/videos via `insert_fill`. Should have flagged this limitation immediately instead of attempting workarounds.
- Moving the logo placeholder repeatedly instead of leaving it in its original position. The user had to correct this multiple times.
- Searching for Canva template library elements — no `search-templates` or `search-elements` tool exists. Don't promise what the API can't do.

**Next:**
- For complex Canva layouts requiring many text elements, start from a template that already has the fields built in and restyle it (the DAHCEgOLAtA approach).
- Investigate whether Canva's `generate-design` or `generate-design-structured` tools could scaffold appointment card layouts with form fields.
- Consider building a prompt library for common Canva design patterns (appointment cards, business cards, social posts) that maps required elements to API capabilities.
- Always audit element limitations before proposing a design plan — count available text elements vs required, flag gaps upfront.

---

### 2026-03-11 — Strategic Ideas

**Next:**
- Sub-agent architecture is the logical next layer above Big Brain/Small Brain. Orchestrator assigns tasks to specialist agents (Research, Design, Listing, QA, Outreach, Analytics) — all propose, Andy approves. Dedicated architecture session needed before building.
- Pre-stock Canva asset folders per niche before design sessions — MCP `insert_fill` can leverage these without creating from scratch. Dog grooming assets needed before next week's session.
