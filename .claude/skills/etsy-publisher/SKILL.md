---
name: etsy-publisher
description: "Publishes listings to Etsy and Google Sheets. Use when creating Etsy drafts,
              uploading images/PDFs, managing listing queue, or debugging publish failures."
---

## Etsy Publishing Protocol

When publishing listings or debugging publish failures:

1. Read `workflows/auto_listing_creator/tools/publish_listings_tool.py` for the publishing logic
2. Verify OAuth credentials are configured (Etsy API key format: `keystring:shared_secret`)
3. Check listing data has all required fields before publishing

## Publishing Flow

```
1. Validate listing content (title ≤140 chars, 13 tags, description sections)
2. Save to Google Sheets "Listing Queue" tab for human review
3. Create Etsy draft via POST /v3/application/shops/{shop_id}/listings
4. Upload product images (PNG) as multipart/form-data
5. Upload digital files (PDFs) for digital download products
6. Activate digital delivery mode via PATCH
```

## Required Listing Fields

- `title`: ≤140 characters, keyword-rich
- `description`: Includes PERFECT FOR, FAQ, and use-case sections
- `tags`: Exactly 13 tags (core product, format/modifier, buyer intent, adjacent niche, seasonal)
- `price`: Decimal string
- `taxonomy_id`: Etsy category ID
- `who_made`: "i_did"
- `when_made`: "2020_2025"
- `is_supply`: false (for finished products)
- `is_digital`: true (for digital downloads)

## Debugging Publish Failures

1. Check for Etsy API 401/403 — likely expired OAuth token or bad API key format
2. Check for 400 errors — usually missing required fields or invalid taxonomy_id
3. Verify image files exist and are valid PNGs before upload
4. Check `data/system.db` execution_logs for error details via SQLiteClient
5. Review `docs/architecture/10-operations.md` for common failure patterns

## Hard Rules

- NEVER skip `logger.flush()` in the finally block
- NEVER hardcode API keys — import from `config.py`
- NEVER publish without human review (save to Sheets queue first)
- Always use `SQLiteClient` for any database queries
- Handle OAuth token refresh on 401 responses
- Use exponential backoff for transient API failures
