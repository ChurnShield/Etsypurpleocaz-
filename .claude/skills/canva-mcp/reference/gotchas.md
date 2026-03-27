# Canva MCP Gotchas

> **Source of truth:** `.claude/rules/canva.md` is authoritative for all Canva rules (folder IDs, design IDs, element limits, link format, colour palettes). This file adds prose context and failure narrative only — it does not replace or override rules/canva.md.

Every entry here caused a real production failure. Read before any Canva work.

---

## Editing Transactions

**One transaction per operation, always commit before next.**
Cascading failures happen when multiple uncommitted operations stack up. Front and back pages must be separate transactions.

**Canva REST editing API returns 404.**
The endpoint `/designs/{id}/editing_sessions` does not exist. All editing must go through MCP tools: `start-editing-transaction`, `perform-editing-operations`, `commit-editing-transaction`.

---

## Element Limitations

**`update_fill` only works on image/video containers.**
Shapes return "does not contain an editable fill." To change a shape's color: export and post-process the PNG. There is no API workaround.

**`insert_fill` always goes on TOP of z-stack.**
No z-order control exists. If you insert an image, it covers everything beneath it. Workaround: export the design and composite in post-processing.

**`update_fill` crop/zoom is uncontrollable.**
After swapping an image, internal crop and zoom may differ from the original. Always verify visually — do not trust the API response alone.

**Cannot insert new text elements.**
`insert_fill` only works for images/videos. If a design doesn't have enough text fields, pick a different template. Don't attempt workarounds.

**Curved text is permanent.**
The curve is baked into the container, not the text content. Replacing text doesn't straighten it. Wasted multiple transactions learning this.

**Grouped elements need 3-segment IDs.**
`replace_text` on grouped elements requires `page-group-element` format. Using 2-segment `page-element` returns "not_found". Get the full ID from the richtexts response.

**Always `format_text` after `replace_text`.**
When repurposing a heading element for body content, the original font size persists and causes overflow. Explicitly set `font_size` after every text replacement.

---

## generate-design

**Always produces personal business cards.**
Requesting "appointment card with form fields" produces a standard name+title business card. The AI interprets `business_card` type literally. Workaround: generate for aesthetic base, then restyle text via editing transactions.

**Use highly specific prompts.**
Include: exact hex color codes, style references (e.g., "Shoreditch/Brooklyn luxury"), illustration type (e.g., "botanical/floral tattoo"), and negative instructions ("no geometric shapes, no patterns"). Vague prompts produce generic results.

**Export candidates for review before editing.**
Save to Spaces CDN so Andy can review on phone. Never start editing without approval — prevents wasted transaction cycles.

---

## Preview & Thumbnails

**Preview URLs are auth-gated.**
`design.canva.ai/*` URLs redirect through authentication — WebFetch gets 403. Use `get-design-thumbnail` from MCP tools instead.

---

## Export

**Width must match aspect ratio.**
Non-matching width causes black borders or letterboxing. Omit width entirely for native dimensions. For listing pages, use `width=3000`.

**First export attempt used wrong fields.**
`quality: "pro"` is not a valid field. Response shape is `job.urls[0]` (plain string array), not `job.result.urls[0].url`. Always debug-dump actual API responses.

---

## Asset Upload

**Binary `application/octet-stream` only.**
JSON body with `upload_ref.type: "url"` returns 400 "Unsupported content type". Must use binary body with `Asset-Upload-Metadata` header containing base64-encoded name.

**Asset name max 50 characters.**
Longer names cause 400 "Invalid upload metadata header". Truncate with `.slice(-50)`.

---

## Shadows

**Never synthesize shadows programmatically.**
Pillow/Sharp shadow compositing (shadow rect → gaussian blur → composite) always looks like a hard black rectangle, not a natural shadow. Even with large padding, high blur sigma, and varying opacity.

**Canva templates with built-in flatlay shadows are the only approach that works.**
`DAHDc0gyebE` has natural shadow and depth built into the design. `update_fill` on card containers preserves the template's shadow. The template IS the shadow system.

**Uploading pre-shadowed cards via `update_fill` doesn't work.**
Canva's internal crop/zoom eats the shadow padding, making it invisible. The container is sized to the card, not card+shadow.

---

## Delivery Links

**USE `/d/{shortcode}` ONLY in delivery PDFs.**
- `/design/{id}/view` — looks safe but exposes the master design. NOT safe.
- `/design/{id}/edit` — gives buyer write access to master. NEVER use.
- Get the shortcode from Canva's "Share > Template link" feature.
- Verify: click the link — must show "Use this template", not open the editor.

**Fixed listings for reference:**
- Appointment card #4473444461: dark=`/d/Mol3iFDMHAATbQt`, light=`/d/UvTaJitKspzs1da`
- Business card #4472977919: dark=`/d/e21A6ZQJ3XcCIq-`, light=`/d/vyaBAtIupW1g7zH`

---

## Does Not Exist

These tools/features do NOT exist in Canva MCP. Don't search for them:
- No clone/duplicate design tool
- No `search-templates` tool
- No `search-elements` tool
- No z-order control for inserted elements
- No way to insert new text elements
- No way to control `update_fill` crop/zoom
