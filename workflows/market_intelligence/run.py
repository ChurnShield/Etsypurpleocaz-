# =============================================================================
# workflows/market_intelligence/run.py
#
# Entry point for the Market Intelligence workflow.
#
#   python workflows/market_intelligence/run.py
#
# Pipeline:
#   Phase 1  (Fetch)   -> Google Trends (enhanced) + Reddit public API
#   Phase 2  (Enrich)  -> Etsy API competitor data (ephemeral)
#   Phase 3  (Score)   -> Claude AI opportunity scoring
#   Phase 4  (Save)    -> Write to "Market Intelligence" Sheets tab
# =============================================================================

import sys
import os
import uuid
import time
from datetime import datetime, timezone

_here = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(_here))
sys.path.insert(0, _project_root)
sys.path.insert(1, _here)

import importlib.util as _ilu
_wf_spec = _ilu.spec_from_file_location("workflow_config", os.path.join(_here, "config.py"))
_wf_config = _ilu.module_from_spec(_wf_spec)
_wf_spec.loader.exec_module(_wf_config)

WORKFLOW_NAME = _wf_config.WORKFLOW_NAME
DATABASE_PATH = _wf_config.DATABASE_PATH
MAX_RETRIES = _wf_config.MAX_RETRIES
ETSY_API_KEY = _wf_config.ETSY_API_KEY
ETSY_PAGE_LIMIT = _wf_config.ETSY_PAGE_LIMIT
ANTHROPIC_API_KEY = _wf_config.ANTHROPIC_API_KEY
ANTHROPIC_MODEL = _wf_config.ANTHROPIC_MODEL
GOOGLE_CREDENTIALS_FILE = _wf_config.GOOGLE_CREDENTIALS_FILE
GOOGLE_SPREADSHEET_ID = _wf_config.GOOGLE_SPREADSHEET_ID
MARKET_INTEL_SHEET_NAME = _wf_config.MARKET_INTEL_SHEET_NAME
TREND_KEYWORDS = _wf_config.TREND_KEYWORDS
REDDIT_SUBREDDITS = _wf_config.REDDIT_SUBREDDITS
REDDIT_POST_LIMIT = _wf_config.REDDIT_POST_LIMIT
REDDIT_LOOKBACK_DAYS = _wf_config.REDDIT_LOOKBACK_DAYS
TRENDS_GEO = _wf_config.TRENDS_GEO
TRENDS_TIMEFRAME = _wf_config.TRENDS_TIMEFRAME
FOCUS_NICHE = _wf_config.FOCUS_NICHE
MIN_OPPORTUNITY_SCORE = _wf_config.MIN_OPPORTUNITY_SCORE
MAX_OPPORTUNITIES = _wf_config.MAX_OPPORTUNITIES
MAX_SIGNALS_TO_ENRICH = _wf_config.MAX_SIGNALS_TO_ENRICH
PROPOSAL_THRESHOLD_RUNS = _wf_config.PROPOSAL_THRESHOLD_RUNS

from lib.common_tools.sqlite_client import SQLiteClient
from lib.orchestrator.execution_logger import ExecutionLogger

from tools.fetch_social_trends_tool    import FetchSocialTrendsTool
from tools.enrich_competitor_data_tool import EnrichCompetitorDataTool
from tools.score_opportunities_tool    import ScoreOpportunitiesTool
from tools.save_market_report_tool     import SaveMarketReportTool

from validators.social_trends_validator import SocialTrendsValidator
from validators.enrichment_validator    import EnrichmentValidator
from validators.scoring_validator       import ScoringValidator
from validators.report_saved_validator  import ReportSavedValidator


def _run_phase(logger, phase_name, tool, params, validator=None, max_retries=MAX_RETRIES):
    logger.phase_start(phase_name)
    log_params = {}
    for k, v in params.items():
        if k in ("api_key", "anthropic_api_key", "gemini_api_key"):
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
            "description": "Market Intelligence - gathers social trends, enriches with Etsy competitor data, scores opportunities with AI.",
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
    subreddits = REDDIT_SUBREDDITS.get(FOCUS_NICHE, REDDIT_SUBREDDITS.get("tattoo", []))

    print(f"\n{'=' * 60}")
    print(f"  Workflow   : {WORKFLOW_NAME}")
    print(f"  Niche      : {FOCUS_NICHE}")
    print(f"  Subreddits : {', '.join(f'r/{s}' for s in subreddits[:4])}")
    print(f"  Keywords   : {len(TREND_KEYWORDS)}")
    print(f"  Model      : {ANTHROPIC_MODEL}")
    print(f"{'=' * 60}")

    if not ANTHROPIC_API_KEY:
        print("\n  ERROR: ANTHROPIC_API_KEY not set in .env")
        return {"success": False}
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
        # ==== PHASE 1: Fetch social trends ====
        print(f"\n[4a] Phase 1: Fetching social trend signals...")
        fetch_result = _run_phase(
            logger, "Phase 1: Fetch Social Trends",
            tool=FetchSocialTrendsTool(),
            params={
                "trend_keywords": TREND_KEYWORDS,
                "subreddits": subreddits,
                "reddit_post_limit": REDDIT_POST_LIMIT,
                "reddit_lookback_days": REDDIT_LOOKBACK_DAYS,
                "trends_geo": TRENDS_GEO,
                "trends_timeframe": TRENDS_TIMEFRAME,
                "focus_niche": FOCUS_NICHE,
            },
            validator=SocialTrendsValidator(),
        )

        if not fetch_result["success"]:
            raise RuntimeError(f"Phase 1 failed: {fetch_result.get('error')}")

        fetch_data = fetch_result["data"]
        trend_signals = fetch_data["trend_signals"]
        print(f"     Total signals: {len(trend_signals)}")

        # ==== PHASE 2: Enrich with Etsy competitor data ====
        print(f"\n[4b] Phase 2: Enriching with Etsy competitor data...")
        enrich_result = _run_phase(
            logger, "Phase 2: Enrich Competitor Data",
            tool=EnrichCompetitorDataTool(),
            params={
                "trend_signals": trend_signals,
                "api_key": ETSY_API_KEY,
                "page_limit": ETSY_PAGE_LIMIT,
                "max_signals_to_enrich": MAX_SIGNALS_TO_ENRICH,
            },
            validator=EnrichmentValidator(),
        )

        if not enrich_result["success"]:
            raise RuntimeError(f"Phase 2 failed: {enrich_result.get('error')}")

        enrich_data = enrich_result["data"]
        enriched_signals = enrich_data["enriched_signals"]
        e_stats = enrich_data["enrichment_stats"]
        print(f"     Enriched: {e_stats['enriched']}, Skipped: {e_stats['skipped']}, Errors: {e_stats['errors']}")

        # ==== PHASE 3: Score & rank opportunities ====
        print(f"\n[4c] Phase 3: Scoring opportunities with Claude...")
        score_result = _run_phase(
            logger, "Phase 3: Score Opportunities",
            tool=ScoreOpportunitiesTool(),
            params={
                "enriched_signals": enriched_signals,
                "anthropic_api_key": ANTHROPIC_API_KEY,
                "model": ANTHROPIC_MODEL,
                "focus_niche": FOCUS_NICHE,
                "min_score": MIN_OPPORTUNITY_SCORE,
                "max_opportunities": MAX_OPPORTUNITIES,
            },
            validator=ScoringValidator(),
        )

        if not score_result["success"]:
            raise RuntimeError(f"Phase 3 failed: {score_result.get('error')}")

        score_data = score_result["data"]
        scored_opps = score_data["scored_opportunities"]
        s_stats = score_data["scoring_stats"]
        print(f"     Opportunities: {len(scored_opps)} (from {s_stats['input_signals']} signals)")

        # ==== PHASE 4: Save to Sheets ====
        print(f"\n[4d] Phase 4: Saving market report to Sheets...")
        save_result = _run_phase(
            logger, "Phase 4: Save Market Report",
            tool=SaveMarketReportTool(),
            params={
                "scored_opportunities": scored_opps,
                "credentials_file": GOOGLE_CREDENTIALS_FILE,
                "spreadsheet_id": GOOGLE_SPREADSHEET_ID,
                "sheet_name": MARKET_INTEL_SHEET_NAME,
            },
            validator=ReportSavedValidator(),
        )

        if save_result["success"]:
            save_data = save_result["data"]
            print(f"     Saved: {save_data['rows_written']} rows to '{save_data['sheet_name']}'")
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

    # BigBrain system health check
    from lib.big_brain.hooks import post_workflow_check
    post_workflow_check(db)

    # ── Obsidian vault sync ──────────────────────────────────────────
    from lib.obsidian.hooks import post_workflow_sync
    post_workflow_sync(db)

    print(f"\n{'=' * 60}")
    if overall_success:
        print(f"  RESULT : SUCCESS")
        print(f"  Check  : Google Sheets '{MARKET_INTEL_SHEET_NAME}' tab")
        print(f"  Next   : Run auto_listing_creator to consume these opportunities")
    else:
        print(f"  RESULT : FAILED")
        print(f"  Debug  : python scripts/show_logs.py {WORKFLOW_NAME} --last 1")
    print(f"  Run ID : {execution_id}")
    print(f"{'=' * 60}\n")

    return {"success": overall_success, "execution_id": execution_id}


if __name__ == "__main__":
    main()
