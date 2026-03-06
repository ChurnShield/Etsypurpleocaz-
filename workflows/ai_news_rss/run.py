# =============================================================================
# workflows/ai_news_rss/run.py
#
# Entry point for the AI News RSS workflow.
#
#   python workflows/ai_news_rss/run.py
#
# Why this workflow does NOT use SimpleOrchestrator
# --------------------------------------------------
# SimpleOrchestrator (from the template) runs a list of independent steps.
# This workflow is a PIPELINE — each phase feeds its output into the next:
#
#     Phase 1 (Fetch) → articles list
#                           ↓
#     Phase 2 (Filter) → recent articles list
#                           ↓
#     Phase 3 (Save)  → Google Sheet rows
#
# Instead we use ExecutionLogger directly, which is what CLAUDE.md Pattern 1
# shows.  A small helper function `_run_phase()` handles the retry logic and
# logging for each phase, keeping the main() function readable.
#
# The critical rule still applies: logger.flush() MUST be in a finally block.
# =============================================================================

import sys
import os
import uuid
import time
from datetime import datetime

# ---------------------------------------------------------------------------
# Path setup — MUST happen before any other local imports
# ---------------------------------------------------------------------------
# run.py lives at: workflows/ai_news_rss/run.py
#   dirname(_here) → workflows/
#   dirname(dirname(_here)) → project root  ✅
#
# _here is inserted FIRST so "from config import ..." finds THIS workflow's
# config.py, not the root-level config.py.
# ---------------------------------------------------------------------------
_here = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(_here))

sys.path.insert(0, _here)          # workflow-local imports (config, tools, …)
sys.path.insert(1, _project_root)  # lib/ imports

# ---------------------------------------------------------------------------
# Imports — workflow config
# ---------------------------------------------------------------------------
from config import (
    WORKFLOW_NAME,
    DATABASE_PATH,
    MAX_RETRIES,
    RSS_FEED_URL,
    RSS_FEED_URLS,
    LOOKBACK_HOURS,
    GOOGLE_CREDENTIALS_FILE,
    GOOGLE_SPREADSHEET_ID,
    GOOGLE_SHEET_NAME,
    PROPOSAL_THRESHOLD_RUNS,
)

# ---------------------------------------------------------------------------
# Imports — project infrastructure
# ---------------------------------------------------------------------------
from lib.common_tools.sqlite_client import SQLiteClient
from lib.orchestrator.execution_logger import ExecutionLogger

# ---------------------------------------------------------------------------
# Imports — this workflow's tools and validators
# ---------------------------------------------------------------------------
from tools.fetch_rss_tool              import FetchRSSTool
from tools.filter_recent_tool          import FilterRecentTool
from tools.save_to_google_sheets_tool       import SaveToGoogleSheetsTool

from validators.articles_fetched_validator  import ArticlesFetchedValidator
from validators.valid_dates_validator       import ValidDatesValidator
from validators.google_sheets_save_validator import GoogleSheetsSaveValidator


# =============================================================================
# Phase runner — the key helper that replaces SimpleOrchestrator
# =============================================================================

def _run_phase(logger, phase_name: str, tool, params: dict,
               validator=None, max_retries: int = MAX_RETRIES) -> dict:
    """
    Execute one pipeline phase: log it, call the tool, validate, retry.

    Parameters
    ----------
    logger      : ExecutionLogger   Shared logger for this execution.
    phase_name  : str               Human-readable name (shown in reports).
    tool        : BaseTool          The tool to call.
    params      : dict              Keyword args passed to tool.execute().
    validator   : BaseValidator     Optional — checks the tool's output.
    max_retries : int               How many attempts before giving up.

    Returns
    -------
    The tool result dict on success, or {"success": False, ...} on failure.

    Note: we log a COMPACT version of params (replacing large lists with
    their count) so the metadata column in execution_logs stays readable.
    """
    logger.phase_start(phase_name)

    # Compact params for logging — don't dump hundreds of articles into the DB.
    log_params = {
        k: (f"[{len(v)} articles]" if isinstance(v, list) else v)
        for k, v in params.items()
        if k != "api_key"           # Never log secrets
    }

    step_success = False
    last_result  = None

    for attempt in range(1, max_retries + 1):
        # Log BEFORE calling the tool (so we have a record if the tool hangs).
        logger.tool_call(tool.get_name(), {**log_params, "attempt": attempt})

        start     = time.time()
        result    = tool.execute(**params)
        duration  = int((time.time() - start) * 1000)

        logger.tool_result(tool.get_name(), result, result["success"], duration)
        last_result = result

        if not result["success"]:
            # Tool itself failed — no point validating bad output.
            if attempt < max_retries:
                continue          # try again
            break                 # out of retries

        if validator is None:
            step_success = True
            break

        val = validator.validate(result.get("data") or {})
        logger.validation_event(validator.get_name(), val["passed"], val["issues"])

        if val["passed"]:
            step_success = True
            break

        if not val["needs_more"] or attempt >= max_retries:
            break
        # else: validator said needs_more=True — loop for another attempt

    logger.phase_end(phase_name, step_success)

    if step_success:
        return last_result

    # Return a failure dict so the caller can check result["success"].
    err = (last_result or {}).get("error") or "Phase failed after all retries"
    return {
        "success":   False,
        "data":      None,
        "error":     err,
        "tool_name": tool.get_name(),
        "metadata":  {},
    }


# =============================================================================
# Database helpers  (identical pattern to the template's run.py)
# =============================================================================

def _ensure_workflow_registered(db, workflow_id: str):
    """Create the workflow row on first run (idempotent)."""
    existing = (
        db.table("workflows").select("id").eq("id", workflow_id).execute()
    )
    if not existing:
        db.table("workflows").insert({
            "id":           workflow_id,
            "name":         workflow_id,
            "description":  "Fetches AI news from RSS and saves to Google Sheets.",
            "created_at":   datetime.utcnow().isoformat(),
            "total_runs":   0,
            "successful_runs": 0,
            "failed_runs":  0,
        }).execute()
        print(f"  Registered new workflow: '{workflow_id}'")


def _update_workflow_stats(db, workflow_id: str, success: bool):
    """Increment run counters — SmallBrain reads these to decide when to analyse."""
    rows = (
        db.table("workflows")
        .select("total_runs, successful_runs, failed_runs")
        .eq("id", workflow_id)
        .execute()
    )
    if not rows:
        return
    row = rows[0]
    db.table("workflows").update({
        "total_runs":      row["total_runs"]      + 1,
        "successful_runs": row["successful_runs"] + (1 if success else 0),
        "failed_runs":     row["failed_runs"]     + (0 if success else 1),
        "last_run_at":     datetime.utcnow().isoformat(),
    }).eq("id", workflow_id).execute()


# =============================================================================
# Main
# =============================================================================

def main():
    print(f"\n{'=' * 60}")
    print(f"  Workflow : {WORKFLOW_NAME}")
    print(f"  Feeds    : {len(RSS_FEED_URLS)} source(s)")
    for feed in RSS_FEED_URLS:
        print(f"             {feed[:70]}")
    print(f"  Lookback : last {LOOKBACK_HOURS} hours")
    print(f"  Sheet    : {GOOGLE_SHEET_NAME}")
    print(f"{'=' * 60}")

    # ── 1. Connect to the database ────────────────────────────────────────────
    db = SQLiteClient(DATABASE_PATH)
    print(f"\n[1] Connected to database: {DATABASE_PATH}")

    # ── 2. Register workflow (first run only) ─────────────────────────────────
    _ensure_workflow_registered(db, WORKFLOW_NAME)
    print(f"[2] Workflow registered")

    # ── 3. Create a unique ID for this run ────────────────────────────────────
    execution_id = str(uuid.uuid4())
    print(f"[3] Execution ID: {execution_id}")

    # ── 4. Record execution start in the database ─────────────────────────────
    db.table("executions").insert({
        "id":         execution_id,
        "workflow_id":WORKFLOW_NAME,
        "started_at": datetime.utcnow().isoformat(),
        "status":     "running",
    }).execute()

    # ── 5. Create the ExecutionLogger ─────────────────────────────────────────
    # The logger buffers events in memory.  flush() writes them to the DB.
    # Creating it before the try block ensures it's always accessible in finally.
    logger = ExecutionLogger(execution_id, WORKFLOW_NAME, db)

    overall_success = False

    try:
        # ======================================================================
        # PHASE 1 — Fetch RSS articles
        # ======================================================================
        print(f"\n[5a] Phase 1: Fetching RSS articles...")
        fetch_result = _run_phase(
            logger,
            phase_name  = "Phase 1: Fetch RSS Articles",
            tool        = FetchRSSTool(),
            params      = {"rss_urls": RSS_FEED_URLS},
            validator   = ArticlesFetchedValidator(),
        )

        if not fetch_result["success"]:
            raise RuntimeError(
                f"Phase 1 failed: {fetch_result.get('error', 'unknown error')}\n"
                f"Tip: check that RSS_FEED_URL in your .env is reachable."
            )

        articles = fetch_result["data"]["articles"]
        print(f"     Fetched {len(articles)} article(s) from feed")

        # ======================================================================
        # PHASE 2 — Filter to last N hours
        # ======================================================================
        print(f"[5b] Phase 2: Filtering to last {LOOKBACK_HOURS}h...")
        filter_result = _run_phase(
            logger,
            phase_name  = "Phase 2: Filter Recent Articles",
            tool        = FilterRecentTool(),
            # Pass the articles list from Phase 1 — this is the "chaining".
            params      = {"articles": articles, "hours": LOOKBACK_HOURS},
            validator   = ValidDatesValidator(),
        )

        if not filter_result["success"]:
            raise RuntimeError(
                f"Phase 2 failed: {filter_result.get('error', 'unknown error')}"
            )

        recent_articles = filter_result["data"]["articles"]
        skipped_old     = filter_result["data"].get("skipped_old", 0)
        skipped_nodate  = filter_result["data"].get("skipped_no_date", 0)
        print(f"     {len(recent_articles)} recent  |  "
              f"{skipped_old} too old  |  "
              f"{skipped_nodate} no date")

        # ======================================================================
        # PHASE 3 — Save to Google Sheets  (skipped if nothing is new)
        # ======================================================================
        if not recent_articles:
            print(f"[5c] Phase 3: Skipped — no new articles in the last {LOOKBACK_HOURS}h")
            overall_success = True
        else:
            print(f"[5c] Phase 3: Saving {len(recent_articles)} article(s) to Google Sheets...")
            save_result = _run_phase(
                logger,
                phase_name  = "Phase 3: Save to Google Sheets",
                tool        = SaveToGoogleSheetsTool(),
                # Pass the filtered articles from Phase 2.
                params      = {
                    "articles":         recent_articles,
                    "credentials_file": GOOGLE_CREDENTIALS_FILE,
                    "spreadsheet_id":   GOOGLE_SPREADSHEET_ID,
                    "sheet_name":       GOOGLE_SHEET_NAME,
                },
                validator   = GoogleSheetsSaveValidator(),
            )

            if save_result["success"]:
                saved    = (save_result.get("data") or {}).get("saved_count", 0)
                skipped  = (save_result.get("metadata") or {}).get("skipped_duplicates", 0)
                print(f"     Saved {saved} new row(s) to Google Sheets"
                      + (f"  |  {skipped} duplicate(s) skipped" if skipped else ""))
                overall_success = True
            else:
                print(f"     Save failed: {save_result.get('error')}")
                overall_success = False

        # ── Mark execution as completed ───────────────────────────────────────
        db.table("executions").update({
            "status":       "completed" if overall_success else "failed",
            "completed_at": datetime.utcnow().isoformat(),
        }).eq("id", execution_id).execute()

    except Exception as exc:
        # Log the unexpected error so SmallBrain can see it.
        logger.error(str(exc))
        db.table("executions").update({
            "status":        "failed",
            "completed_at":  datetime.utcnow().isoformat(),
            "error_message": str(exc),
        }).eq("id", execution_id).execute()
        print(f"\n  ERROR: {exc}")

    finally:
        # ======================================================================
        # CRITICAL: logger.flush() MUST always run — even if an exception
        # occurred above.  This is the only thing that writes buffered log
        # events to the database.  Without it, SmallBrain has no data.
        # ======================================================================
        logger.flush()
        print(f"\n[6] Logs flushed to database")

    # ── 7. Update workflow statistics ─────────────────────────────────────────
    _update_workflow_stats(db, WORKFLOW_NAME, overall_success)
    print(f"[7] Workflow stats updated")

    # ── 8. SmallBrain analysis ────────────────────────────────────────────────
    # SmallBrain reads from the database (not from this run's memory),
    # so it works correctly even after a crash — as long as flush() ran.
    print(f"[8] Running SmallBrain analysis...")
    try:
        # Import SmallBrain from the template — it's generic and works for
        # any workflow without modification.
        from templates.workflow_template.brain import SmallBrain
        brain     = SmallBrain(workflow_id=WORKFLOW_NAME, db=db)
        proposals = brain.analyze()
        if proposals:
            print(f"    {len(proposals)} proposal(s) saved.")
            print(f"    View them:  SELECT title, description FROM proposals "
                  f"WHERE workflow_id = '{WORKFLOW_NAME}';")
    except Exception as brain_err:
        print(f"    SmallBrain skipped: {brain_err}")

    # ── 8b. BigBrain system health check ─────────────────────────────────
    from lib.big_brain.hooks import post_workflow_check
    post_workflow_check(db)

    # ── 9. Final summary ──────────────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    if overall_success:
        print(f"  RESULT : SUCCESS")
    else:
        print(f"  RESULT : FAILED")
        print(f"  Debug  : python scripts/show_logs.py {WORKFLOW_NAME} --last 1")
    print(f"  Run ID : {execution_id}")
    print(f"{'=' * 60}\n")

    return {"success": overall_success, "execution_id": execution_id}


if __name__ == "__main__":
    main()
