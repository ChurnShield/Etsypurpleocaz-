# =============================================================================
# workflows/etsy_analytics/run_triage.py
#
# Listing Triage: Scores all listings and writes A/B/C tier report
# to the "Listing Triage" tab in Google Sheets.
#
#   python workflows/etsy_analytics/run_triage.py
#
# Pipeline:
#   Phase 1 -> Fetch all listings from Etsy API (+ sales data via OAuth)
#   Phase 2 -> Score & categorise into A/B/C tiers
#   Phase 3 -> Save triage report to Google Sheets
# =============================================================================

import sys
import os
import time

_here = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(_here))
sys.path.insert(0, _here)
sys.path.insert(1, _project_root)

from config import (
    ETSY_API_KEY, ETSY_SHOP_ID, ETSY_PAGE_LIMIT,
    GOOGLE_CREDENTIALS_FILE, GOOGLE_SPREADSHEET_ID,
    FOCUS_NICHE,
)

from tools.fetch_etsy_data_tool    import FetchEtsyDataTool
from tools.triage_listings_tool    import TriageListingsTool

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

TRIAGE_SHEET = "Listing Triage"

TRIAGE_HEADERS = [
    "Tier", "Score", "Listing ID", "Title", "Price", "Currency",
    "Views", "Favourites", "Sales", "Revenue",
    "Tags", "Niche?",
    "Views Pts", "Sales Pts", "Favs Pts", "Engage Pts",
    "Tag Pts", "Age Pts", "Niche Pts",
    "Recommendation", "URL",
]

SUMMARY_SHEET = "Triage Summary"

SUMMARY_HEADERS = [
    "Date", "Total Listings",
    "A-Tier Count", "A-Tier Views", "A-Tier Sales", "A-Tier Revenue", "A-Tier Niche",
    "B-Tier Count", "B-Tier Views", "B-Tier Sales", "B-Tier Revenue", "B-Tier Niche",
    "C-Tier Count", "C-Tier Views", "C-Tier Sales", "C-Tier Revenue", "C-Tier Niche",
    "A Views %", "B Views %", "C Views %",
    "Avg Score", "Focus Niche",
]


def _ensure_sheet(spreadsheet, name, headers):
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


def main():
    print(f"\n{'=' * 60}")
    print(f"  LISTING TRIAGE")
    print(f"  Shop ID   : {ETSY_SHOP_ID}")
    print(f"  Focus     : {FOCUS_NICHE} niche (gets +5 bonus)")
    print(f"{'=' * 60}")

    # -- Preflight checks --
    if not ETSY_API_KEY or ETSY_API_KEY == ":":
        print("\n  ERROR: Etsy API credentials not set in .env")
        return {"success": False}

    if not _GSPREAD:
        print("\n  ERROR: gspread not installed. Run: pip install gspread")
        return {"success": False}

    # ==== Phase 1: Fetch all listings ====
    print(f"\n[1] Fetching all listings from Etsy API...")
    fetch = FetchEtsyDataTool()
    fetch_result = fetch.execute(
        api_key=ETSY_API_KEY,
        shop_id=ETSY_SHOP_ID,
        page_limit=ETSY_PAGE_LIMIT,
    )

    if not fetch_result["success"]:
        print(f"    FAILED: {fetch_result.get('error')}")
        return {"success": False}

    listings = fetch_result["data"]["listings"]
    has_sales = fetch_result["data"]["has_sales_data"]
    print(f"    Fetched {len(listings)} listings")
    print(f"    Sales data: {'YES (OAuth)' if has_sales else 'NO (run etsy_oauth.py)'}")

    # ==== Phase 2: Score & triage ====
    print(f"\n[2] Scoring and triaging all listings...")
    triage = TriageListingsTool()
    triage_result = triage.execute(
        listings=listings,
        focus_niche=FOCUS_NICHE,
    )

    if not triage_result["success"]:
        print(f"    FAILED: {triage_result.get('error')}")
        return {"success": False}

    scored   = triage_result["data"]["scored_listings"]
    summary  = triage_result["data"]["summary"]

    a = summary["a_tier"]
    b = summary["b_tier"]
    c = summary["c_tier"]
    vs = summary["view_share"]

    print(f"\n    === TRIAGE RESULTS ===")
    print(f"    A-tier (KEEP)       : {a['count']:>4} listings  |  {a['views']:>6} views  |  {a['sales']:>4} sales  |  {a['revenue']:>8.2f} revenue")
    print(f"    B-tier (OPTIMIZE)   : {b['count']:>4} listings  |  {b['views']:>6} views  |  {b['sales']:>4} sales  |  {b['revenue']:>8.2f} revenue")
    print(f"    C-tier (DEACTIVATE) : {c['count']:>4} listings  |  {c['views']:>6} views  |  {c['sales']:>4} sales  |  {c['revenue']:>8.2f} revenue")
    print(f"")
    print(f"    View share: A={vs['a_pct']}% | B={vs['b_pct']}% | C={vs['c_pct']}%")
    print(f"    Average score: {summary['avg_score']}/100")
    print(f"    {FOCUS_NICHE.title()} niche: A={a['niche']}, B={b['niche']}, C={c['niche']}")

    # ==== Phase 3: Save to Google Sheets ====
    print(f"\n[3] Saving triage report to Google Sheets...")

    if not os.path.exists(GOOGLE_CREDENTIALS_FILE):
        print(f"    WARNING: {GOOGLE_CREDENTIALS_FILE} not found, skipping Sheets save")
        return {"success": True, "summary": summary}

    if not GOOGLE_SPREADSHEET_ID:
        print(f"    WARNING: No GOOGLE_SPREADSHEET_ID set, skipping Sheets save")
        return {"success": True, "summary": summary}

    try:
        creds = Credentials.from_service_account_file(GOOGLE_CREDENTIALS_FILE, scopes=SCOPES)
        gc = gspread.authorize(creds)
        spreadsheet = gc.open_by_key(GOOGLE_SPREADSHEET_ID)

        # -- Triage detail sheet (full refresh) --
        ws = _ensure_sheet(spreadsheet, TRIAGE_SHEET, TRIAGE_HEADERS)
        if ws.row_count > 1:
            ws.batch_clear([f"A2:Z{ws.row_count}"])

        rows = []
        for s in scored:
            bd = s["breakdown"]
            rows.append([
                s["tier"],
                s["score"],
                s["listing_id"],
                s["title"][:80],
                s["price"],
                s["currency"],
                s["views"],
                s["num_favorers"],
                s["sales"],
                s["revenue"],
                s["tag_count"],
                "Yes" if s["is_niche"] else "",
                bd["views"],
                bd["sales"],
                bd["favs"],
                bd["engagement"],
                bd["tags"],
                bd["age_efficiency"],
                bd["niche_bonus"],
                s["recommendation"],
                s["url"],
            ])

        if rows:
            # Write in chunks to avoid API limits
            chunk_size = 500
            for i in range(0, len(rows), chunk_size):
                chunk = rows[i:i + chunk_size]
                ws.append_rows(chunk, value_input_option="USER_ENTERED")
                if i + chunk_size < len(rows):
                    time.sleep(1)

        print(f"    '{TRIAGE_SHEET}' tab: {len(rows)} listings written")

        # -- Triage summary sheet (append row per run) --
        sum_ws = _ensure_sheet(spreadsheet, SUMMARY_SHEET, SUMMARY_HEADERS)

        # Dedup on date
        today = summary["date"]
        existing = sum_ws.col_values(1)[1:]
        if today not in existing:
            sum_ws.append_row([
                summary["date"],
                summary["total_listings"],
                a["count"], a["views"], a["sales"], a["revenue"], a["niche"],
                b["count"], b["views"], b["sales"], b["revenue"], b["niche"],
                c["count"], c["views"], c["sales"], c["revenue"], c["niche"],
                vs["a_pct"], vs["b_pct"], vs["c_pct"],
                summary["avg_score"],
                summary["focus_niche"],
            ], value_input_option="USER_ENTERED")
            print(f"    '{SUMMARY_SHEET}' tab: summary row added")
        else:
            print(f"    '{SUMMARY_SHEET}' tab: today's row already exists")

        print(f"\n{'=' * 60}")
        print(f"  TRIAGE COMPLETE")
        print(f"  A-tier: {a['count']} (keep)  |  B-tier: {b['count']} (optimize)  |  C-tier: {c['count']} (deactivate)")
        print(f"  Check Google Sheets: '{TRIAGE_SHEET}' and '{SUMMARY_SHEET}' tabs")
        print(f"{'=' * 60}\n")

        return {"success": True, "summary": summary}

    except Exception as e:
        print(f"    Sheets save failed: {e}")
        return {"success": True, "summary": summary}


if __name__ == "__main__":
    main()
