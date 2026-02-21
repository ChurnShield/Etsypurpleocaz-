import sys, os
_here = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(_here)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
from lib.orchestrator.base_validator import BaseValidator

class ListingsPublishedValidator(BaseValidator):
    def validate(self, data, context=None):
        issues = []
        if not isinstance(data, dict):
            return {"passed": False, "issues": ["Not a dict"], "needs_more": False,
                    "validator_name": self.get_name(), "metadata": {}}
        if data.get("queue_rows", 0) == 0:
            issues.append("No listings saved to queue")
        return {
            "passed": len(issues) == 0, "issues": issues, "needs_more": False,
            "validator_name": self.get_name(),
            "metadata": {"queue_rows": data.get("queue_rows", 0),
                         "drafts": data.get("drafts_created", 0)},
        }
