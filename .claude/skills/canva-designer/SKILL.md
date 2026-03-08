---
name: canva-designer
description: "Creates product images and designs using the two-tier image pipeline. Use when
              generating product mockups, exporting Canva designs, or creating listing visuals."
---

## Image Creation Protocol

When creating product images or working with designs:

1. Read `workflows/auto_listing_creator/tools/product_creator_tool.py` for the tier routing logic
2. Determine which tier to use based on the product requirements
3. Follow the niche-specific design guidelines

## Two-Tier Architecture

### Tier 1 — Nano Banana (Premium: Gemini AI + Editable PDF)

**Provider**: `workflows/auto_listing_creator/tools/gemini_image_client.py`

**Flow**:
1. Generate product mockup via Gemini 2.5 Flash image API
2. Composite text onto hero image using `text_compositor.py`
3. Create editable PDF with form fields via `editable_pdf_generator.py`

**Design Philosophy**:
- Flat-lay product photography (NOT graphic design posters)
- Warm beige/cream textured kraft paper background
- Niche-specific props (tattoo ink, nail polish, scissors, etc.)
- Blank cards — text added by compositor, never by Gemini

### Tier 2 — HTML/Playwright (Standard)

**Provider**: `workflows/auto_listing_creator/tools/image_renderer.py`

**Flow**:
1. Generate HTML template via `html_templates.py`
2. Render to PNG using Playwright screenshot
3. Create title band, badge, and Page 2 infographic

**Components**:
- `render_template()` — Main product template
- `render_band()` — Title/tagline banner
- `render_badge()` — Circular "EDIT IN CANVA" badge
- `create_page2()` — "What You Get" infographic
- `create_pdf()` — Branded PDF

## Canva Export Integration

**Tool**: `workflows/auto_listing_creator/tools/canva_export_tool.py`

- Search user's Canva designs by keyword
- Export all pages as separate PNGs (up to 5 pages per design)
- Export full design as PDF
- Handles OAuth token refresh automatically

## SVG Botanical Design System

**Location**: `workflows/auto_listing_creator/tools/svg_botanical/`

- `ai_design_generator_tool.py` — Fine-line botanical tattoo designs
- Providers: Gemini (default) or Replicate (FLUX.1)
- `svg_generator_tool.py` — Vectorize PNG to SVG via potrace
- 150+ pre-defined botanical categories

## Design Constants

**Location**: `workflows/auto_listing_creator/tools/design_constants.py`

- Export dimensions: 2250x3000 px (portrait)
- PurpleOcaz brand colors: Purple (#663399), Dark BG, Orange accent
- Custom TTF font system

## Hard Rules

- NEVER skip `logger.flush()` in the finally block
- NEVER hardcode API keys or model names — import from `config.py`
- Always validate generated images exist and are valid before proceeding
- Use `ExecutionLogger` with `try/finally` for all image generation tools
- Follow niche-specific prop guidelines for Tier 1 generation
