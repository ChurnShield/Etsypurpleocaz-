# =============================================================================
# workflows/etsy_analytics/tools/fetch_etsy_data_tool.py
#
# Phase 1: Fetches all active listings + shop stats from the Etsy API v3.
# Paginates automatically to pull all listings (up to 100 per request).
#
# When OAuth tokens are available (etsy_tokens.json), also fetches
# transaction data to calculate per-listing sales count and revenue.
#
# Uses only stdlib (urllib) — no extra dependencies.
# =============================================================================

import json
import time
import urllib.request
import urllib.error
import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
_workflow = os.path.dirname(_here)
_project_root = os.path.dirname(os.path.dirname(_workflow))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_tool import BaseTool
from config import PAGINATION_MAX_PAGES

ETSY_BASE_URL = "https://openapi.etsy.com/v3/application"
TOKEN_FILE    = os.path.join(_workflow, "etsy_tokens.json")


class FetchEtsyDataTool(BaseTool):
    """Fetch all active listings, shop stats, and sales data from Etsy API v3."""

    def execute(self, **kwargs) -> dict:
        api_key    = kwargs.get("api_key", "")
        shop_id    = kwargs.get("shop_id", "")
        page_limit = kwargs.get("page_limit", 100)

        if not api_key or not shop_id:
            return {
                "success":   False,
                "data":      None,
                "error":     "api_key and shop_id are required",
                "tool_name": self.get_name(),
                "metadata":  {},
            }

        try:
            # -- Load OAuth tokens if available --
            access_token = self._load_access_token(api_key)

            # -- Fetch shop-level stats --
            shop_data = self._api_get(
                f"{ETSY_BASE_URL}/shops/{shop_id}", api_key, access_token
            )

            # -- Fetch all active listings (paginated) --
            all_listings = []
            offset = 0
            total  = None

            for _page in range(PAGINATION_MAX_PAGES):
                url = (
                    f"{ETSY_BASE_URL}/shops/{shop_id}/listings/active"
                    f"?limit={page_limit}&offset={offset}"
                )
                page = self._api_get(url, api_key, access_token)

                if total is None:
                    total = page.get("count", 0)

                results = page.get("results", [])
                if not results:
                    break

                all_listings.extend(results)
                offset += len(results)

                if offset >= total:
                    break

                time.sleep(0.3)

            # -- Fetch transactions (sales) if OAuth is available --
            sales_by_listing = {}
            revenue_by_listing = {}
            transactions_fetched = False

            if access_token:
                try:
                    sales_by_listing, revenue_by_listing = self._fetch_transactions(
                        shop_id, api_key, access_token, page_limit
                    )
                    transactions_fetched = True
                except Exception as tx_err:
                    # OAuth might be expired — continue without sales data
                    print(f"  Warning: Could not fetch transactions: {tx_err}")
                    print(f"  Run: python workflows/etsy_analytics/etsy_oauth.py to re-authorize")

            # -- Build compact listing records --
            listings = []
            for l in all_listings:
                price = l.get("price", {})
                amt = price.get("amount", 0) / price.get("divisor", 1) if price else 0
                currency = price.get("currency_code", "")
                lid = l.get("listing_id")

                listing_sales   = sales_by_listing.get(lid, 0)
                listing_revenue = revenue_by_listing.get(lid, 0.0)

                listings.append({
                    "listing_id":    lid,
                    "title":         l.get("title", ""),
                    "price":         round(amt, 2),
                    "currency":      currency,
                    "views":         l.get("views", 0),
                    "num_favorers":  l.get("num_favorers", 0),
                    "sales":         listing_sales,
                    "revenue":       round(listing_revenue, 2),
                    "tags":          l.get("tags", []),
                    "tag_count":     len(l.get("tags", [])),
                    "quantity":      l.get("quantity", 0),
                    "state":         l.get("state", ""),
                    "url":           l.get("url", ""),
                    "created":       l.get("original_creation_timestamp", 0),
                    "last_modified": l.get("last_modified_timestamp", 0),
                    "section_id":    l.get("shop_section_id"),
                    "featured_rank": l.get("featured_rank", -1),
                })

            # -- Extract shop summary --
            shop_summary = {
                "shop_id":              shop_data.get("shop_id"),
                "shop_name":            shop_data.get("shop_name", ""),
                "total_sales":          shop_data.get("transaction_sold_count", 0),
                "active_listings":      shop_data.get("listing_active_count", 0),
                "num_favorers":         shop_data.get("num_favorers", 0),
                "review_average":       shop_data.get("review_average", 0),
                "review_count":         shop_data.get("review_count", 0),
                "currency_code":        shop_data.get("currency_code", ""),
                "is_vacation":          shop_data.get("is_vacation", False),
            }

            return {
                "success":   True,
                "data": {
                    "shop":     shop_summary,
                    "listings": listings,
                    "has_sales_data": transactions_fetched,
                },
                "error":     None,
                "tool_name": self.get_name(),
                "metadata": {
                    "listing_count":        len(listings),
                    "total_in_shop":        total,
                    "pages_fetched":        (offset // page_limit) + 1,
                    "shop_name":            shop_summary["shop_name"],
                    "has_oauth":            access_token is not None,
                    "transactions_fetched": transactions_fetched,
                    "unique_sold_listings": len(sales_by_listing),
                },
            }

        except Exception as e:
            return {
                "success":   False,
                "data":      None,
                "error":     str(e),
                "tool_name": self.get_name(),
                "metadata":  {"exception_type": type(e).__name__},
            }

    # -- Private helpers --

    def _load_access_token(self, api_key):
        """Load OAuth access token from file. Returns None if not available."""
        if not os.path.exists(TOKEN_FILE):
            return None
        try:
            with open(TOKEN_FILE) as f:
                tokens = json.load(f)

            access_token = tokens.get("access_token")
            if not access_token:
                return None

            # Try a quick test to see if token is still valid
            req = urllib.request.Request(f"{ETSY_BASE_URL}/users/me")
            req.add_header("x-api-key", api_key)
            req.add_header("Authorization", f"Bearer {access_token}")
            req.add_header("Accept", "application/json")
            urllib.request.urlopen(req, timeout=10)
            return access_token

        except urllib.error.HTTPError as e:
            if e.code == 401:
                # Token expired — try refresh
                refreshed = self._try_refresh_token(tokens, api_key)
                if refreshed:
                    return refreshed
                print(f"  OAuth token expired and refresh failed. Run etsy_oauth.py to re-authorize.")
            else:
                print(f"  OAuth token test failed (HTTP {e.code}). Continuing without sales data.")
            return None
        except Exception as ex:
            print(f"  OAuth token test error: {ex}. Continuing without sales data.")
            return None

    def _try_refresh_token(self, tokens, api_key):
        """Attempt to refresh an expired access token."""
        refresh_token = tokens.get("refresh_token")
        if not refresh_token:
            return None

        try:
            # Import the keystring from config for the refresh call
            keystring = api_key.split(":")[0] if ":" in api_key else api_key

            data = urllib.parse.urlencode({
                "grant_type":    "refresh_token",
                "client_id":     keystring,
                "refresh_token": refresh_token,
            }).encode("utf-8")

            req = urllib.request.Request(
                "https://api.etsy.com/v3/public/oauth/token",
                data=data, method="POST"
            )
            req.add_header("Content-Type", "application/x-www-form-urlencoded")
            req.add_header("x-api-key", api_key)

            with urllib.request.urlopen(req, timeout=30) as resp:
                new_tokens = json.loads(resp.read().decode("utf-8"))

            # Save refreshed tokens
            with open(TOKEN_FILE, "w") as f:
                json.dump(new_tokens, f, indent=2)

            return new_tokens.get("access_token")

        except Exception:
            return None

    def _fetch_transactions(self, shop_id, api_key, access_token, page_limit):
        """Fetch all transactions and aggregate sales/revenue per listing."""
        sales_by_listing   = {}
        revenue_by_listing = {}
        offset = 0

        for _page in range(PAGINATION_MAX_PAGES):
            url = (
                f"{ETSY_BASE_URL}/shops/{shop_id}/transactions"
                f"?limit={page_limit}&offset={offset}"
            )
            page = self._api_get_auth(url, api_key, access_token)

            results = page.get("results", [])
            if not results:
                break

            for tx in results:
                lid = tx.get("listing_id")
                if not lid:
                    continue

                sales_by_listing[lid] = sales_by_listing.get(lid, 0) + tx.get("quantity", 1)

                price = tx.get("price", {})
                if price:
                    amt = price.get("amount", 0) / price.get("divisor", 1)
                    revenue_by_listing[lid] = revenue_by_listing.get(lid, 0.0) + amt

            total = page.get("count", 0)
            offset += len(results)

            if offset >= total:
                break

            time.sleep(0.3)

        return sales_by_listing, revenue_by_listing

    def _api_get(self, url, api_key, access_token=None):
        """GET request using API key (+ optional OAuth bearer token)."""
        req = urllib.request.Request(url)
        req.add_header("x-api-key", api_key)
        req.add_header("Accept", "application/json")
        if access_token:
            req.add_header("Authorization", f"Bearer {access_token}")

        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def _api_get_auth(self, url, api_key, access_token):
        """GET request with OAuth bearer token (required for transactions)."""
        req = urllib.request.Request(url)
        req.add_header("x-api-key", api_key)
        req.add_header("Authorization", f"Bearer {access_token}")
        req.add_header("Accept", "application/json")

        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
