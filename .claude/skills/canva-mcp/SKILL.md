---
name: canva-mcp
description: "Canva MCP integration: design creation, editing, export, hero thumbnails,
              delivery PDFs, and folder management. Loads automatically for any Canva
              design work, template editing, or export task."
user-invocable: false
---

# Canva MCP Skill

All Canva design work goes through the Canva MCP tools. Never use REST API endpoints directly — they return 404.

For gotchas and failure history, see [reference/gotchas.md](reference/gotchas.md).

---

## Folder IDs

| Folder | ID | Use |
|--------|----|-----|
| Root (PurpleOcaz) | `FAHENpMANrQ` | Top-level brand folder |
| Tattoo Masters | `FAHENuO2Vkc` | Master designs per niche |
| Listing Templates | `FAHENvJko1A` | Generic reusable listing pages |
| Thumbnails / Hero | `FAHENqKrgvk` | Hero thumbnail templates |

Move every new design to the correct folder immediately after creation.

---

## Master Design IDs

### Tattoo Niche

| Design | ID | Pages | Purpose |
|--------|----|-------|---------|
| Dark business card | `DAHD07F9MsY` | 1 | Black/gold card — front only |
| Light business card | `DAHD15IcxRs` | 1 | White/gold card — front only |
| Dark appointment card | `DAHENCEJGjk` | 2 | Black/gold/botanical — front+back |
| Light appointment card | `DAHENKnCBoM` | 2 | Cream/charcoal/gold — front+back |
| Hero thumbnail template | `DAHDc0gyebE` | 1 | Flatlay with natural shadows |
| Generic listing pages | `DAFx_dsWpTA` | 5 | Reusable across all listings |

### Generic Listing Pages (DAFx_dsWpTA)

| Page | Content | Etsy Rank |
|------|---------|-----------|
| 3 | "Canva Basics" — free e-book promo | 2 |
| 5 | "Please Note" — digital disclaimer | 3 |

Pages 1, 2, 4 are product-specific. Only pages 3 and 5 are reusable.

### Spaces CDN

- Bucket: `purpleocaz-assets` / Region: `lon1`
- CDN base: `https://purpleocaz-assets.lon1.digitaloceanspaces.com/`
- Thumbnails: `thumbnails/` prefix
- Reviews: `reviews/` prefix

Full element IDs and asset IDs are in `config/design_registry.json`. Always read that file before editing any design.

---

## Hard Rules

These are non-negotiable. Every one caused a production failure.

1. **One transaction per logical change.** Commit before starting the next. Front and back pages are separate transactions.
2. **MCP tools only.** Canva REST editing API returns 404. Use `start-editing-transaction`, `perform-editing-operations`, `commit-editing-transaction`.
3. **`/d/{shortcode}` links only** in delivery PDFs. Never `/design/.../edit` or `/design/.../view`. Verify by clicking — must show "Use this template".
4. **Cannot insert new text elements.** Only `insert_fill` for images/videos. If you need more text fields, pick a different template.
5. **`update_fill` only works on image/video containers.** Shapes return "does not contain an editable fill."
6. **`insert_fill` goes on TOP of z-stack.** No z-order control. Workaround: export and post-process.
7. **`replace_text` on grouped elements needs 3-segment IDs** (`page-group-element`). 2-segment returns "not_found".
8. **After `replace_text`, always `format_text` with explicit `font_size`.** Repurposed headings overflow.
9. **Export width must match aspect ratio.** Non-matching width causes black borders/letterboxing. Omit width for native dimensions.
10. **No clone/duplicate design tool.** Generate fresh or user copies in Canva UI.
11. **No `search-templates` or `search-elements` tool.** Don't promise search.
12. **Preview URLs (`design.canva.ai/*`) are auth-gated.** WebFetch gets 403. Use `get-design-thumbnail`.
13. **Verify visually after every `update_fill`.** Internal crop/zoom is uncontrollable.
14. **Never synthesize shadows programmatically.** Use Canva templates with built-in flatlay shadows. The template IS the shadow system.
15. **Asset upload uses binary `application/octet-stream`** with `Asset-Upload-Metadata` header (base64). NOT JSON. Name max 50 chars.
16. **Register every new design in `config/design_registry.json` immediately.** Unregistered IDs are lost if a session crashes.

---

## Workflow 1: Export a Design

1. Read `config/design_registry.json` for the design ID and page details
2. Call `export-design` with the design ID and page number
3. For generic listing pages: `width=3000`
4. For hero thumbnails: omit width (native dimensions) or `width=3000` for high-res
5. Upload PNG to Spaces CDN under the correct prefix
6. **Verify**: open the Spaces URL to confirm the export looks correct

---

## Workflow 2: Hero Thumbnail (DAHDc0gyebE)

The hero template has natural flatlay shadows built in. Never add shadows programmatically.

1. Read `config/design_registry.json` for element IDs
2. `start-editing-transaction` on `DAHDc0gyebE`
3. `update_fill` front card element with dark card export asset
4. `update_fill` back card element with light card export asset
5. `replace_text` headline + subtext as needed
6. `position_element` / `resize_element` banner shape to full width (left=0, width=1587)
7. `commit-editing-transaction`
8. Export at native dimensions (1587x2245)
9. **Post-export**: pixel swap — brightness < 180 below y=82% → black #000000 (changes crimson banner to black while preserving white text)
10. Upload to Spaces + Etsy as rank 1 image
11. **Verify**: GET the Etsy listing images to confirm upload

---

## Workflow 3: Create a New Design

1. `generate-design` with `business_card` type and detailed aesthetic prompt:
   - Include exact hex color codes, style references, illustration type
   - Add negative instructions ("no geometric shapes, no patterns")
   - Result will always be a personal business card layout — plan to restyle
2. Export candidates to Spaces CDN for Andy to review on phone
3. **Wait for Andy's approval before editing**
4. If approved: `start-editing-transaction` on the chosen candidate
5. `replace_text` all text elements with product content
6. `format_text` every replaced element with explicit `font_size`
7. `resize_element` + `position_element` to fix layout
8. `commit-editing-transaction`
9. Repeat steps 4-8 for each page (one transaction per page)
10. Export final PNGs to Spaces
11. Register in `config/design_registry.json` with all element IDs
12. Move to correct Canva folder

---

## Workflow 4: Delivery PDF

1. Generate PDF using reportlab with clickable Canva template links
2. **Links must use `/d/{shortcode}` format only**
3. Get shortcodes from Canva's "Share > Template link" feature
4. Include all product variants (dark + light) with labels
5. Professional layout with branded PurpleOcaz footer
6. Upload PDF to Etsy via `POST /shops/{id}/listings/{id}/files`
7. **Verify**: `GET /shops/{id}/listings/{id}/files` to confirm PDF attached
8. Click every link in the PDF — must show "Use this template", not the editor

---

## Token Management

- Canva tokens: `workflows/auto_listing_creator/canva_tokens.json` + `purpleocaz-canva-mcp/.env`
- Tokens expire hourly — auto-refresh works but verify before long operations
- Use `canva_token_manager.py` for token access — never read token files directly
