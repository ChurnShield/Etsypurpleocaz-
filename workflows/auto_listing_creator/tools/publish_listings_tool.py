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
        taxonomy_id       = kwargs.get("taxonomy_id", 69150467)
        currency          = kwargs.get("currency", "GBP")

        if not listings:
            return {
                "success": False, "data": None,
                "error": "No listings to publish",
                "tool_name": self.get_name(), "metadata": {},
            }

        try:
            drafts_created = 0
            draft_errors = []

            # -- Optionally create Etsy drafts --
            if create_drafts and api_key and shop_id and token_file:
                print("     [3a] Creating draft listings on Etsy...", flush=True)
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
            print("     [3b] Saving to Listing Queue sheet...", flush=True)
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
                    "draft_errors": len(draft_errors),
                    "listings": listings,
                },
                "error": None,
                "tool_name": self.get_name(),
                "metadata": {
                    "queue_rows": queue_rows,
                    "drafts_created": drafts_created,
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
        """Create a draft listing on Etsy via API."""
        # Build the listing payload
        # Price must be in the minor unit (pence/cents)
        price_float = float(listing.get("price", 4.99))
        price_amount = int(price_float * 100)

        payload = {
            "quantity": 999,
            "title": listing["title"][:140],
            "description": listing.get("description", ""),
            "price": price_float,
            "who_made": "i_did",
            "when_made": "2020_2025",
            "taxonomy_id": taxonomy_id,
            "tags": listing.get("tags", [])[:13],
            "type": "download",  # digital product
            "is_supply": False,
        }

        data = json.dumps(payload).encode("utf-8")
        url = f"{ETSY_BASE_URL}/shops/{shop_id}/listings"

        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("x-api-key", api_key)
        req.add_header("Authorization", f"Bearer {access_token}")
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json")

        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))

        return result.get("listing_id")

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
