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

## 4. Images

- [ ] **3 images** prepared, matching rank order:
  - Rank 1: Hero thumbnail (from `DAHDc0gyebE`).
  - Rank 2: "Canva Basics" (from `DAFx_dsWpTA` page 3).
  - Rank 3: "Please Note" disclaimer (from `DAFx_dsWpTA` page 5).
- [ ] Hero thumbnail is **3000 x 3000 px** with shadow applied.
- [ ] Upload format: `multipart/form-data`.

## 5. Digital File (PDF)

- [ ] Delivery PDF attached with correct filename.
- [ ] PDF links use **`/d/{shortcode}`** format only — never `/design/.../view` or `/design/.../edit`.
- [ ] Shortcode verified by clicking — must show "Use this template".

## 6. API Call Format

- [ ] Listing create/update uses `application/x-www-form-urlencoded` (not JSON).
- [ ] Tags passed as comma-separated string (not array).
- [ ] Using **PATCH** for updates (never PUT — returns 404).
- [ ] Auth header: `x-api-key: {keystring}:{shared_secret}`, `Authorization: Bearer {access_token}`.

## 7. Post-Publish Verification

- [ ] Run `python scripts/verify_listing.py {listing_id}` immediately after publish.
- [ ] GET `/listings/{id}/images` — confirm image count and rank order.
- [ ] GET `/shops/{id}/listings/{id}/files` — confirm PDF attached.
- [ ] Show raw API response — do not mark done without API confirmation.

---

**If any item fails**: stop, fix, re-check from the top. Never push a listing with a known SOP violation.
