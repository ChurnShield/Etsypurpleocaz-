# Workflows

**Version**: 1.0.0 | **Date**: 2026-02-25 | **Status**: 🚧 In Progress

> **Note**: This covers workflow structure, existing workflows, and how to add new ones.
> For project-wide rules and conventions, see [CLAUDE.md](../../CLAUDE.md).
>
> **Cross-references**:
> - Tool patterns: [docs/architecture/03-tool-patterns.md](03-tool-patterns.md)
> - Validator patterns: [docs/architecture/04-validator-patterns.md](04-validator-patterns.md)
> - Orchestrator: [docs/architecture/02-orchestrator.md](02-orchestrator.md)

## Table of Contents

1. [Overview](#overview)
2. [Structure](#structure)
3. [Configuration](#configuration)
4. [Execution Sequence](#execution-sequence)
5. [Existing Workflows](#existing-workflows)
6. [Adding a New Workflow](#adding-a-new-workflow)

## Overview

Workflows are self-contained pipelines that fetch data, transform it, and save results. Each workflow has its own tools, validators, config, and entry point.

### What it does

- Execute multi-phase pipelines (typically 3-4 phases)
- Chain phase outputs: Phase 1 result feeds into Phase 2
- Log every action for SmallBrain analysis
- Save results to Google Sheets or Etsy API

### What it does NOT do

- Share tools between workflows (each workflow has its own tools/)
- Run on a schedule (manually triggered via `python workflows/*/run.py`)
- Depend on other workflows at runtime (auto_listing_creator reads saved data, not live output)

## Structure

Every workflow follows this directory layout:

```
workflows/<workflow_name>/
|-- __init__.py
|-- config.py           Workflow-specific settings
|-- run.py              Entry point (python workflows/<name>/run.py)
|-- tools/
|   |-- __init__.py
|   |-- <tool_1>.py     Extends BaseTool
|   +-- <tool_2>.py
+-- validators/
    |-- __init__.py
    |-- <validator_1>.py  Extends BaseValidator
    +-- <validator_2>.py
```

### Path Setup Pattern

Every `run.py` starts with this boilerplate:

```python
_here = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(_here))
sys.path.insert(0, _here)          # workflow-local imports
sys.path.insert(1, _project_root)  # lib/ imports
```

`_here` is inserted first so `from config import ...` finds the **workflow's** config.py, not the root config.py.

## Configuration

Each workflow has its own `config.py` with:

```python
# Required in every workflow config.py
WORKFLOW_NAME = "my_workflow"           # Used as ID in workflows table
DATABASE_PATH = "data/system.db"       # Same DB for all workflows
MAX_RETRIES = 3                        # Per-phase retry limit

# SmallBrain settings
PROPOSAL_THRESHOLD_RUNS = 15
SLOW_TOOL_THRESHOLD_MS = 5000
MIN_PATTERN_CONFIDENCE = 0.7

# Workflow-specific settings (API keys, sheet names, etc.)
```

## Execution Sequence

Every `run.py` follows this sequence:

```
[1] Connect to SQLite DB
[2] Register workflow (first run only, idempotent)
[3] Create execution_id (UUID)
[4] Insert executions row (status="running")
[5] Create ExecutionLogger
[6] try:
        Phase 1: _run_phase(logger, tool, params, validator)
        Phase 2: _run_phase(logger, tool, params, validator)  -- uses Phase 1 output
        Phase 3: _run_phase(logger, tool, params, validator)  -- uses Phase 2 output
        Update executions row (status="completed" or "failed")
    except:
        logger.error(str(exc))
        Update executions row (status="failed")
    finally:
        logger.flush()       <-- CRITICAL
[7] Update workflow stats (total_runs, successful_runs, etc.)
[8] SmallBrain.analyze() (non-fatal if it fails)
[9] Print summary
```

## Existing Workflows

### ai_news_rss

**Purpose**: Fetch AI news from RSS feeds and save to Google Sheets.

| Phase | Tool | Validator |
|-------|------|-----------|
| 1. Fetch RSS | FetchRSSTool | ArticlesFetchedValidator |
| 2. Filter recent | FilterRecentTool | ValidDatesValidator |
| 3. Save to Sheets | SaveToGoogleSheetsTool | GoogleSheetsSaveValidator |

**Run**: `python workflows/ai_news_rss/run.py`

### etsy_analytics

**Purpose**: Fetch all Etsy listings, analyze performance, save dashboard to Google Sheets.

| Phase | Tool | Validator |
|-------|------|-----------|
| 1. Fetch listings | FetchEtsyDataTool | ListingsFetchedValidator |
| 2. Analyze performance | AnalyzePerformanceTool | AnalysisValidator |
| 3. Save to Sheets | SaveAnalyticsTool | AnalyticsSavedValidator |

**Run**: `python workflows/etsy_analytics/run.py`
**Extra**: `run_triage.py` for listing triage scoring.

### etsy_seo_optimizer

**Purpose**: Scan listing tags, identify SEO problems, generate optimized tags via Claude.

| Phase | Tool | Validator |
|-------|------|-----------|
| 1. Analyze tags | AnalyzeTagsTool | TagAnalysisValidator |
| 2. Generate tags (Claude) | GenerateTagsTool | TagsGeneratedValidator |
| 3. Save report | SaveSeoReportTool | ReportSavedValidator |

**Run**: `python workflows/etsy_seo_optimizer/run.py`

### tattoo_trend_monitor

**Purpose**: Track Google Trends + Etsy competitors to find product opportunities.

| Phase | Tool | Validator |
|-------|------|-----------|
| 1. Fetch trends | FetchTrendsTool | TrendsFetchedValidator |
| 2. Analyse opportunities | AnalyseOpportunitiesTool | OpportunitiesValidator |
| 3. Save report | SaveTrendsReportTool | ReportSavedValidator |

**Run**: `python workflows/tattoo_trend_monitor/run.py`

### auto_listing_creator

**Purpose**: End-to-end: load opportunities -> generate content -> create images -> publish to Etsy.

| Phase | Tool | Validator |
|-------|------|-----------|
| 1. Load opportunities | LoadOpportunitiesTool | OpportunitiesLoadedValidator |
| 2. Generate content (Claude) | GenerateListingContentTool | ContentGeneratedValidator |
| 3. Create images (Playwright) | ProductCreatorTool | (inline check) |
| 4. Publish listings | PublishListingsTool | ListingsPublishedValidator |

**Run**: `python workflows/auto_listing_creator/run.py`
**Note**: Phase 3 uses HTML templates rendered to PNG via Playwright, not Canva API.

## Adding a New Workflow

1. **Copy the template**: `cp -r templates/workflow_template workflows/<new_name>`
2. **Edit config.py**: Set `WORKFLOW_NAME = "<new_name>"` and add workflow-specific settings
3. **Create tools**: Add tool files in `tools/`, each extending `BaseTool`
4. **Create validators**: Add validator files in `validators/`, each extending `BaseValidator`
5. **Edit run.py**: Import your tools/validators, define the phase pipeline
6. **Test**: Run `python workflows/<new_name>/run.py`
7. **Verify logs**: `python scripts/show_logs.py <new_name> --last 1`

### Template files to modify

| File | What to change |
|------|---------------|
| config.py | WORKFLOW_NAME, add API keys/settings |
| run.py | Import your tools/validators, define phases |
| tools/example_tool.py | Replace with your tool (or delete and create new) |
| validators/example_validator.py | Replace with your validator |
| orchestrator.py | Usually no changes needed |
| brain.py | Usually no changes needed |
