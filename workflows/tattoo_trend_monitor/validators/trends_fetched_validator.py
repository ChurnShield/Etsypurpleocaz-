import sys, os
_here = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(_here)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
from lib.orchestrator.base_validator import BaseValidator

class TrendsFetchedValidator(BaseValidator):
    def validate(self, data, context=None):
        issues = []
        if not isinstance(data, dict):
            return {"passed": False, "issues": ["Not a dict"], "needs_more": False,
                    "validator_name": self.get_name(), "metadata": {}}
        if not data.get("trends") and not data.get("competitor_search"):
            issues.append("No trend or competitor data fetched")
        return {
            "passed": len(issues) == 0, "issues": issues, "needs_more": False,
            "validator_name": self.get_name(),
            "metadata": {"trends": len(data.get("trends", [])),
                         "searches": len(data.get("competitor_search", []))},
        }
