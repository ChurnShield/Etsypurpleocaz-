# =============================================================================
# workflows/auto_listing_creator/run_single_listing.py
#
# Single-listing runner -- bypasses Google Sheets Phase 1, injects one
# opportunity directly, runs Phase 2-4.
#
#   python3 workflows/auto_listing_creator/run_single_listing.py
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
    ETSY_API_KEY, ETSY_SHOP_ID,
    ANTHROPIC_API_KEY, ANTHROPIC_MODEL,
    GOOGLE_CREDENTIALS_FILE, GOOGLE_SPREADSHEET_ID,
    LISTING_QUEUE_SHEET, FOCUS_NICHE,
    DEFAULT_CURRENCY, DEFAULT_TAXONOMY_ID, TOKEN_FILE,
    IDEOGRAM_API_KEY,
)

from lib.common_tools.sqlite_client import SQLiteClient
from lib.orchestrator.execution_logger import ExecutionLogger

from tools.generate_listing_content_tool import GenerateListingContentTool
from tools.publish_listings_tool import PublishListingsTool
from tools.product_creator_tool import ProductCreatorTool

from validators.content_generated_validator import ContentGeneratedValidator
from validators.listings_published_validator import ListingsPublishedValidator
from validators.listing_quality_validator import ListingQualityValidator
from validators.image_quality_validator import ImageQualityValidator


# Real Canva buyer-template links for the Tattoo Studio Business Kit
TEMPLATE_LINKS = {
    "business_card": "https://www.canva.com/d/e21A6ZQJ3XcCIq-",
}

OPPORTUNITY = {
    "rank": 1,
    "product_title": "Tattoo Studio Business Kit",
    "why": (
        "Tattoo studio owners need a complete branding set -- gift certificates, "
        "appointment cards, price lists, aftercare cards, business cards -- all "
        "matching. Selling as a bundle kit captures higher AOV and reduces "
        "competition vs single-item listings."
    ),
    "suggested_price": 12.99,
    "priority": "HIGH",
    "effort": "MEDIUM",
    "target_keywords": [
        "tattoo business kit",
        "tattoo studio branding",
        "tattoo template bundle",
        "ink studio starter kit",
        "tattoo shop templates",
    ],
}


def _run_phase(logger, phase_name, tool, params, validator=None,
               max_retries=MAX_RETRIES):
    logger.phase_start(phase_name)
    log_params = {}
    for k, v in params.items():
        if k in ("api_key", "anthropic_api_key", "ideogram_api_key"):
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
            "description": "Auto Listing Creator -- single-listing run.",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "total_runs": 0, "successful_runs": 0, "failed_runs": 0,
        }).execute()


def main():
    print(f"\n{'=' * 60}")
    print(f"  SINGLE LISTING RUNNER")
    print(f"  Product : {OPPORTUNITY['product_title']}")
    print(f"  Price   : {OPPORTUNITY['suggested_price']} {DEFAULT_CURRENCY}")
    print(f"  Niche   : {FOCUS_NICHE}")
    print(f"  Model   : {ANTHROPIC_MODEL}")
    print(f"{'=' * 60}")

    if not ETSY_API_KEY or ETSY_API_KEY == ":":
        print("\n  ERROR: Etsy API credentials not set in .env")
        return
    if not ANTHROPIC_API_KEY:
        print("\n  ERROR: ANTHROPIC_API_KEY not set in .env")
        return

    create_drafts = os.path.exists(TOKEN_FILE)
    print(f"  Drafts  : {'Etsy draft + Sheets' if create_drafts else 'Sheets only (no OAuth)'}")
    print(f"  Token   : {TOKEN_FILE}")

    db = SQLiteClient(DATABASE_PATH)
    _ensure_workflow_registered(db, WORKFLOW_NAME)

    execution_id = str(uuid.uuid4())
    print(f"  Run ID  : {execution_id}")

    db.table("executions").insert({
        "id": execution_id, "workflow_id": WORKFLOW_NAME,
        "started_at": datetime.now(timezone.utc).isoformat(), "status": "running",
    }).execute()

    logger = ExecutionLogger(execution_id, WORKFLOW_NAME, db)
    overall_success = False

    try:
        # ==== PHASE 2: Generate listing content ====
        print(f"\n[1] Phase 2: Generating listing content with Claude...")
        generate_result = _run_phase(
            logger, "Phase 2: Generate Listing Content",
            tool=GenerateListingContentTool(),
            params={
                "opportunities": [OPPORTUNITY],
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

        # Inject real Canva template links into the generated listing
        for gl in gen_data.get("generated_listings", []):
            gl["template_links"] = TEMPLATE_LINKS

        # ==== PHASE 2-QA: Listing quality ====
        print(f"\n[2] Validating listing quality...")
        lq_validator = ListingQualityValidator()
        listing_qa = lq_validator.validate(gen_data)
        logger.validation_event(lq_validator.get_name(), listing_qa["passed"], listing_qa["issues"])
        listing_avg_score = listing_qa["metadata"].get("average_score", 0)
        print(f"     Quality score: {listing_avg_score}/100")
        for issue in listing_qa["issues"][:5]:
            print(f"       - {issue}")

        # ==== PHASE 3: Create product images ====
        image_map = {}
        pdf_map = {}
        print(f"\n[3] Phase 3: Creating product images...")
        create_result = _run_phase(
            logger, "Phase 3: Create Products",
            tool=ProductCreatorTool(),
            params={
                "generated_listings": gen_data["generated_listings"],
                "anthropic_api_key": ANTHROPIC_API_KEY,
                "model": ANTHROPIC_MODEL,
                "focus_niche": FOCUS_NICHE,
                "ideogram_api_key": IDEOGRAM_API_KEY,
            },
        )

        image_qa_meta = {}
        if create_result["success"]:
            create_data = create_result["data"]
            print(f"     Created: {create_data['created_count']}/{create_data['total_listings']} products")
            image_map = {int(k): v for k, v in create_data.get("image_map", {}).items()}
            pdf_map = {int(k): v for k, v in create_data.get("pdf_map", {}).items()}

            print(f"\n[3-QA] Validating image quality...")
            iq_validator = ImageQualityValidator()
            image_qa = iq_validator.validate(create_data)
            logger.validation_event(iq_validator.get_name(), image_qa["passed"], image_qa["issues"])
            image_qa_meta = image_qa["metadata"]
            print(f"     Image pass rate: {image_qa_meta.get('images_passed', 0)}"
                  f"/{image_qa_meta.get('images_checked', 0)}")
            for issue in image_qa["issues"][:5]:
                print(f"       - {issue}")
        else:
            print(f"     Image creation failed: {create_result.get('error')}")
            print(f"     Continuing without images...")

        # ==== PHASE 4: Publish (Sheets + Etsy draft) ====
        print(f"\n[4] Phase 4: Publishing to Etsy + Sheets...")
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
            print(f"     Sheets: {pub_data['queue_rows']} rows saved")
            print(f"     Etsy drafts: {pub_data['drafts_created']} created")
            print(f"     Images uploaded: {pub_data.get('images_uploaded', 0)}")
            if pub_data["draft_errors"] > 0:
                print(f"     Draft errors: {pub_data['draft_errors']}")
            overall_success = pub_data["drafts_created"] > 0
        else:
            print(f"     Publish failed: {publish_result.get('error')}")

        # ==== Report ====
        print(f"\n{'_' * 60}")
        img_score = image_qa_meta.get("score", 0)
        combined = round(listing_avg_score * 0.7 + img_score * 0.3, 1)
        print(f"  Listing quality : {listing_avg_score}/100")
        print(f"  Image quality   : {img_score}/100")
        print(f"  Combined score  : {combined}/100")

        if gen_data.get("generated_listings"):
            listing = gen_data["generated_listings"][0]
            print(f"\n  TITLE: {listing['title']}")
            print(f"  TAGS:  {', '.join(listing.get('tags', []))}")
            print(f"  PRICE: {listing.get('price')} {DEFAULT_CURRENCY}")
            print(f"  TYPE:  {listing.get('product_type')}")
        print(f"{'_' * 60}")

        db.table("executions").update({
            "status": "completed" if overall_success else "failed",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "outcome_quality": combined,
        }).eq("id", execution_id).execute()

    except Exception as exc:
        logger.error(str(exc))
        db.table("executions").update({
            "status": "failed",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "error_message": str(exc),
        }).eq("id", execution_id).execute()
        print(f"\n  ERROR: {exc}")
        import traceback
        traceback.print_exc()

    finally:
        logger.flush()
        print(f"\n  Logs flushed to database")

    print(f"\n{'=' * 60}")
    if overall_success:
        print(f"  RESULT: SUCCESS")
        print(f"  Next: Review draft in Etsy Shop Manager > Listings > Drafts")
    else:
        print(f"  RESULT: FAILED (check output above)")
    print(f"  Run ID: {execution_id}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
