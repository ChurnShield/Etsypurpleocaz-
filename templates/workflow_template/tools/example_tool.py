# =============================================================================
# templates/workflow_template/tools/example_tool.py
#
# HOW TO USE THIS TEMPLATE
# ------------------------
# 1. Copy this file and rename the class (e.g. SummariserTool, FetcherTool).
# 2. Replace the logic inside the try block with your real work.
# 3. Keep the return dict exactly as-is — the orchestrator and SmallBrain
#    both depend on these specific keys.
#
# RULES (from CLAUDE.md)
# ----------------------
# ✅ Always extend BaseTool.
# ✅ Implement execute(**kwargs) — keyword arguments only, no positional args.
# ✅ Return the standard 5-key dict every time.
# ❌ Never raise exceptions — catch them and return {'success': False, ...}.
# =============================================================================

import sys
import os

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
# This file lives at: templates/workflow_template/tools/example_tool.py
# We need the project root on sys.path so we can import from lib/.
#
#   dirname(__file__)        → templates/workflow_template/tools
#   dirname(dirname(...))    → templates/workflow_template
#   dirname(dirname(dirname(...))) → project root  ✅
# ---------------------------------------------------------------------------
_here = os.path.dirname(os.path.abspath(__file__))
# example_tool.py is at: templates/workflow_template/tools/example_tool.py
#   dirname(_here)                    → templates/workflow_template/tools
#   dirname(dirname(_here))           → templates/workflow_template
#   dirname(dirname(dirname(_here)))  → project root  ✅
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(_here)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.orchestrator.base_tool import BaseTool


class ExampleTool(BaseTool):
    """
    Minimal example: uppercases the input text.

    In a real workflow you would replace the body of execute() with
    something like an API call, a file read, a database query, etc.

    The only contract you must preserve is the return dict format.
    """

    def execute(self, **kwargs) -> dict:
        """
        Parameters
        ----------
        text : str
            The text to process. Passed as a keyword argument by the
            orchestrator: tool.execute(**step["params"])

        Returns
        -------
        dict
            Standard tool result with keys: success, data, error,
            tool_name, metadata.
        """
        try:
            # ------------------------------------------------------------------
            # ✏️  YOUR LOGIC GOES HERE
            # ------------------------------------------------------------------
            text = kwargs.get("text", "")

            # Simple example operation — replace with your real work.
            result = text.upper()
            # ------------------------------------------------------------------

            return {
                "success": True,
                "data": {"processed_text": result},   # ← validator reads from "data"
                "error": None,
                "tool_name": self.get_name(),          # ← always use self.get_name()
                "metadata": {"input_length": len(text)},
            }

        except Exception as e:
            # Never raise — return the error in the dict so the orchestrator
            # can log it and decide whether to retry.
            return {
                "success": False,
                "data": None,
                "error": str(e),
                "tool_name": self.get_name(),
                "metadata": {"exception_type": type(e).__name__},
            }
