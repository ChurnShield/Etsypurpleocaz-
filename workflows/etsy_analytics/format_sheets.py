# =============================================================================
# workflows/etsy_analytics/format_sheets.py
#
# Formats the Etsy Analytics Google Sheets with professional styling:
#   - Purple brand colors (matching PurpleOcaz branding)
#   - Bold headers with coloured backgrounds
#   - Conditional formatting (green = good, red = needs attention)
#   - Frozen header rows
#   - Auto-sized column widths
#   - Number formatting (commas, percentages)
#   - Alternating row colours for readability
#
# Run:  python workflows/etsy_analytics/format_sheets.py
# =============================================================================

import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(_here))
sys.path.insert(0, _here)
sys.path.insert(1, _project_root)

from config import (
    GOOGLE_CREDENTIALS_FILE,
    GOOGLE_SPREADSHEET_ID,
    ETSY_SNAPSHOT_SHEET_NAME,
    ETSY_LISTINGS_SHEET_NAME,
    ETSY_TOP_PERFORMERS_SHEET,
)

import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# -- PurpleOcaz brand colours --
PURPLE_DARK    = {"red": 0.42, "green": 0.13, "blue": 0.55}   # #6B2189
PURPLE_LIGHT   = {"red": 0.91, "green": 0.82, "blue": 0.96}   # #E8D1F5
PURPLE_MID     = {"red": 0.72, "green": 0.53, "blue": 0.82}   # #B787D1
WHITE          = {"red": 1.0,  "green": 1.0,  "blue": 1.0}
BLACK          = {"red": 0.0,  "green": 0.0,  "blue": 0.0}
LIGHT_GREY     = {"red": 0.95, "green": 0.95, "blue": 0.95}   # #F2F2F2
GREEN_LIGHT    = {"red": 0.85, "green": 0.95, "blue": 0.85}   # #D9F2D9
RED_LIGHT      = {"red": 0.98, "green": 0.85, "blue": 0.85}   # #FAD9D9
GOLD           = {"red": 1.0,  "green": 0.84, "blue": 0.0}    # #FFD700
DARK_GREY      = {"red": 0.2,  "green": 0.2,  "blue": 0.2}


def get_spreadsheet():
    creds = Credentials.from_service_account_file(GOOGLE_CREDENTIALS_FILE, scopes=SCOPES)
    gc = gspread.authorize(creds)
    return gc.open_by_key(GOOGLE_SPREADSHEET_ID)


def batch_format(spreadsheet, sheet_id, requests):
    """Send batch update requests to the Sheets API."""
    if not requests:
        return
    spreadsheet.batch_update({"requests": requests})


def make_header_format(sheet_id, row_count=1, col_count=20):
    """Format header row(s) with purple background and white bold text."""
    return [
        # Header background colour
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": row_count,
                    "startColumnIndex": 0,
                    "endColumnIndex": col_count,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": PURPLE_DARK,
                        "textFormat": {
                            "foregroundColor": WHITE,
                            "bold": True,
                            "fontSize": 11,
                        },
                        "horizontalAlignment": "CENTER",
                        "verticalAlignment": "MIDDLE",
                        "padding": {"top": 6, "bottom": 6, "left": 8, "right": 8},
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment,padding)",
            }
        },
        # Freeze header row
        {
            "updateSheetProperties": {
                "properties": {
                    "sheetId": sheet_id,
                    "gridProperties": {"frozenRowCount": row_count},
                },
                "fields": "gridProperties.frozenRowCount",
            }
        },
    ]


def make_alternating_rows(spreadsheet, sheet_id, col_count=20):
    """Add alternating row colours for readability (removes existing banding first)."""
    # Check for existing banded ranges and remove them
    remove_requests = []
    sheet_meta = spreadsheet.fetch_sheet_metadata()
    for sheet in sheet_meta.get("sheets", []):
        if sheet["properties"]["sheetId"] == sheet_id:
            for br in sheet.get("bandedRanges", []):
                remove_requests.append({
                    "deleteBanding": {"bandedRangeId": br["bandedRangeId"]}
                })
            break

    add_request = {
        "addBanding": {
            "bandedRange": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": col_count,
                },
                "rowProperties": {
                    "headerColor": PURPLE_DARK,
                    "firstBandColor": WHITE,
                    "secondBandColor": PURPLE_LIGHT,
                },
            },
        }
    }

    return remove_requests + [add_request]


def make_column_widths(sheet_id, widths):
    """Set specific column widths. widths = [(col_index, pixel_width), ...]"""
    reqs = []
    for col_idx, px in widths:
        reqs.append({
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": col_idx,
                    "endIndex": col_idx + 1,
                },
                "properties": {"pixelSize": px},
                "fields": "pixelSize",
            }
        })
    return reqs


def make_number_format(sheet_id, col_idx, row_start, row_end, pattern):
    """Apply number format to a column range."""
    return {
        "repeatCell": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": row_start,
                "endRowIndex": row_end,
                "startColumnIndex": col_idx,
                "endColumnIndex": col_idx + 1,
            },
            "cell": {
                "userEnteredFormat": {
                    "numberFormat": {"type": "NUMBER", "pattern": pattern}
                }
            },
            "fields": "userEnteredFormat.numberFormat",
        }
    }


def make_conditional_format_gradient(sheet_id, col_idx, row_start, row_end):
    """Green gradient for high values (views, favs)."""
    return {
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [{
                    "sheetId": sheet_id,
                    "startRowIndex": row_start,
                    "endRowIndex": row_end,
                    "startColumnIndex": col_idx,
                    "endColumnIndex": col_idx + 1,
                }],
                "gradientRule": {
                    "minpoint": {
                        "color": WHITE,
                        "type": "MIN",
                    },
                    "midpoint": {
                        "color": GREEN_LIGHT,
                        "type": "PERCENTILE",
                        "value": "50",
                    },
                    "maxpoint": {
                        "color": {"red": 0.2, "green": 0.66, "blue": 0.33},
                        "type": "MAX",
                    },
                },
            },
            "index": 0,
        }
    }


def make_conditional_red_below(sheet_id, col_idx, row_start, row_end, threshold):
    """Red highlight for values below a threshold."""
    return {
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [{
                    "sheetId": sheet_id,
                    "startRowIndex": row_start,
                    "endRowIndex": row_end,
                    "startColumnIndex": col_idx,
                    "endColumnIndex": col_idx + 1,
                }],
                "booleanRule": {
                    "condition": {
                        "type": "NUMBER_LESS",
                        "values": [{"userEnteredValue": str(threshold)}],
                    },
                    "format": {
                        "backgroundColor": RED_LIGHT,
                        "textFormat": {"foregroundColor": {"red": 0.7, "green": 0.0, "blue": 0.0}},
                    },
                },
            },
            "index": 0,
        }
    }


def format_snapshot_sheet(spreadsheet):
    """Format the Daily Snapshot sheet."""
    print("  Formatting: Etsy Daily Snapshot...")
    try:
        ws = spreadsheet.worksheet(ETSY_SNAPSHOT_SHEET_NAME)
    except gspread.exceptions.WorksheetNotFound:
        print("    Sheet not found, skipping.")
        return

    sheet_id = ws.id
    row_count = ws.row_count
    requests = []

    # Header styling
    requests.extend(make_header_format(sheet_id, row_count=1, col_count=20))

    # Column widths
    requests.extend(make_column_widths(sheet_id, [
        (0, 120),   # Date
        (1, 100),   # Total Sales
        (2, 120),   # Active Listings
        (3, 120),   # Shop Favourites
        (4, 100),   # Review Avg
        (5, 110),   # Review Count
        (6, 110),   # Total Views
        (7, 100),   # Total Favs
        (8, 130),   # Avg Views/Listing
        (9, 130),   # Avg Favs/Listing
        (10, 100),  # Avg Price
        (11, 110),  # Median Price
        (12, 90),   # Min Price
        (13, 90),   # Max Price
        (14, 140),  # Zero-View Listings
        (15, 130),  # Low-View Listings
        (16, 110),  # Under-Tagged
        (17, 120),  # Tattoo Listings
        (18, 110),  # Tattoo Views
        (19, 100),  # Tattoo Favs
    ]))

    # Number formatting for numeric columns
    for col in [1, 2, 3, 5, 6, 7, 14, 15, 16, 17, 18, 19]:
        requests.append(make_number_format(sheet_id, col, 1, row_count, "#,##0"))

    # Price columns with 2 decimal places
    for col in [10, 11, 12, 13]:
        requests.append(make_number_format(sheet_id, col, 1, row_count, "#,##0.00"))

    # Review avg with 1 decimal
    requests.append(make_number_format(sheet_id, 4, 1, row_count, "0.0"))

    # Green gradient on Total Views and Total Favs
    requests.append(make_conditional_format_gradient(sheet_id, 6, 1, row_count))
    requests.append(make_conditional_format_gradient(sheet_id, 7, 1, row_count))

    # Red highlight for zero-view and under-tagged counts
    requests.append(make_conditional_red_below(sheet_id, 14, 1, row_count, 1))

    batch_format(spreadsheet, sheet_id, requests)
    print("    Done!")


def format_listings_sheet(spreadsheet):
    """Format the Listing Tracker sheet."""
    print("  Formatting: Etsy Listing Tracker...")
    try:
        ws = spreadsheet.worksheet(ETSY_LISTINGS_SHEET_NAME)
    except gspread.exceptions.WorksheetNotFound:
        print("    Sheet not found, skipping.")
        return

    sheet_id = ws.id
    row_count = ws.row_count
    requests = []

    # Header styling
    requests.extend(make_header_format(sheet_id, row_count=1, col_count=10))

    # Column widths: ID, Title, Price, Currency, Views, Favs, Sales, Revenue, Fav Rate, Tags, Tag Count, URL
    requests.extend(make_column_widths(sheet_id, [
        (0, 110),   # Listing ID
        (1, 400),   # Title (wide)
        (2, 80),    # Price
        (3, 80),    # Currency
        (4, 90),    # Views
        (5, 100),   # Favourites
        (6, 80),    # Sales
        (7, 100),   # Revenue
        (8, 100),   # Fav Rate %
        (9, 300),   # Tags
        (10, 90),   # Tag Count
        (11, 350),  # URL
    ]))

    # Number formatting
    requests.append(make_number_format(sheet_id, 2, 1, row_count, "#,##0.00"))  # Price
    requests.append(make_number_format(sheet_id, 4, 1, row_count, "#,##0"))     # Views
    requests.append(make_number_format(sheet_id, 5, 1, row_count, "#,##0"))     # Favs
    requests.append(make_number_format(sheet_id, 6, 1, row_count, "#,##0"))     # Sales
    requests.append(make_number_format(sheet_id, 7, 1, row_count, "#,##0.00"))  # Revenue
    requests.append(make_number_format(sheet_id, 8, 1, row_count, "0.00\"%\""))  # Fav Rate

    # Green gradient on Views column
    requests.append(make_conditional_format_gradient(sheet_id, 4, 1, row_count))
    # Green gradient on Favs column
    requests.append(make_conditional_format_gradient(sheet_id, 5, 1, row_count))
    # Green gradient on Sales column
    requests.append(make_conditional_format_gradient(sheet_id, 6, 1, row_count))
    # Green gradient on Revenue column
    requests.append(make_conditional_format_gradient(sheet_id, 7, 1, row_count))

    # Red highlight: tag count below 13 (missing SEO opportunity)
    requests.append(make_conditional_red_below(sheet_id, 10, 1, row_count, 13))

    # Red highlight: zero views
    requests.append(make_conditional_red_below(sheet_id, 4, 1, row_count, 1))

    # Alternating rows
    requests.extend(make_alternating_rows(spreadsheet, sheet_id, col_count=12))

    batch_format(spreadsheet, sheet_id, requests)
    print("    Done!")


def format_top_performers_sheet(spreadsheet):
    """Format the Top Performers sheet."""
    print("  Formatting: Etsy Top Performers...")
    try:
        ws = spreadsheet.worksheet(ETSY_TOP_PERFORMERS_SHEET)
    except gspread.exceptions.WorksheetNotFound:
        print("    Sheet not found, skipping.")
        return

    sheet_id = ws.id
    row_count = ws.row_count
    requests = []

    # Header styling
    requests.extend(make_header_format(sheet_id, row_count=1, col_count=9))

    # Column widths: Rank, Category, ID, Title, Price, Views, Favs, Sales, Revenue, Fav Rate, URL
    requests.extend(make_column_widths(sheet_id, [
        (0, 60),    # Rank
        (1, 130),   # Category
        (2, 110),   # Listing ID
        (3, 380),   # Title
        (4, 80),    # Price
        (5, 90),    # Views
        (6, 100),   # Favourites
        (7, 80),    # Sales
        (8, 100),   # Revenue
        (9, 100),   # Fav Rate %
        (10, 350),  # URL
    ]))

    # Number formatting
    requests.append(make_number_format(sheet_id, 4, 1, row_count, "#,##0.00"))  # Price
    requests.append(make_number_format(sheet_id, 5, 1, row_count, "#,##0"))     # Views
    requests.append(make_number_format(sheet_id, 6, 1, row_count, "#,##0"))     # Favs
    requests.append(make_number_format(sheet_id, 7, 1, row_count, "#,##0"))     # Sales
    requests.append(make_number_format(sheet_id, 8, 1, row_count, "#,##0.00"))  # Revenue
    requests.append(make_number_format(sheet_id, 9, 1, row_count, "0.00\"%\""))  # Fav Rate

    # Green gradient on Views
    requests.append(make_conditional_format_gradient(sheet_id, 5, 1, row_count))
    # Green gradient on Favs
    requests.append(make_conditional_format_gradient(sheet_id, 6, 1, row_count))
    # Green gradient on Sales
    requests.append(make_conditional_format_gradient(sheet_id, 7, 1, row_count))
    # Green gradient on Revenue
    requests.append(make_conditional_format_gradient(sheet_id, 8, 1, row_count))

    # Category column — colour-code by type
    # "Top Views" rows get a subtle gold tint
    requests.append({
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [{
                    "sheetId": sheet_id,
                    "startRowIndex": 1,
                    "endRowIndex": row_count,
                    "startColumnIndex": 0,
                    "endColumnIndex": 11,
                }],
                "booleanRule": {
                    "condition": {
                        "type": "CUSTOM_FORMULA",
                        "values": [{"userEnteredValue": "=$B2=\"Top Views\""}],
                    },
                    "format": {
                        "backgroundColor": {"red": 1.0, "green": 0.97, "blue": 0.88},
                    },
                },
            },
            "index": 0,
        }
    })

    # "Top Favs" rows get light purple
    requests.append({
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [{
                    "sheetId": sheet_id,
                    "startRowIndex": 1,
                    "endRowIndex": row_count,
                    "startColumnIndex": 0,
                    "endColumnIndex": 11,
                }],
                "booleanRule": {
                    "condition": {
                        "type": "CUSTOM_FORMULA",
                        "values": [{"userEnteredValue": "=$B2=\"Top Favs\""}],
                    },
                    "format": {
                        "backgroundColor": PURPLE_LIGHT,
                    },
                },
            },
            "index": 1,
        }
    })

    # "Top Engagement" rows get light green
    requests.append({
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [{
                    "sheetId": sheet_id,
                    "startRowIndex": 1,
                    "endRowIndex": row_count,
                    "startColumnIndex": 0,
                    "endColumnIndex": 11,
                }],
                "booleanRule": {
                    "condition": {
                        "type": "CUSTOM_FORMULA",
                        "values": [{"userEnteredValue": "=$B2=\"Top Engagement\""}],
                    },
                    "format": {
                        "backgroundColor": GREEN_LIGHT,
                    },
                },
            },
            "index": 2,
        }
    })

    # "Top Revenue" rows get gold
    requests.append({
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [{
                    "sheetId": sheet_id,
                    "startRowIndex": 1,
                    "endRowIndex": row_count,
                    "startColumnIndex": 0,
                    "endColumnIndex": 11,
                }],
                "booleanRule": {
                    "condition": {
                        "type": "CUSTOM_FORMULA",
                        "values": [{"userEnteredValue": "=$B2=\"Top Revenue\""}],
                    },
                    "format": {
                        "backgroundColor": {"red": 1.0, "green": 0.93, "blue": 0.75},
                    },
                },
            },
            "index": 3,
        }
    })

    # "Top Sales" rows get light blue
    requests.append({
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [{
                    "sheetId": sheet_id,
                    "startRowIndex": 1,
                    "endRowIndex": row_count,
                    "startColumnIndex": 0,
                    "endColumnIndex": 11,
                }],
                "booleanRule": {
                    "condition": {
                        "type": "CUSTOM_FORMULA",
                        "values": [{"userEnteredValue": "=$B2=\"Top Sales\""}],
                    },
                    "format": {
                        "backgroundColor": {"red": 0.85, "green": 0.92, "blue": 1.0},
                    },
                },
            },
            "index": 4,
        }
    })

    batch_format(spreadsheet, sheet_id, requests)
    print("    Done!")


def main():
    print("\n=== Formatting Etsy Analytics Sheets ===\n")
    print("  Brand: PurpleOcaz purple theme")
    print()

    spreadsheet = get_spreadsheet()

    format_snapshot_sheet(spreadsheet)
    format_listings_sheet(spreadsheet)
    format_top_performers_sheet(spreadsheet)

    print("\n=== All sheets formatted! ===")
    print("  Open your Google Spreadsheet to see the results.\n")


if __name__ == "__main__":
    main()
