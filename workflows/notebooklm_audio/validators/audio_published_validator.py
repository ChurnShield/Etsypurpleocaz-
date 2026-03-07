import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(_here)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_validator import BaseValidator


class AudioPublishedValidator(BaseValidator):
    """Validates that audio products were published successfully."""

    def validate(self, data, context=None):
        issues = []

        if not isinstance(data, dict):
            return {
                "passed": False,
                "issues": ["Expected a dict with publishing results"],
                "needs_more": False,
                "validator_name": self.get_name(),
                "metadata": {},
            }

        queue_rows = data.get("queue_rows", 0)
        drafts_created = data.get("drafts_created", 0)
        draft_errors = data.get("draft_errors", 0)
        total = data.get("total_products", 0)

        if queue_rows == 0 and drafts_created == 0:
            issues.append("No products published to Sheets or Etsy")

        if draft_errors > 0:
            issues.append(f"{draft_errors} Etsy draft creation error(s)")

        return {
            "passed": queue_rows > 0 or drafts_created > 0,
            "issues": issues,
            "needs_more": False,
            "validator_name": self.get_name(),
            "metadata": {
                "queue_rows": queue_rows,
                "drafts_created": drafts_created,
                "draft_errors": draft_errors,
            },
        }
