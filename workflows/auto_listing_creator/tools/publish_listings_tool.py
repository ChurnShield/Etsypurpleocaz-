# =============================================================================
# workflows/auto_listing_creator/tools/publish_listings_tool.py
#
# Phase 3: Saves generated listings to Google Sheets "Listing Queue" tab
# AND optionally creates draft listings on Etsy via API (if OAuth has
# listings_w scope).
#
# Draft listings appear in your Etsy shop manager under "Listings > Drafts"
# — you review, attach your Canva template file + images, then publish.
# =============================================================================

import json
import time
import urllib.request
import urllib.error
import urllib.parse
import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
_workflow = os.path.dirname(_here)
_project_root = os.path.dirname(os.path.dirname(_workflow))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_tool import BaseTool

ETSY_BASE_URL = "https://openapi.etsy.com/v3/application"

try:
    import gspread
    from google.oauth2.service_account import Credentials
    _GSPREAD = True
except ImportError:
    _GSPREAD = False

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

QUEUE_HEADERS = [
    "Status", "Priority", "Effort", "Title", "Description",
    "Tags", "Price", "Product Type", "Why", "Etsy Draft ID",
]


class PublishListingsTool(BaseTool):
    """Save listings to Google Sheets queue and optionally create Etsy drafts."""

    def execute(self, **kwargs) -> dict:
        listings          = kwargs.get("generated_listings", [])
        credentials_file  = kwargs.get("credentials_file", "")
        spreadsheet_id    = kwargs.get("spreadsheet_id", "")
        queue_sheet_name  = kwargs.get("queue_sheet_name", "Listing Queue")
        # Etsy draft creation (optional)
        api_key           = kwargs.get("api_key", "")
        shop_id           = kwargs.get("shop_id", "")
        token_file        = kwargs.get("token_file", "")
        create_drafts     = kwargs.get("create_drafts", False)
        taxonomy_id       = kwargs.get("taxonomy_id", 1874)
        currency          = kwargs.get("currency", "GBP")
        # Image map: listing index -> list of local PNG paths
        image_map         = kwargs.get("image_map", {})
        # PDF map: listing index -> local PDF path (digital download file)
        pdf_map           = kwargs.get("pdf_map", {})

        if not listings:
            return {
                "success": False, "data": None,
                "error": "No listings to publish",
                "tool_name": self.get_name(), "metadata": {},
            }

        try:
            drafts_created = 0
            images_uploaded = 0
            draft_errors = []

            # -- Optionally create Etsy drafts --
            if create_drafts and api_key and shop_id and token_file:
                print("     [4a] Creating draft listings on Etsy...", flush=True)
                access_token = self._load_access_token(token_file, api_key)

                if access_token:
                    for i, listing in enumerate(listings):
                        try:
                            draft_id = self._create_etsy_draft(
                                api_key, shop_id, access_token,
                                listing, taxonomy_id, currency,
                            )
                            listing["etsy_draft_id"] = draft_id
                            drafts_created += 1
                            print(f"          Draft {i+1}/{len(listings)}: "
                                  f"{listing['title'][:40]}... (ID: {draft_id})", flush=True)

                            # Upload listing images if available
                            # image_map[i] can be a single path (str) or list of paths
                            img_data = image_map.get(i)
                            if img_data:
                                img_paths = img_data if isinstance(img_data, list) else [img_data]
                                for rank, img_path in enumerate(img_paths, start=1):
                                    if img_path and os.path.exists(img_path):
                                        try:
                                            self._upload_listing_image(
                                                api_key, shop_id, draft_id,
                                                access_token, img_path, rank=rank,
                                            )
                                            images_uploaded += 1
                                            print(f"            Image {rank}/{len(img_paths)}: "
                                                  f"{os.path.basename(img_path)}", flush=True)
                                            time.sleep(0.3)
                                        except Exception as img_err:
                                            print(f"            Image {rank} failed: "
                                                  f"{str(img_err)[:80]}", flush=True)

                            # Upload digital file (PDF/ZIP) if available
                            pdf_path = pdf_map.get(i)
                            if pdf_path and os.path.exists(pdf_path):
                                try:
                                    self._upload_digital_file(
                                        api_key, shop_id, draft_id,
                                        access_token, pdf_path,
                                    )
                                    print(f"            Digital file: "
                                          f"{os.path.basename(pdf_path)}", flush=True)
                                    # Activate digital delivery — required
                                    # PATCH after file upload so Etsy UI
                                    # recognises the file
                                    self._activate_digital_delivery(
                                        api_key, shop_id, draft_id,
                                        access_token,
                                    )
                                    print("            Digital delivery activated",
                                          flush=True)
                                    time.sleep(0.3)
                                except Exception as pdf_err:
                                    print(f"            Digital file FAILED: "
                                          f"{str(pdf_err)[:80]}", flush=True)

                            time.sleep(0.5)
                        except Exception as e:
                            err_msg = str(e)[:100]
                            listing["etsy_draft_id"] = f"ERROR: {err_msg}"
                            draft_errors.append(err_msg)
                            print(f"          Draft {i+1} FAILED: {err_msg}", flush=True)
                else:
                    print("          No valid OAuth token - skipping Etsy drafts", flush=True)
                    print("          Run: python workflows/etsy_analytics/etsy_oauth.py", flush=True)
                    for listing in listings:
                        listing["etsy_draft_id"] = "SKIPPED - no OAuth"
            else:
                for listing in listings:
                    listing["etsy_draft_id"] = "NOT ATTEMPTED"

            # -- Save to Google Sheets queue --
            print("     [4b] Saving to Listing Queue sheet...", flush=True)
            queue_rows = 0

            if _GSPREAD and os.path.exists(credentials_file) and spreadsheet_id:
                creds = Credentials.from_service_account_file(credentials_file, scopes=SCOPES)
                gc = gspread.authorize(creds)
                spreadsheet = gc.open_by_key(spreadsheet_id)

                ws = self._ensure_sheet(spreadsheet, queue_sheet_name, QUEUE_HEADERS)

                # Clear old data
                if ws.row_count > 1:
                    ws.batch_clear([f"A2:Z{ws.row_count}"])

                rows = []
                for listing in listings:
                    draft_id = listing.get("etsy_draft_id", "")
                    if isinstance(draft_id, int):
                        status = "DRAFT CREATED"
                    elif "ERROR" in str(draft_id):
                        status = "FAILED"
                    else:
                        status = "PENDING"

                    rows.append([
                        status,
                        listing.get("source_priority", ""),
                        listing.get("source_effort", ""),
                        listing.get("title", ""),
                        listing.get("description", "")[:500],  # Truncate for sheet
                        ", ".join(listing.get("tags", [])),
                        listing.get("price", 0),
                        listing.get("product_type", ""),
                        listing.get("source_why", "")[:200],
                        str(draft_id),
                    ])

                if rows:
                    ws.append_rows(rows, value_input_option="USER_ENTERED")
                    queue_rows = len(rows)

                print(f"          {queue_rows} listings saved to queue", flush=True)
            else:
                print("          Sheets save skipped (missing credentials)", flush=True)

            return {
                "success": True,
                "data": {
                    "queue_rows": queue_rows,
                    "drafts_created": drafts_created,
                    "images_uploaded": images_uploaded,
                    "draft_errors": len(draft_errors),
                    "listings": listings,
                },
                "error": None,
                "tool_name": self.get_name(),
                "metadata": {
                    "queue_rows": queue_rows,
                    "drafts_created": drafts_created,
                    "images_uploaded": images_uploaded,
                    "draft_errors": len(draft_errors),
                },
            }

        except Exception as e:
            return {
                "success": False, "data": None,
                "error": str(e),
                "tool_name": self.get_name(),
                "metadata": {"exception_type": type(e).__name__},
            }

    # -------------------------------------------------------------------------
    # Etsy draft creation
    # -------------------------------------------------------------------------

    def _create_etsy_draft(self, api_key, shop_id, access_token,
                           listing, taxonomy_id, currency):
        """Create a draft listing on Etsy via API.

        Etsy v3 createDraftListing uses application/x-www-form-urlencoded,
        NOT JSON. Tags are sent as repeated 'tags[]' fields.
        """
        price_float = float(listing.get("price", 4.99))
        # Etsy tags: max 13, each max 20 chars
        raw_tags = listing.get("tags", [])[:13]
        tags = [t[:20] for t in raw_tags if t.strip()]

        # Build form data — Etsy expects form-urlencoded
        form_fields = [
            ("quantity", "999"),
            ("title", listing["title"][:140]),
            ("description", listing.get("description", "")),
            ("price", str(price_float)),
            ("who_made", "i_did"),
            ("when_made", "2020_2025"),
            ("taxonomy_id", str(taxonomy_id)),
            ("type", "download"),
            ("is_supply", "false"),
        ]
        # Tags sent as comma-separated string
        if tags:
            form_fields.append(("tags", ",".join(tags)))

        data = urllib.parse.urlencode(form_fields).encode("utf-8")
        url = f"{ETSY_BASE_URL}/shops/{shop_id}/listings"

        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("x-api-key", api_key)
        req.add_header("Authorization", f"Bearer {access_token}")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        req.add_header("Accept", "application/json")

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
            return result.get("listing_id")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Etsy {e.code}: {body[:300]}")

    def _upload_listing_image(self, api_key, shop_id, listing_id,
                              access_token, image_path, rank=1):
        """Upload an image to an Etsy listing via multipart/form-data."""
        boundary = f"----EtsyBoundary{int(time.time() * 1000)}"
        filename = os.path.basename(image_path)

        with open(image_path, "rb") as f:
            image_data = f.read()

        # Build multipart body
        body = bytearray()
        # rank field
        body += f"--{boundary}\r\n".encode()
        body += b"Content-Disposition: form-data; name=\"rank\"\r\n\r\n"
        body += f"{rank}\r\n".encode()
        # image file
        body += f"--{boundary}\r\n".encode()
        body += f"Content-Disposition: form-data; name=\"image\"; filename=\"{filename}\"\r\n".encode()
        body += b"Content-Type: image/png\r\n\r\n"
        body += image_data
        body += b"\r\n"
        body += f"--{boundary}--\r\n".encode()

        url = f"{ETSY_BASE_URL}/shops/{shop_id}/listings/{listing_id}/images"
        req = urllib.request.Request(url, data=bytes(body), method="POST")
        req.add_header("x-api-key", api_key)
        req.add_header("Authorization", f"Bearer {access_token}")
        req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
        req.add_header("Accept", "application/json")

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body_text = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Image upload {e.code}: {body_text[:200]}")

    def _upload_digital_file(self, api_key, shop_id, listing_id,
                             access_token, file_path):
        """Upload a digital file (PDF) to an Etsy listing.

        This is the actual downloadable product the customer receives.
        Uses: POST /v3/application/shops/{shop_id}/listings/{listing_id}/files
        """
        boundary = f"----EtsyFileBoundary{int(time.time() * 1000)}"
        filename = os.path.basename(file_path)

        with open(file_path, "rb") as f:
            file_data = f.read()

        # Build multipart body
        body = bytearray()
        # name field (display name for the file)
        body += f"--{boundary}\r\n".encode()
        body += b"Content-Disposition: form-data; name=\"name\"\r\n\r\n"
        body += f"{filename}\r\n".encode()
        # file field
        body += f"--{boundary}\r\n".encode()
        body += (f"Content-Disposition: form-data; name=\"file\"; "
                 f"filename=\"{filename}\"\r\n").encode()
        body += b"Content-Type: application/pdf\r\n\r\n"
        body += file_data
        body += b"\r\n"
        body += f"--{boundary}--\r\n".encode()

        url = f"{ETSY_BASE_URL}/shops/{shop_id}/listings/{listing_id}/files"
        req = urllib.request.Request(url, data=bytes(body), method="POST")
        req.add_header("x-api-key", api_key)
        req.add_header("Authorization", f"Bearer {access_token}")
        req.add_header("Content-Type",
                        f"multipart/form-data; boundary={boundary}")
        req.add_header("Accept", "application/json")

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body_text = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"File upload {e.code}: {body_text[:200]}")

    def _activate_digital_delivery(self, api_key, shop_id, listing_id,
                                    access_token):
        """PATCH listing with type=download to activate digital delivery.

        Etsy requires this step AFTER uploading a digital file — without
        it the file exists in the API but does not appear in the listing
        editor UI and buyers cannot download it.
        """
        data = urllib.parse.urlencode({"type": "download"}).encode("utf-8")
        url = f"{ETSY_BASE_URL}/shops/{shop_id}/listings/{listing_id}"

        req = urllib.request.Request(url, data=data, method="PATCH")
        req.add_header("x-api-key", api_key)
        req.add_header("Authorization", f"Bearer {access_token}")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        req.add_header("Accept", "application/json")

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"Activate digital delivery {e.code}: {body[:300]}"
            )

    def _load_access_token(self, token_file, api_key):
        """Load and validate OAuth access token."""
        if not os.path.exists(token_file):
            return None

        try:
            with open(token_file) as f:
                tokens = json.load(f)

            access_token = tokens.get("access_token")
            if not access_token:
                return None

            # Quick validation
            req = urllib.request.Request(f"{ETSY_BASE_URL}/users/me")
            req.add_header("x-api-key", api_key)
            req.add_header("Authorization", f"Bearer {access_token}")
            req.add_header("Accept", "application/json")
            urllib.request.urlopen(req, timeout=10)
            return access_token

        except urllib.error.HTTPError as e:
            if e.code == 401:
                # Try refresh
                return self._try_refresh(tokens, api_key, token_file)
            return None
        except Exception:
            return None

    def _try_refresh(self, tokens, api_key, token_file):
        """Refresh expired OAuth token."""
        refresh_token = tokens.get("refresh_token")
        if not refresh_token:
            return None
        try:
            keystring = api_key.split(":")[0] if ":" in api_key else api_key
            data = urllib.parse.urlencode({
                "grant_type": "refresh_token",
                "client_id": keystring,
                "refresh_token": refresh_token,
            }).encode("utf-8")
            req = urllib.request.Request(
                "https://api.etsy.com/v3/public/oauth/token",
                data=data, method="POST",
            )
            req.add_header("Content-Type", "application/x-www-form-urlencoded")
            req.add_header("x-api-key", api_key)
            with urllib.request.urlopen(req, timeout=30) as resp:
                new_tokens = json.loads(resp.read().decode("utf-8"))
            with open(token_file, "w") as f:
                json.dump(new_tokens, f, indent=2)
            return new_tokens.get("access_token")
        except Exception:
            return None

    # -------------------------------------------------------------------------
    # Google Sheets helpers
    # -------------------------------------------------------------------------

    def _ensure_sheet(self, spreadsheet, name, headers):
        try:
            ws = spreadsheet.worksheet(name)
        except gspread.exceptions.WorksheetNotFound:
            ws = spreadsheet.add_worksheet(title=name, rows=500, cols=len(headers))
            ws.append_row(headers, value_input_option="USER_ENTERED")
            return ws
        first_row = ws.row_values(1)
        if not first_row:
            ws.append_row(headers, value_input_option="USER_ENTERED")
        elif first_row != headers:
            ws.update(range_name="A1", values=[headers], value_input_option="USER_ENTERED")
        return ws
