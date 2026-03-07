# =============================================================================
# workflows/notebooklm_audio/config.py
#
# Configuration for the NotebookLM Audio Product workflow.
# Generates audio overview products from NotebookLM notebooks
# for sale as digital products on Etsy.
# =============================================================================

import os
from dotenv import load_dotenv

load_dotenv()

# -- Identity
WORKFLOW_NAME = "notebooklm_audio"
DATABASE_PATH = "data/system.db"

# -- Orchestrator
MAX_RETRIES = 2

# -- SmallBrain
PROPOSAL_THRESHOLD_RUNS = 15
SLOW_TOOL_THRESHOLD_MS = 10000
MIN_PATTERN_CONFIDENCE = 0.7

# -- Audio product settings
AUDIO_NICHES = [
    n.strip() for n in
    os.getenv("AUDIO_NICHES", "tattoo,nail,hair,beauty").split(",")
    if n.strip()
]

AUDIO_PRODUCT_TYPES = [
    "business_startup_guide",
    "template_walkthrough",
    "industry_tips",
    "seasonal_guide",
]

DEFAULT_AUDIO_PRICE_GBP = float(os.getenv("DEFAULT_AUDIO_PRICE_GBP", "3.99"))
BUNDLE_AUDIO_WITH_TEMPLATES = os.getenv("BUNDLE_AUDIO_WITH_TEMPLATES", "true").lower() == "true"

# -- NotebookLM notebook IDs (one per niche)
NOTEBOOKLM_NOTEBOOK_IDS = {
    "tattoo": os.getenv("NOTEBOOKLM_NOTEBOOK_TATTOO", ""),
    "nail": os.getenv("NOTEBOOKLM_NOTEBOOK_NAIL", ""),
    "hair": os.getenv("NOTEBOOKLM_NOTEBOOK_HAIR", ""),
    "beauty": os.getenv("NOTEBOOKLM_NOTEBOOK_BEAUTY", ""),
}

# -- Claude API (for listing content generation for audio products)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

# -- Google Sheets
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "google-credentials.json")
GOOGLE_SPREADSHEET_ID = os.getenv("ETSY_ANALYTICS_SPREADSHEET_ID",
                                  os.getenv("GOOGLE_SPREADSHEET_ID", ""))
AUDIO_PRODUCTS_SHEET = "Audio Products"

# -- Etsy API
ETSY_API_KEYSTRING = os.getenv("ETSY_API_KEYSTRING", "")
ETSY_SHARED_SECRET = os.getenv("ETSY_SHARED_SECRET", "")
ETSY_SHOP_ID = os.getenv("ETSY_SHOP_ID", "")
ETSY_API_KEY = f"{ETSY_API_KEYSTRING}:{ETSY_SHARED_SECRET}"
DEFAULT_CURRENCY = "GBP"
DEFAULT_TAXONOMY_ID = 1874

# -- OAuth tokens
TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "..", "etsy_analytics", "etsy_tokens.json")

# -- Export directory
EXPORT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports")
