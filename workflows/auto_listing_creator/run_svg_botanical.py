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

from config import (
    DATABASE_PATH, GEMINI_API_KEY, MAX_RETRIES, PLAYWRIGHT_PAGE_TIMEOUT_MS,
    REPLICATE_API_TOKEN, SVG_IMAGE_PROVIDER,
)

from lib.common_tools.sqlite_client import SQLiteClient
from lib.orchestrator.execution_logger import ExecutionLogger

from tools.svg_botanical.svg_generator_tool import SvgGeneratorTool
from tools.svg_botanical.ai_design_generator_tool import AiDesignGeneratorTool
from tools.svg_botanical.format_converter_tool import FormatConverterTool
from tools.svg_botanical.bundle_packager_tool import BundlePackagerTool
from tools.svg_botanical.thumbnail_generator_tool import ThumbnailGeneratorTool

WORKFLOW_NAME = "svg_botanical_bundle"
OUTPUT_DIR = os.path.join(_here, "exports", "svg_bundles")

# ── Generator mode toggle ──
# Set SVG_GENERATOR_MODE=code to fall back to code-generated designs
USE_AI_GENERATOR = os.getenv("SVG_GENERATOR_MODE", "ai").lower() == "ai"
CATEGORY_FILTER = os.getenv("SVG_CATEGORY_FILTER", "")


def _run_phase(logger, phase_name, tool, params, max_retries=MAX_RETRIES):
    """Execute a tool with retries and logging."""
    logger.phase_start(phase_name)
    log_params = {}
    for k, v in params.items():
        if k in ("api_key", "anthropic_api_key", "gemini_api_key",
                 "image_api_key"):
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
    print(f"  Workflow  : {WORKFLOW_NAME}")
    print(f"  Product   : Fine-Line Botanical Tattoo SVG/PNG Bundle")
    print(f"  Generator : {'AI (Gemini + potrace)' if USE_AI_GENERATOR else 'Code (svgwrite)'}")
    print(f"  Thumbnails: {'AI (Nano Banana 3.1)' if GEMINI_API_KEY else 'HTML/Playwright'}")
    if CATEGORY_FILTER:
        print(f"  Filter    : {CATEGORY_FILTER}")
    print(f"  Output    : {OUTPUT_DIR}")
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
        if USE_AI_GENERATOR:
            # Resolve image API key based on provider
            _image_key = (REPLICATE_API_TOKEN if SVG_IMAGE_PROVIDER == "replicate"
                          else GEMINI_API_KEY)
            if not _image_key:
                raise RuntimeError(
                    f"{'REPLICATE_API_TOKEN' if SVG_IMAGE_PROVIDER == 'replicate' else 'GEMINI_API_KEY'} "
                    f"required for AI generator (provider={SVG_IMAGE_PROVIDER}). "
                    "Set SVG_GENERATOR_MODE=code to use code fallback.")
            print(f"\n[4a] Phase 1: Generating SVG designs "
                  f"(AI/{SVG_IMAGE_PROVIDER})...")
            gen_params = {
                "output_dir": OUTPUT_DIR,
                "image_api_key": _image_key,
            }
            if CATEGORY_FILTER:
                gen_params["category_filter"] = CATEGORY_FILTER
            gen_result = _run_phase(
                logger, "Phase 1: Generate SVGs (AI)",
                tool=AiDesignGeneratorTool(),
                params=gen_params,
                max_retries=1,
            )
        else:
            print(f"\n[4a] Phase 1: Generating SVG designs (code)...")
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
                "gemini_api_key": GEMINI_API_KEY,
            },
        )

        if thumb_result["success"]:
            thumb_data = thumb_result["data"]
            method = thumb_data.get("method", "unknown")
            print(f"     Thumbnails: {thumb_data['count']} pages generated ({method})")
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

    # Auto-open review page in browser
    if overall_success:
        review_path = _build_review_page(OUTPUT_DIR, design_count, category_counts)
        print(f"[8] Opening review page: {review_path}")
        import webbrowser
        webbrowser.open(f"file:///{review_path.replace(os.sep, '/')}")

    return {"success": overall_success, "execution_id": execution_id}


def _build_review_page(output_dir, design_count, category_counts):
    """Generate an HTML review page and return its path."""
    thumb_dir = os.path.join(output_dir, "thumbnails")
    svg_dir = os.path.join(output_dir, "svg")

    # Thumbnail images
    thumb_imgs = ""
    for f in sorted(os.listdir(thumb_dir)):
        if f.endswith(".png"):
            p = os.path.join(thumb_dir, f).replace(os.sep, "/")
            thumb_imgs += (
                f'<div style="text-align:center">'
                f'<img src="file:///{p}" style="width:360px;border-radius:8px;'
                f'box-shadow:0 4px 20px rgba(0,0,0,0.3)">'
                f'<div style="margin-top:8px;font-size:14px;color:#888">{f}</div>'
                f'</div>\n'
            )

    # Sample SVGs (first 2 per category)
    svg_previews = ""
    for cat in sorted(os.listdir(svg_dir)):
        cat_path = os.path.join(svg_dir, cat)
        if not os.path.isdir(cat_path):
            continue
        files = sorted(f for f in os.listdir(cat_path) if f.endswith(".svg"))
        for f in files[:2]:
            p = os.path.join(cat_path, f).replace(os.sep, "/")
            svg_previews += (
                f'<div style="background:#fff;border-radius:8px;padding:12px;'
                f'text-align:center">'
                f'<img src="file:///{p}" style="width:180px;height:180px">'
                f'<div style="font-size:12px;color:#888;margin-top:4px">'
                f'{cat}/{f}</div></div>\n'
            )

    html = f"""<!DOCTYPE html><html><head>
    <title>Bundle Review - {design_count} Designs</title>
    <style>
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ background:#111; color:#eee; font-family:system-ui; padding:40px; }}
    h1 {{ font-size:28px; margin-bottom:8px; }}
    h2 {{ font-size:20px; color:#C9A84C; margin:40px 0 16px; }}
    .stats {{ color:#888; margin-bottom:30px; }}
    .thumbs {{ display:flex; gap:20px; flex-wrap:wrap; }}
    .svgs {{ display:grid; grid-template-columns:repeat(auto-fill,210px);
             gap:12px; }}
    </style></head><body>
    <h1>Bundle Review</h1>
    <div class="stats">{design_count} designs &middot; 5 formats &middot;
    {design_count * 5} total files</div>
    <h2>Etsy Listing Thumbnails</h2>
    <div class="thumbs">{thumb_imgs}</div>
    <h2>Sample Designs (2 per category)</h2>
    <div class="svgs">{svg_previews}</div>
    </body></html>"""

    review_path = os.path.join(output_dir, "_review.html")
    with open(review_path, "w", encoding="utf-8") as f:
        f.write(html)
    return review_path


if __name__ == "__main__":
    main()
