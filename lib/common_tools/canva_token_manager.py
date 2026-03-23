"""
lib/common_tools/canva_token_manager.py

Shared Canva token management: load, validate, auto-refresh, and sync.

Writes refreshed tokens to both:
  - workflows/auto_listing_creator/canva_tokens.json  (Python pipeline)
  - purpleocaz-canva-mcp/.env                         (TypeScript MCP)

Usage:
    from lib.common_tools.canva_token_manager import get_valid_token

    token = get_valid_token()  # auto-refreshes if expired
"""

import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request

_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CANVA_API_URL = "https://api.canva.com/rest/v1"
TOKEN_FILE = os.path.join(
    _project_root, "workflows", "auto_listing_creator", "canva_tokens.json"
)
MCP_ENV_FILE = os.path.join(_project_root, "purpleocaz-canva-mcp", ".env")


def _load_env_var(name: str, default: str = "") -> str:
    """Load from environment, falling back to MCP .env file."""
    val = os.environ.get(name, "")
    if val:
        return val

    if os.path.exists(MCP_ENV_FILE):
        with open(MCP_ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if line.startswith(f"{name}="):
                    return line.split("=", 1)[1].strip()
    return default


def _get_credentials() -> tuple:
    """Return (client_id, client_secret) from environment."""
    client_id = _load_env_var("CANVA_CLIENT_ID")
    client_secret = _load_env_var("CANVA_CLIENT_SECRET")
    return client_id, client_secret


def load_tokens() -> dict:
    """Load token data from canva_tokens.json."""
    if not os.path.exists(TOKEN_FILE):
        return {}
    with open(TOKEN_FILE) as f:
        return json.load(f)


def save_tokens(token_data: dict) -> None:
    """Save tokens to canva_tokens.json and sync to MCP .env."""
    with open(TOKEN_FILE, "w") as f:
        json.dump(token_data, f, indent=2)

    _sync_to_mcp_env(token_data)


def _sync_to_mcp_env(token_data: dict) -> None:
    """Update CANVA_ACCESS_TOKEN and CANVA_REFRESH_TOKEN in MCP .env."""
    if not os.path.exists(MCP_ENV_FILE):
        return

    with open(MCP_ENV_FILE) as f:
        lines = f.readlines()

    updated = []
    for line in lines:
        if line.startswith("CANVA_ACCESS_TOKEN="):
            updated.append(f"CANVA_ACCESS_TOKEN={token_data.get('access_token', '')}\n")
        elif line.startswith("CANVA_REFRESH_TOKEN="):
            updated.append(f"CANVA_REFRESH_TOKEN={token_data.get('refresh_token', '')}\n")
        else:
            updated.append(line)

    with open(MCP_ENV_FILE, "w") as f:
        f.writelines(updated)


def validate_token(access_token: str) -> bool:
    """Test if an access token is still valid via /users/me."""
    try:
        req = urllib.request.Request(f"{CANVA_API_URL}/users/me")
        req.add_header("Authorization", f"Bearer {access_token}")
        req.add_header("Accept", "application/json")
        urllib.request.urlopen(req, timeout=10)
        return True
    except urllib.error.HTTPError as e:
        if e.code == 401:
            return False
        raise
    except Exception:
        return False


def refresh_token(current_refresh_token: str,
                  client_id: str = "",
                  client_secret: str = "") -> dict:
    """
    Exchange a refresh token for new access + refresh tokens.

    Returns the full token response dict with access_token, refresh_token, etc.
    Raises on failure.
    """
    if not client_id or not client_secret:
        client_id, client_secret = _get_credentials()

    if not client_id or not client_secret:
        raise ValueError("CANVA_CLIENT_ID and CANVA_CLIENT_SECRET required for refresh")

    if not current_refresh_token:
        raise ValueError("No refresh token available")

    credentials = base64.b64encode(
        f"{client_id}:{client_secret}".encode("utf-8")
    ).decode("utf-8")

    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": current_refresh_token,
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{CANVA_API_URL}/oauth/token",
        data=data, method="POST",
    )
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("Authorization", f"Basic {credentials}")

    with urllib.request.urlopen(req, timeout=30) as resp:
        new_tokens = json.loads(resp.read().decode("utf-8"))

    return new_tokens


def get_valid_token() -> str:
    """
    Return a valid Canva access token, auto-refreshing if expired.

    Loads from canva_tokens.json, validates via API, refreshes if needed,
    and saves + syncs the new tokens.

    Returns the access token string, or empty string on failure.
    """
    tokens = load_tokens()
    access_token = tokens.get("access_token", "")

    if not access_token:
        return ""

    # Check if current token works
    if validate_token(access_token):
        return access_token

    # Token expired — try refresh
    current_refresh = tokens.get("refresh_token", "")
    if not current_refresh:
        return ""

    try:
        new_tokens = refresh_token(current_refresh)
        save_tokens(new_tokens)
        return new_tokens.get("access_token", "")
    except Exception as e:
        print(f"[canva_token_manager] Refresh failed: {e}")
        return ""
