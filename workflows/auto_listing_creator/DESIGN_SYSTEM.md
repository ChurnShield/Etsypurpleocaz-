# PurpleOcaz Design System

Single source of truth for all product image generation.
Every renderer (Gemini AI, Pillow, HTML/Playwright) MUST follow these rules.

Source: `tools/brand_reference.py` (extracted from live PurpleOcaz Etsy store)

---

## Brand Colors (NON-NEGOTIABLE)

| Token | Hex | Usage |
|-------|-----|-------|
| `brand_purple` | `#6B3E9E` | Bottom banners, accent lines, highlights |
| `brand_purple_light` | `#9B59B6` | Vibrant variant, secondary accents |
| `brand_lavender` | `#A78BFA` | Ebook accent, soft UI elements |
| `hero_bg` | `#F5F5F5` | Hero image background (light warm gray) |
| `note_bg` | `#F8F6F3` | Note page background |
| `card_bg` | `#FFFFFF` | ALL certificate/card backgrounds |
| `badge_dark` | `#2C2C2C` | Badge circles (NOT orange) |
| `text_dark` | `#2C2C2C` | Primary text on cards |
| `text_light` | `#FFFFFF` | Text on purple/dark banners |
| `text_gray` | `#999999` | Field labels (TO:, FROM:) |
| `field_line` | `#CCCCCC` | Form field underlines |

### Color Rules

- Banner color is ALWAYS `#6B3E9E` (deep purple), NEVER black
- Cards are ALWAYS pure white `#FFFFFF`, NEVER cream/ivory/off-white
- Badge is ALWAYS dark `#2C2C2C`, NEVER orange
- Accents are ALWAYS purple, NEVER gold, NEVER orange, NEVER red
- Background is ALWAYS light warm gray `#F5F5F5`, NEVER dark/black/beige

---

## Typography

| Role | Primary Font | Fallback | Size | Color |
|------|-------------|----------|------|-------|
| Script heading | Great Vibes | Playfair Display italic | 72-120pt | `#2C2C2C` |
| Business name | Helvetica Neue Bold | Montserrat 700 | 22-28pt | `#2C2C2C` |
| Field labels | Helvetica Neue | Montserrat 400 | 16-18pt | `#999999` |
| Banner title | Helvetica Neue Bold | Montserrat 700 | 60-80pt | `#FFFFFF` |
| Banner subtitle | Helvetica Neue | Montserrat 400 | 18-22pt | `#FFFFFF` |
| Body text | Helvetica Neue | Montserrat 400 | 10-24pt | `#2C2C2C` |
| Disclaimer | Helvetica Neue italic | Montserrat 400 italic | 12pt | `#999999` |

### System Font Fallbacks (when web fonts unavailable)

| Primary | System Fallback |
|---------|----------------|
| Great Vibes | LiberationSerif-Italic |
| Helvetica Neue Bold | DejaVuSans-Bold |
| Helvetica Neue | DejaVuSans |
| Montserrat | DejaVuSans |

---

## 5-Page Listing Structure

| Page | Name | Type |
|------|------|------|
| 1 | Hero | Lifestyle flat-lay mockup with product cards |
| 2 | Note | "Please note" disclaimer (digital product notice) |
| 3 | Instruction | Template instruction mockup (drag & drop guide) |
| 4 | Print | Print mockup (print at home / print shop) |
| 5 | Bonus | Free Canva Basics ebook mockup |

---

## Hero Image (Page 1) Spec

### Canvas
- Working size: 2000x1500 px
- Final Etsy size: 2250x3000 px (4:3 portrait)
- DPI: 300 for print quality

### Background
- Color: `#F5F5F5` (light warm gray)
- Texture: subtle canvas/paper grain
- Lighting: soft even studio light, gentle shadows under objects

### Certificate Card(s)
- Background: `#FFFFFF` (pure white, NEVER cream)
- Border: none (clean edges)
- Position: center, slightly overlapping if two cards
- Orientation: landscape 2:1 ratio
- Shadow: soft drop shadow 5-8px, 20% opacity
- Top photo strip: 4 niche-relevant photos, tight spacing, 8px gaps, rounded 12px
- Header: Great Vibes cursive script, 72pt, `#2C2C2C`
- Fields: TO:, FROM:, AMOUNT:, EXPIRES: with thin 1px `#CCCCCC` underlines
- Disclaimer: 12pt italic `#999999`
- Footer: 4x 24px circle icons (email, phone, map, globe) + contact text 10pt

### Bottom Banner
- Height: 220px
- Color: `#6B3E9E` (deep purple)
- Main text: 80pt white bold sans-serif (product title)
- Sub text: 22pt white uppercase (selling tagline)
- Canva badge: bottom-right, `#2C2C2C` dark circle, 180px diameter, "EDIT IN CANVA"

### Props (Flat-Lay)
Standard props on EVERY hero:
- Top-left: small round green potted succulent (~300px)
- Bottom-left: white ceramic coffee cup with latte-art foam swirl (~280px)
- Top-right: eucalyptus branch or green leaves
- Bottom-right: rose-gold pen and/or marble pen

Niche-specific extras (ADD to standard, don't replace):
- Tattoo: flash art sheet, ink bottle
- Nail: polish bottles (pink, red, nude), nail art gems
- Hair: professional scissors, fine-tooth comb, hair oil
- Beauty: compact mirror, makeup brushes fanned, perfume
- Spa: lit white candle, rolled white towels, bath salts

---

## Design Exceptions

Some product types have UNIQUE designs that override the default white-card look:

### Appointment Card (Torn Paper Design)
- See: `design_specs/book_appointment_card.json`
- Cards are BLACK background with torn/ripped paper edge revealing white
- This is the ONE exception where cards are not white
- The torn paper effect is the signature design element
- Bottom banner still uses `#6B3E9E` purple

### All Other Products
- Follow the standard white card + purple banner design above

---

## Gemini Prompt Alignment Checklist

When building Gemini prompts, verify:

- [ ] Background is `#F5F5F5` light warm gray (NOT dark, NOT beige/craft paper)
- [ ] Cards are `#FFFFFF` pure white (unless appointment card)
- [ ] Banner is `#6B3E9E` deep purple (NOT black)
- [ ] Badge is `#2C2C2C` dark circle (NOT orange)
- [ ] Props include succulent + coffee cup + eucalyptus + pen
- [ ] Niche props ADD to standard props (don't replace)
- [ ] Script heading uses Great Vibes or equivalent cursive
- [ ] No gold accents, no orange accents, no red accents
- [ ] Fields use `#999999` gray labels with `#CCCCCC` underlines

---

## File Responsibility Map

| File | What it controls |
|------|-----------------|
| `brand_reference.py` | Source of truth - colors, typography, layout specs |
| `DESIGN_SYSTEM.md` | Human-readable version of the brand reference |
| `design_specs/*.json` | Per-product-type design blueprints |
| `gemini_image_client.py` | AI generation prompts (must match brand) |
| `png_renderer.py` | Pillow fallback renderer (must match brand) |
| `html_templates.py` | HTML template renderer (must match brand) |
| `design_constants.py` | Shared dimensions, paths, color constants |
| `tier_config.py` | Routes products to Tier 1 (Gemini) or Tier 2 (HTML) |
