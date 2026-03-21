---
name: review
description: "Active during listing quality audits, architecture decisions, pipeline health checks. Critical, thorough, evidence-required."
type: context
---

# Review Context

Mode: Quality audit, architecture review, pipeline health check
Focus: Critical eye — flag everything, approve nothing without evidence

## Behaviour

- Read thoroughly before commenting.
- Quality over speed. Take the time to check properly.
- Never approve without evidence (screenshot, API response, test output).
- Prioritise issues by severity: CRITICAL > HIGH > MEDIUM > LOW.
- Flag both problems AND things that look correct (explicit confirmation).
- If something can't be verified automatically, say so and suggest manual check.

## Priorities

1. Find problems before they reach customers
2. Confirm what's working with evidence
3. Recommend specific fixes (not vague suggestions)

## Rules Enforced

All 7 rule files are active and enforced:

- `.claude/rules/canva.md` — verify delivery links are `/d/` format, transactions committed
- `.claude/rules/etsy.md` — verify tags < 20 chars, no duplicates, price correct, images ranked
- `.claude/rules/pipeline.md` — verify image sources match standard, hero thumbnail correct
- `.claude/rules/database.md` — verify SQLiteClient usage, no raw sqlite3
- `.claude/rules/security.md` — verify no hardcoded keys, protected files unchanged
- `.claude/rules/testing.md` — verify tests pass, coverage adequate
- `.claude/rules/tool-conventions.md` — verify BaseTool/BaseValidator contracts, logger.flush()

## Agent Sequence

1. **Verifier** — primary agent for all review work
2. Other agents only if verifier finds issues that need deeper investigation

## Review Checklist

### Listing Review
- [ ] All images present and correctly ranked (GET /listings/{id}/images)
- [ ] PDF attached with correct filename (GET /shops/{id}/listings/{id}/files)
- [ ] Tags: all under 20 chars, no duplicates, 13 total
- [ ] Price: £2.99 (or bundle price if flagged)
- [ ] Delivery PDF links: all `/d/` format, all clickable
- [ ] Title and description match provided copy verbatim
- [ ] State: active or draft as expected

### Pipeline Health Review
- [ ] All tests passing (`pytest tests/ -v`)
- [ ] No hardcoded credentials in recent commits
- [ ] Protected files unchanged
- [ ] Database schema consistent with init_db.py
- [ ] Config values loaded from config.py, not hardcoded

### Architecture Review
- [ ] Tools extend BaseTool, validators extend BaseValidator
- [ ] ExecutionLogger with try/finally and logger.flush()
- [ ] Error paths return error dicts, never raise
- [ ] No Brain proposals auto-applied

## Output Format

```
## Review: {subject}

### CRITICAL
- {issue with evidence}

### HIGH
- {issue with evidence}

### MEDIUM
- {issue with evidence}

### CONFIRMED OK
- {thing verified} — evidence: {API response / test output / screenshot}

### CANNOT VERIFY
- {thing that needs manual check} — reason: {why}
```

## Tools to Favour

- Bash for verify_listing.py, pytest, git diff, API GET calls
- Read for inspecting files and configs
- Grep for searching for hardcoded values or pattern violations

## Tools to Avoid

- Write, Edit (review mode doesn't change things — only reports)
- Canva MCP editing tools (review, don't modify)
