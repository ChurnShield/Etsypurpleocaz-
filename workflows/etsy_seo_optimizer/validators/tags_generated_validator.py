import sys, os
_here = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(_here)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
from lib.orchestrator.base_validator import BaseValidator

class TagsGeneratedValidator(BaseValidator):
    def validate(self, data, context=None):
        issues = []
        if not isinstance(data, dict):
            return {"passed": False, "issues": ["Not a dict"], "needs_more": False,
                    "validator_name": self.get_name(), "metadata": {}}
        optimized = data.get("optimized_listings", [])
        with_tags = [o for o in optimized if o.get("new_tags")]
        if not with_tags:
            issues.append("No tags were generated")
        stats = data.get("stats", {})
        failed = stats.get("failed", 0)
        if failed > len(optimized) / 2:
            issues.append(f"More than half failed ({failed}/{len(optimized)})")
        return {
            "passed": len(issues) == 0, "issues": issues, "needs_more": False,
            "validator_name": self.get_name(),
            "metadata": {"generated": len(with_tags), "failed": failed},
        }
