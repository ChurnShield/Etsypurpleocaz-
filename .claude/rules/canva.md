# Canva MCP Rules

Rules learned from production. Every one caused a real failure.

## Delivery Links — CRITICAL
- **USE `/d/{shortcode}` ONLY** in delivery PDFs.
- `/design/{id}/view` — exposes the master design. NOT safe.
- `/design/{id}/edit` — gives buyer write access to master. NEVER use.
- Get shortcode from Canva's "Share > Template link" feature.
- Verify by clicking — must show "Use this template", not the editor.

## Folder IDs — File Immediately After Creation
| Folder | ID |
|--------|----|
| Root (PurpleOcaz) | `FAHENpMANrQ` |
| Tattoo Masters | `FAHENuO2Vkc` |
| Listing Templates | `FAHENvJko1A` |
| Thumbnails / Hero | `FAHENqKrgvk` |

## Editing Transactions
- **One transaction per logical change, commit before next.** Prevents cascading failures.
- **One transaction per page side** for multi-page designs. Front and back separately.
- Canva REST editing API (`/designs/{id}/editing_sessions`) returns 404 — use MCP tools only.

## Element Limitations
- `update_fill` only works on **image/video containers**, not shapes. Shapes return "does not contain an editable fill."
- `insert_fill` always goes on TOP of z-stack. No z-order control. Workaround: export and post-process.
- `update_fill` internal crop/zoom is uncontrollable. Always verify visually after swap.
- **Cannot insert new text elements.** Only `insert_fill` for images/videos. If you need more text fields, use a different template.
- Curved text is permanent — curve is baked into the container, not the text.
- `replace_text` on grouped elements needs **3-segment IDs** (`page-group-element`). 2-segment returns "not_found."
- After `replace_text`, always `format_text` with explicit `font_size`. Repurposed headings overflow.

## generate-design
- Always produces **personal business cards**. Cannot create appointment/booking cards.
- Workaround: generate for aesthetic base, then restyle via editing transactions.
- Use highly specific prompts: hex codes, style references, negative instructions.
- Export candidates to Spaces CDN for Andy to review before editing.

## Does Not Exist
- No clone/duplicate design tool. Generate fresh or user copies in Canva UI.
- No `search-templates` or `search-elements` tool. Don't promise search.
- Preview URLs (`design.canva.ai/*`) are auth-gated — WebFetch gets 403. Use `get-design-thumbnail`.

## Export
- Export width must match aspect ratio. Non-matching width causes black borders/letterboxing.
- Omit width for native dimensions.
- Generic listing pages: export at `width=3000`.
- Asset upload: binary `application/octet-stream` with `Asset-Upload-Metadata` header (base64). NOT JSON. Name max 50 chars.

## Shadows
- Never synthesize shadows programmatically (Pillow/Sharp). Always looks fake.
- Use Canva templates with built-in flatlay shadows. The template IS the shadow system.
