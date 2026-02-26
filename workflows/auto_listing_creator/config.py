# =============================================================================
# workflows/auto_listing_creator/config.py
# =============================================================================

import os
from dotenv import load_dotenv

load_dotenv()

# -- Identity
WORKFLOW_NAME = "auto_listing_creator"
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

# -- Claude API (for listing content generation)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL   = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

# -- Google Sheets
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "google-credentials.json")
GOOGLE_SPREADSHEET_ID   = os.getenv("ETSY_ANALYTICS_SPREADSHEET_ID",
                                    os.getenv("GOOGLE_SPREADSHEET_ID", ""))
LISTING_QUEUE_SHEET     = "Listing Queue"

# -- Listing defaults for digital Canva templates
FOCUS_NICHE      = os.getenv("SEO_FOCUS_NICHE", "tattoo")
DEFAULT_CURRENCY = "GBP"
WHO_MADE         = "i_did"
WHEN_MADE        = "2020_2025"
IS_DIGITAL       = True
IS_SUPPLY        = False
# Etsy taxonomy ID — matches existing PurpleOcaz listings
# (1874 = Paper & Party Supplies > Paper > Stationery > Templates)
DEFAULT_TAXONOMY_ID = 1874

# -- OAuth tokens (for creating draft listings on Etsy)
TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "..", "etsy_analytics", "etsy_tokens.json")

# -- Gemini API (Nano Banana -- AI image generation for Tier 1 products)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# -- Canva API (for design export)
CANVA_CLIENT_ID     = os.getenv("CANVA_CLIENT_ID", "")
CANVA_CLIENT_SECRET = os.getenv("CANVA_CLIENT_SECRET", "")
CANVA_TOKEN_FILE    = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "canva_tokens.json")
