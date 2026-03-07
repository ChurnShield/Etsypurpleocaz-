import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(_here)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_validator import BaseValidator


class SourcesCuratedValidator(BaseValidator):
    """Validates that sources were curated and notebooks populated."""

    def validate(self, data, context=None):
        issues = []

        if not isinstance(data, dict):
            return {
                "passed": False,
                "issues": ["Expected a dict with 'notebooks' key"],
                "needs_more": False,
                "validator_name": self.get_name(),
                "metadata": {},
            }

        notebooks = data.get("notebooks", [])
        total_sources = data.get("total_sources", 0)

        if not notebooks:
            issues.append("No notebooks curated")

        if total_sources == 0:
            issues.append("No sources added to any notebook")

        # Check each notebook has at least one source
        empty_notebooks = [n["niche"] for n in notebooks if n.get("sources_added", 0) == 0]
        if empty_notebooks:
            issues.append(f"Empty notebooks: {', '.join(empty_notebooks)}")

        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "needs_more": len(issues) > 0,
            "validator_name": self.get_name(),
            "metadata": {
                "notebooks": len(notebooks),
                "total_sources": total_sources,
            },
        }
