# =============================================================================
# workflows/auto_listing_creator/tools/affiliate_guide_generator.py
#
# Generates a branded "Getting Started" PDF guide bundled with every
# digital product download. The guide includes:
#   - How to use / edit the template
#   - Recommended tools with affiliate links
#   - Printing service recommendations with affiliate links
#   - Links to PurpleOcaz social channels & email list
#
# Uses ReportLab (already a project dependency) and matches the existing
# PurpleOcaz branding: #6B2189 purple, dark aesthetic, Helvetica fonts.
# =============================================================================

import os

from tools.design_constants import EXPORT_DIR, BRAND_PURPLE, safe_filename
from tools.tier_config import TIER_1

# ---- Page dimensions ---------------------------------------------------------
A4_W, A4_H = 595.27, 841.89

# ---- Brand colours as 0-1 RGB tuples ----------------------------------------
_PURPLE = (0.420, 0.129, 0.537)   # #6B2189
_DARK_BG = (0.051, 0.051, 0.051)  # #0D0D0D
_DARK_CARD = (0.102, 0.102, 0.102)  # #1A1A1A
_WHITE = (1, 1, 1)
_LIGHT_GREY = (0.75, 0.75, 0.75)
_MID_GREY = (0.45, 0.45, 0.45)
_GOLD = (0.788, 0.659, 0.298)     # #C9A84C

# ---- Affiliate link configuration -------------------------------------------
# Replace YOUR_AFFILIATE_ID placeholders with your actual affiliate links.
# These are the verified sign-up / referral URLs for each program.

AFFILIATE_LINKS = {
    "canva": {
        "name": "Canva Pro",
        # Replace with your Canvassador link once accepted.
        # Apply at: https://app.impact.com/campaign-promo-signup/Canva.brand
        # Program status: currently CLOSED — check periodically.
        "url": "https://www.canva.com/pro/",
        "description": "Edit templates with premium fonts, graphics & features",
        "commission_note": "Free plan available — Pro unlocks premium elements",
        "signup_url": "https://app.impact.com/campaign-promo-signup/Canva.brand",
        "network": "Impact",
        "commission": "Up to $36 per referral (when program reopens)",
    },
    "creative_fabrica": {
        "name": "Creative Fabrica",
        # Replace YOUR_AFFILIATE_ID after signing up (open to all).
        # Sign up: https://www.creativefabrica.com/affiliates/
        # Or email: affiliates@creativefabrica.com
        "url": "https://www.creativefabrica.com/ref/YOUR_AFFILIATE_ID/",
        "description": "Premium fonts, graphics & SVGs for your designs",
        "commission_note": "Thousands of free assets with subscription",
        "signup_url": "https://www.creativefabrica.com/affiliates/",
        "network": "In-house (direct program)",
        "commission": "25% per sale / 20% recurring on subscriptions",
    },
    "vistaprint": {
        "name": "Vistaprint",
        # Apply via Impact: https://www.vistaprint.com/affiliate.aspx
        # Also: https://www.vistaprint.com/brand-ambassador-program
        "url": "https://www.vistaprint.co.uk/",
        "description": "Professional printing for business cards & marketing materials",
        "commission_note": "High-quality printing delivered to your door",
        "signup_url": "https://www.vistaprint.com/affiliate.aspx",
        "network": "Impact",
        "commission": "2.5-8% per sale (up to 25% via brand ambassador)",
    },
    "moo": {
        "name": "MOO",
        # Apply via CJ Affiliate (US): https://signup.cj.com/member/signup/publisher/?cid=2202486
        # Or Awin (UK): https://ui.awin.com/merchant-profile/2562
        "url": "https://www.moo.com/",
        "description": "Premium business cards & stationery",
        "commission_note": "Luxury quality printing with unique finishes",
        "signup_url": "https://www.moo.com/us/affiliates",
        "network": "CJ Affiliate (US) / Awin (UK/EU)",
        "commission": "8-12% new customers / 1-2% returning",
    },
    "adobe": {
        "name": "Adobe Creative Cloud",
        # Sign up via Partnerize: https://www.adobe.com/affiliates.html
        # Open to all — no minimum audience.
        "url": "https://www.adobe.com/creativecloud.html",
        "description": "Edit PDF & vector templates in Photoshop, Illustrator & more",
        "commission_note": "Industry-standard design software",
        "signup_url": "https://www.adobe.com/affiliates.html",
        "network": "Partnerize",
        "commission": "85% of first month's subscription",
    },
    "printful": {
        "name": "Printful",
        # Sign up via Impact: https://www.printful.com/affiliates
        # Review takes 2-5 business days.
        "url": "https://www.printful.com/a/YOUR_AFFILIATE_ID",
        "description": "Print-on-demand products — turn your designs into merch",
        "commission_note": "No minimum orders, ships worldwide",
        "signup_url": "https://www.printful.com/affiliates",
        "network": "Impact",
        "commission": "10% revenue share for 12 months + $25 per Growth sub",
    },
    "printify": {
        "name": "Printify",
        # Sign up via PartnerStack: https://printify.com/affiliate/
        # Review within 2 business days. 90-day cookie.
        "url": "https://printify.com/ref/YOUR_AFFILIATE_ID/",
        "description": "Create & sell custom products with no upfront cost",
        "commission_note": "800+ products, global delivery network",
        "signup_url": "https://printify.com/affiliate/",
        "network": "PartnerStack",
        "commission": "5% recurring for 12 months (90-day cookie)",
    },
}

# Which affiliates to show in the guide, and in what order
# Adjust per tier: Tier 1 (editable PDF) recommends Adobe; Tier 2 recommends Canva
TIER1_TOOL_ORDER = ["adobe", "creative_fabrica", "vistaprint", "moo"]
TIER2_TOOL_ORDER = ["canva", "creative_fabrica", "vistaprint", "moo"]


def create_affiliate_guide(listing, product_type, tier, output_dir=None):
    """Create a branded Getting Started PDF guide with affiliate links.

    Args:
        listing: dict with at least 'title' key
        product_type: str like "appointment card", "gift certificate", etc.
        tier: TIER_1 or TIER_2 from tier_config
        output_dir: output directory (defaults to EXPORT_DIR)

    Returns:
        {"success": bool, "pdf_path": str|None, "error": str|None}
    """
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.colors import Color

        out_dir = output_dir or EXPORT_DIR
        os.makedirs(out_dir, exist_ok=True)

        title = listing.get("title", "Template")
        safe_title = safe_filename(title)
        output_path = os.path.join(out_dir, f"{safe_title}_guide.pdf")

        c = canvas.Canvas(output_path)

        # Page 1: Welcome + How to Use
        _render_page1(c, listing, product_type, tier)

        # Page 2: Recommended Tools + Printing Services
        c.showPage()
        _render_page2(c, tier)

        c.save()

        if os.path.exists(output_path):
            size_kb = os.path.getsize(output_path) // 1024
            print(f"       Affiliate guide: {os.path.basename(output_path)} "
                  f"({size_kb}KB, 2 pages)", flush=True)
            return {"success": True, "pdf_path": output_path, "error": None}

        return {"success": False, "pdf_path": None,
                "error": "Guide PDF not created"}

    except ImportError:
        return {"success": False, "pdf_path": None,
                "error": "reportlab not installed (pip install reportlab)"}
    except Exception as e:
        return {"success": False, "pdf_path": None,
                "error": f"{type(e).__name__}: {str(e)[:200]}"}


# =============================================================================
# Page 1: Welcome + How to Use Your Template
# =============================================================================

def _render_page1(c, listing, product_type, tier):
    """Render the welcome page with usage instructions."""
    from reportlab.lib.colors import Color

    c.setPageSize((A4_W, A4_H))

    # --- Dark background ---
    c.setFillColor(Color(*_DARK_BG))
    c.rect(0, 0, A4_W, A4_H, fill=1, stroke=0)

    # --- Purple accent strip at top ---
    strip_h = 8
    c.setFillColor(Color(*_PURPLE))
    c.rect(0, A4_H - strip_h, A4_W, strip_h, fill=1, stroke=0)

    # --- Header section ---
    cx = A4_W / 2
    y = A4_H - 60

    # Shop name
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(Color(*_GOLD))
    c.drawCentredString(cx, y, "PURPLEOCAZ")
    y -= 8
    c.setFont("Helvetica", 7)
    c.setFillColor(Color(*_MID_GREY))
    c.drawCentredString(cx, y, "PREMIUM DIGITAL TEMPLATES")

    # Divider line
    y -= 16
    c.setStrokeColor(Color(*_PURPLE))
    c.setLineWidth(1.5)
    c.line(cx - 80, y, cx + 80, y)

    # Main title
    y -= 32
    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(Color(*_WHITE))
    c.drawCentredString(cx, y, "Getting Started")

    # Subtitle
    y -= 20
    c.setFont("Helvetica", 10)
    c.setFillColor(Color(*_LIGHT_GREY))
    product_name = listing.get("title", product_type.title())
    # Truncate long titles
    if len(product_name) > 55:
        product_name = product_name[:52] + "..."
    c.drawCentredString(cx, y, f"Your {product_name}")

    # --- How to Use section ---
    y -= 45
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(Color(*_GOLD))
    c.drawString(50, y, "How to Use Your Template")

    y -= 6
    c.setStrokeColor(Color(*_PURPLE))
    c.setLineWidth(0.75)
    c.line(50, y, 250, y)

    # Steps based on tier
    if tier == TIER_1:
        steps = [
            ("1", "Open the PDF", "Open the editable PDF file in any PDF reader "
             "(Adobe Acrobat, Preview, Chrome, or any free PDF viewer)."),
            ("2", "Click & Type", "Click on any highlighted field and type your "
             "studio details — name, phone, email, website, etc."),
            ("3", "Save Your Version", "Save the completed PDF with your details. "
             "Your information is now embedded in the design."),
            ("4", "Print at Home or Professionally",
             "Print on quality card stock at home, or upload to a professional "
             "printing service (see our recommendations on the next page)."),
        ]
    else:
        steps = [
            ("1", "Click the Canva Link", "Open the Canva template link included "
             "in your download. You'll need a free Canva account."),
            ("2", "Customise Your Design", "Edit the text, swap colours, change "
             "fonts, and add your logo to make it uniquely yours."),
            ("3", "Download as PDF", "When you're happy with your design, click "
             "Share > Download > PDF Print for the best quality."),
            ("4", "Print at Home or Professionally",
             "Print on quality card stock at home, or upload to a professional "
             "printing service (see our recommendations on the next page)."),
        ]

    y -= 20
    for num, heading, desc in steps:
        # Step number circle
        circle_x = 65
        circle_r = 12
        c.setFillColor(Color(*_PURPLE))
        c.circle(circle_x, y - 2, circle_r, fill=1, stroke=0)
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(Color(*_WHITE))
        c.drawCentredString(circle_x, y - 6, num)

        # Step heading
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(Color(*_WHITE))
        c.drawString(90, y, heading)

        # Step description (wrapped)
        y -= 16
        c.setFont("Helvetica", 9)
        c.setFillColor(Color(*_LIGHT_GREY))
        lines = _wrap_text(desc, 70)
        for line in lines:
            c.drawString(90, y, line)
            y -= 13

        y -= 12  # spacing between steps

    # --- What's Included section ---
    y -= 10
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(Color(*_GOLD))
    c.drawString(50, y, "What's Included")

    y -= 6
    c.setStrokeColor(Color(*_PURPLE))
    c.setLineWidth(0.75)
    c.line(50, y, 200, y)

    y -= 20
    if tier == TIER_1:
        items = [
            "Editable PDF template (fillable fields — no software needed)",
            "Front & back card designs",
            "Print-ready layouts: US Letter & A4 (8 cards per page)",
            "This Getting Started guide with printing recommendations",
        ]
    else:
        items = [
            "Canva template link (free account required)",
            "Fully customisable design — change text, colours & fonts",
            "A4 & US Letter sizes included",
            "This Getting Started guide with printing recommendations",
        ]

    c.setFont("Helvetica", 9)
    for item in items:
        c.setFillColor(Color(*_PURPLE))
        c.drawString(60, y + 1, "\u2022")  # bullet
        c.setFillColor(Color(*_LIGHT_GREY))
        c.drawString(75, y, item)
        y -= 16

    # --- Tips box ---
    y -= 15
    box_x, box_w = 40, A4_W - 80
    box_h = 65
    box_y = y - box_h + 10

    # Dark card background
    c.setFillColor(Color(*_DARK_CARD))
    c.roundRect(box_x, box_y, box_w, box_h, 6, fill=1, stroke=0)

    # Purple left accent bar
    c.setFillColor(Color(*_PURPLE))
    c.rect(box_x, box_y, 4, box_h, fill=1, stroke=0)

    # Tip content
    tip_x = box_x + 18
    tip_y = box_y + box_h - 18
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(Color(*_GOLD))
    c.drawString(tip_x, tip_y, "PRO TIP")
    tip_y -= 14
    c.setFont("Helvetica", 8.5)
    c.setFillColor(Color(*_LIGHT_GREY))
    c.drawString(tip_x, tip_y, "For the best print quality, use 300gsm card stock "
                 "and select 'Actual Size' (not 'Fit to Page')")
    tip_y -= 12
    c.drawString(tip_x, tip_y, "in your printer settings. This ensures your cards "
                 "print at the correct business card dimensions.")

    # --- Footer ---
    _render_footer(c)


# =============================================================================
# Page 2: Recommended Tools + Printing Services
# =============================================================================

def _render_page2(c, tier):
    """Render the tools & printing recommendations page with affiliate links."""
    from reportlab.lib.colors import Color

    c.setPageSize((A4_W, A4_H))

    # --- Dark background ---
    c.setFillColor(Color(*_DARK_BG))
    c.rect(0, 0, A4_W, A4_H, fill=1, stroke=0)

    # --- Purple accent strip at top ---
    strip_h = 8
    c.setFillColor(Color(*_PURPLE))
    c.rect(0, A4_H - strip_h, A4_W, strip_h, fill=1, stroke=0)

    cx = A4_W / 2
    y = A4_H - 55

    # Section title
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(Color(*_WHITE))
    c.drawCentredString(cx, y, "Recommended Tools")

    y -= 16
    c.setFont("Helvetica", 9)
    c.setFillColor(Color(*_MID_GREY))
    c.drawCentredString(cx, y, "Our favourite tools to get the most from your templates")

    y -= 10
    c.setStrokeColor(Color(*_PURPLE))
    c.setLineWidth(1.5)
    c.line(cx - 60, y, cx + 60, y)

    # --- Design Tools section ---
    y -= 30
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(Color(*_GOLD))
    c.drawString(50, y, "Design & Editing Tools")

    y -= 5
    c.setStrokeColor(Color(*_PURPLE))
    c.setLineWidth(0.75)
    c.line(50, y, 230, y)

    tool_order = TIER1_TOOL_ORDER if tier == TIER_1 else TIER2_TOOL_ORDER

    # Design tools (first 2 in the order)
    y -= 10
    for key in tool_order[:2]:
        link = AFFILIATE_LINKS[key]
        y = _render_tool_card(c, link, y)

    # --- Printing Services section ---
    y -= 20
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(Color(*_GOLD))
    c.drawString(50, y, "Professional Printing Services")

    y -= 5
    c.setStrokeColor(Color(*_PURPLE))
    c.setLineWidth(0.75)
    c.line(50, y, 280, y)

    y -= 10
    # Printing tools (last 2 in the order)
    for key in tool_order[2:]:
        link = AFFILIATE_LINKS[key]
        y = _render_tool_card(c, link, y)

    # --- Discount / coupon box ---
    y -= 15
    box_x, box_w = 40, A4_W - 80
    box_h = 55
    box_y = y - box_h + 10

    c.setFillColor(Color(*_DARK_CARD))
    c.roundRect(box_x, box_y, box_w, box_h, 6, fill=1, stroke=0)

    # Purple border
    c.setStrokeColor(Color(*_PURPLE))
    c.setLineWidth(1)
    c.roundRect(box_x, box_y, box_w, box_h, 6, fill=0, stroke=1)

    inner_y = box_y + box_h - 20
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(Color(*_GOLD))
    c.drawCentredString(cx, inner_y, "Loved your template? Leave us a review!")
    inner_y -= 16
    c.setFont("Helvetica", 9)
    c.setFillColor(Color(*_LIGHT_GREY))
    c.drawCentredString(cx, inner_y, "Your feedback helps us create more designs "
                        "for your studio. Thank you for your support!")

    # --- Connect With Us section ---
    y = box_y - 25
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(Color(*_GOLD))
    c.drawString(50, y, "Connect With Us")

    y -= 5
    c.setStrokeColor(Color(*_PURPLE))
    c.setLineWidth(0.75)
    c.line(50, y, 190, y)

    y -= 20
    social_links = [
        ("Etsy Shop", "etsy.com/shop/PurpleOcaz"),
        ("Instagram", "@purpleocaz"),
        ("Email", "hello@purpleocaz.com"),
    ]
    for label, value in social_links:
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(Color(*_PURPLE))
        c.drawString(60, y, label + ":")
        c.setFont("Helvetica", 9)
        c.setFillColor(Color(*_LIGHT_GREY))
        c.drawString(140, y, value)
        y -= 16

    # Newsletter CTA
    y -= 8
    cta_x, cta_w = 50, A4_W - 100
    cta_h = 38
    cta_y = y - cta_h + 10

    c.setFillColor(Color(*_PURPLE))
    c.roundRect(cta_x, cta_y, cta_w, cta_h, 5, fill=1, stroke=0)

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(Color(*_WHITE))
    c.drawCentredString(cx, cta_y + 22, "Join our mailing list for exclusive templates & discounts")
    c.setFont("Helvetica", 8)
    c.setFillColor(Color(0.85, 0.75, 1.0))
    c.drawCentredString(cx, cta_y + 9, "purpleocaz.com/newsletter")

    # --- Footer ---
    _render_footer(c)


# =============================================================================
# Shared helpers
# =============================================================================

def _render_tool_card(c, link_data, y):
    """Render a single tool recommendation card. Returns new y position."""
    from reportlab.lib.colors import Color

    card_x, card_w = 45, A4_W - 90
    card_h = 72
    card_y = y - card_h

    # Card background
    c.setFillColor(Color(*_DARK_CARD))
    c.roundRect(card_x, card_y, card_w, card_h, 5, fill=1, stroke=0)

    # Left purple accent
    c.setFillColor(Color(*_PURPLE))
    c.rect(card_x, card_y, 3, card_h, fill=1, stroke=0)

    # Tool name
    tx = card_x + 16
    ty = card_y + card_h - 18
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(Color(*_WHITE))
    c.drawString(tx, ty, link_data["name"])

    # Description
    ty -= 15
    c.setFont("Helvetica", 8.5)
    c.setFillColor(Color(*_LIGHT_GREY))
    c.drawString(tx, ty, link_data["description"])

    # Commission note / value prop
    ty -= 13
    c.setFont("Helvetica", 8)
    c.setFillColor(Color(*_MID_GREY))
    c.drawString(tx, ty, link_data["commission_note"])

    # URL (styled as a link)
    ty -= 15
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(Color(0.55, 0.35, 0.75))  # lighter purple for links
    url_display = link_data["url"]
    # Shorten display URL
    if len(url_display) > 60:
        url_display = url_display[:57] + "..."
    c.drawString(tx, ty, url_display)

    return card_y - 8  # spacing below card


def _render_footer(c):
    """Render the standard PurpleOcaz footer at the bottom of a page."""
    from reportlab.lib.colors import Color

    # Thin purple line above footer
    c.setStrokeColor(Color(*_PURPLE))
    c.setLineWidth(0.5)
    c.line(40, 35, A4_W - 40, 35)

    c.setFont("Helvetica", 7)
    c.setFillColor(Color(*_MID_GREY))
    c.drawCentredString(A4_W / 2, 22,
                        "PurpleOcaz \u2014 Premium Digital Templates")
    c.setFont("Helvetica", 6)
    c.drawCentredString(A4_W / 2, 13,
                        "\u00a9 2026 PurpleOcaz. All rights reserved. "
                        "Thank you for your purchase!")


def _wrap_text(text, max_chars):
    """Simple word-wrap to fit text within max_chars per line."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        if len(test) <= max_chars:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines
