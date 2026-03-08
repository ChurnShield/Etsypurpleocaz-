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

GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-flash-image:generateContent"
)

# ---------------------------------------------------------------------------
# PurpleOcaz brand-aligned prompt system
#
# Visual identity (from live store reference images):
#   - Background: warm beige/cream textured craft paper
#   - Card style: bold black cards with torn/ripped paper edge detail
#   - Props: eucalyptus leaves, terracotta succulent pot, latte art coffee,
#            tortoiseshell reading glasses, marble pens, wicker trays
#   - Layout: styled overhead flat-lay, cards overlapping at slight angle
#   - Typography on cards: script/calligraphy headings, clean sans-serif fields
#   - Badge: circular "EDIT IN CANVA" (bottom-right of scene)
#   - Bottom band: bold product title + tagline (added in compositing step)
# ---------------------------------------------------------------------------

# Product-type-specific prompt components
#
# IMPORTANT: card_description is NO LONGER USED for the main hero prompt.
# The hero prompt now requests blank cards (no text) and uses card_count only.
# Text is composited afterwards by text_compositor.py using real TTF fonts.
#
# These descriptions are kept for reference and for any future use.
PROMPT_TEMPLATES = {
    "appointment card": {
        "card_count": "two cards",
    },
    "gift certificate": {
        "card_count": "one card",
    },
    "gift voucher": {
        "card_count": "one card",
    },
    "price list": {
        "card_count": "one card",
    },
    "service menu": {
        "card_count": "one card",
    },
    "business card": {
        "card_count": "two cards",
    },
    "aftercare card": {
        "card_count": "one card",
    },
    "branding bundle": {
        "card_count": "multiple cards fanned out",
    },
    "consent form": {
        "card_count": "one form",
    },
    "social media": {
        "card_count": "one template",
    },
}

_DEFAULT_PROMPT_PARTS = {
    "card_count": "one card",
}


def generate_product_image(api_key, prompt, aspect_ratio="3:4",
                           image_size="2K", max_retries=2):
    """Call Gemini 2.5 Flash to generate a product mockup image.

    Args:
        api_key: Gemini API key (never logged).
        prompt: Text prompt describing the desired image.
        aspect_ratio: Image aspect ratio (e.g. "3:4", "2:1").
        image_size: Resolution tier ("1K", "2K").
        max_retries: Retry attempts on transient failures.

    Returns:
        {"success": bool, "image_bytes": bytes|None,
         "mime_type": str|None, "error": str|None}
    """
    last_error = None

    for attempt in range(max_retries + 1):
        if attempt > 0:
            wait = min(2 ** attempt, 10)
            print(f"       Gemini retry {attempt}/{max_retries} "
                  f"(waiting {wait}s)...", flush=True)
            time.sleep(wait)

        result = _call_gemini_api(api_key, prompt, aspect_ratio, image_size)

        if result["success"]:
            return result

        last_error = result["error"]

        # Only retry on transient errors
        if not _is_retryable(last_error):
            return result

    return {
        "success": False, "image_bytes": None,
        "mime_type": None, "error": f"Failed after {max_retries + 1} attempts: {last_error}",
    }


def build_product_prompt(product_type, niche, theme,
                         hero_title=None, tagline=None):
    """Build a Gemini prompt for generating a product mockup image.

    Returns the assembled prompt string optimised for professional
    Etsy product mockup images that match the PurpleOcaz store aesthetic.

    The prompt is engineered to produce consistent, Star-Seller-quality
    flat-lay product photography — not generic graphic design posters.

    IMPORTANT: Text is NOT rendered by Gemini. The prompt asks for BLANK
    white cards with only decorative dividers/ornaments. All typography
    (card titles, field labels, footer banner, badge) is composited
    afterwards by text_compositor.py using real TTF fonts for pixel-perfect
    results.

    Args:
        product_type: e.g. "appointment card", "gift certificate"
        niche: e.g. "tattoo", "nail", "hair"
        theme: e.g. "dark", "light"
        hero_title: (unused — text added by compositor, kept for API compat)
        tagline: (unused — text added by compositor, kept for API compat)
    """
    pt_lower = product_type.lower().strip()
    parts = _DEFAULT_PROMPT_PARTS

    for key, template_parts in PROMPT_TEMPLATES.items():
        if key in pt_lower:
            parts = template_parts
            break

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

    # Card count description (without text-specific instructions)
    card_count = parts.get("card_count", "one card")

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

        # === THE PRODUCT (BLANK CARDS — NO TEXT) ===
        f"Center of the top zone: {card_count} — pure white (#FFFFFF) "
        f"rectangular cards with slightly rounded corners, placed in the center, "
        f"slightly overlapping at a casual angle (not perfectly aligned — styled "
        f"to look natural, as if placed by hand on a desk). "
        f"The cards must be COMPLETELY BLANK — NO text whatsoever. No titles, "
        f"no labels, no words, no letters, no numbers. Just clean white cards. "
        f"Each card should have a thin subtle double-line grey border around "
        f"the edge, and a single thin ornamental divider line across the "
        f"upper third of the card — a {niche}-appropriate fine-line art "
        f"element (thin mandala, geometric dot-work, filigree, or delicate "
        f"line art). The divider is purely decorative. "
        f"Below the divider, the card is EMPTY white space. "

        # === NICHE CONTEXT ===
        f"This is a {niche} studio template product. "

        # === PROPS (NICHE-SPECIFIC PLACEMENT) ===
        f"Surrounding props arranged in a styled flat-lay composition — every "
        f"prop should clearly signal that this product is for a {niche} business: "
        f"{niche_accent}. "
        f"All props should be partially cropped at the edges of the frame to "
        f"create depth — they are secondary to the cards in the center. "
        f"Props should look real and photographed, not illustrated or clipart. "

        # === FOOTER BANNER (BOTTOM 30%) — BLANK ===
        f"Below the product photography scene, there is a SOLID BLACK (#000000) "
        f"footer banner that spans the full width of the image. "
        f"The banner must be completely EMPTY — solid flat black, no text, "
        f"no logos, no badges, nothing. Just a clean black rectangle. "
        f"Sharp clean edge where the black banner meets the beige scene above. "

        # === LIGHTING & PHOTOGRAPHY ===
        f"Lighting: soft, diffused natural daylight from the top-left. Gentle "
        f"shadows under the cards and props to give real depth and dimension. "
        f"No harsh shadows. The overall mood should be warm, inviting, and "
        f"professionally styled. "

        # === QUALITY & RESTRICTIONS ===
        f"The image should look indistinguishable from a professional product "
        f"photo on a top-selling Etsy shop. Crisp details, natural textures, "
        f"photorealistic rendering. "
        f"Do NOT include ANY text, words, letters, or numbers anywhere in the "
        f"image. The cards and banner must be completely blank. "
        f"Do NOT include any human hands, fingers, arms, or body parts. "
        f"Do NOT include any real brand names, logos, or trademarked text. "
        f"Do NOT include any phones, tablets, laptops, or device screens. "
        f"Output: high-resolution photograph, sharp details, 300 DPI quality."
    )


def _call_gemini_api(api_key, prompt, aspect_ratio, image_size):
    """Make a single API call to Gemini. Returns result dict."""
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
    req = urllib.request.Request(GEMINI_API_URL, data=data, method="POST")
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
