# =============================================================================
# workflows/auto_listing_creator/tools/replicate_image_client.py
#
# FLUX.1 [schnell] image generation via Replicate API.
# Drop-in replacement for gemini_image_client.generate_product_image().
# Uses urllib (project standard) for HTTP calls.
#
# Model: black-forest-labs/flux-schnell (~$0.003/image, Apache 2.0 licensed)
# =============================================================================

import json
import time
import urllib.request
import urllib.error

REPLICATE_MODEL_URL = (
    "https://api.replicate.com/v1/models/"
    "black-forest-labs/flux-schnell/predictions"
)

# FLUX schnell supported aspect ratios
_SUPPORTED_RATIOS = {"1:1", "16:9", "21:9", "2:3", "3:2", "4:5", "5:4",
                     "9:16", "9:21"}

# Map unsupported ratios to closest supported
_RATIO_FALLBACKS = {
    "3:4": "4:5",
    "4:3": "3:2",
}


def generate_product_image(api_key, prompt, aspect_ratio="1:1",
                           image_size="1K", max_retries=2):
    """Call FLUX.1 schnell via Replicate to generate an image.

    Same interface as gemini_image_client.generate_product_image().

    Args:
        api_key: Replicate API token (never logged).
        prompt: Text prompt describing the desired image.
        aspect_ratio: Image aspect ratio (e.g. "1:1", "4:5").
        image_size: Ignored (FLUX outputs at native resolution).
        max_retries: Retry attempts on transient failures.

    Returns:
        {"success": bool, "image_bytes": bytes|None,
         "mime_type": str|None, "error": str|None}
    """
    last_error = None

    for attempt in range(max_retries + 1):
        if attempt > 0:
            wait = min(2 ** attempt, 10)
            print(f"       Replicate retry {attempt}/{max_retries} "
                  f"(waiting {wait}s)...", flush=True)
            time.sleep(wait)

        result = _call_replicate_api(api_key, prompt, aspect_ratio)

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
    """Return a FLUX-supported aspect ratio, falling back if needed."""
    if ratio in _SUPPORTED_RATIOS:
        return ratio
    return _RATIO_FALLBACKS.get(ratio, "1:1")


def _call_replicate_api(api_key, prompt, aspect_ratio):
    """Make a single synchronous API call to Replicate. Returns result dict."""
    resolved_ratio = _resolve_aspect_ratio(aspect_ratio)

    payload = {
        "input": {
            "prompt": prompt,
            "aspect_ratio": resolved_ratio,
            "output_format": "png",
            "num_outputs": 1,
            "go_fast": True,
        }
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(REPLICATE_MODEL_URL, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Prefer", "wait")  # Sync mode — blocks until complete

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read().decode("utf-8"))

        status = body.get("status")
        if status == "failed":
            error = body.get("error", "Unknown error")
            return {
                "success": False, "image_bytes": None,
                "mime_type": None,
                "error": f"Prediction failed: {error}",
            }

        output = body.get("output", [])
        if not output:
            return {
                "success": False, "image_bytes": None,
                "mime_type": None,
                "error": "No output in Replicate response",
            }

        # Output is a list of URLs — download the first image
        image_url = output[0]
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
