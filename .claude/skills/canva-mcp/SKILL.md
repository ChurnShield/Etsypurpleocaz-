---
name: canva-mcp
description: "Canva MCP integration: design creation, editing, export, hero thumbnails,
              delivery PDFs, and folder management. Loads automatically for any Canva
              design work, template editing, or export task."
user-invocable: false
requires:
  - rules/canva.md
  - rules/pipeline.md
  - rules/infra.md
---

# Canva MCP Skill

All rules (folder IDs, design IDs, element limits, link format, transaction rules, colour palettes) are in `.claude/rules/canva.md`. This skill contains only the procedural workflows.

---

## Workflow 1: Export a Design Page

1. Read `config/design_registry.json` for the design ID and page details
2. Call `export-design` with the design ID and page number
3. Specify `format.width: 3000` for listing images; omit width for hero templates (native dimensions)
4. Export response shape is `job.urls[0]` — a plain string. Not `job.result.urls[0].url`
5. Upload PNG to Spaces under the correct prefix with `ACL='public-read'`
6. Verify: `curl -sI {SPACES_URL}` — must return HTTP 200

---

## Workflow 2: Hero Thumbnail (DAHDc0gyebE)

The hero template has a natural flatlay shadow built in. Never add shadows programmatically.

1. Read `config/design_registry.json` for element IDs
2. `start-editing-transaction` on `DAHDc0gyebE`
3. `update_fill` front card element with dark card export asset
4. `update_fill` back card element with light card export asset
5. `replace_text` headline + subtext as needed
6. `format_text` on any replaced text with explicit `font_size` — prevents overflow
7. `position_element` / `resize_element` banner shape to full width (left=0, width=1587)
8. `commit-editing-transaction`
9. Export at native dimensions (1587x2245) — do not specify width
10. **Post-export pixel swap**: brightness < 180 below y=82% of image height → `#000000`
    (changes crimson banner to black while preserving white text)
11. Upload to Spaces + Etsy as rank 1 image
12. Verify: GET Etsy listing images to confirm rank 1 upload

---

## Workflow 3: Create a New Design

1. `generate-design` with `business_card` type and highly specific aesthetic prompt:
   - Include exact hex codes, style references, illustration type
   - Add negative instructions ("no geometric shapes", "no blue")
   - Output will always be a personal business card layout — plan to restyle it
2. Export candidates to Spaces CDN for Andy to review — **do not edit until approved**
3. `start-editing-transaction` on the approved candidate
4. `replace_text` all text elements → `format_text` with explicit `font_size` on each
5. `resize_element` + `position_element` to fix layout
6. `commit-editing-transaction`
7. Repeat steps 3-6 for each page (one transaction per page)
8. Export final PNGs to Spaces
9. Register in `config/design_registry.json` with all element IDs and page details
10. Move design to correct Canva folder immediately

---

## Workflow 4: Delivery PDF

1. Generate PDF with reportlab — clickable Canva template links, branded PurpleOcaz footer
2. Links must use `https://www.canva.com/d/{shortcode}` format only
3. Get shortcodes from Canva's "Share > Template link" feature
4. Include all product variants (dark + light) with clear labels
5. Upload PDF to Etsy via `POST /shops/{id}/listings/{id}/files`
6. Verify: `GET /shops/{id}/listings/{id}/files` — confirm PDF attached, filename correct
7. Click every link — must show "Use this template", not the editor

---

## Token Management

- Canva tokens: `workflows/auto_listing_creator/canva_tokens.json` + `purpleocaz-canva-mcp/.env`
- Tokens expire hourly — verify freshness before long operations
- Use `lib/common_tools/canva_token_manager.py` for token access — never read token files directly
- Auto-refresh script: `scripts/refresh_canva_token.py` (also runs via cron every 3h)
