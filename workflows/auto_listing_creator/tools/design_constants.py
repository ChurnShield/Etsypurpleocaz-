# =============================================================================
# workflows/auto_listing_creator/tools/design_constants.py
#
# Shared constants, colour palettes, dimension values, font imports,
# boilerplate page paths, theme accents, and utility functions used by
# all product-creation modules.
# =============================================================================

import os
import html as html_module

_here = os.path.dirname(os.path.abspath(__file__))
_workflow = os.path.dirname(_here)

EXPORT_DIR = os.path.join(_workflow, "exports")

# ---- Image dimensions (Etsy listing images) --------------------------------
IMG_W, IMG_H = 2250, 3000
BAND_H = 750  # Height of title band at bottom

# ---- Template design dimensions (landscape card) ---------------------------
TMPL_W, TMPL_H = 2000, 950

# ---- Brand constants --------------------------------------------------------
BRAND_PURPLE = "#6B2189"
BEIGE_BG = "#E6E5E1"
BEIGE_RGB = (230, 229, 225)

# ---- PurpleOcaz brand palette (from live store — see brand_reference.py) ----
BRAND_PURPLE = "#6B3E9E"
BRAND_PURPLE_RGB = (107, 62, 158)
BRAND_PURPLE_LIGHT = "#9B59B6"
BADGE_DARK = "#2C2C2C"
BADGE_DARK_RGB = (44, 44, 44)
CARD_WHITE = "#FFFFFF"
HERO_BG = "#F5F5F5"
HERO_BG_RGB = (245, 245, 245)
TEXT_GRAY = "#999999"
FIELD_LINE = "#CCCCCC"

# Legacy aliases (kept for backward compat with existing code)
DARK_BG = "#0D0D0D"
DARK_CARD = "#1A1A1A"
DARK_BG_RGB = (13, 13, 13)
ACCENT_ORANGE = "#FF6B00"
ACCENT_GOLD = "#C9A84C"

# ---- Shared Google Fonts import --------------------------------------------
FONTS_CSS = (
    "@import url('https://fonts.googleapis.com/css2?"
    "family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400"
    "&family=Montserrat:wght@300;400;600;700;800"
    "&family=Oswald:wght@400;500;600;700"
    "&family=Great+Vibes&display=swap');"
)

# ---- Boilerplate pages from existing Canva exports -------------------------
_BOILERPLATE_PREFIX = "Etsy Listing - Gift Certificate Gothic Tattoo"
BOILERPLATE_PAGES = {
    3: os.path.join(EXPORT_DIR, f"{_BOILERPLATE_PREFIX}_page3.png"),
    4: os.path.join(EXPORT_DIR, f"{_BOILERPLATE_PREFIX}_page4.png"),
    5: os.path.join(EXPORT_DIR, f"{_BOILERPLATE_PREFIX}_page5.png"),
}

# ---- Accent colour presets for different product themes --------------------
THEME_ACCENTS = {
    "dark": {"band": BRAND_PURPLE, "accent": BRAND_PURPLE, "photos": "dark"},
    "gothic": {"band": BRAND_PURPLE, "accent": BRAND_PURPLE, "photos": "gothic"},
    "classic": {"band": BRAND_PURPLE, "accent": BRAND_PURPLE, "photos": "classic"},
    "vibrant": {"band": BRAND_PURPLE_LIGHT, "accent": BRAND_PURPLE_LIGHT, "photos": "vibrant"},
    "default": {"band": BRAND_PURPLE, "accent": BRAND_PURPLE, "photos": "dark"},
}


# ---- Utility functions -----------------------------------------------------

def esc(text):
    """HTML-escape text for safe template insertion."""
    return html_module.escape(str(text)) if text else ""


def safe_filename(title):
    """Convert title to a safe filename."""
    safe = "".join(c if c.isalnum() or c in " -_" else "" for c in title)
    return safe.strip()[:50]
