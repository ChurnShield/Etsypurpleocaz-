# =============================================================================
# workflows/auto_listing_creator/tools/image_provider.py
#
# Unified image provider dispatcher. Routes image generation to Ideogram,
# Grok, or both based on IMAGE_PROVIDER env var.
#
# IMAGE_PROVIDER=ideogram  -> Ideogram only (default)
# IMAGE_PROVIDER=grok      -> Grok only
# IMAGE_PROVIDER=both      -> Generate with both, save side-by-side
# =============================================================================

import os

from tools.ideogram_image_client import generate_product_image as _ideogram_generate
from tools.grok_image_client import generate_grok_image as _grok_generate


def generate_images(prompt, ideogram_api_key="", grok_api_key="",
                    aspect_ratio="3:4", provider=None):
    """Generate image(s) based on the configured provider.

    Args:
        prompt: The image generation prompt.
        ideogram_api_key: API key for Ideogram.
        grok_api_key: API key for xAI Grok.
        aspect_ratio: Aspect ratio for Ideogram (Grok uses prompt only).
        provider: Override for IMAGE_PROVIDER env var.

    Returns:
        dict with keys:
            success: bool
            results: list of {provider: str, image_bytes: bytes, error: str|None}
            error: str|None (only if all providers failed)
    """
    if provider is None:
        provider = os.getenv("IMAGE_PROVIDER", "ideogram").lower().strip()

    results = []

    if provider in ("ideogram", "both"):
        if ideogram_api_key:
            print("       Generating image with Ideogram...", flush=True)
            ideo_result = _ideogram_generate(
                ideogram_api_key, prompt, aspect_ratio=aspect_ratio,
            )
            results.append({
                "provider": "ideogram",
                "image_bytes": ideo_result.get("image_bytes"),
                "success": ideo_result["success"],
                "error": ideo_result.get("error"),
            })
            if ideo_result["success"]:
                print(f"       Ideogram: OK "
                      f"({len(ideo_result['image_bytes']) // 1024}KB)", flush=True)
            else:
                print(f"       Ideogram: FAILED — {ideo_result['error'][:80]}",
                      flush=True)
        else:
            results.append({
                "provider": "ideogram",
                "image_bytes": None,
                "success": False,
                "error": "No IDEOGRAM_API_KEY configured",
            })
            if provider == "ideogram":
                print("       Ideogram: skipped (no API key)", flush=True)

    if provider in ("grok", "both"):
        if grok_api_key:
            print("       Generating image with Grok...", flush=True)
            grok_result = _grok_generate(grok_api_key, prompt)
            results.append({
                "provider": "grok",
                "image_bytes": grok_result.get("image_bytes"),
                "success": grok_result["success"],
                "error": grok_result.get("error"),
            })
            if grok_result["success"]:
                print(f"       Grok: OK "
                      f"({len(grok_result['image_bytes']) // 1024}KB)", flush=True)
            else:
                print(f"       Grok: FAILED — {grok_result['error'][:80]}",
                      flush=True)
        else:
            results.append({
                "provider": "grok",
                "image_bytes": None,
                "success": False,
                "error": "No XAI_API_KEY configured",
            })
            if provider == "grok":
                print("       Grok: skipped (no API key)", flush=True)

    any_success = any(r["success"] for r in results)
    error = None
    if not any_success:
        errors = [f"{r['provider']}: {r['error']}" for r in results]
        error = "; ".join(errors)

    return {
        "success": any_success,
        "results": results,
        "error": error,
    }


def get_best_result(gen_output):
    """Return the first successful result from generate_images output.

    Used by the pipeline when it needs a single image (e.g. for compositing).
    Prefers Ideogram over Grok when both succeed.
    """
    for r in gen_output.get("results", []):
        if r["success"] and r["image_bytes"]:
            return r
    return None


def save_provider_images(gen_output, export_dir, base_name):
    """Save all successful images with provider-suffixed filenames.

    Returns list of saved file paths.
    E.g. listing_0_ideogram.png, listing_0_grok.png
    """
    saved = []
    for r in gen_output.get("results", []):
        if r["success"] and r["image_bytes"]:
            filename = f"{base_name}_{r['provider']}.png"
            path = os.path.join(export_dir, filename)
            with open(path, "wb") as f:
                f.write(r["image_bytes"])
            saved.append(path)
            print(f"       Saved: {filename} ({len(r['image_bytes']) // 1024}KB)",
                  flush=True)
    return saved
