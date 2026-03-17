# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added — 2026-03-17 (Pipeline Architecture)
- **`purpleocaz-pipeline` skill** (`.claude/skills/purpleocaz-pipeline/SKILL.md`) — Claude-only auto-loading skill covering standard listing spec, image sources, Canva folder IDs, delivery link rules, and 29 numbered gotchas extracted from every production failure in LESSONS.md. Replaces old `etsy-listing` skill.
- **`verify_listing.py`** (`scripts/verify_listing.py`) — post-build listing verifier. Checks images (count + ranks), PDF attachment, tag lengths + duplicates, price (£2.99), state, and Canva link format via Etsy API. Auto-refreshes OAuth on 401. Exit code 1 on failure.
- **`.claude/rules/pipeline.md`** — listing image sources (DAHDc0gyebE, DAFx_dsWpTA p3+p5), hero thumbnail pipeline, design creation pattern, proven design IDs.
- **`.claude/rules/canva.md`** — delivery link rules (/d/ shortcode only), folder IDs, element limitations, generate-design workarounds, export rules, shadow rules.
- **`.claude/rules/etsy.md`** — tag limits (20 chars, no dupes), pricing (set at creation), auth patterns, standard listing spec, verification requirement.

### Changed — 2026-03-17
- **CLAUDE.md refactored** — slimmed from 246 to 130 lines. Now a hub pointing to 7 rules files in `.claude/rules/`. All pipeline/Canva/Etsy rules extracted to dedicated files that auto-load every session.

### Removed — 2026-03-17
- **`etsy-listing` skill** — superseded by broader `purpleocaz-pipeline` skill.

### Verified — 2026-03-17
- **Listing #4472977919** (Business Card) — PASSED WITH WARNINGS (12/13 tags)
- **Listing #4473444461** (Appointment Card) — ALL CHECKS PASSED (9/9)

### Added — 2026-03-17 (Appointment Card — Product 2/7)
- **Tattoo appointment card — dark variant** (`DAHENCEJGjk`) — black/gold/botanical design with front appointment fields (Artist, Date, Time, Contact) and back aftercare tips + social CTA. Approved and registered.
- **Tattoo appointment card — light variant** (`DAHENKnCBoM`) — cream/charcoal/gold/botanical matching existing light business card palette. 7 text elements on back for granular aftercare tips. Approved and registered.
- **Design registry updated** — `tattoo/appointment_card/dark` and `tattoo/appointment_card/light` entries with all element IDs, color schemes, and Spaces export URLs.
- **Proven design pattern documented** — `generate-design` for aesthetic base → restyle text elements via editing API → export to Spaces for review → register in design_registry.json. Reusable for all future products.
- **Listing #4473444461 published LIVE** — Tattoo Appointment Card Template, £2.99, 3 images (hero + Canva Basics + Please Note), delivery PDF with dark + light Canva template links, 13 SEO tags. All verified via GET API before publish.
- **Hero thumbnail for appointment card** — DAHDc0gyebE template reused with appointment card images swapped in, banner post-processed to black, uploaded to Spaces CDN and Etsy rank 1.
- **6 hard rules added to CLAUDE.md** — verify before done, generate-design limitation, Etsy tag max 20 chars, price on drafts, listing image standard, Canva folder IDs.

### Fixed — 2026-03-17
- **STANDUP.md price correction** — tattoo business card listing price corrected from £12.99 to £2.99.

### Added — 2026-03-16 (Listing Pipeline)
- **Complete Etsy listing pipeline** — draft #4472977919 with verbatim copy, 3 images (hero + Canva Basics + Please Note), delivery PDF with Canva template links, 12 SEO tags. All verified via raw Etsy API GET calls.
- **Approved hero thumbnail pipeline** — DAHDc0gyebE template → card swap → full-width banner → export → Sharp black banner post-processing → Spaces CDN upload → Etsy listing upload.
- **Black banner via post-export pixel swap** — Canva API cannot change shape fill colors or control z-order, so crimson→black is done in Sharp after export.
- **Solid black Canva asset** `MAHEIi_EfxE` uploaded for future use.
- **Design page source documentation** — DAHDc0gyebE (1 page, hero only), DAFx_dsWpTA pages 3+5 are standard generic listing pages (Canva Basics + Please Note).
- **Etsy API learnings documented** — 20-char tag limit, no clone endpoint, price PATCH ignored on drafts, duplicate tag rejection, mandatory GET verification after uploads.

### Fixed — 2026-03-16
- **Hero thumbnail shadow approach** — replaced Pillow/Sharp shadow compositing (which produced hard black rectangles) with Canva template `DAHDc0gyebE` that has natural flatlay shadows built in. Cards now look physically lifted off the surface.
- **Black border on export** — removed explicit `width: 2000` from Canva export; native 1587x2245 dimensions export cleanly with no letterboxing.
- **Light card right-edge crop** — repositioned back card element from left=541 to left=470 so full card is visible within frame.

### Changed — 2026-03-16
- **Design registry v2** — `DAHDc0gyebE` is now the canonical thumbnail template for tattoo/business_card (replaces `DAFx_dsWpTA` for thumbnails). Registry restructured: `thumbnail_design_id` for hero images, `listing_design_id` for the 5-page listing design. Removed `shadow_preset` (shadows are now handled by the template, not code).

### Added — 2026-03-16
- **Terminus mobile SSH access** configured. UFW opened port 22 (`sudo ufw allow 22`). Root password set for password-based auth. Terminus on Android now successfully connects to droplet via password. Key-based auth attempted but not completed - future task to clean up.
- **Etsy OAuth headless flow** — `etsy_oauth.py` rewritten to use paste-the-redirect-URL approach (like Canva OAuth) instead of localhost callback server. Works from remote droplet and Terminus mobile SSH.
- **Etsy OAuth tokens live** — verified working against `/v3/application/users/me` and shop endpoint. Shop ID `34071205`, 937 active listings, 931 sales.
- **Full pipeline end-to-end run successful** — `run_single_listing.py` completed all 4 phases:
  - Phase 2: Claude generated listing content (13 tags, 100/100 quality)
  - Phase 3: Created 2 product images + delivery PDF + light business card variant + getting started guide
  - Phase 4: Published Etsy draft `#4472750162` with 2 images + digital PDF, saved to Google Sheets
  - Combined quality score: 100/100
  - Title: "Tattoo Business Kit Template, Editable Studio Branding Bundle, Printable Tattoo Shop Templates for Canva" at £12.99
- **Proactive Etsy token refresh** built in `publish_listings_tool.py` — 7 new tests, 16/16 passing, `expires_at` now persisted on refresh
- **Design registry** (`config/design_registry.json`) — maps niche + product_type to base Canva designs with confirmed-unlocked element IDs, card variants, text elements, shadow preset, and Spaces config. Initial entry: tattoo/business_card using DAFx_dsWpTA with 2 confirmed card slots and 2 text elements.
- **ThumbnailPipelineTool** (`workflows/auto_listing_creator/tools/thumbnail_pipeline_tool.py`) — autonomous Etsy thumbnail generator. Reads registry → gets Canva token (auto-refresh) → swaps card images via Canva REST editing API (one transaction per operation) → swaps text → exports PNG → applies ETSY_CARD_SHADOW_PRESET via Pillow (blur=12, opacity=0.75, asymmetric padding T40/R120/B80/L40) → uploads to DigitalOcean Spaces → returns CDN URL. Extends `BaseTool`, standard return shape.
- **20 tests** for thumbnail pipeline — registry lookup (9 tests), shadow compositing (5 tests), mocked execute flow (6 tests). All 47/47 project tests passing.

---

## [1.0.0] - 2026-03-15 — Canva MCP Pipeline & Shadow Tools

### Added
- **purpleocaz-canva-mcp** — TypeScript MCP server for Canva + DigitalOcean Spaces pipeline
  - `src/spaces-client.ts` — S3-compatible Spaces wrapper (upload/download/delete, CDN base `purpleocaz-assets.lon1.digitaloceanspaces.com`)
  - `src/canva-client.ts` — Canva API wrapper (export designs as PNG at 2100px, upload assets via binary `application/octet-stream` API)
  - `src/tools/asset-tools.ts` — `canva_export_and_stage`: export → download → Spaces → Canva asset
  - `src/tools/render-tools.ts` — four shadow/export tools:
    - `purpleocaz_export_full_card` — high-res full design export to Spaces + Canva
    - `purpleocaz_render_card_with_shadow` — configurable drop shadow compositing via Sharp
    - `purpleocaz_apply_etsy_shadow` — Canva-native shadow preset with asymmetric padding (T40/R120/B80/L40 for listing templates)
    - `purpleocaz_apply_etsy_shadow_angled` — -5 degree rotated lifestyle variant
  - `src/config/niches.ts` — `ETSY_CARD_SHADOW_PRESET` (blur=12, opacity=0.75, offset=15,15) and `ETSY_CARD_SHADOW_ANGLED_PRESET`
- **Canva OAuth headless flow** (`canva_oauth_headless.py`) — PKCE flow for remote servers, auto-updates MCP `.env` with tokens
- **Slash commands** — `/export-full-card`, `/etsy-shadow`, `/etsy-angled`
- **DigitalOcean Spaces** bucket `purpleocaz-assets` (lon1) with permanent public CDN URLs
- **Canva MCP design editing** — text replacement via editing transactions, gold colour scheme bulk restyling, asset uploads via `upload-asset-from-url`
- **Light business card** — Canva design `DAHD15IcxRs` (cream/charcoal/gold) + HTML/Playwright fallback with Ideogram circle photo composite
- **Multi-product delivery PDF** — `create_pdf()` supports named product link boxes with fallback to legacy A4/Letter/Print layout
- **Etsy thumbnail compositor** — `build_listing_1.py` (2700x2700 Pillow pipeline using real Canva card exports)
- **AI Brain Principles** in LESSONS.md — tool design principles from Claude Code team insights

### Changed
- **CLAUDE.md** — added Canva & Pipeline Tools section with session-start instructions
- **Etsy thumbnail strategy** — clone existing proven designs and swap card images via Canva MCP, never rebuild from scratch
- **Ideogram appointment card prompt** — two-card flatlay composition (front + back overlapping)
- **`product_creator_tool.py`** — both tiers render light business card variant, pass `ideogram_api_key` through
- Design DAHDolzpMTY restyled from dark red torn-edge to premium gold aesthetic (#C9A96E, #E8E0D4)
- MCP edit pattern established: one transaction per operation, commit before next

### Known Limitations
- Canva access tokens expire — no auto-refresh flow yet (refresh token saved but not wired)
- Canva asset upload name limited to 50 chars (truncated with `.slice(-50)`)
- Canva MCP cannot add new text elements, search templates/elements, or clone designs

---

## [0.9.0] - 2026-02-25

### Added

- **`docs/architecture/` directory** -- 11 architecture documentation files covering
  every built component in the system:
  - `00-index.md` -- Navigation hub with quick-find table and reading paths
  - `01-overview.md` -- System overview, tech stack, 3-layer architecture diagram
  - `02-orchestrator.md` -- SimpleOrchestrator, ExecutionLogger, _run_phase pattern
  - `03-tool-patterns.md` -- BaseTool contract, return format, all 18 existing tools
  - `04-validator-patterns.md` -- BaseValidator contract, return format, all 15 validators
  - `05-database.md` -- SQLiteClient query builder, full schema (4 tables), standard queries
  - `06-brain.md` -- SmallBrain analysis patterns, proposal format, thresholds
  - `07-workflows.md` -- All 5 workflows documented with phase tables, adding new workflows
  - `08-configuration.md` -- Config pattern, environment variables, LLM client
  - `09-testing.md` -- pytest patterns, test organization, running tests
  - `10-operations.md` -- Running workflows, debugging, show_logs, troubleshooting table

### Changed

- **`CLAUDE.md` rewritten from 805 lines to 111 lines** -- now a lean navigational
  file that routes to `docs/architecture/` for details. Contains only:
  - Architecture reference table (links to all 11 docs)
  - Critical rules (DO NOT / ALWAYS / NEVER)
  - Project conventions (one-liner summaries)
  - Quick task guide (6 reading paths)
  - Emergency procedures (5 common failures with fix links)
  - No implementation details (all moved to architecture files)

---

## [0.8.0] - 2026-02-20

### Added
- **Reddit and HackerNews as data sources** — workflow now monitors 8 feeds
  in total, pulling from a much wider signal pool.
  - HackerNews front page — `https://hnrss.org/frontpage`
  - HackerNews AI tool search — `https://hnrss.org/newest?q=AI+tool`
  - Reddit r/artificial — `https://www.reddit.com/r/artificial/new/.rss`
  - Reddit r/MachineLearning — `https://www.reddit.com/r/MachineLearning/new/.rss`
  - Reddit r/singularity — `https://www.reddit.com/r/singularity/new/.rss`
- **Atom feed support in `FetchRSSTool`** — Reddit serves Atom XML (not RSS 2.0)
  despite the `.rss` URL extension. `_parse()` now auto-detects the format:
  - RSS 2.0: delegates to `_parse_rss()` (existing logic, unchanged)
  - Atom: delegates to `_parse_atom()` (new) — handles namespaced tags,
    `<link href="..."/>` attribute URLs, and `<updated>`/`<published>` dates.
- **`ATOM_NS` module constant** — `"http://www.w3.org/2005/Atom"` used by the
  Atom parser to build namespaced tag queries.
- New feeds added to `.env` `RSS_FEED_URLS` — 3 original + 5 new = 8 total.

### Changed

- Updated header comment in `fetch_rss_tool.py` to document both supported
  feed formats (RSS 2.0 and Atom).

---

## [0.7.0] - 2026-02-19

### Fixed
- **Duplicate rows in Google Sheets** — `SaveToGoogleSheetsTool` now reads all
  existing URLs from column B before writing. Articles whose URL is already
  present in the sheet are skipped, preventing the same article being saved on
  every workflow run.
- Terminal output now shows a duplicate count:
  `Saved 3 new row(s) to Google Sheets  |  9 duplicate(s) skipped`

### Changed
- `GoogleSheetsSaveValidator` receives `total_input = new articles only` so
  the validator correctly passes when all new articles were saved (even when
  some were skipped as duplicates).

---

## [0.6.0] - 2026-02-19

### Added
- **Multi-feed RSS support** — `FetchRSSTool` now accepts `rss_urls` (a list)
  in addition to the original single `rss_url` parameter (kept for backward
  compatibility).
- Results from multiple feeds are combined and deduplicated by article URL, so
  if the same story appears in two feeds it is only saved once.
- If one feed fails to download, the tool continues with the remaining feeds
  and only errors if ALL feeds fail.
- Default feeds pre-configured in `workflows/ai_news_rss/config.py`:
  - TechCrunch AI — `https://techcrunch.com/category/artificial-intelligence/feed/`
  - The Verge AI — `https://www.theverge.com/ai-artificial-intelligence/rss/index.xml`
  - VentureBeat AI — `https://venturebeat.com/category/ai/feed/`
- `RSS_FEED_URLS` env var (comma-separated) added to `.env.example`.
- Startup banner now lists every feed URL being polled.

### Changed
- `workflows/ai_news_rss/config.py` — `RSS_FEED_URL` kept as a backward-compat
  alias pointing to the first feed; new canonical setting is `RSS_FEED_URLS`.

---

## [0.5.0] - 2026-02-19

### Changed
- **Migrated Phase 3 destination from Airtable to Google Sheets** across the
  entire `ai_news_rss` workflow.
- `SaveToGoogleSheetsTool` (new) replaces `SaveToAirtableTool` (removed).
  Uses `gspread` with a Service Account JSON key for auth.
  - Auto-creates the worksheet tab if it does not exist.
  - Auto-adds the header row (Title, URL, Publication Date, Description, Source)
    if the sheet is empty.
  - Appends all rows in a single `append_rows` API call.
- `GoogleSheetsSaveValidator` (new) replaces `AirtableSaveValidator` (removed).
  `needs_more = False` always — retrying would create duplicate rows.
- `workflows/ai_news_rss/config.py` — Airtable block replaced with:
  `GOOGLE_CREDENTIALS_FILE`, `GOOGLE_SPREADSHEET_ID`, `GOOGLE_SHEET_NAME`.
- `workflows/ai_news_rss/run.py` — all Phase 3 imports, params, and print
  statements updated to reference Google Sheets.
- `.env.example` — Airtable fields replaced with Google Sheets setup guide.
- `.gitignore` — added `google-credentials.json`, `*-credentials.json`,
  `service-account*.json` to prevent accidental credential commits.

### Added
- `gspread>=6.0.0` added to `requirements.txt`.

### Removed
- `workflows/ai_news_rss/tools/save_to_airtable_tool.py`
- `workflows/ai_news_rss/validators/airtable_save_validator.py`

---

## [0.4.0] - 2026-02-18

### Added
- **`workflows/ai_news_rss/` — AI News RSS workflow** (3-phase pipeline).

  | Phase | Tool | Validator |
  |-------|------|-----------|
  | 1 — Fetch | `FetchRSSTool` | `ArticlesFetchedValidator` |
  | 2 — Filter | `FilterRecentTool` | `ValidDatesValidator` |
  | 3 — Save | `SaveToGoogleSheetsTool` | `GoogleSheetsSaveValidator` |

- `FetchRSSTool` — downloads RSS 2.0 feeds using only stdlib (`urllib` +
  `xml.etree.ElementTree`). Strips HTML from descriptions. Skips items that
  have neither a title nor a URL.
- `FilterRecentTool` — keeps articles published within a configurable lookback
  window (default 24 h). Parses RFC 2822 dates (standard RSS) with ISO 8601
  fallback. Adds a normalized `pub_date_iso` field to each article.
- `ArticlesFetchedValidator` — fails if the articles list is empty or not a
  list. `needs_more = False` (retrying the same feed won't help).
- `ValidDatesValidator` — passes even when the filtered list is empty (no
  recent articles today is a valid outcome, not an error).
- `workflows/ai_news_rss/config.py` — workflow-local config with RSS and
  Google Sheets settings loaded from `.env` via `python-dotenv`.
- `workflows/ai_news_rss/run.py` — pipeline entry point using
  `ExecutionLogger` directly (not `SimpleOrchestrator`) because each phase
  passes its output as input to the next phase. Implements `_run_phase()`
  helper for retry + logging logic.
- `.env.example` updated with `RSS_FEED_URL` and `LOOKBACK_HOURS`.

---

## [0.3.0] - 2026-02-18

### Added
- **`scripts/show_logs.py` — HTML execution log viewer**.
  - Queries `data/system.db` via `SQLiteClient` (no raw SQL).
  - Generates a self-contained HTML report grouped by execution, with
    color-coded rows per event type (phase, tool call, validation, error).
  - JSON metadata rendered as a mini key/value table.
  - Collapsible execution sections via `<details>/<summary>`.
  - Auto-opens the report in the default browser.
  - CLI usage: `python scripts/show_logs.py [workflow_id] [--last N]`

---

## [0.2.0] - 2026-02-18

### Added
- **`templates/workflow_template/` — reusable workflow scaffold**.
  Copy this folder to start any new workflow; all wiring is already in place.

  | File | Purpose |
  |------|---------|
  | `config.py` | Workflow-local settings (name, DB path, thresholds) |
  | `run.py` | Entry point; registers workflow, drives orchestrator, runs SmallBrain |
  | `orchestrator.py` | `SimpleOrchestrator` — iterates plan steps, handles retry + logging |
  | `brain.py` | `SmallBrain` — queries execution logs, saves improvement proposals |
  | `tools/example_tool.py` | Reference `BaseTool` implementation |
  | `validators/example_validator.py` | Reference `BaseValidator` implementation |

- All template files use correct `sys.path` depth so `from lib.orchestrator...`
  and `from config import ...` resolve regardless of where Python is invoked.

---

## [0.1.0] - 2026-02-18

### Added
- **Core infrastructure** (`lib/` directory):
  - `lib/orchestrator/base_tool.py` — abstract base class for all tools;
    enforces `execute(**kwargs) -> dict` contract with standard return shape
    (`success`, `data`, `error`, `tool_name`, `metadata`).
  - `lib/orchestrator/base_validator.py` — abstract base class for all
    validators; enforces `validate(data, context) -> dict` contract
    (`passed`, `issues`, `needs_more`, `validator_name`, `metadata`).
  - `lib/orchestrator/execution_logger.py` — buffered event logger; writes
    `phase_start/end`, `tool_call/result`, `validation_event`, and `error`
    events to `execution_logs` table. **Must call `flush()` in a `finally`
    block** — the buffer is lost otherwise and SmallBrain has no data.
  - `lib/common_tools/sqlite_client.py` — Supabase-compatible query builder
    over SQLite. Chainable API: `.table().select().eq().order().limit().execute()`.
    Same code runs unchanged against Supabase in production.
  - `lib/common_tools/llm_client.py` — thin wrapper around the Anthropic
    Claude API (`call_llm()`).
  - `lib/brain/small_brain.py` — per-workflow pattern learner; activates after
    `PROPOSAL_THRESHOLD_RUNS` executions and saves proposals to DB.
  - `lib/brain/big_brain.py` — cross-workflow insight engine (future).
- **Database schema** (`scripts/init_db.py`):
  tables: `workflows`, `executions`, `execution_logs`, `proposals`.
- **Project configuration** (`config.py`) — central settings file; all
  values loaded from `.env` via `python-dotenv`. Never hardcode these.
- **`requirements.txt`** — pinned dependencies:
  `anthropic`, `python-dotenv`, `pytest`, `pytest-cov`, `fastapi`, `uvicorn`,
  `requests`, `feedparser`, `gspread`.
- **`tests/`** — pytest suite covering `BaseTool`, `BaseValidator`,
  `ExecutionLogger`, and `SQLiteClient`.
- **`.env.example`** — environment variable template.
- **`.gitignore`** — excludes `.env`, `data/*.db`, `__pycache__`, IDE files,
  Google credential JSON files, build artefacts.
- **`CLAUDE.md`** — AI assistant guide; documents critical rules, patterns,
  anti-patterns, and architecture for this codebase.
- **`SYSTEM_ARCHITECTURE.md`** — full 35 KB architecture specification.

---

[Unreleased]: https://github.com/ChurnShield/Etsypurpleocaz-/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/ChurnShield/Etsypurpleocaz-/compare/v0.9.0...v1.0.0
[0.9.0]: https://github.com/ChurnShield/Etsypurpleocaz-/compare/v0.8.0...v0.9.0
[0.8.0]: https://github.com/ChurnShield/Etsypurpleocaz-/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/ChurnShield/Etsypurpleocaz-/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/ChurnShield/Etsypurpleocaz-/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/ChurnShield/Etsypurpleocaz-/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/ChurnShield/Etsypurpleocaz-/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/ChurnShield/Etsypurpleocaz-/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/ChurnShield/Etsypurpleocaz-/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/ChurnShield/Etsypurpleocaz-/releases/tag/v0.1.0
