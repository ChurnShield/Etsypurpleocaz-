"""
AI News Workflow Runner
========================
Fetches AI news from an RSS feed, filters to the last 24 hours,
and saves the results to Airtable.

HOW TO RUN:
    cd "c:\\Users\\andyn\\OneDrive\\Desktop\\NEW AI PROJECT"
    python -m workflows.ai_news_workflow.run

BEFORE RUNNING:
    1. pip install feedparser
    2. python scripts/init_db.py  (if you haven't already)
    3. Add to your .env file:
           RSS_FEED_URL=https://your-rss-feed-url.com/feed
           AIRTABLE_API_KEY=pat-xxxxx
           AIRTABLE_BASE_ID=appxxxxx
           AIRTABLE_TABLE_NAME=AI News
    4. Create the Airtable table (see config.py for field setup)

WHAT HAPPENS:
    Phase 1 (FETCH):  Download all articles from the RSS feed
    Phase 2 (FILTER): Keep only articles from the last 24 hours
    Phase 3 (SAVE):   Send filtered articles to Airtable

    Every step is logged to data/system.db by the ExecutionLogger.
    After enough runs, the SmallBrain can analyze patterns.
"""

import uuid
import sys
import os
from datetime import datetime

# ── Setup: Add project root to path ──
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# ── Import config (never hardcode these!) ──
from workflows.ai_news_workflow.config import (
    WORKFLOW_NAME,
    DATABASE_PATH,
    RSS_FEED_URL,
    AIRTABLE_API_KEY,
    AIRTABLE_BASE_ID,
    AIRTABLE_TABLE_NAME,
    HOURS_RECENT,
    MAX_RETRIES,
)

# ── Import the orchestrator components ──
from lib.orchestrator.execution_logger import ExecutionLogger
from lib.common_tools.sqlite_client import SQLiteClient

# ── Import tools ──
from workflows.ai_news_workflow.tools.fetch_rss_tool import FetchRSSTool
from workflows.ai_news_workflow.tools.filter_recent_tool import FilterRecentTool
from workflows.ai_news_workflow.tools.save_to_airtable_tool import SaveToAirtableTool

# ── Import validators ──
from workflows.ai_news_workflow.validators.articles_fetched_validator import ArticlesFetchedValidator
from workflows.ai_news_workflow.validators.valid_dates_validator import ValidDatesValidator
from workflows.ai_news_workflow.validators.airtable_save_validator import AirtableSaveValidator


def main():
    """Run the AI News workflow."""

    # ── Step 1: Connect to the database ──
    print(f"Connecting to database: {DATABASE_PATH}")
    db = SQLiteClient(DATABASE_PATH)

    # ── Step 2: Generate a unique execution ID ──
    execution_id = str(uuid.uuid4())
    print(f"Workflow:     {WORKFLOW_NAME}")
    print(f"Execution ID: {execution_id}")
    print(f"RSS Feed:     {RSS_FEED_URL}")
    print(f"Filter:       Last {HOURS_RECENT} hours")
    print()

    # ── Step 3: Record this execution in the database ──
    db.table('executions').insert({
        'id': execution_id,
        'workflow_id': WORKFLOW_NAME,
        'started_at': datetime.utcnow().isoformat(),
        'status': 'running',
        'input_summary': f"RSS: {RSS_FEED_URL}, Filter: {HOURS_RECENT}h",
    }).execute()

    # ── Step 4: Create tools and validators ──
    fetch_tool = FetchRSSTool()
    filter_tool = FilterRecentTool()
    save_tool = SaveToAirtableTool()

    articles_validator = ArticlesFetchedValidator(min_articles=1)
    dates_validator = ValidDatesValidator()
    save_validator = AirtableSaveValidator()

    # ── Step 5: Create the ExecutionLogger ──
    logger = ExecutionLogger(execution_id, WORKFLOW_NAME, db)

    # Track results across phases so each phase can use the previous output
    fetched_articles = []
    filtered_articles = []
    overall_success = True
    import time

    try:
        # ══════════════════════════════════════════════════════
        # PHASE 1: FETCH - Get articles from the RSS feed
        # ══════════════════════════════════════════════════════
        print("=" * 55)
        print("PHASE 1: FETCH - Getting articles from RSS feed...")
        print("=" * 55)
        logger.phase_start("FETCH")

        # Log the tool call (what we're about to do)
        fetch_params = {'feed_url': RSS_FEED_URL}
        logger.tool_call(fetch_tool.get_name(), fetch_params)

        # Run the tool and measure how long it takes
        start = time.time()
        fetch_result = fetch_tool.execute(**fetch_params)
        duration = int((time.time() - start) * 1000)

        # Log the tool result (what happened)
        logger.tool_result(
            fetch_tool.get_name(),
            fetch_result,
            fetch_result['success'],
            duration
        )

        if fetch_result['success']:
            fetched_articles = fetch_result['data']
            print(f"  Fetched {len(fetched_articles)} articles ({duration}ms)")
        else:
            print(f"  FAILED: {fetch_result['error']}")

        # Validate the fetch result
        validation = articles_validator.validate(fetch_result)
        logger.validation_event(
            articles_validator.get_name(),
            validation['passed'],
            validation.get('issues', [])
        )

        if not validation['passed']:
            print(f"  Validation FAILED: {validation['issues']}")
            logger.phase_end("FETCH", success=False)
            overall_success = False
        else:
            print(f"  Validation passed: {len(fetched_articles)} articles OK")
            logger.phase_end("FETCH", success=True)

        # ══════════════════════════════════════════════════════
        # PHASE 2: FILTER - Keep only recent articles
        # ══════════════════════════════════════════════════════
        if overall_success:
            print()
            print("=" * 55)
            print(f"PHASE 2: FILTER - Keeping articles from last {HOURS_RECENT}h...")
            print("=" * 55)
            logger.phase_start("FILTER")

            filter_params = {
                'articles': fetched_articles,
                'hours': HOURS_RECENT,
            }
            logger.tool_call(filter_tool.get_name(), {'hours': HOURS_RECENT, 'article_count': len(fetched_articles)})

            start = time.time()
            filter_result = filter_tool.execute(**filter_params)
            duration = int((time.time() - start) * 1000)

            logger.tool_result(
                filter_tool.get_name(),
                filter_result,
                filter_result['success'],
                duration
            )

            if filter_result['success']:
                filtered_articles = filter_result['data']
                print(f"  {len(fetched_articles)} -> {len(filtered_articles)} articles after filter ({duration}ms)")
            else:
                print(f"  FAILED: {filter_result['error']}")

            # Validate dates
            validation = dates_validator.validate(filter_result)
            logger.validation_event(
                dates_validator.get_name(),
                validation['passed'],
                validation.get('issues', [])
            )

            if not validation['passed']:
                print(f"  Validation FAILED: {validation['issues']}")
                logger.phase_end("FILTER", success=False)
                overall_success = False
            else:
                print(f"  Validation passed: dates look good")
                logger.phase_end("FILTER", success=True)

            # Handle case where filter removed everything
            if overall_success and len(filtered_articles) == 0:
                print(f"  No articles from the last {HOURS_RECENT} hours.")
                print("  This is normal if nothing was published recently.")

        # ══════════════════════════════════════════════════════
        # PHASE 3: SAVE - Send to Airtable
        # ══════════════════════════════════════════════════════
        if overall_success and len(filtered_articles) > 0:
            print()
            print("=" * 55)
            print(f"PHASE 3: SAVE - Sending {len(filtered_articles)} articles to Airtable...")
            print("=" * 55)
            logger.phase_start("SAVE")

            save_params = {
                'articles': filtered_articles,
                'api_key': AIRTABLE_API_KEY,
                'base_id': AIRTABLE_BASE_ID,
                'table_name': AIRTABLE_TABLE_NAME,
            }
            # Log params without the API key (don't put secrets in logs!)
            logger.tool_call(save_tool.get_name(), {
                'article_count': len(filtered_articles),
                'base_id': AIRTABLE_BASE_ID,
                'table_name': AIRTABLE_TABLE_NAME,
            })

            start = time.time()
            save_result = save_tool.execute(**save_params)
            duration = int((time.time() - start) * 1000)

            logger.tool_result(
                save_tool.get_name(),
                save_result,
                save_result['success'],
                duration
            )

            if save_result['success']:
                saved = save_result['data'].get('saved_count', 0)
                print(f"  Saved {saved} articles to Airtable ({duration}ms)")
            else:
                print(f"  FAILED: {save_result['error']}")

            # Validate the save
            validation = save_validator.validate(
                save_result,
                context={'expected_count': len(filtered_articles)}
            )
            logger.validation_event(
                save_validator.get_name(),
                validation['passed'],
                validation.get('issues', [])
            )

            if not validation['passed']:
                print(f"  Validation FAILED: {validation['issues']}")
                logger.phase_end("SAVE", success=False)
                overall_success = False
            else:
                print(f"  Validation passed: all articles saved")
                logger.phase_end("SAVE", success=True)

        elif overall_success:
            # Fetch and filter worked, but no recent articles to save
            print()
            print("Skipping SAVE phase (no recent articles to save)")

    except Exception as e:
        # Log unexpected crashes
        logger.error(
            f"Workflow crashed: {str(e)}",
            metadata={'exception_type': type(e).__name__}
        )
        overall_success = False
        print(f"\nERROR: {e}")

    finally:
        # ╔══════════════════════════════════════════════════════╗
        # ║  CRITICAL: flush() MUST be in a finally block!      ║
        # ║  Without this, all logs are lost if anything fails.  ║
        # ╚══════════════════════════════════════════════════════╝
        logger.flush()

    # ── Step 6: Update execution record ──
    status = 'completed' if overall_success else 'failed'
    db.table('executions') \
        .update({
            'completed_at': datetime.utcnow().isoformat(),
            'status': status,
            'output_summary': (
                f"Fetched: {len(fetched_articles)}, "
                f"Filtered: {len(filtered_articles)}, "
                f"Status: {status}"
            ),
        }) \
        .eq('id', execution_id) \
        .execute()

    # ── Step 7: Show final result ──
    print()
    print("=" * 55)
    if overall_success:
        print(f"WORKFLOW COMPLETED SUCCESSFULLY")
    else:
        print(f"WORKFLOW FAILED")
    print(f"  Execution ID: {execution_id}")
    print(f"  Articles fetched:  {len(fetched_articles)}")
    print(f"  Articles filtered: {len(filtered_articles)}")
    print(f"  Status: {status}")
    print("=" * 55)
    print()
    print("View logs: python scripts/show_logs.py ai_news_workflow")


if __name__ == '__main__':
    main()
