Review generated Etsy listing content for quality, SEO compliance, and anti-gravity strategy alignment.

## Steps

1. Find the most recent listing output by checking:
   - Google Sheets "Listing Queue" tab (if `GOOGLE_SPREADSHEET_ID` is set)
   - Or check execution logs in `data/system.db` for the latest `auto_listing_creator` run
   - Or check any local output files in `workflows/auto_listing_creator/output/`

2. For each listing, run the **listing-reviewer agent** checklist:

### SEO & Keywords (13-tag formula)
- [ ] Exactly 13 tags present
- [ ] Tags split across: core product, format/modifier, buyer intent, adjacent niche, seasonal
- [ ] Title uses long-tail keywords (not generic like "template" alone)
- [ ] Title is under 140 characters
- [ ] Tags include `bundle_tags` for automatic grouping

### Content Quality (dwell-time optimization)
- [ ] Description has PERFECT FOR section
- [ ] Description has FAQ section
- [ ] Description has use-case / how-to-edit section
- [ ] Description has what's included section
- [ ] Getting Started guide referenced

### Bundle Compliance
- [ ] Bundles grouped into Starter Kit / Complete Bundle / Mega Pack tiers
- [ ] Each bundle has minimum 3 components (`MIN_BUNDLE_SIZE`)
- [ ] Bundle references its component listings for cross-pollination

### Anti-Gravity Alignment
- [ ] Keywords target the configured niche (check `SEO_FOCUS_NICHE`)
- [ ] Long-tail keywords used (not competing on generic high-volume terms)
- [ ] Price is competitive for digital products in this niche

3. Score each listing: PASS / NEEDS WORK / FAIL
4. For any NEEDS WORK or FAIL, provide specific fix suggestions
5. Summarize: X listings reviewed, Y passed, Z need work
6. Update `tasks/todo.md` with review results
