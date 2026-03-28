#!/usr/bin/env python3
"""
pinterest_oauth.py — Pinterest API v5 OAuth 2.0 flow.

Run once to get access + refresh tokens:
    python3 scripts/pinterest_oauth.py

Saves to: workflows/pinterest_tokens.json
Reads credentials from .env: PINTEREST_APP_ID, PINTEREST_APP_SECRET
"""

import base64
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

from dotenv import load_dotenv

PROJECT = Path(__file__).parent.parent
load_dotenv(PROJECT / ".env")

TOKEN_FILE = PROJECT / "workflows" / "pinterest_tokens.json"
AUTH_URL   = "https://www.pinterest.com/oauth/"
TOKEN_URL  = "https://api.pinterest.com/v5/oauth/token"
SCOPES     = "boards:read,boards:write,pins:read,pins:write"

APP_ID     = os.environ.get("PINTEREST_APP_ID", "1555060")
APP_SECRET = os.environ.get("PINTEREST_APP_SECRET", "")


def _basic_auth() -> str:
    return base64.b64encode(f"{APP_ID}:{APP_SECRET}".encode()).decode()


def load_tokens() -> dict | None:
    if TOKEN_FILE.exists():
        return json.loads(TOKEN_FILE.read_text())
    return None


def save_tokens(data: dict) -> None:
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(json.dumps(data, indent=2))
    print(f"  Tokens saved → {TOKEN_FILE}")


def refresh_tokens(tokens: dict) -> dict:
    """Exchange refresh_token for new access_token."""
    payload = urllib.parse.urlencode({
        "grant_type":    "refresh_token",
        "refresh_token": tokens["refresh_token"],
    }).encode()
    req = urllib.request.Request(
        TOKEN_URL,
        data=payload,
        headers={
            "Authorization": f"Basic {_basic_auth()}",
            "Content-Type":  "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    tokens["access_token"]  = data["access_token"]
    tokens["expires_at"]    = time.time() + data.get("expires_in", 3600)
    if "refresh_token" in data:
        tokens["refresh_token"] = data["refresh_token"]
    save_tokens(tokens)
    return tokens


def get_valid_tokens() -> dict:
    """Return valid tokens, refreshing if expired. Run OAuth if none exist."""
    if not APP_SECRET:
        sys.exit(
            "ERROR: PINTEREST_APP_SECRET not set in .env\n"
            "Add it then re-run: python3 scripts/pinterest_oauth.py"
        )

    tokens = load_tokens()
    if tokens:
        if time.time() < tokens.get("expires_at", 0) - 60:
            return tokens
        print("  [Pinterest] Access token expired — refreshing...")
        return refresh_tokens(tokens)

    # ── Full OAuth flow ───────────────────────────────────────────────────────
    redirect_uri = "https://localhost/"
    params = urllib.parse.urlencode({
        "client_id":     APP_ID,
        "redirect_uri":  redirect_uri,
        "response_type": "code",
        "scope":         SCOPES,
        "state":         "purpleocaz",
    })
    auth_link = f"{AUTH_URL}?{params}"

    print("\n" + "=" * 60)
    print("PINTEREST OAUTH — First-time setup")
    print("=" * 60)
    print(f"\n1. Open this URL in your browser:\n\n   {auth_link}\n")
    print("2. Log in to Pinterest and click Authorise")
    print("3. You'll be redirected to localhost (page will fail — that's OK)")
    print("4. Copy the full URL from the browser address bar")
    print("   It will look like: https://localhost/?state=purpleocaz&code=XXXX\n")

    callback = input("Paste the full redirect URL here: ").strip()
    parsed   = urllib.parse.urlparse(callback)
    code     = urllib.parse.parse_qs(parsed.query).get("code", [None])[0]
    if not code:
        sys.exit("ERROR: Could not extract code from URL. Try again.")

    payload = urllib.parse.urlencode({
        "grant_type":   "authorization_code",
        "code":         code,
        "redirect_uri": redirect_uri,
    }).encode()
    req = urllib.request.Request(
        TOKEN_URL,
        data=payload,
        headers={
            "Authorization": f"Basic {_basic_auth()}",
            "Content-Type":  "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())

    tokens = {
        "access_token":  data["access_token"],
        "refresh_token": data.get("refresh_token", ""),
        "expires_at":    time.time() + data.get("expires_in", 3600),
        "scope":         data.get("scope", SCOPES),
        "app_id":        APP_ID,
    }
    save_tokens(tokens)
    print("\n  OAuth complete. Tokens saved.")
    return tokens


if __name__ == "__main__":
    tokens = get_valid_tokens()
    print(f"\n  access_token : {tokens['access_token'][:20]}…")
    print(f"  expires_at   : {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(tokens['expires_at']))}")
    print(f"  scope        : {tokens.get('scope', '')}")
