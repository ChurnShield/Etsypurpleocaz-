# =============================================================================
# workflows/ai_news_rss/tools/save_to_google_sheets_tool.py
#
# SaveToGoogleSheetsTool — Phase 3
#
# Appends filtered articles as new rows in a Google Sheet.
# Uses gspread (pip install gspread) with a Service Account JSON key for auth.
#
# HOW AUTHENTICATION WORKS
# ------------------------
# Google requires a "Service Account" — a robot Google account your script
# logs in as.  You download a JSON key file for it and share your Sheet
# with the service account's email address (just like sharing with a person).
#
# ONE-TIME SETUP (do this before running the workflow):
# ──────────────────────────────────────────────────────
# 1. Go to https://console.cloud.google.com
# 2. Create a project (or pick an existing one)
# 3. Search for "Google Sheets API" → Enable it
# 4. Also enable "Google Drive API"
# 5. Go to "IAM & Admin" → "Service Accounts" → "Create Service Account"
# 6. Give it any name (e.g. "ai-news-writer"), click Done
# 7. Click the service account → "Keys" tab → "Add Key" → JSON
#    → a .json file downloads (this is your credentials file)
# 8. Move that file to your project root, rename it google-credentials.json
# 9. Open your Google Sheet → Share → paste the service account email
#    (looks like ai-news-writer@your-project.iam.gserviceaccount.com)
#    → give it "Editor" access
# 10. Copy the spreadsheet ID from the URL:
#    https://docs.google.com/spreadsheets/d/THIS_IS_THE_ID/edit
#
# Required columns (Row 1 headers in your Sheet):
# ──────────────────────────────────────────────────────
#   A: Title  |  B: URL  |  C: Publication Date  |  D: Description  |  E: Source
#
# The tool creates these headers automatically if the sheet is empty.
# =============================================================================

import sys
import os

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_here = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(_here)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_tool import BaseTool

# gspread and its auth dependency (google-auth) are installed together.
# If this import fails: pip install gspread
try:
    import gspread
    from google.oauth2.service_account import Credentials
    _GSPREAD_AVAILABLE = True
except ImportError:
    _GSPREAD_AVAILABLE = False


# Column headers — must match what's in row 1 of your Google Sheet.
SHEET_HEADERS = ["Title", "URL", "Publication Date", "Description", "Source"]

# Scopes tell Google what this service account is allowed to do.
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


class SaveToGoogleSheetsTool(BaseTool):
    """
    Appends article rows to a Google Sheet using a Service Account.

    Each article becomes one new row.  The tool:
      1. Opens the spreadsheet by its ID.
      2. Gets (or creates) the named worksheet.
      3. Adds the header row if the sheet is empty.
      4. Reads existing URLs from column B to avoid saving duplicates.
      5. Appends only new articles in a single API call (efficient).
    """

    def execute(self, **kwargs) -> dict:
        """
        Parameters
        ----------
        articles         : list   Filtered article dicts from FilterRecentTool.
        credentials_file : str    Path to the service account JSON key file.
        spreadsheet_id   : str    The ID from the Google Sheets URL.
        sheet_name       : str    Name of the worksheet tab (e.g. "AI News").

        Returns
        -------
        Standard tool dict.
        """
        articles         = kwargs.get("articles",         [])
        credentials_file = kwargs.get("credentials_file", "")
        spreadsheet_id   = kwargs.get("spreadsheet_id",   "")
        sheet_name       = kwargs.get("sheet_name",       "AI News")

        try:
            # ── Dependency check ──────────────────────────────────────────────
            if not _GSPREAD_AVAILABLE:
                raise ImportError(
                    "gspread is not installed. Run:  pip install gspread"
                )

            # ── Credential checks before hitting the API ──────────────────────
            if not credentials_file:
                raise ValueError(
                    "GOOGLE_CREDENTIALS_FILE is not set. "
                    "Add it to your .env file:  "
                    "GOOGLE_CREDENTIALS_FILE=google-credentials.json"
                )
            if not os.path.exists(credentials_file):
                raise FileNotFoundError(
                    f"Credentials file not found: '{credentials_file}'\n"
                    "Download it from Google Cloud Console → Service Accounts "
                    "→ Keys → Add Key → JSON."
                )
            if not spreadsheet_id:
                raise ValueError(
                    "GOOGLE_SPREADSHEET_ID is not set. "
                    "Add it to your .env file:  GOOGLE_SPREADSHEET_ID=your_sheet_id\n"
                    "The ID is in the URL: "
                    "docs.google.com/spreadsheets/d/THIS_PART_HERE/edit"
                )

            # ── Nothing to save ───────────────────────────────────────────────
            if not articles:
                return {
                    "success": True,
                    "data": {"saved_count": 0, "total_input": 0},
                    "error": None,
                    "tool_name": self.get_name(),
                    "metadata": {"note": "No articles to save"},
                }

            # ── Authenticate ──────────────────────────────────────────────────
            # Credentials.from_service_account_file reads the JSON key and
            # creates a credential object that gspread uses for all API calls.
            creds  = Credentials.from_service_account_file(
                credentials_file, scopes=SCOPES
            )
            client = gspread.authorize(creds)

            # ── Open the spreadsheet ──────────────────────────────────────────
            spreadsheet = client.open_by_key(spreadsheet_id)

            # ── Get or create the worksheet ───────────────────────────────────
            try:
                sheet = spreadsheet.worksheet(sheet_name)
            except gspread.exceptions.WorksheetNotFound:
                # The tab doesn't exist yet — create it automatically.
                sheet = spreadsheet.add_worksheet(
                    title=sheet_name, rows=5000, cols=10
                )
                # New sheet: add the header row right away.
                sheet.append_row(SHEET_HEADERS)

            # ── Add headers if the sheet is completely empty ───────────────────
            # (handles the case where the sheet existed but was cleared)
            first_row = sheet.row_values(1)
            if not first_row:
                sheet.append_row(SHEET_HEADERS)

            # ── Read existing URLs to avoid duplicates ────────────────────────
            # col_values(2) returns every value in column B (the URL column).
            # We skip the header row and build a set for O(1) lookup.
            existing_urls = set(sheet.col_values(2)[1:])  # [1:] skips header

            # ── Filter out articles already in the sheet ──────────────────────
            new_articles      = [a for a in articles
                                  if a.get("url", "") not in existing_urls]
            skipped_count     = len(articles) - len(new_articles)

            if not new_articles:
                return {
                    "success": True,
                    "data": {"saved_count": 0, "total_input": 0},
                    "error": None,
                    "tool_name": self.get_name(),
                    "metadata": {
                        "note":             "All articles already in sheet — nothing new to save.",
                        "skipped_duplicates": skipped_count,
                        "spreadsheet_id":   spreadsheet_id,
                        "sheet_name":       sheet_name,
                    },
                }

            # ── Build data rows ───────────────────────────────────────────────
            rows = [
                [
                    article.get("title",       ""),
                    article.get("url",         ""),
                    # Use the cleaner ISO date if the filter tool produced one.
                    article.get("pub_date_iso") or article.get("pub_date", ""),
                    article.get("description", ""),
                    article.get("source",      ""),
                ]
                for article in new_articles
            ]

            # ── Append only new rows in one API call ──────────────────────────
            # append_rows is more efficient than calling append_row in a loop.
            sheet.append_rows(rows, value_input_option="USER_ENTERED")

            return {
                "success": True,
                "data": {
                    # total_input = new articles only; validator compares this
                    # to saved_count.  Duplicates are excluded from both counts
                    # so the validator still passes when all new rows saved.
                    "saved_count": len(rows),
                    "total_input": len(new_articles),
                },
                "error": None,
                "tool_name": self.get_name(),
                "metadata": {
                    "saved_count":        len(rows),
                    "skipped_duplicates": skipped_count,
                    "spreadsheet_id":     spreadsheet_id,
                    "sheet_name":         sheet_name,
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
