Run the full Etsy revenue pipeline or individual phases.

## Arguments
- No args: run the full pipeline (phases 1-4 in sequence)
- `trends`: run only Phase 1 (tattoo trend monitor)
- `listings`: run only Phase 2 (auto listing creator)
- `analytics`: run only the Etsy analytics dashboard
- `seo`: run only the SEO optimizer

## Before Running
1. First run `/check-api` to verify all API connections are configured
2. Ensure the virtual environment is active or use `python` from the project root

## Full Pipeline Execution (no args)

Run phases in this order, stopping if any phase fails:

### Phase 1: Trend Monitor
```bash
cd /home/user/Etsypurpleocaz- && python workflows/tattoo_trend_monitor/run.py
```
- Scans Google Trends + Etsy competitors
- Writes opportunities to Google Sheets tabs: "Tattoo Trends", "Tattoo Opportunities"
- If this fails, check Etsy API keys and Google Sheets credentials

### Phase 2: Listing Creator
```bash
cd /home/user/Etsypurpleocaz- && python workflows/auto_listing_creator/run.py
```
- Reads opportunities from Phase 1
- Generates SEO titles, descriptions, 13 tags per listing
- Auto-bundles into Starter Kit / Complete Bundle / Mega Pack
- Writes to "Listing Queue" sheet
- If Etsy OAuth tokens exist, also creates Etsy draft listings

### Phase 3: Analytics (optional, for existing shops)
```bash
cd /home/user/Etsypurpleocaz- && python workflows/etsy_analytics/run.py
```
- Pulls shop performance data
- Writes daily snapshots and top performers to Sheets

### Phase 4: SEO Optimizer (optional, for existing listings)
```bash
cd /home/user/Etsypurpleocaz- && python workflows/etsy_seo_optimizer/run.py
```
- Analyzes existing listings for SEO improvements

## After Running
1. Check Google Sheets for output in the relevant tabs
2. Use `/review-listings` to QA the generated listing content
3. Review execution logs if anything failed: query `data/system.db` execution_logs table
4. Update `tasks/todo.md` with progress

## Error Handling
- If a phase fails, report the error and stop — don't continue to next phase
- Check `data/system.db` execution_logs for detailed error context
- Common issues: missing API keys (run `/check-api`), rate limits (wait and retry)
