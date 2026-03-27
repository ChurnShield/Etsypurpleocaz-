---
name: workflow-runner
description: "Runs and debugs orchestrated workflows. Use when executing pipeline phases,
              diagnosing workflow failures, or checking execution logs."
requires:
  - rules/tool-conventions.md
---

# Workflow Runner

## Execution Protocol

1. Read the workflow's `config.py` and `__init__.py` to understand its phases
2. Check `docs/architecture/07-workflows.md` for the workflow pattern
3. Verify all required environment variables are set in `.env`
4. Run via `python main.py` or the workflow-specific entry point

## Debugging Failed Workflows

1. Check execution logs in `data/system.db` via SQLiteClient
2. Look for missing `logger.flush()` — most common cause of silent failures (see `rules/tool-conventions.md`)
3. Check the tool's return dict for `{success: false, error: ...}`
4. Review `docs/architecture/10-operations.md` for common failure patterns

## Pipeline Phase Order

```
Phase 1  -> Load opportunities from Trend Monitor
Phase 2  -> Generate listing content (anti-gravity keyword engine)
Phase 2b -> Auto-bundle creation
Phase 3  -> Create product images (Tier 1: Gemini AI / Tier 2: HTML)
Phase 4  -> Publish to Sheets + Etsy drafts + upload images/PDFs
Phase 5  -> verify_listing.py — automated verification
```

## Hard Rules

- NEVER skip `logger.flush()` in finally blocks — see `rules/tool-conventions.md`
- NEVER auto-apply Brain proposals — present them for human review
- Always check tool return values for `success: false` before proceeding
