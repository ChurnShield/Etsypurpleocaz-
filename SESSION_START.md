# Session Quick Resume

Last updated: 2026-03-15

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

## purpleocaz-canva-mcp (NEW — 2026-03-15)

TypeScript MCP server at `/root/NEW-AI-PROJECT/purpleocaz-canva-mcp/`

**Slash commands:**
- `/export-full-card <designId> [page]` — export full design PNG to Spaces + Canva asset
- `/etsy-shadow <spaces_key>` — apply Etsy drop shadow (blur=12, opacity=0.75, asymmetric padding)
- `/etsy-angled <spaces_key>` — angled -5deg lifestyle shadow variant

**Quick test:**
```bash
cd /root/NEW-AI-PROJECT/purpleocaz-canva-mcp
npx tsx src/tools/render-tools.ts export-full DAHD07F9MsY 1
npx tsx src/tools/render-tools.ts etsy-shadow designs/DAHD07F9MsY/full_page1_1773531422649.png
```

**Spaces CDN:** `https://purpleocaz-assets.lon1.digitaloceanspaces.com/`

## Next Session Priorities

### Priority 1: Build weekly_review.py
Build `scripts/weekly_review.py` that:
1. Reads Google Sheet queue — counts DONE/PENDING/FAILED
2. Reads CHANGELOG.md — summarises last 7 days of entries
3. Reads LESSONS.md — shows last 5 lessons added
4. Compares listings count against the 16-week plan targets
5. Writes plain English summary to Google Sheet tab "WEEKLY_REVIEW" with today's date
6. Add to cron: every Monday at 7:30am after digest.py

### Priority 2: Session end hook
Create `.claude/hooks/stop.sh` that prompts the session end checklist:
1. Did you update CHANGELOG.md?
2. Did you update LESSONS.md?
3. Did you update SESSION_START.md?
4. Is the Google Sheet queue updated?

### Priority 3: Canva token auto-refresh
Wire refresh token flow so expired access tokens auto-refresh using saved refresh token.

### Priority 4: Wire shadow tools into listing pipeline
Connect `/export-full-card` and `/etsy-shadow` into auto listing creator Phase 3.

### Priority 5: More kit products
- Appointment card, gift cert, price list, aftercare card
- Wire light card PDF into Etsy digital file uploads

## Etsy Drafts Created

- Draft ID `4471274562` (first run)
- Draft ID `4471271403` (second run)
