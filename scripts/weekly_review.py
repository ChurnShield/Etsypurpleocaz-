#!/usr/bin/env python3
"""
scripts/weekly_review.py — Weekly Review Generator

Reads Google Sheet queue, CHANGELOG, LESSONS, and compares against
the 16-week listing plan. Writes a plain-English summary to a
"WEEKLY_REVIEW" tab in the Google Sheet.

Designed to run every Monday at 7:30am UTC after digest.py.

Usage:
    python scripts/weekly_review.py              # normal run
    python scripts/weekly_review.py --dry-run    # print to terminal only
"""

import argparse
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_script_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_script_dir)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from config import (
    GOOGLE_CREDENTIALS_FILE,
    GOOGLE_SPREADSHEET_ID,
)

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

REVIEW_SHEET_NAME = "WEEKLY_REVIEW"

# 16-week plan: cumulative listing targets per week.
# Week 1 = first week of plan, etc.
# Based on rapid-launch strategy: 20-40 in month 1, then steady growth.
SIXTEEN_WEEK_PLAN = {
    1: 10,   2: 20,   3: 30,   4: 40,
    5: 50,   6: 60,   7: 70,   8: 80,
    9: 90,  10: 100, 11: 115, 12: 130,
    13: 145, 14: 160, 15: 180, 16: 200,
}
# Plan start date — update this when Andy confirms the real start
PLAN_START_DATE = datetime(2026, 3, 10)


# ---------------------------------------------------------------------------
# Google Sheets helpers
# ---------------------------------------------------------------------------

def get_gspread_client():
    """Authenticate and return gspread client."""
    if not _GSPREAD:
        print("[ERROR] gspread not installed. Run: pip install gspread")
        sys.exit(1)

    creds_path = os.path.join(_project_root, GOOGLE_CREDENTIALS_FILE)
    if not os.path.exists(creds_path):
        print(f"[ERROR] Credentials file not found: {creds_path}")
        sys.exit(1)

    creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    return gspread.authorize(creds)


def read_listing_queue(client) -> dict:
    """Read Listing Queue sheet and count statuses."""
    try:
        ss = client.open_by_key(GOOGLE_SPREADSHEET_ID)
        ws = ss.worksheet("Listing Queue")
        all_rows = ws.get_all_records()
    except gspread.exceptions.WorksheetNotFound:
        return {"total": 0, "by_status": {}, "error": "Listing Queue sheet not found"}
    except Exception as e:
        return {"total": 0, "by_status": {}, "error": str(e)}

    by_status = {}
    for row in all_rows:
        status = str(row.get("Status", "")).strip().upper() or "UNKNOWN"
        by_status[status] = by_status.get(status, 0) + 1

    return {
        "total": len(all_rows),
        "by_status": by_status,
        "error": None,
    }


def ensure_review_sheet(client):
    """Get or create the WEEKLY_REVIEW worksheet."""
    ss = client.open_by_key(GOOGLE_SPREADSHEET_ID)
    try:
        ws = ss.worksheet(REVIEW_SHEET_NAME)
    except gspread.exceptions.WorksheetNotFound:
        ws = ss.add_worksheet(title=REVIEW_SHEET_NAME, rows=100, cols=5)
        ws.update(range_name="A1:E1", values=[["Date", "Summary", "Queue Stats",
                             "Plan Progress", "Lessons Count"]])
    return ws


# ---------------------------------------------------------------------------
# Local file readers
# ---------------------------------------------------------------------------

def read_changelog_last_7_days() -> str:
    """Extract CHANGELOG entries from the last 7 days."""
    changelog_path = Path(_project_root) / "CHANGELOG.md"
    if not changelog_path.exists():
        return "CHANGELOG.md not found."

    text = changelog_path.read_text(encoding="utf-8")

    # Extract [Unreleased] section — everything between ## [Unreleased] and next ## [
    unreleased_match = re.search(
        r"## \[Unreleased\]\s*\n(.*?)(?=\n## \[|\Z)",
        text, re.DOTALL,
    )
    if not unreleased_match:
        return "No [Unreleased] section found."

    section = unreleased_match.group(1).strip()
    if not section:
        return "No unreleased changes."

    # Truncate to keep summary concise
    lines = section.splitlines()
    if len(lines) > 30:
        lines = lines[:30] + [f"... and {len(lines) - 30} more lines"]
    return "\n".join(lines)


def read_lessons_recent(n: int = 5) -> str:
    """Return the last N lesson entries from LESSONS.md."""
    lessons_path = Path(_project_root) / "LESSONS.md"
    if not lessons_path.exists():
        return "LESSONS.md not found."

    text = lessons_path.read_text(encoding="utf-8")

    # Find all ### dated entries
    entries = re.findall(
        r"(### \d{4}-\d{2}-\d{2} .*?)(?=\n### \d{4}-\d{2}-\d{2}|\n---|\Z)",
        text, re.DOTALL,
    )
    if not entries:
        return "No dated lesson entries found."

    recent = entries[:n]  # already most-recent-first per LESSONS.md format
    summaries = []
    for entry in recent:
        # Extract just the header line
        header = entry.splitlines()[0].strip()
        summaries.append(f"- {header.replace('### ', '')}")

    return "\n".join(summaries)


def count_total_lessons() -> int:
    """Count total lesson entries in LESSONS.md."""
    lessons_path = Path(_project_root) / "LESSONS.md"
    if not lessons_path.exists():
        return 0
    text = lessons_path.read_text(encoding="utf-8")
    return len(re.findall(r"### \d{4}-\d{2}-\d{2}", text))


def get_plan_progress(total_listings: int) -> str:
    """Compare listing count against 16-week plan targets."""
    today = datetime.now()
    days_since_start = (today - PLAN_START_DATE).days
    current_week = max(1, min(16, (days_since_start // 7) + 1))

    target = SIXTEEN_WEEK_PLAN.get(current_week, SIXTEEN_WEEK_PLAN[16])
    delta = total_listings - target
    pct = (total_listings / target * 100) if target > 0 else 0

    if delta >= 0:
        status = "ON TRACK"
    elif delta >= -5:
        status = "SLIGHTLY BEHIND"
    else:
        status = "BEHIND"

    return (
        f"Week {current_week}/16 | Target: {target} | Actual: {total_listings} | "
        f"{pct:.0f}% | {status} ({delta:+d})"
    )


# ---------------------------------------------------------------------------
# Summary builder
# ---------------------------------------------------------------------------

def build_summary(queue_stats: dict, changelog: str, lessons: str,
                  plan_progress: str, lessons_count: int) -> str:
    """Build the plain-English weekly review summary."""
    today = datetime.now().strftime("%Y-%m-%d")
    by_status = queue_stats.get("by_status", {})

    status_lines = []
    for status, count in sorted(by_status.items()):
        status_lines.append(f"  - {status}: {count}")
    status_block = "\n".join(status_lines) if status_lines else "  (no listings)"

    summary = f"""# Weekly Review — {today}

## Listing Queue
Total listings: {queue_stats['total']}
{status_block}

## 16-Week Plan Progress
{plan_progress}

## CHANGELOG (Unreleased)
{changelog}

## Recent Lessons ({lessons_count} total)
{lessons}
"""

    if queue_stats.get("error"):
        summary += f"\n## Warnings\n- Queue read error: {queue_stats['error']}\n"

    return summary


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Weekly review generator")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print summary to terminal without writing to Sheets")
    args = parser.parse_args()

    print("[INFO] Generating weekly review...")

    # Read local files (no API needed)
    changelog = read_changelog_last_7_days()
    lessons = read_lessons_recent(5)
    lessons_count = count_total_lessons()

    if args.dry_run:
        # Dry run: skip Sheets, use placeholder queue stats
        queue_stats = {"total": 0, "by_status": {}, "error": "dry-run mode"}
        plan_progress = get_plan_progress(queue_stats["total"])
        summary = build_summary(queue_stats, changelog, lessons,
                                plan_progress, lessons_count)
        print(summary)
        print("[OK] Dry run complete (no Sheets write)")
        return

    # Connect to Google Sheets
    client = get_gspread_client()

    # Read queue
    queue_stats = read_listing_queue(client)
    plan_progress = get_plan_progress(queue_stats["total"])

    # Build summary
    summary = build_summary(queue_stats, changelog, lessons,
                            plan_progress, lessons_count)

    # Print to terminal
    print(summary)

    # Write to WEEKLY_REVIEW sheet
    try:
        ws = ensure_review_sheet(client)
        today = datetime.now().strftime("%Y-%m-%d")

        # Compact row for the sheet
        status_compact = ", ".join(
            f"{s}: {c}" for s, c in sorted(queue_stats.get("by_status", {}).items())
        )
        row = [
            today,
            summary,
            f"Total: {queue_stats['total']} | {status_compact}",
            plan_progress,
            str(lessons_count),
        ]
        ws.append_row(row, value_input_option="RAW")
        print(f"[OK] Review written to '{REVIEW_SHEET_NAME}' tab")
    except Exception as e:
        print(f"[ERROR] Failed to write to Sheets: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
