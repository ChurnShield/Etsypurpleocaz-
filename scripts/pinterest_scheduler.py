#!/usr/bin/env python3
"""
pinterest_scheduler.py — PurpleOcaz Pinterest auto-poster (py3-pinterest).

Reads configs/pinterest_queue.json, posts up to 1 pending pin whose
scheduled_date <= today, marks it posted, logs to logs/pinterest.log.

Uses py3-pinterest (unofficial) with email/password login via Selenium.
Session cookies are cached under data/pinterest_session/ — login only
happens when the session expires (~15 days).

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
import tempfile
import time
import urllib.request
from datetime import date, datetime
from pathlib import Path

from dotenv import load_dotenv

PROJECT = Path(__file__).parent.parent
load_dotenv(PROJECT / ".env")
sys.path.insert(0, str(PROJECT))

QUEUE_FILE    = PROJECT / "configs" / "pinterest_queue.json"
LOG_FILE      = PROJECT / "logs" / "pinterest.log"
SESSION_ROOT  = str(PROJECT / "data" / "pinterest_session")

LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
Path(SESSION_ROOT).mkdir(parents=True, exist_ok=True)


# ── Logging ───────────────────────────────────────────────────────────────────

def log(msg: str) -> None:
    ts   = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    line = f"[{ts}] {msg}"
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


# ── py3-pinterest client ──────────────────────────────────────────────────────

def get_pinterest_client():
    """Return an authenticated py3-pinterest client."""
    from py3pin.Pinterest import Pinterest

    email    = os.getenv("PINTEREST_EMAIL", "")
    password = os.getenv("PINTEREST_PASSWORD", "")

    if not email or not password:
        raise RuntimeError(
            "PINTEREST_EMAIL and PINTEREST_PASSWORD must be set in .env"
        )

    client = Pinterest(
        email=email,
        password=password,
        username="",
        cred_root=SESSION_ROOT,
    )
    log("  [Auth] Logging in to Pinterest (Selenium — headless)...")
    client.login()
    log("  [Auth] Login complete.")
    return client


def get_or_create_board(client, board_name: str) -> str:
    """Return board_id for board_name, creating it if it doesn't exist."""
    boards = client.boards_all()
    for board in boards:
        if board.get("name", "").lower() == board_name.lower():
            board_id = board["id"]
            log(f"  [Board] Found existing: '{board_name}' → {board_id}")
            return board_id

    # Create board
    resp     = client.create_board(name=board_name, privacy="public")
    board_id = resp["resource_response"]["data"]["id"]
    log(f"  [Board] Created: '{board_name}' → {board_id}")
    return board_id


def download_image(url: str) -> str:
    """Download image from URL to /tmp/, return local file path."""
    suffix = Path(url.split("?")[0]).suffix or ".jpg"
    tmp    = tempfile.NamedTemporaryFile(
        delete=False, suffix=suffix, dir="/tmp", prefix="pinterest_"
    )
    log(f"  [Download] {url} → {tmp.name}")
    urllib.request.urlretrieve(url, tmp.name)
    return tmp.name


def post_pin(client, pin: dict, board_id: str) -> str:
    """Download image from Spaces and upload via upload_pin(). Returns pin_id."""
    local_path = download_image(pin["image_url"])
    try:
        resp = client.upload_pin(
            board_id=board_id,
            image_file=local_path,
            description=pin.get("description", ""),
            link=pin.get("link", ""),
            title=pin.get("title", ""),
        )
        # Response shape: resource_response.data.id
        pin_id = (
            resp.get("resource_response", {})
                .get("data", {})
                .get("id", "unknown")
        )
        return pin_id
    finally:
        try:
            os.unlink(local_path)
        except OSError:
            pass


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(description="Pinterest auto-poster (py3-pinterest)")
    ap.add_argument("--dry-run", action="store_true", help="Preview pins without posting")
    ap.add_argument("--limit",   type=int, default=1, help="Max pins to post (default 1 per cron run)")
    args = ap.parse_args()

    log("=" * 50)
    log(f"pinterest_scheduler.py — {'DRY RUN' if args.dry_run else 'LIVE'} (py3-pinterest)")

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
            log(f"  [DRY-RUN] Would post: '{p['title']}' → board '{p['board']}'")
            log(f"    image : {p['image_url']}")
            log(f"    link  : {p.get('link', '')}")
        return

    client      = get_pinterest_client()
    board_cache: dict[str, str] = {}
    posted      = 0

    for pin in pins:
        board_name = pin["board"]
        if board_name not in board_cache:
            board_cache[board_name] = get_or_create_board(client, board_name)
        board_id = board_cache[board_name]

        log(f"  Posting: '{pin['title']}'")
        log(f"    image : {pin['image_url']}")
        log(f"    board : {board_name} ({board_id})")
        log(f"    link  : {pin.get('link', '')}")

        try:
            pin_id = post_pin(client, pin, board_id)
            log(f"    OK Posted — pin_id: {pin_id}")

            for q in queue:
                if q is pin:
                    q["status"]      = "posted"
                    q["posted_date"] = date.today().isoformat()
                    q["pin_id"]      = pin_id
                    break

            save_queue(queue)
            posted += 1

        except Exception as e:
            log(f"    FAILED: {e}")
            # Leave status=pending to retry next run

        time.sleep(2)

    log(f"Done. {posted}/{len(pins)} pin(s) posted.")
    log("=" * 50)


if __name__ == "__main__":
    main()
