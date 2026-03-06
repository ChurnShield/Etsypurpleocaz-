# Configuration

**Version**: 1.0.0 | **Date**: 2026-02-25 | **Status**: 🚧 In Progress

> **Note**: This covers the configuration system and environment variables.
> For project-wide rules and conventions, see [CLAUDE.md](../../CLAUDE.md).
>
> **Cross-references**:
> - Workflows (per-workflow config): [docs/architecture/07-workflows.md](07-workflows.md)
> - Database: [docs/architecture/05-database.md](05-database.md)
> - Operations: [docs/architecture/10-operations.md](10-operations.md)

## Table of Contents

1. [Overview](#overview)
2. [Root config.py](#root-configpy)
3. [Workflow config.py Files](#workflow-configpy-files)
4. [Environment Variables](#environment-variables)
5. [LLM Client](#llm-client)

## Overview

Configuration is split between a root-level `config.py` (system-wide defaults) and per-workflow `config.py` files (workflow-specific settings). Secrets come from `.env` via python-dotenv.

### What it does

- Centralize all configuration values (API keys, thresholds, paths)
- Load secrets from `.env` file at runtime
- Provide per-workflow overrides for shared settings

### What it does NOT do

- Hot-reload configuration (requires restart)
- Validate configuration values at startup
- Support multiple environments (single .env file)

## Root config.py

**Location**: `config.py` (project root)

```python
import os
from dotenv import load_dotenv
load_dotenv()

# API
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

# Database
DATABASE_PATH = os.getenv("DATABASE_PATH", "data/system.db")

# Execution
DEFAULT_TIMEOUT_SECONDS = 120
MAX_RETRIES = 3

# SmallBrain
PROPOSAL_THRESHOLD_RUNS = 15
MIN_PATTERN_CONFIDENCE = 0.7

# BigBrain
BIG_BRAIN_MIN_WORKFLOWS = 2
BIG_BRAIN_MIN_RUNS_PER_WORKFLOW = 10
```

## Workflow config.py Files

Each workflow has its own `config.py` that overrides or extends root settings. The workflow's `run.py` imports from its local config (not the root):

```python
# In run.py, sys.path[0] = workflow dir, so this finds the LOCAL config:
from config import WORKFLOW_NAME, DATABASE_PATH, MAX_RETRIES, ...
```

### Common workflow config pattern

```python
import os
from dotenv import load_dotenv
load_dotenv()

WORKFLOW_NAME = "my_workflow"
DATABASE_PATH = "data/system.db"
MAX_RETRIES = 3

PROPOSAL_THRESHOLD_RUNS = 15
SLOW_TOOL_THRESHOLD_MS = 5000
MIN_PATTERN_CONFIDENCE = 0.7

# Workflow-specific
MY_API_KEY = os.getenv("MY_API_KEY", "")
```

## Environment Variables

**File**: `.env` (gitignored, never committed)
**Template**: `.env.example`

### Required variables

| Variable | Purpose |
|----------|---------|
| ANTHROPIC_API_KEY | Claude API key |

### Optional variables (with defaults)

| Variable | Default | Purpose |
|----------|---------|---------|
| ANTHROPIC_MODEL | claude-sonnet-4-20250514 | Claude model to use |
| DATABASE_PATH | data/system.db | SQLite database path |

### Etsy workflows

| Variable | Purpose |
|----------|---------|
| ETSY_API_KEYSTRING | Etsy API key string |
| ETSY_SHARED_SECRET | Etsy API shared secret |
| ETSY_SHOP_ID | Etsy shop ID (34071205) |

**Note**: Etsy API key header = `keystring:shared_secret` (combined in workflow config).

### Google Sheets

| Variable | Purpose |
|----------|---------|
| GOOGLE_CREDENTIALS_FILE | Path to service account JSON (default: google-credentials.json) |
| GOOGLE_SPREADSHEET_ID / ETSY_ANALYTICS_SPREADSHEET_ID | Target spreadsheet ID |

### RSS workflow

| Variable | Default | Purpose |
|----------|---------|---------|
| RSS_FEED_URL | TechCrunch AI feed | Primary RSS feed URL |
| LOOKBACK_HOURS | 24 | Filter articles from last N hours |

## LLM Client

**Location**: `lib/common_tools/llm_client.py`

Wraps the Anthropic Claude API with a simple function interface:

```python
from lib.common_tools.llm_client import call_llm

result = call_llm(
    prompt="Summarize this text",
    system="You are a helpful assistant",
    max_tokens=4096,
    temperature=0.7
)
# Returns:
# {
#     "success": bool,
#     "content": str,      # Response text
#     "usage": {
#         "input_tokens": int,
#         "output_tokens": int
#     },
#     "error": str | None
# }
```

Uses `ANTHROPIC_API_KEY` and `ANTHROPIC_MODEL` from root config.py.
Some workflow tools (SEO optimizer, trend monitor, auto listing creator) call the Anthropic API directly with their own config values instead of using `call_llm()`.
