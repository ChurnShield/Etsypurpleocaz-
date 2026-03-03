#!/usr/bin/env python3
"""
Self-contained Etsy listing publisher for GitHub Actions.
Handles: OAuth token exchange -> Create draft -> Upload images -> Upload ZIP.
No external dependencies beyond stdlib + requests.
"""

import hashlib
import json
import os
import sys
import time
import urllib.request
import urllib.error
import urllib.parse

ETSY_BASE = "https://openapi.etsy.com/v3/application"
ETSY_TOKEN_URL = "https://api.etsy.com/v3/public/oauth/token"

# Paths relative to repo root
LISTING_JSON = "workflows/auto_listing_creator/exports/svg_bundles/listing_content.json"
THUMBNAILS_DIR = "workflows/auto_listing_creator/exports/svg_bundles/thumbnail_preview"
ZIP_FILE = "workflows/auto_listing_creator/exports/svg_bundles/delivery/120-Botanical-SVG-Bundle-PurpleOcaz.zip"


def log(msg):
    print(f"[publish] {msg}", flush=True)


def exchange_auth_code(api_keystring, auth_code, code_verifier, redirect_uri):
    """Exchange OAuth auth code for access + refresh tokens."""
    data = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "client_id": api_keystring,
        "redirect_uri": redirect_uri,
        "code": auth_code,
        "code_verifier": code_verifier,
    }).encode("utf-8")

    req = urllib.request.Request(ETSY_TOKEN_URL, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            tokens = json.loads(resp.read().decode("utf-8"))
        log(f"Token exchange successful. Token type: {tokens.get('token_type')}")
        return tokens
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        log(f"Token exchange FAILED ({e.code}): {body[:500]}")
        sys.exit(1)


def create_draft_listing(api_key, shop_id, access_token, listing_data):
    """Create a draft listing on Etsy."""
    tags = [t[:20] for t in listing_data.get("tags", [])[:13] if t.strip()]

    form_fields = [
        ("quantity", "999"),
        ("title", listing_data["title"][:140]),
        ("description", listing_data.get("description", "")),
        ("price", str(listing_data.get("price", 4.99))),
        ("who_made", "i_did"),
        ("when_made", "2020_2025"),
        ("taxonomy_id", str(listing_data.get("taxonomy_id", 2078))),
        ("type", "download"),
        ("is_supply", "false"),
    ]
    if tags:
        form_fields.append(("tags", ",".join(tags)))

    data = urllib.parse.urlencode(form_fields).encode("utf-8")
    url = f"{ETSY_BASE}/shops/{shop_id}/listings"

    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("x-api-key", api_key)
    req.add_header("Authorization", f"Bearer {access_token}")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("Accept", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        listing_id = result.get("listing_id")
        log(f"Draft listing created! ID: {listing_id}")
        return listing_id
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        log(f"Create draft FAILED ({e.code}): {body[:500]}")
        sys.exit(1)


def upload_image(api_key, shop_id, listing_id, access_token, image_path, rank=1):
    """Upload a listing image via multipart/form-data."""
    boundary = f"----EtsyBoundary{int(time.time() * 1000)}{rank}"
    filename = os.path.basename(image_path)

    with open(image_path, "rb") as f:
        image_data = f.read()

    body = bytearray()
    body += f"--{boundary}\r\n".encode()
    body += b"Content-Disposition: form-data; name=\"rank\"\r\n\r\n"
    body += f"{rank}\r\n".encode()
    body += f"--{boundary}\r\n".encode()
    body += f"Content-Disposition: form-data; name=\"image\"; filename=\"{filename}\"\r\n".encode()
    body += b"Content-Type: image/png\r\n\r\n"
    body += image_data
    body += b"\r\n"
    body += f"--{boundary}--\r\n".encode()

    url = f"{ETSY_BASE}/shops/{shop_id}/listings/{listing_id}/images"
    req = urllib.request.Request(url, data=bytes(body), method="POST")
    req.add_header("x-api-key", api_key)
    req.add_header("Authorization", f"Bearer {access_token}")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    req.add_header("Accept", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            json.loads(resp.read().decode("utf-8"))
        log(f"  Image {rank}: {filename} uploaded")
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        log(f"  Image {rank} FAILED ({e.code}): {body_text[:200]}")


def upload_digital_file(api_key, shop_id, listing_id, access_token, file_path):
    """Upload the digital download file (ZIP)."""
    boundary = f"----EtsyFileBoundary{int(time.time() * 1000)}"
    filename = os.path.basename(file_path)

    with open(file_path, "rb") as f:
        file_data = f.read()

    body = bytearray()
    body += f"--{boundary}\r\n".encode()
    body += b"Content-Disposition: form-data; name=\"name\"\r\n\r\n"
    body += f"{filename}\r\n".encode()
    body += f"--{boundary}\r\n".encode()
    body += f"Content-Disposition: form-data; name=\"file\"; filename=\"{filename}\"\r\n".encode()
    body += b"Content-Type: application/zip\r\n\r\n"
    body += file_data
    body += b"\r\n"
    body += f"--{boundary}--\r\n".encode()

    url = f"{ETSY_BASE}/shops/{shop_id}/listings/{listing_id}/files"
    req = urllib.request.Request(url, data=bytes(body), method="POST")
    req.add_header("x-api-key", api_key)
    req.add_header("Authorization", f"Bearer {access_token}")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    req.add_header("Accept", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            json.loads(resp.read().decode("utf-8"))
        log(f"  Digital file uploaded: {filename}")
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        log(f"  Digital file FAILED ({e.code}): {body_text[:200]}")


def activate_digital_delivery(api_key, shop_id, listing_id, access_token):
    """PATCH listing to activate digital delivery."""
    data = urllib.parse.urlencode({"type": "download"}).encode("utf-8")
    url = f"{ETSY_BASE}/shops/{shop_id}/listings/{listing_id}"

    req = urllib.request.Request(url, data=data, method="PATCH")
    req.add_header("x-api-key", api_key)
    req.add_header("Authorization", f"Bearer {access_token}")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("Accept", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            json.loads(resp.read().decode("utf-8"))
        log("  Digital delivery activated")
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        log(f"  Activate digital delivery FAILED ({e.code}): {body_text[:200]}")


def main():
    # Read config from environment (set by GitHub Secrets)
    api_keystring = os.environ.get("ETSY_API_KEYSTRING", "")
    shared_secret = os.environ.get("ETSY_SHARED_SECRET", "")
    shop_id = os.environ.get("ETSY_SHOP_ID", "")
    auth_code = os.environ.get("AUTH_CODE", "")
    code_verifier = os.environ.get("CODE_VERIFIER", "")
    redirect_uri = "http://localhost:3847/callback"

    api_key = f"{api_keystring}:{shared_secret}"

    if not all([api_keystring, shared_secret, shop_id, auth_code, code_verifier]):
        log("ERROR: Missing required environment variables")
        log(f"  ETSY_API_KEYSTRING: {'set' if api_keystring else 'MISSING'}")
        log(f"  ETSY_SHARED_SECRET: {'set' if shared_secret else 'MISSING'}")
        log(f"  ETSY_SHOP_ID: {'set' if shop_id else 'MISSING'}")
        log(f"  AUTH_CODE: {'set' if auth_code else 'MISSING'}")
        log(f"  CODE_VERIFIER: {'set' if code_verifier else 'MISSING'}")
        sys.exit(1)

    # Step 1: Exchange auth code for tokens
    log("Step 1: Exchanging auth code for access token...")
    tokens = exchange_auth_code(api_keystring, auth_code, code_verifier, redirect_uri)
    access_token = tokens["access_token"]

    # Step 2: Load listing content
    log("Step 2: Loading listing content...")
    with open(LISTING_JSON) as f:
        listing_data = json.load(f)
    log(f"  Title: {listing_data['title'][:60]}...")

    # Step 3: Create draft listing
    log("Step 3: Creating draft listing on Etsy...")
    listing_id = create_draft_listing(api_key, shop_id, access_token, listing_data)

    # Step 4: Upload thumbnail images
    log("Step 4: Uploading listing images...")
    if os.path.isdir(THUMBNAILS_DIR):
        pngs = sorted([f for f in os.listdir(THUMBNAILS_DIR) if f.endswith(".png")])
        for rank, png in enumerate(pngs, start=1):
            img_path = os.path.join(THUMBNAILS_DIR, png)
            upload_image(api_key, shop_id, listing_id, access_token, img_path, rank)
            time.sleep(0.5)
    else:
        log("  No thumbnails directory found, skipping images")

    # Step 5: Upload digital file (ZIP)
    log("Step 5: Uploading digital download file...")
    if os.path.exists(ZIP_FILE):
        upload_digital_file(api_key, shop_id, listing_id, access_token, ZIP_FILE)
        time.sleep(0.5)
        activate_digital_delivery(api_key, shop_id, listing_id, access_token)
    else:
        log(f"  ZIP file not found at {ZIP_FILE}, skipping")

    # Done
    log("=" * 60)
    log(f"DONE! Draft listing ID: {listing_id}")
    log(f"View it: https://www.etsy.com/your/shops/me/listing-editor/retail/{listing_id}")
    log("The listing is saved as DRAFT — review and publish from Etsy Shop Manager.")
    log("=" * 60)

    # Save tokens for future use
    tokens_path = "etsy_tokens.json"
    with open(tokens_path, "w") as f:
        json.dump(tokens, f, indent=2)
    log(f"Tokens saved to {tokens_path} (use for future API calls)")


if __name__ == "__main__":
    main()
