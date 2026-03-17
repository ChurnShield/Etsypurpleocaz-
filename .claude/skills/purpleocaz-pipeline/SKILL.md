---
name: purpleocaz-pipeline
description: "PurpleOcaz Etsy listing pipeline: Canva design, image sourcing, Etsy
              publishing, and verification. Loads automatically for all listing,
              design, and publishing work. Contains every production failure as a gotcha."
user-invocable: false
---

# PurpleOcaz Pipeline

Complete reference for building and publishing Etsy digital product listings.
Read `.claude/rules/etsy.md`, `.claude/rules/canva.md`, and `.claude/rules/pipeline.md`
for the full rule sets. This skill is the summary + gotchas layer on top.

---

## Quick Reference

### Standard Listing Spec
| Field | Value |
|-------|-------|
| Price | £2.99 (set at creation, not patchable on drafts) |
| Quantity | 999 |
| who_made | `i_did` |
| when_made | `2020_2025` |
| taxonomy_id | `1874` |
| type | `download` |
| Tags | 13 tags, each max 20 chars, no duplicates |

### Standard Images (3 per listing)
| Rank | Source | What |
|------|--------|------|
| 1 | `DAHDc0gyebE` p1 | Hero thumbnail (product-specific) |
| 2 | `DAFx_dsWpTA` p3 | Canva Basics (reusable) |
| 3 | `DAFx_dsWpTA` p5 | Please Note (reusable) |

### Canva Folder IDs
| Folder | ID |
|--------|----|
| Root | `FAHENpMANrQ` |
| Tattoo Masters | `FAHENuO2Vkc` |
| Listing Templates | `FAHENvJko1A` |
| Thumbnails / Hero | `FAHENqKrgvk` |

### Delivery Links
- YES: `https://www.canva.com/d/{shortcode}`
- NO: `https://www.canva.com/design/{id}/view` or `/edit`

---

## Gotchas — Production Failures

Every item below caused a real failure. Do not repeat them.

### Etsy API

1. **PUT returns 404.** Always PATCH for listing updates.
2. **Price on drafts is immutable via API.** Set at creation. Dashboard only after.
3. **Tags > 20 chars = 400.** Validate every tag length before submission.
4. **Duplicate tags = 400.** Deduplicate the list.
5. **No clone endpoint.** `copy_listing` does not exist.
6. **Never report success without GET confirmation.** POST response is not proof.
7. **Token expires mid-upload.** Loop handles 401 auto-refresh — don't abort.

### Canva MCP

8. **`update_fill` on shapes fails.** "Does not contain an editable fill." Image/video containers only.
9. **`insert_fill` z-order uncontrollable.** Always on top, covers text. Export + post-process instead.
10. **`update_fill` crop/zoom uncontrollable.** Verify visually after every swap.
11. **Curved text is permanent.** Baked into container. Can't straighten by replacing text.
12. **Cannot insert text elements.** Only `insert_fill` for images/videos.
13. **`generate-design` = personal business cards only.** Generate for aesthetic, restyle for function.
14. **No clone/duplicate design tool.** Generate fresh or manual copy in UI.
15. **`replace_text` grouped elements: use 3-segment IDs.** `page-group-element` from richtexts. 2-segment = "not_found."
16. **No search-templates or search-elements tool.** Don't promise what doesn't exist.
17. **Preview URLs auth-gated.** `design.canva.ai/*` → 403. Use `get-design-thumbnail`.
18. **One transaction per change, commit before next.** Prevents cascading failures.
19. **Asset upload is binary.** `application/octet-stream` + base64 metadata header. Not JSON. Name max 50 chars.
20. **Export width must match aspect ratio.** Wrong width = black borders.
21. **REST editing API (`/designs/{id}/editing_sessions`) = 404.** Use MCP tools only.
22. **After `replace_text`, always `format_text`.** Repurposed headings inherit large font size → overflow.

### Design & Pipeline

23. **Don't synthesize shadows.** Pillow/Sharp compositing always looks fake. Use Canva template flatlay.
24. **Audit element count before planning.** Count text elements vs required fields. Flag gaps immediately.
25. **Register design IDs in `config/design_registry.json` immediately.** Unregistered IDs lost on crash.
26. **Export to Spaces CDN for review before editing.** Prevents wasted edit cycles on rejected designs.
27. **Canva export defaults to tiny 336x192.** Specify `format.width: 2100` (or 3000) for full resolution.
28. **Export response shape is `job.urls[0]`** (plain string). Not `job.result.urls[0].url`.
29. **Canva `update_fill` visual verify required.** API success doesn't mean it looks right — internal crop may differ.

---

## Verification

After every listing build, run:
```bash
python scripts/verify_listing.py {listing_id}
```

Checks: image count/ranks, PDF attached, tag lengths, price, state, PDF link format.
