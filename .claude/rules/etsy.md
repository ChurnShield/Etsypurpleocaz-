# Etsy API Rules

Rules learned from production. Every one caused a real failure.

## Tags
- Max **20 characters** per tag. API returns 400 if exceeded.
- **No duplicates.** API returns 400 "You may have duplicate tags."
- **13 tags** per listing, split across: core product, format/modifier, buyer intent, adjacent niche, seasonal.

## Price
- **Set price at creation time.** Price PATCH is silently ignored on draft listings.
- To change a draft price: recreate the listing or edit manually in dashboard.

## Listing Updates
- **Always PATCH, never PUT.** PUT returns 404 on listings endpoint.
- `state: active` on a draft with images + files works cleanly — no extra fields needed.

## Verification — NEVER Skip
- **GET after every upload.** Never report success from POST response alone.
- `GET /listings/{id}/images` — confirm image count and ranks.
- `GET /shops/{id}/listings/{id}/files` — confirm PDF attached.
- Show raw response. Do not mark done without API confirmation.

## Content-Type
- Listing create/update: `application/x-www-form-urlencoded`
- Image/file upload: `multipart/form-data`
- Tags in create: comma-separated string, not array.

## Auth
- `x-api-key` header: `{keystring}:{shared_secret}` (colon-separated)
- `Authorization: Bearer {access_token}` for OAuth endpoints
- Token auto-refreshes on 401 during upload loops — don't abort on single auth error.
- Token file: `workflows/etsy_analytics/etsy_tokens.json`

## Does Not Exist
- No `copy_listing` or `clone` endpoint. Don't search for one.
- No bulk listing creation. One at a time.

## Standard Listing Spec (PurpleOcaz)
- Price: £2.99
- Quantity: 999
- who_made: `i_did`
- when_made: `2020_2025`
- taxonomy_id: `1874` (digital templates)
- type: `download`
- is_supply: `false`
