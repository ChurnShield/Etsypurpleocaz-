# System Overview -- 3-Layer Dual Learning Agentic AI

**Version**: 1.1.0 | **Date**: 2026-03-23 | **Status**: 🚧 In Progress

> **Note**: This is the high-level system overview.
> For project-wide rules and conventions, see [CLAUDE.md](../../CLAUDE.md).
>
> **Cross-references**:
> - Architecture details: [docs/architecture/02-orchestrator.md](02-orchestrator.md)
> - Database schema: [docs/architecture/05-database.md](05-database.md)
> - Brain system: [docs/architecture/06-brain.md](06-brain.md)

## Table of Contents

1. [Overview](#overview)
2. [Tech Stack](#tech-stack)
3. [System Architecture](#system-architecture)
4. [Data Flow](#data-flow)
5. [Directory Structure](#directory-structure)

## Overview

A self-improving workflow automation platform where an Orchestrator executes tasks mechanically, a SmallBrain learns per-workflow patterns, and a BigBrain detects cross-workflow insights. Built for Andy Nosworthy's Etsy shop PurpleOcaz.

### What it does

- Executes multi-phase workflows (fetch data, transform, save to Google Sheets/Etsy)
- Logs every tool call, validation, and phase transition to SQLite
- SmallBrain analyses execution logs after 15+ runs and proposes improvements
- BigBrain detects patterns across multiple workflows (`lib/big_brain/`)
- All proposals require human approval before changes are applied

### What it does NOT do

- Auto-apply proposals without human review (human-in-the-loop enforced)
- Serve a web UI (CLI-only execution via `python workflows/*/run.py`)
- Handle real-time streaming or webhooks

## Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | 3.10+ |
| LLM | Anthropic Claude API | claude-sonnet-4-20250514 |
| Database (dev) | SQLite | via sqlite3 stdlib |
| Database (prod) | Supabase | planned |
| HTTP Client | requests | 2.31.0+ |
| Sheets | gspread | 6.0+ |
| RSS | feedparser | 6.0+ |
| API | FastAPI + Uvicorn | 0.104.0+ |
| PDF Generation | ReportLab | 4.0+ |
| SVG | svgwrite | 1.4+ |
| Email | SendGrid | 6.12+ |
| Trends | pytrends | 4.9+ |
| Testing | pytest + pytest-cov | 7.4.0+ |
| Config | python-dotenv | 1.0.0+ |

## System Architecture

```
Layer 3: BRAIN (Intelligence)
    SmallBrain (per-workflow)     BigBrain (cross-workflow) — lib/big_brain/
         |                              |
         | reads logs                   | reads logs from ALL workflows
         | writes proposals             | writes system-wide proposals
         v                              v
    [proposals table]            [proposals table]
         |                              |
         | human approves               | human approves
         v                              v

Layer 2: ORCHESTRATOR (Execution)
    SimpleOrchestrator
         |
         | runs plan: tool -> validate -> retry -> log
         |
    ExecutionLogger (buffers events, flush() writes to DB)
         |
         v
    [execution_logs table]

Layer 1: TOOLS & VALIDATORS (Business Logic)
    BaseTool subclasses          BaseValidator subclasses
    (fetch, transform, save)     (check quality, flag issues)
         |                              |
         | standard return dicts        | standard return dicts
         v                              v
    {success, data, error,       {passed, issues, needs_more,
     tool_name, metadata}         validator_name, metadata}
```

## Data Flow

```
Workflow Trigger (python workflows/*/run.py)
    |
    v
[1] Connect to SQLite DB
    |
    v
[2] Register workflow (first run only)
    |
    v
[3] Create execution_id (UUID)
    |
    v
[4] Run phases via _run_phase() or SimpleOrchestrator
    |   For each phase:
    |     tool.execute(**params) -> validator.validate(data)
    |     ExecutionLogger records every event
    |
    v
[5] logger.flush() in finally block (CRITICAL)
    |
    v
[6] Update workflow stats (total_runs, successful_runs)
    |
    v
[7] SmallBrain.analyze() -- checks if 15+ runs accumulated
    |
    v
[8] Print summary
```

## Directory Structure

```
NEW AI PROJECT/
|-- lib/                          Core system libraries
|   |-- orchestrator/             Execution layer
|   |   |-- base_tool.py          ABC for all tools
|   |   |-- base_validator.py     ABC for all validators
|   |   |-- execution_logger.py   Buffered logging to DB
|   |   +-- __init__.py
|   |-- common_tools/             Shared utilities
|   |   |-- sqlite_client.py      Supabase-compatible query builder
|   |   |-- llm_client.py         Claude API wrapper
|   |   |-- canva_token_manager.py Canva OAuth token management
|   |   +-- __init__.py
|   |-- brain/                    Intelligence layer (SmallBrain lives in templates/)
|   |   +-- __init__.py
|   +-- big_brain/                Cross-workflow intelligence
|       |-- brain.py              BigBrain analysis engine
|       |-- hooks.py              Event hooks for brain triggers
|       |-- system_proposer.py    System-wide proposal generator
|       +-- __init__.py
|-- workflows/                    Production workflows
|   |-- ai_news_rss/              RSS -> Google Sheets
|   |-- ai_news_workflow/         RSS -> Airtable (alternate pipeline)
|   |-- etsy_analytics/           Etsy API -> analysis -> Sheets
|   |-- etsy_seo_optimizer/       Tag analysis -> Claude -> Sheets
|   |-- tattoo_trend_monitor/     Trends -> opportunities -> Sheets
|   |-- market_intelligence/      Market research -> insights
|   +-- auto_listing_creator/     Trends -> content -> images -> Etsy
|-- templates/
|   +-- workflow_template/        Reference implementation
|       |-- orchestrator.py       SimpleOrchestrator class
|       |-- brain.py              SmallBrain class
|       |-- run.py                Entry point template
|       |-- config.py             Config template
|       |-- tools/                Example tool
|       +-- validators/           Example validator
|-- scripts/                      Utility & generation scripts
|   |-- init_db.py                Database initialization
|   |-- show_logs.py              HTML execution report generator
|   |-- verify_listing.py         Post-listing Etsy verification
|   |-- digest_processor.py       Weekly digest -> ideas + SendGrid email
|   |-- weekly_review.py          Weekly performance review
|   |-- weekly_performance_check.py  Performance metrics check
|   |-- digest_performance.py     Digest analytics
|   |-- generate_tattoo_forms.py  Tattoo form PDF generation (+ v2)
|   |-- generate_*_forms.py       Niche-specific form generators (barbershop, lash, nail, hair)
|   |-- generate_flyer_*.py       Flyer generators (flash, promo, studio, walkin)
|   |-- generate_loyalty_card.py  Loyalty card PDF generation
|   |-- generate_gift_certificate.py Gift certificate generation
|   |-- generate_price_list.py    Price list generation
|   |-- composite_forms_hero.py   Hero image compositing
|   |-- fetch_niche_photo.py      Unsplash niche photo fetcher
|   +-- rebuild_rank_images.py    Etsy image rank rebuilder
|-- api/                          FastAPI REST layer
|   +-- app.py                    API endpoints
|-- skills/                       Claude Code skill definitions
|   |-- design.md                 Canva design skill
|   |-- etsy-listing.md           Etsy listing skill
|   |-- pdf-bundle.md             PDF bundle skill
|   |-- sop.md                    SOP skill
|   |-- stop-slop/                Anti-slop copy quality rules
|   +-- tech-stack.md             Tech stack skill
|-- hooks/                        Session & task lifecycle hooks
|   |-- preflight.sh              Session start pre-flight check
|   |-- on_task_complete.sh       Log wins after successful tasks
|   +-- on_task_fail.sh           Log lessons after failures
|-- config/                       Runtime configuration
|   +-- design_registry.json      Canva design ID registry
|-- exports/                      Listing build scripts
|-- tests/                        pytest test suite
|-- data/                         SQLite database (gitignored)
|-- digests/                      Weekly intelligence digests
|-- transcripts/                  YouTube transcript archive
|-- CanvaAutomationSuite/         Browser-based Canva automation
|-- purpleocaz-canva-mcp/         Canva MCP server (Node/TS)
|-- config.py                     Root-level configuration
|-- digest.py                     Weekly digest generator (cron)
|-- transcribe.py                 YouTube transcript fetcher (cron)
|-- server.py                     FastAPI dev server entry point
|-- main.py                       API test script (demo only)
+-- requirements.txt              Python dependencies
```
