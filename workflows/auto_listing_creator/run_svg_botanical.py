# =============================================================================
# workflows/auto_listing_creator/run_svg_botanical.py
#
# Standalone entry point for the Fine-Line Botanical SVG/PNG Bundle pipeline.
#
#   python workflows/auto_listing_creator/run_svg_botanical.py
#
# Pipeline:
#   Phase 1  (Generate)  -> Create all SVG designs from registry
#   Phase 2  (Convert)   -> SVG -> PNG, DXF, PDF, EPS
#   Phase 3  (Package)   -> ZIP bundle with LICENSE, README, guide
#   Phase 4  (Thumbnails)-> 5 Etsy listing images
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

from config import DATABASE_PATH, MAX_RETRIES, PLAYWRIGHT_PAGE_TIMEOUT_MS

from lib.common_tools.sqlite_client import SQLiteClient
from lib.orchestrator.execution_logger import ExecutionLogger

from tools.svg_botanical.svg_generator_tool import SvgGeneratorTool
from tools.svg_botanical.format_converter_tool import FormatConverterTool
from tools.svg_botanical.bundle_packager_tool import BundlePackagerTool
from tools.svg_botanical.thumbnail_generator_tool import ThumbnailGeneratorTool

WORKFLOW_NAME = "svg_botanical_bundle"
OUTPUT_DIR = os.path.join(_here, "exports", "svg_bundles")


def _run_phase(logger, phase_name, tool, params, max_retries=MAX_RETRIES):
    """Execute a tool with retries and logging."""
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
        step_success = True
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
            "description": "Fine-Line Botanical SVG/PNG Bundle - generates designs, converts formats, packages for Etsy.",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "total_runs": 0, "successful_runs": 0, "failed_runs": 0,
        }).execute()
        print(f"  Registered workflow: '{wid}'")


def _update_workflow_stats(db, wid, success):
    rows = db.table("workflows").select(
        "total_runs, successful_runs, failed_runs"
    ).eq("id", wid).execute()
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
    print(f"  Workflow : {WORKFLOW_NAME}")
    print(f"  Product  : Fine-Line Botanical Tattoo SVG/PNG Bundle")
    print(f"  Output   : {OUTPUT_DIR}")
    print(f"{'=' * 60}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    db = SQLiteClient(DATABASE_PATH)
    print(f"\n[1] Connected to database")
    _ensure_workflow_registered(db, WORKFLOW_NAME)
    print(f"[2] Workflow registered")

    execution_id = str(uuid.uuid4())
    print(f"[3] Execution ID: {execution_id}")

    db.table("executions").insert({
        "id": execution_id, "workflow_id": WORKFLOW_NAME,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "status": "running",
    }).execute()

    logger = ExecutionLogger(execution_id, WORKFLOW_NAME, db)
    overall_success = False

    try:
        # ==== PHASE 1: Generate SVG designs ====
        print(f"\n[4a] Phase 1: Generating SVG designs...")
        gen_result = _run_phase(
            logger, "Phase 1: Generate SVGs",
            tool=SvgGeneratorTool(),
            params={"output_dir": OUTPUT_DIR},
        )

        if not gen_result["success"]:
            raise RuntimeError(
                f"Phase 1 failed: {gen_result.get('error')}")

        gen_data = gen_result["data"]
        svg_dir = gen_data["svg_dir"]
        design_count = gen_data["generated_count"]
        category_counts = gen_data["category_counts"]
        print(f"     Generated: {design_count} SVGs")
        print(f"     Categories: {category_counts}")

        # ==== PHASE 2: Convert to PNG, DXF, PDF, EPS ====
        print(f"\n[4b] Phase 2: Converting to PNG, DXF, PDF, EPS...")
        conv_result = _run_phase(
            logger, "Phase 2: Format Conversion",
            tool=FormatConverterTool(),
            params={
                "svg_dir": svg_dir,
                "output_dir": OUTPUT_DIR,
                "formats": ["png", "dxf", "pdf", "eps"],
            },
        )

        if not conv_result["success"]:
            raise RuntimeError(
                f"Phase 2 failed: {conv_result.get('error')}")

        conv_data = conv_result["data"]
        print(f"     Conversions: {conv_data['conversions']}")
        if conv_data["error_count"] > 0:
            print(f"     Errors: {conv_data['error_count']}")

        # ==== PHASE 3: Package ZIP bundle ====
        print(f"\n[4c] Phase 3: Packaging ZIP bundle...")
        pkg_result = _run_phase(
            logger, "Phase 3: Bundle Packaging",
            tool=BundlePackagerTool(),
            params={
                "output_dir": OUTPUT_DIR,
                "design_count": design_count,
                "category_counts": category_counts,
            },
        )

        if not pkg_result["success"]:
            raise RuntimeError(
                f"Phase 3 failed: {pkg_result.get('error')}")

        pkg_data = pkg_result["data"]
        print(f"     ZIP: {pkg_data['zip_path']}")
        print(f"     Size: {pkg_data['zip_size_mb']} MB")

        # ==== PHASE 4: Generate Etsy thumbnails ====
        print(f"\n[4d] Phase 4: Generating Etsy listing thumbnails...")
        thumb_result = _run_phase(
            logger, "Phase 4: Thumbnail Generation",
            tool=ThumbnailGeneratorTool(),
            params={
                "svg_dir": svg_dir,
                "output_dir": OUTPUT_DIR,
                "design_count": design_count,
                "category_counts": category_counts,
            },
        )

        if thumb_result["success"]:
            thumb_data = thumb_result["data"]
            print(f"     Thumbnails: {thumb_data['count']} pages generated")
            overall_success = True
        else:
            # Thumbnails are nice-to-have; bundle is still usable
            print(f"     Thumbnails failed: {thumb_result.get('error')}")
            print(f"     (Bundle is still complete without thumbnails)")
            overall_success = True  # Bundle itself succeeded

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
        print(f"  RESULT   : SUCCESS")
        print(f"  Bundle   : {os.path.join(OUTPUT_DIR, 'PurpleOcaz-Fine-Line-Botanical-Bundle.zip')}")
        print(f"  SVGs     : {design_count} designs")
        print(f"  Formats  : SVG, PNG, DXF, PDF, EPS")
    else:
        print(f"  RESULT   : FAILED")
        print(f"  Debug    : python scripts/show_logs.py {WORKFLOW_NAME} --last 1")
    print(f"  Run ID   : {execution_id}")
    print(f"{'=' * 60}\n")

    return {"success": overall_success, "execution_id": execution_id}


if __name__ == "__main__":
    main()
