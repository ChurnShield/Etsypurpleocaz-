# =============================================================================
# workflows/etsy_analytics/run.py
#
# Entry point for the Etsy Analytics Dashboard workflow.
#
#   python workflows/etsy_analytics/run.py
#
# Pipeline:
#   Phase 1 (Fetch)   → all listings + shop stats from Etsy API
#                           ↓
#   Phase 2 (Analyze) → performance metrics, top performers, tag analysis
#                           ↓
#   Phase 3 (Save)    → Google Sheets (3 tabs)
#
# Uses ExecutionLogger directly (same pattern as ai_news_rss).
# Critical: logger.flush() MUST be in a finally block.
# =============================================================================

import sys
import os
import uuid
import time
from datetime import datetime

# ---------------------------------------------------------------------------
# Path setup — MUST happen before any other local imports
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
    ETSY_API_KEY,
    ETSY_SHOP_ID,
    ETSY_PAGE_LIMIT,
    GOOGLE_CREDENTIALS_FILE,
    GOOGLE_SPREADSHEET_ID,
    ETSY_SNAPSHOT_SHEET_NAME,
    ETSY_LISTINGS_SHEET_NAME,
    ETSY_TOP_PERFORMERS_SHEET,
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
from tools.fetch_etsy_data_tool     import FetchEtsyDataTool
from tools.analyze_performance_tool import AnalyzePerformanceTool
from tools.save_analytics_tool      import SaveAnalyticsTool

from validators.listings_fetched_validator import ListingsFetchedValidator
from validators.analysis_validator         import AnalysisValidator
from validators.analytics_saved_validator  import AnalyticsSavedValidator


# =============================================================================
# Phase runner (same pattern as ai_news_rss)
# =============================================================================

def _run_phase(logger, phase_name: str, tool, params: dict,
               validator=None, max_retries: int = MAX_RETRIES) -> dict:
    logger.phase_start(phase_name)

    # Compact params for logging — never log secrets or huge lists
    log_params = {}
    for k, v in params.items():
        if k in ("api_key",):
            continue
        if isinstance(v, list):
            log_params[k] = f"[{len(v)} items]"
        elif isinstance(v, dict) and len(str(v)) > 200:
            log_params[k] = f"{{dict with {len(v)} keys}}"
        else:
            log_params[k] = v

    step_success = False
    last_result  = None

    for attempt in range(1, max_retries + 1):
        logger.tool_call(tool.get_name(), {**log_params, "attempt": attempt})

        start    = time.time()
        result   = tool.execute(**params)
        duration = int((time.time() - start) * 1000)

        logger.tool_result(tool.get_name(), result, result["success"], duration)
        last_result = result

        if not result["success"]:
            if attempt < max_retries:
                continue
            break

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

    logger.phase_end(phase_name, step_success)

    if step_success:
        return last_result

    err = (last_result or {}).get("error") or "Phase failed after all retries"
    return {
        "success":   False,
        "data":      None,
        "error":     err,
        "tool_name": tool.get_name(),
        "metadata":  {},
    }


# =============================================================================
# Database helpers
# =============================================================================

def _ensure_workflow_registered(db, workflow_id: str):
    existing = db.table("workflows").select("id").eq("id", workflow_id).execute()
    if not existing:
        db.table("workflows").insert({
            "id":              workflow_id,
            "name":            workflow_id,
            "description":     "Etsy Analytics Dashboard — daily shop & listing performance tracking.",
            "created_at":      datetime.utcnow().isoformat(),
            "total_runs":      0,
            "successful_runs": 0,
            "failed_runs":     0,
        }).execute()
        print(f"  Registered new workflow: '{workflow_id}'")


def _update_workflow_stats(db, workflow_id: str, success: bool):
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
    print(f"  Shop ID  : {ETSY_SHOP_ID}")
    print(f"  Sheets   : Snapshot  = {ETSY_SNAPSHOT_SHEET_NAME}")
    print(f"             Listings  = {ETSY_LISTINGS_SHEET_NAME}")
    print(f"             Top Perf  = {ETSY_TOP_PERFORMERS_SHEET}")
    print(f"{'=' * 60}")

    # -- Preflight checks --
    if not ETSY_API_KEY or ETSY_API_KEY == ":":
        print("\n  ERROR: ETSY_API_KEYSTRING and ETSY_SHARED_SECRET must be set in .env")
        return {"success": False, "execution_id": None}

    if not ETSY_SHOP_ID:
        print("\n  ERROR: ETSY_SHOP_ID must be set in .env")
        return {"success": False, "execution_id": None}

    # ── 1. Connect to database ─────────────────────────────────────────
    db = SQLiteClient(DATABASE_PATH)
    print(f"\n[1] Connected to database: {DATABASE_PATH}")

    # ── 2. Register workflow ───────────────────────────────────────────
    _ensure_workflow_registered(db, WORKFLOW_NAME)
    print(f"[2] Workflow registered")

    # ── 3. Create execution ID ─────────────────────────────────────────
    execution_id = str(uuid.uuid4())
    print(f"[3] Execution ID: {execution_id}")

    # ── 4. Record execution start ──────────────────────────────────────
    db.table("executions").insert({
        "id":          execution_id,
        "workflow_id": WORKFLOW_NAME,
        "started_at":  datetime.utcnow().isoformat(),
        "status":      "running",
    }).execute()

    # ── 5. Create ExecutionLogger ──────────────────────────────────────
    logger = ExecutionLogger(execution_id, WORKFLOW_NAME, db)
    overall_success = False

    try:
        # ==============================================================
        # PHASE 1 — Fetch all listings + shop stats from Etsy
        # ==============================================================
        print(f"\n[5a] Phase 1: Fetching all listings from Etsy API...")
        fetch_result = _run_phase(
            logger,
            phase_name = "Phase 1: Fetch Etsy Data",
            tool       = FetchEtsyDataTool(),
            params     = {
                "api_key":    ETSY_API_KEY,
                "shop_id":    ETSY_SHOP_ID,
                "page_limit": ETSY_PAGE_LIMIT,
            },
            validator  = ListingsFetchedValidator(),
        )

        if not fetch_result["success"]:
            raise RuntimeError(
                f"Phase 1 failed: {fetch_result.get('error', 'unknown')}\n"
                f"Check ETSY_API_KEYSTRING and ETSY_SHARED_SECRET in .env"
            )

        shop     = fetch_result["data"]["shop"]
        listings = fetch_result["data"]["listings"]
        has_sales = fetch_result["data"].get("has_sales_data", False)
        print(f"     Fetched {len(listings)} listings for {shop['shop_name']}")
        print(f"     Shop stats: {shop['total_sales']} sales | "
              f"{shop['num_favorers']} favs | "
              f"{shop['review_average']:.1f} avg review ({shop['review_count']} reviews)")
        if has_sales:
            print(f"     Sales data: AVAILABLE (OAuth connected)")
        else:
            print(f"     Sales data: Not available (run etsy_oauth.py to enable)")

        # ==============================================================
        # PHASE 2 — Analyze performance
        # ==============================================================
        print(f"\n[5b] Phase 2: Analyzing listing performance...")
        analyze_result = _run_phase(
            logger,
            phase_name = "Phase 2: Analyze Performance",
            tool       = AnalyzePerformanceTool(),
            params     = {"shop": shop, "listings": listings},
            validator  = AnalysisValidator(),
        )

        if not analyze_result["success"]:
            raise RuntimeError(
                f"Phase 2 failed: {analyze_result.get('error', 'unknown')}"
            )

        analysis = analyze_result["data"]
        snapshot = analysis["snapshot"]
        print(f"     Total views: {snapshot['total_views']:,} | "
              f"Total favs: {snapshot['total_favs']:,}")
        print(f"     Avg views/listing: {snapshot['avg_views']} | "
              f"Avg favs/listing: {snapshot['avg_favs']}")
        print(f"     Zero-view listings: {snapshot['zero_view_count']} | "
              f"Under-tagged: {snapshot['under_tagged']}")
        print(f"     Tattoo niche: {snapshot['tattoo_listings']} listings | "
              f"{snapshot['tattoo_views']:,} views | "
              f"{snapshot['tattoo_favs']:,} favs")
        if snapshot.get("total_revenue", 0) > 0:
            print(f"     Revenue: {snapshot['total_revenue']:,.2f} GBP total | "
                  f"{snapshot.get('tattoo_revenue', 0):,.2f} GBP tattoo")

        # ==============================================================
        # PHASE 3 — Save to Google Sheets
        # ==============================================================
        print(f"\n[5c] Phase 3: Saving analytics to Google Sheets...")
        save_result = _run_phase(
            logger,
            phase_name = "Phase 3: Save to Google Sheets",
            tool       = SaveAnalyticsTool(),
            params     = {
                "credentials_file":   GOOGLE_CREDENTIALS_FILE,
                "spreadsheet_id":     GOOGLE_SPREADSHEET_ID,
                "snapshot_sheet_name": ETSY_SNAPSHOT_SHEET_NAME,
                "listings_sheet_name": ETSY_LISTINGS_SHEET_NAME,
                "top_perf_sheet_name": ETSY_TOP_PERFORMERS_SHEET,
                "snapshot":           snapshot,
                "listings":           analysis["listings"],
                "top_by_views":       analysis["top_by_views"],
                "top_by_favs":        analysis["top_by_favs"],
                "top_by_revenue":     analysis.get("top_by_revenue", []),
                "top_by_sales":       analysis.get("top_by_sales", []),
                "top_engagement":     analysis["top_engagement"],
            },
            validator = AnalyticsSavedValidator(),
        )

        if save_result["success"]:
            sd = save_result["data"]
            print(f"     Snapshot: {'added' if sd['snapshot_added'] else 'already exists for today'}")
            print(f"     Listings written: {sd['listings_saved']}")
            print(f"     Top performers: {sd['top_rows_saved']} rows")
            overall_success = True
        else:
            print(f"     Save failed: {save_result.get('error')}")
            overall_success = False

        # -- Mark execution completed --
        db.table("executions").update({
            "status":       "completed" if overall_success else "failed",
            "completed_at": datetime.utcnow().isoformat(),
        }).eq("id", execution_id).execute()

    except Exception as exc:
        logger.error(str(exc))
        db.table("executions").update({
            "status":        "failed",
            "completed_at":  datetime.utcnow().isoformat(),
            "error_message": str(exc),
        }).eq("id", execution_id).execute()
        print(f"\n  ERROR: {exc}")

    finally:
        logger.flush()
        print(f"\n[6] Logs flushed to database")

    # ── 7. Update workflow stats ───────────────────────────────────────
    _update_workflow_stats(db, WORKFLOW_NAME, overall_success)
    print(f"[7] Workflow stats updated")

    # ── 8. SmallBrain analysis ─────────────────────────────────────────
    print(f"[8] Running SmallBrain analysis...")
    try:
        from templates.workflow_template.brain import SmallBrain
        brain     = SmallBrain(workflow_id=WORKFLOW_NAME, db=db)
        proposals = brain.analyze()
        if proposals:
            print(f"    {len(proposals)} proposal(s) saved.")
    except Exception as brain_err:
        print(f"    SmallBrain skipped: {brain_err}")

    # ── 8b. BigBrain system health check ─────────────────────────────────
    from lib.big_brain.hooks import post_workflow_check
    post_workflow_check(db)

    # ── 9. Final summary ──────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    if overall_success:
        print(f"  RESULT : SUCCESS")
        print(f"  Sheets : Check your Google Spreadsheet for updated data")
    else:
        print(f"  RESULT : FAILED")
        print(f"  Debug  : python scripts/show_logs.py {WORKFLOW_NAME} --last 1")
    print(f"  Run ID : {execution_id}")
    print(f"{'=' * 60}\n")

    return {"success": overall_success, "execution_id": execution_id}


if __name__ == "__main__":
    main()
