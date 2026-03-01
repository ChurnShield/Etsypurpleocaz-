# CLAUDE.md -- 3-Layer Dual Learning Agentic AI System

**For AI Assistants**: Read this file first. For detailed docs, load files from docs/architecture/ on-demand.

---

## Architecture Reference

| Topic | File |
|-------|------|
| Navigation hub | [docs/architecture/00-index.md](docs/architecture/00-index.md) |
| System overview | [docs/architecture/01-overview.md](docs/architecture/01-overview.md) |
| Orchestrator & Logger | [docs/architecture/02-orchestrator.md](docs/architecture/02-orchestrator.md) |
| Tool patterns | [docs/architecture/03-tool-patterns.md](docs/architecture/03-tool-patterns.md) |
| Validator patterns | [docs/architecture/04-validator-patterns.md](docs/architecture/04-validator-patterns.md) |
| Database layer | [docs/architecture/05-database.md](docs/architecture/05-database.md) |
| Brain system | [docs/architecture/06-brain.md](docs/architecture/06-brain.md) |
| Workflows | [docs/architecture/07-workflows.md](docs/architecture/07-workflows.md) |
| Configuration | [docs/architecture/08-configuration.md](docs/architecture/08-configuration.md) |
| Testing | [docs/architecture/09-testing.md](docs/architecture/09-testing.md) |
| Operations | [docs/architecture/10-operations.md](docs/architecture/10-operations.md) |

---

## Critical Rules

### DO NOT Modify or Delete

- `lib/orchestrator/base_tool.py` -- ABC contract for all tools; changing breaks all workflows
- `lib/orchestrator/base_validator.py` -- ABC contract for all validators
- `lib/orchestrator/execution_logger.py` -- Logging contract; Brain depends on it
- `lib/common_tools/sqlite_client.py` -- Supabase compatibility layer
- `scripts/init_db.py` -- Database schema; changes require migration strategy
- `config.py` -- Root configuration; changes cascade system-wide
- `data/system.db` -- Production data; corruption is unrecoverable

### ALWAYS Do

- Use `ExecutionLogger` with `try/finally` and `logger.flush()` in the finally block
- Extend `BaseTool` for all tools; return `{success, data, error, tool_name, metadata}`
- Extend `BaseValidator` for all validators; return `{passed, issues, needs_more, validator_name, metadata}`
- Use `SQLiteClient` query builder for all DB access (never raw sqlite3)
- Import config values from `config.py` (never hardcode API keys, paths, thresholds)
- Run `pytest tests/ -v` before claiming code is complete

### NEVER Do

- Skip `logger.flush()` or put it outside a finally block (logs are lost, Brain goes blind)
- Bypass base classes with custom tool/validator interfaces (breaks Brain analysis)
- Use raw `sqlite3` instead of `SQLiteClient` (breaks Supabase compatibility)
- Hardcode API keys, model names, file paths, or thresholds
- Auto-apply Brain proposals without human approval
- Log API keys or secrets in execution_logs metadata

---

## Project Conventions

- **Files**: `snake_case.py` (e.g., `execution_logger.py`, `base_tool.py`)
- **Classes**: `PascalCase` with `Base*` prefix for ABCs (e.g., `BaseTool`, `ExecutionLogger`)
- **Functions/variables**: `snake_case`; private methods `_prefixed`
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`, `DATABASE_PATH`)
- **Error handling**: Tools catch all exceptions and return error dicts (never raise)
- **Database**: Always via `SQLiteClient` chainable API (`.table().select().eq().execute()`)
- **Tools return**: `{success: bool, data: Any, error: str|None, tool_name: str, metadata: dict}`
- **Validators return**: `{passed: bool, issues: list, needs_more: bool, validator_name: str, metadata: dict}`

---

## Quick Task Guide

**Understanding the system**: Read 01-overview -> 02-orchestrator -> 07-workflows -> 05-database

**Adding a new workflow**: Read 07-workflows -> 03-tool-patterns -> 04-validator-patterns -> 08-configuration

**Adding a new tool**: Read 03-tool-patterns -> 04-validator-patterns -> 09-testing

**Debugging a failure**: Read 10-operations -> 02-orchestrator -> 05-database

**Understanding SmallBrain**: Read 06-brain -> 02-orchestrator -> 05-database

**Setting up from scratch**: Read 08-configuration -> 10-operations -> 01-overview

---

## Out of Scope

Do NOT:
- Modify base class interfaces without explicit permission
- Add new dependencies without approval
- Change database schema without a migration strategy
- Auto-apply proposals from SmallBrain (human-in-the-loop required)
- Refactor working workflows unless explicitly requested

---

## Emergency Procedures

- **No logs after workflow run**: Missing `logger.flush()` in finally block -> see [02-orchestrator.md](docs/architecture/02-orchestrator.md)
- **Database corruption**: Restore backup or re-run `python scripts/init_db.py` (WARNING: loses data) -> see [05-database.md](docs/architecture/05-database.md)
- **Etsy API 401/403**: Check API key format (`keystring:shared_secret`) or re-run OAuth -> see [10-operations.md](docs/architecture/10-operations.md)
- **Import errors**: Ensure `__init__.py` exists in all dirs and check sys.path setup -> see [10-operations.md](docs/architecture/10-operations.md)
- **SmallBrain not generating proposals**: Need 15+ runs first; check `PROPOSAL_THRESHOLD_RUNS` -> see [06-brain.md](docs/architecture/06-brain.md)

---

## Anti-Gravity Strategy (Etsy Growth Engine)

The pipeline implements three compounding flywheels designed to produce increasing returns with decreasing effort:

### 1. Algorithmic Flywheel (Etsy quality score)

- **Long-tail keywords**: `NICHE_KEYWORD_STRATEGIES` in `generate_listing_content_tool.py` provides niche-specific keyword research data
- **Dwell-time descriptions**: Listings include PERFECT FOR, FAQ, and use-case sections to increase time-on-page (2026 algorithm signal)
- **Tag formula**: 13 tags split across core product, format/modifier, buyer intent, adjacent niche, and seasonal angles
- **Bundle tags**: Every listing gets `bundle_tags` for automatic grouping

### 2. Catalog Flywheel (compounding assets)

- **Bundle auto-creator**: `BundleCreatorTool` in `tools/bundle_creator_tool.py` groups products into Starter Kit / Complete Bundle / Mega Pack tiers
- **Niche expansion**: `EXPANSION_NICHES` in config supports multi-niche catalog growth (tattoo, nail, hair, beauty, spa)
- **Cross-pollination**: Each bundle references its component listings, driving traffic between them

### 3. Operational Flywheel (automation leverage)

- **Zero marginal cost**: Digital products created once, sold infinitely
- **Affiliate guide**: Every PDF includes branded Getting Started guide with affiliate links
- **Pipeline phases**: Load -> Generate (anti-gravity keywords) -> Bundle -> Create -> Publish

### Key Config

| Setting | Location | Default |
|---------|----------|---------|
| `FOCUS_NICHE` | workflow config.py | `tattoo` |
| `EXPANSION_NICHES` | env / config.py | `[FOCUS_NICHE]` |
| `ENABLE_BUNDLES` | env / config.py | `true` |
| `MIN_BUNDLE_SIZE` | env / config.py | `3` |

### Pipeline Flow (Updated)

```
Phase 1  -> Load opportunities from Trend Monitor
Phase 2  -> Generate listing content (anti-gravity keyword engine)
Phase 2b -> Auto-bundle creation (groups products into value bundles)
Phase 3  -> Create product images (Tier 1: Gemini AI / Tier 2: HTML)
Phase 4  -> Publish to Sheets + Etsy drafts + upload images/PDFs
```

---

## Quick Start

1. Read this file (critical rules and conventions)
2. Load the relevant docs/architecture/ file for your task
3. Run tests before claiming any change is complete: `pytest tests/ -v`
