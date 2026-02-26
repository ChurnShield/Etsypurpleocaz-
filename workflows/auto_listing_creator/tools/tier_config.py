# =============================================================================
# workflows/auto_listing_creator/tools/tier_config.py
#
# Product tier classification and tier-specific messaging constants.
#
# Tier 1 (Nano Banana): premium products -- AI-generated mockups + editable PDF
# Tier 2 (HTML/Playwright): utility products -- existing HTML template pipeline
# =============================================================================

TIER_1 = "nano_banana"
TIER_2 = "html_playwright"

# Product types routed to Tier 1 (Nano Banana + editable PDF)
TIER_1_KEYWORDS = frozenset({
    "appointment card",
    "gift certificate",
    "gift voucher",
    "price list",
    "service menu",
    "business card",
    "branding bundle",
})

# Product types remaining on Tier 2 (HTML/Playwright)
TIER_2_KEYWORDS = frozenset({
    "aftercare card",
    "consent form",
    "release form",
    "intake form",
    "flash sheet",
    "stencil sheet",
    "social media",
    "instagram",
})


def classify_tier(product_type):
    """Classify a product type into Tier 1 or Tier 2.

    Returns TIER_1 for premium products needing AI-generated mockups,
    TIER_2 for utility products using HTML templates.
    Defaults to TIER_2 for unknown types.
    """
    pt_lower = product_type.lower().strip()
    for keyword in TIER_1_KEYWORDS:
        if keyword in pt_lower:
            return TIER_1
    return TIER_2


# ---- Badge text per tier ---------------------------------------------------
BADGE_TEXT = {
    TIER_1: ("EDITABLE", "PDF"),
    TIER_2: ("EDIT IN", "CANVA"),
}

# ---- Page 2 feature bullets per tier ---------------------------------------
PAGE2_FEATURES = {
    TIER_1: [
        "Editable {product_type}",
        "A4 &amp; US Letter Sizes",
        "Instant Digital Download",
        "Print-Ready (300 DPI)",
        "Fillable PDF -- No Software Needed",
        "Works in Any PDF Reader",
    ],
    TIER_2: [
        "Editable {product_type}",
        "A4 &amp; US Letter Sizes",
        "Instant Digital Download",
        "Print-Ready (300 DPI)",
        "Free Canva Account Only",
        "Step-by-Step Guide",
    ],
}

# ---- Page 2 "How It Works" steps per tier ----------------------------------
PAGE2_STEPS = {
    TIER_1: [
        "Download the PDF from your Etsy receipt",
        "Open in any PDF reader (Adobe, Preview, etc.)",
        "Click each field and type your details",
    ],
    TIER_2: [
        "Click the Canva link in your download",
        "Customise text, colours and images",
        "Download as PDF and print at home",
    ],
}

# ---- Page 2 pill labels per tier -------------------------------------------
PAGE2_PILLS = {
    TIER_1: ["Editable PDF", "A4 + Letter", "Instant Download"],
    TIER_2: ["Editable in Canva", "A4 + Letter", "Instant Download"],
}
