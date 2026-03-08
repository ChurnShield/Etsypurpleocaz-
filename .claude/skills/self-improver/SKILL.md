---
name: self-improver
description: "Reviews and applies Brain system proposals for system optimization. Use when
              analyzing execution patterns, reviewing SmallBrain/BigBrain proposals, or
              checking system health metrics."
---

## Self-Improvement Protocol

When reviewing system health or Brain proposals:

1. Read `docs/architecture/06-brain.md` for the full Brain system documentation
2. Check system health via BigBrain before reviewing individual proposals
3. **NEVER auto-apply proposals** — always present them for human review

## Two-Layer Brain Architecture

### SmallBrain (Per-Workflow Learning)

**Location**: Each workflow's `brain.py` (template at `templates/workflow_template/brain.py`)

**What it does**:
- Analyzes execution logs from a single workflow after 15+ runs
- Detects per-workflow patterns:
  - Slow tools (threshold: 10s)
  - Repeated validation failures
  - Retry patterns
  - Error trends
- Generates workflow-specific proposals saved to `proposals/` directory

**Trigger**: Automatic after `PROPOSAL_THRESHOLD_RUNS` (default: 15) executions

### BigBrain (Cross-Workflow Learning)

**Location**: `lib/big_brain/`

**Components**:
- `brain.py` — System-wide health analysis engine
- `system_proposer.py` — Converts health findings into actionable proposals
- `hooks.py` — Integration points for automatic triggering

**Health Checks**:
- System failure rate (critical: >50%, degraded: >25%)
- Cross-workflow error patterns
- Performance degradation (>1.5x slower than baseline)
- Resource issues (database size >500MB)
- Timeout patterns (5+ in 24 hours)
- API key failures

**Proposal Categories**:
- `platform_optimization` — From high system failure rates
- `security_hardening` — From API key failures
- `infrastructure_upgrade` — From database or timeout issues

## Reviewing Proposals

1. Query proposals from `data/system.db` via SQLiteClient:
   ```python
   SQLiteClient().table("proposals").select("*").order("created_at", desc=True).execute()
   ```
2. Check proposal files in `proposals/` (workflow-specific) and `proposals/system/` (system-wide)
3. Evaluate each proposal against current system state
4. Present findings to the user with clear recommendation and rationale

## System Health Check

1. Run BigBrain health analysis across all workflows
2. Report: failure rate, slowest tools, most common errors, resource usage
3. Compare against thresholds in `config.py`:
   - `BIG_BRAIN_MIN_WORKFLOWS = 2`
   - `BIG_BRAIN_MIN_RUNS_PER_WORKFLOW = 10`
   - `BIG_BRAIN_CACHE_TTL_SECONDS = 300`
   - `MIN_PATTERN_CONFIDENCE = 0.7`

## Hard Rules

- **NEVER auto-apply proposals** — human-in-the-loop is mandatory
- NEVER skip `logger.flush()` in the finally block
- NEVER modify `lib/orchestrator/` base classes based on proposals
- NEVER modify `config.py` or `scripts/init_db.py` without explicit permission
- Always use `SQLiteClient` for querying execution logs and proposals
- Proposals need 15+ workflow runs (SmallBrain) or 10+ per workflow (BigBrain) before generation
- Present proposals with confidence scores and supporting data
