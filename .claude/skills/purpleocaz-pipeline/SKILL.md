---
name: purpleocaz-pipeline
description: "PurpleOcaz Etsy listing pipeline: Canva design, image sourcing, Etsy
              publishing, and verification. Loads automatically for all listing,
              design, and publishing work. Contains every production failure as a gotcha."
user-invocable: false
requires:
  - rules/etsy.md
  - rules/canva.md
  - rules/pipeline.md
  - rules/infra.md
---

# PurpleOcaz Pipeline

Entry point for all listing work. Rules live in `.claude/rules/` — this skill contains the pre-publish checklist and the gotchas not already captured in rules.

---

## Pre-Publish Checklist

Run through this before every Etsy listing create, update, or activate call.

**Copy**
- [ ] Read `skills/stop-slop/SKILL.md` and score the listing copy — must be 35/50+
- [ ] If exact copy was provided, use it VERBATIM — never rewrite

**Tags** (see `rules/etsy.md` for full rules)
- [ ] Exactly 13 tags
- [ ] Every tag ≤ 20 characters
- [ ] No duplicate tags (case-insensitive)

**Fields** (see `rules/etsy.md` for standard spec)
- [ ] Price set at creation time (not patchable on drafts)
- [ ] `who_made: i_did`, `when_made: 2020_2025`, `taxonomy_id: 1874`, `type: download`

**Images** (see `rules/pipeline.md` for star seller standard)
- [ ] 7 images minimum, ranks 1–7 populated
- [ ] Hero shows ALL product items — no subset for bundles
- [ ] Canva Basics (DAFx_dsWpTA p3) at rank 6
- [ ] Please Note (DAFx_dsWpTA p5) at rank 7

**Delivery PDF**
- [ ] PDF attached
- [ ] All Canva links use `/d/{shortcode}` format — click-verified

**Post-publish**
- [ ] Run `python scripts/verify_listing.py {listing_id}`
- [ ] GET images — confirm count and rank order
- [ ] GET files — confirm PDF attached

---

## Gotchas Not Already in Rules

These caused real failures and aren't captured elsewhere:

1. **Etsy GET images uses a different endpoint prefix than POST.** GET is `/listings/{id}/images` (no shops prefix). POST upload and PATCH activate use `/shops/{shop_id}/listings/{id}/...`.
2. **Images from a previous session may be gone.** Always verify image state on session start — don't assume prior work survived.
3. **`when_made` requires `who_made` and `is_supply` in the same PATCH call** or the API returns 400.
4. **Canva export URL in delivery PDFs.** Export URLs expire. Only Spaces CDN URLs are permanent. Always upload to Spaces before using in a PDF.
5. **Hero images for bundles must show ALL items.** A forms bundle of 8 shows 8 pages — not 4. Etsy buyers make decisions on thumbnail alone.
6. **After any image swap, verify all ranks still exist.** Deleting rank 1 can shift remaining ranks or leave gaps.

---

## Verification

After every listing build:

```bash
python scripts/verify_listing.py {listing_id}
```

Use `--bundle` flag for non-standard pricing (skips £2.99 check).

Checks: image count/ranks, PDF attached, tag lengths, tag duplicates, price, state, PDF link format.
