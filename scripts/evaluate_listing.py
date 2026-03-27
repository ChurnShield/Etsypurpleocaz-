#!/usr/bin/env python3
"""
evaluate_listing.py — Catches problems verify_listing.py misses.

Checks:
  1. Duplicate images   — perceptual hash, flags pairs with hamming distance < 5
  2. Hero image quality — text-only hero detection, min dimension check
  3. Variant coverage   — detects all-dark or all-light listing image sets

Usage:
    python scripts/evaluate_listing.py 4478726787
    python scripts/evaluate_listing.py 4478726787 --bundle

Exit code 0 = all pass, 1 = any fail.
Report saved to outputs/evaluations/{listing_id}_eval.md
"""

import io
import json
import os
import sys
import urllib.request
import urllib.error
from collections import Counter
from pathlib import Path

import imagehash
from PIL import Image

# ── Config ───────────────────────────────────────────────────────────────────

TOKEN_FILE = Path(__file__).parent.parent / "workflows/etsy_analytics/etsy_tokens.json"
ETSY_BASE = "https://openapi.etsy.com/v3/application"
DUPE_HAMMING_THRESHOLD = 5     # hash distance below this = duplicate
HERO_MIN_DIMENSION    = 2000   # px — shortest side
HERO_MONO_THRESHOLD   = 0.70   # >70% near-black/white = text-only hero
MONO_TOLERANCE        = 40     # channel distance from 0 or 255 to count as near-mono
PALETTE_DARK_CUTOFF   = 128    # average R+G+B below this = "dark" image


# ── Auth helpers (mirrors verify_listing.py) ─────────────────────────────────

def _load_auth():
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
    ks = os.getenv("ETSY_API_KEYSTRING", "")
    ss = os.getenv("ETSY_SHARED_SECRET", "")
    return f"{ks}:{ss}" if ss else ks


def _load_token():
    if TOKEN_FILE.exists():
        return json.loads(TOKEN_FILE.read_text()).get("access_token")
    return None


def _get(url, api_key, token):
    req = urllib.request.Request(url)
    req.add_header("x-api-key", api_key)
    req.add_header("Accept", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def _fetch_image(url: str) -> Image.Image:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return Image.open(io.BytesIO(r.read())).convert("RGB")


# ── Result collector ──────────────────────────────────────────────────────────

class EvalResult:
    def __init__(self):
        self.checks = []

    def ok(self, label, detail=""):   self.checks.append(("PASS", label, detail))
    def fail(self, label, detail=""): self.checks.append(("FAIL", label, detail))
    def warn(self, label, detail=""): self.checks.append(("WARN", label, detail))

    def passed(self): return all(s != "FAIL" for s, _, _ in self.checks)

    def render(self, listing_id: str) -> str:
        lines = [f"# Evaluation Report — Listing #{listing_id}\n"]
        for status, label, detail in self.checks:
            icon = {"PASS": "+", "FAIL": "X", "WARN": "!"}[status]
            lines.append(f"- [{icon}] **{label}**" + (f" — {detail}" if detail else ""))
        n_fail = sum(1 for s, _, _ in self.checks if s == "FAIL")
        n_warn = sum(1 for s, _, _ in self.checks if s == "WARN")
        n_pass = sum(1 for s, _, _ in self.checks if s == "PASS")
        lines.append(f"\n**{n_pass} passed, {n_fail} failed, {n_warn} warnings**")
        lines.append("RESULT: " + ("ALL CHECKS PASSED" if self.passed() else "FAILED — fix before publishing"))
        return "\n".join(lines)

    def print_report(self, listing_id: str):
        print("\n" + "=" * 60)
        print("EVALUATION REPORT (evaluate_listing.py)")
        print("=" * 60)
        for status, label, detail in self.checks:
            icon = {"PASS": "+", "FAIL": "X", "WARN": "!"}[status]
            line = f"  [{icon}] {label}"
            if detail:
                line += f" — {detail}"
            print(line)
        n_fail = sum(1 for s, _, _ in self.checks if s == "FAIL")
        n_warn = sum(1 for s, _, _ in self.checks if s == "WARN")
        n_pass = sum(1 for s, _, _ in self.checks if s == "PASS")
        print("-" * 60)
        print(f"  {n_pass} passed, {n_fail} failed, {n_warn} warnings")
        print("  RESULT:", "ALL CHECKS PASSED" if self.passed() else "FAILED — fix before publishing")
        print("=" * 60)


# ── Checks ────────────────────────────────────────────────────────────────────

def check_duplicates(images: list, result: EvalResult):
    """Perceptual hash every image; flag pairs with hamming distance < threshold."""
    hashes = []
    for img_meta in images:
        url = img_meta.get("url_fullxfull") or img_meta.get("url_570xN", "")
        rank = img_meta.get("rank", "?")
        try:
            img = _fetch_image(url)
            h = imagehash.phash(img)
            hashes.append((rank, h))
        except Exception as e:
            result.warn(f"Duplicate check rank {rank}", f"Could not fetch image: {e}")

    dupes = []
    for i in range(len(hashes)):
        for j in range(i + 1, len(hashes)):
            r1, h1 = hashes[i]
            r2, h2 = hashes[j]
            dist = h1 - h2
            if dist < DUPE_HAMMING_THRESHOLD:
                dupes.append(f"rank {r1} and rank {r2} (distance {dist})")

    if dupes:
        result.fail("Duplicate images", "; ".join(dupes))
    else:
        result.ok("Duplicate images", f"All {len(hashes)} images are visually distinct")


def check_hero_quality(images: list, result: EvalResult):
    """Analyse rank 1: min dimension + text-only detection."""
    hero_meta = next((i for i in images if i.get("rank") == 1), None)
    if not hero_meta:
        result.fail("Hero quality", "No rank 1 image found")
        return

    url = hero_meta.get("url_fullxfull") or hero_meta.get("url_570xN", "")
    try:
        img = _fetch_image(url)
    except Exception as e:
        result.fail("Hero quality", f"Could not fetch hero: {e}")
        return

    w, h = img.size
    shortest = min(w, h)
    if shortest < HERO_MIN_DIMENSION:
        result.fail("Hero dimensions", f"{w}×{h}px — shortest side {shortest}px < {HERO_MIN_DIMENSION}px minimum")
    else:
        result.ok("Hero dimensions", f"{w}×{h}px")

    # Text-only detection: count pixels near pure black or pure white
    pixels = list(img.getdata())
    total = len(pixels)
    mono = sum(
        1 for r, g, b in pixels
        if (r < MONO_TOLERANCE and g < MONO_TOLERANCE and b < MONO_TOLERANCE)
        or (r > 255 - MONO_TOLERANCE and g > 255 - MONO_TOLERANCE and b > 255 - MONO_TOLERANCE)
    )
    mono_pct = mono / total
    if mono_pct > HERO_MONO_THRESHOLD:
        result.fail("Hero content", f"{mono_pct:.0%} pixels near black/white — likely text-only hero, consider product mockup")
    else:
        result.ok("Hero content", f"{mono_pct:.0%} near-mono pixels — looks like a product image")


def check_variant_coverage(images: list, result: EvalResult):
    """Compute average brightness per image; flag if all images share the same tone."""
    dark_count = 0
    light_count = 0
    total = 0

    for img_meta in images:
        url = img_meta.get("url_fullxfull") or img_meta.get("url_570xN", "")
        rank = img_meta.get("rank", "?")
        try:
            img = _fetch_image(url).resize((64, 64))  # thumbnail for speed
            pixels = list(img.getdata())  # noqa: PIL compat
            avg = sum(r + g + b for r, g, b in pixels) / (len(pixels) * 3)
            if avg < PALETTE_DARK_CUTOFF:
                dark_count += 1
            else:
                light_count += 1
            total += 1
        except Exception:
            pass  # already warned in dupe check

    if total == 0:
        result.warn("Variant coverage", "Could not analyse any images")
        return

    if dark_count == total:
        result.fail("Variant coverage", f"All {total} images use a dark palette — light variant may be missing")
    elif light_count == total:
        result.warn("Variant coverage", f"All {total} images use a light palette — dark variant may be missing")
    else:
        result.ok("Variant coverage", f"{dark_count} dark, {light_count} light images — good mix")


# ── Main ──────────────────────────────────────────────────────────────────────

def evaluate(listing_id: str):
    api_key = _load_auth()
    token   = _load_token()
    result  = EvalResult()

    print(f"\nEvaluating listing #{listing_id}...")

    try:
        images_data = _get(f"{ETSY_BASE}/listings/{listing_id}/images", api_key, token)
        images = images_data.get("results", [])
        if not images:
            result.fail("Images", "No images returned from API")
        else:
            print(f"  Fetching {len(images)} images for analysis...")
            check_duplicates(images, result)
            check_hero_quality(images, result)
            check_variant_coverage(images, result)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else ""
        result.fail("API", f"HTTP {e.code}: {body[:200]}")
    except Exception as e:
        result.fail("API", str(e))

    result.print_report(listing_id)

    out_dir = Path(__file__).parent.parent / "outputs" / "evaluations"
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / f"{listing_id}_eval.md"
    report_path.write_text(result.render(listing_id))
    print(f"\n  Report saved → {report_path}")

    return result.passed()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/evaluate_listing.py <listing_id>")
        sys.exit(1)
    ok = evaluate(sys.argv[1])
    sys.exit(0 if ok else 1)
