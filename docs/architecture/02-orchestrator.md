# Orchestrator & ExecutionLogger

**Version**: 1.0.0 | **Date**: 2026-02-25 | **Status**: 🚧 In Progress

> **Note**: This covers the execution engine and logging system.
> For project-wide rules and conventions, see [CLAUDE.md](../../CLAUDE.md).
>
> **Cross-references**:
> - Tool patterns: [docs/architecture/03-tool-patterns.md](03-tool-patterns.md)
> - Validator patterns: [docs/architecture/04-validator-patterns.md](04-validator-patterns.md)
> - Database schema: [docs/architecture/05-database.md](05-database.md)

## Table of Contents

1. [Overview](#overview)
2. [SimpleOrchestrator](#simpleorchestrator)
3. [ExecutionLogger](#executionlogger)
4. [The _run_phase Pattern](#the-_run_phase-pattern)
5. [Execution Flow](#execution-flow)
6. [Configuration](#configuration)
7. [Common Issues](#common-issues)

## Overview

The Orchestrator layer is the mechanical worker. It runs plans, logs every action, and retries on failure. It does not decide what to run or learn from results.

### What it does

- Runs a list of steps (tool + validator + retry logic)
- Logs phase_start, phase_end, tool_call, tool_result, validation_event to DB
- Buffers log events in memory and flushes to DB in a finally block
- Records execution start/end in the executions table

### What it does NOT do

- Decide what workflow to run (that comes from run.py)
- Learn or propose improvements (that is SmallBrain's job)
- Handle workflow-specific business logic

## SimpleOrchestrator

**Location**: `templates/workflow_template/orchestrator.py`

Used by the template workflow. Most production workflows use `_run_phase()` directly instead (see below).

```python
class SimpleOrchestrator:
    def __init__(self, workflow_id: str, execution_id: str, db):
        self.logger = ExecutionLogger(execution_id, workflow_id, db)

    def run(self, plan: list) -> dict:
        """
        plan: list of dicts with keys:
            "phase"     : str           -- logged to DB
            "tool"      : BaseTool      -- called with execute(**params)
            "params"    : dict          -- forwarded to tool.execute()
            "validator" : BaseValidator  -- checks tool output (optional)
        Returns: {"success": bool, "execution_id": str}
        """
```

### Execution Flow (SimpleOrchestrator)

1. `_record_execution_start()` -- inserts row in `executions` table with status='running'
2. For each step in plan:
   - `logger.phase_start(phase_name)`
   - `logger.tool_call(tool_name, params)`
   - `tool.execute(**params)` -- returns standard dict
   - `logger.tool_result(tool_name, result, success, duration_ms)`
   - If validator: `validator.validate(data)` then `logger.validation_event(...)`
   - Retry if `needs_more=True` and attempts remaining
   - `logger.phase_end(phase_name, success)`
3. `_record_execution_end(success)` -- updates executions row
4. **CRITICAL**: `logger.flush()` in finally block

## ExecutionLogger

**Location**: `lib/orchestrator/execution_logger.py`

Buffers log events in memory (`_buffer` list) and writes them all to `execution_logs` table when `flush()` is called.

### API

| Method | When to call | What it logs |
|--------|-------------|--------------|
| `phase_start(name)` | Beginning of a logical phase | event_type="phase_start" |
| `phase_end(name, success)` | End of a logical phase | event_type="phase_end" |
| `tool_call(name, params)` | Before calling a tool | event_type="tool_call" |
| `tool_result(name, result, success, duration_ms)` | After tool returns | event_type="tool_result" |
| `validation_event(name, passed, issues)` | After validator runs | event_type="validation" |
| `error(message, metadata)` | On unexpected errors | event_type="error" |
| `flush()` | **ALWAYS in finally block** | Writes buffer to DB |

### Log Entry Structure

Each buffered event is a dict written to `execution_logs`:

```python
{
    "id": str,              # UUID
    "execution_id": str,    # Links to executions table
    "workflow_id": str,     # Which workflow
    "timestamp": str,       # ISO 8601 UTC
    "phase": str,           # Current phase name
    "event_type": str,      # phase_start|phase_end|tool_call|tool_result|validation|error
    "tool_name": str,       # Which tool (if applicable)
    "validator_name": str,  # Which validator (if applicable)
    "success": bool,        # Pass/fail
    "duration_ms": int,     # Tool execution time (tool_result only)
    "metadata": str,        # JSON string of extra data
    "error_message": str    # Error details (error events only)
}
```

## The _run_phase Pattern

Production workflows (ai_news_rss, etsy_analytics, etc.) use `_run_phase()` directly instead of SimpleOrchestrator. This gives more control over data chaining between phases.

```python
def _run_phase(logger, phase_name: str, tool, params: dict,
               validator=None, max_retries: int = MAX_RETRIES) -> dict:
    """
    Execute one pipeline phase: log, call tool, validate, retry.
    Returns the tool result dict on success, or failure dict.
    """
```

### Why _run_phase instead of SimpleOrchestrator?

SimpleOrchestrator runs independent steps. Most workflows are **pipelines** where Phase 1 output feeds into Phase 2:

```
Phase 1 (Fetch) -> articles list
                        |
Phase 2 (Filter) -> recent articles list
                        |
Phase 3 (Save)  -> Google Sheet rows
```

`_run_phase()` lets you capture each result and pass it to the next phase.

### Key behavior in _run_phase

- Compacts large params for logging (replaces lists with `[N items]`)
- Never logs secrets (`api_key` params are excluded)
- Returns standard failure dict if all retries exhausted

## Configuration

| Setting | Source | Default | Purpose |
|---------|--------|---------|---------|
| MAX_RETRIES | workflow config.py | 3 | Max attempts per phase |
| DEFAULT_TIMEOUT_SECONDS | root config.py | 120 | Not enforced in orchestrator yet |

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| No logs in execution_logs after run | Missing `logger.flush()` in finally block | Add `try/finally` with `logger.flush()` |
| SmallBrain sees incomplete data | Exception before `flush()` without finally | Ensure flush is in finally, not in try |
| Phase shows success=False but tool succeeded | Validator returned `passed=False` | Check validator thresholds |
| Duplicate execution_id | UUID collision (extremely rare) | Rerun -- uuid4 collisions are near-impossible |
