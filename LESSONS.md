# Lessons Learned

A living document updated every session. Most recent entries first.

---

## AI Brain Principles

- **Give Claude tools shaped to its abilities** — not the easiest to implement. A well-designed tool that the model understands beats a quick hack it struggles with.
- **Progressive disclosure** — skill files that reference other files recursively beats a bloated system prompt. Let the agent discover context layer by layer instead of front-loading everything.
- **Revisit tool design as model capabilities improve** — what helped before can become a constraint. TodoWrite kept early models on track but later made them rigid; it was replaced with Tasks.
- **Always use the right tool for the job** — Canva MCP for layout, Python for data, Claude for reasoning. Match the tool to the domain rather than forcing one tool to do everything.

---

### 2026-03-13 — Etsy Thumbnails

**Worked:**
- Canva MCP `get-design-thumbnail` returns real card artwork usable directly in Python — no screenshot hacks needed
- Canva `generate-design` produces good layout candidates when given detailed prompts with exact dimensions, colors, and element placement
- Existing 2+ year old Etsy listing designs are the right base — clone and swap card images rather than building from scratch
- Canva brand gradient confirmed: `#00C4CC` to `#7D2AE8` left to right

**Failed:**
- Python/Pillow card cropping is fragile — Canva exports both pages side by side so crops give wrong dimensions without careful math
- Iterating PIL compositing is slow — Canva native editing is faster and more accurate for layout work
- Rebuilding thumbnails from scratch wastes hours when proven designs already exist

**Next:**
- Open existing proven listing design (`DAFx_dsWpTA` or `DAFxukwKaiA`) in Canva MCP
- Clone it, swap card images with real dark `DAHD07F9MsY` and light `DAHD15IcxRs` designs
- Complete all 6 listing thumbnails using clone-and-swap method only

---

### 2026-03-13 — Light Business Card & Delivery PDF Pipeline

**Worked:**
- Canva MCP `generate-design` with highly specific layout prompts (exact element positions, colors, font styles) produces much better results than vague descriptions. Including negative instructions ("no geometric shapes, no patterns") is critical.
- Two-step Ideogram + Pillow composite for circle photos: Ideogram generates the photo (1:1 ratio), Pillow crops to circle mask, draws gold border ring, composites onto HTML-rendered card. Clean separation of concerns.
- Multi-product `template_links` dict with named keys (`business_card`, `business_card_light`) scales cleanly — `create_pdf()` renders one link box per product with proper labels and fallback to legacy format.
- Canva MCP grouped element IDs (triple-segment like `page-group-element`) work with `find_and_replace_text` even when `replace_text` fails with "not_found" on the same element.

**Failed:**
- First Canva `generate-design` round produced geometric/abstract designs with no tattoo relevance despite requesting "tattoo studio". Needed a second round with explicit negative constraints and style references ("Shoreditch/Brooklyn luxury meets ink artistry").
- Canva MCP has no clone/duplicate design tool — wasted time looking for it. Must generate fresh or user copies manually in Canva UI.
- `replace_text` on grouped elements returns "not_found" when using the 2-segment page-element ID format. Must use the full 3-segment page-group-element ID from the richtexts response.

**Next:**
- Build a prompt template library for Canva `generate-design` by niche (tattoo, nail, hair, etc.) with proven layout descriptions that work first time.
- Wire the light card PDF into Etsy digital file uploads alongside the dark version — buyers get both colour variants.
- Consider auto-generating both dark and light Canva designs in a single pipeline run using the `generate-design` → `create-design-from-candidate` → `start-editing-transaction` flow.

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
