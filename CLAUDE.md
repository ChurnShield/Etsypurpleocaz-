CRITICAL: Read SOUL.md before anything else every session. If SOUL.md is missing from disk, stop immediately and tell Andy.

# CLAUDE.md — PurpleOcaz Agentic AI System

**Entry point.** Rules are split into focused files loaded automatically.

---

## Rules (auto-loaded by Claude Code)

| File | Scope |
|------|-------|
| `.claude/rules/pipeline.md` | Listing pipeline: image sources, hero thumbnails, design flow |
| `.claude/rules/canva.md` | Canva MCP: delivery links, folder IDs, element limits, gotchas |
| `.claude/rules/etsy.md` | Etsy API: tags, pricing, auth, verification |
| `.claude/rules/database.md` | SQLiteClient access, schema rules |
| `.claude/rules/security.md` | Credentials, protected files, Brain safety |
| `.claude/rules/testing.md` | pytest conventions, mocking, coverage |
| `.claude/rules/tool-conventions.md` | BaseTool / BaseValidator contracts |

## Architecture Docs (load on-demand)

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

## Critical Rules (summary — details in rules files)

### ALWAYS
- `ExecutionLogger` with `try/finally` and `logger.flush()` in finally
- Extend `BaseTool` / `BaseValidator` for all tools/validators
- `SQLiteClient` for all DB access (never raw sqlite3)
- Config values from `config.py` (never hardcode)
- `pytest tests/ -v` before claiming done
- `python scripts/verify_listing.py {id}` after every listing build

### NEVER
- Skip `logger.flush()` — Brain goes blind
- Auto-apply Brain proposals — human-in-the-loop required
- Hardcode API keys, paths, or thresholds
- Use PUT on Etsy listings — PATCH only
- Use `/design/.../edit` links in delivery PDFs — `/d/{shortcode}` only

---

## Project Conventions

- **Files**: `snake_case.py`
- **Classes**: `PascalCase`, `Base*` for ABCs
- **Functions/variables**: `snake_case`, `_private`
- **Constants**: `UPPER_SNAKE_CASE`
- **Tools return**: `{success, data, error, tool_name, metadata}`
- **Validators return**: `{passed, issues, needs_more, validator_name, metadata}`
- **Content**: When exact copy is provided — use it VERBATIM. Never rewrite.

---

## Quick Task Guide

| Task | Read order |
|------|------------|
| Understanding the system | 01-overview → 02-orchestrator → 07-workflows |
| Adding a workflow | 07-workflows → 03-tool-patterns → 08-configuration |
| Adding a tool | 03-tool-patterns → 04-validator-patterns → 09-testing |
| Debugging a failure | 10-operations → 02-orchestrator → 05-database |
| Building a listing | `.claude/rules/pipeline.md` → `canva.md` → `etsy.md` |

---

## Session Management

### On Session Start
1. Read SOUL.md
2. Read most recent file in `digests/`
3. Check `ideas_backlog.md` for unchecked items
4. Check `transcripts/` for files newer than latest digest
5. Check GitHub commits, Canva folders, Etsy drafts for crash recovery

### On Session End
1. Update CHANGELOG.md [Unreleased] section
2. Update LESSONS.md with worked/failed/next
3. git add + commit + push all changed files
4. Confirm push was successful

---

## Canva & Pipeline Tools

- Shadow commands: `/export-full-card`, `/etsy-shadow`, `/etsy-angled`
- Shadow preset: `purpleocaz-canva-mcp/src/config/niches.ts` (`ETSY_CARD_SHADOW_PRESET`)
- Canva tokens: `workflows/auto_listing_creator/canva_tokens.json` + `purpleocaz-canva-mcp/.env`

---

## Emergency Procedures

- **No logs after run**: Missing `logger.flush()` in finally → see 02-orchestrator.md
- **Database corruption**: `python scripts/init_db.py` (WARNING: loses data)
- **Etsy 401/403**: Check key format (`keystring:shared_secret`) or re-run OAuth
- **Import errors**: Check `__init__.py` and sys.path

---

## Business Context

#PurpleOcaz → Etsy, templates, digital products, Canva, passive income
#ChurnShield → SaaS, churn, retention, B2B
#AgentLearning → Claude, AI agents, MCP, n8n, automation
