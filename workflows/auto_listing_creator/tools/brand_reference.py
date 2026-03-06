# =============================================================================
# workflows/auto_listing_creator/tools/brand_reference.py
#
# Purple OCAZ Brand Reference System
#
# Extracted from real store listing thumbnails (Etsy Star Seller aesthetic).
# Every new product must follow this visual DNA for store congruence.
#
# 5-Image Listing Structure:
#   Page 1 (hero)        -> lifestyle_flatlay_mockup
#   Page 2 (note)        -> informational_note_page ("Please note" disclaimer)
#   Page 3 (instruction) -> template_instruction_mockup (drag & drop guide)
#   Page 4 (print)       -> print_mockup (print at home / print shop)
#   Page 5 (bonus)       -> bonus_ebook_mockup (free Canva Basics guide)
# =============================================================================

# ---------------------------------------------------------------------------
# COLOUR PALETTE (from live store images)
# ---------------------------------------------------------------------------
BRAND_COLORS = {
    # Primary
    "brand_purple":       "#6B3E9E",  # Deep purple — bottom banners, accents
    "brand_purple_light": "#9B59B6",  # Lighter purple for vibrant variants
    "brand_lavender":     "#A78BFA",  # Lavender — ebook accent, soft UI

    # Backgrounds
    "hero_bg":            "#F5F5F5",  # Light warm gray textured paper (hero)
    "note_bg":            "#F8F6F3",  # Off-white textured paper (note page)
    "card_bg":            "#FFFFFF",  # Pure white — all certificate cards
    "badge_dark":         "#2C2C2C",  # Dark circle badges

    # Text
    "text_dark":          "#2C2C2C",  # Primary text on cards
    "text_light":         "#FFFFFF",  # Text on purple/dark banners
    "text_gray":          "#999999",  # Field labels (TO:, FROM:, etc.)
    "field_line":         "#CCCCCC",  # Thin underlines on form fields
}

# ---------------------------------------------------------------------------
# TYPOGRAPHY (from live store images)
# ---------------------------------------------------------------------------
BRAND_TYPOGRAPHY = {
    "script_heading": {
        "font": "Great Vibes",
        "fallback": "Playfair Display italic",
        "usage": "Certificate titles, 'Gift Certificate', 'Please note'",
        "size_range": "72-120 pt",
        "color": BRAND_COLORS["text_dark"],
    },
    "business_name": {
        "font": "Helvetica Neue Bold",
        "fallback": "Montserrat 700",
        "usage": "YOUR BUSINESS NAME, uppercase headings",
        "size_range": "22-28 pt",
        "color": BRAND_COLORS["text_dark"],
        "transform": "uppercase",
    },
    "field_labels": {
        "font": "Helvetica Neue",
        "fallback": "Montserrat 400",
        "usage": "TO:, FROM:, AMOUNT:, EXPIRES: labels",
        "size_range": "16-18 pt",
        "color": BRAND_COLORS["text_gray"],
    },
    "banner_main": {
        "font": "Helvetica Neue Bold",
        "fallback": "Montserrat 700",
        "usage": "Bottom banner product title",
        "size_range": "60-80 pt",
        "color": BRAND_COLORS["text_light"],
    },
    "banner_sub": {
        "font": "Helvetica Neue",
        "fallback": "Montserrat 400",
        "usage": "Bottom banner subtitle (MAKE EXTRA INCOME...)",
        "size_range": "18-22 pt",
        "color": BRAND_COLORS["text_light"],
        "transform": "uppercase",
    },
    "body_text": {
        "font": "Helvetica Neue",
        "fallback": "Montserrat 400",
        "usage": "Bullet points, contact info, disclaimers",
        "size_range": "10-24 pt",
        "color": BRAND_COLORS["text_dark"],
    },
    "disclaimer": {
        "font": "Helvetica Neue italic",
        "fallback": "Montserrat 400 italic",
        "usage": "Non-refundable voucher notice",
        "size_range": "12 pt",
        "color": BRAND_COLORS["text_gray"],
    },
}

# ---------------------------------------------------------------------------
# LIFESTYLE PROPS (from live store images)
# These create the styled flat-lay look. Keep consistent across ALL products.
# ---------------------------------------------------------------------------
STANDARD_PROPS = {
    "top_left":     "small round green potted plant (succulent), ~300px",
    "bottom_left":  "white ceramic coffee cup with latte-art foam swirl, ~280px",
    "top_right":    "eucalyptus branch or green leaves",
    "bottom_right": "rose-gold pen and/or marble pen",
}

# Niche-specific props ADD to (not replace) the standard props above
NICHE_EXTRA_PROPS = {
    "tattoo": "tattoo flash art sheet partially visible, ink bottle",
    "nail":   "nail polish bottles (pink, red, nude), nail art gems",
    "hair":   "professional scissors, fine-tooth comb, hair oil bottle",
    "beauty": "compact mirror, makeup brushes fanned, perfume bottle",
    "spa":    "lit white candle, rolled white towels, bath salts bowl",
}

# ---------------------------------------------------------------------------
# HERO IMAGE (Page 1) — lifestyle_flatlay_mockup
# ---------------------------------------------------------------------------
HERO_SPEC = {
    "type": "lifestyle_flatlay_mockup",
    "canvas": "2000x1500 px (72 dpi) — resized to 2250x3000 for Etsy",
    "background": {
        "color": BRAND_COLORS["hero_bg"],
        "texture": "subtle canvas/paper grain",
        "lighting": "soft even studio light, gentle shadows under objects",
    },
    "certificate_layout": {
        "position": "center, slightly overlapping",
        "orientation": "landscape 2:1 ratio",
        "shadow": "soft drop shadow 5-8 px, 20% opacity",
    },
    "certificate_design": {
        "background": BRAND_COLORS["card_bg"],
        "border": "none (clean edges)",
        "top_photo_strip": {
            "height": "~180 px",
            "photos": "4 niche-relevant photos, tight spacing, 8px gaps, rounded corners 12px",
        },
        "header_font": "Great Vibes / cursive script, 72pt",
        "fields": "TO:, FROM:, AMOUNT:, EXPIRES: with thin 1px gray underlines",
        "disclaimer": "12pt italic non-refundable notice",
        "footer_contacts": "4x 24px circle icons (email, phone, map, globe) + contact text 10pt",
    },
    "bottom_banner": {
        "height": "220 px",
        "color": BRAND_COLORS["brand_purple"],
        "main_text": "80pt white bold sans-serif — product title",
        "sub_text": "22pt white uppercase — selling point tagline",
        "canva_badge": {
            "position": "bottom-right",
            "background": BRAND_COLORS["badge_dark"],
            "text": "EDIT IN CANVA",
            "size": "180px diameter circle",
        },
    },
}

# ---------------------------------------------------------------------------
# NOTE PAGE (Page 2) — informational_note_page
# ---------------------------------------------------------------------------
NOTE_PAGE_SPEC = {
    "type": "informational_note_page",
    "background": BRAND_COLORS["note_bg"],
    "texture": "off-white textured paper",
    "layout": "centered vertical text block",
    "header": {
        "text": "Please note",
        "font": "Great Vibes / cursive, 120pt black",
        "decoration": "thin black line with heart symbol",
    },
    "bullet_points": [
        "This is a downloadable digital product",
        "There will be NO physical product shipped to you",
        "You will need to print it yourself or take it to your local printer",
    ],
    "font_bullets": "24pt black sans-serif",
    "logo": {
        "position": "top-right",
        "shape": "circular watercolor frame (blue/teal)",
        "illustration": "Purple OCAZ family logo",
        "text": "Purple OCAZ (script + dots)",
    },
}

# ---------------------------------------------------------------------------
# INSTRUCTION PAGE (Page 3) — template_instruction_mockup
# ---------------------------------------------------------------------------
INSTRUCTION_PAGE_SPEC = {
    "type": "template_instruction_mockup",
    "left_side": {
        "object": "three stacked blank A4 landscape templates",
        "content": "gradient sky blue + layered green rolling hills, clouds, person silhouette",
        "label": "FRONT — A4 - Save your certificate as a PNG...",
    },
    "arrow": "hand-drawn thick black curved arrow pointing right",
    "right_side": "three finished certificate examples (matching hero design)",
    "bottom_text": "To PRINT AT HOME just drag and drop your finished certificates into the template document provided",
    "font": "32pt black sans-serif",
    "decor": "green leaves top-right and bottom-left",
}

# ---------------------------------------------------------------------------
# PRINT MOCKUP (Page 4) — print_mockup
# ---------------------------------------------------------------------------
PRINT_PAGE_SPEC = {
    "type": "print_mockup",
    "background": "light gray textured surface",
    "objects": [
        "gray modern printer top-center ejecting finished certificate",
        "white coffee cup + spoon bottom-right",
        "eucalyptus branch left",
        "gray rounded overlay: Canva print dialog (PDF Print, All pages, RGB, crop marks/bleed)",
    ],
    "badges": [
        "circular 'PRINT AT HOME' icon with printer symbol",
        "PRINT AT HOME OR AT A PRINT SHOP",
        "Download as a PDF or JPG",
        "Save with bleed + crop marks",
    ],
}

# ---------------------------------------------------------------------------
# BONUS EBOOK (Page 5) — bonus_ebook_mockup
# ---------------------------------------------------------------------------
EBOOK_PAGE_SPEC = {
    "type": "bonus_ebook_mockup",
    "layout": "three overlapping Canva guide pages on wooden desk texture",
    "pages_shown": [
        "left: 'EDITING BASICS' with Canva upload photos screenshot",
        "middle: 'Contents' page (page numbers 2-11)",
        "right: arched 'Canva Basics' cover with Purple OCAZ family logo",
    ],
    "accent_color": BRAND_COLORS["brand_lavender"],
    "bottom_text": "Includes a free e-book to help you with Canva editing basics!",
    "font": "bold 36pt",
    "props": "rose-gold pen, marble pen, green plants top-right and bottom-left",
    "canva_badge": "EDIT IN CANVA (dark blue circle)",
}

# ---------------------------------------------------------------------------
# OVERALL STYLE RULES — apply to ALL pages
# ---------------------------------------------------------------------------
STYLE_RULES = {
    "aesthetic": "clean, modern, vibrant, high-contrast photos",
    "lighting": "soft diffused natural light, gentle shadows",
    "texture": "always textured paper backgrounds, never flat/smooth digital",
    "props_rule": "succulent + coffee cup + eucalyptus appear in most images",
    "logo_placement": "Purple OCAZ watercolor circle logo on note page",
    "canva_badge": "appears on hero (bottom-right of banner) and ebook page",
    "color_consistency": "purple accents throughout, never orange or red",
    "card_style": "pure white cards, never cream/off-white, no dark backgrounds on cards",
    "banner_color": "deep purple #6B3E9E, NOT black",
}
