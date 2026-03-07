import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(_here)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_validator import BaseValidator


class AudioGeneratedValidator(BaseValidator):
    """Validates that audio files were generated successfully."""

    def validate(self, data, context=None):
        issues = []

        if not isinstance(data, dict):
            return {
                "passed": False,
                "issues": ["Expected a dict with 'audio_products' key"],
                "needs_more": False,
                "validator_name": self.get_name(),
                "metadata": {},
            }

        products = data.get("audio_products", [])
        stats = data.get("stats", {})

        if not products:
            issues.append("No audio products generated")

        # Check each audio file exists
        for product in products:
            path = product.get("audio_path", "")
            if path and not os.path.exists(path):
                issues.append(f"Audio file missing: {path}")

        if stats.get("failed", 0) > 0:
            issues.append(f"{stats['failed']} audio generation(s) failed")

        return {
            "passed": len(products) > 0 and all(
                os.path.exists(p.get("audio_path", "")) for p in products if p.get("audio_path")
            ),
            "issues": issues,
            "needs_more": len(products) == 0,
            "validator_name": self.get_name(),
            "metadata": {
                "generated": len(products),
                "failed": stats.get("failed", 0),
            },
        }
