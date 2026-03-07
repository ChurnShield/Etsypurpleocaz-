# =============================================================================
# workflows/notebooklm_audio/tools/audio_publisher_tool.py
#
# Phase 4: Publishes audio products to Google Sheets and Etsy.
# =============================================================================

import json
import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
_workflow = os.path.dirname(_here)
_project_root = os.path.dirname(os.path.dirname(_workflow))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_tool import BaseTool


class AudioPublisherTool(BaseTool):
    """Publishes audio products to Google Sheets and Etsy drafts.

    Follows the same publishing pattern as the auto_listing_creator
    publish_listings_tool, adapted for audio products.
    """

    def execute(self, **kwargs) -> dict:
        packaged_products = kwargs.get("packaged_products", [])
        credentials_file = kwargs.get("credentials_file", "")
        spreadsheet_id = kwargs.get("spreadsheet_id", "")
        sheet_name = kwargs.get("sheet_name", "Audio Products")
        api_key = kwargs.get("api_key", "")
        shop_id = kwargs.get("shop_id", "")
        token_file = kwargs.get("token_file", "")
        create_drafts = kwargs.get("create_drafts", False)
        taxonomy_id = kwargs.get("taxonomy_id", 1874)
        currency = kwargs.get("currency", "GBP")

        if not packaged_products:
            return {
                "success": False,
                "data": None,
                "error": "No products to publish",
                "tool_name": self.get_name(),
                "metadata": {},
            }

        try:
            queue_rows = 0
            drafts_created = 0
            draft_errors = 0

            # Phase A: Save to Google Sheets
            if credentials_file and spreadsheet_id:
                try:
                    queue_rows = self._save_to_sheets(
                        packaged_products, credentials_file,
                        spreadsheet_id, sheet_name,
                    )
                    print(f"     Saved {queue_rows} audio products to Sheets", flush=True)
                except Exception as e:
                    print(f"     Sheets save failed: {e}", flush=True)

            # Phase B: Create Etsy drafts (if OAuth tokens available)
            if create_drafts and os.path.exists(token_file or ""):
                for product in packaged_products:
                    try:
                        draft_id = self._create_etsy_draft(
                            product, api_key, shop_id, token_file,
                            taxonomy_id, currency,
                        )
                        if draft_id:
                            drafts_created += 1
                            # Upload audio file if available
                            audio_path = product.get("audio_path", "")
                            if audio_path and os.path.exists(audio_path):
                                self._upload_digital_file(
                                    draft_id, audio_path,
                                    api_key, shop_id, token_file,
                                )
                    except Exception as e:
                        draft_errors += 1
                        print(f"     Draft creation failed: {e}", flush=True)

            return {
                "success": True,
                "data": {
                    "queue_rows": queue_rows,
                    "drafts_created": drafts_created,
                    "draft_errors": draft_errors,
                    "total_products": len(packaged_products),
                },
                "error": None,
                "tool_name": self.get_name(),
                "metadata": {
                    "queue_rows": queue_rows,
                    "drafts_created": drafts_created,
                    "draft_errors": draft_errors,
                },
            }

        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": str(e),
                "tool_name": self.get_name(),
                "metadata": {"exception_type": type(e).__name__},
            }

    def _save_to_sheets(self, products, credentials_file, spreadsheet_id, sheet_name):
        """Save audio product listings to Google Sheets."""
        try:
            import gspread
            from google.oauth2.service_account import Credentials

            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ]
            creds = Credentials.from_service_account_file(credentials_file, scopes=scopes)
            gc = gspread.authorize(creds)
            sh = gc.open_by_key(spreadsheet_id)

            try:
                ws = sh.worksheet(sheet_name)
            except gspread.WorksheetNotFound:
                ws = sh.add_worksheet(title=sheet_name, rows=100, cols=10)
                ws.append_row([
                    "Title", "Description", "Tags", "Price",
                    "Product Type", "Niche", "Audio Path", "Status",
                ])

            rows_added = 0
            for product in products:
                ws.append_row([
                    product.get("title", ""),
                    product.get("description", "")[:500],
                    ", ".join(product.get("tags", [])),
                    product.get("price", 0),
                    product.get("product_type", "audio_guide"),
                    product.get("niche", ""),
                    product.get("audio_path", ""),
                    "pending",
                ])
                rows_added += 1

            return rows_added
        except ImportError:
            print("     gspread not installed, skipping Sheets save", flush=True)
            return 0

    def _create_etsy_draft(self, product, api_key, shop_id, token_file,
                           taxonomy_id, currency):
        """Create an Etsy draft listing for an audio product."""
        # Read OAuth tokens
        with open(token_file, "r") as f:
            tokens = json.load(f)

        access_token = tokens.get("access_token", "")
        if not access_token:
            return None

        import urllib.request
        import urllib.error

        payload = json.dumps({
            "title": product.get("title", ""),
            "description": product.get("description", ""),
            "price": {"amount": int(product.get("price", 3.99) * 100), "divisor": 100, "currency_code": currency},
            "taxonomy_id": taxonomy_id,
            "who_made": "i_did",
            "when_made": "2020_2025",
            "is_digital": True,
            "is_supply": False,
            "tags": product.get("tags", [])[:13],
            "quantity": 999,
            "type": "download",
        }).encode("utf-8")

        url = f"https://openapi.etsy.com/v3/application/shops/{shop_id}/listings"
        req = urllib.request.Request(url, data=payload, method="POST")
        req.add_header("Authorization", f"Bearer {access_token}")
        req.add_header("x-api-key", api_key.split(":")[0] if ":" in api_key else api_key)
        req.add_header("Content-Type", "application/json")

        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        return data.get("listing_id")

    def _upload_digital_file(self, listing_id, file_path, api_key, shop_id, token_file):
        """Upload digital file to an Etsy listing."""
        # Digital file upload requires multipart form data
        # This is a placeholder — full implementation would use
        # the Etsy v3 upload endpoint
        pass
