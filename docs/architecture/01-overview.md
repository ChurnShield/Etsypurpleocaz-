# System Overview -- 3-Layer Dual Learning Agentic AI

**Version**: 1.0.0 | **Date**: 2026-02-25 | **Status**: 🚧 In Progress

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
- BigBrain (planned) detects patterns across multiple workflows
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
| Testing | pytest + pytest-cov | 7.4.0+ |
| Config | python-dotenv | 1.0.0+ |

## System Architecture

```
Layer 3: BRAIN (Intelligence)
    SmallBrain (per-workflow)     BigBrain (cross-workflow, planned)
         |                              |
         | reads logs                   | reads logs from ALL workflows
         | writes proposals             | writes system-wide proposals
         v                              v
    [proposals table]            [proposals table]
         |
         | human approves
         v

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
|   |   +-- __init__.py
|   +-- brain/                    Intelligence layer
|       +-- __init__.py           (SmallBrain lives in templates/)
|-- workflows/                    Production workflows
|   |-- ai_news_rss/              RSS -> Google Sheets
|   |-- etsy_analytics/           Etsy API -> analysis -> Sheets
|   |-- etsy_seo_optimizer/       Tag analysis -> Claude -> Sheets
|   |-- tattoo_trend_monitor/     Trends -> opportunities -> Sheets
|   +-- auto_listing_creator/     Trends -> content -> images -> Etsy
|-- templates/
|   +-- workflow_template/        Reference implementation
|       |-- orchestrator.py       SimpleOrchestrator class
|       |-- brain.py              SmallBrain class
|       |-- run.py                Entry point template
|       |-- config.py             Config template
|       |-- tools/                Example tool
|       +-- validators/           Example validator
|-- tests/                        pytest test suite
|-- scripts/                      Utility scripts
|   |-- init_db.py                Database initialization
|   +-- show_logs.py              HTML execution report generator
|-- data/                         SQLite database (gitignored)
|-- config.py                     Root-level configuration
|-- main.py                       API test script (demo only)
+-- requirements.txt              Python dependencies
```
