#!/usr/bin/env python3
"""
niche_evaluator.py — Score a niche idea 0-100 for build priority.

Usage:
    python3 scripts/niche_evaluator.py "wedding planner"
    python3 scripts/niche_evaluator.py "planner templates"
"""

import json
import os
import re
import sys
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timezone

# ── Paths ────────────────────────────────────────────────────────────────────

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN_FILE = os.path.join(ROOT, "workflows", "etsy_analytics", "etsy_tokens.json")
NICHES_DIR = os.path.join(ROOT, "configs", "niches")
EVALS_DIR = os.path.join(ROOT, "outputs", "evaluations")
IDEAS_FILE = os.path.join(ROOT, "ideas_backlog.md")
ETSY_BASE = "https://openapi.etsy.com/v3/application"

# ── Auth helpers (same pattern as verify_listing.py) ─────────────────────────

def load_credentials():
    from dotenv import load_dotenv
    load_dotenv(os.path.join(ROOT, ".env"))
    keystring = os.getenv("ETSY_API_KEYSTRING", "")
    secret    = os.getenv("ETSY_SHARED_SECRET", "")
    return f"{keystring}:{secret}" if secret else keystring


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
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())

# ── Etsy search (public listings endpoint) ───────────────────────────────────

def etsy_search_count(query, api_key, access_token):
    """Return result count for a search query. Returns -1 on error."""
    encoded = urllib.parse.quote(query)
    path = f"/listings/active?keywords={encoded}&limit=1"
    try:
        data = etsy_get(path, api_key, access_token)
        return data.get("count", -1)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            # Try token refresh once
            _, refresh_tok = load_tokens()
            if refresh_tok:
                new_token = refresh_token(api_key, refresh_tok)
                try:
                    data = etsy_get(path, api_key, new_token)
                    return data.get("count", -1)
                except Exception:
                    pass
    except Exception:
        pass
    return -1

# ── Scoring dimensions ────────────────────────────────────────────────────────

def score_demand(count):
    """40 pts max — raw listing count for the niche term."""
    if count < 0:
        return 15, "API unavailable — fallback score"
    if count > 10000:
        return 40, f"{count:,} results (>10k)"
    if count > 5000:
        return 30, f"{count:,} results (>5k)"
    if count > 1000:
        return 20, f"{count:,} results (>1k)"
    if count > 100:
        return 10, f"{count:,} results (>100)"
    return 5, f"{count:,} results (<100)"


def score_competition_gap(count):
    """25 pts max — bundle-specific search: FEWER = better gap."""
    if count < 0:
        return 10, "API unavailable — fallback score"
    if count < 50:
        return 25, f"{count:,} bundle results (<50, strong gap)"
    if count < 200:
        return 20, f"{count:,} bundle results (<200)"
    if count < 500:
        return 15, f"{count:,} bundle results (<500)"
    if count < 1000:
        return 10, f"{count:,} bundle results (<1k)"
    return 5, f"{count:,} bundle results (>1k, saturated)"


def score_coverage(niche_name):
    """20 pts max — 0 if already built, 10 if adjacent, 20 if new."""
    slug = slugify(niche_name)
    terms = set(slug.split("-"))

    exact_match = False
    adjacent_match = False

    for fname in os.listdir(NICHES_DIR):
        if not fname.endswith(".json") or fname == "sample_niche.json":
            continue
        existing = fname.replace(".json", "")
        existing_terms = set(existing.split("-"))

        # Exact slug match
        if existing == slug:
            exact_match = True
            break

        # Substantial overlap (>50% of terms match)
        overlap = terms & existing_terms
        if len(overlap) >= max(1, len(terms) // 2):
            adjacent_match = True

    if exact_match:
        return 0, f"Already covered: {slug}.json"
    if adjacent_match:
        return 10, "Adjacent to existing niche — asset reuse possible"
    return 20, "New niche — fresh opportunity"


def score_build_cost(niche_name):
    """15 pts max — can factory handle it, or needs new work?"""
    factory_path = os.path.join(ROOT, "scripts", "niche_template_factory.py")
    factory_exists = os.path.exists(factory_path)

    # Keywords that suggest novel template types outside the factory
    novel_keywords = {"app", "software", "saas", "digital art", "print on demand",
                      "video", "course", "coaching", "3d", "animation"}
    slug_terms = set(slugify(niche_name).split("-"))

    needs_novel = bool(slug_terms & novel_keywords)

    if factory_exists and not needs_novel:
        return 15, "Factory exists — reuse niche_template_factory.py"
    if factory_exists and needs_novel:
        return 10, "Factory exists but niche needs new template types"
    return 5, "No factory — would need new scripts/tools"

# ── Helpers ───────────────────────────────────────────────────────────────────

def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def tier_label(score):
    if score >= 70:
        return "APPROVED"
    if score >= 50:
        return "REVIEW"
    return "SKIPPED"

# ── Report writer ─────────────────────────────────────────────────────────────

def write_report(niche_name, slug, scores, total, api_available):
    os.makedirs(EVALS_DIR, exist_ok=True)
    path = os.path.join(EVALS_DIR, f"niche_{slug}_score.md")
    tier = tier_label(total)
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    lines = [
        f"# Niche Evaluation: {niche_name}",
        f"**Date:** {date}  ",
        f"**Score:** {total}/100  ",
        f"**Tier:** {tier}",
        "",
        "## Score Breakdown",
        "",
        f"| Dimension         | Score | Max | Notes |",
        f"|-------------------|-------|-----|-------|",
    ]
    for label, pts, mx, note in scores:
        lines.append(f"| {label:<17} | {pts:>5} | {mx:>3} | {note} |")

    lines += [
        "",
        f"**Total: {total}/100**",
        "",
        "## Etsy API",
        f"Available during this run: {'Yes' if api_available else 'No (fallback scores used)'}",
    ]

    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")

    return path


def append_to_backlog(niche_name, total, report_path):
    tier = tier_label(total)
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    entry = (
        f"\n[{tier}: {date}] **Niche Idea** {niche_name} — "
        f"Score: {total}/100 — see {os.path.relpath(report_path, ROOT)}\n"
    )
    with open(IDEAS_FILE, "a") as f:
        f.write(entry)

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/niche_evaluator.py \"niche name\"")
        sys.exit(1)

    niche_name = " ".join(sys.argv[1:])
    slug = slugify(niche_name)

    print(f"\nEvaluating niche: \"{niche_name}\"")
    print("=" * 55)

    # Auth
    api_key = load_credentials()
    access_token, refresh_tok = load_tokens()
    api_available = bool(api_key and access_token)

    # 1. Demand — search for niche term
    print(f"  [1/4] Etsy demand search: \"{niche_name}\" ...", end=" ", flush=True)
    demand_count = etsy_search_count(niche_name, api_key, access_token) if api_available else -1
    demand_pts, demand_note = score_demand(demand_count)
    print(f"{demand_pts}/40")

    # 2. Competition gap — bundle-specific search
    bundle_query = f"{niche_name} template bundle canva"
    print(f"  [2/4] Competition gap search: \"{bundle_query}\" ...", end=" ", flush=True)
    bundle_count = etsy_search_count(bundle_query, api_key, access_token) if api_available else -1
    gap_pts, gap_note = score_competition_gap(bundle_count)
    print(f"{gap_pts}/25")

    # 3. Niche coverage
    print(f"  [3/4] Coverage check ...", end=" ", flush=True)
    cov_pts, cov_note = score_coverage(niche_name)
    print(f"{cov_pts}/20")

    # 4. Build cost
    print(f"  [4/4] Build cost estimate ...", end=" ", flush=True)
    cost_pts, cost_note = score_build_cost(niche_name)
    print(f"{cost_pts}/15")

    total = demand_pts + gap_pts + cov_pts + cost_pts
    tier = tier_label(total)

    scores = [
        ("Etsy Demand",       demand_pts, 40, demand_note),
        ("Competition Gap",   gap_pts,    25, gap_note),
        ("Niche Coverage",    cov_pts,    20, cov_note),
        ("Build Cost",        cost_pts,   15, cost_note),
    ]

    # Print breakdown
    print()
    print("  SCORE BREAKDOWN")
    print("  " + "-" * 50)
    for label, pts, mx, note in scores:
        bar = "#" * pts + "." * (mx - pts)
        print(f"  {label:<18} {pts:>2}/{mx:<2}  [{bar}]")
        print(f"                       {note}")
    print("  " + "-" * 50)
    print(f"  TOTAL: {total}/100  →  [{tier}]")
    print()

    # Save report
    report_path = write_report(niche_name, slug, scores, total, api_available)
    print(f"  Report saved: {os.path.relpath(report_path, ROOT)}")

    # Append to backlog
    append_to_backlog(niche_name, total, report_path)
    print(f"  ideas_backlog.md updated: [{tier}] {niche_name} ({total}/100)")
    print()


if __name__ == "__main__":
    main()
