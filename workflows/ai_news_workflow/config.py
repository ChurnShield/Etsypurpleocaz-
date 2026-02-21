"""
AI News Workflow - Configuration
=================================
All settings for the AI news RSS-to-Airtable workflow.

SETUP CHECKLIST:
    1. Add your RSS feed URL below (replace the placeholder)
    2. Add your Airtable credentials to the .env file:
           AIRTABLE_API_KEY=pat-xxxxx
           AIRTABLE_BASE_ID=appxxxxx
           AIRTABLE_TABLE_NAME=AI News
    3. Create the Airtable table with the fields listed in the
       AIRTABLE TABLE SETUP section below
    4. Install feedparser: pip install feedparser
    5. Run: python -m workflows.ai_news_workflow.run

AIRTABLE TABLE SETUP:
    Create a table in Airtable with these fields:
    ┌─────────────────┬──────────────┬──────────────────────────────────┐
    │ Field Name      │ Field Type   │ Notes                            │
    ├─────────────────┼──────────────┼──────────────────────────────────┤
    │ Title           │ Single line  │ Article headline                 │
    │ URL             │ URL          │ Link to the full article         │
    │ Published       │ Date         │ When the article was published   │
    │ Description     │ Long text    │ Summary/snippet from the feed    │
    │ Source          │ Single line  │ Name of the RSS feed/publisher   │
    │ Fetched At      │ Date         │ When this workflow saved it      │
    └─────────────────┴──────────────┴──────────────────────────────────┘

    How to get your Airtable credentials:
    - API Key:    https://airtable.com/create/tokens  (create a personal access token)
    - Base ID:    Open your base, look at the URL: airtable.com/appXXXXXXXX/...
    - Table Name: The name of your table tab (e.g., "AI News")
"""

import os
import sys

# Add project root to path so we can import from config.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from dotenv import load_dotenv
load_dotenv()

# ── Workflow Identity ──
# Used in database records so the Brain can track this workflow
WORKFLOW_NAME = "ai_news_workflow"

# ── Database ──
# Import from the project-wide config (single source of truth)
from config import DATABASE_PATH

# ── RSS Feed ──
# Replace this with your actual RSS feed URL
# Examples:
#   "https://feeds.feedburner.com/TechCrunch/AI"
#   "https://www.artificialintelligence-news.com/feed/"
#   "https://news.google.com/rss/search?q=artificial+intelligence"
RSS_FEED_URL = os.getenv("RSS_FEED_URL", "YOUR_RSS_FEED_URL_HERE")

# ── Airtable Credentials ──
# These come from your .env file (never hardcode secrets!)
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY", "")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID", "")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME", "AI News")

# ── Filter Settings ──
# How recent an article must be to pass the filter (in hours)
# Default: 24 hours (only articles from the last day)
HOURS_RECENT = int(os.getenv("NEWS_HOURS_RECENT", "24"))

# ── Execution Settings ──
MAX_RETRIES = 3
TIMEOUT_SECONDS = 30

# ── Small Brain Settings ──
PROPOSAL_THRESHOLD_RUNS = 15
MIN_CONFIDENCE = 0.7
SLOW_TOOL_THRESHOLD_MS = 5000
HIGH_FAILURE_RATE = 0.3
