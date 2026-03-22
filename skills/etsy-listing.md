# Etsy Listing — API Rules & Publishing Reference

All rules learned from production failures. Every one caused a real bug.

---

## Shop Details

| Field | Value |
|-------|-------|
| Shop ID | `34071205` |
| Shop name | `PurpleOcaz` |
| Token file | `workflows/etsy_analytics/etsy_tokens.json` |
| Auth header | `x-api-key: {keystring}:{shared_secret}` |
| OAuth header | `Authorization: Bearer {access_token}` |

## Standard Listing Spec

| Field | Value |
|-------|-------|
| Price | £2.99 (bundles may differ) |
| Quantity | 999 |
| who_made | `i_did` |
| when_made | `2020_2025` |
| taxonomy_id | `1874` (digital templates) |
| type | `download` |
| is_supply | `false` |

## Tags — Hard Rules

- **Max 20 characters per tag.** API returns 400 if any tag exceeds this.
- **No duplicate tags.** API returns 400 "You may have duplicate tags."
- **13 tags per listing**, split across: core product, format/modifier, buyer intent, adjacent niche, seasonal.
- Tags in create request: **comma-separated string**, not array.

## Pricing — Critical Gotcha

- **Set price at creation time.** Price PATCH is silently ignored on draft listings.
- To change a draft price: recreate the listing or edit manually in the Etsy dashboard.
- There is no workaround via the API.

## Content-Type

| Operation | Content-Type |
|-----------|-------------|
| Listing create/update | `application/x-www-form-urlencoded` |
| Image/file upload | `multipart/form-data` |

## Listing Updates

- **Always PATCH, never PUT.** PUT returns 404 on the listings endpoint.
- `state: active` on a draft with images + files works cleanly — no extra fields needed.

## Image Upload

- Upload images via `POST /listings/{id}/images` with `multipart/form-data`.
- Images have ranks (1-10). Rank 1 = hero thumbnail.
- Standard image sources for tattoo listings:

| Rank | Source | Description |
|------|--------|-------------|
| 1 | `DAHDc0gyebE` page 1 | Hero thumbnail — product-specific |
| 2 | `DAFx_dsWpTA` page 3 | "Canva Basics" — reusable |
| 3 | `DAFx_dsWpTA` page 5 | "Please Note" — reusable |

## PDF / Digital File Delivery

- Upload via `POST /shops/{shop_id}/listings/{listing_id}/files` with `multipart/form-data`.
- PDF delivery links must use `/d/{shortcode}` format (Canva template links).
- **NEVER** use `/design/{id}/view` or `/design/{id}/edit` — exposes or grants write access to master design.
- Get shortcode from Canva's "Share > Template link" feature.

## Verification — NEVER Skip

After every upload, verify with GET calls before reporting success:

```
GET /listings/{listing_id}/images      → confirm image count and ranks
GET /shops/{shop_id}/listings/{listing_id}/files  → confirm PDF attached
```

- **Never assume an upload worked based on POST response alone.**
- Show raw response. Do not mark done without API confirmation.
- Run `python scripts/verify_listing.py {listing_id}` after every listing build.
- Use `--bundle` flag for bundle listings (skips £2.99 price check).

## Auth & Token Refresh

- Token auto-refreshes on 401 during upload loops — don't abort on a single auth error.
- If 401/403 persists: check key format (`keystring:shared_secret`) or re-run OAuth via `etsy_oauth.py`.

## Does NOT Exist in Etsy API

- No `copy_listing` or `clone` endpoint.
- No bulk listing creation. One at a time.
