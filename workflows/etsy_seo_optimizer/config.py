# =============================================================================
# workflows/etsy_seo_optimizer/config.py
# =============================================================================

import os
from dotenv import load_dotenv

load_dotenv()

# -- Identity
WORKFLOW_NAME = "etsy_seo_optimizer"
DATABASE_PATH = "data/system.db"

# -- Orchestrator
MAX_RETRIES = 2

# -- SmallBrain
PROPOSAL_THRESHOLD_RUNS = 15
SLOW_TOOL_THRESHOLD_MS  = 10000
MIN_PATTERN_CONFIDENCE  = 0.7

# -- Etsy API
ETSY_API_KEYSTRING = os.getenv("ETSY_API_KEYSTRING", "")
ETSY_SHARED_SECRET = os.getenv("ETSY_SHARED_SECRET", "")
ETSY_SHOP_ID       = os.getenv("ETSY_SHOP_ID", "")
ETSY_API_KEY       = f"{ETSY_API_KEYSTRING}:{ETSY_SHARED_SECRET}"
ETSY_PAGE_LIMIT    = 100

# -- Claude API (for tag generation)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL   = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

# -- Google Sheets
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "google-credentials.json")
GOOGLE_SPREADSHEET_ID   = os.getenv("ETSY_ANALYTICS_SPREADSHEET_ID",
                                    os.getenv("GOOGLE_SPREADSHEET_ID", ""))
SEO_REPORT_SHEET_NAME   = os.getenv("SEO_REPORT_SHEET_NAME", "SEO Tag Fixes")
SEO_OVERVIEW_SHEET_NAME = os.getenv("SEO_OVERVIEW_SHEET_NAME", "SEO Overview")

# -- SEO analysis settings
# Tags used across this many listings are considered "overused/generic"
OVERUSED_TAG_THRESHOLD  = 50
# How many listings to process per Claude API batch (to manage token costs)
CLAUDE_BATCH_SIZE       = 15
# Max listings to optimize per run (0 = all). Start small to control API costs.
MAX_LISTINGS_PER_RUN    = int(os.getenv("SEO_MAX_LISTINGS", "0"))  # 0 = ALL listings
# Focus niche (prioritize these listings for optimization)
FOCUS_NICHE             = os.getenv("SEO_FOCUS_NICHE", "tattoo")
