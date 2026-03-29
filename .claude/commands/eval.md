---
description: Run full verification on an Etsy listing
---
Full listing evaluation for $ARGUMENTS:
1. Refresh Etsy token first
2. python3 scripts/verify_listing.py $ARGUMENTS --bundle
3. python3 scripts/evaluate_listing.py $ARGUMENTS
4. Report: which checks passed, which failed, specific fixes needed
Do NOT mark anything as done — just report.
