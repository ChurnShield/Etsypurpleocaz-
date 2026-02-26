# Operations & Debugging

**Version**: 1.0.0 | **Date**: 2026-02-25 | **Status**: 🚧 In Progress

> **Note**: This covers running workflows, debugging, and system maintenance.
> For project-wide rules and conventions, see [CLAUDE.md](../../CLAUDE.md).
>
> **Cross-references**:
> - Workflows: [docs/architecture/07-workflows.md](07-workflows.md)
> - Database: [docs/architecture/05-database.md](05-database.md)
> - Configuration: [docs/architecture/08-configuration.md](08-configuration.md)

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Running the System](#running-the-system)
4. [Debugging](#debugging)
5. [Monitoring](#monitoring)
6. [Troubleshooting](#troubleshooting)

## Overview

The system runs as CLI scripts. Each workflow is executed manually via `python workflows/<name>/run.py`. No web server, scheduler, or daemon is involved.

### What it does

- Run individual workflows from the command line
- Generate HTML debug reports from execution logs
- Query the database for execution history and proposals

### What it does NOT do

- Run on a schedule (no cron, no systemd)
- Serve a web interface
- Send alerts or notifications on failure

## Prerequisites

1. Python 3.10+ installed
2. Dependencies: `pip install -r requirements.txt`
3. `.env` file with required API keys (copy from `.env.example`)
4. Database initialized: `python scripts/init_db.py`
5. Google credentials: `google-credentials.json` in project root
6. Etsy OAuth tokens: Run `python workflows/etsy_analytics/etsy_oauth.py` once

## Running the System

### First-time setup

```shell
pip install -r requirements.txt
cp .env.example .env        # Edit with your API keys
python scripts/init_db.py   # Create database
```

### Running workflows

```shell
# Each workflow is independent -- run any one:
python workflows/ai_news_rss/run.py
python workflows/etsy_analytics/run.py
python workflows/etsy_seo_optimizer/run.py
python workflows/tattoo_trend_monitor/run.py
python workflows/auto_listing_creator/run.py

# Template (demo/test):
python templates/workflow_template/run.py

# Etsy analytics triage:
python workflows/etsy_analytics/run_triage.py
```

Each workflow prints a numbered step log and a final SUCCESS/FAILED summary.

## Debugging

### show_logs.py -- HTML execution report

```shell
python scripts/show_logs.py <workflow_name> --last <N>
```

Generates an HTML report with:
- Execution summary (status, duration, timestamps)
- Collapsible event details (phases, tool calls, validations)
- Color-coded rows by event type (blue=phase, amber=tool_call, green=success, red=fail)

### Direct database queries

```shell
# Recent executions for a workflow
sqlite3 data/system.db "SELECT id, status, started_at FROM executions WHERE workflow_id='etsy_analytics' ORDER BY started_at DESC LIMIT 5;"

# Execution logs for a specific run
sqlite3 data/system.db "SELECT event_type, tool_name, success, error_message FROM execution_logs WHERE execution_id='<UUID>' ORDER BY timestamp;"

# Pending proposals
sqlite3 data/system.db "SELECT workflow_id, title, description FROM proposals WHERE status='pending';"

# Workflow stats
sqlite3 data/system.db "SELECT id, total_runs, successful_runs, failed_runs FROM workflows;"
```

## Monitoring

### Key metrics to check

| Metric | Query |
|--------|-------|
| Success rate | `SELECT successful_runs * 100.0 / total_runs FROM workflows WHERE id='...'` |
| Recent failures | `SELECT * FROM executions WHERE status='failed' ORDER BY started_at DESC LIMIT 5` |
| Slow tools | `SELECT tool_name, AVG(duration_ms) FROM execution_logs WHERE event_type='tool_result' GROUP BY tool_name` |
| Pending proposals | `SELECT COUNT(*) FROM proposals WHERE status='pending'` |

### Database backup

```shell
cp data/system.db data/system_backup_$(date +%Y%m%d).db
```

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `ModuleNotFoundError: No module named 'lib'` | Project root not on sys.path | Check `_project_root` setup in run.py |
| `ModuleNotFoundError: No module named 'config'` | Wrong config.py resolved | Check sys.path order (`_here` must be index 0) |
| Workflow runs but no logs in DB | Missing `logger.flush()` | Add try/finally with `logger.flush()` |
| Etsy API returns 401 | API key format wrong | Must be `keystring:shared_secret` in x-api-key header |
| Etsy API returns 403 | OAuth token expired | Re-run `python workflows/etsy_analytics/etsy_oauth.py` |
| Google Sheets permission error | Service account not shared | Share spreadsheet with service account email |
| SmallBrain says "Need N more runs" | Not enough data yet | Run workflow more times to accumulate data |
| `sqlite3.OperationalError: database is locked` | Concurrent writes | Ensure only one workflow runs at a time |
| Unicode errors in print() | Windows terminal encoding | Use ASCII alternatives, avoid emoji in print() |
