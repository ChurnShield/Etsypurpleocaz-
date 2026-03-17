# Listing Pipeline Rules

## Standard Image Sources (All Tattoo Listings)

| Rank | Source | Description |
|------|--------|-------------|
| 1 | `DAHDc0gyebE` page 1 | Hero thumbnail — product-specific, swap card images per product |
| 2 | `DAFx_dsWpTA` page 3 | "Canva Basics" — free e-book promo (reusable across all listings) |
| 3 | `DAFx_dsWpTA` page 5 | "Please Note" — digital product disclaimer (reusable across all listings) |

- `DAHDc0gyebE` has **only 1 page**. Pages 2/3 do not exist.
- `DAFx_dsWpTA` is a 5-page design. Only pages 3 and 5 are used for listings.

## Hero Thumbnail Pipeline (DAHDc0gyebE)

1. `start-editing-transaction` on DAHDc0gyebE
2. `update_fill` front card element with dark card export
3. `update_fill` back card element with light card export
4. `replace_text` headline + subtext as needed
5. `position_element` / `resize_element` banner shape to full width (left=0, width=1587)
6. Commit transaction
7. Export at native dimensions (1587x2245) or width=3000 for high-res
8. **Post-export**: Sharp pixel swap — brightness < 180 below y=82% → black #000000
9. Upload to Spaces + Etsy as rank 1 image

## Design Creation Pattern

1. `generate-design` with detailed aesthetic prompt (colors, style, illustration type)
2. Save candidate → export to Spaces CDN → Andy reviews on phone
3. If approved: `start-editing-transaction` → `replace_text` → `format_text` + `resize_element` + `position_element` → commit
4. One transaction per page, commit between
5. Export final PNGs to Spaces, register in `config/design_registry.json`

## Pipeline Flow

```
Phase 1  → Load opportunities from Trend Monitor
Phase 2  → Generate listing content (anti-gravity keyword engine)
Phase 2b → Auto-bundle creation (value bundles)
Phase 3  → Create product images (Tier 1: Gemini AI / Tier 2: HTML)
Phase 4  → Publish to Sheets + Etsy drafts + upload images/PDFs
Phase 5  → verify_listing.py — automated verification
```

## Post-Listing Verification

After every listing build, run `python scripts/verify_listing.py {listing_id}` to check:
- Images: count and rank order correct
- PDF: attached with correct filename
- Tags: all under 20 chars, no duplicates
- Price: £2.99
- State: active or draft as expected
- PDF links: `/d/` format, not `/design/`

## Content Rules

When exact copy is provided for titles, descriptions, or tags — use it **VERBATIM**. Never rewrite, summarise, or improve. Flag technical limitations before proceeding.

## Crash Recovery

On session start: check GitHub commits, Canva folders, and Etsy drafts API to audit what survived. Never assume crashed session work is lost without checking.

## Design Registry

Register design IDs in `config/design_registry.json` immediately after creation. Unregistered IDs are lost if a session crashes.

## Proven Design IDs

| Design | ID | Purpose |
|--------|----|---------|
| Dark business card | `DAHD07F9MsY` | page 1 |
| Light business card | `DAHD15IcxRs` | page 1 |
| Dark appointment card | `DAHENCEJGjk` | black/gold/botanical |
| Light appointment card | `DAHENKnCBoM` | cream/charcoal/gold/botanical |
| Hero thumbnail template | `DAHDc0gyebE` | flatlay with natural shadows |
| Listing pages (5-page) | `DAFx_dsWpTA` | generic pages for all listings |
