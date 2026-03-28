#!/usr/bin/env python3
"""
pinterest_scheduler.py — PurpleOcaz Pinterest auto-poster.

Reads configs/pinterest_queue.json, posts up to 3 pending pins whose
scheduled_date <= today, marks them posted, logs to logs/pinterest.log.

Cron (3 runs/day — each posts 1 pin):
    0 10 * * * cd /root/NEW-AI-PROJECT && python3 scripts/pinterest_scheduler.py >> logs/pinterest.log 2>&1
    0 14 * * * cd /root/NEW-AI-PROJECT && python3 scripts/pinterest_scheduler.py >> logs/pinterest.log 2>&1
    0 18 * * * cd /root/NEW-AI-PROJECT && python3 scripts/pinterest_scheduler.py >> logs/pinterest.log 2>&1

Manual run:
    python3 scripts/pinterest_scheduler.py [--dry-run] [--limit N]
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import date, datetime
from pathlib import Path

from dotenv import load_dotenv

PROJECT    = Path(__file__).parent.parent
load_dotenv(PROJECT / ".env")
sys.path.insert(0, str(PROJECT))

from scripts.pinterest_oauth import get_valid_tokens, refresh_tokens, load_tokens, save_tokens

QUEUE_FILE = PROJECT / "configs" / "pinterest_queue.json"
LOG_FILE   = PROJECT / "logs" / "pinterest.log"
API_BASE   = "https://api.pinterest.com/v5"

LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


# ── Logging ───────────────────────────────────────────────────────────────────

def log(msg: str) -> None:
    ts    = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    line  = f"[{ts}] {msg}"
    print(line)
    with LOG_FILE.open("a") as f:
        f.write(line + "\n")


# ── Queue helpers ─────────────────────────────────────────────────────────────

def load_queue() -> list[dict]:
    if not QUEUE_FILE.exists():
        return []
    return json.loads(QUEUE_FILE.read_text())


def save_queue(queue: list[dict]) -> None:
    QUEUE_FILE.write_text(json.dumps(queue, indent=2))


def due_pins(queue: list[dict], limit: int) -> list[dict]:
    today = date.today().isoformat()
    return [
        p for p in queue
        if p.get("status") == "pending"
        and p.get("scheduled_date", "9999-99-99") <= today
    ][:limit]


# ── Pinterest API ─────────────────────────────────────────────────────────────

def _api(method: str, path: str, body: dict | None, tokens: dict) -> dict:
    url  = f"{API_BASE}{path}"
    data = json.dumps(body).encode() if body else None
    req  = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {tokens['access_token']}",
            "Content-Type":  "application/json",
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        # Auto-refresh on 401
        if e.code == 401:
            log("  [Auth] 401 — refreshing token and retrying...")
            tokens = refresh_tokens(tokens)
            req.add_header("Authorization", f"Bearer {tokens['access_token']}")
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read())
        raise RuntimeError(f"Pinterest API {e.code}: {err_body}") from e


def get_or_create_board(board_name: str, tokens: dict) -> str:
    """Return board_id for board_name, creating it if it doesn't exist."""
    # List boards (paginate if needed)
    result = _api("GET", "/boards?page_size=100", None, tokens)
    for board in result.get("items", []):
        if board["name"].lower() == board_name.lower():
            log(f"  [Board] Found existing: '{board_name}' → {board['id']}")
            return board["id"]

    # Create board
    resp = _api("POST", "/boards", {"name": board_name, "privacy": "PUBLIC"}, tokens)
    board_id = resp["id"]
    log(f"  [Board] Created: '{board_name}' → {board_id}")
    return board_id


def post_pin(pin: dict, board_id: str, tokens: dict) -> dict:
    """POST a single pin to Pinterest. Returns API response."""
    payload = {
        "board_id":   board_id,
        "title":      pin["title"],
        "description": pin["description"],
        "link":       pin.get("link", ""),
        "media_source": {
            "source_type": "image_url",
            "url":         pin["image_url"],
        },
    }
    # Video pin: use video_id source type if image_url ends in .mp4
    if pin["image_url"].lower().endswith(".mp4"):
        payload["media_source"] = {
            "source_type": "video_id",
            "cover_image_url": pin.get("cover_image_url", pin["image_url"]),
            "media_id":        pin.get("media_id", ""),
        }
    return _api("POST", "/pins", payload, tokens)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(description="Pinterest auto-poster")
    ap.add_argument("--dry-run", action="store_true", help="Preview pins without posting")
    ap.add_argument("--limit",   type=int, default=1, help="Max pins to post (default 1 per cron run)")
    args = ap.parse_args()

    log("=" * 50)
    log(f"pinterest_scheduler.py — {'DRY RUN' if args.dry_run else 'LIVE'}")

    queue = load_queue()
    if not queue:
        log("Queue is empty. Run populate_pinterest_queue.py to build it.")
        return

    pins = due_pins(queue, args.limit)
    if not pins:
        log(f"No pending pins due today ({date.today().isoformat()}) — nothing to post.")
        return

    log(f"Found {len(pins)} pin(s) to post.")

    if args.dry_run:
        for p in pins:
            log(f"  [DRY-RUN] Would post: '{p['title']}' → {p['board']}")
        return

    tokens = get_valid_tokens()
    board_cache: dict[str, str] = {}
    posted = 0

    for pin in pins:
        board_name = pin["board"]
        if board_name not in board_cache:
            board_cache[board_name] = get_or_create_board(board_name, tokens)
        board_id = board_cache[board_name]

        log(f"  Posting: '{pin['title']}'")
        log(f"    image  : {pin['image_url']}")
        log(f"    board  : {board_name} ({board_id})")
        log(f"    link   : {pin.get('link', '')}")

        try:
            resp = post_pin(pin, board_id, tokens)
            pin_id = resp.get("id", "unknown")
            log(f"    ✓ Posted — pin_id: {pin_id}")

            # Mark posted in queue
            for q in queue:
                if q is pin:
                    q["status"]      = "posted"
                    q["posted_date"] = date.today().isoformat()
                    q["pin_id"]      = pin_id
                    break

            save_queue(queue)
            posted += 1

        except Exception as e:
            log(f"    ✗ FAILED: {e}")
            # Don't mark as failed — leave pending to retry next run

        time.sleep(2)  # polite delay between pins

    log(f"Done. {posted}/{len(pins)} pin(s) posted.")
    log("=" * 50)


if __name__ == "__main__":
    main()
