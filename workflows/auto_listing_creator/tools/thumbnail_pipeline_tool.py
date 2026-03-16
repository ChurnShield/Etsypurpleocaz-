# =============================================================================
# workflows/auto_listing_creator/tools/thumbnail_pipeline_tool.py
#
# Autonomous Etsy thumbnail generator.
#
# Reads config/design_registry.json to look up base Canva designs with
# confirmed-unlocked element IDs, swaps card images and text via the
# Canva REST editing API, exports the result as PNG, applies the proven
# ETSY_CARD_SHADOW_PRESET via Pillow, and uploads to DigitalOcean Spaces.
#
# One transaction per operation, commit before next (LESSONS.md hard rule).
# =============================================================================

import io
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from PIL import Image, ImageFilter

_here = os.path.dirname(os.path.abspath(__file__))
_workflow = os.path.dirname(_here)
_project_root = os.path.dirname(os.path.dirname(_workflow))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_tool import BaseTool
from lib.common_tools.canva_token_manager import get_valid_token
from config import CANVA_POLL_MAX_ITERATIONS, CANVA_POLL_MAX_WAIT_SECONDS

CANVA_API_URL = "https://api.canva.com/rest/v1"
REGISTRY_PATH = os.path.join(_project_root, "config", "design_registry.json")


class ThumbnailPipelineTool(BaseTool):
    """Generate professional Etsy thumbnails from proven Canva base designs."""

    def execute(self, **kwargs) -> dict:
        niche = kwargs.get("niche", "tattoo")
        product_type = kwargs.get("product_type", "business_card")
        front_variant = kwargs.get("front_variant", "dark")
        back_variant = kwargs.get("back_variant", "light")
        title_text = kwargs.get("title_text")
        subtitle_text = kwargs.get("subtitle_text")
        export_pages = kwargs.get("export_pages", [1])
        apply_shadow = kwargs.get("apply_shadow", True)

        try:
            # 1. Load registry
            registry = self._load_registry()
            if not registry:
                return self._error("Design registry not found at " + REGISTRY_PATH)

            # 2. Look up design config
            design_cfg = self._lookup_design(registry, niche, product_type)
            if not design_cfg:
                return self._error(
                    f"No design registered for niche={niche}, "
                    f"product_type={product_type}"
                )

            # 3. Get Canva token (auto-refresh)
            access_token = get_valid_token()
            if not access_token:
                return self._error(
                    "No valid Canva token. Run canva_oauth_headless.py"
                )

            base_design_id = design_cfg["base_design_id"]
            page1 = design_cfg["pages"]["1"]
            card_designs = design_cfg["card_designs"]

            # 4. Resolve card assets
            front_asset = card_designs.get(front_variant, {}).get("canva_asset_id")
            back_asset = card_designs.get(back_variant, {}).get("canva_asset_id")
            if not front_asset or not back_asset:
                return self._error(
                    f"Card variant not found: front={front_variant}, "
                    f"back={back_variant}"
                )

            # 5. Swap front card (one transaction)
            front_slot = page1["card_slots"]["front_card"]
            print(f"     Swapping front card ({front_variant})...", flush=True)
            ok, err = self._swap_element(
                access_token, base_design_id,
                front_slot["element_id"], front_asset,
                f"{niche} {product_type} front card",
            )
            if not ok:
                return self._error(f"Front card swap failed: {err}")
            time.sleep(1)

            # 6. Swap back card (one transaction)
            back_slot = page1["card_slots"]["back_card"]
            print(f"     Swapping back card ({back_variant})...", flush=True)
            ok, err = self._swap_element(
                access_token, base_design_id,
                back_slot["element_id"], back_asset,
                f"{niche} {product_type} back card",
            )
            if not ok:
                return self._error(f"Back card swap failed: {err}")
            time.sleep(1)

            # 7. Update title text if provided (one transaction)
            if title_text:
                title_el = page1["text_elements"]["title"]["element_id"]
                print(f"     Updating title text...", flush=True)
                ok, err = self._update_text(
                    access_token, base_design_id, title_el, title_text,
                )
                if not ok:
                    print(f"     Title update failed (non-fatal): {err}", flush=True)
                time.sleep(1)

            # 8. Update subtitle text if provided (one transaction)
            if subtitle_text:
                sub_el = page1["text_elements"]["subtitle"]["element_id"]
                print(f"     Updating subtitle text...", flush=True)
                ok, err = self._update_text(
                    access_token, base_design_id, sub_el, subtitle_text,
                )
                if not ok:
                    print(f"     Subtitle update failed (non-fatal): {err}", flush=True)
                time.sleep(1)

            # 9. Export requested pages
            print(f"     Exporting page(s) {export_pages}...", flush=True)
            export_urls = self._export_pages(
                access_token, base_design_id,
                page1["width"], page1["height"], export_pages,
            )
            if not export_urls:
                return self._error("Export returned no URLs")

            # 10. Download, apply shadow, upload to Spaces
            shadow_preset = registry.get("shadow_preset", {})
            spaces_cfg = registry.get("spaces", {})
            results = []

            for i, url in enumerate(export_urls):
                page_num = export_pages[i] if i < len(export_pages) else i + 1
                print(f"     Processing page {page_num}...", flush=True)

                # Download
                image_bytes = self._download_bytes(url)
                if not image_bytes:
                    results.append({"page": page_num, "error": "download failed"})
                    continue

                # Apply shadow
                if apply_shadow and shadow_preset:
                    image_bytes = self._apply_shadow(image_bytes, shadow_preset)

                # Upload to Spaces
                ts = int(time.time())
                key = (
                    f"{spaces_cfg.get('thumbnail_prefix', 'thumbnails')}/"
                    f"{niche}_{product_type}_page{page_num}_{ts}.png"
                )
                cdn_url = self._upload_to_spaces(
                    image_bytes, key, spaces_cfg,
                )
                if not cdn_url:
                    results.append({"page": page_num, "error": "upload failed"})
                    continue

                results.append({
                    "page": page_num,
                    "spaces_url": cdn_url,
                    "spaces_key": key,
                    "size_bytes": len(image_bytes),
                })
                print(f"       -> {cdn_url}", flush=True)

            return {
                "success": True,
                "data": {
                    "base_design_id": base_design_id,
                    "niche": niche,
                    "product_type": product_type,
                    "front_variant": front_variant,
                    "back_variant": back_variant,
                    "pages": results,
                },
                "error": None,
                "tool_name": self.get_name(),
                "metadata": {
                    "pages_exported": len([r for r in results if "spaces_url" in r]),
                    "shadow_applied": apply_shadow,
                },
            }

        except Exception as e:
            return self._error(str(e), exception_type=type(e).__name__)

    # =========================================================================
    # Registry
    # =========================================================================

    @staticmethod
    def _load_registry(path=None):
        """Load design registry JSON. Returns dict or None."""
        p = path or REGISTRY_PATH
        if not os.path.exists(p):
            return None
        with open(p) as f:
            return json.load(f)

    @staticmethod
    def _lookup_design(registry, niche, product_type):
        """Navigate registry to find design config. Returns dict or None."""
        try:
            return registry["designs"][niche][product_type]
        except (KeyError, TypeError):
            return None

    # =========================================================================
    # Canva editing API — one transaction per operation
    # =========================================================================

    def _swap_element(self, token, design_id, element_id, asset_id, alt_text):
        """Start transaction, update_fill, commit. Returns (ok, error)."""
        # Start editing session
        session_id, err = self._start_session(token, design_id)
        if not session_id:
            return False, err

        # Perform update_fill
        ok, err = self._perform_operation(token, design_id, session_id, {
            "type": "update_fill",
            "element_id": element_id,
            "asset_type": "image",
            "asset_id": asset_id,
            "alt_text": alt_text,
        })
        if not ok:
            self._cancel_session(token, design_id, session_id)
            return False, err

        # Commit
        return self._commit_session(token, design_id, session_id)

    def _update_text(self, token, design_id, element_id, new_text):
        """Start transaction, replace_text, commit. Returns (ok, error)."""
        session_id, err = self._start_session(token, design_id)
        if not session_id:
            return False, err

        ok, err = self._perform_operation(token, design_id, session_id, {
            "type": "replace_text",
            "element_id": element_id,
            "text": new_text,
        })
        if not ok:
            self._cancel_session(token, design_id, session_id)
            return False, err

        return self._commit_session(token, design_id, session_id)

    def _start_session(self, token, design_id):
        """POST /designs/{id}/editing_sessions. Returns (session_id, error)."""
        try:
            resp = self._canva_post(
                token,
                f"/designs/{design_id}/editing_sessions",
                {},
            )
            sid = resp.get("editing_session", {}).get("id", "")
            if not sid:
                return None, f"No session ID in response: {resp}"
            return sid, None
        except Exception as e:
            return None, str(e)

    def _perform_operation(self, token, design_id, session_id, operation):
        """POST operation to editing session. Returns (ok, error)."""
        try:
            self._canva_post(
                token,
                f"/designs/{design_id}/editing_sessions/{session_id}/operations",
                {"operations": [operation]},
            )
            return True, None
        except Exception as e:
            return False, str(e)

    def _commit_session(self, token, design_id, session_id):
        """POST commit. Returns (ok, error)."""
        try:
            self._canva_post(
                token,
                f"/designs/{design_id}/editing_sessions/{session_id}/commit",
                {},
            )
            return True, None
        except Exception as e:
            return False, str(e)

    def _cancel_session(self, token, design_id, session_id):
        """POST cancel (best-effort)."""
        try:
            self._canva_post(
                token,
                f"/designs/{design_id}/editing_sessions/{session_id}/cancel",
                {},
            )
        except Exception:
            pass

    # =========================================================================
    # Canva export
    # =========================================================================

    def _export_pages(self, token, design_id, width, height, pages):
        """Export specific pages as PNG. Returns list of download URLs."""
        payload = {
            "design_id": design_id,
            "format": {
                "type": "png",
                "width": width,
                "height": height,
                "pages": pages,
            },
        }
        resp = self._canva_post(token, "/exports", payload)
        job_id = resp.get("job", {}).get("id", "")
        if not job_id:
            return []

        # Poll
        wait = 3
        for _ in range(CANVA_POLL_MAX_ITERATIONS):
            time.sleep(wait)
            status = self._canva_get(token, f"/exports/{job_id}")
            job_status = status.get("job", {}).get("status", "")
            if job_status == "success":
                return status.get("job", {}).get("urls", [])
            if job_status == "failed":
                return []
            wait = min(wait * 1.3, CANVA_POLL_MAX_WAIT_SECONDS)
        return []

    # =========================================================================
    # Shadow compositing (Pillow — mirrors TypeScript applyShadowToBuffer)
    # =========================================================================

    @staticmethod
    def _apply_shadow(image_bytes, preset):
        """Apply drop shadow with asymmetric padding. Returns PNG bytes."""
        img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")

        base_pad = preset.get("padding", 40)
        extra_r = preset.get("extra_right_padding", 80)
        extra_b = preset.get("extra_bottom_padding", 40)
        pad_t = base_pad
        pad_r = base_pad + extra_r
        pad_b = base_pad + extra_b
        pad_l = base_pad

        canvas_w = pad_l + img.width + pad_r
        canvas_h = pad_t + img.height + pad_b

        # Shadow rectangle at specified opacity
        r, g, b = preset.get("shadow_color", [0, 0, 0])
        alpha = int(preset.get("shadow_opacity", 0.75) * 255)
        shadow = Image.new("RGBA", (img.width, img.height), (r, g, b, alpha))

        # Place shadow on transparent canvas at offset
        canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        ox = pad_l + preset.get("shadow_offset_x", 15)
        oy = pad_t + preset.get("shadow_offset_y", 15)
        canvas.paste(shadow, (ox, oy))

        # Blur
        blur_radius = preset.get("shadow_blur", 12)
        canvas = canvas.filter(ImageFilter.GaussianBlur(radius=blur_radius))

        # Composite original on top (no alpha mask — paste opaque over shadow)
        canvas.paste(img, (pad_l, pad_t))

        # Flatten onto white background so shadow is visible in final output
        background = Image.new("RGBA", canvas.size, (255, 255, 255, 255))
        background = Image.alpha_composite(background, canvas)

        buf = io.BytesIO()
        background.save(buf, "PNG")
        return buf.getvalue()

    # =========================================================================
    # DigitalOcean Spaces upload
    # =========================================================================

    @staticmethod
    def _upload_to_spaces(image_bytes, key, spaces_cfg):
        """Upload PNG to Spaces. Returns CDN URL or None."""
        try:
            import boto3

            # Load creds from MCP .env (same source as TypeScript pipeline)
            mcp_env = os.path.join(_project_root, "purpleocaz-canva-mcp", ".env")
            spaces_key = os.environ.get("DO_SPACES_KEY", "")
            spaces_secret = os.environ.get("DO_SPACES_SECRET", "")

            if (not spaces_key or not spaces_secret) and os.path.exists(mcp_env):
                with open(mcp_env) as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("DO_SPACES_KEY="):
                            spaces_key = line.split("=", 1)[1]
                        elif line.startswith("DO_SPACES_SECRET="):
                            spaces_secret = line.split("=", 1)[1]

            if not spaces_key or not spaces_secret:
                print("     WARNING: DO_SPACES_KEY/SECRET not found", flush=True)
                return None

            bucket = spaces_cfg.get("bucket", "purpleocaz-assets")
            endpoint = spaces_cfg.get("endpoint", "https://lon1.digitaloceanspaces.com")
            region = spaces_cfg.get("region", "lon1")
            cdn_base = spaces_cfg.get("cdn_base",
                                      "https://purpleocaz-assets.lon1.digitaloceanspaces.com")

            s3 = boto3.client(
                "s3",
                endpoint_url=endpoint,
                aws_access_key_id=spaces_key,
                aws_secret_access_key=spaces_secret,
                region_name=region,
            )
            s3.put_object(
                Bucket=bucket,
                Key=key,
                Body=image_bytes,
                ContentType="image/png",
                ACL="public-read",
            )
            return f"{cdn_base}/{key}"
        except Exception as e:
            print(f"     Spaces upload failed: {e}", flush=True)
            return None

    # =========================================================================
    # HTTP helpers
    # =========================================================================

    @staticmethod
    def _canva_post(token, path, payload):
        """POST JSON to Canva API. Returns parsed response."""
        url = f"{CANVA_API_URL}{path}"
        data = json.dumps(payload).encode("utf-8") if payload else b"{}"
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json")
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))

    @staticmethod
    def _canva_get(token, path):
        """GET from Canva API. Returns parsed response."""
        url = f"{CANVA_API_URL}{path}"
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("Accept", "application/json")
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))

    @staticmethod
    def _download_bytes(url):
        """Download URL to bytes."""
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read()
        except Exception:
            return None

    # =========================================================================
    # Helpers
    # =========================================================================

    def _error(self, msg, exception_type=None):
        meta = {}
        if exception_type:
            meta["exception_type"] = exception_type
        return {
            "success": False,
            "data": None,
            "error": msg,
            "tool_name": self.get_name(),
            "metadata": meta,
        }
