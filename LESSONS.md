# Lessons Learned

A living document updated every session. Most recent entries first.

---

### 2026-03-11 — Canva MCP Integration & Design Editing

**Worked:**
- Applying gold color scheme to an existing template (DAHCEgOLAtA) in one bulk operation across both pages — 15 text elements formatted in a single transaction. Start from a solid structure and restyle, don't rebuild.
- Uploading assets via `upload-asset-from-url` to bring external images into a design when `update_fill` fails due to missing media bundles.
- `insert_fill` with explicit width/height/position creates clean new image elements without the cropping issues that `update_fill` + resize causes on existing containers.
- One transaction per logical change, commit before next — prevents cascading failures and makes rollback trivial.

**Failed:**
- Repurposing curved text elements — the curve is baked into the element container, not the text. Replacing text doesn't straighten it. Wasted multiple transactions discovering this.
- `update_fill` on existing image containers causes internal cropping that can't be controlled via the API. The fill zoom/offset is set internally by Canva.
- Trying to build a complex appointment card layout with only 3 text elements. The API cannot insert new text elements — only images/videos via `insert_fill`. Should have flagged this limitation immediately instead of attempting workarounds.
- Moving the logo placeholder repeatedly instead of leaving it in its original position. The user had to correct this multiple times.
- Searching for Canva template library elements — no `search-templates` or `search-elements` tool exists. Don't promise what the API can't do.

**Next:**
- For complex Canva layouts requiring many text elements, start from a template that already has the fields built in and restyle it (the DAHCEgOLAtA approach).
- Investigate whether Canva's `generate-design` or `generate-design-structured` tools could scaffold appointment card layouts with form fields.
- Consider building a prompt library for common Canva design patterns (appointment cards, business cards, social posts) that maps required elements to API capabilities.
- Always audit element limitations before proposing a design plan — count available text elements vs required, flag gaps upfront.

---

### 2026-03-11 — Strategic Ideas

**Next:**
- Sub-agent architecture is the logical next layer above Big Brain/Small Brain. Orchestrator assigns tasks to specialist agents (Research, Design, Listing, QA, Outreach, Analytics) — all propose, Andy approves. Dedicated architecture session needed before building.
- Pre-stock Canva asset folders per niche before design sessions — MCP `insert_fill` can leverage these without creating from scratch. Dog grooming assets needed before next week's session.
