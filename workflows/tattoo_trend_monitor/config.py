# =============================================================================
# workflows/tattoo_trend_monitor/config.py
# =============================================================================

import os
from dotenv import load_dotenv

load_dotenv()

# -- Identity
WORKFLOW_NAME = "tattoo_trend_monitor"
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

# -- Claude API (for opportunity analysis)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL   = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

# -- Google Sheets
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "google-credentials.json")
GOOGLE_SPREADSHEET_ID   = os.getenv("ETSY_ANALYTICS_SPREADSHEET_ID",
                                    os.getenv("GOOGLE_SPREADSHEET_ID", ""))
TRENDS_SHEET_NAME       = "Tattoo Trends"
OPPORTUNITIES_SHEET_NAME = "Tattoo Opportunities"

# -- Trend monitoring settings
FOCUS_NICHE = os.getenv("SEO_FOCUS_NICHE", "tattoo")

# Tattoo sub-niche keywords to track in Google Trends
TREND_KEYWORDS = [
    # Core tattoo products
    "tattoo gift certificate",
    "tattoo consent form",
    "tattoo aftercare card",
    "tattoo flash sheet",
    "tattoo price list",
    # Business templates
    "tattoo booking form",
    "tattoo waiver template",
    "tattoo business card",
    "tattoo loyalty card",
    "tattoo studio branding",
    # Specialty / trending
    "fine line tattoo",
    "minimalist tattoo",
    "tattoo voucher",
    "tattoo appointment card",
    "tattoo release form",
    # Digital products
    "tattoo instagram template",
    "tattoo social media kit",
    "tattoo portfolio template",
    "tattoo menu template",
    "tattoo stencil template",
]

# Etsy search queries to scan competitor landscape
ETSY_SEARCH_QUERIES = [
    "tattoo gift certificate template",
    "tattoo consent form canva",
    "tattoo aftercare card editable",
    "tattoo flash sheet digital",
    "tattoo price list template",
    "tattoo booking form template",
    "tattoo waiver form",
    "tattoo business card canva",
    "tattoo loyalty card template",
    "tattoo social media template",
    "tattoo studio branding kit",
    "tattoo appointment card",
    "tattoo portfolio template",
    "tattoo menu design",
    "tattoo stencil printable",
]

# Google Trends geo (GB = United Kingdom, empty = worldwide)
TRENDS_GEO = ""  # worldwide for broader signal
TRENDS_TIMEFRAME = "today 12-m"  # last 12 months
