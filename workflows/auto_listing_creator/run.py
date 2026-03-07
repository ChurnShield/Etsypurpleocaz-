# =============================================================================
# workflows/auto_listing_creator/run.py
#
# Entry point for the Auto Listing Creator workflow.
#
#   python workflows/auto_listing_creator/run.py
#
# Pipeline:
#   Phase 1  (Load)     -> Read opportunities from Tattoo Trend Monitor
#                            |
#   Phase 2  (Generate) -> Claude creates full listing content (anti-gravity keywords)
#                            |
#   Phase 2b (Bundle)   -> Auto-group products into value bundles (optional)
#                            |
#   Phase 3  (Create)   -> Generate product images (HTML templates + Playwright)
#                            |
#   Phase 4  (Publish)  -> Save to Sheets + create Etsy drafts + upload images
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
    LISTING_QUEUE_SHEET, FOCUS_NICHE,
    DEFAULT_CURRENCY, DEFAULT_TAXONOMY_ID, TOKEN_FILE,
    CANVA_CLIENT_ID, CANVA_CLIENT_SECRET,
    GEMINI_API_KEY, IDEOGRAM_API_KEY,
    TIER1_IMAGE_PROVIDER,
    PROPOSAL_THRESHOLD_RUNS,
    ENABLE_BUNDLES, MIN_BUNDLE_SIZE,
)

from lib.common_tools.sqlite_client import SQLiteClient
from lib.orchestrator.execution_logger import ExecutionLogger

from tools.load_opportunities_tool      import LoadOpportunitiesTool
from tools.generate_listing_content_tool import GenerateListingContentTool
from tools.bundle_creator_tool           import BundleCreatorTool
from tools.publish_listings_tool         import PublishListingsTool
from tools.product_creator_tool          import ProductCreatorTool
from tools.canva_export_tool             import CanvaExportTool

from validators.opportunities_loaded_validator import OpportunitiesLoadedValidator
from validators.content_generated_validator    import ContentGeneratedValidator
from validators.listings_published_validator   import ListingsPublishedValidator


def _run_phase(logger, phase_name, tool, params, validator=None, max_retries=MAX_RETRIES):
    logger.phase_start(phase_name)
    log_params = {}
    for k, v in params.items():
        if k in ("api_key", "anthropic_api_key", "gemini_api_key", "ideogram_api_key"):
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
            "description": "Auto Listing Creator - generates and publishes new Etsy listings from Trend Monitor opportunities.",
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
    nano_banana_enabled = bool(GEMINI_API_KEY) or bool(IDEOGRAM_API_KEY)

    print(f"\n{'=' * 60}")
    print(f"  Workflow  : {WORKFLOW_NAME}")
    print(f"  Shop ID   : {ETSY_SHOP_ID}")
    print(f"  Niche     : {FOCUS_NICHE}")
    print(f"  Model     : {ANTHROPIC_MODEL}")
    print(f"  Currency  : {DEFAULT_CURRENCY}")
    nano_status = "enabled" if nano_banana_enabled else "disabled (no key)"
    provider_label = TIER1_IMAGE_PROVIDER if nano_banana_enabled else "none"
    print(f"  NanoBanana: {nano_status} (provider: {provider_label})")
    bundle_status = "enabled" if ENABLE_BUNDLES else "disabled"
    print(f"  Bundles   : {bundle_status} (min {MIN_BUNDLE_SIZE} items)")
    print(f"{'=' * 60}")

    if not ETSY_API_KEY or ETSY_API_KEY == ":":
        print("\n  ERROR: Etsy API credentials not set in .env")
        return {"success": False}
    if not ANTHROPIC_API_KEY:
        print("\n  ERROR: ANTHROPIC_API_KEY not set in .env")
        return {"success": False}

    pdf_map = {}  # listing index -> PDF path (for digital file upload)

    # Check if Etsy draft creation is possible
    create_drafts = os.path.exists(TOKEN_FILE)
    if create_drafts:
        print(f"  Drafts    : Will attempt Etsy draft creation")
    else:
        print(f"  Drafts    : Sheets only (no OAuth token)")

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
        # ==== PHASE 1: Load opportunities ====
        print(f"\n[4a] Phase 1: Loading opportunities from Trend Monitor...")
        load_result = _run_phase(
            logger, "Phase 1: Load Opportunities",
            tool=LoadOpportunitiesTool(),
            params={
                "credentials_file": GOOGLE_CREDENTIALS_FILE,
                "spreadsheet_id": GOOGLE_SPREADSHEET_ID,
                "opportunities_sheet_name": "Tattoo Opportunities",
                "market_intel_sheet_name": "Market Intelligence",
                "api_key": ETSY_API_KEY,
                "shop_id": ETSY_SHOP_ID,
                "page_limit": ETSY_PAGE_LIMIT,
            },
            validator=OpportunitiesLoadedValidator(),
        )

        if not load_result["success"]:
            raise RuntimeError(f"Phase 1 failed: {load_result.get('error')}")

        load_data = load_result["data"]
        opportunities = load_data["opportunities"]
        print(f"     Loaded: {load_data['total_loaded']} opportunities")
        print(f"     New: {len(opportunities)} (skipped {load_data['skipped_duplicates']} duplicates)")

        # ==== PHASE 2: Generate listing content ====
        print(f"\n[4b] Phase 2: Generating listing content with Claude...")
        generate_result = _run_phase(
            logger, "Phase 2: Generate Listing Content",
            tool=GenerateListingContentTool(),
            params={
                "opportunities": opportunities,
                "anthropic_api_key": ANTHROPIC_API_KEY,
                "model": ANTHROPIC_MODEL,
                "focus_niche": FOCUS_NICHE,
                "currency": DEFAULT_CURRENCY,
            },
            validator=ContentGeneratedValidator(),
        )

        if not generate_result["success"]:
            raise RuntimeError(f"Phase 2 failed: {generate_result.get('error')}")

        gen_data = generate_result["data"]
        gen_stats = gen_data["stats"]
        print(f"     Generated: {gen_stats['listings_generated']}/{gen_stats['total_opportunities']}")
        if gen_stats["failed"] > 0:
            print(f"     Failed: {gen_stats['failed']}")

        # ==== PHASE 2b: Auto-bundle creation (Anti-Gravity) ====
        all_listings = gen_data["generated_listings"]

        if ENABLE_BUNDLES and len(all_listings) >= MIN_BUNDLE_SIZE:
            print(f"\n[4b+] Phase 2b: Creating bundles (Anti-Gravity)...")
            bundle_result = _run_phase(
                logger, "Phase 2b: Bundle Creation",
                tool=BundleCreatorTool(),
                params={
                    "generated_listings": all_listings,
                    "anthropic_api_key": ANTHROPIC_API_KEY,
                    "model": ANTHROPIC_MODEL,
                    "focus_niche": FOCUS_NICHE,
                    "currency": DEFAULT_CURRENCY,
                    "min_bundle_size": MIN_BUNDLE_SIZE,
                },
            )

            if bundle_result["success"]:
                bundle_data = bundle_result["data"]
                bundles = bundle_data.get("bundles", [])
                b_stats = bundle_data.get("stats", {})
                print(f"     Bundles created: {b_stats.get('bundles_created', 0)}")
                print(f"     Items bundled: {b_stats.get('total_items_bundled', 0)}")

                # Append bundle listings to the main listings array
                for bundle in bundles:
                    bundle_listing = {
                        "title": bundle.get("title", ""),
                        "description": bundle.get("description", ""),
                        "tags": bundle.get("tags", []),
                        "price": bundle.get("bundle_price", 9.99),
                        "product_type": bundle.get("product_type", "bundle"),
                        "bundle_tags": [],
                        "source_rank": 0,
                        "source_priority": "HIGH",
                        "source_effort": "LOW",
                        "source_why": (
                            f"Anti-Gravity bundle: {bundle['tier']} tier, "
                            f"{bundle['item_count']} items, "
                            f"save {bundle['savings_pct']}%"
                        ),
                        "is_bundle": True,
                        "bundle_item_titles": bundle.get("item_titles", []),
                    }
                    all_listings.append(bundle_listing)

                # Update gen_data to include bundles
                gen_data["generated_listings"] = all_listings
                gen_data["stats"]["bundles_created"] = len(bundles)
            else:
                print(f"     Bundle creation skipped: {bundle_result.get('error')}")
        else:
            if not ENABLE_BUNDLES:
                print(f"\n[4b+] Bundles: disabled in config")
            else:
                print(f"\n[4b+] Bundles: not enough listings ({len(all_listings)} < {MIN_BUNDLE_SIZE})")

        # ==== PHASE 3: Create product images ====
        image_map = {}  # index -> list of png paths
        print(f"\n[4c] Phase 3: Creating product images...")
        create_result = _run_phase(
            logger, "Phase 3: Create Products",
            tool=ProductCreatorTool(),
            params={
                "generated_listings": gen_data["generated_listings"],
                "anthropic_api_key": ANTHROPIC_API_KEY,
                "model": ANTHROPIC_MODEL,
                "focus_niche": FOCUS_NICHE,
                "gemini_api_key": GEMINI_API_KEY,
                "ideogram_api_key": IDEOGRAM_API_KEY,
                "tier1_provider": TIER1_IMAGE_PROVIDER,
            },
        )

        if create_result["success"]:
            create_data = create_result["data"]
            print(f"     Created: {create_data['created_count']}/{create_data['total_listings']} products")
            print(f"     Files in: {create_data['export_dir']}")
            # Use the image_map and pdf_map from the product creator
            image_map = create_data.get("image_map", {})
            # Convert string keys back to int (JSON serialisation quirk)
            image_map = {int(k): v for k, v in image_map.items()}
            pdf_map = create_data.get("pdf_map", {})
            pdf_map = {int(k): v for k, v in pdf_map.items()}
        else:
            print(f"     Product creation failed: {create_result.get('error')}")
            print(f"     Continuing without images...")

        # ==== PHASE 4: Publish (Sheets + Etsy drafts + upload images) ====
        print(f"\n[4d] Phase 4: Publishing listings...")
        publish_result = _run_phase(
            logger, "Phase 4: Publish Listings",
            tool=PublishListingsTool(),
            params={
                "generated_listings": gen_data["generated_listings"],
                "credentials_file": GOOGLE_CREDENTIALS_FILE,
                "spreadsheet_id": GOOGLE_SPREADSHEET_ID,
                "queue_sheet_name": LISTING_QUEUE_SHEET,
                "api_key": ETSY_API_KEY,
                "shop_id": ETSY_SHOP_ID,
                "token_file": TOKEN_FILE,
                "create_drafts": create_drafts,
                "taxonomy_id": DEFAULT_TAXONOMY_ID,
                "currency": DEFAULT_CURRENCY,
                "image_map": image_map,
                "pdf_map": pdf_map,
            },
            validator=ListingsPublishedValidator(),
        )

        if publish_result["success"]:
            pub_data = publish_result["data"]
            print(f"     Queue: {pub_data['queue_rows']} listings saved to Sheets")
            if create_drafts:
                print(f"     Etsy drafts: {pub_data['drafts_created']} created")
                print(f"     Images uploaded: {pub_data.get('images_uploaded', 0)}")
                if pub_data["draft_errors"] > 0:
                    print(f"     Draft errors: {pub_data['draft_errors']}")
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

    # ── 7b. BigBrain system health check ─────────────────────────────────
    from lib.big_brain.hooks import post_workflow_check
    post_workflow_check(db)

    print(f"\n{'=' * 60}")
    if overall_success:
        print(f"  RESULT : SUCCESS")
        print(f"  Check  : Google Sheets '{LISTING_QUEUE_SHEET}' tab")
        if create_drafts:
            print(f"  Next   : Review drafts in Etsy Shop Manager > Listings > Drafts")
            print(f"           Product images auto-created and uploaded")
    else:
        print(f"  RESULT : FAILED")
        print(f"  Debug  : python scripts/show_logs.py {WORKFLOW_NAME} --last 1")
    print(f"  Run ID : {execution_id}")
    print(f"{'=' * 60}\n")

    return {"success": overall_success, "execution_id": execution_id}


if __name__ == "__main__":
    main()
