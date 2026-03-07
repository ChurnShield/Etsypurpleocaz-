# Tomorrow's Plan: First Revenue Pipeline Run

## The Goal
Go from zero to **published Etsy draft listings** generating passive income from digital products.

## What You Already Have (it's more than you think)
Your codebase has a **fully built 4-phase pipeline** that:
1. Finds trending product gaps competitors are selling that you're not
2. Uses Claude AI to write SEO-optimized listings with anti-gravity keywords
3. Auto-bundles products into Starter Kit / Complete / Mega Pack tiers
4. Publishes to Google Sheets queue AND creates Etsy draft listings

**The code is done. You just need to connect the APIs.**

---

## Step-by-Step Setup (in order)

### Step 1: Get Your API Keys (~20 min)

You need these 3 things connected:

| Service | What You Need | Where to Get It |
|---------|--------------|-----------------|
| **Anthropic** | API key | https://console.anthropic.com → API Keys |
| **Google Sheets** | Service account JSON + Spreadsheet ID | Google Cloud Console → Service Accounts |
| **Etsy** | API keystring + shared secret + shop ID | https://developers.etsy.com → Your Apps |

### Step 2: Configure Your .env (~5 min)

```bash
cp .env.example .env
# Then fill in:
ANTHROPIC_API_KEY=sk-ant-...
ETSY_API_KEYSTRING=your-keystring
ETSY_SHARED_SECRET=your-secret
ETSY_SHOP_ID=your-numeric-shop-id
GOOGLE_CREDENTIALS_FILE=google-credentials.json
GOOGLE_SPREADSHEET_ID=your-spreadsheet-id
```

### Step 3: Create Your Google Sheet (~2 min)

Create a new Google Sheet and share it with your service account email.
The pipeline will auto-create these tabs:
- **Tattoo Trends** — raw trend data
- **Tattoo Opportunities** — ranked product ideas
- **Listing Queue** — generated listings ready for review

### Step 4: Run the Trend Monitor (~3 min runtime)

```bash
source .venv/bin/activate
python workflows/tattoo_trend_monitor/run.py
```

This scans Google Trends + Etsy competitors and writes product opportunities
to your Sheet. **This is your idea engine.**

### Step 5: Run the Listing Creator (~5 min runtime)

```bash
python workflows/auto_listing_creator/run.py
```

This takes those opportunities and:
- Generates SEO titles, descriptions, 13 tags per listing
- Auto-bundles related products (Starter Kit, Complete Bundle, Mega Pack)
- Saves everything to "Listing Queue" sheet

### Step 6: Review & Publish

Check your Google Sheet "Listing Queue" tab. Each row is a complete listing:
- Title (SEO-optimized, max 140 chars)
- Description (7 sections: hook, what's included, how to edit, features, perfect for, FAQ, disclaimer)
- 13 tags (anti-gravity keyword formula)
- Price
- Product type

**Copy these into Etsy manually to start, or set up OAuth for auto-draft creation.**

---

## Optional: Auto-Publish to Etsy Drafts

To skip manual copy-paste and create drafts directly:

```bash
python workflows/etsy_analytics/etsy_oauth.py
# Follow the browser flow to authorize your app
# Saves token to workflows/etsy_analytics/etsy_tokens.json
```

Then re-run the listing creator — it will now create Etsy drafts automatically.

---

## The Wealth-Building Flywheel

Here's why this compounds:

```
Week 1:  Run pipeline → 10 listings + 3 bundles = 13 products
Week 2:  Run again   → 10 more + 3 bundles     = 26 products total
Week 4:  Run again   → algorithm sees catalog depth, ranks you higher
Week 8:  Run again   → 50+ products, bundles cross-sell, organic traffic grows
Week 12: SmallBrain kicks in → optimizes based on what's selling
```

**Key insight:** Every product costs you $0 after creation. Digital = infinite margin.
The more products, the more Etsy shows your shop. Bundles increase average order value.

---

## Niche Expansion (after tattoo is running)

Your system already supports 5 niches. Change one env var:

```bash
SEO_FOCUS_NICHE=nail    # or: hair, beauty, spa
```

Same pipeline, new market. Each niche has its own keyword research data built in.

---

## What NOT to Do

- Don't manually write listings (the AI does it better for SEO)
- Don't skip bundles (they increase AOV and catalog depth)
- Don't publish without reviewing (quality control matters)
- Don't run the same pipeline twice without checking for duplicates (the tool handles this, but verify)
- Don't auto-apply SmallBrain proposals (always review first)
