# =============================================================================
# workflows/etsy_seo_optimizer/tools/save_seo_report_tool.py
#
# Phase 3: Saves the SEO analysis and new tags to Google Sheets.
#
# Two sheets:
#   1. "SEO Overview" — shop-wide tag health summary
#   2. "SEO Tag Fixes" — per-listing old tags vs new tags with reasoning
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

OVERVIEW_HEADERS = [
    "Metric", "Value",
]

FIXES_HEADERS = [
    "Listing ID", "Title", "SEO Score", "Views", "Favs",
    "Current Tags", "New Tags", "Reasoning", "URL",
]


class SaveSeoReportTool(BaseTool):
    """Save SEO tag analysis and recommendations to Google Sheets."""

    def execute(self, **kwargs) -> dict:
        credentials_file  = kwargs.get("credentials_file", "")
        spreadsheet_id    = kwargs.get("spreadsheet_id", "")
        overview_sheet    = kwargs.get("overview_sheet_name", "SEO Overview")
        fixes_sheet       = kwargs.get("fixes_sheet_name", "SEO Tag Fixes")
        optimized         = kwargs.get("optimized_listings", [])
        overview_data     = kwargs.get("overview", {})
        overused_summary  = kwargs.get("overused_summary", [])
        stats             = kwargs.get("stats", {})

        if not _GSPREAD_AVAILABLE:
            return {
                "success": False, "data": None,
                "error": "gspread not installed",
                "tool_name": self.get_name(), "metadata": {},
            }

        if not os.path.exists(credentials_file):
            return {
                "success": False, "data": None,
                "error": f"Credentials not found: {credentials_file}",
                "tool_name": self.get_name(), "metadata": {},
            }

        try:
            creds = Credentials.from_service_account_file(credentials_file, scopes=SCOPES)
            gc = gspread.authorize(creds)
            spreadsheet = gc.open_by_key(spreadsheet_id)

            # ==== Sheet 1: SEO Overview ====
            ov_ws = self._ensure_sheet(spreadsheet, overview_sheet, OVERVIEW_HEADERS)
            if ov_ws.row_count > 1:
                ov_ws.batch_clear([f"A2:Z{ov_ws.row_count}"])

            overview_rows = [
                ["Total Listings",         overview_data.get("total_listings", 0)],
                ["Average SEO Score",      overview_data.get("avg_seo_score", 0)],
                ["Under-Tagged (<13)",     overview_data.get("under_tagged", 0)],
                ["Heavily Overused Tags",  overview_data.get("heavily_overused", 0)],
                ["Tattoo Niche Listings",  overview_data.get("niche_count", 0)],
                ["Unique Tags in Shop",    overview_data.get("unique_tags_total", 0)],
                ["Overused Tags (50+)",    overview_data.get("overused_tag_count", 0)],
                ["", ""],
                ["Listings Processed",     stats.get("total_processed", 0)],
                ["Tags Generated",         stats.get("tags_generated", 0)],
                ["Failed",                 stats.get("failed", 0)],
                ["", ""],
                ["--- TOP OVERUSED TAGS ---", "--- COUNT ---"],
            ]
            for tag, count in overused_summary[:30]:
                overview_rows.append([tag, count])

            ov_ws.append_rows(overview_rows, value_input_option="USER_ENTERED")

            # ==== Sheet 2: SEO Tag Fixes ====
            fx_ws = self._ensure_sheet(spreadsheet, fixes_sheet, FIXES_HEADERS)
            if fx_ws.row_count > 1:
                fx_ws.batch_clear([f"A2:Z{fx_ws.row_count}"])

            fix_rows = []
            for item in optimized:
                new_tags = item.get("new_tags", [])
                if not new_tags:
                    continue  # Skip listings where generation failed
                fix_rows.append([
                    item.get("listing_id", ""),
                    item.get("title", "")[:80],
                    item.get("seo_score", 0),
                    item.get("views", 0),
                    item.get("num_favorers", 0),
                    ", ".join(item.get("current_tags", [])),
                    ", ".join(new_tags),
                    item.get("reasoning", ""),
                    item.get("url", ""),
                ])

            if fix_rows:
                fx_ws.append_rows(fix_rows, value_input_option="USER_ENTERED")

            return {
                "success": True,
                "data": {
                    "overview_rows": len(overview_rows),
                    "fix_rows":      len(fix_rows),
                },
                "error": None,
                "tool_name": self.get_name(),
                "metadata": {
                    "overview_sheet": overview_sheet,
                    "fixes_sheet":    fixes_sheet,
                    "fix_rows":       len(fix_rows),
                },
            }

        except Exception as e:
            return {
                "success": False, "data": None,
                "error": str(e),
                "tool_name": self.get_name(),
                "metadata": {"exception_type": type(e).__name__},
            }

    def _ensure_sheet(self, spreadsheet, name, headers):
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
            ws.update(range_name="A1", values=[headers], value_input_option="USER_ENTERED")
        return ws
