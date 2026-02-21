# =============================================================================
# workflows/tattoo_trend_monitor/tools/save_trends_report_tool.py
#
# Phase 3: Saves trend analysis to Google Sheets (2 tabs):
#   1. "Tattoo Trends"        - keyword trends + gap analysis
#   2. "Tattoo Opportunities" - AI-ranked product ideas
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
    _GSPREAD = True
except ImportError:
    _GSPREAD = False

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

TRENDS_HEADERS = [
    "Keyword", "Trend Score", "Direction", "Growth %",
    "Current Interest", "Avg Interest", "Peak Interest",
    "Opportunity Score", "Gap Status", "Your Listings",
    "Competitor Count", "Avg Competitor Price",
    "Avg Competitor Views",
]

OPPORTUNITIES_HEADERS = [
    "Rank", "Product Title", "Why", "Suggested Price",
    "Priority", "Effort", "Target Keywords",
]


class SaveTrendsReportTool(BaseTool):
    """Save tattoo trend analysis to Google Sheets."""

    def execute(self, **kwargs) -> dict:
        credentials_file  = kwargs.get("credentials_file", "")
        spreadsheet_id    = kwargs.get("spreadsheet_id", "")
        trends_sheet      = kwargs.get("trends_sheet_name", "Tattoo Trends")
        opps_sheet        = kwargs.get("opportunities_sheet_name", "Tattoo Opportunities")
        opportunities     = kwargs.get("opportunities", [])
        ai_opportunities  = kwargs.get("ai_opportunities", [])
        summary           = kwargs.get("summary", {})

        if not _GSPREAD:
            return {
                "success": False, "data": None,
                "error": "gspread not installed",
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
                "error": "spreadsheet_id required",
                "tool_name": self.get_name(), "metadata": {},
            }

        try:
            creds = Credentials.from_service_account_file(credentials_file, scopes=SCOPES)
            gc = gspread.authorize(creds)
            spreadsheet = gc.open_by_key(spreadsheet_id)

            # ==== Tab 1: Tattoo Trends ====
            ws = self._ensure_sheet(spreadsheet, trends_sheet, TRENDS_HEADERS)
            if ws.row_count > 1:
                ws.batch_clear([f"A2:Z{ws.row_count}"])

            trend_rows = []
            for opp in opportunities:
                trend_rows.append([
                    opp.get("keyword", ""),
                    opp.get("trend_score", 0),
                    opp.get("trend_direction", ""),
                    opp.get("growth_pct", 0),
                    opp.get("current_interest", 0),
                    opp.get("avg_interest", 0) if "avg_interest" in opp else "",
                    opp.get("peak_interest", 0) if "peak_interest" in opp else "",
                    opp.get("opportunity_score", 0),
                    opp.get("gap_status", ""),
                    opp.get("you_have_listings", 0),
                    opp.get("competitor_count", 0),
                    opp.get("avg_competitor_price", 0),
                    opp.get("avg_competitor_views", 0),
                ])

            if trend_rows:
                ws.append_rows(trend_rows, value_input_option="USER_ENTERED")

            # ==== Tab 2: Tattoo Opportunities ====
            opp_ws = self._ensure_sheet(spreadsheet, opps_sheet, OPPORTUNITIES_HEADERS)
            if opp_ws.row_count > 1:
                opp_ws.batch_clear([f"A2:Z{opp_ws.row_count}"])

            opp_rows = []
            for item in ai_opportunities:
                opp_rows.append([
                    item.get("rank", ""),
                    item.get("product_title", ""),
                    item.get("why", ""),
                    item.get("suggested_price", ""),
                    item.get("priority", ""),
                    item.get("effort", ""),
                    ", ".join(item.get("target_keywords", [])),
                ])

            if opp_rows:
                opp_ws.append_rows(opp_rows, value_input_option="USER_ENTERED")

            return {
                "success": True,
                "data": {
                    "trends_rows": len(trend_rows),
                    "opportunity_rows": len(opp_rows),
                },
                "error": None,
                "tool_name": self.get_name(),
                "metadata": {
                    "trends_sheet": trends_sheet,
                    "opps_sheet": opps_sheet,
                    "trends_written": len(trend_rows),
                    "opps_written": len(opp_rows),
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
            ws = spreadsheet.add_worksheet(title=name, rows=500, cols=len(headers))
            ws.append_row(headers, value_input_option="USER_ENTERED")
            return ws
        first_row = ws.row_values(1)
        if not first_row:
            ws.append_row(headers, value_input_option="USER_ENTERED")
        elif first_row != headers:
            ws.update(range_name="A1", values=[headers], value_input_option="USER_ENTERED")
        return ws
