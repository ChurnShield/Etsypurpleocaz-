#!/usr/bin/env python3
"""Fetch a high-resolution photo from Unsplash for a given niche keyword.

Usage:
    python scripts/fetch_niche_photo.py "tattoo artist studio"
    python scripts/fetch_niche_photo.py "nail salon interior" --count 3
"""

import argparse
import os
import re
import sys

import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

UNSPLASH_ACCESS_KEY = os.getenv('UNSPLASH_ACCESS_KEY')
ASSETS_DIR = os.path.join(os.path.dirname(__file__), '..', 'assets', 'photos')


def slugify(keyword: str) -> str:
    return re.sub(r'[^a-z0-9]+', '_', keyword.lower()).strip('_')


def fetch_photos(keyword: str, count: int = 1) -> list[dict]:
    resp = requests.get(
        'https://api.unsplash.com/search/photos',
        params={'query': keyword, 'per_page': count, 'orientation': 'landscape'},
        headers={'Authorization': f'Client-ID {UNSPLASH_ACCESS_KEY}'},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json().get('results', [])


def download_photo(photo: dict, dest_path: str) -> str:
    raw_url = photo['urls']['raw']
    # Request high-res (4000px wide) but not the full uncompressed file
    url = f"{raw_url}&w=4000&q=85"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, 'wb') as f:
        f.write(resp.content)
    return dest_path


def main():
    if not UNSPLASH_ACCESS_KEY:
        print("ERROR: UNSPLASH_ACCESS_KEY not set in .env", file=sys.stderr)
        sys.exit(1)

    parser = argparse.ArgumentParser(description='Fetch niche photos from Unsplash')
    parser.add_argument('keyword', help='Search keyword (e.g. "tattoo artist studio")')
    parser.add_argument('--count', type=int, default=1, help='Number of photos to fetch (default: 1)')
    args = parser.parse_args()

    slug = slugify(args.keyword)
    niche_dir = os.path.join(ASSETS_DIR, slug)

    # Check cache first — skip API call entirely if all photos exist
    needed = []
    for i in range(1, args.count + 1):
        dest = os.path.join(niche_dir, f'photo_{i}.jpg')
        if os.path.exists(dest):
            print(f"CACHED: {dest} already exists, skipping download")
        else:
            needed.append(i)

    if not needed:
        return

    results = fetch_photos(args.keyword, args.count)
    if not results:
        print(f"No photos found for '{args.keyword}'", file=sys.stderr)
        sys.exit(1)

    for i, photo in enumerate(results, 1):
        if i not in needed:
            continue
        dest = os.path.join(niche_dir, f'photo_{i}.jpg')
        path = download_photo(photo, dest)
        photographer = photo.get('user', {}).get('name', 'Unknown')
        print(f"SAVED: {path} (by {photographer}, {photo['width']}x{photo['height']})")


if __name__ == '__main__':
    main()
