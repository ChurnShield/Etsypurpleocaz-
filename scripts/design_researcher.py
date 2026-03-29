#!/usr/bin/env python3
"""
design_researcher.py — Visual analysis of top Etsy listings to extract design patterns.

Usage:
    python3 scripts/design_researcher.py "yoga studio"
"""

import base64
import json
import os
import re
import sys
import urllib.request
import urllib.error
import urllib.parse

# ── Paths ─────────────────────────────────────────────────────────────────────

ROOT       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN_FILE = os.path.join(ROOT, "workflows", "etsy_analytics", "etsy_tokens.json")
ETSY_BASE  = "https://openapi.etsy.com/v3/application"
OUT_DIR    = os.path.join(ROOT, "outputs", "design_research")
TMP_BASE   = "/tmp/design_research"

# ── Auth (same pattern as niche_evaluator.py) ─────────────────────────────────

def load_credentials():
    from dotenv import load_dotenv
    load_dotenv(os.path.join(ROOT, ".env"))
    keystring = os.getenv("ETSY_API_KEYSTRING", "")
    secret    = os.getenv("ETSY_SHARED_SECRET", "")
    anthropic = os.getenv("ANTHROPIC_API_KEY", "")
    return (f"{keystring}:{secret}" if secret else keystring), anthropic


def load_tokens():
    if not os.path.exists(TOKEN_FILE):
        return None, None
    with open(TOKEN_FILE) as f:
        t = json.load(f)
    return t.get("access_token"), t.get("refresh_token")


def refresh_token(api_key, refresh_tok):
    data = urllib.parse.urlencode({
        "grant_type":    "refresh_token",
        "client_id":     api_key.split(":")[0],
        "refresh_token": refresh_tok,
    }).encode()
    req = urllib.request.Request(
        "https://api.etsy.com/v3/public/oauth/token", data=data, method="POST"
    )
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("x-api-key", api_key)
    with urllib.request.urlopen(req, timeout=15) as r:
        result = json.loads(r.read())
    with open(TOKEN_FILE, "w") as f:
        json.dump(result, f, indent=2)
    return result["access_token"]


def etsy_get(path, api_key, access_token):
    req = urllib.request.Request(f"{ETSY_BASE}{path}")
    req.add_header("x-api-key", api_key)
    req.add_header("Accept", "application/json")
    if access_token:
        req.add_header("Authorization", f"Bearer {access_token}")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        if e.code == 401:
            _, refresh_tok = load_tokens()
            if refresh_tok:
                new_token = refresh_token(api_key, refresh_tok)
                req2 = urllib.request.Request(f"{ETSY_BASE}{path}")
                req2.add_header("x-api-key", api_key)
                req2.add_header("Accept", "application/json")
                req2.add_header("Authorization", f"Bearer {new_token}")
                with urllib.request.urlopen(req2, timeout=20) as r:
                    return json.loads(r.read())
        raise

# ── Etsy steps ────────────────────────────────────────────────────────────────

def search_listings(niche, api_key, access_token):
    query = urllib.parse.quote(f"{niche} template canva bundle")
    path  = f"/listings/active?keywords={query}&sort_on=score&limit=5"
    data  = etsy_get(path, api_key, access_token)
    return data.get("results", [])[:3]


def get_hero_image_url(listing_id, api_key, access_token):
    data   = etsy_get(f"/listings/{listing_id}/images", api_key, access_token)
    images = data.get("results", [])
    if not images:
        return None
    # Prefer full-res; fall back through available keys
    img = images[0]
    for key in ("url_fullxfull", "url_570xN", "url_75x75"):
        if img.get(key):
            return img[key]
    return None


def download_image(url, dest_path):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        with open(dest_path, "wb") as f:
            f.write(r.read())

# ── Vision analysis ───────────────────────────────────────────────────────────

VISION_PROMPT = (
    'Analyse this Etsy template listing image. Return JSON:\n'
    '{\n'
    '  "primary_colour": "#hex",\n'
    '  "secondary_colour": "#hex",\n'
    '  "accent_colour": "#hex",\n'
    '  "background_colour": "#hex",\n'
    '  "heading_font_style": "serif|sans-serif|script",\n'
    '  "body_font_style": "serif|sans-serif",\n'
    '  "layout": "grid|mockup|collage|single",\n'
    '  "white_space": "minimal|moderate|generous",\n'
    '  "quality_score": 1,\n'
    '  "design_notes": "one sentence"\n'
    '}'
)


def analyse_image(image_path, anthropic_key):
    with open(image_path, "rb") as f:
        b64 = base64.standard_b64encode(f.read()).decode()

    ext = os.path.splitext(image_path)[1].lower()
    media_type = "image/png" if ext == ".png" else "image/jpeg"

    payload = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 512,
        "system": "You are a design analyst. Return ONLY valid JSON, no backticks, no preamble.",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}},
                {"type": "text",  "text": VISION_PROMPT},
            ],
        }],
    }).encode()

    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=payload, method="POST")
    req.add_header("x-api-key", anthropic_key)
    req.add_header("anthropic-version", "2023-06-01")
    req.add_header("content-type", "application/json")

    with urllib.request.urlopen(req, timeout=60) as r:
        resp = json.loads(r.read())

    raw = resp["content"][0]["text"].strip()
    # Strip markdown fences if present
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return json.loads(raw)


def text_fallback(listings):
    """Minimal fallback when vision API fails — neutral safe palette."""
    print("  [WARN] Vision API unavailable — using text-based fallback palette")
    titles = [l.get("title", "") for l in listings]
    print(f"  Listings analysed: {titles}")
    return {
        "primary_colour":    "#2D2D2D",
        "secondary_colour":  "#FFFFFF",
        "accent_colour":     "#C9A96E",
        "background_colour": "#F5F0EB",
        "heading_font_style": "sans-serif",
        "body_font_style":    "sans-serif",
        "layout":            "mockup",
        "white_space":       "moderate",
        "quality_score":     5,
        "design_notes":      "Fallback palette — vision API unavailable.",
    }

# ── Output writers ─────────────────────────────────────────────────────────────

def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def save_outputs(slug, niche, winner, listings):
    os.makedirs(OUT_DIR, exist_ok=True)

    config = {
        "palette": {
            "primary":    winner["primary_colour"],
            "secondary":  winner["secondary_colour"],
            "accent":     winner["accent_colour"],
            "background": winner["background_colour"],
        },
        "font_style": {
            "heading": winner["heading_font_style"],
            "body":    winner["body_font_style"],
        },
        "layout":            winner["layout"],
        "reference_quality": winner["quality_score"],
    }

    brief_lines = [
        f"# Design Research Brief — {niche.title()}",
        "",
        f"**Quality score:** {winner['quality_score']}/10",
        f"**Layout:**        {winner['layout']}",
        f"**White space:**   {winner['white_space']}",
        "",
        "## Colour Palette",
        f"- Primary:    {winner['primary_colour']}",
        f"- Secondary:  {winner['secondary_colour']}",
        f"- Accent:     {winner['accent_colour']}",
        f"- Background: {winner['background_colour']}",
        "",
        "## Typography",
        f"- Heading: {winner['heading_font_style']}",
        f"- Body:    {winner['body_font_style']}",
        "",
        "## Design Notes",
        winner["design_notes"],
        "",
        "## Top Listings Analysed",
    ]
    for l in listings:
        brief_lines.append(f"- [{l['listing_id']}] {l.get('title','')[:80]}")

    brief_path  = os.path.join(OUT_DIR, f"{slug}_brief.md")
    config_path = os.path.join(OUT_DIR, f"{slug}_config.json")

    with open(brief_path, "w") as f:
        f.write("\n".join(brief_lines) + "\n")
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    return brief_path, config_path

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/design_researcher.py \"niche name\"")
        sys.exit(1)

    niche = " ".join(sys.argv[1:])
    slug  = slugify(niche)
    tmp_dir = os.path.join(TMP_BASE, slug)
    os.makedirs(tmp_dir, exist_ok=True)

    print(f"\nDesign Research: \"{niche}\"")
    print("=" * 55)

    etsy_key, anthropic_key = load_credentials()
    access_token, _         = load_tokens()

    # 1. Search
    print("  [1/4] Searching Etsy top listings ...", end=" ", flush=True)
    listings = search_listings(niche, etsy_key, access_token)
    print(f"found {len(listings)}")

    # 2+3. Fetch images for top 3
    image_paths = []
    for i, listing in enumerate(listings[:3], 1):
        lid = listing["listing_id"]
        print(f"  [2/4] Listing {i}: {lid} — fetching hero image ...", end=" ", flush=True)
        url = get_hero_image_url(lid, etsy_key, access_token)
        if not url:
            print("no image, skipping")
            continue
        ext  = ".jpg" if "jpg" in url.lower() else ".png"
        dest = os.path.join(tmp_dir, f"listing_{i}{ext}")
        download_image(url, dest)
        image_paths.append((dest, listing))
        print(f"saved ({os.path.getsize(dest)//1024}KB)")

    # 4+5. Vision analysis
    analyses = []
    if anthropic_key and image_paths:
        for i, (img_path, listing) in enumerate(image_paths, 1):
            print(f"  [3/4] Vision analysis {i}/{len(image_paths)} ...", end=" ", flush=True)
            try:
                result = analyse_image(img_path, anthropic_key)
                result["listing_id"] = listing["listing_id"]
                result["title"]      = listing.get("title", "")
                analyses.append(result)
                print(f"quality={result.get('quality_score','?')}/10")
            except Exception as e:
                print(f"FAILED ({e})")

    if not analyses:
        winner = text_fallback(listings)
        winner["listing_id"] = listings[0]["listing_id"] if listings else "unknown"
        winner["title"]      = listings[0].get("title", "") if listings else ""
        analyses = [winner]

    # 6. Pick winner by quality_score
    winner = max(analyses, key=lambda x: x.get("quality_score", 0))
    print(f"  [4/4] Winner: listing {winner['listing_id']} (score {winner.get('quality_score')}/10)")

    # 7. Save outputs
    brief_path, config_path = save_outputs(slug, niche, winner, listings)

    # 8. Print brief
    print()
    with open(brief_path) as f:
        print(f.read())

    print(f"  Brief:  {os.path.relpath(brief_path, ROOT)}")
    print(f"  Config: {os.path.relpath(config_path, ROOT)}")
    print()


if __name__ == "__main__":
    main()
