# =============================================================================
# workflows/etsy_analytics/validators/listings_fetched_validator.py
#
# Validates Phase 1 output — checks that we received listings from Etsy.
# needs_more = False: if the API fails, retrying blindly won't help.
# =============================================================================

import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
_workflow = os.path.dirname(_here)
_project_root = os.path.dirname(os.path.dirname(_workflow))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_validator import BaseValidator


class ListingsFetchedValidator(BaseValidator):

    def validate(self, data, context=None):
        issues = []

        if not isinstance(data, dict):
            return {
                "passed": False,
                "issues": ["Data is not a dict"],
                "needs_more": False,
                "validator_name": self.get_name(),
                "metadata": {},
            }

        listings = data.get("listings", [])
        shop     = data.get("shop", {})

        if not isinstance(listings, list):
            issues.append("listings is not a list")
        elif len(listings) == 0:
            issues.append("No listings returned from Etsy API")

        if not shop:
            issues.append("No shop data returned")

        passed = len(issues) == 0

        return {
            "passed":         passed,
            "issues":         issues,
            "needs_more":     False,
            "validator_name": self.get_name(),
            "metadata": {
                "listing_count": len(listings) if isinstance(listings, list) else 0,
                "has_shop_data": bool(shop),
            },
        }
