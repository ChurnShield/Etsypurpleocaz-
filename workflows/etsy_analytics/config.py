# =============================================================================
# workflows/etsy_analytics/config.py
#
# Configuration for the Etsy Analytics Dashboard workflow.
# All secrets live in .env — never hardcode them here.
# =============================================================================

import os
from dotenv import load_dotenv

load_dotenv()

# -- Identity
WORKFLOW_NAME = "etsy_analytics"
DATABASE_PATH = "data/system.db"

# -- Orchestrator settings
MAX_RETRIES = 3

# -- SmallBrain thresholds
PROPOSAL_THRESHOLD_RUNS = 15
SLOW_TOOL_THRESHOLD_MS  = 10000
MIN_PATTERN_CONFIDENCE  = 0.7

# -- Etsy API
ETSY_API_KEYSTRING  = os.getenv("ETSY_API_KEYSTRING", "")
ETSY_SHARED_SECRET  = os.getenv("ETSY_SHARED_SECRET", "")
ETSY_SHOP_ID        = os.getenv("ETSY_SHOP_ID", "")
ETSY_API_KEY        = f"{ETSY_API_KEYSTRING}:{ETSY_SHARED_SECRET}"

# How many listings to fetch per API page (max 100)
ETSY_PAGE_LIMIT     = 100

# -- Google Sheets (analytics output)
GOOGLE_CREDENTIALS_FILE     = os.getenv("GOOGLE_CREDENTIALS_FILE", "google-credentials.json")
GOOGLE_SPREADSHEET_ID       = os.getenv("ETSY_ANALYTICS_SPREADSHEET_ID",
                                        os.getenv("GOOGLE_SPREADSHEET_ID", ""))
ETSY_SNAPSHOT_SHEET_NAME    = os.getenv("ETSY_SNAPSHOT_SHEET_NAME", "Etsy Daily Snapshot")
ETSY_LISTINGS_SHEET_NAME    = os.getenv("ETSY_LISTINGS_SHEET_NAME", "Etsy Listing Tracker")
ETSY_TOP_PERFORMERS_SHEET   = os.getenv("ETSY_TOP_PERFORMERS_SHEET", "Etsy Top Performers")

# -- Niche focus (for triage scoring bonus)
FOCUS_NICHE = os.getenv("SEO_FOCUS_NICHE", "tattoo")
