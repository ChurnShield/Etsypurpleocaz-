# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

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

[Unreleased]: https://github.com/your-org/your-repo/compare/v0.7.0...HEAD
[0.7.0]: https://github.com/your-org/your-repo/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/your-org/your-repo/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/your-org/your-repo/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/your-org/your-repo/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/your-org/your-repo/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/your-org/your-repo/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/your-org/your-repo/releases/tag/v0.1.0
