#!/usr/bin/env python3
"""
Test script: Run a single product through the Auto Listing Creator pipeline.

Bypasses Phase 1 (Google Sheets) and Phase 4 (Publish) by hardcoding a single
opportunity and printing the output. Tests Phase 2 (Claude content generation)
and Phase 3 (product image creation) if Playwright is available.

Usage:
    python scripts/test_single_product.py
"""

import sys
import os
import json
import uuid
import time
from datetime import datetime, timezone

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _project_root)
sys.path.insert(1, os.path.join(_project_root, "workflows", "auto_listing_creator"))

from config import DATABASE_PATH
from workflows.auto_listing_creator.config import (
    WORKFLOW_NAME, ANTHROPIC_API_KEY, ANTHROPIC_MODEL,
    FOCUS_NICHE, DEFAULT_CURRENCY, GEMINI_API_KEY,
)

from lib.common_tools.sqlite_client import SQLiteClient
from lib.orchestrator.execution_logger import ExecutionLogger
from workflows.auto_listing_creator.tools.generate_listing_content_tool import GenerateListingContentTool

# ── Single test opportunity ─────────────────────────────────────────────
TEST_OPPORTUNITY = {
    "product_title": "Tattoo Gift Certificate Template - Dark Luxury Gothic Style",
    "why": "Gift certificates are the #1 selling digital template for tattoo studios. "
           "High demand, low competition for premium dark/gothic aesthetic. "
           "Average seller price £4.99-£7.99. Buyers searching for editable, "
           "professional gift cards they can customise in Canva.",
    "suggested_price": 5.99,
    "priority": "HIGH",
    "effort": "LOW",
    "rank": 1,
    "target_keywords": [
        "tattoo gift certificate", "tattoo gift card template",
        "editable tattoo voucher", "tattoo studio gift card",
        "gothic gift certificate", "ink studio voucher",
    ],
}


def main():
    print(f"\n{'=' * 60}")
    print(f"  TEST: Single Product Pipeline")
    print(f"  Product: Tattoo Gift Certificate (Dark Luxury)")
    print(f"  Niche  : {FOCUS_NICHE}")
    print(f"  Model  : {ANTHROPIC_MODEL}")
    print(f"  Gemini : {'available' if GEMINI_API_KEY else 'not configured'}")
    print(f"{'=' * 60}")

    if not ANTHROPIC_API_KEY:
        print("\n  ERROR: ANTHROPIC_API_KEY not set in .env")
        return {"success": False}

    db = SQLiteClient(DATABASE_PATH)
    execution_id = str(uuid.uuid4())

    db.table("executions").insert({
        "id": execution_id, "workflow_id": f"{WORKFLOW_NAME}_test",
        "started_at": datetime.now(timezone.utc).isoformat(), "status": "running",
    }).execute()

    logger = ExecutionLogger(execution_id, f"{WORKFLOW_NAME}_test", db)

    try:
        # ── Phase 2: Generate listing content ─────────────────────────
        print(f"\n[Phase 2] Generating listing content with Claude...")
        print(f"  Sending opportunity to {ANTHROPIC_MODEL}...")

        logger.phase_start("Phase 2: Generate Content (Test)")
        tool = GenerateListingContentTool()
        start = time.time()
        result = tool.execute(
            opportunities=[TEST_OPPORTUNITY],
            anthropic_api_key=ANTHROPIC_API_KEY,
            model=ANTHROPIC_MODEL,
            focus_niche=FOCUS_NICHE,
            currency=DEFAULT_CURRENCY,
        )
        duration = int((time.time() - start) * 1000)
        logger.tool_result(tool.get_name(), result, result["success"], duration)
        logger.phase_end("Phase 2: Generate Content (Test)", result["success"])

        if not result["success"]:
            print(f"\n  FAILED: {result.get('error')}")
            return {"success": False}

        listings = result["data"]["generated_listings"]
        if not listings:
            print("\n  FAILED: No listings generated")
            return {"success": False}

        listing = listings[0]
        print(f"\n{'=' * 60}")
        print(f"  GENERATED LISTING")
        print(f"{'=' * 60}")
        print(f"\nTITLE ({len(listing['title'])} chars):")
        print(f"  {listing['title']}")
        print(f"\nPRICE: £{listing['price']}")
        print(f"\nPRODUCT TYPE: {listing.get('product_type', 'N/A')}")
        print(f"\nTAGS ({len(listing['tags'])}):")
        for i, tag in enumerate(listing["tags"], 1):
            print(f"  {i:2d}. {tag} ({len(tag)} chars)")
        print(f"\nBUNDLE TAGS: {listing.get('bundle_tags', [])}")
        print(f"\nDESCRIPTION:")
        print(f"  {listing['description'][:500]}...")
        print(f"  ... ({len(listing['description'])} chars total)")

        # Save full listing to JSON for review
        output_path = os.path.join(_project_root, "data", "test_listing_output.json")
        with open(output_path, "w") as f:
            json.dump(listing, f, indent=2)
        print(f"\n  Full listing saved to: {output_path}")

        # ── Phase 3: Product images (if Playwright available) ─────────
        try:
            from playwright.sync_api import sync_playwright
            playwright_ok = True
        except ImportError:
            playwright_ok = False

        if playwright_ok:
            print(f"\n[Phase 3] Creating product images...")
            from workflows.auto_listing_creator.tools.product_creator_tool import ProductCreatorTool

            logger.phase_start("Phase 3: Create Product (Test)")
            creator = ProductCreatorTool()
            start = time.time()
            create_result = creator.execute(
                generated_listings=[listing],
                anthropic_api_key=ANTHROPIC_API_KEY,
                model=ANTHROPIC_MODEL,
                focus_niche=FOCUS_NICHE,
                gemini_api_key=GEMINI_API_KEY,
            )
            duration = int((time.time() - start) * 1000)
            logger.tool_result(creator.get_name(), create_result, create_result["success"], duration)
            logger.phase_end("Phase 3: Create Product (Test)", create_result["success"])

            if create_result["success"]:
                cdata = create_result["data"]
                print(f"  Created: {cdata['created_count']}/{cdata['total_listings']} products")
                print(f"  Files in: {cdata['export_dir']}")
            else:
                print(f"  Image creation failed: {create_result.get('error')}")
                print(f"  (This is expected if Chromium browser is not installed)")
        else:
            print(f"\n[Phase 3] Skipped — Playwright not available")
            print(f"  Install with: pip install playwright && playwright install chromium")

        # ── Done ──────────────────────────────────────────────────────
        db.table("executions").update({
            "status": "completed",
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", execution_id).execute()

        print(f"\n{'=' * 60}")
        print(f"  RESULT: SUCCESS")
        print(f"  Review: data/test_listing_output.json")
        print(f"  Run ID: {execution_id}")
        print(f"{'=' * 60}\n")
        return {"success": True, "listing": listing}

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
        return {"success": False}

    finally:
        logger.flush()
        print(f"  Logs flushed to database")


if __name__ == "__main__":
    main()
