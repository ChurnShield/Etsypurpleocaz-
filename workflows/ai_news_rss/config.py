# =============================================================================
# workflows/ai_news_rss/config.py
#
# All settings for the AI News RSS workflow.
# ✅ DO: Change values here — never hardcode them in tools or validators.
# ✅ DO: Put secrets (API keys) in your .env file, not here.
# ❌ DON'T: Commit your .env file to git.
# =============================================================================

import os
from dotenv import load_dotenv

# Load values from the .env file in the project root.
# python-dotenv searches upward from cwd, so this works when run from anywhere.
load_dotenv()

# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------
WORKFLOW_NAME = "ai_news_rss"
DATABASE_PATH = "data/system.db"

# ---------------------------------------------------------------------------
# Orchestrator / retry settings
# ---------------------------------------------------------------------------
MAX_RETRIES = 3

# ---------------------------------------------------------------------------
# SmallBrain thresholds
# ---------------------------------------------------------------------------
PROPOSAL_THRESHOLD_RUNS = 15     # Analyse after this many executions
SLOW_TOOL_THRESHOLD_MS  = 10000  # RSS + Sheets API calls can take several seconds
MIN_PATTERN_CONFIDENCE  = 0.7

# ---------------------------------------------------------------------------
# RSS settings
# ---------------------------------------------------------------------------
# Set RSS_FEED_URLS in your .env file as a comma-separated list of feed URLs.
# You can also set a single RSS_FEED_URL for backward compatibility.
#
# Example .env entry:
#   RSS_FEED_URLS=https://techcrunch.com/category/artificial-intelligence/feed/,https://www.theverge.com/ai-artificial-intelligence/rss/index.xml
#
_DEFAULT_FEEDS = ",".join([
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml",
    "https://venturebeat.com/category/ai/feed/",
])

_raw_urls  = os.getenv("RSS_FEED_URLS") or os.getenv("RSS_FEED_URL") or _DEFAULT_FEEDS
RSS_FEED_URLS = [u.strip() for u in _raw_urls.split(",") if u.strip()]

# Keep RSS_FEED_URL as an alias pointing to the first feed (backward compat).
RSS_FEED_URL = RSS_FEED_URLS[0] if RSS_FEED_URLS else ""

# Only keep articles published within this many hours of "now".
LOOKBACK_HOURS = int(os.getenv("LOOKBACK_HOURS", "24"))

# ---------------------------------------------------------------------------
# Google Sheets settings
# ---------------------------------------------------------------------------
# Add these to your .env file:
#
#   GOOGLE_CREDENTIALS_FILE=google-credentials.json   <- path to JSON key file
#   GOOGLE_SPREADSHEET_ID=1BxiMVs0X...                <- ID from the Sheet URL
#   GOOGLE_SHEET_NAME=AI News                         <- worksheet tab name
#
# One-time setup — see the full guide at the top of save_to_google_sheets_tool.py
#
# Required Sheet columns (Row 1 headers — created automatically if empty):
#
#   A: Title  |  B: URL  |  C: Publication Date  |  D: Description  |  E: Source
#
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "google-credentials.json")
GOOGLE_SPREADSHEET_ID   = os.getenv("GOOGLE_SPREADSHEET_ID")
GOOGLE_SHEET_NAME       = os.getenv("GOOGLE_SHEET_NAME", "AI News")
