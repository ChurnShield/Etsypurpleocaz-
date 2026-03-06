# =============================================================================
# workflows/etsy_analytics/tools/save_analytics_tool.py
#
# Phase 3: Saves analytics data to Google Sheets.
#
# Three sheets are written:
#   1. "Etsy Daily Snapshot"   — one row per day with shop-level totals
#   2. "Etsy Listing Tracker"  — all listings with current stats (overwritten)
#   3. "Etsy Top Performers"   — top 20 by views, favs, and engagement
#
# Requires: pip install gspread
# Setup: same Google Service Account as the ai_news_rss workflow.
# =============================================================================

import os
import sys

_here = os.path.dirname(os.path.abspath(__file__))
_workflow = os.path.dirname(_here)
_project_root = os.path.dirname(os.path.dirname(_workflow))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_tool import BaseTool

try:
    import gspread
    from google.oauth2.service_account import Credentials
    _GSPREAD_AVAILABLE = True
except ImportError:
    _GSPREAD_AVAILABLE = False

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SNAPSHOT_HEADERS = [
    "Date", "Total Sales", "Active Listings", "Shop Favourites",
    "Review Avg", "Review Count", "Total Views", "Total Favs",
    "Avg Views/Listing", "Avg Favs/Listing", "Avg Price", "Median Price",
    "Min Price", "Max Price", "Zero-View Listings", "Low-View Listings",
    "Under-Tagged", "Tattoo Listings", "Tattoo Views", "Tattoo Favs",
    "Total Item Sales", "Total Revenue", "Tattoo Sales", "Tattoo Revenue",
]

LISTING_HEADERS = [
    "Listing ID", "Title", "Price", "Currency", "Views", "Favourites",
    "Sales", "Revenue", "Fav Rate %", "Tags", "Tag Count", "URL",
]

TOP_PERF_HEADERS = [
    "Rank", "Category", "Listing ID", "Title", "Price", "Views",
    "Favourites", "Sales", "Revenue", "Fav Rate %", "URL",
]


class SaveAnalyticsTool(BaseTool):
    """Save Etsy analytics to Google Sheets (3 tabs)."""

    def execute(self, **kwargs) -> dict:
        credentials_file = kwargs.get("credentials_file", "")
        spreadsheet_id   = kwargs.get("spreadsheet_id", "")
        snapshot_sheet   = kwargs.get("snapshot_sheet_name", "Etsy Daily Snapshot")
        listings_sheet   = kwargs.get("listings_sheet_name", "Etsy Listing Tracker")
        top_perf_sheet   = kwargs.get("top_perf_sheet_name", "Etsy Top Performers")
        snapshot         = kwargs.get("snapshot", {})
        listings         = kwargs.get("listings", [])
        top_by_views     = kwargs.get("top_by_views", [])
        top_by_favs      = kwargs.get("top_by_favs", [])
        top_by_revenue   = kwargs.get("top_by_revenue", [])
        top_by_sales     = kwargs.get("top_by_sales", [])
        top_engagement   = kwargs.get("top_engagement", [])

        if not _GSPREAD_AVAILABLE:
            return {
                "success": False, "data": None,
                "error": "gspread not installed. Run: pip install gspread",
                "tool_name": self.get_name(), "metadata": {},
            }

        if not os.path.exists(credentials_file):
            return {
                "success": False, "data": None,
                "error": f"Credentials file not found: {credentials_file}",
                "tool_name": self.get_name(), "metadata": {},
            }

        if not spreadsheet_id:
            return {
                "success": False, "data": None,
                "error": "spreadsheet_id is required",
                "tool_name": self.get_name(), "metadata": {},
            }

        try:
            creds = Credentials.from_service_account_file(credentials_file, scopes=SCOPES)
            gc = gspread.authorize(creds)
            spreadsheet = gc.open_by_key(spreadsheet_id)

            # ==== Sheet 1: Daily Snapshot (append one row per day) ====
            snap_ws = self._ensure_sheet(spreadsheet, snapshot_sheet, SNAPSHOT_HEADERS)

            # Check if today's snapshot already exists (prevent duplicates)
            today = snapshot.get("date", "")
            existing_dates = snap_ws.col_values(1)[1:]  # skip header
            if today not in existing_dates:
                snap_row = [
                    snapshot.get("date", ""),
                    snapshot.get("total_sales", 0),
                    snapshot.get("active_listings", 0),
                    snapshot.get("shop_favorers", 0),
                    snapshot.get("review_average", 0),
                    snapshot.get("review_count", 0),
                    snapshot.get("total_views", 0),
                    snapshot.get("total_favs", 0),
                    snapshot.get("avg_views", 0),
                    snapshot.get("avg_favs", 0),
                    snapshot.get("avg_price", 0),
                    snapshot.get("median_price", 0),
                    snapshot.get("min_price", 0),
                    snapshot.get("max_price", 0),
                    snapshot.get("zero_view_count", 0),
                    snapshot.get("low_view_count", 0),
                    snapshot.get("under_tagged", 0),
                    snapshot.get("tattoo_listings", 0),
                    snapshot.get("tattoo_views", 0),
                    snapshot.get("tattoo_favs", 0),
                    snapshot.get("total_item_sales", 0),
                    snapshot.get("total_revenue", 0),
                    snapshot.get("tattoo_sales", 0),
                    snapshot.get("tattoo_revenue", 0),
                ]
                snap_ws.append_row(snap_row, value_input_option="USER_ENTERED")
                snapshot_added = True
            else:
                snapshot_added = False

            # ==== Sheet 2: Listing Tracker (full refresh each run) ====
            list_ws = self._ensure_sheet(spreadsheet, listings_sheet, LISTING_HEADERS)

            # Clear old data (keep header) and write fresh
            if list_ws.row_count > 1:
                list_ws.batch_clear([f"A2:Z{list_ws.row_count}"])

            listing_rows = []
            for l in listings:
                listing_rows.append([
                    l.get("listing_id", ""),
                    l.get("title", ""),
                    l.get("price", 0),
                    l.get("currency", ""),
                    l.get("views", 0),
                    l.get("num_favorers", 0),
                    l.get("sales", 0),
                    round(l.get("revenue", 0), 2),
                    round(l.get("fav_rate", 0), 2),
                    ", ".join(l.get("tags", [])[:5]),
                    l.get("tag_count", 0),
                    l.get("url", ""),
                ])

            if listing_rows:
                list_ws.append_rows(listing_rows, value_input_option="USER_ENTERED")

            # ==== Sheet 3: Top Performers (full refresh each run) ====
            top_ws = self._ensure_sheet(spreadsheet, top_perf_sheet, TOP_PERF_HEADERS)

            if top_ws.row_count > 1:
                top_ws.batch_clear([f"A2:Z{top_ws.row_count}"])

            top_rows = []

            # Top 20 by views
            for i, l in enumerate(top_by_views[:20], 1):
                top_rows.append([
                    i, "Top Views", l.get("listing_id", ""),
                    l.get("title", "")[:80], l.get("price", 0),
                    l.get("views", 0), l.get("num_favorers", 0),
                    l.get("sales", 0), round(l.get("revenue", 0), 2),
                    round(l.get("fav_rate", 0), 2), l.get("url", ""),
                ])

            # Top 20 by favourites
            for i, l in enumerate(top_by_favs[:20], 1):
                top_rows.append([
                    i, "Top Favs", l.get("listing_id", ""),
                    l.get("title", "")[:80], l.get("price", 0),
                    l.get("views", 0), l.get("num_favorers", 0),
                    l.get("sales", 0), round(l.get("revenue", 0), 2),
                    round(l.get("fav_rate", 0), 2), l.get("url", ""),
                ])

            # Top 20 by engagement (fav rate)
            for i, l in enumerate(top_engagement[:20], 1):
                top_rows.append([
                    i, "Top Engagement", l.get("listing_id", ""),
                    l.get("title", "")[:80], l.get("price", 0),
                    l.get("views", 0), l.get("num_favorers", 0),
                    l.get("sales", 0), round(l.get("revenue", 0), 2),
                    round(l.get("fav_rate", 0), 2), l.get("url", ""),
                ])

            # Top 20 by revenue (if sales data available)
            for i, l in enumerate(top_by_revenue[:20], 1):
                top_rows.append([
                    i, "Top Revenue", l.get("listing_id", ""),
                    l.get("title", "")[:80], l.get("price", 0),
                    l.get("views", 0), l.get("num_favorers", 0),
                    l.get("sales", 0), round(l.get("revenue", 0), 2),
                    round(l.get("fav_rate", 0), 2), l.get("url", ""),
                ])

            # Top 20 by sales count (if sales data available)
            for i, l in enumerate(top_by_sales[:20], 1):
                top_rows.append([
                    i, "Top Sales", l.get("listing_id", ""),
                    l.get("title", "")[:80], l.get("price", 0),
                    l.get("views", 0), l.get("num_favorers", 0),
                    l.get("sales", 0), round(l.get("revenue", 0), 2),
                    round(l.get("fav_rate", 0), 2), l.get("url", ""),
                ])

            if top_rows:
                top_ws.append_rows(top_rows, value_input_option="USER_ENTERED")

            return {
                "success":   True,
                "data": {
                    "snapshot_added":  snapshot_added,
                    "listings_saved":  len(listing_rows),
                    "top_rows_saved":  len(top_rows),
                },
                "error":     None,
                "tool_name": self.get_name(),
                "metadata": {
                    "spreadsheet_id":   spreadsheet_id,
                    "snapshot_sheet":    snapshot_sheet,
                    "listings_sheet":    listings_sheet,
                    "top_perf_sheet":    top_perf_sheet,
                    "snapshot_added":    snapshot_added,
                    "listings_written":  len(listing_rows),
                    "top_rows_written":  len(top_rows),
                },
            }

        except Exception as e:
            return {
                "success":   False,
                "data":      None,
                "error":     str(e),
                "tool_name": self.get_name(),
                "metadata":  {"exception_type": type(e).__name__},
            }

    # -- Helpers --

    def _ensure_sheet(self, spreadsheet, name, headers):
        """Get or create a worksheet and ensure it has correct headers."""
        try:
            ws = spreadsheet.worksheet(name)
        except gspread.exceptions.WorksheetNotFound:
            ws = spreadsheet.add_worksheet(title=name, rows=5000, cols=len(headers))
            ws.append_row(headers, value_input_option="USER_ENTERED")
            return ws

        first_row = ws.row_values(1)
        if not first_row:
            ws.append_row(headers, value_input_option="USER_ENTERED")
        elif first_row != headers:
            # Headers changed (e.g. new columns added) — update them
            ws.update(range_name="A1", values=[headers], value_input_option="USER_ENTERED")

        return ws
