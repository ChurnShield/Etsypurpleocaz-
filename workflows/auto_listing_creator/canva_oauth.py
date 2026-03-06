# =============================================================================
# workflows/auto_listing_creator/canva_oauth.py
#
# One-time Canva OAuth 2.0 setup (PKCE flow).
#
# Run:  python workflows/auto_listing_creator/canva_oauth.py
#
# After this, the auto listing creator can:
#   - Search your Canva designs
#   - Export designs as PNG (thumbnails) and PDF (previews)
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


def generate_pkce():
    """Generate PKCE code_verifier and code_challenge (S256)."""
    verifier = secrets.token_urlsafe(64)[:128]
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return verifier, challenge


def build_auth_url(code_challenge, state):
    """Build the Canva OAuth authorization URL."""
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
    """Exchange authorization code for access + refresh tokens."""
    data = urllib.parse.urlencode({
        "grant_type":     "authorization_code",
        "code":           auth_code,
        "code_verifier":  code_verifier,
        "redirect_uri":   REDIRECT_URI,
    }).encode("utf-8")

    # Canva uses Basic auth with client_id:client_secret
    credentials = base64.b64encode(
        f"{CANVA_CLIENT_ID}:{CANVA_CLIENT_SECRET}".encode("utf-8")
    ).decode("utf-8")

    req = urllib.request.Request(TOKEN_URL, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("Authorization", f"Basic {credentials}")

    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def save_tokens(token_data):
    """Save tokens to disk."""
    with open(TOKEN_FILE, "w") as f:
        json.dump(token_data, f, indent=2)
    print(f"  Tokens saved to: {TOKEN_FILE}")


def load_tokens():
    """Load tokens from disk."""
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE) as f:
        return json.load(f)


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Handles the Canva OAuth callback."""
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
                "<h1 style='color:#6B2189'>PurpleOcaz - Canva Authorization Successful!</h1>"
                "<p>You can close this tab and return to your terminal.</p>"
                "</body></html>"
            )
        else:
            error = params.get("error", ["unknown"])[0]
            html = (
                f"<html><body style='font-family:sans-serif;text-align:center;padding:60px'>"
                f"<h1 style='color:red'>Canva Authorization Failed</h1>"
                f"<p>Error: {error}</p>"
                f"</body></html>"
            )

        self.wfile.write(html.encode("utf-8"))

    def log_message(self, format, *args):
        pass


def main():
    print("\n=== Canva OAuth Setup ===\n")

    if not CANVA_CLIENT_ID:
        print("  ERROR: CANVA_CLIENT_ID not set in .env")
        return
    if not CANVA_CLIENT_SECRET:
        print("  ERROR: CANVA_CLIENT_SECRET not set in .env")
        return

    existing = load_tokens()
    if existing and existing.get("access_token"):
        print("  Existing tokens found - re-authorizing with updated scopes...")
        print(f"  Scopes: {SCOPES}")
        print()

    # Generate PKCE
    code_verifier, code_challenge = generate_pkce()
    state = secrets.token_urlsafe(16)

    # Build auth URL
    auth_url = build_auth_url(code_challenge, state)

    # Start callback server
    server = HTTPServer(("127.0.0.1", 3847), OAuthCallbackHandler)
    server_thread = Thread(target=server.handle_request, daemon=True)
    server_thread.start()

    print("  Opening your browser to authorize with Canva...")
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
        print("\n  ERROR: State mismatch - possible CSRF attack")
        return

    print("  Authorization code received!")
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
    print(f"\n=== Canva OAuth setup complete! ===")
    print(f"  The auto listing creator can now search and export your Canva designs.\n")


if __name__ == "__main__":
    main()
