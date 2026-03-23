# PurpleOcaz Canva MCP — Element ID Spec

Design element IDs extracted via `start-editing-transaction` inspection.
These IDs are stable across editing sessions and are required for `update_fill` / `replace_text` operations.

---

## DAHD07F9MsY — Tattoo Dark Business Card (Master)

**Pages:** 2 (Front + Back), 336 x 192 Canva units

### Page 1 (Front) — `PBwdJPdRSxNJvVSz`

| Element | Type | Element ID | Notes |
|---------|------|------------|-------|
| Circular image frame | SHAPE (image fill) | `PBwdJPdRSxNJvVSz-LBdTn8WTgTDmwTJt` | **Primary swap target.** 139.7 x 139.7, editable. Default asset: `MAHD042u66o` |
| Gold circle border | SHAPE | `PBwdJPdRSxNJvVSz-LBDV32bNtY4Kg4Yq` | 160.7 x 160.7, wraps around image frame. Not editable for fill. |
| "Elegant Tattoo Studio" | TEXT | `PBwdJPdRSxNJvVSz-LBrvBjWP7lbLwjst` | Headline, top-left |
| "Artistry on Skin..." | TEXT | `PBwdJPdRSxNJvVSz-LBkn3CS2rvjBZFQt` | Tagline, below headline |

### Page 2 (Back) — `PBrvKJcW6wxxWwPM`

| Element | Type | Element ID | Notes |
|---------|------|------------|-------|
| "YOUR STUDIO NAME" | TEXT | `PBrvKJcW6wxxWwPM-LBhr4qx1CW3DQxQ8-LBwpRDw27BMXskdJ` | 3-segment ID (grouped) |
| "Your Address..." | TEXT | `PBrvKJcW6wxxWwPM-LBhr4qx1CW3DQxQ8-LBRz14HBv6yS2Bff` | 3-segment ID (grouped) |
| "Phone: ..." | TEXT | `PBrvKJcW6wxxWwPM-LBTG2FNB7SMQyjbK-LBMRxzlHxlWvj5Kt` | 3-segment ID (grouped) |
| "Email: ..." | TEXT | `PBrvKJcW6wxxWwPM-LBTG2FNB7SMQyjbK-LBLwcm6P5l6KvGX4` | 3-segment ID (grouped) |
| "Website / Instagram" | TEXT | `PBrvKJcW6wxxWwPM-LBTG2FNB7SMQyjbK-LBWrFHQp0vYyWJLd` | 3-segment ID (grouped) |
| Small decorative shape | SHAPE | `PBrvKJcW6wxxWwPM-LBn4LT9X7LgG8d7T` | 10.2 x 10.2 |

---

## swap_card_images Tool

**Location:** `purpleocaz-canva-mcp/src/tools/swap-card-images.ts`

### What it does

1. Reads a local image file
2. Uploads it to Canva as an asset via REST API (with auto token refresh on 401)
3. Returns `{ asset_id, design_id, element_id }` for use with MCP editing tools

### Usage

```bash
# Step 1: Upload image and get asset_id
node dist/tools/swap-card-images.js <image_path> [design_id]

# Step 2: Use Canva MCP tools to swap
# start-editing-transaction → update_fill → commit-editing-transaction
```

### Why two steps?

The Canva REST editing API (`/designs/{id}/editing_sessions`) returns 404.
Editing transactions must go through the Canva MCP tools, which are only
available within a Claude Code session. The TypeScript tool handles the
asset upload (REST), and the MCP tools handle the design editing.

### Tested

- 2026-03-23: Successfully swapped image on `DAHD07F9MsY` page 1
  - Uploaded `assets/photos/tattoo_artist_studio/photo_1.jpg` → asset `MAHEwn7neUI`
  - `update_fill` on element `PBwdJPdRSxNJvVSz-LBdTn8WTgTDmwTJt` → success
  - Transaction cancelled (test only — master preserved)

---

## Design ID Registry

| Design | ID | Inspection Status |
|--------|----|-------------------|
| Dark business card | `DAHD07F9MsY` | Fully mapped (above) |
| Light business card | `DAHD15IcxRs` | Not yet inspected |
| Dark appointment card | `DAHENCEJGjk` | Not yet inspected |
| Light appointment card | `DAHENKnCBoM` | Not yet inspected |
| Hero thumbnail template | `DAHDc0gyebE` | Not yet inspected |
| Listing pages (5-page) | `DAFx_dsWpTA` | Not yet inspected |
| Tattoo Gift Certificate | `DAHEw2AXYFw` | Imported from PDF. Shortlink: `/d/YgKBSHN1dZ_U8qf` |
