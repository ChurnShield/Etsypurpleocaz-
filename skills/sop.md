# Publishing SOP — Pre-Etsy API Checklist

Run this checklist before every Etsy listing create, update, or activate call.
Do NOT proceed until every item passes.

---

## 1. Copy Quality

- [ ] Read `skills/stop-slop/SKILL.md` and score the listing copy.
- [ ] Score is **35/50 or above**. If below, rewrite and re-score before continuing.
- [ ] Title, description, and tags match Andy's provided copy **verbatim** (if exact copy was given).

## 2. Tags

- [ ] Exactly **13 tags** provided.
- [ ] Every tag is **20 characters or fewer**.
- [ ] **No duplicate tags** (case-insensitive check).
- [ ] Tags cover: core product, format/modifier, buyer intent, adjacent niche, seasonal.

## 3. Pricing & Listing Fields

- [ ] Price set to **GBP 2.99** at creation time (cannot be PATCHed on drafts).
- [ ] `quantity`: 999
- [ ] `who_made`: `i_did`
- [ ] `when_made`: `2020_2025`
- [ ] `taxonomy_id`: `1874`
- [ ] `type`: `download`
- [ ] `is_supply`: `false`

## 4. Hero Thumbnail

- [ ] **Check existing Canva assets first.** Search Canva folders (Thumbnails/Hero `FAHENqKrgvk`, Listing Templates `FAHENvJko1A`) for a proven hero design before generating anything with Pillow.
- [ ] Only use Pillow-generated heroes when no suitable Canva design exists.
- [ ] Hero must show **ALL product items**, not a subset. A bundle of 8 forms shows 8 pages, not 4.
- [ ] Minimum resolution: **3000px** on the longest side.

## 5. Images

- [ ] **3 images** prepared, matching rank order:
  - Rank 1: Hero thumbnail.
  - Rank 2: "Canva Basics" (from `DAFx_dsWpTA` page 3).
  - Rank 3: "Please Note" disclaimer (from `DAFx_dsWpTA` page 5).
- [ ] After every image swap, **verify all 3 ranks exist** via GET — not just R1. Deleting R1 can shift ranks or leave R2/R3 missing.
- [ ] Upload format: `multipart/form-data`.

## 6. Digital File (PDF)

- [ ] Delivery PDF attached with correct filename.
- [ ] PDF links use **`/d/{shortcode}`** format only — never `/design/.../view` or `/design/.../edit`.
- [ ] Shortcode verified by clicking — must show "Use this template".

## 7. API Call Format

- [ ] Listing create/update uses `application/x-www-form-urlencoded` (not JSON).
- [ ] Tags passed as comma-separated string (not array).
- [ ] Using **PATCH** for updates (never PUT — returns 404).
- [ ] Auth header: `x-api-key: {keystring}:{shared_secret}`, `Authorization: Bearer {access_token}`.

## 8. Post-Publish Verification

- [ ] Run `python scripts/verify_listing.py {listing_id}` immediately after publish.
- [ ] GET `/listings/{id}/images` — confirm image count and rank order.
- [ ] GET `/shops/{id}/listings/{id}/files` — confirm PDF attached.
- [ ] Show raw API response — do not mark done without API confirmation.

---

**If any item fails**: stop, fix, re-check from the top. Never push a listing with a known SOP violation.
