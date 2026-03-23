#!/usr/bin/env python3
"""Upload 7 images to each of 4 car detailing Etsy listings.
Deletes existing images first, uploads in rank order, verifies with GET.
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
import urllib.parse

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT)

from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT, ".env"))

TOKEN_FILE = os.path.join(PROJECT, "workflows", "etsy_analytics", "etsy_tokens.json")
ETSY_BASE = "https://openapi.etsy.com/v3/application"

API_KEYSTRING = os.getenv("ETSY_API_KEYSTRING", "")
SHARED_SECRET = os.getenv("ETSY_SHARED_SECRET", "")
SHOP_ID = os.getenv("ETSY_SHOP_ID", "")
X_API_KEY = f"{API_KEYSTRING}:{SHARED_SECRET}"

THUMBS = os.path.join(PROJECT, "thumbnails", "car-detail")


def load_tokens():
    with open(TOKEN_FILE) as f:
        return json.load(f)


def refresh_token(tokens):
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "client_id": API_KEYSTRING,
        "refresh_token": tokens["refresh_token"],
    }).encode()
    req = urllib.request.Request(
        "https://api.etsy.com/v3/public/oauth/token",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    resp = urllib.request.urlopen(req)
    new_tokens = json.loads(resp.read())
    with open(TOKEN_FILE, "w") as f:
        json.dump(new_tokens, f, indent=2)
    print(f"  Token refreshed")
    return new_tokens


def etsy_get(endpoint, tokens):
    url = f"{ETSY_BASE}{endpoint}"
    req = urllib.request.Request(url, method="GET")
    req.add_header("x-api-key", X_API_KEY)
    req.add_header("Authorization", f"Bearer {tokens['access_token']}")
    try:
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code == 401:
            tokens.update(refresh_token(tokens))
            req.remove_header("Authorization")
            req.add_header("Authorization", f"Bearer {tokens['access_token']}")
            resp = urllib.request.urlopen(req)
            return json.loads(resp.read())
        body = e.read().decode()
        print(f"  GET {endpoint} -> {e.code}: {body[:200]}")
        return None


def etsy_delete(endpoint, tokens):
    url = f"{ETSY_BASE}{endpoint}"
    req = urllib.request.Request(url, method="DELETE")
    req.add_header("x-api-key", X_API_KEY)
    req.add_header("Authorization", f"Bearer {tokens['access_token']}")
    try:
        resp = urllib.request.urlopen(req)
        return True
    except urllib.error.HTTPError as e:
        if e.code == 401:
            tokens.update(refresh_token(tokens))
            req.remove_header("Authorization")
            req.add_header("Authorization", f"Bearer {tokens['access_token']}")
            resp = urllib.request.urlopen(req)
            return True
        print(f"  DELETE error {e.code}: {e.read().decode()[:200]}")
        return False


def upload_image(tokens, listing_id, image_path, rank):
    boundary = "----PurpleOcazImgBoundary"
    filename = os.path.basename(image_path)

    with open(image_path, "rb") as f:
        file_data = f.read()

    body = bytearray()
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(f'Content-Disposition: form-data; name="rank"\r\n\r\n{rank}\r\n'.encode())
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'.encode())
    body.extend(b"Content-Type: image/png\r\n\r\n")
    body.extend(file_data)
    body.extend(b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode())

    url = f"{ETSY_BASE}/shops/{SHOP_ID}/listings/{listing_id}/images"
    req = urllib.request.Request(url, data=bytes(body), method="POST")
    req.add_header("x-api-key", X_API_KEY)
    req.add_header("Authorization", f"Bearer {tokens['access_token']}")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")

    try:
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read())
        print(f"    Rank {rank}: {filename} -> image_id={result.get('listing_image_id', '?')}")
        return result
    except urllib.error.HTTPError as e:
        if e.code == 401:
            tokens.update(refresh_token(tokens))
            req.remove_header("Authorization")
            req.add_header("Authorization", f"Bearer {tokens['access_token']}")
            resp = urllib.request.urlopen(req)
            result = json.loads(resp.read())
            print(f"    Rank {rank}: {filename} -> image_id={result.get('listing_image_id', '?')}")
            return result
        print(f"    Upload error rank {rank}: {e.code} {e.read().decode()[:200]}")
        return None


def delete_existing_images(tokens, listing_id):
    """Delete all existing images from a listing."""
    result = etsy_get(f"/listings/{listing_id}/images", tokens)
    if not result:
        return
    images = result.get("results", [])
    if not images:
        print("  No existing images to delete")
        return
    print(f"  Deleting {len(images)} existing image(s)...")
    for img in images:
        img_id = img.get("listing_image_id")
        if img_id:
            ok = etsy_delete(f"/shops/{SHOP_ID}/listings/{listing_id}/images/{img_id}", tokens)
            if ok:
                print(f"    Deleted image {img_id}")
            time.sleep(0.5)


def verify_images(tokens, listing_id):
    """Verify listing has expected images."""
    result = etsy_get(f"/listings/{listing_id}/images", tokens)
    if not result:
        return 0
    images = result.get("results", [])
    print(f"  VERIFIED: {len(images)} images on listing {listing_id}")
    for img in images:
        print(f"    rank={img.get('rank', '?')} id={img.get('listing_image_id', '?')}")
    return len(images)


# Image files in rank order
RANK_FILES = [
    "rank1_hero.png",
    "rank2_whats_inside.png",
    "rank3_lifestyle.png",
    "rank4_how_it_works.png",
    "rank5_why_buy.png",
    "rank6_canva_basics.png",
    "rank7_please_note.png",
]

LISTINGS = {
    "forms_bundle": 4476619120,
    "visual_bundle": 4476619282,
    "flyer_pack": 4476619330,
    "starter_bundle": 4476610441,
}


if __name__ == "__main__":
    os.chdir(PROJECT)
    tokens = load_tokens()
    tokens = refresh_token(tokens)

    results = {}

    for slug, listing_id in LISTINGS.items():
        print(f"\n{'='*60}")
        print(f"  {slug.upper()} — Listing #{listing_id}")
        print(f"{'='*60}")

        # Step 1: Delete existing images
        delete_existing_images(tokens, listing_id)
        time.sleep(1)

        # Step 2: Upload 7 new images
        print(f"  Uploading 7 images...")
        for rank, fname in enumerate(RANK_FILES, 1):
            path = os.path.join(THUMBS, slug, fname)
            if not os.path.exists(path):
                print(f"    SKIP: {fname} not found")
                continue
            upload_image(tokens, listing_id, path, rank)
            time.sleep(1)  # Rate limit

        # Step 3: Verify
        time.sleep(2)
        count = verify_images(tokens, listing_id)
        results[slug] = {"listing_id": listing_id, "images": count}

    # Summary
    print(f"\n{'='*60}")
    print("  FINAL SUMMARY")
    print(f"{'='*60}")
    all_good = True
    for slug, data in results.items():
        status = "OK" if data["images"] == 7 else "FAIL"
        if data["images"] != 7:
            all_good = False
        print(f"  {slug}: #{data['listing_id']} | {data['images']}/7 images | {status}")

    if all_good:
        print("\n  ALL 4 LISTINGS VERIFIED WITH 7 IMAGES EACH")
    else:
        print("\n  WARNING: Some listings have missing images")
        sys.exit(1)
