# =============================================================================
# canva_oauth_headless.py
#
# Headless Canva OAuth 2.0 setup (PKCE flow) for remote servers.
# Instead of a local callback server, you paste the redirect URL manually.
#
# Run:  python workflows/auto_listing_creator/canva_oauth_headless.py
# =============================================================================

import sys
import os
import json
import hashlib
import base64
import secrets
import urllib.request
import urllib.parse
import urllib.error

_here = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(_here))
sys.path.insert(0, _project_root)

from dotenv import load_dotenv
load_dotenv()

CANVA_CLIENT_ID     = os.getenv("CANVA_CLIENT_ID", "")
CANVA_CLIENT_SECRET = os.getenv("CANVA_CLIENT_SECRET", "")

REDIRECT_URI  = "http://127.0.0.1:3847/callback"
SCOPES        = "design:meta:read design:content:read design:content:write asset:read asset:write"
TOKEN_FILE    = os.path.join(_here, "canva_tokens.json")
AUTH_URL_BASE = "https://www.canva.com/api/oauth/authorize"
TOKEN_URL     = "https://api.canva.com/rest/v1/oauth/token"

# Also update the MCP project .env
MCP_ENV_FILE  = os.path.join(_project_root, "purpleocaz-canva-mcp", ".env")


def generate_pkce():
    verifier = secrets.token_urlsafe(64)[:128]
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return verifier, challenge


def build_auth_url(code_challenge, state):
    params = {
        "response_type":         "code",
        "redirect_uri":          REDIRECT_URI,
        "scope":                 SCOPES,
        "client_id":             CANVA_CLIENT_ID,
        "state":                 state,
        "code_challenge":        code_challenge,
        "code_challenge_method": "S256",
    }
    return f"{AUTH_URL_BASE}?{urllib.parse.urlencode(params)}"


def exchange_code(auth_code, code_verifier):
    data = urllib.parse.urlencode({
        "grant_type":     "authorization_code",
        "code":           auth_code,
        "code_verifier":  code_verifier,
        "redirect_uri":   REDIRECT_URI,
    }).encode("utf-8")

    credentials = base64.b64encode(
        f"{CANVA_CLIENT_ID}:{CANVA_CLIENT_SECRET}".encode("utf-8")
    ).decode("utf-8")

    req = urllib.request.Request(TOKEN_URL, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("Authorization", f"Basic {credentials}")

    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def save_tokens(token_data):
    with open(TOKEN_FILE, "w") as f:
        json.dump(token_data, f, indent=2)
    print(f"  Tokens saved to: {TOKEN_FILE}")


def update_mcp_env(token_data):
    """Update the purpleocaz-canva-mcp .env with the new tokens."""
    if not os.path.exists(MCP_ENV_FILE):
        print(f"  MCP .env not found at {MCP_ENV_FILE}, skipping")
        return

    with open(MCP_ENV_FILE, "r") as f:
        lines = f.readlines()

    updated = []
    for line in lines:
        if line.startswith("CANVA_ACCESS_TOKEN="):
            updated.append(f"CANVA_ACCESS_TOKEN={token_data.get('access_token', 'PLACEHOLDER')}\n")
        elif line.startswith("CANVA_REFRESH_TOKEN="):
            updated.append(f"CANVA_REFRESH_TOKEN={token_data.get('refresh_token', 'PLACEHOLDER')}\n")
        else:
            updated.append(line)

    with open(MCP_ENV_FILE, "w") as f:
        f.writelines(updated)
    print(f"  MCP .env updated: {MCP_ENV_FILE}")


def extract_code_from_url(url):
    """Extract the authorization code from a callback URL."""
    parsed = urllib.parse.urlparse(url)
    params = urllib.parse.parse_qs(parsed.query)
    return params.get("code", [None])[0]


def main():
    print("\n=== Canva OAuth Setup (Headless) ===\n")

    if not CANVA_CLIENT_ID:
        print("  ERROR: CANVA_CLIENT_ID not set in .env")
        return
    if not CANVA_CLIENT_SECRET:
        print("  ERROR: CANVA_CLIENT_SECRET not set in .env")
        return

    print(f"  Client ID: {CANVA_CLIENT_ID}")
    print(f"  Scopes:    {SCOPES}\n")

    # Generate PKCE
    code_verifier, code_challenge = generate_pkce()
    state = secrets.token_urlsafe(16)

    # Build auth URL
    auth_url = build_auth_url(code_challenge, state)

    print("=" * 70)
    print("  STEP 1: Open this URL in your browser:\n")
    print(f"  {auth_url}\n")
    print("=" * 70)
    print()
    print("  STEP 2: Authorize PurpleOcaz to access your Canva account.")
    print()
    print("  STEP 3: After authorizing, your browser will try to redirect to")
    print("  http://127.0.0.1:3847/callback?code=... which will FAIL.")
    print("  That's OK! Copy the FULL URL from your browser's address bar.\n")
    print("=" * 70)
    print()

    raw = input("  Paste the full redirect URL here: ").strip()

    if not raw:
        print("\n  ERROR: No URL provided")
        return

    # Handle both full URL and bare code
    if raw.startswith("http"):
        auth_code = extract_code_from_url(raw)
        # Also check state
        parsed = urllib.parse.urlparse(raw)
        params = urllib.parse.parse_qs(parsed.query)
        returned_state = params.get("state", [None])[0]
        if returned_state and returned_state != state:
            print("\n  ERROR: State mismatch - possible CSRF attack")
            return
    else:
        auth_code = raw

    if not auth_code:
        print("\n  ERROR: Could not extract authorization code from URL")
        return

    print(f"\n  Authorization code: {auth_code[:20]}...")
    print("  Exchanging code for tokens...")

    try:
        token_data = exchange_code(auth_code, code_verifier)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"\n  ERROR: Token exchange failed ({e.code}): {body}")
        return

    save_tokens(token_data)
    update_mcp_env(token_data)

    print(f"\n  Access token:  {token_data.get('access_token', '')[:20]}...")
    print(f"  Refresh token: {token_data.get('refresh_token', '')[:20]}...")
    print(f"  Expires in:    {token_data.get('expires_in', 0)} seconds")
    print(f"\n=== Canva OAuth setup complete! ===\n")


if __name__ == "__main__":
    main()
