#!/usr/bin/env python3
"""
Weekly Etsy performance check.
Runs every Monday 8am via cron.
Refreshes OAuth token, pulls all active listings (paginated),
fetches transaction data for sales counts, identifies top 5 and
underperformers (<10 views), saves JSON report to reports/.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime

from dotenv import load_dotenv

load_dotenv("/root/NEW-AI-PROJECT/.env")

SHOP_ID = os.getenv("ETSY_SHOP_ID", "34071205")
API_KEY = os.getenv("ETSY_API_KEYSTRING")
SECRET = os.getenv("ETSY_SHARED_SECRET")
X_API_KEY = f"{API_KEY}:{SECRET}"
TOKEN_FILE = "/root/NEW-AI-PROJECT/workflows/etsy_analytics/etsy_tokens.json"
ETSY_BASE = "https://openapi.etsy.com/v3/application"
REPORT_DIR = "/root/NEW-AI-PROJECT/reports"
PAGE_LIMIT = 100
MAX_PAGES = 50


def refresh_token():
    """Refresh the OAuth access token and persist to disk."""
    with open(TOKEN_FILE) as f:
        tokens = json.load(f)

    keystring = API_KEY.split(":")[0] if ":" in API_KEY else API_KEY

    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "client_id": keystring,
        "refresh_token": tokens["refresh_token"],
    }).encode()

    req = urllib.request.Request(
        "https://api.etsy.com/v3/public/oauth/token",
        data=data,
        method="POST",
    )
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    with urllib.request.urlopen(req, timeout=30) as resp:
        new_tokens = json.loads(resp.read().decode())

    # Preserve any extra fields from original file, overlay new tokens
    tokens.update(new_tokens)
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f, indent=2)

    return tokens["access_token"]


def api_get(path, token):
    """GET from Etsy v3 API. Returns parsed JSON or None on error."""
    url = f"{ETSY_BASE}{path}" if path.startswith("/") else path
    req = urllib.request.Request(url)
    req.add_header("x-api-key", X_API_KEY)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode()[:200]
        except Exception:
            pass
        print(f"  HTTP {e.code} on {path}: {body}")
        return None


def fetch_all_listings(token):
    """Paginate through all active listings."""
    all_listings = []
    offset = 0
    total = None

    for _ in range(MAX_PAGES):
        data = api_get(
            f"/shops/{SHOP_ID}/listings/active?limit={PAGE_LIMIT}&offset={offset}",
            token,
        )
        if not data:
            break

        if total is None:
            total = data.get("count", 0)

        results = data.get("results", [])
        if not results:
            break

        all_listings.extend(results)
        offset += len(results)

        if offset >= total:
            break

        time.sleep(0.3)

    return all_listings, total or len(all_listings)


def fetch_transactions(token):
    """Fetch all shop transactions and aggregate sales/revenue per listing."""
    sales = {}
    revenue = {}
    offset = 0

    for _ in range(MAX_PAGES):
        data = api_get(
            f"/shops/{SHOP_ID}/transactions?limit={PAGE_LIMIT}&offset={offset}",
            token,
        )
        if not data:
            break

        results = data.get("results", [])
        if not results:
            break

        for tx in results:
            lid = tx.get("listing_id")
            if not lid:
                continue
            sales[lid] = sales.get(lid, 0) + tx.get("quantity", 1)
            price = tx.get("price", {})
            if price:
                amt = price.get("amount", 0) / price.get("divisor", 1)
                revenue[lid] = revenue.get(lid, 0.0) + amt

        total = data.get("count", 0)
        offset += len(results)
        if offset >= total:
            break

        time.sleep(0.3)

    return sales, revenue


def build_report(listings, sales, revenue):
    """Build enriched listing records sorted by views descending."""
    enriched = []
    for item in listings:
        lid = item.get("listing_id")
        price_obj = item.get("price", {})
        amt = price_obj.get("amount", 0) / price_obj.get("divisor", 1) if price_obj else 0

        enriched.append({
            "listing_id": lid,
            "title": item.get("title", "")[:80],
            "price": round(amt, 2),
            "currency": price_obj.get("currency_code", "GBP"),
            "views": item.get("views", 0),
            "favorites": item.get("num_favorers", 0),
            "sales": sales.get(lid, 0),
            "revenue": round(revenue.get(lid, 0.0), 2),
            "tags": len(item.get("tags", [])),
            "url": item.get("url", ""),
            "created": item.get("original_creation_timestamp", 0),
        })

    enriched.sort(key=lambda x: x["views"], reverse=True)
    return enriched


def main():
    print(
        f"\n{'=' * 55}\n"
        f"WEEKLY PERFORMANCE CHECK - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        f"{'=' * 55}\n"
    )

    # --- Validate config ---
    if not API_KEY or not SECRET:
        print("ETSY_API_KEYSTRING and ETSY_SHARED_SECRET must be set in .env")
        sys.exit(1)

    if not os.path.exists(TOKEN_FILE):
        print(f"Token file missing: {TOKEN_FILE}")
        print("Run: python workflows/etsy_analytics/etsy_oauth.py")
        sys.exit(1)

    # --- Refresh OAuth token ---
    try:
        token = refresh_token()
        print("Token refreshed successfully")
    except Exception as e:
        print(f"Token refresh failed: {e}")
        print("Run: python workflows/etsy_analytics/etsy_oauth.py to re-authorize")
        sys.exit(1)

    # --- Fetch all active listings (paginated) ---
    print(f"Fetching active listings for shop {SHOP_ID}...")
    listings, total = fetch_all_listings(token)
    if not listings:
        print("Failed to fetch listings or shop is empty")
        sys.exit(1)
    print(f"Active listings fetched: {len(listings)} / {total}")

    # --- Fetch transaction data for sales counts ---
    print("Fetching transaction data...")
    sales, revenue = fetch_transactions(token)
    tx_count = sum(sales.values())
    print(f"Transactions loaded: {tx_count} sales across {len(sales)} listings")

    # --- Build enriched report ---
    enriched = build_report(listings, sales, revenue)

    # --- Top 5 ---
    print(f"\nTOP 5 (by views):")
    for i, item in enumerate(enriched[:5], 1):
        print(
            f"  {i}. {item['views']:>6} views | "
            f"{item['favorites']:>3} favs | "
            f"{item['sales']:>3} sales | "
            f"{item['price']:.2f} {item['currency']} | "
            f"{item['title']}"
        )

    # --- Underperformers ---
    under = [item for item in enriched if item["views"] < 10]
    print(f"\nUNDERPERFORMERS (<10 views): {len(under)}")
    for item in under[:15]:
        print(f"  {item['views']:>3} views | {item['favorites']} favs | {item['title']}")

    # --- Summary stats ---
    total_views = sum(item["views"] for item in enriched)
    total_favs = sum(item["favorites"] for item in enriched)
    total_sales = sum(item["sales"] for item in enriched)
    total_rev = sum(item["revenue"] for item in enriched)
    avg_views = total_views / len(enriched) if enriched else 0

    print(f"\nSUMMARY:")
    print(f"  Total listings:  {len(enriched)}")
    print(f"  Total views:     {total_views:,}")
    print(f"  Avg views:       {avg_views:.1f}")
    print(f"  Total favorites: {total_favs:,}")
    print(f"  Total sales:     {total_sales:,}")
    print(f"  Total revenue:   {total_rev:,.2f} GBP")

    # --- Save JSON report ---
    os.makedirs(REPORT_DIR, exist_ok=True)
    report = {
        "generated": datetime.now().isoformat(),
        "shop_id": SHOP_ID,
        "summary": {
            "total_listings": len(enriched),
            "total_views": total_views,
            "avg_views": round(avg_views, 1),
            "total_favorites": total_favs,
            "total_sales": total_sales,
            "total_revenue": round(total_rev, 2),
            "underperformer_count": len(under),
        },
        "top_5": enriched[:5],
        "underperformers": under,
        "all_listings": enriched,
    }

    report_path = os.path.join(
        REPORT_DIR,
        f"performance_{datetime.now().strftime('%Y%m%d')}.json",
    )
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nReport saved: {report_path}")
    print(f"{'=' * 55}\n")


if __name__ == "__main__":
    main()
