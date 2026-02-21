# =============================================================================
# workflows/auto_listing_creator/tools/canva_export_tool.py
#
# Canva integration for the Auto Listing Creator:
#   - Search your existing Canva designs by keyword
#   - Export ALL PAGES of each design as separate PNGs (for Etsy listing images)
#   - Export full design as PDF (for digital download preview)
#   - Download exported files to a local folder
#
# Your Canva designs have 5 pages each matching the Etsy listing image pattern:
#   Page 1 = Hero image (bundle overview)
#   Pages 2-5 = Individual template variants
#
# Requires: Canva OAuth tokens (run canva_oauth.py first)
# =============================================================================

import json
import time
import urllib.request
import urllib.error
import urllib.parse
import base64
import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
_workflow = os.path.dirname(_here)
_project_root = os.path.dirname(os.path.dirname(_workflow))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_tool import BaseTool

CANVA_API_URL = "https://api.canva.com/rest/v1"
CANVA_TOKEN_FILE = os.path.join(_workflow, "canva_tokens.json")
EXPORT_DIR = os.path.join(_workflow, "exports")

# Match existing PurpleOcaz listing image dimensions (portrait)
EXPORT_WIDTH = 2250
EXPORT_HEIGHT = 3000
MAX_PAGES = 5  # Etsy allows up to 10 images, shop standard is 5


class CanvaExportTool(BaseTool):
    """Search Canva designs and export all pages as PNG for Etsy listing images."""

    def execute(self, **kwargs) -> dict:
        search_queries    = kwargs.get("search_queries", [])
        canva_client_id   = kwargs.get("canva_client_id", "")
        canva_secret      = kwargs.get("canva_client_secret", "")
        export_png        = kwargs.get("export_png", True)
        export_pdf        = kwargs.get("export_pdf", True)

        try:
            access_token = self._load_token(canva_client_id, canva_secret)
            if not access_token:
                return {
                    "success": False, "data": None,
                    "error": "No Canva OAuth token. Run: python workflows/auto_listing_creator/canva_oauth.py",
                    "tool_name": self.get_name(), "metadata": {},
                }

            os.makedirs(EXPORT_DIR, exist_ok=True)

            all_exports = []

            for query in search_queries:
                print(f"     Searching Canva for: '{query}'...", flush=True)

                designs = self._search_designs(access_token, query)
                print(f"       Found {len(designs)} designs", flush=True)

                if not designs:
                    all_exports.append({
                        "query": query,
                        "design_id": None,
                        "design_title": None,
                        "png_paths": [],
                        "pdf_path": None,
                        "page_count": 0,
                        "status": "NO DESIGNS FOUND",
                    })
                    continue

                # Take the best match (first result)
                design = designs[0]
                design_id = design.get("id", "")
                design_title = design.get("title", "Untitled")
                page_count = design.get("page_count", 1)
                print(f"       Best match: '{design_title}' ({design_id}, {page_count} pages)", flush=True)

                export_result = {
                    "query": query,
                    "design_id": design_id,
                    "design_title": design_title,
                    "thumbnail": design.get("thumbnail", {}).get("url", ""),
                    "edit_url": design.get("urls", {}).get("edit_url", ""),
                    "png_paths": [],
                    "pdf_path": None,
                    "page_count": page_count,
                    "status": "FOUND",
                }

                # Export all pages as separate PNGs (up to MAX_PAGES)
                if export_png:
                    try:
                        pages_to_export = min(page_count, MAX_PAGES)
                        png_paths = self._export_all_pages(
                            access_token, design_id, design_title, pages_to_export,
                        )
                        export_result["png_paths"] = png_paths
                        export_result["status"] = "EXPORTED"
                        print(f"       {len(png_paths)} page PNGs exported", flush=True)
                        for i, p in enumerate(png_paths):
                            print(f"         Image {i+1}: {os.path.basename(p)}", flush=True)
                    except Exception as e:
                        print(f"       PNG export failed: {e}", flush=True)
                        # Fallback: try single-page export
                        try:
                            single_path = self._export_single_page(
                                access_token, design_id, "png", design_title,
                            )
                            export_result["png_paths"] = [single_path]
                            export_result["status"] = "EXPORTED"
                            print(f"       Fallback single PNG: {os.path.basename(single_path)}", flush=True)
                        except Exception as e2:
                            print(f"       Fallback also failed: {e2}", flush=True)

                # Export full PDF
                if export_pdf:
                    try:
                        pdf_path = self._export_single_page(
                            access_token, design_id, "pdf", design_title,
                        )
                        export_result["pdf_path"] = pdf_path
                        print(f"       PDF exported: {os.path.basename(pdf_path)}", flush=True)
                    except Exception as e:
                        print(f"       PDF export failed: {e}", flush=True)

                all_exports.append(export_result)
                time.sleep(1)

            exported_count = sum(1 for e in all_exports if e["status"] == "EXPORTED")

            return {
                "success": True,
                "data": {
                    "exports": all_exports,
                    "exported_count": exported_count,
                    "total_queries": len(search_queries),
                    "export_dir": EXPORT_DIR,
                },
                "error": None,
                "tool_name": self.get_name(),
                "metadata": {
                    "exported": exported_count,
                    "queries": len(search_queries),
                },
            }

        except Exception as e:
            return {
                "success": False, "data": None,
                "error": str(e),
                "tool_name": self.get_name(),
                "metadata": {"exception_type": type(e).__name__},
            }

    # =========================================================================
    # Canva API helpers
    # =========================================================================

    def _search_designs(self, access_token, query, limit=5):
        """Search user's Canva designs by keyword."""
        url = (
            f"{CANVA_API_URL}/designs"
            f"?query={urllib.parse.quote(query)}"
            f"&ownership=owned&sort_by=relevance&limit={limit}"
        )
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Bearer {access_token}")
        req.add_header("Accept", "application/json")

        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        return data.get("items", [])

    def _export_all_pages(self, access_token, design_id, title, page_count):
        """Export all pages of a design as separate PNG files.

        Returns list of file paths, one per page.
        """
        pages_to_export = list(range(1, page_count + 1))

        payload = {
            "design_id": design_id,
            "format": {
                "type": "png",
                "width": EXPORT_WIDTH,
                "height": EXPORT_HEIGHT,
                "pages": pages_to_export,
            },
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{CANVA_API_URL}/exports", data=data, method="POST",
        )
        req.add_header("Authorization", f"Bearer {access_token}")
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json")

        with urllib.request.urlopen(req, timeout=30) as resp:
            job = json.loads(resp.read().decode("utf-8"))

        job_id = job.get("job", {}).get("id", "")

        # Poll until complete
        wait = 3
        for _ in range(25):
            time.sleep(wait)
            status_req = urllib.request.Request(f"{CANVA_API_URL}/exports/{job_id}")
            status_req.add_header("Authorization", f"Bearer {access_token}")
            status_req.add_header("Accept", "application/json")

            with urllib.request.urlopen(status_req, timeout=30) as resp:
                status = json.loads(resp.read().decode("utf-8"))

            job_status = status.get("job", {}).get("status", "")
            if job_status == "success":
                urls = status.get("job", {}).get("urls", [])
                # Download each page as a separate file
                paths = []
                for i, url in enumerate(urls):
                    page_num = i + 1
                    filepath = self._download_file(url, title, "png", page_num)
                    paths.append(filepath)
                return paths
            elif job_status == "failed":
                raise RuntimeError(f"Multi-page export failed: {status}")
            wait = min(wait * 1.3, 8)

        raise RuntimeError("Multi-page export timed out")

    def _export_single_page(self, access_token, design_id, format_type, title):
        """Export page 1 of a design as PNG or full PDF. Returns file path."""
        if format_type == "png":
            payload = {
                "design_id": design_id,
                "format": {
                    "type": "png",
                    "width": EXPORT_WIDTH,
                    "height": EXPORT_HEIGHT,
                },
            }
        else:
            payload = {
                "design_id": design_id,
                "format": {
                    "type": "pdf",
                    "size": "a4",
                },
            }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{CANVA_API_URL}/exports", data=data, method="POST",
        )
        req.add_header("Authorization", f"Bearer {access_token}")
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json")

        with urllib.request.urlopen(req, timeout=30) as resp:
            job = json.loads(resp.read().decode("utf-8"))

        job_id = job.get("job", {}).get("id", "")

        wait = 2
        for _ in range(20):
            time.sleep(wait)
            status_req = urllib.request.Request(f"{CANVA_API_URL}/exports/{job_id}")
            status_req.add_header("Authorization", f"Bearer {access_token}")
            status_req.add_header("Accept", "application/json")

            with urllib.request.urlopen(status_req, timeout=30) as resp:
                status = json.loads(resp.read().decode("utf-8"))

            job_status = status.get("job", {}).get("status", "")
            if job_status == "success":
                urls = status.get("job", {}).get("urls", [])
                if urls:
                    return self._download_file(urls[0], title, format_type)
                break
            elif job_status == "failed":
                raise RuntimeError(f"Export failed: {status}")
            wait = min(wait * 1.5, 10)

        raise RuntimeError("Export timed out")

    def _download_file(self, url, title, format_type, page_num=None):
        """Download exported file to local exports directory."""
        safe_title = "".join(c if c.isalnum() or c in " -_" else "" for c in title)
        safe_title = safe_title.strip()[:50]

        if page_num:
            filename = f"{safe_title}_page{page_num}.{format_type}"
        else:
            filename = f"{safe_title}.{format_type}"

        filepath = os.path.join(EXPORT_DIR, filename)

        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=60) as resp:
            with open(filepath, "wb") as f:
                f.write(resp.read())

        return filepath

    # =========================================================================
    # Token management
    # =========================================================================

    def _load_token(self, client_id, client_secret):
        """Load and optionally refresh the Canva access token."""
        if not os.path.exists(CANVA_TOKEN_FILE):
            return None

        try:
            with open(CANVA_TOKEN_FILE) as f:
                tokens = json.load(f)

            access_token = tokens.get("access_token")
            if not access_token:
                return None

            # Quick test
            req = urllib.request.Request(f"{CANVA_API_URL}/users/me")
            req.add_header("Authorization", f"Bearer {access_token}")
            req.add_header("Accept", "application/json")
            urllib.request.urlopen(req, timeout=10)
            return access_token

        except urllib.error.HTTPError as e:
            if e.code == 401 and client_id and client_secret:
                return self._refresh_token(tokens, client_id, client_secret)
            return None
        except Exception:
            return None

    def _refresh_token(self, tokens, client_id, client_secret):
        """Refresh an expired Canva access token."""
        refresh_token = tokens.get("refresh_token")
        if not refresh_token:
            return None

        try:
            credentials = base64.b64encode(
                f"{client_id}:{client_secret}".encode("utf-8")
            ).decode("utf-8")

            data = urllib.parse.urlencode({
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            }).encode("utf-8")

            req = urllib.request.Request(
                f"{CANVA_API_URL}/oauth/token",
                data=data, method="POST",
            )
            req.add_header("Content-Type", "application/x-www-form-urlencoded")
            req.add_header("Authorization", f"Basic {credentials}")

            with urllib.request.urlopen(req, timeout=30) as resp:
                new_tokens = json.loads(resp.read().decode("utf-8"))

            with open(CANVA_TOKEN_FILE, "w") as f:
                json.dump(new_tokens, f, indent=2)

            return new_tokens.get("access_token")
        except Exception:
            return None
