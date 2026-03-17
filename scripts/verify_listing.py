#!/usr/bin/env python3
"""
verify_listing.py — Post-build listing verification.

Checks a listing ID against all production rules:
  - Images: count and rank order
  - PDF: attached with correct filename
  - Tags: all under 20 chars, no duplicates
  - Price: £2.99
  - State: active or draft
  - PDF links: /d/ format, not /design/

Usage:
    python scripts/verify_listing.py 4472977919
    python scripts/verify_listing.py 4472977919 --shop-id 12345678
"""

import json
import os
import re
import sys
import urllib.request
import urllib.error

# ── Config ──────────────────────────────────────────────────────────────────

TOKEN_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "workflows", "etsy_analytics", "etsy_tokens.json",
)

ETSY_BASE_URL = "https://openapi.etsy.com/v3/application"
EXPECTED_PRICE_GBP = 2.99
MAX_TAG_LENGTH = 20
EXPECTED_IMAGE_COUNT = 3


def load_config():
    """Load Etsy credentials from environment."""
    from dotenv import load_dotenv

    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    load_dotenv(env_path)

    api_keystring = os.getenv("ETSY_API_KEYSTRING", "")
    shared_secret = os.getenv("ETSY_SHARED_SECRET", "")
    shop_id = os.getenv("ETSY_SHOP_ID", "")
    api_key = f"{api_keystring}:{shared_secret}" if shared_secret else api_keystring

    return api_key, shop_id


def load_tokens():
    """Load OAuth tokens from token file."""
    if not os.path.exists(TOKEN_FILE):
        print(f"  WARN: Token file not found: {TOKEN_FILE}")
        return None, None
    with open(TOKEN_FILE, "r") as f:
        tokens = json.load(f)
    return tokens.get("access_token"), tokens.get("refresh_token")


def refresh_access_token(api_key, refresh_token):
    """Refresh the access token using the refresh token."""
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "client_id": api_key.split(":")[0],
        "refresh_token": refresh_token,
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.etsy.com/v3/public/oauth/token",
        data=data,
        method="POST",
    )
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("x-api-key", api_key)

    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    # Save refreshed tokens
    with open(TOKEN_FILE, "w") as f:
        json.dump(result, f, indent=2)

    return result["access_token"]


def api_get(url, api_key, access_token):
    """Make an authenticated GET request to the Etsy API."""
    req = urllib.request.Request(url)
    req.add_header("x-api-key", api_key)
    req.add_header("Accept", "application/json")
    if access_token:
        req.add_header("Authorization", f"Bearer {access_token}")

    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


# ── Checks ──────────────────────────────────────────────────────────────────

class VerificationResult:
    def __init__(self):
        self.checks = []

    def ok(self, label, detail=""):
        self.checks.append(("PASS", label, detail))

    def fail(self, label, detail=""):
        self.checks.append(("FAIL", label, detail))

    def warn(self, label, detail=""):
        self.checks.append(("WARN", label, detail))

    def print_report(self):
        passed = sum(1 for s, _, _ in self.checks if s == "PASS")
        failed = sum(1 for s, _, _ in self.checks if s == "FAIL")
        warned = sum(1 for s, _, _ in self.checks if s == "WARN")

        print("\n" + "=" * 60)
        print("LISTING VERIFICATION REPORT")
        print("=" * 60)

        for status, label, detail in self.checks:
            icon = {"PASS": "+", "FAIL": "X", "WARN": "!"}[status]
            line = f"  [{icon}] {label}"
            if detail:
                line += f" — {detail}"
            print(line)

        print("-" * 60)
        print(f"  {passed} passed, {failed} failed, {warned} warnings")
        if failed > 0:
            print("  RESULT: FAILED — fix issues before publishing")
        elif warned > 0:
            print("  RESULT: PASSED WITH WARNINGS")
        else:
            print("  RESULT: ALL CHECKS PASSED")
        print("=" * 60)

        return failed == 0


def check_listing(listing_data, result):
    """Check listing metadata: state, price, tags."""
    listing = listing_data

    # State
    state = listing.get("state", "unknown")
    result.ok("State", state) if state in ("active", "draft") else result.fail("State", state)

    # Price
    price = listing.get("price", {})
    amount = float(price.get("amount", 0)) / int(price.get("divisor", 100))
    currency = price.get("currency_code", "???")
    if abs(amount - EXPECTED_PRICE_GBP) < 0.01:
        result.ok("Price", f"{currency} {amount:.2f}")
    else:
        result.fail("Price", f"Expected {EXPECTED_PRICE_GBP}, got {currency} {amount:.2f}")

    # Tags
    tags = listing.get("tags", [])
    if not tags:
        result.fail("Tags", "No tags found")
    else:
        long_tags = [t for t in tags if len(t) > MAX_TAG_LENGTH]
        if long_tags:
            result.fail("Tag length", f"{len(long_tags)} tags exceed {MAX_TAG_LENGTH} chars: {long_tags}")
        else:
            result.ok("Tag length", f"All {len(tags)} tags <= {MAX_TAG_LENGTH} chars")

        seen = set()
        dupes = [t for t in tags if t.lower() in seen or seen.add(t.lower())]
        if dupes:
            result.fail("Tag duplicates", f"Duplicates: {dupes}")
        else:
            result.ok("Tag duplicates", "None")

        result.ok("Tag count", str(len(tags))) if len(tags) == 13 else result.warn("Tag count", f"{len(tags)} (expected 13)")


def check_images(images_data, result):
    """Check image count and rank order."""
    images = images_data.get("results", [])
    count = len(images)

    if count >= EXPECTED_IMAGE_COUNT:
        result.ok("Image count", str(count))
    else:
        result.fail("Image count", f"{count} (expected >= {EXPECTED_IMAGE_COUNT})")

    if images:
        ranks = [img.get("rank", 0) for img in images]
        expected_ranks = list(range(1, count + 1))
        if sorted(ranks) == expected_ranks:
            result.ok("Image ranks", f"Sequential 1-{count}")
        else:
            result.warn("Image ranks", f"Ranks: {ranks}")


def check_files(files_data, result):
    """Check digital file attachment."""
    files = files_data.get("results", []) if isinstance(files_data, dict) else []
    count = files_data.get("count", len(files)) if isinstance(files_data, dict) else 0

    if count > 0:
        filenames = [f.get("filename", "unknown") for f in files]
        result.ok("PDF attached", f"{count} file(s): {', '.join(filenames)}")
    else:
        result.fail("PDF attached", "No digital files found")


def check_pdf_links(listing_data, result):
    """Check that description doesn't contain edit links."""
    desc = listing_data.get("description", "")

    edit_links = re.findall(r'canva\.com/design/[^/]+/edit', desc)
    view_links = re.findall(r'canva\.com/design/[^/]+/view', desc)
    safe_links = re.findall(r'canva\.com/d/', desc)

    if edit_links:
        result.fail("Canva links", f"EDIT links found in description: {edit_links}")
    elif view_links:
        result.warn("Canva links", f"/design/.../view links found — should use /d/ shortlinks: {view_links}")
    elif safe_links:
        result.ok("Canva links", f"{len(safe_links)} /d/ shortlinks found")
    else:
        result.ok("Canva links", "No Canva links in description (may be in PDF only)")


# ── Main ────────────────────────────────────────────────────────────────────

def verify(listing_id, shop_id_override=None):
    """Run all verification checks on a listing."""
    api_key, shop_id = load_config()
    if shop_id_override:
        shop_id = shop_id_override

    if not api_key or not shop_id:
        print("ERROR: Missing ETSY_API_KEYSTRING, ETSY_SHARED_SECRET, or ETSY_SHOP_ID in .env")
        sys.exit(1)

    access_token, refresh_token = load_tokens()

    print(f"\nVerifying listing #{listing_id} in shop {shop_id}...")

    # Try API call, refresh token on 401
    def get_with_refresh(url):
        nonlocal access_token
        try:
            return api_get(url, api_key, access_token)
        except urllib.error.HTTPError as e:
            if e.code == 401 and refresh_token:
                print("  Token expired, refreshing...")
                access_token = refresh_access_token(api_key, refresh_token)
                return api_get(url, api_key, access_token)
            raise

    result = VerificationResult()

    try:
        # Fetch listing
        listing = get_with_refresh(f"{ETSY_BASE_URL}/listings/{listing_id}")
        check_listing(listing, result)
        check_pdf_links(listing, result)

        # Fetch images
        images = get_with_refresh(f"{ETSY_BASE_URL}/listings/{listing_id}/images")
        check_images(images, result)

        # Fetch files
        files = get_with_refresh(f"{ETSY_BASE_URL}/shops/{shop_id}/listings/{listing_id}/files")
        check_files(files, result)

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else ""
        result.fail("API call", f"HTTP {e.code}: {body[:200]}")
    except Exception as e:
        result.fail("API call", str(e))

    success = result.print_report()
    return success


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/verify_listing.py <listing_id> [--shop-id <id>]")
        sys.exit(1)

    listing_id = sys.argv[1]
    shop_id_override = None
    if "--shop-id" in sys.argv:
        idx = sys.argv.index("--shop-id")
        if idx + 1 < len(sys.argv):
            shop_id_override = sys.argv[idx + 1]

    success = verify(listing_id, shop_id_override)
    sys.exit(0 if success else 1)
