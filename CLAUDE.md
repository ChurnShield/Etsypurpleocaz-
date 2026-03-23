CRITICAL: Run the pre-flight hook first every session: `bash hooks/preflight.sh`
This reads SOUL.md, STANDUP.md, and LESSONS.md and outputs a session summary.
If SOUL.md is missing from disk, stop immediately and tell Andy.

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

Context modes: `.claude/contexts/` — type `/context [build|research|review]` to switch.

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
- Commit based on "yes" alone — only commit when user explicitly says "approved, commit now" or "commit this"

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
| Adding a script | `scripts/` → look at existing generators for patterns |
| Debugging a failure | 10-operations → 02-orchestrator → 05-database |
| Building a listing | `.claude/rules/pipeline.md` → `canva.md` → `etsy.md` |
| Running the weekly pipeline | See "Weekly Automation Pipeline" section below |

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

## Weekly Automation Pipeline

Four cron jobs run every Monday (UTC) to produce weekly intelligence:

| Time | Script | What it does |
|------|--------|-------------|
| 06:00 | `transcribe.py` | Fetches YouTube transcripts → `transcripts/` |
| 07:00 | `digest.py` | Analyses transcripts via Claude → `digests/DIGEST_YYYY-MM-DD.md` |
| 07:30 | `scripts/weekly_review.py` | Weekly performance review |
| 08:00 | `scripts/digest_processor.py` | Extracts top 5 ideas via Claude, appends to `ideas_backlog.md`, emails summary via SendGrid |

Crontab is on the VPS. Edit with `crontab -e`. Logs go to `logs/`.

---

## Scripts Overview

`scripts/` contains 26+ utility scripts. Key categories:

- **Pipeline**: `digest_processor.py`, `weekly_review.py`, `weekly_performance_check.py`, `digest_performance.py`
- **Verification**: `verify_listing.py` (post-listing Etsy checks)
- **PDF Generators**: `generate_tattoo_forms.py`, `generate_*_forms.py` (barbershop, lash, nail, hair), `generate_flyer_*.py`, `generate_loyalty_card.py`, `generate_gift_certificate.py`, `generate_price_list.py`
- **Image Tools**: `composite_forms_hero.py`, `fetch_niche_photo.py`, `rebuild_rank_images.py`, `generate_starter_bundle_heroes.py`
- **Database**: `init_db.py`, `show_logs.py`

---

## Skills

`skills/` contains Claude Code skill definitions used by slash commands:

| Skill | File |
|-------|------|
| Design (Canva) | `skills/design.md` |
| Etsy listing | `skills/etsy-listing.md` |
| PDF bundle | `skills/pdf-bundle.md` |
| SOP | `skills/sop.md` |
| Anti-slop copy rules | `skills/stop-slop/` |
| Tech stack | `skills/tech-stack.md` |

---

## BigBrain & API

- **BigBrain** (`lib/big_brain/`): Cross-workflow intelligence layer. `brain.py` analyses patterns across all workflows, `system_proposer.py` generates system-wide proposals, `hooks.py` triggers analysis on events. All proposals require human approval.
- **API** (`api/app.py`, `server.py`): FastAPI REST layer for programmatic access.

---

## Emergency Procedures

- **No logs after run**: Missing `logger.flush()` in finally → see 02-orchestrator.md
- **Database corruption**: `python scripts/init_db.py` (WARNING: loses data)
- **Etsy 401/403**: Check key format (`keystring:shared_secret`) or re-run OAuth
- **Import errors**: Check `__init__.py` and sys.path
- **SendGrid email not arriving**: Check `SENDGRID_API_KEY` in `.env`, verify sender in SendGrid dashboard, check `logs/digest_processor.log`
- **Cron jobs not running**: `crontab -l` to verify, check `logs/` for output, ensure scripts have correct shebangs
- **Transcript pipeline stale**: Check `transcripts/` for recent files, verify YouTube API key in `.env`, check `logs/transcribe.log`

---

## Business Context

#PurpleOcaz → Etsy, templates, digital products, Canva, passive income
#ChurnShield → SaaS, churn, retention, B2B
#AgentLearning → Claude, AI agents, MCP, n8n, automation

## Learning Loop — Post-Task Requirements

After every significant task (listing build, design creation, pipeline run, tool build, bug fix):

### On success
Run: `bash hooks/on_task_complete.sh "Task name" "What worked and why"`
This appends the successful pattern to `WINS.md` so we repeat what works.

### On failure or gotcha
Run: `bash hooks/on_task_fail.sh "Task name" "What failed" "Root cause" "Fix applied"`
This appends the lesson to `LESSONS.md` so we never hit the same problem twice.

### What counts as "significant"
- Any Etsy API call (create, update, activate, upload)
- Any Canva design operation (generate, edit, export)
- Any pipeline phase completion
- Any tool or script creation/modification
- Any bug fix or production incident

Trivial tasks (reading files, git status, exploratory searches) do not need logging.

---

## Copy Quality Rule
ALWAYS read skills/stop-slop/SKILL.md before writing ANY Etsy listing copy, descriptions, titles or tags. No exceptions. Score the copy before submitting — must be 35/50 or above.
