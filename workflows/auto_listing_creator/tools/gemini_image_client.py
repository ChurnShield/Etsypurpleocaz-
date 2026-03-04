# =============================================================================
# workflows/auto_listing_creator/tools/gemini_image_client.py
#
# Nano Banana -- Gemini 2.5 Flash image generation client.
# Generates professional product mockup images for Tier 1 products.
# Uses urllib (project standard) for HTTP calls.
# =============================================================================

import json
import base64
import time
import urllib.request
import urllib.error

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

# Model priority: try best-quality first, fall back to faster alternatives
GEMINI_IMAGE_MODELS = [
    "gemini-2.5-flash-preview-image",   # Latest preview (best quality)
    "gemini-2.5-flash-image",           # Stable image generation
    "gemini-2.0-flash-exp",             # Experimental fallback
]

# Default model — override via GEMINI_IMAGE_MODEL env var
DEFAULT_MODEL = "gemini-2.5-flash-preview-image"

# ---------------------------------------------------------------------------
# PurpleOcaz brand-aligned prompt system
#
# Visual identity (from live store reference images):
#   - Background: warm beige/cream textured craft paper
#   - Card style: elegant ivory/cream cards with dark borders, gold accents
#   - Props: eucalyptus leaves, terracotta succulent pot, latte art coffee,
#            tortoiseshell reading glasses, marble pens, wicker trays
#   - Layout: styled overhead flat-lay, cards overlapping at slight angle
#   - Typography on cards: script/calligraphy headings, clean sans-serif fields
#   - Badge: circular "EDIT IN CANVA" (bottom-right of scene)
#   - Bottom band: bold product title + tagline (added in compositing step)
# ---------------------------------------------------------------------------

# Product-type-specific prompt components
PROMPT_TEMPLATES = {
    "appointment card": {
        "card_description": (
            "Two overlapping appointment cards (front and back visible). "
            "BOTH cards must be the EXACT SAME pure WHITE colour — no cream, "
            "no off-white, no variation between the two cards. "
            "BOTH cards use the SAME elegant script font at the SAME size "
            "for their titles — consistency is critical. "
            "Front card: pure white background. A fine-line tattoo-style "
            "ornamental divider (e.g. a thin mandala line, dagger, or "
            "geometric dot-work line) separates the heading area from the "
            "form fields. Title: 'Appointment Card' in elegant dark script. "
            "Below the divider are four form fields, each on its own line: "
            "NAME:  followed by a thin horizontal line. "
            "DATE:  followed by a thin horizontal line. "
            "TIME:  followed by a thin horizontal line. "
            "DAY:   followed by a thin horizontal line. "
            "ALL four horizontal lines must END at the SAME right-hand edge "
            "of the card — perfectly aligned, same length, creating a neat "
            "uniform column. No slashes, no extra symbols, no random marks. "
            "Show these fields ONLY ONCE — do not duplicate any text. "
            "Back card: SAME pure white background as front card — identical "
            "colour, no variation. Same style ornamental divider. "
            "Title: 'Book Appointment' in the same script font and size as "
            "the front card. Below the divider are EXACTLY three form fields "
            "and NOTHING else — no extra words, no misspellings: "
            "EMAIL:   followed by a thin horizontal line. "
            "PHONE:   followed by a thin horizontal line. "
            "WEBSITE: followed by a thin horizontal line. "
            "That is THREE fields total. Do NOT add any other text or labels. "
            "ALL three lines must END at the SAME right-hand edge — perfectly "
            "aligned, same length. "
            "Below the three fields, in the remaining space, place a small "
            "decorative tattoo-style line art icon centred on the card — "
            "such as a fine-line rose, a small mandala, or a minimalist "
            "dagger/arrow illustration. This should be subtle and decorative, "
            "not overpowering. "
            "A small circular 'LOGO' placeholder in the top-right corner"
        ),
        "card_count": "two cards",
        "design_element": (
            "fine-line tattoo-style ornamental dividers (thin mandala lines, "
            "geometric dot-work, or delicate dagger/arrow line art)"
        ),
    },
    "gift certificate": {
        "card_description": (
            "One elegant gift certificate card. Elegant ivory/cream background with dark accents and gold borders with "
            "a niche-appropriate ornamental divider separating sections. "
            "Elegant script heading 'Gift Certificate' (same font family and "
            "size as used on all other cards). Dark placeholder fields with gold accents "
            "for TO:, FROM:, AMOUNT:, EXPIRES: each with thin underlines. "
            "Studio name placeholder at top. Contact details footer with "
            "email, phone, website"
        ),
        "card_count": "one card",
    },
    "gift voucher": {
        "card_description": (
            "One elegant gift voucher card. Elegant ivory/cream background with dark accents and gold borders with "
            "a niche-appropriate ornamental divider. Elegant script heading "
            "'Gift Voucher' (same font family and size as all other cards). "
            "White placeholder fields for RECIPIENT:, AMOUNT:, FROM:, "
            "VALID UNTIL: each with thin underlines. Studio name at top. "
            "Contact details footer"
        ),
        "card_count": "one card",
    },
    "price list": {
        "card_description": (
            "One price list / service menu card, larger format (A5 or A4 size). "
            "Elegant ivory/cream background with dark accents and gold borders with niche-appropriate ornamental dividers "
            "between sections. Elegant script heading 'Price List' (same font "
            "as all other cards). Organized sections with service categories "
            "and prices in clean columns. Studio name placeholder at top. "
            "Contact footer"
        ),
        "card_count": "one card",
    },
    "service menu": {
        "card_description": (
            "One service menu card, larger format. Elegant ivory/cream background with dark accents and gold borders with "
            "niche-appropriate ornamental dividers between pricing tiers. "
            "Script heading 'Service Menu' (same font as all other cards). "
            "Tiered pricing sections with service names and prices. Studio "
            "name at top, contact details at bottom"
        ),
        "card_count": "one card",
    },
    "business card": {
        "card_description": (
            "Two overlapping business cards (front and back visible). "
            "BOTH cards use the SAME elegant script font at the SAME size "
            "for their titles. "
            "Front: elegant ivory/cream background with dark accents, niche-appropriate ornamental "
            "divider, centered studio name in elegant script, minimal "
            "contact details (phone, email, website) in clean sans-serif. "
            "Back: elegant ivory/cream background with dark accents, large 'LOGO' circular placeholder, "
            "tagline, same ornamental design elements"
        ),
        "card_count": "two cards",
    },
    "aftercare card": {
        "card_description": (
            "One aftercare instruction card. Elegant ivory/cream background with dark accents and gold borders with "
            "niche-appropriate ornamental divider. Script heading 'Aftercare "
            "Instructions' (same font as all other cards). Numbered care "
            "steps in clean white text. Studio name and contact footer"
        ),
        "card_count": "one card",
    },
    "branding bundle": {
        "card_description": (
            "Multiple matching stationery pieces fanned out and overlapping — "
            "business card, appointment card, gift certificate, and letterhead. "
            "All share the same elegant ivory/cream background with dark accents with matching "
            "niche-appropriate ornamental design elements. Studio name "
            "placeholder consistent across all pieces"
        ),
        "card_count": "multiple cards fanned out",
    },
    "consent form": {
        "card_description": (
            "One consent/waiver form. Bold black header band with niche-"
            "appropriate ornamental divider. Script heading 'Consent Form' "
            "(same font as all other cards). Clean form fields for CLIENT "
            "NAME:, DATE:, SIGNATURE: with thin underlines. Professional "
            "legal feel with organized sections. Studio name at top"
        ),
        "card_count": "one form",
    },
    "social media": {
        "card_description": (
            "One social media post template (square format). Bold black "
            "background with niche-appropriate ornamental accents. Large "
            "script heading (same font as all other cards) with promotional "
            "text. Studio name and logo placeholder. Modern, Instagram-ready "
            "composition"
        ),
        "card_count": "one template",
    },
}

_DEFAULT_PROMPT_PARTS = {
    "card_description": (
        "One professional editable template card. Elegant ivory/cream background with dark accents and gold borders with "
        "a niche-appropriate ornamental divider. Elegant script heading with "
        "the product title. Clean white placeholder fields for NAME:, DATE:, "
        "PHONE:, EMAIL: each with thin underlines. Studio name at top, "
        "contact footer"
    ),
    "card_count": "one card",
}


def generate_product_image(api_key, prompt, aspect_ratio="3:4",
                           image_size="2K", max_retries=2, model=None):
    """Call Gemini to generate a product mockup image.

    Tries multiple Gemini models in priority order for resilience.
    Override the model with GEMINI_IMAGE_MODEL env var or the model arg.

    Args:
        api_key: Gemini API key (never logged).
        prompt: Text prompt describing the desired image.
        aspect_ratio: Image aspect ratio (e.g. "3:4", "2:1").
        image_size: Resolution tier ("1K", "2K").
        max_retries: Retry attempts on transient failures.
        model: Specific model name to use (overrides auto-selection).

    Returns:
        {"success": bool, "image_bytes": bytes|None,
         "mime_type": str|None, "model_used": str|None, "error": str|None}
    """
    import os as _os

    # Determine model list — explicit model, env var, or full fallback chain
    env_model = _os.getenv("GEMINI_IMAGE_MODEL", "")
    if model:
        models_to_try = [model]
    elif env_model:
        models_to_try = [env_model]
    else:
        models_to_try = list(GEMINI_IMAGE_MODELS)

    last_error = None

    for model_name in models_to_try:
        api_url = f"{GEMINI_API_BASE}/{model_name}:generateContent"
        print(f"       Trying Gemini model: {model_name}", flush=True)

        for attempt in range(max_retries + 1):
            if attempt > 0:
                wait = min(2 ** attempt, 10)
                print(f"       Gemini retry {attempt}/{max_retries} "
                      f"(waiting {wait}s)...", flush=True)
                time.sleep(wait)

            result = _call_gemini_api(api_key, prompt, aspect_ratio,
                                     image_size, api_url)

            if result["success"]:
                result["model_used"] = model_name
                return result

            last_error = result["error"]

            # Model not found → skip to next model immediately
            if "404" in str(last_error) or "not found" in str(last_error).lower():
                print(f"       Model {model_name} not available, trying next...",
                      flush=True)
                break

            # Only retry on transient errors
            if not _is_retryable(last_error):
                break

    return {
        "success": False, "image_bytes": None,
        "mime_type": None, "model_used": None,
        "error": f"All models failed. Last error: {last_error}",
    }


def build_product_prompt(product_type, niche, theme,
                         hero_title=None, tagline=None):
    """Build a Gemini prompt for generating a product mockup image.

    Returns the assembled prompt string optimised for professional
    Etsy product mockup images that match the PurpleOcaz store aesthetic.

    The prompt is engineered to produce consistent, Star-Seller-quality
    flat-lay product photography — not generic graphic design posters.

    Args:
        product_type: e.g. "appointment card", "gift certificate"
        niche: e.g. "tattoo", "nail", "hair"
        theme: e.g. "dark", "light"
        hero_title: Bold title for the footer banner (e.g. "Tattoo Studio
                    Appointment Card"). Auto-derived if not provided.
        tagline: Subtitle for the footer banner (e.g. "EDITABLE CANVA
                 TEMPLATE | INSTANT DOWNLOAD"). Default used if not provided.
    """
    pt_lower = product_type.lower().strip()
    parts = _DEFAULT_PROMPT_PARTS

    for key, template_parts in PROMPT_TEMPLATES.items():
        if key in pt_lower:
            parts = template_parts
            break

    # Auto-derive footer banner text if not provided
    if not hero_title:
        hero_title = f"{niche.title()} Studio {product_type.title()}"
    if not tagline:
        tagline = "EDITABLE CANVA TEMPLATE | INSTANT DOWNLOAD"

    # Niche-specific prop sets — ALL props should reflect the niche
    # so the customer instantly knows what industry the template is for
    niche_prop_sets = {
        "tattoo": (
            "TOP-LEFT corner: two small black tattoo ink bottles (one open with "
            "ink visible) and a sprig of dark eucalyptus leaves. "
            "LEFT side: a coiled tattoo machine (rotary pen style) resting flat. "
            "TOP-RIGHT corner: a sheet of tattoo flash art / tattoo stencil paper "
            "with simple line art designs, partially visible. "
            "BOTTOM-RIGHT or scattered: a few loose tattoo needles and a pair "
            "of black nitrile gloves folded neatly"
        ),
        "nail": (
            "TOP-LEFT corner: three bottles of nail polish in different colours "
            "(pink, red, nude) arranged at angles. "
            "LEFT side: a set of professional nail tools (cuticle pusher, nail "
            "file, small scissors) on a small white towel. "
            "TOP-RIGHT corner: scattered nail art gems and a thin nail art brush. "
            "BOTTOM-RIGHT: a small potted succulent and a sprig of dried flowers"
        ),
        "hair": (
            "TOP-LEFT corner: professional hair styling scissors (open) and a "
            "fine-tooth comb on a small white towel. "
            "LEFT side: a round hair brush and a few bobby pins scattered. "
            "TOP-RIGHT corner: a small amber bottle of hair oil/serum. "
            "BOTTOM-RIGHT: a sprig of eucalyptus and a hair clip"
        ),
        "barber": (
            "TOP-LEFT corner: a classic straight razor (closed) and a leather "
            "strop, with a sprig of eucalyptus. "
            "LEFT side: a shaving brush standing upright in a small bowl. "
            "TOP-RIGHT corner: a vintage barber comb and small scissors. "
            "BOTTOM-RIGHT: a small jar of pomade or beard oil"
        ),
        "beauty": (
            "TOP-LEFT corner: a compact mirror and a lipstick in a gold tube. "
            "LEFT side: a makeup brush set (3-4 brushes) fanned out. "
            "TOP-RIGHT corner: a small potted succulent and dried lavender. "
            "BOTTOM-RIGHT: a perfume bottle and a silk scrunchie"
        ),
        "spa": (
            "TOP-LEFT corner: a lit white candle in a ceramic holder and a "
            "sprig of eucalyptus. "
            "LEFT side: two rolled white towels stacked neatly. "
            "TOP-RIGHT corner: a small bowl of bath salts and a wooden scoop. "
            "BOTTOM-RIGHT: smooth massage stones and a small succulent"
        ),
        "lash": (
            "TOP-LEFT corner: a pair of false lash strips on a white surface "
            "and a lash applicator tool. "
            "LEFT side: a small bottle of lash adhesive and micro brushes. "
            "TOP-RIGHT corner: a lash wand/spoolie and a compact mirror. "
            "BOTTOM-RIGHT: dried flowers and a silk eye mask"
        ),
        "piercing": (
            "TOP-LEFT corner: a small velvet jewelry box (open) showing stud "
            "earrings and a sprig of eucalyptus. "
            "LEFT side: sterile piercing needles in sealed packets. "
            "TOP-RIGHT corner: a small mirror and antiseptic spray bottle. "
            "BOTTOM-RIGHT: scattered small jewelry pieces (hoops, studs)"
        ),
    }
    niche_accent = niche_prop_sets.get(niche.lower(), (
        "TOP-LEFT corner: a small potted succulent and eucalyptus leaves. "
        "LEFT side: a white ceramic coffee cup with latte art. "
        "TOP-RIGHT corner: tortoiseshell reading glasses, arms open. "
        "BOTTOM-RIGHT: a stylish pen and a small notebook"
    ))

    return (
        # === SCENE TYPE ===
        f"A styled overhead flat-lay product photograph shot from directly above, "
        f"as seen on a premium Etsy digital product listing. "
        f"This must look like a real photograph taken by a professional product "
        f"photographer — NOT a graphic design, NOT a digital mockup, NOT a poster. "

        # === IMAGE LAYOUT (TWO ZONES) ===
        f"The image is divided into two zones: the TOP 70% is the product "
        f"photography scene, and the BOTTOM 30% is a solid-colour footer banner. "

        # === BACKGROUND (TOP 70%) ===
        f"Top zone background: warm beige/cream textured craft paper surface. "
        f"The texture must be clearly VISIBLE — real kraft paper grain, fibres, "
        f"and subtle creases. It should look and feel tactile, like you could "
        f"touch the paper. NOT smooth, NOT flat, NOT digitally clean. Think "
        f"real recycled craft paper photographed up close. "

        # === THE PRODUCT (CARDS) ===
        f"Center of the top zone: {parts['card_description']}. "
        f"The {parts['card_count']} should be placed in the center, "
        f"slightly overlapping at a casual angle (not perfectly aligned — styled "
        f"to look natural, as if placed by hand on a desk). "

        # === NICHE CONTEXT ===
        f"This is a {niche} studio template product. "

        # === CARD TYPOGRAPHY (CRITICAL — READ CAREFULLY) ===
        f"ALL text on the cards must be PERFECTLY SHARP, SPELLED CORRECTLY, "
        f"and clearly LEGIBLE even at small sizes. This is non-negotiable. "
        f"Title text: elegant flowing script/calligraphy font, large enough "
        f"to read instantly. "
        f"Form field labels: clean UPPERCASE sans-serif font, moderate size. "
        f"Each field is: LABEL: followed by a thin horizontal line. "
        f"ALIGNMENT RULE: every horizontal fill-in line on a card must be "
        f"the SAME length and END at the SAME right-hand margin — creating "
        f"a clean, uniform, professional form layout. No stray lines, no "
        f"random slashes, no extra marks or symbols anywhere on the cards. "
        f"Do NOT render checkboxes, tick boxes, or any tiny UI elements. "
        f"Keep the form fields simple: LABEL + underline, nothing more. "
        f"Every word must be spelled correctly — no garbled, duplicated, "
        f"or overlapping text. "

        # === PROPS (NICHE-SPECIFIC PLACEMENT) ===
        f"Surrounding props arranged in a styled flat-lay composition — every "
        f"prop should clearly signal that this product is for a {niche} business: "
        f"{niche_accent}. "
        f"All props should be partially cropped at the edges of the frame to "
        f"create depth — they are secondary to the cards in the center. "
        f"Props should look real and photographed, not illustrated or clipart. "

        # === CARD DESIGN STYLE ===
        f"Card design style: the cards have warm IVORY/CREAM backgrounds "
        f"(#FAF6EF) with dark borders and gold accent lines. "
        f"Use niche-appropriate ornamental design elements as dividers and "
        f"accents — for {niche} this means fine-line art such as thin mandala "
        f"lines, compass roses, geometric dot-work borders, delicate dagger/"
        f"arrow line art, or ornate filigree patterns. These dividers should "
        f"be thin, dark, and elegant — separating the title from the form fields. "
        f"ALL cards must use the SAME script font family at the SAME size "
        f"for their titles to ensure a consistent, branded look across "
        f"the product range. "

        # === FOOTER BANNER (BOTTOM 30%) ===
        f"Below the product photography scene, there is a BOLD, HIGH-CONTRAST "
        f"footer banner that spans the full width of the image. This banner "
        f"must visually POP and be clearly distinct from the beige scene above. "
        f"Banner background colour: SOLID BLACK (#000000) — flat, opaque, "
        f"no texture, no transparency. Sharp clean edge where the black "
        f"banner meets the beige photography area above. "
        f"Banner text (centered, stacked on the black background): "
        f"Line 1 (large): '{hero_title}' in bold WHITE serif font "
        f"(like Playfair Display), large and prominent. "
        f"Line 2 (small): '{tagline}' in smaller uppercase "
        f"WHITE sans-serif tracking-wide letters underneath. "
        f"BOTTOM-RIGHT corner of the banner: a small circular badge with "
        f"the Canva logo 'C' icon and text 'EDIT IN CANVA' — white circle "
        f"with dark text, or inverted. "

        # === LIGHTING & PHOTOGRAPHY ===
        f"Lighting: soft, diffused natural daylight from the top-left. Gentle "
        f"shadows under the cards and props to give real depth and dimension. "
        f"No harsh shadows. The overall mood should be warm, inviting, and "
        f"professionally styled. "

        # === QUALITY & RESTRICTIONS ===
        f"The image should look indistinguishable from a professional product "
        f"photo on a top-selling Etsy shop. Crisp details, natural textures, "
        f"photorealistic rendering. "
        f"Do NOT include any human hands, fingers, arms, or body parts. "
        f"Do NOT include any real brand names, logos, or trademarked text. "
        f"Do NOT include any phones, tablets, laptops, or device screens. "
        f"Output: high-resolution photograph, sharp details, 300 DPI quality."
    )


def _call_gemini_api(api_key, prompt, aspect_ratio, image_size, api_url=None):
    """Make a single API call to Gemini. Returns result dict."""
    if api_url is None:
        api_url = f"{GEMINI_API_BASE}/{DEFAULT_MODEL}:generateContent"

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {
                "aspectRatio": aspect_ratio,
                "imageSize": image_size,
            },
        },
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(api_url, data=data, method="POST")
    req.add_header("x-goog-api-key", api_key)
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read().decode("utf-8"))

        # Extract image from response parts
        candidates = body.get("candidates", [])
        if not candidates:
            return {
                "success": False, "image_bytes": None,
                "mime_type": None, "error": "No candidates in Gemini response",
            }

        for part in candidates[0].get("content", {}).get("parts", []):
            inline = part.get("inlineData") or part.get("inline_data")
            if inline and "data" in inline:
                image_bytes = base64.b64decode(inline["data"])
                mime_type = inline.get("mimeType") or inline.get("mime_type", "image/png")
                return {
                    "success": True,
                    "image_bytes": image_bytes,
                    "mime_type": mime_type,
                    "error": None,
                }

        return {
            "success": False, "image_bytes": None,
            "mime_type": None, "error": "No image data in Gemini response",
        }

    except urllib.error.HTTPError as e:
        error_body = ""
        try:
            error_body = e.read().decode("utf-8")[:200]
        except Exception:
            pass
        return {
            "success": False, "image_bytes": None,
            "mime_type": None, "error": f"HTTP {e.code}: {error_body}",
        }
    except urllib.error.URLError as e:
        return {
            "success": False, "image_bytes": None,
            "mime_type": None, "error": f"URL error: {e.reason}",
        }
    except Exception as e:
        return {
            "success": False, "image_bytes": None,
            "mime_type": None, "error": f"{type(e).__name__}: {str(e)[:200]}",
        }


def _is_retryable(error_str):
    """Check if an error is transient and worth retrying."""
    if not error_str:
        return False
    retryable_codes = ("429", "500", "502", "503", "504")
    return any(code in error_str for code in retryable_codes)
