# =============================================================================
# workflows/tattoo_trend_monitor/run.py
#
# Entry point for the Tattoo Trend Monitor workflow.
#
#   python workflows/tattoo_trend_monitor/run.py
#
# Pipeline:
#   Phase 1 (Fetch)   -> Google Trends + Etsy competitor search + your listings
#                          |
#   Phase 2 (Analyse) -> Gap analysis + AI opportunity ranking
#                          |
#   Phase 3 (Save)    -> Write report to Google Sheets
# =============================================================================

import sys
import os
import uuid
import time
from datetime import datetime, timezone

_here = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(_here))
sys.path.insert(0, _here)
sys.path.insert(1, _project_root)

from config import (
    WORKFLOW_NAME, DATABASE_PATH, MAX_RETRIES,
    ETSY_API_KEY, ETSY_SHOP_ID, ETSY_PAGE_LIMIT,
    ANTHROPIC_API_KEY, ANTHROPIC_MODEL,
    GOOGLE_CREDENTIALS_FILE, GOOGLE_SPREADSHEET_ID,
    TRENDS_SHEET_NAME, OPPORTUNITIES_SHEET_NAME,
    TREND_KEYWORDS, ETSY_SEARCH_QUERIES,
    TRENDS_GEO, TRENDS_TIMEFRAME,
    FOCUS_NICHE, PROPOSAL_THRESHOLD_RUNS,
)

from lib.common_tools.sqlite_client import SQLiteClient
from lib.orchestrator.execution_logger import ExecutionLogger

from tools.fetch_trends_tool          import FetchTrendsTool
from tools.analyse_opportunities_tool import AnalyseOpportunitiesTool
from tools.save_trends_report_tool    import SaveTrendsReportTool

from validators.trends_fetched_validator import TrendsFetchedValidator
from validators.opportunities_validator  import OpportunitiesValidator
from validators.report_saved_validator   import ReportSavedValidator


def _run_phase(logger, phase_name, tool, params, validator=None, max_retries=MAX_RETRIES):
    logger.phase_start(phase_name)
    log_params = {}
    for k, v in params.items():
        if k in ("api_key", "anthropic_api_key"):
            continue
        if isinstance(v, list):
            log_params[k] = f"[{len(v)} items]"
        elif isinstance(v, dict) and len(str(v)) > 200:
            log_params[k] = f"{{dict with {len(v)} keys}}"
        else:
            log_params[k] = v

    step_success = False
    last_result = None
    for attempt in range(1, max_retries + 1):
        logger.tool_call(tool.get_name(), {**log_params, "attempt": attempt})
        start = time.time()
        result = tool.execute(**params)
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
    err = (last_result or {}).get("error") or "Phase failed"
    return {"success": False, "data": None, "error": err,
            "tool_name": tool.get_name(), "metadata": {}}


def _ensure_workflow_registered(db, wid):
    if not db.table("workflows").select("id").eq("id", wid).execute():
        db.table("workflows").insert({
            "id": wid, "name": wid,
            "description": "Tattoo Trend Monitor - tracks Google Trends + Etsy competitors to find product opportunities.",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "total_runs": 0, "successful_runs": 0, "failed_runs": 0,
        }).execute()
        print(f"  Registered workflow: '{wid}'")


def _update_workflow_stats(db, wid, success):
    rows = db.table("workflows").select("total_runs, successful_runs, failed_runs").eq("id", wid).execute()
    if not rows:
        return
    row = rows[0]
    db.table("workflows").update({
        "total_runs": row["total_runs"] + 1,
        "successful_runs": row["successful_runs"] + (1 if success else 0),
        "failed_runs": row["failed_runs"] + (0 if success else 1),
        "last_run_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", wid).execute()


def main():
    print(f"\n{'=' * 60}")
    print(f"  Workflow  : {WORKFLOW_NAME}")
    print(f"  Shop ID   : {ETSY_SHOP_ID}")
    print(f"  Niche     : {FOCUS_NICHE}")
    print(f"  Keywords  : {len(TREND_KEYWORDS)} tracked")
    print(f"  Searches  : {len(ETSY_SEARCH_QUERIES)} competitor queries")
    print(f"  Model     : {ANTHROPIC_MODEL}")
    print(f"{'=' * 60}")

    if not ETSY_API_KEY or ETSY_API_KEY == ":":
        print("\n  ERROR: Etsy API credentials not set in .env")
        return {"success": False}

    db = SQLiteClient(DATABASE_PATH)
    print(f"\n[1] Connected to database")
    _ensure_workflow_registered(db, WORKFLOW_NAME)
    print(f"[2] Workflow registered")

    execution_id = str(uuid.uuid4())
    print(f"[3] Execution ID: {execution_id}")

    db.table("executions").insert({
        "id": execution_id, "workflow_id": WORKFLOW_NAME,
        "started_at": datetime.now(timezone.utc).isoformat(), "status": "running",
    }).execute()

    logger = ExecutionLogger(execution_id, WORKFLOW_NAME, db)
    overall_success = False

    try:
        # ==== PHASE 1: Fetch trends + competitor data ====
        print(f"\n[4a] Phase 1: Fetching trend data...")
        fetch_result = _run_phase(
            logger, "Phase 1: Fetch Trends",
            tool=FetchTrendsTool(),
            params={
                "trend_keywords": TREND_KEYWORDS,
                "etsy_search_queries": ETSY_SEARCH_QUERIES,
                "api_key": ETSY_API_KEY,
                "shop_id": ETSY_SHOP_ID,
                "page_limit": ETSY_PAGE_LIMIT,
                "trends_geo": TRENDS_GEO,
                "trends_timeframe": TRENDS_TIMEFRAME,
            },
            validator=TrendsFetchedValidator(),
        )

        if not fetch_result["success"]:
            raise RuntimeError(f"Phase 1 failed: {fetch_result.get('error')}")

        fetch_data = fetch_result["data"]
        print(f"     Trends: {len(fetch_data['trends'])} keywords")
        print(f"     Competitors: {len(fetch_data['competitor_search'])} queries scanned")
        print(f"     Your tattoo listings: {len(fetch_data['my_tattoo_listings'])}")

        # ==== PHASE 2: Analyse opportunities ====
        print(f"\n[4b] Phase 2: Analysing opportunities...")
        analyse_result = _run_phase(
            logger, "Phase 2: Analyse Opportunities",
            tool=AnalyseOpportunitiesTool(),
            params={
                "trends": fetch_data["trends"],
                "competitor_search": fetch_data["competitor_search"],
                "my_tattoo_listings": fetch_data["my_tattoo_listings"],
                "anthropic_api_key": ANTHROPIC_API_KEY,
                "model": ANTHROPIC_MODEL,
            },
            validator=OpportunitiesValidator(),
        )

        if not analyse_result["success"]:
            raise RuntimeError(f"Phase 2 failed: {analyse_result.get('error')}")

        analysis = analyse_result["data"]
        summary = analysis["summary"]
        print(f"     Rising trends: {summary['rising_trends']}")
        print(f"     Product gaps: {summary['total_gaps']}")
        print(f"     Weak coverage: {summary['weak_coverage']}")
        print(f"     AI product ideas: {len(analysis['ai_opportunities'])}")

        if analysis["opportunities"]:
            top = analysis["opportunities"][0]
            print(f"     Top opportunity: '{top['keyword']}' (score: {top['opportunity_score']})")

        # ==== PHASE 3: Save report to Google Sheets ====
        print(f"\n[4c] Phase 3: Saving trend report to Google Sheets...")
        save_result = _run_phase(
            logger, "Phase 3: Save Report",
            tool=SaveTrendsReportTool(),
            params={
                "credentials_file": GOOGLE_CREDENTIALS_FILE,
                "spreadsheet_id": GOOGLE_SPREADSHEET_ID,
                "trends_sheet_name": TRENDS_SHEET_NAME,
                "opportunities_sheet_name": OPPORTUNITIES_SHEET_NAME,
                "opportunities": analysis["opportunities"],
                "ai_opportunities": analysis["ai_opportunities"],
                "summary": summary,
            },
            validator=ReportSavedValidator(),
        )

        if save_result["success"]:
            sd = save_result["data"]
            print(f"     Trends tab: {sd['trends_rows']} rows")
            print(f"     Opportunities tab: {sd['opportunity_rows']} product ideas")
            overall_success = True
        else:
            print(f"     Save failed: {save_result.get('error')}")

        db.table("executions").update({
            "status": "completed" if overall_success else "failed",
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", execution_id).execute()

    except Exception as exc:
        logger.error(str(exc))
        db.table("executions").update({
            "status": "failed",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "error_message": str(exc),
        }).eq("id", execution_id).execute()
        print(f"\n  ERROR: {exc}")

    finally:
        logger.flush()
        print(f"\n[5] Logs flushed to database")

    _update_workflow_stats(db, WORKFLOW_NAME, overall_success)
    print(f"[6] Workflow stats updated")

    print(f"\n[7] Running SmallBrain analysis...")
    try:
        from templates.workflow_template.brain import SmallBrain
        brain = SmallBrain(workflow_id=WORKFLOW_NAME, db=db)
        proposals = brain.analyze()
        if proposals:
            print(f"    {len(proposals)} proposal(s) saved.")
    except Exception as brain_err:
        print(f"    SmallBrain skipped: {brain_err}")

    print(f"\n{'=' * 60}")
    if overall_success:
        print(f"  RESULT : SUCCESS")
        print(f"  Check  : Google Sheets '{TRENDS_SHEET_NAME}' and '{OPPORTUNITIES_SHEET_NAME}' tabs")
    else:
        print(f"  RESULT : FAILED")
        print(f"  Debug  : python scripts/show_logs.py {WORKFLOW_NAME} --last 1")
    print(f"  Run ID : {execution_id}")
    print(f"{'=' * 60}\n")

    return {"success": overall_success, "execution_id": execution_id}


if __name__ == "__main__":
    main()
