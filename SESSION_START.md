# Session Quick Resume

Last updated: 2026-03-13

---

## Canva Designs — Tattoo Studio Business Kit

| Design | ID | Type | Buyer URL |
|--------|----|------|-----------|
| Business Card (Dark) | `DAHD07F9MsY` | Master template | https://www.canva.com/d/e21A6ZQJ3XcCIq- |
| Business Card (Light) | `DAHD15IcxRs` | Master template | https://www.canva.com/d/vyaBAtIupW1g7zH |
| Appointment Card | `DAHDolzpMTY` | Master template | https://www.canva.com/d/yz8a1A3If14wZfp |

## .env Design IDs

```
TATTOO_MASTER_DESIGN_ID=DAHD07F9MsY
TATTOO_MASTER_LIGHT_DESIGN_ID=DAHD15IcxRs
```

## TEMPLATE_LINKS (run_single_listing.py)

```python
TEMPLATE_LINKS = {
    "business_card": "https://www.canva.com/d/e21A6ZQJ3XcCIq-",
    "business_card_light": "https://www.canva.com/d/vyaBAtIupW1g7zH",
}
```

## Key Files Changed This Session

| File | What |
|------|------|
| `workflows/auto_listing_creator/templates/business_card_light.html` | Light card HTML template (cream/charcoal/gold) |
| `workflows/auto_listing_creator/tools/image_renderer.py` | Multi-product delivery PDF, `render_business_card_light()` with Ideogram circle photo |
| `workflows/auto_listing_creator/tools/product_creator_tool.py` | Both tiers render light card variant, pass ideogram_api_key |
| `workflows/auto_listing_creator/tools/ideogram_image_client.py` | Two-card flatlay prompt, #F2C4CE banner color |
| `workflows/auto_listing_creator/run_single_listing.py` | TEMPLATE_LINKS with both Canva buyer URLs |

## Delivery PDF

Tested and working. Shows two link boxes:
- **Business Card Template (Dark)** with clickable Canva URL
- **Business Card Template (Light)** with clickable Canva URL

Test file: `/root/NEW-AI-PROJECT/exports/delivery_test.pdf`

## Etsy Drafts Created

- Draft ID `4471274562` (first run)
- Draft ID `4471271403` (second run)

## Next Steps

- Wire light card PDF into Etsy digital file uploads
- Add more products to the kit (appointment card, gift cert, price list, aftercare)
- Run full pipeline test with Ideogram two-step process
- Build Canva prompt template library per niche
