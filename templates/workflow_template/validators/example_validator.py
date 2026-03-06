# =============================================================================
# templates/workflow_template/validators/example_validator.py
#
# HOW TO USE THIS TEMPLATE
# ------------------------
# 1. Copy this file and rename the class (e.g. LengthValidator, JsonValidator).
# 2. Replace the quality checks inside validate() with your real criteria.
# 3. Keep the return dict exactly as-is — orchestrator and SmallBrain depend
#    on these specific keys.
#
# RULES (from CLAUDE.md)
# ----------------------
# ✅ Always extend BaseValidator.
# ✅ Implement validate(data, context) — context is optional extra info.
# ✅ Return the standard 5-key dict every time.
# ✅ Set needs_more=True when the orchestrator should retry the tool.
# ❌ Never raise exceptions — always return a dict.
# =============================================================================

import sys
import os

# ---------------------------------------------------------------------------
# Path setup — same pattern as example_tool.py
# ---------------------------------------------------------------------------
_here = os.path.dirname(os.path.abspath(__file__))
# example_validator.py is at: templates/workflow_template/validators/example_validator.py
#   dirname(_here)                    → templates/workflow_template
#   dirname(dirname(_here))           → templates
#   dirname(dirname(dirname(_here)))  → project root  ✅
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(_here)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_validator import BaseValidator


class ExampleValidator(BaseValidator):
    """
    Minimal example: checks that the tool produced non-empty output.

    In a real workflow replace the quality checks inside validate() with
    whatever criteria matter for your use case — minimum word count,
    required JSON keys, sentiment score threshold, etc.
    """

    def validate(self, data: dict, context: dict = None) -> dict:
        """
        Parameters
        ----------
        data : dict
            The value of tool_result["data"] — whatever the tool put there.
            ExampleTool puts {"processed_text": "..."} here.
        context : dict, optional
            Extra information the orchestrator may pass in (e.g. the
            original input, the attempt number). Ignore if not needed.

        Returns
        -------
        dict
            Standard validator result with keys: passed, issues,
            needs_more, validator_name, metadata.
        """
        issues = []

        # ------------------------------------------------------------------
        # ✏️  YOUR QUALITY CHECKS GO HERE
        # ------------------------------------------------------------------
        processed_text = (data or {}).get("processed_text", "")

        # Check 1: tool must have produced something
        if not processed_text:
            issues.append("processed_text is empty — tool produced no output")

        # Check 2: add more checks as needed, e.g.:
        # if len(processed_text.split()) < 10:
        #     issues.append("Output has fewer than 10 words")
        # ------------------------------------------------------------------

        passed = len(issues) == 0

        return {
            "passed": passed,
            # List of human-readable problem descriptions (empty if passed).
            "issues": issues,
            # needs_more=True → orchestrator will retry the tool.
            # Set to False if retrying won't help (e.g. malformed input).
            "needs_more": not passed,
            "validator_name": self.get_name(),   # ← always use self.get_name()
            "metadata": {"output_length": len(processed_text)},
        }
