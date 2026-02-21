# =============================================================================
# workflows/auto_listing_creator/tools/load_opportunities_tool.py
#
# Phase 1: Loads product opportunities from the Tattoo Trend Monitor's
# "Tattoo Opportunities" Google Sheets tab and your existing listings
# so we know what NOT to duplicate.
# =============================================================================

import json
import urllib.request
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


class LoadOpportunitiesTool(BaseTool):
    """Load product opportunities from Tattoo Trend Monitor + existing listings."""

    def execute(self, **kwargs) -> dict:
        credentials_file = kwargs.get("credentials_file", "")
        spreadsheet_id   = kwargs.get("spreadsheet_id", "")
        opps_sheet_name  = kwargs.get("opportunities_sheet_name", "Tattoo Opportunities")
        api_key          = kwargs.get("api_key", "")
        shop_id          = kwargs.get("shop_id", "")
        page_limit       = kwargs.get("page_limit", 100)

        if not _GSPREAD:
            return {
                "success": False, "data": None,
                "error": "gspread not installed",
                "tool_name": self.get_name(), "metadata": {},
            }

        try:
            # -- Load opportunities from Google Sheets --
            print("     [1a] Loading opportunities from Tattoo Trend Monitor...", flush=True)
            creds = Credentials.from_service_account_file(credentials_file, scopes=SCOPES)
            gc = gspread.authorize(creds)
            spreadsheet = gc.open_by_key(spreadsheet_id)

            try:
                ws = spreadsheet.worksheet(opps_sheet_name)
                rows = ws.get_all_records()
            except Exception:
                rows = []

            if not rows:
                return {
                    "success": False, "data": None,
                    "error": f"No opportunities found in '{opps_sheet_name}' tab. Run the Tattoo Trend Monitor first.",
                    "tool_name": self.get_name(), "metadata": {},
                }

            opportunities = []
            for row in rows:
                opportunities.append({
                    "rank": row.get("Rank", 0),
                    "product_title": row.get("Product Title", ""),
                    "why": row.get("Why", ""),
                    "suggested_price": row.get("Suggested Price", 0),
                    "priority": row.get("Priority", ""),
                    "effort": row.get("Effort", ""),
                    "target_keywords": [k.strip() for k in str(row.get("Target Keywords", "")).split(",") if k.strip()],
                })

            print(f"          {len(opportunities)} opportunities loaded", flush=True)

            # -- Load existing titles to avoid duplicates --
            print("     [1b] Loading existing shop listings...", flush=True)
            existing_titles = self._fetch_existing_titles(api_key, shop_id, page_limit)
            print(f"          {len(existing_titles)} existing listings found", flush=True)

            # -- Filter out opportunities that already exist --
            new_opportunities = []
            skipped = 0
            for opp in opportunities:
                opp_title_lower = opp["product_title"].lower()
                # Check if a very similar listing already exists
                already_exists = False
                for existing in existing_titles:
                    existing_lower = existing.lower()
                    # Check word overlap (if >60% words match, consider it a duplicate)
                    opp_words = set(opp_title_lower.split())
                    exist_words = set(existing_lower.split())
                    if len(opp_words) > 0:
                        overlap = len(opp_words & exist_words) / len(opp_words)
                        if overlap > 0.6:
                            already_exists = True
                            break
                if already_exists:
                    skipped += 1
                else:
                    new_opportunities.append(opp)

            print(f"          {len(new_opportunities)} new opportunities ({skipped} already exist)", flush=True)

            return {
                "success": True,
                "data": {
                    "opportunities": new_opportunities,
                    "skipped_duplicates": skipped,
                    "total_loaded": len(opportunities),
                    "existing_listing_count": len(existing_titles),
                },
                "error": None,
                "tool_name": self.get_name(),
                "metadata": {
                    "loaded": len(opportunities),
                    "new": len(new_opportunities),
                    "skipped": skipped,
                },
            }

        except Exception as e:
            return {
                "success": False, "data": None,
                "error": str(e),
                "tool_name": self.get_name(),
                "metadata": {"exception_type": type(e).__name__},
            }

    def _fetch_existing_titles(self, api_key, shop_id, page_limit):
        """Fetch all existing listing titles from the shop."""
        titles = []
        offset = 0

        while True:
            url = (
                f"{ETSY_BASE_URL}/shops/{shop_id}/listings/active"
                f"?limit={page_limit}&offset={offset}"
            )
            req = urllib.request.Request(url)
            req.add_header("x-api-key", api_key)
            req.add_header("Accept", "application/json")

            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            results = data.get("results", [])
            total = data.get("count", 0)

            if not results:
                break

            for l in results:
                titles.append(l.get("title", ""))

            offset += len(results)
            if offset >= total:
                break

            import time
            time.sleep(0.3)

        return titles
