---
name: etsy-listing
description: "Hard rules for creating Etsy listings: tag limits, pricing, image sources,
              Canva delivery links, folder IDs, and production gotchas. Use whenever
              creating, editing, or publishing Etsy listings or uploading images/files."
user-invocable: false
---

# Etsy Listing — Production Rules

These rules are non-negotiable. Every one was learned from a production failure.

---

## Etsy API Hard Rules

### Tags
- **Max 20 characters per tag.** Validate every tag length before submitting. The API returns 400 if any tag exceeds 20 chars.
- **No duplicates.** The API returns 400 "You may have duplicate tags." Deduplicate before submission.
- **13 tags** split across: core product, format/modifier, buyer intent, adjacent niche, seasonal.

### Price
- **Set price at creation time.** Price PATCH is silently ignored on draft listings. If you need to change the price on a draft, you must do it manually in the Etsy dashboard or recreate the listing.

### Listing Updates
- **Always PATCH, never PUT.** Etsy v3 API returns 404 for PUT on listings endpoint.
- **`state: active`** on a draft with images + files works cleanly — no additional fields required beyond the state change.

### Verification — NEVER Skip
- **Always GET after every upload.** Never report success based on the POST response alone.
- Run `GET /listings/{id}/images` and `GET /shops/{id}/listings/{id}/files` after every upload.
- Show the raw response. Do not mark a task done without API confirmation.

### Cloning
- No `copy_listing` or `clone` endpoint exists in Etsy v3. Don't look for one.

---

## Standard Listing Image Sources

Every tattoo listing uses these three images in this order:

| Rank | Source | Description |
|------|--------|-------------|
| 1 | `DAHDc0gyebE` page 1 | Hero thumbnail (product-specific, swap card images per product) |
| 2 | `DAFx_dsWpTA` page 3 | "Canva Basics" — free e-book for Canva editing basics |
| 3 | `DAFx_dsWpTA` page 5 | "Please Note" — digital product disclaimer with PurpleOcaz branding |

- Export generic pages (ranks 2 & 3) at `width=3000`. These URLs are reusable across all listings.
- `DAHDc0gyebE` has only 1 page. Pages 2/3 do not exist — don't try to export them.
- `DAFx_dsWpTA` is a 5-page design. Only pages 3 and 5 are used for listings.

### Hero Thumbnail Pipeline (DAHDc0gyebE)
1. `start-editing-transaction` on DAHDc0gyebE
2. `update_fill` front card element with product dark card export
3. `update_fill` back card element with product light card export
4. `replace_text` headline + subtext as needed
5. `position_element` / `resize_element` banner shape to full width (left=0, width=1587)
6. Commit transaction
7. Export at native dimensions (1587x2245) or width=3000 for high-res
8. **Post-export**: Sharp pixel swap — all dark pixels (brightness < 180) below y=82% → black #000000 (changes crimson banner to black, preserves white text)
9. Upload to Spaces + Etsy as rank 1 image

---

## Canva Delivery Link Rules

**USE VIEW LINKS, NEVER EDIT LINKS.**

| Format | Safe? | Behaviour |
|--------|-------|-----------|
| `https://www.canva.com/d/{shortcode}` | YES | Forces "Use this template" — buyer gets a copy |
| `https://www.canva.com/design/{id}/view` | NO | Exposes the master design |
| `https://www.canva.com/design/{id}/edit` | NO | Gives buyer write access to master |

- Always use `/d/{shortcode}` format in delivery PDFs.
- Get the shortcode from Canva's "Share > Template link" feature.
- Verify by clicking — it must show "Use this template", not open the editor.

---

## Canva Folder IDs

Move every new design to its correct folder immediately after creation.

| Folder | ID |
|--------|----|
| Root (PurpleOcaz) | `FAHENpMANrQ` |
| Tattoo Masters | `FAHENuO2Vkc` |
| Listing Templates | `FAHENvJko1A` |
| Thumbnails / Hero | `FAHENqKrgvk` |

---

## Gotchas — Every Failure From LESSONS.md

### Canva API Gotchas

1. **`update_fill` on shapes fails.** Shape elements return "shape does not contain an editable fill." Only works on image/video containers.

2. **`insert_fill` z-order is uncontrollable.** New image elements always go on TOP of the z-stack, covering text. No z-order API. Workaround: keep original shape, export, post-process the PNG.

3. **`update_fill` internal cropping.** Replacing image containers causes internal crop/zoom that cannot be controlled via the API. Always verify visually after every swap.

4. **Curved text elements are permanent.** The curve is baked into the element container. Replacing text does not straighten it.

5. **Cannot insert new text elements.** The API only supports `insert_fill` for images/videos. If you need more text fields than the template has, use a different template.

6. **`generate-design` always produces personal business cards.** It cannot create appointment/booking cards with form fields. Workaround: generate for aesthetic base, then restyle via editing transactions.

7. **No clone/duplicate design tool.** Must generate fresh or have the user copy manually in Canva UI.

8. **`replace_text` on grouped elements needs 3-segment IDs.** Use the full `page-group-element` ID from richtexts response. The 2-segment `page-element` format returns "not_found."

9. **No `search-templates` or `search-elements` tool.** Don't promise search capabilities that don't exist.

10. **Preview thumbnail URLs are auth-gated.** `design.canva.ai/*` URLs redirect through auth — WebFetch gets 403. Use `get-design-thumbnail` or export to inspect.

11. **One transaction per logical change, commit before next.** Prevents cascading failures. Never batch unrelated changes.

12. **Asset upload is binary.** Use `application/octet-stream` with `Asset-Upload-Metadata` header (base64-encoded name). NOT JSON body. Asset name max 50 chars.

13. **Export width must match aspect ratio.** Specifying a non-matching width causes black borders/letterboxing. Omit width for native dimensions.

14. **Canva REST editing API (`/designs/{id}/editing_sessions`) returns 404.** This endpoint doesn't exist. Use MCP tools only.

### Etsy API Gotchas

15. **PUT returns 404.** Always use PATCH for listing updates.

16. **Price on drafts is immutable via API.** Set at creation time or change in dashboard.

17. **Tags over 20 chars = 400 error.** Validate lengths before every submission.

18. **Duplicate tags = 400 error.** Deduplicate the tag list.

19. **No clone endpoint.** Don't waste time searching for `copy_listing`.

20. **Token expiry mid-upload is handled.** The upload loop auto-refreshes on 401 — don't abort if a single request fails with auth error.

### Design & Pipeline Gotchas

21. **Don't synthesize shadows programmatically.** Pillow/Sharp shadow compositing always looks fake. Use a Canva template with built-in shadows (flatlay background).

22. **After `replace_text`, always `format_text` with explicit `font_size`.** Repurposed heading elements inherit the original (large) font size, causing overflow.

23. **Always audit element count before proposing a design plan.** Count available text elements vs required fields. Flag gaps immediately — don't attempt workarounds.

24. **Register design IDs in `config/design_registry.json` immediately.** If a session crashes, unregistered IDs are lost.

25. **Export Canva designs to Spaces CDN for review before editing.** Prevents wasted edit cycles on rejected designs.

---

## Content Rules

When exact copy is provided for listing titles, descriptions, or tags — use it **VERBATIM**. Never rewrite, summarise, or improve provided copy. If a technical limitation prevents exact use, flag it before proceeding.
