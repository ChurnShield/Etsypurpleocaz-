# =============================================================================
# workflows/market_intelligence/tools/save_market_report_tool.py
#
# Phase 4: Writes scored opportunities to the "Market Intelligence" Google
# Sheets tab. Headers are compatible with LoadOpportunitiesTool so the
# auto_listing_creator can consume them directly.
#
# Pattern source: save_trends_report_tool.py
# =============================================================================

import sys
import os

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

# First 7 columns are LoadOpportunitiesTool-compatible
MARKET_INTEL_HEADERS = [
    "Rank",
    "Product Title",
    "Why",
    "Suggested Price",
    "Priority",
    "Effort",
    "Target Keywords",
    "Opportunity Score",
    "Product Type",
    "Competition Level",
    "Urgency",
    "Source Signals",
    "Avg Competitor Price",
    "Total Competitors",
    "Scored At",
]

# Mapping: urgency -> Priority
URGENCY_TO_PRIORITY = {
    "immediate": "HIGH",
    "this_week": "HIGH",
    "this_month": "MEDIUM",
    "backlog": "LOW",
}

# Mapping: competition_assessment -> Effort
COMPETITION_TO_EFFORT = {
    "low": "quick",
    "medium": "moderate",
    "high": "complex",
    "saturated": "complex",
}


class SaveMarketReportTool(BaseTool):
    """Save scored opportunities to Market Intelligence Google Sheets tab."""

    def execute(self, **kwargs) -> dict:
        scored_opportunities = kwargs.get("scored_opportunities", [])
        credentials_file     = kwargs.get("credentials_file", "")
        spreadsheet_id       = kwargs.get("spreadsheet_id", "")
        sheet_name           = kwargs.get("sheet_name", "Market Intelligence")

        if not _GSPREAD:
            return {
                "success": False, "data": None,
                "error": "gspread not installed",
                "tool_name": self.get_name(), "metadata": {},
            }

        if not scored_opportunities:
            return {
                "success": False, "data": None,
                "error": "No scored opportunities to save",
                "tool_name": self.get_name(), "metadata": {},
            }

        try:
            creds = Credentials.from_service_account_file(
                credentials_file, scopes=SCOPES
            )
            gc = gspread.authorize(creds)
            spreadsheet = gc.open_by_key(spreadsheet_id)

            ws = self._ensure_sheet(spreadsheet, sheet_name, MARKET_INTEL_HEADERS)

            # Clear existing data below headers
            if ws.row_count > 1:
                ws.batch_clear([f"A2:Z{ws.row_count}"])

            # Build rows
            rows = []
            for opp in scored_opportunities:
                urgency = opp.get("urgency", "backlog")
                competition = opp.get("competition_assessment", "medium")

                tags = opp.get("recommended_tags", [])
                if isinstance(tags, list):
                    tags_str = ", ".join(tags)
                else:
                    tags_str = str(tags)

                source_signals = opp.get("source_signals", [])
                if isinstance(source_signals, list):
                    signals_str = "; ".join(source_signals)
                else:
                    signals_str = str(source_signals)

                rows.append([
                    opp.get("rank", ""),
                    opp.get("product_suggestion", ""),
                    opp.get("reasoning", ""),
                    opp.get("recommended_price", ""),
                    URGENCY_TO_PRIORITY.get(urgency, "MEDIUM"),
                    COMPETITION_TO_EFFORT.get(competition, "moderate"),
                    tags_str,
                    opp.get("opportunity_score", ""),
                    opp.get("product_type", ""),
                    competition,
                    urgency,
                    signals_str,
                    opp.get("avg_competitor_price", ""),
                    opp.get("total_results", ""),
                    opp.get("scored_at", ""),
                ])

            if rows:
                ws.append_rows(rows, value_input_option="USER_ENTERED")

            print(f"     {len(rows)} opportunities saved to '{sheet_name}'", flush=True)

            return {
                "success": True,
                "data": {
                    "rows_written": len(rows),
                    "sheet_name": sheet_name,
                },
                "error": None,
                "tool_name": self.get_name(),
                "metadata": {"sheet_name": sheet_name, "rows": len(rows)},
            }

        except Exception as e:
            return {
                "success": False, "data": None,
                "error": str(e),
                "tool_name": self.get_name(),
                "metadata": {"exception_type": type(e).__name__},
            }

    def _ensure_sheet(self, spreadsheet, name, headers):
        """Get or create worksheet with correct headers."""
        try:
            ws = spreadsheet.worksheet(name)
        except gspread.exceptions.WorksheetNotFound:
            ws = spreadsheet.add_worksheet(
                title=name, rows=5000, cols=len(headers)
            )
            ws.append_row(headers, value_input_option="USER_ENTERED")
            return ws

        first_row = ws.row_values(1)
        if not first_row:
            ws.append_row(headers, value_input_option="USER_ENTERED")
        elif first_row != headers:
            ws.update(
                range_name="A1", values=[headers],
                value_input_option="USER_ENTERED"
            )
        return ws
