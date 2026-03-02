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
from config import PAGINATION_MAX_PAGES

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
        credentials_file    = kwargs.get("credentials_file", "")
        spreadsheet_id      = kwargs.get("spreadsheet_id", "")
        opps_sheet_name     = kwargs.get("opportunities_sheet_name", "Tattoo Opportunities")
        mi_sheet_name       = kwargs.get("market_intel_sheet_name", "Market Intelligence")
        api_key             = kwargs.get("api_key", "")
        shop_id             = kwargs.get("shop_id", "")
        page_limit          = kwargs.get("page_limit", 100)

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

            # -- Also load from Market Intelligence sheet (if it exists) --
            mi_opportunities = []
            try:
                mi_ws = spreadsheet.worksheet(mi_sheet_name)
                mi_rows = mi_ws.get_all_records()
                for row in mi_rows:
                    mi_opportunities.append({
                        "rank": row.get("Rank", 0),
                        "product_title": row.get("Product Title", ""),
                        "why": row.get("Why", ""),
                        "suggested_price": row.get("Suggested Price", 0),
                        "priority": row.get("Priority", ""),
                        "effort": row.get("Effort", ""),
                        "target_keywords": [
                            k.strip()
                            for k in str(row.get("Target Keywords", "")).split(",")
                            if k.strip()
                        ],
                        "opportunity_score": row.get("Opportunity Score", 0),
                        "source": "market_intelligence",
                    })
                print(f"          {len(mi_opportunities)} opportunities from Market Intelligence", flush=True)
            except Exception:
                print(f"          Market Intelligence sheet not found (skipped)", flush=True)

            # Tag trend monitor opportunities with source
            for opp in opportunities:
                opp["source"] = opp.get("source", "tattoo_trend_monitor")
                opp["opportunity_score"] = opp.get("opportunity_score", opp.get("rank", 50))

            # Merge and cross-source deduplicate
            all_opportunities = opportunities + mi_opportunities
            seen_titles = {}
            merged = []
            for opp in all_opportunities:
                title_lower = opp["product_title"].lower()
                title_words = set(title_lower.split())
                is_dup = False
                for seen_title, seen_idx in seen_titles.items():
                    seen_words = set(seen_title.split())
                    if len(title_words) > 0 and len(seen_words) > 0:
                        overlap = len(title_words & seen_words) / len(title_words)
                        if overlap > 0.6:
                            existing = merged[seen_idx]
                            if float(opp.get("opportunity_score", 0)) > float(existing.get("opportunity_score", 0)):
                                merged[seen_idx] = opp
                            is_dup = True
                            break
                if not is_dup:
                    seen_titles[title_lower] = len(merged)
                    merged.append(opp)

            # Sort by opportunity score
            merged.sort(key=lambda x: float(x.get("opportunity_score", 0)), reverse=True)
            opportunities = merged
            print(f"          {len(opportunities)} merged opportunities (after cross-dedup)", flush=True)

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

        import time

        for _page in range(PAGINATION_MAX_PAGES):
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

            time.sleep(0.3)

        return titles
