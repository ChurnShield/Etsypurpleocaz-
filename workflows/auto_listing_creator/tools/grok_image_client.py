# =============================================================================
# workflows/auto_listing_creator/tools/grok_image_client.py
#
# xAI Grok image generation client.
# Uses grok-2-image-1212 model via https://api.x.ai/v1/images/generations
# =============================================================================

import json
import time
import urllib.request
import urllib.error

GROK_API_URL = "https://api.x.ai/v1/images/generations"
GROK_MODEL = "grok-2-image-1212"


def generate_grok_image(api_key, prompt, n=1, max_retries=2):
    """Generate an image using the xAI Grok image API.

    Returns dict matching the project's image client convention:
        {success: bool, image_bytes: bytes|None, mime_type: str|None, error: str|None}
    """
    last_error = None
    for attempt in range(max_retries + 1):
        if attempt > 0:
            wait = min(2 ** attempt, 10)
            print(f"       Grok retry {attempt}/{max_retries} (waiting {wait}s)...",
                  flush=True)
            time.sleep(wait)
        result = _call_grok_api(api_key, prompt, n)
        if result["success"]:
            return result
        last_error = result["error"]
        if not _is_retryable(last_error):
            return result
    return {
        "success": False, "image_bytes": None, "mime_type": None,
        "error": f"Failed after {max_retries + 1} attempts: {last_error}",
    }


def _call_grok_api(api_key, prompt, n=1):
    """Make a single request to the xAI image generation endpoint."""
    payload = {
        "model": GROK_MODEL,
        "prompt": prompt,
        "n": n,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(GROK_API_URL, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read().decode("utf-8"))

        images = body.get("data", [])
        if not images:
            return {
                "success": False, "image_bytes": None, "mime_type": None,
                "error": "No images in Grok response",
            }

        image_url = images[0].get("url")
        if not image_url:
            return {
                "success": False, "image_bytes": None, "mime_type": None,
                "error": "No URL in Grok response",
            }

        with urllib.request.urlopen(image_url, timeout=60) as img_resp:
            image_bytes = img_resp.read()

        return {
            "success": True, "image_bytes": image_bytes,
            "mime_type": "image/png", "error": None,
        }

    except urllib.error.HTTPError as e:
        error_body = ""
        try:
            error_body = e.read().decode("utf-8")[:200]
        except Exception:
            pass
        return {
            "success": False, "image_bytes": None, "mime_type": None,
            "error": f"HTTP {e.code}: {error_body}",
        }
    except urllib.error.URLError as e:
        return {
            "success": False, "image_bytes": None, "mime_type": None,
            "error": f"URL error: {e.reason}",
        }
    except Exception as e:
        return {
            "success": False, "image_bytes": None, "mime_type": None,
            "error": f"{type(e).__name__}: {str(e)[:200]}",
        }


def _is_retryable(error_str):
    if not error_str:
        return False
    return any(code in error_str for code in ("429", "500", "502", "503", "504"))
