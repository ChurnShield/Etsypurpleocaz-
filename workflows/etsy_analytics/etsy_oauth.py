# =============================================================================
# workflows/etsy_analytics/etsy_oauth.py
#
# One-time Etsy OAuth 2.0 setup (PKCE flow).
#
# Run:  python workflows/etsy_analytics/etsy_oauth.py
#
# What happens:
#   1. Opens your browser to Etsy's authorization page
#   2. You click "Allow" to grant your app access to your shop data
#   3. Etsy redirects to localhost where this script captures the code
#   4. Exchanges the code for access + refresh tokens
#   5. Saves tokens to etsy_tokens.json (used by the analytics workflow)
#
# After this, the workflow can read your transactions/receipts (sales data).
# =============================================================================

import sys
import os
import json
import hashlib
import base64
import secrets
import webbrowser
import urllib.request
import urllib.parse
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

_here = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(_here))
sys.path.insert(0, _here)
sys.path.insert(1, _project_root)

from config import ETSY_API_KEYSTRING, ETSY_SHARED_SECRET

# -- OAuth settings --
REDIRECT_URI  = "http://localhost:3847/callback"
SCOPES        = "shops_r transactions_r listings_r listings_w listings_d"
TOKEN_FILE    = os.path.join(_here, "etsy_tokens.json")
AUTH_URL_BASE = "https://www.etsy.com/oauth/connect"
TOKEN_URL     = "https://api.etsy.com/v3/public/oauth/token"


def generate_pkce():
    """Generate PKCE code_verifier and code_challenge."""
    verifier = secrets.token_urlsafe(64)[:128]
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return verifier, challenge


def build_auth_url(code_challenge, state):
    """Build the Etsy OAuth authorization URL."""
    params = {
        "response_type":        "code",
        "redirect_uri":         REDIRECT_URI,
        "scope":                SCOPES,
        "client_id":            ETSY_API_KEYSTRING,
        "state":                state,
        "code_challenge":       code_challenge,
        "code_challenge_method": "S256",
    }
    return f"{AUTH_URL_BASE}?{urllib.parse.urlencode(params)}"


def exchange_code(auth_code, code_verifier):
    """Exchange the authorization code for access + refresh tokens."""
    data = urllib.parse.urlencode({
        "grant_type":    "authorization_code",
        "client_id":     ETSY_API_KEYSTRING,
        "redirect_uri":  REDIRECT_URI,
        "code":          auth_code,
        "code_verifier": code_verifier,
    }).encode("utf-8")

    req = urllib.request.Request(TOKEN_URL, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("x-api-key", f"{ETSY_API_KEYSTRING}:{ETSY_SHARED_SECRET}")

    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def refresh_access_token(refresh_token):
    """Use a refresh token to get a new access token."""
    data = urllib.parse.urlencode({
        "grant_type":    "refresh_token",
        "client_id":     ETSY_API_KEYSTRING,
        "refresh_token": refresh_token,
    }).encode("utf-8")

    req = urllib.request.Request(TOKEN_URL, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("x-api-key", f"{ETSY_API_KEYSTRING}:{ETSY_SHARED_SECRET}")

    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def save_tokens(token_data):
    """Save tokens to disk."""
    with open(TOKEN_FILE, "w") as f:
        json.dump(token_data, f, indent=2)
    print(f"  Tokens saved to: {TOKEN_FILE}")


def load_tokens():
    """Load tokens from disk. Returns None if not found."""
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE) as f:
        return json.load(f)


# -- Callback server to capture the OAuth redirect --

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Handles the OAuth callback from Etsy."""
    auth_code = None
    state     = None

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        OAuthCallbackHandler.auth_code = params.get("code", [None])[0]
        OAuthCallbackHandler.state     = params.get("state", [None])[0]

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()

        if OAuthCallbackHandler.auth_code:
            html = (
                "<html><body style='font-family:sans-serif;text-align:center;padding:60px'>"
                "<h1 style='color:#6B2189'>PurpleOcaz - Authorization Successful!</h1>"
                "<p>You can close this tab and return to your terminal.</p>"
                "</body></html>"
            )
        else:
            error = params.get("error", ["unknown"])[0]
            html = (
                f"<html><body style='font-family:sans-serif;text-align:center;padding:60px'>"
                f"<h1 style='color:red'>Authorization Failed</h1>"
                f"<p>Error: {error}</p>"
                f"</body></html>"
            )

        self.wfile.write(html.encode("utf-8"))

    def log_message(self, format, *args):
        pass  # Suppress server log output


def main():
    print("\n=== Etsy OAuth Setup ===\n")

    if not ETSY_API_KEYSTRING:
        print("  ERROR: ETSY_API_KEYSTRING not set in .env")
        return

    # Check if already authorized
    existing = load_tokens()
    if existing and existing.get("access_token"):
        print("  Existing tokens found — re-authorizing with updated scopes...")
        print(f"  Scopes: {SCOPES}")
        print()

    # Generate PKCE
    code_verifier, code_challenge = generate_pkce()
    state = secrets.token_urlsafe(16)

    # Build auth URL
    auth_url = build_auth_url(code_challenge, state)

    # Start local callback server
    server = HTTPServer(("localhost", 3847), OAuthCallbackHandler)
    server_thread = Thread(target=server.handle_request, daemon=True)
    server_thread.start()

    print("  Opening your browser to authorize with Etsy...")
    print(f"  If the browser doesn't open, paste this URL:\n")
    print(f"  {auth_url}\n")

    webbrowser.open(auth_url)

    print("  Waiting for authorization callback...")
    server_thread.join(timeout=120)
    server.server_close()

    if not OAuthCallbackHandler.auth_code:
        print("\n  ERROR: No authorization code received (timed out or denied)")
        return

    if OAuthCallbackHandler.state != state:
        print("\n  ERROR: State mismatch — possible CSRF attack")
        return

    print("  Authorization code received!")

    # Exchange for tokens
    print("  Exchanging code for tokens...")
    try:
        token_data = exchange_code(OAuthCallbackHandler.auth_code, code_verifier)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"\n  ERROR: Token exchange failed ({e.code}): {body}")
        return

    save_tokens(token_data)

    print(f"\n  Access token:  {token_data.get('access_token', '')[:20]}...")
    print(f"  Refresh token: {token_data.get('refresh_token', '')[:20]}...")
    print(f"  Expires in:    {token_data.get('expires_in', 0)} seconds")
    print(f"\n=== OAuth setup complete! ===")
    print(f"  The analytics workflow will now pull per-listing sales data.\n")


if __name__ == "__main__":
    main()
