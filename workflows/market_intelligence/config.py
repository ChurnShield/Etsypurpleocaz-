# =============================================================================
# workflows/market_intelligence/config.py
#
# Market Intelligence workflow - gathers social trend signals, enriches with
# Etsy competitor data (official API), scores opportunities with Claude AI.
# =============================================================================

import os
from dotenv import load_dotenv

load_dotenv()

# -- Identity
WORKFLOW_NAME = "market_intelligence"
DATABASE_PATH = "data/system.db"

# -- Orchestrator
MAX_RETRIES = 2

# -- SmallBrain
PROPOSAL_THRESHOLD_RUNS = 15
SLOW_TOOL_THRESHOLD_MS  = 15000  # Social APIs can be slower
MIN_PATTERN_CONFIDENCE  = 0.7

# -- Etsy API (for competitor enrichment -- ephemeral, not stored long-term)
ETSY_API_KEYSTRING = os.getenv("ETSY_API_KEYSTRING", "")
ETSY_SHARED_SECRET = os.getenv("ETSY_SHARED_SECRET", "")
ETSY_SHOP_ID       = os.getenv("ETSY_SHOP_ID", "")
ETSY_API_KEY       = f"{ETSY_API_KEYSTRING}:{ETSY_SHARED_SECRET}"
ETSY_PAGE_LIMIT    = 25  # Only need top 25 per trend for enrichment

# -- Claude API (for opportunity scoring)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL   = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

# -- Google Sheets
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "google-credentials.json")
GOOGLE_SPREADSHEET_ID   = os.getenv("ETSY_ANALYTICS_SPREADSHEET_ID",
                                    os.getenv("GOOGLE_SPREADSHEET_ID", ""))
MARKET_INTEL_SHEET_NAME = "Market Intelligence"

# -- Niche configuration
FOCUS_NICHE = os.getenv("SEO_FOCUS_NICHE", "tattoo")
EXPANSION_NICHES = [
    n.strip() for n in
    os.getenv("EXPANSION_NICHES", "").split(",")
    if n.strip()
] or [FOCUS_NICHE]

# -- Reddit configuration (public JSON API, no auth needed)
REDDIT_SUBREDDITS = {
    "tattoo": ["tattoos", "tattoo", "TattooDesigns", "tattooadvice"],
    "nail":   ["Nails", "NailArt", "RedditLaqueristas"],
    "hair":   ["Hair", "HairDye", "FancyFollicles"],
    "beauty": ["MakeupAddiction", "SkincareAddiction"],
    "spa":    ["Esthetics", "massage"],
}
REDDIT_POST_LIMIT    = int(os.getenv("MI_REDDIT_POST_LIMIT", "50"))
REDDIT_LOOKBACK_DAYS = int(os.getenv("MI_REDDIT_LOOKBACK_DAYS", "30"))

# -- Google Trends enhanced settings
TRENDS_GEO       = os.getenv("MI_TRENDS_GEO", "")  # empty = worldwide
TRENDS_TIMEFRAME = os.getenv("MI_TRENDS_TIMEFRAME", "today 12-m")

# -- Scoring thresholds
MIN_OPPORTUNITY_SCORE = int(os.getenv("MI_MIN_OPPORTUNITY_SCORE", "30"))
MAX_OPPORTUNITIES     = int(os.getenv("MI_MAX_OPPORTUNITIES", "20"))
MAX_SIGNALS_TO_ENRICH = 30  # Cap Etsy API calls per run

# -- Trend keywords (same base set as tattoo_trend_monitor)
TREND_KEYWORDS = [
    "tattoo gift certificate", "tattoo consent form", "tattoo aftercare card",
    "tattoo flash sheet", "tattoo price list", "tattoo booking form",
    "tattoo waiver template", "tattoo business card", "tattoo loyalty card",
    "tattoo studio branding", "fine line tattoo", "minimalist tattoo",
    "tattoo voucher", "tattoo appointment card", "tattoo release form",
    "tattoo instagram template", "tattoo social media kit",
    "tattoo portfolio template", "tattoo menu template", "tattoo stencil template",
]

# -- Pagination
PAGINATION_MAX_PAGES = 50
