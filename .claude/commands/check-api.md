Verify all API keys and connections are configured before running the Etsy pipeline.

## Steps

1. Check that `.env` file exists (if not, tell user to run `cp .env.example .env`)
2. Load and verify these required environment variables are set (non-empty, not placeholder values):
   - `ANTHROPIC_API_KEY` — must start with `sk-ant-`
   - `ETSY_API_KEYSTRING` — must not be empty or `your-etsy-keystring-here`
   - `ETSY_SHARED_SECRET` — must not be empty or `your-etsy-secret-here`
   - `ETSY_SHOP_ID` — must not be empty or `your-shop-id-here`
   - `GOOGLE_SPREADSHEET_ID` — must not be empty or `your-spreadsheet-id-here`
   - `GOOGLE_CREDENTIALS_FILE` — file must exist on disk
3. Check optional but useful keys:
   - `GEMINI_API_KEY` — needed for Tier 1 AI image generation (warn if missing, not blocking)
4. Test Anthropic API connectivity: `python -c "import anthropic; c = anthropic.Anthropic(); print(c.models.list())"`
   - If this fails, report the specific error (invalid key, network issue, etc.)
5. Check if Google credentials JSON file exists and is valid JSON
6. Check if Etsy OAuth tokens exist at `workflows/etsy_analytics/etsy_tokens.json`
   - If missing, remind user to run `python workflows/etsy_analytics/etsy_oauth.py`
   - This is optional — pipeline works without it (just can't auto-create drafts)
7. Print a summary table:

```
API Status:
  Anthropic .... [OK] / [MISSING] / [INVALID]
  Etsy ......... [OK] / [MISSING] / [NO OAUTH]
  Google Sheets . [OK] / [MISSING] / [NO CREDS FILE]
  Gemini ....... [OK] / [SKIP - optional]
```

8. If any required key is missing, point the user to the relevant setup step in `TOMORROW_PLAN.md`
