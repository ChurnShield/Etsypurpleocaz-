# PurpleOcaz Design Rules

Load this skill before any design creation, hero thumbnail build, or listing image work.

---

## Tattoo Niche Palette

| Token | Hex | Usage |
|-------|-----|-------|
| Text / Dark | `#1A1A1A` | Headlines, body copy, dark card backgrounds |
| Gold accent | `#C9A96E` | Borders, foil details, decorative elements |
| Background | `#FFFFFF` | Card backgrounds, listing image backgrounds |
| Cream alt | `#F5F0EB` | Light card variant backgrounds |
| Black alt | `#000000` | Full-black card variant backgrounds |

Never introduce colours outside this palette without Andy's approval.

---

## Thumbnail Standards

- **Dimensions**: minimum 3000px on the longest side. Match the Canva design's native aspect ratio to avoid black borders.
- **Card placement**: centred on canvas, natural flat-lay shadow applied via Canva template (never Pillow/Sharp).
- **Shadow source**: Canva template `DAHDc0gyebE` — the template IS the shadow system.
- **Post-export pixel swap**: brightness < 180 below y = 82% becomes `#000000` (Sharp).
- **Export width**: native 1587 x 2245 for hero template; `width=3000` for high-res listing upload.
- **Canva first**: always check existing Canva assets in Thumbnails/Hero folder (`FAHENqKrgvk`) before generating with Pillow. Only use Pillow when no suitable Canva design exists.
- **Show all items**: hero thumbnails for bundles must display ALL included products, not a subset.

---

## Font Rules

- **Primary heading**: Use the font already set in the Canva template — do not override.
- **After `replace_text`**: always follow with `format_text` setting explicit `font_size` to prevent overflow.
- **Curved text**: cannot be un-curved — the curve is baked into the container.
- **New text elements**: cannot be inserted via MCP. If more text fields are needed, use a different template.

---

## Listing Image Ranks

| Rank | Source Design | Page | Content |
|------|---------------|------|---------|
| 1 | `DAHDc0gyebE` | 1 | Hero thumbnail — product-specific, swap card images per product |
| 2 | `DAFx_dsWpTA` | 3 | "Canva Basics" — free e-book promo (reusable across all listings) |
| 3 | `DAFx_dsWpTA` | 5 | "Please Note" — digital product disclaimer (reusable across all listings) |

- `DAHDc0gyebE` has **only 1 page**. Pages 2/3 do not exist.
- `DAFx_dsWpTA` is a 5-page design. Only pages 3 and 5 are used for listings.

---

## Canva Folder IDs

| Folder | ID |
|--------|----|
| Root (PurpleOcaz) | `FAHENpMANrQ` |
| Tattoo Masters | `FAHENuO2Vkc` |
| Listing Templates | `FAHENvJko1A` |
| Thumbnails / Hero | `FAHENqKrgvk` |

File designs into the correct folder immediately after creation.

---

## Proven Design IDs

| Design | ID | Notes |
|--------|----|-------|
| Dark business card | `DAHD07F9MsY` | page 1 |
| Light business card | `DAHD15IcxRs` | page 1 |
| Dark appointment card | `DAHENCEJGjk` | black / gold / botanical |
| Light appointment card | `DAHENKnCBoM` | cream / charcoal / gold / botanical |
| Hero thumbnail template | `DAHDc0gyebE` | flat-lay with natural shadows |
| Listing pages (5-page) | `DAFx_dsWpTA` | generic pages for all listings |

Never create a new template when an existing proven design covers the use case.
