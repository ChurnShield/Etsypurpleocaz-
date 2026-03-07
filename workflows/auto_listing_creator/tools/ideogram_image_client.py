# =============================================================================
# workflows/auto_listing_creator/tools/ideogram_image_client.py
#
# Ideogram V2 image generation client — typography-focused AI provider.
# Drop-in replacement for gemini_image_client.generate_product_image().
# Uses urllib (project standard) for HTTP calls.
#
# Ideogram excels at rendering legible, correctly-spelled text in images,
# making it ideal for text-heavy products (appointment cards, gift
# certificates, price lists, etc.).
#
# Model: V_2 (or V_2_TURBO for faster generation)
# API docs: https://developer.ideogram.ai/api-reference/api-reference/generate
# =============================================================================

import json
import time
import urllib.request
import urllib.error

IDEOGRAM_API_URL = "https://api.ideogram.ai/generate"

# Ideogram V2 supported aspect ratios (enum values)
_SUPPORTED_RATIOS = {
    "1:1": "ASPECT_1_1",
    "10:16": "ASPECT_10_16",
    "16:10": "ASPECT_16_10",
    "9:16": "ASPECT_9_16",
    "16:9": "ASPECT_16_9",
    "3:2": "ASPECT_3_2",
    "2:3": "ASPECT_2_3",
    "4:3": "ASPECT_4_3",
    "3:4": "ASPECT_3_4",
    "1:3": "ASPECT_1_3",
    "3:1": "ASPECT_3_1",
}

# Map unsupported ratios to closest Ideogram equivalent
_RATIO_FALLBACKS = {
    "4:5": "ASPECT_3_4",
    "5:4": "ASPECT_4_3",
    "2:1": "ASPECT_16_9",
    "1:2": "ASPECT_9_16",
}


def generate_product_image(api_key, prompt, aspect_ratio="3:4",
                           image_size="2K", max_retries=2):
    """Call Ideogram V2 to generate a product mockup image.

    Same interface as gemini_image_client.generate_product_image().

    Args:
        api_key: Ideogram API key (never logged).
        prompt: Text prompt describing the desired image.
        aspect_ratio: Image aspect ratio (e.g. "3:4", "1:1").
        image_size: Ignored (Ideogram controls resolution internally).
        max_retries: Retry attempts on transient failures.

    Returns:
        {"success": bool, "image_bytes": bytes|None,
         "mime_type": str|None, "error": str|None}
    """
    last_error = None

    for attempt in range(max_retries + 1):
        if attempt > 0:
            wait = min(2 ** attempt, 10)
            print(f"       Ideogram retry {attempt}/{max_retries} "
                  f"(waiting {wait}s)...", flush=True)
            time.sleep(wait)

        result = _call_ideogram_api(api_key, prompt, aspect_ratio)

        if result["success"]:
            return result

        last_error = result["error"]

        if not _is_retryable(last_error):
            return result

    return {
        "success": False, "image_bytes": None,
        "mime_type": None,
        "error": f"Failed after {max_retries + 1} attempts: {last_error}",
    }


def _resolve_aspect_ratio(ratio):
    """Return an Ideogram-compatible aspect ratio enum value."""
    if ratio in _SUPPORTED_RATIOS:
        return _SUPPORTED_RATIOS[ratio]
    if ratio in _RATIO_FALLBACKS:
        return _RATIO_FALLBACKS[ratio]
    # Default to 3:4 portrait for Etsy listings
    return "ASPECT_3_4"


def _call_ideogram_api(api_key, prompt, aspect_ratio):
    """Make a single API call to Ideogram. Returns result dict."""
    resolved_ratio = _resolve_aspect_ratio(aspect_ratio)

    payload = {
        "image_request": {
            "prompt": prompt,
            "model": "V_2",
            "aspect_ratio": resolved_ratio,
            "magic_prompt_option": "OFF",
            "style_type": "REALISTIC",
            "num_images": 1,
        }
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(IDEOGRAM_API_URL, data=data, method="POST")
    req.add_header("Api-Key", api_key)
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read().decode("utf-8"))

        images = body.get("data", [])
        if not images:
            return {
                "success": False, "image_bytes": None,
                "mime_type": None, "error": "No images in Ideogram response",
            }

        image_url = images[0].get("url")
        if not image_url:
            return {
                "success": False, "image_bytes": None,
                "mime_type": None, "error": "No image URL in Ideogram response",
            }

        # Check safety filter
        if not images[0].get("is_image_safe", True):
            return {
                "success": False, "image_bytes": None,
                "mime_type": None,
                "error": "Image flagged by Ideogram safety filter",
            }

        # Download the generated image
        img_req = urllib.request.Request(image_url)
        with urllib.request.urlopen(img_req, timeout=60) as img_resp:
            image_bytes = img_resp.read()

        return {
            "success": True,
            "image_bytes": image_bytes,
            "mime_type": "image/png",
            "error": None,
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
            "mime_type": None,
            "error": f"{type(e).__name__}: {str(e)[:200]}",
        }


def _is_retryable(error_str):
    """Check if an error is transient and worth retrying."""
    if not error_str:
        return False
    retryable_codes = ("429", "500", "502", "503", "504")
    return any(code in error_str for code in retryable_codes)
