# Brain -- Learning System

**Version**: 1.1.0 | **Date**: 2026-02-25 | **Status**: Active

> **Note**: This covers both SmallBrain (per-workflow) and BigBrain (cross-workflow) learning systems.
> For project-wide rules and conventions, see [CLAUDE.md](../../CLAUDE.md).
>
> **Cross-references**:
> - Orchestrator (generates logs): [docs/architecture/02-orchestrator.md](02-orchestrator.md)
> - Database (stores logs/proposals): [docs/architecture/05-database.md](05-database.md)
> - Configuration (thresholds): [docs/architecture/08-configuration.md](08-configuration.md)

## Table of Contents

1. [Overview](#overview)
2. [SmallBrain](#smallbrain)
3. [Analysis Patterns](#analysis-patterns)
4. [Proposal Format](#proposal-format)
5. [BigBrain](#bigbrain)
6. [Configuration](#configuration)

## Overview

The Brain layer reads execution logs and identifies improvement patterns. SmallBrain operates per-workflow. BigBrain operates cross-workflow.

### What it does

- Analyse execution logs after sufficient runs accumulate (15+ by default)
- Detect validators with high failure rates
- Detect tools with consistently slow execution
- Save proposals to the proposals table for human review

### What it does NOT do

- Modify workflows automatically (human-in-the-loop enforced)
- Run during execution (runs after each workflow completes)
- Access external APIs (reads only from the local database)

## SmallBrain

**Location**: `templates/workflow_template/brain.py`

SmallBrain is a generic class used by all workflows. It is imported from the template:

```python
from templates.workflow_template.brain import SmallBrain

brain = SmallBrain(workflow_id="etsy_analytics", db=db)
proposals = brain.analyze()  # Returns list of proposal dicts
```

### Execution Flow

1. Count total runs for this workflow
2. If runs < `PROPOSAL_THRESHOLD_RUNS` (default 15): return early (not enough data)
3. Run `_analyze_validators()`: find validators failing 70%+ of the time
4. Run `_analyze_slow_tools()`: find tools exceeding threshold 70%+ of the time
5. Save each proposal to the proposals table with status="pending"
6. Return list of proposals generated

### When SmallBrain runs

Every workflow's `run.py` calls SmallBrain after the main execution completes:

```python
# Step 8 in every run.py
try:
    from templates.workflow_template.brain import SmallBrain
    brain = SmallBrain(workflow_id=WORKFLOW_NAME, db=db)
    proposals = brain.analyze()
except Exception as brain_err:
    print(f"SmallBrain skipped: {brain_err}")
```

SmallBrain failures are non-fatal -- the workflow result is not affected.

## Analysis Patterns

### 1. Validator Failure Rate

Queries `execution_logs` where `event_type="validation"` for this workflow. Groups by `validator_name` and computes pass/fail rate.

**Triggers proposal when**: `fail_rate >= MIN_PATTERN_CONFIDENCE` (default 0.7 = 70%)

```python
# Example: if ExampleValidator fails 80% of the time
proposal = {
    "proposal_type": "validator_improvement",
    "title": "High failure rate in ExampleValidator",
    "description": "ExampleValidator fails 80% of the time (8 of 10 checks)...",
    "pattern_data": {
        "validator_name": "ExampleValidator",
        "pass_rate": 0.2,
        "fail_rate": 0.8,
        "total_checks": 10
    },
    "proposed_changes": {
        "action": "review_validator",
        "target": "ExampleValidator",
        "suggestion": "Review validation thresholds or improve the upstream tool."
    }
}
```

### 2. Slow Tool Detection

Queries `execution_logs` where `event_type="tool_result"` for this workflow. Groups by `tool_name` and checks `duration_ms` against `SLOW_TOOL_THRESHOLD_MS`.

**Triggers proposal when**: Tools exceed threshold 70%+ of the time.

```python
# Example: if FetchRSSTool is slow 75% of the time
proposal = {
    "proposal_type": "performance_improvement",
    "title": "Slow execution detected in FetchRSSTool",
    "description": "FetchRSSTool exceeds 5000ms 75% of the time (avg: 8500ms)...",
    "pattern_data": {
        "tool_name": "FetchRSSTool",
        "avg_duration_ms": 8500,
        "slow_rate": 0.75,
        "threshold_ms": 5000
    },
    "proposed_changes": {
        "action": "optimise_tool",
        "target": "FetchRSSTool",
        "suggestion": "Add caching, reduce API round-trips, or run slow operations in parallel."
    }
}
```

## Proposal Format

Proposals are stored in the `proposals` table as:

| Field | Value |
|-------|-------|
| id | UUID |
| workflow_id | Which workflow |
| status | "pending" (human must change to "approved" or "rejected") |
| proposal_type | "validator_improvement" or "performance_improvement" |
| pattern_data | JSON string with analysis details |
| proposed_changes | JSON string with suggested action |

## BigBrain

**Location**: `lib/big_brain/brain.py`

BigBrain analyses execution logs across ALL workflows and detects system-wide health problems, cross-workflow patterns, and critical alerts. It never modifies workflows -- it only reads logs and writes proposals (human-in-the-loop).

```python
from lib.big_brain.brain import BigBrain
from lib.common_tools.sqlite_client import get_client

db = get_client()
brain = BigBrain(workflows_dir="workflows", db_client=db)

# Full analysis (health + patterns + alerts + proposals)
result = brain.analyze()
print(f"Status: {result['status']}, {result['proposals_saved']} proposals")

# Health check only
health = brain.analyze_system_health()
print(f"System: {health.status}, {health.total_executions_24h} executions")

# Cross-workflow patterns only
patterns = brain.detect_cross_workflow_patterns()
print(f"Found {len(patterns)} cross-workflow patterns")
```

### Preconditions

- At least `BIG_BRAIN_MIN_WORKFLOWS` (2) workflows must have `BIG_BRAIN_MIN_RUNS_PER_WORKFLOW` (10) runs each before `analyze()` produces results. Otherwise returns `status: "insufficient_data"`.

### Workflow Discovery

`discover_workflows()` scans the `workflows/` directory for subdirectories containing `run.py`. Returns a dict of `workflow_id -> WorkflowInfo` dataclass.

### System Health Analysis (15 checks)

`analyze_system_health()` runs 3 DB queries upfront (execution_logs, executions, workflows for last 24h), then evaluates 15 health checks in Python:

| # | Check | Severity | Trigger |
|---|-------|----------|---------|
| 1 | System-wide failure rate | critical/high | >50% / >25% |
| 2 | Multiple workflows failing | critical/high | 3+ / 2+ at >80% failure |
| 3 | Performance degradation | medium | 1.5x slower than baseline |
| 4 | Recurring errors | high | Same error 10+ times in 24h |
| 5 | Database size | high/medium | >90% / >75% of 500MB limit |
| 6 | API key failures | high | >3 auth errors in 24h |
| 7 | Unauthorized access | critical | Security keywords detected |
| 8 | Data corruption | critical | Corruption keywords detected |
| 9 | Memory usage | critical/high | >95% / >90% |
| 10 | Disk space | critical/high | >95% / >90% |
| 11 | Database connections | critical | Lock/IO error keywords |
| 12 | System crashes | critical | Crash/fatal keywords |
| 13 | Data loss | critical | Data loss keywords |
| 14 | Validation trends | medium | Failure rate up 20%+ (12h vs 12h) |
| 15 | Timeout patterns | medium | 5+ timeouts in 24h |

Results are cached for 5 minutes (`BIG_BRAIN_CACHE_TTL_SECONDS`).

### Cross-Workflow Pattern Detection (5 detectors)

`detect_cross_workflow_patterns()` finds issues affecting 3+ workflows:

| Detector | Pattern | Severity |
|----------|---------|----------|
| Common errors | Same error message in 3+ workflows | high |
| Performance | 30%+ slow tools in 3+ workflows | medium |
| Infrastructure | Network/connection errors in 3+ workflows | high |
| Resource contention | Rate limits/locks in 3+ workflows | high |
| Security | Auth failures in 3+ workflows | critical |

### Proposals

System-wide proposals use `workflow_id=None` in the proposals table. Same `_save_proposal()` pattern as SmallBrain (uuid, json.dumps, status="pending"). Only high/critical severity patterns and critical alerts generate proposals.

### SystemProposer

**Location**: `lib/big_brain/system_proposer.py`

SystemProposer converts BigBrain health results into rich, actionable proposals that are saved to both the database and markdown files in `proposals/system/`.

```python
from dataclasses import asdict
health = brain.analyze_system_health()
proposals = brain.proposer.generate_proposals_from_health(asdict(health))
```

**Proposal types** (mapped from problem categories):

| Proposal Type | Covers |
|---------------|--------|
| platform_optimization | System failure rate, performance degradation, validation trends |
| cross_workflow_fix | Multiple workflow failures, recurring errors |
| resource_management | Database size, memory usage, disk space |
| security_hardening | API key failures, unauthorized access |
| infrastructure_upgrade | Data corruption, DB connections, crashes, data loss, timeouts |

Each proposal includes:
- Database record (`proposals` table, `workflow_id=NULL`, `status="pending"`)
- Markdown file (`proposals/system/proposal_YYYYMMDD_HHMMSS_<uuid8>.md`) with: issue description, evidence, recommendation, changes checklist, expected impact, review instructions

### Tests

- 10 tests in `tests/test_big_brain.py` -- workflow discovery, empty dir, insufficient data, healthy system, critical failure rate, recurring errors, cross-workflow patterns, proposal saving, cache behavior, alert generation
- 11 tests in `tests/test_system_proposer.py` -- healthy no-op, degraded/critical generation, DB persistence, markdown file output, content structure, type mapping, affected workflow extraction, unknown category skipping, checklist generation, BigBrain integration

## Configuration

| Setting | Source | Default | Purpose |
|---------|--------|---------|---------|
| PROPOSAL_THRESHOLD_RUNS | workflow config.py | 15 | Min runs before SmallBrain analysis |
| MIN_PATTERN_CONFIDENCE | workflow config.py | 0.7 | Min rate to trigger proposal (70%) |
| SLOW_TOOL_THRESHOLD_MS | workflow config.py | 5000-10000 | Slow tool threshold (varies by workflow) |
| BIG_BRAIN_MIN_WORKFLOWS | root config.py | 2 | Min workflows for BigBrain |
| BIG_BRAIN_MIN_RUNS_PER_WORKFLOW | root config.py | 10 | Min runs per workflow for BigBrain |
| BIG_BRAIN_CACHE_TTL_SECONDS | root config.py | 300 | Health metrics cache lifetime |
| BIG_BRAIN_FAILURE_RATE_CRITICAL | root config.py | 0.50 | Critical failure threshold |
| BIG_BRAIN_FAILURE_RATE_DEGRADED | root config.py | 0.25 | Degraded failure threshold |
| BIG_BRAIN_RECURRING_ERROR_THRESHOLD | root config.py | 10 | Recurring error count threshold |
| BIG_BRAIN_TIMEOUT_THRESHOLD | root config.py | 5 | Timeout count threshold |
| BIG_BRAIN_DB_MAX_SIZE_MB | root config.py | 500 | Database size limit for alerts |
| BIG_BRAIN_PERF_DEGRADATION_FACTOR | root config.py | 1.5 | Performance degradation multiplier |
