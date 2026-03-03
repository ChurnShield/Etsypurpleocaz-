#!/usr/bin/env python3
"""
PURPLEOCAZ — Botanical SVG Bundle — Etsy Draft Publisher
=========================================================

One-click script to:
  1. Authenticate with Etsy (OAuth 2.0 PKCE — opens browser)
  2. Create a DRAFT listing with optimised title, description, 13 tags
  3. Upload all 7 listing images (2250x3000 PNGs)
  4. Upload the delivery ZIP (120 SVG designs)
  5. Activate digital delivery

Run:  python publish-botanical-bundle.py

The listing is created in DRAFT status — review in Etsy Shop Manager
before publishing.
"""

import os
import sys
import json
import hashlib
import base64
import secrets
import time
import urllib.request
import urllib.parse
import urllib.error
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

# ── Load .env ────────────────────────────────────────────────────────────────

_HERE = os.path.dirname(os.path.abspath(__file__))
_ENV_PATH = os.path.join(_HERE, ".env")


def _load_env():
    """Load .env file into os.environ."""
    if not os.path.exists(_ENV_PATH):
        return
    with open(_ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip())


_load_env()

ETSY_API_KEYSTRING = os.getenv("ETSY_API_KEYSTRING", "")
ETSY_SHARED_SECRET = os.getenv("ETSY_SHARED_SECRET", "")
ETSY_SHOP_ID = os.getenv("ETSY_SHOP_ID", "")
ETSY_API_KEY = f"{ETSY_API_KEYSTRING}:{ETSY_SHARED_SECRET}"

if not ETSY_API_KEYSTRING or not ETSY_SHARED_SECRET:
    print("ERROR: ETSY_API_KEYSTRING and ETSY_SHARED_SECRET must be set in .env")
    sys.exit(1)

# ── Paths ─────────────────────────────────────────────────────────────────────

EXPORTS_DIR = os.path.join(
    _HERE, "workflows", "auto_listing_creator", "exports", "svg_bundles"
)
THUMBNAILS_DIR = os.path.join(EXPORTS_DIR, "thumbnails")
DELIVERY_ZIP = os.path.join(
    EXPORTS_DIR, "delivery", "Fine-Line-Botanical-Tattoo-Designs-PURPLEOCAZ.zip"
)
TOKEN_FILE = os.path.join(_HERE, "workflows", "etsy_analytics", "etsy_tokens.json")

IMAGE_FILES = [
    "01-Hero.png",
    "02-What-You-Get.png",
    "03-Please-Note.png",
    "04-Usage-Ideas.png",
    "05-Categories.png",
    "06-Leave-Review.png",
    "07-Thank-You.png",
]

# ── Listing Content ───────────────────────────────────────────────────────────

LISTING = {
    "title": (
        "120+ Fine Line Botanical Tattoo SVG Bundle | Floral Tattoo Designs"
        " | Cricut SVG | Tattoo Flash | Digital Download"
    ),
    "description": """★ 120+ FINE-LINE BOTANICAL TATTOO DESIGNS ★

The ultimate collection of delicate, hand-crafted botanical SVG designs — perfect for tattoo artists, Cricut crafters, and creative makers.

120 unique designs across 8 curated categories, delivered as clean vector SVGs ready to use immediately.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

8 DESIGN CATEGORIES

🌹 Roses (12 designs) — Single stems, climbing vines, open blooms, pairs
🌼 Wildflowers (18 designs) — Daisies, poppies, cosmos, lavender, sunflowers, chamomile
🌸 Birth Flowers (12 designs) — All 12 months, January to December
🌿 Botanical Stems (12 designs) — Eucalyptus, fern, monstera, olive, palm, ivy
💐 Bouquets (15 designs) — Minimal 3-stem, mixed large, wildflower, rose arrangements
🎀 Decorative (14 designs) — Berry branches, leaf pairs, trailing vines, detailed leaves
✨ Mini (25 designs) — Tiny tattoo-ready: buds, hearts, stars, crescents, micro florals
🌾 Wreaths & Frames (12 designs) — Full circles, crescents, half-wreaths, corner frames

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHAT YOU GET

• 120 unique SVG vector files
• Organised in 8 named folders
• Clean, scalable vectors — resize without quality loss
• Black line art on transparent background
• Commercial licence included

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PERFECT FOR

→ Tattoo stencils & flash sheets — fine-line references for your studio
→ Cricut & cutting machines — SVG ready to cut in vinyl, paper, or HTV
→ Wall art & prints — high-res gallery-quality at any size
→ Apparel & products — sublimation, embroidery, screen printing
→ Stickers, invitations, journals, engraving, nail art, embroidery

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHY MAKERS LOVE THIS BUNDLE

✓ Less than $0.05 per design — incredible value for 120 unique pieces
✓ 600+ total files when you include all format variations
✓ Commercial licence — use in products you sell
✓ Instant download — start creating within minutes
✓ Scalable vectors — from tiny finger tattoos to large back pieces
✓ Organised folders — find exactly what you need, fast

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HOW TO USE

1. Purchase and download instantly
2. Unzip the file — designs are organised in 8 category folders
3. Open SVGs in your preferred software (Cricut Design Space, Silhouette Studio, Adobe Illustrator, Inkscape, Procreate, etc.)
4. Resize, arrange, and create — vectors scale perfectly to any size

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FAQ

Q: Can I use these commercially?
A: Yes! Commercial licence is included. Use them in products you sell — stickers, prints, apparel, and more.

Q: What software do I need?
A: Any software that opens SVG files — Cricut Design Space, Silhouette Studio, Adobe Illustrator, Inkscape, Canva Pro, and many more.

Q: Can I resize these?
A: Absolutely. These are vector files — they scale to any size without losing quality. Perfect for tiny finger tattoos or large back pieces.

Q: Are these suitable for tattoo stencils?
A: Yes! The fine-line style is specifically designed for clean tattoo references. Print at any size for stencil use.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PLEASE NOTE

• This is a DIGITAL DOWNLOAD — no physical items will be shipped
• Files are delivered as SVG vectors in a ZIP file
• Designs are black line art on transparent background
• Colours may vary slightly between screens

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Questions? We'd love to help — just send us a message!

PurpleOcaz — Handcrafted Digital Designs""",
    "tags": [
        "botanical tattoo svg",
        "fine line tattoo",
        "floral svg bundle",
        "tattoo flash sheet",
        "cricut svg files",
        "minimalist tattoo",
        "wildflower tattoo",
        "rose tattoo design",
        "botanical svg",
        "tattoo stencil",
        "digital download",
        "birth flower tattoo",
        "wreath tattoo svg",
    ],
    "price": 4.99,
    "quantity": 999,
    "who_made": "i_did",
    "when_made": "2020_2025",
    "taxonomy_id": 1874,
}

# ── Etsy API URLs ─────────────────────────────────────────────────────────────

ETSY_BASE = "https://openapi.etsy.com/v3/application"
TOKEN_URL = "https://api.etsy.com/v3/public/oauth/token"
AUTH_URL_BASE = "https://www.etsy.com/oauth/connect"
REDIRECT_URI = "http://localhost:3847/callback"
SCOPES = "shops_r listings_r listings_w listings_d"


# ── OAuth 2.0 PKCE ───────────────────────────────────────────────────────────


def generate_pkce():
    verifier = secrets.token_urlsafe(64)[:128]
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return verifier, challenge


class _CallbackHandler(BaseHTTPRequestHandler):
    auth_code = None
    state = None

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        _CallbackHandler.auth_code = params.get("code", [None])[0]
        _CallbackHandler.state = params.get("state", [None])[0]

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()

        if _CallbackHandler.auth_code:
            html = (
                "<html><body style='font-family:sans-serif;text-align:center;"
                "padding:60px;background:#f8f0ff'>"
                "<h1 style='color:#6B3E9E'>PurpleOcaz — Authorised!</h1>"
                "<p>You can close this tab and return to your terminal.</p>"
                "</body></html>"
            )
        else:
            error = params.get("error", ["unknown"])[0]
            html = (
                f"<html><body style='font-family:sans-serif;text-align:center;"
                f"padding:60px'><h1 style='color:red'>Failed</h1>"
                f"<p>Error: {error}</p></body></html>"
            )
        self.wfile.write(html.encode())

    def log_message(self, *args):
        pass


def authenticate():
    """Run OAuth 2.0 PKCE flow. Returns token dict."""
    code_verifier, code_challenge = generate_pkce()
    state = secrets.token_urlsafe(16)

    auth_params = {
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
        "client_id": ETSY_API_KEYSTRING,
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    auth_url = f"{AUTH_URL_BASE}?{urllib.parse.urlencode(auth_params)}"

    server = HTTPServer(("localhost", 3847), _CallbackHandler)
    thread = Thread(target=server.handle_request, daemon=True)
    thread.start()

    print("\n  Opening browser for Etsy authorisation...")
    print(f"  If it doesn't open, paste this URL:\n")
    print(f"  {auth_url}\n")
    webbrowser.open(auth_url)

    print("  Waiting for authorisation callback...")
    thread.join(timeout=120)
    server.server_close()

    if not _CallbackHandler.auth_code:
        print("\n  ERROR: No auth code received (timed out or denied)")
        sys.exit(1)
    if _CallbackHandler.state != state:
        print("\n  ERROR: State mismatch")
        sys.exit(1)

    print("  Authorisation code received — exchanging for tokens...")

    data = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "client_id": ETSY_API_KEYSTRING,
        "redirect_uri": REDIRECT_URI,
        "code": _CallbackHandler.auth_code,
        "code_verifier": code_verifier,
    }).encode()

    req = urllib.request.Request(TOKEN_URL, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("x-api-key", ETSY_API_KEY)

    with urllib.request.urlopen(req, timeout=30) as resp:
        tokens = json.loads(resp.read().decode())

    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f, indent=2)

    print(f"  Tokens saved to {TOKEN_FILE}")
    return tokens


def load_or_refresh_tokens():
    """Load existing tokens, refresh if expired, or authenticate fresh."""
    if not os.path.exists(TOKEN_FILE):
        return None

    with open(TOKEN_FILE) as f:
        tokens = json.load(f)

    access_token = tokens.get("access_token")
    if not access_token:
        return None

    # Test token
    try:
        req = urllib.request.Request(f"{ETSY_BASE}/users/me")
        req.add_header("x-api-key", ETSY_API_KEY)
        req.add_header("Authorization", f"Bearer {access_token}")
        with urllib.request.urlopen(req, timeout=10) as resp:
            json.loads(resp.read().decode())
        return tokens
    except urllib.error.HTTPError as e:
        if e.code != 401:
            return None

    # Try refresh
    refresh_token = tokens.get("refresh_token")
    if not refresh_token:
        return None

    try:
        data = urllib.parse.urlencode({
            "grant_type": "refresh_token",
            "client_id": ETSY_API_KEYSTRING,
            "refresh_token": refresh_token,
        }).encode()
        req = urllib.request.Request(TOKEN_URL, data=data, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        req.add_header("x-api-key", ETSY_API_KEY)
        with urllib.request.urlopen(req, timeout=30) as resp:
            new_tokens = json.loads(resp.read().decode())
        with open(TOKEN_FILE, "w") as f:
            json.dump(new_tokens, f, indent=2)
        print("  Token refreshed successfully")
        return new_tokens
    except Exception:
        return None


# ── Etsy API Helpers ──────────────────────────────────────────────────────────


def etsy_get(endpoint, access_token):
    req = urllib.request.Request(f"{ETSY_BASE}{endpoint}")
    req.add_header("x-api-key", ETSY_API_KEY)
    req.add_header("Authorization", f"Bearer {access_token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def etsy_post_form(endpoint, access_token, fields):
    data = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(f"{ETSY_BASE}{endpoint}", data=data, method="POST")
    req.add_header("x-api-key", ETSY_API_KEY)
    req.add_header("Authorization", f"Bearer {access_token}")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def etsy_patch_form(endpoint, access_token, fields):
    data = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(f"{ETSY_BASE}{endpoint}", data=data, method="PATCH")
    req.add_header("x-api-key", ETSY_API_KEY)
    req.add_header("Authorization", f"Bearer {access_token}")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def upload_image(shop_id, listing_id, access_token, image_path, rank):
    """Upload a listing image via multipart/form-data."""
    boundary = f"----EtsyBoundary{int(time.time() * 1000)}"
    filename = os.path.basename(image_path)

    with open(image_path, "rb") as f:
        image_data = f.read()

    body = bytearray()
    body += f"--{boundary}\r\n".encode()
    body += b'Content-Disposition: form-data; name="rank"\r\n\r\n'
    body += f"{rank}\r\n".encode()
    body += f"--{boundary}\r\n".encode()
    body += f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'.encode()
    body += b"Content-Type: image/png\r\n\r\n"
    body += image_data
    body += b"\r\n"
    body += f"--{boundary}--\r\n".encode()

    url = f"{ETSY_BASE}/shops/{shop_id}/listings/{listing_id}/images"
    req = urllib.request.Request(url, data=bytes(body), method="POST")
    req.add_header("x-api-key", ETSY_API_KEY)
    req.add_header("Authorization", f"Bearer {access_token}")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")

    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())


def upload_digital_file(shop_id, listing_id, access_token, file_path):
    """Upload the digital delivery file (ZIP)."""
    boundary = f"----EtsyFileBoundary{int(time.time() * 1000)}"
    filename = os.path.basename(file_path)

    with open(file_path, "rb") as f:
        file_data = f.read()

    body = bytearray()
    body += f"--{boundary}\r\n".encode()
    body += b'Content-Disposition: form-data; name="name"\r\n\r\n'
    body += f"{filename}\r\n".encode()
    body += f"--{boundary}\r\n".encode()
    body += f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode()
    body += b"Content-Type: application/zip\r\n\r\n"
    body += file_data
    body += b"\r\n"
    body += f"--{boundary}--\r\n".encode()

    url = f"{ETSY_BASE}/shops/{shop_id}/listings/{listing_id}/files"
    req = urllib.request.Request(url, data=bytes(body), method="POST")
    req.add_header("x-api-key", ETSY_API_KEY)
    req.add_header("Authorization", f"Bearer {access_token}")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")

    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())


# ── Main ──────────────────────────────────────────────────────────────────────


def main():
    print("")
    print("=" * 56)
    print("  PURPLEOCAZ — Botanical SVG Bundle Publisher")
    print("  120+ Fine-Line Botanical Tattoo Designs")
    print("=" * 56)

    # ── Step 0: Check files ──
    print("\nSTEP 0: Checking files...")

    missing = []
    for img in IMAGE_FILES:
        p = os.path.join(THUMBNAILS_DIR, img)
        if not os.path.exists(p):
            missing.append(img)
    if not os.path.exists(DELIVERY_ZIP):
        missing.append("DELIVERY ZIP")

    if missing:
        print(f"  MISSING FILES: {', '.join(missing)}")
        print("  Run the thumbnail renderer first, then try again.")
        sys.exit(1)

    zip_size = os.path.getsize(DELIVERY_ZIP) / 1024
    print(f"  Images: {len(IMAGE_FILES)} PNGs in {THUMBNAILS_DIR}")
    print(f"  ZIP:    {os.path.basename(DELIVERY_ZIP)} ({zip_size:.0f}KB)")
    print("  All files found!")

    # ── Step 1: Authenticate ──
    print("\nSTEP 1: Authenticating with Etsy...")

    tokens = load_or_refresh_tokens()
    if tokens:
        print("  Existing tokens are valid")
    else:
        print("  No valid tokens found — starting OAuth flow...")
        tokens = authenticate()

    access_token = tokens["access_token"]

    # ── Step 2: Get shop ──
    print("\nSTEP 2: Getting shop details...")

    me = etsy_get("/users/me", access_token)
    user_id = me["user_id"]

    shop_resp = etsy_get(f"/users/{user_id}/shops", access_token)
    shop_id = shop_resp.get("shop_id") or shop_resp.get("results", [{}])[0].get("shop_id")
    shop_name = shop_resp.get("shop_name") or shop_resp.get("results", [{}])[0].get("shop_name")

    if not shop_id:
        # Fall back to env
        shop_id = ETSY_SHOP_ID
        shop_name = "(from .env)"

    print(f"  Shop: {shop_name} (ID: {shop_id})")

    # ── Step 3: Create draft listing ──
    print("\nSTEP 3: Creating draft listing...")

    tags = [t[:20] for t in LISTING["tags"][:13]]

    form_fields = [
        ("quantity", str(LISTING["quantity"])),
        ("title", LISTING["title"][:140]),
        ("description", LISTING["description"]),
        ("price", str(LISTING["price"])),
        ("who_made", LISTING["who_made"]),
        ("when_made", LISTING["when_made"]),
        ("taxonomy_id", str(LISTING["taxonomy_id"])),
        ("type", "download"),
        ("is_supply", "false"),
        ("tags", ",".join(tags)),
    ]

    try:
        listing_resp = etsy_post_form(
            f"/shops/{shop_id}/listings", access_token, form_fields
        )
        listing_id = listing_resp["listing_id"]
        print(f"  Draft created! Listing ID: {listing_id}")
        print(f"  Status: {listing_resp.get('state', 'draft')}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"  FAILED ({e.code}): {body[:500]}")
        sys.exit(1)

    # ── Step 4: Upload images ──
    print("\nSTEP 4: Uploading listing images...")

    for i, img_file in enumerate(IMAGE_FILES):
        rank = i + 1
        img_path = os.path.join(THUMBNAILS_DIR, img_file)
        print(f"  [{rank}/7] {img_file}...", end=" ", flush=True)

        try:
            result = upload_image(shop_id, listing_id, access_token, img_path, rank)
            if result.get("listing_image_id"):
                print(f"OK (ID: {result['listing_image_id']})")
            else:
                print(f"Warning: {json.dumps(result)[:100]}")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            print(f"FAILED ({e.code}): {body[:100]}")

        time.sleep(0.3)

    # ── Step 5: Upload digital file ──
    print("\nSTEP 5: Uploading digital delivery file...")
    print(f"  {os.path.basename(DELIVERY_ZIP)} ({zip_size:.0f}KB)")

    try:
        file_result = upload_digital_file(
            shop_id, listing_id, access_token, DELIVERY_ZIP
        )
        if file_result.get("listing_file_id"):
            print(f"  Uploaded! File ID: {file_result['listing_file_id']}")
        else:
            print(f"  Warning: {json.dumps(file_result)[:200]}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"  FAILED ({e.code}): {body[:200]}")

    # ── Step 6: Activate digital delivery ──
    print("\nSTEP 6: Activating digital delivery...")

    try:
        patch_result = etsy_patch_form(
            f"/shops/{shop_id}/listings/{listing_id}",
            access_token,
            {"type": "download"},
        )
        print(f"  Digital delivery activated (state: {patch_result.get('state', '?')})")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"  Warning ({e.code}): {body[:200]}")

    # ── Done ──
    print("\n" + "=" * 56)
    print("  LISTING CREATED SUCCESSFULLY!")
    print("=" * 56)
    print(f"""
  Listing ID:  {listing_id}
  Title:       {LISTING['title'][:60]}...
  Price:       £{LISTING['price']:.2f}
  Images:      {len(IMAGE_FILES)} uploaded
  Digital:     {os.path.basename(DELIVERY_ZIP)}

  The listing is in DRAFT status.
  Go to: Etsy Shop Manager → Listings → Drafts
  Review it and click PUBLISH when ready.

  Direct URL: https://www.etsy.com/listing/{listing_id}
""")


if __name__ == "__main__":
    main()
