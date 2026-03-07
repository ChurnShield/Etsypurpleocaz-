# =============================================================================
# workflows/notebooklm_audio/run.py
#
# Entry point for the NotebookLM Audio Product workflow.
#
#   python workflows/notebooklm_audio/run.py
#
# Pipeline:
#   Phase 1 (Curate)   -> Gather sources and populate NotebookLM notebooks
#                           |
#   Phase 2 (Generate)  -> Trigger Audio Overview generation
#                           |
#   Phase 3 (Package)   -> Generate listing content + assemble products
#                           |
#   Phase 4 (Publish)   -> Save to Sheets + create Etsy drafts
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
    AUDIO_NICHES, AUDIO_PRODUCT_TYPES,
    DEFAULT_AUDIO_PRICE_GBP, BUNDLE_AUDIO_WITH_TEMPLATES,
    NOTEBOOKLM_NOTEBOOK_IDS,
    ANTHROPIC_API_KEY, ANTHROPIC_MODEL,
    GOOGLE_CREDENTIALS_FILE, GOOGLE_SPREADSHEET_ID,
    AUDIO_PRODUCTS_SHEET,
    ETSY_API_KEY, ETSY_SHOP_ID,
    DEFAULT_CURRENCY, DEFAULT_TAXONOMY_ID, TOKEN_FILE,
    EXPORT_DIR,
    PROPOSAL_THRESHOLD_RUNS,
)

from lib.common_tools.sqlite_client import SQLiteClient
from lib.orchestrator.execution_logger import ExecutionLogger

from tools.source_curator_tool import SourceCuratorTool
from tools.audio_generator_tool import AudioGeneratorTool
from tools.audio_product_packager_tool import AudioProductPackagerTool
from tools.audio_publisher_tool import AudioPublisherTool

from validators.sources_curated_validator import SourcesCuratedValidator
from validators.audio_generated_validator import AudioGeneratedValidator
from validators.audio_published_validator import AudioPublishedValidator


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
            "description": "NotebookLM Audio - generates audio guide products from NotebookLM notebooks.",
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
    print(f"  Niches    : {', '.join(AUDIO_NICHES)}")
    print(f"  Products  : {', '.join(AUDIO_PRODUCT_TYPES)}")
    print(f"  Model     : {ANTHROPIC_MODEL}")
    print(f"  Currency  : {DEFAULT_CURRENCY}")
    print(f"  Bundle    : {'yes' if BUNDLE_AUDIO_WITH_TEMPLATES else 'no'}")
    print(f"{'=' * 60}")

    if not ANTHROPIC_API_KEY:
        print("\n  ERROR: ANTHROPIC_API_KEY not set in .env")
        return {"success": False}

    create_drafts = os.path.exists(TOKEN_FILE)

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
        # ==== PHASE 1: Curate sources ====
        print(f"\n[4a] Phase 1: Curating sources for NotebookLM notebooks...")
        curate_result = _run_phase(
            logger, "Phase 1: Curate Sources",
            tool=SourceCuratorTool(),
            params={
                "niches": AUDIO_NICHES,
                "product_types": AUDIO_PRODUCT_TYPES,
                "notebook_ids": NOTEBOOKLM_NOTEBOOK_IDS,
                "db": db,
            },
            validator=SourcesCuratedValidator(),
        )

        if not curate_result["success"]:
            raise RuntimeError(f"Phase 1 failed: {curate_result.get('error')}")

        curate_data = curate_result["data"]
        notebooks = curate_data["notebooks"]
        print(f"     Curated: {len(notebooks)} notebooks, {curate_data['total_sources']} sources")

        # ==== PHASE 2: Generate audio ====
        print(f"\n[4b] Phase 2: Generating audio overviews...")
        audio_result = _run_phase(
            logger, "Phase 2: Generate Audio",
            tool=AudioGeneratorTool(),
            params={
                "notebooks": notebooks,
                "export_dir": EXPORT_DIR,
            },
            validator=AudioGeneratedValidator(),
        )

        if not audio_result["success"]:
            raise RuntimeError(f"Phase 2 failed: {audio_result.get('error')}")

        audio_data = audio_result["data"]
        audio_stats = audio_data["stats"]
        print(f"     Generated: {audio_stats['generated']}/{audio_stats['total']} audio files")

        # ==== PHASE 3: Package products ====
        print(f"\n[4c] Phase 3: Packaging audio products...")
        package_result = _run_phase(
            logger, "Phase 3: Package Products",
            tool=AudioProductPackagerTool(),
            params={
                "audio_products": audio_data["audio_products"],
                "anthropic_api_key": ANTHROPIC_API_KEY,
                "model": ANTHROPIC_MODEL,
                "currency": DEFAULT_CURRENCY,
                "default_price": DEFAULT_AUDIO_PRICE_GBP,
                "bundle_with_templates": BUNDLE_AUDIO_WITH_TEMPLATES,
            },
        )

        if not package_result["success"]:
            raise RuntimeError(f"Phase 3 failed: {package_result.get('error')}")

        package_data = package_result["data"]
        pkg_stats = package_data["stats"]
        print(f"     Packaged: {pkg_stats['packaged']}/{pkg_stats['total']} products")

        # ==== PHASE 4: Publish ====
        print(f"\n[4d] Phase 4: Publishing audio products...")
        publish_result = _run_phase(
            logger, "Phase 4: Publish",
            tool=AudioPublisherTool(),
            params={
                "packaged_products": package_data["packaged_products"],
                "credentials_file": GOOGLE_CREDENTIALS_FILE,
                "spreadsheet_id": GOOGLE_SPREADSHEET_ID,
                "sheet_name": AUDIO_PRODUCTS_SHEET,
                "api_key": ETSY_API_KEY,
                "shop_id": ETSY_SHOP_ID,
                "token_file": TOKEN_FILE,
                "create_drafts": create_drafts,
                "taxonomy_id": DEFAULT_TAXONOMY_ID,
                "currency": DEFAULT_CURRENCY,
            },
            validator=AudioPublishedValidator(),
        )

        if publish_result["success"]:
            pub_data = publish_result["data"]
            print(f"     Queue: {pub_data['queue_rows']} products saved to Sheets")
            if create_drafts:
                print(f"     Etsy drafts: {pub_data['drafts_created']} created")
            overall_success = True
        else:
            print(f"     Publish failed: {publish_result.get('error')}")

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

    from lib.big_brain.hooks import post_workflow_check
    post_workflow_check(db)

    print(f"\n{'=' * 60}")
    if overall_success:
        print(f"  RESULT : SUCCESS")
        print(f"  Check  : Google Sheets '{AUDIO_PRODUCTS_SHEET}' tab")
        if create_drafts:
            print(f"  Next   : Review drafts in Etsy Shop Manager > Listings > Drafts")
    else:
        print(f"  RESULT : FAILED")
        print(f"  Debug  : python scripts/show_logs.py {WORKFLOW_NAME} --last 1")
    print(f"  Run ID : {execution_id}")
    print(f"{'=' * 60}\n")

    return {"success": overall_success, "execution_id": execution_id}


if __name__ == "__main__":
    main()
