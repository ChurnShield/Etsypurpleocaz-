# =============================================================================
# templates/workflow_template/orchestrator.py
#
# SimpleOrchestrator — the mechanical worker.
#
# What it does
# ------------
# 1. Creates an ExecutionLogger tied to this specific run.
# 2. Iterates over the execution plan (a list of steps).
# 3. For each step: runs the tool → validates the result → retries if needed.
# 4. Logs every action via ExecutionLogger.
# 5. CRITICAL: calls logger.flush() in a finally block no matter what.
#
# What it does NOT do
# -------------------
# It does not decide *what* to run — that comes from the plan in run.py.
# It does not learn or propose improvements — that is SmallBrain's job.
# =============================================================================

import sys
import os
import time
from datetime import datetime

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
# This file lives at: templates/workflow_template/orchestrator.py
#   dirname(__file__)     → templates/workflow_template
#   dirname(dirname(...)) → project root  ✅
# ---------------------------------------------------------------------------
_here = os.path.dirname(os.path.abspath(__file__))
# orchestrator.py is at: templates/workflow_template/orchestrator.py
#   dirname(_here) → templates/
#   dirname(dirname(_here)) → project root  ✅
_project_root = os.path.dirname(os.path.dirname(_here))

# Project root must be on sys.path so lib/ imports work.
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# Template directory must be on sys.path so 'from config import ...' picks up
# THIS workflow's config.py, not the root-level config.py.
if _here not in sys.path:
    sys.path.insert(0, _here)

from lib.orchestrator.execution_logger import ExecutionLogger
from config import MAX_RETRIES


class SimpleOrchestrator:
    """
    Runs a list of steps, logging every action to the database.

    Parameters
    ----------
    workflow_id  : str   The unique name of this workflow (from config.py).
    execution_id : str   A UUID generated in run.py for this specific run.
    db           : SQLiteClient  An open database connection.
    """

    def __init__(self, workflow_id: str, execution_id: str, db):
        self.workflow_id = workflow_id
        self.execution_id = execution_id
        self.db = db

        # ExecutionLogger buffers events in memory and writes them all at once
        # when flush() is called.  NEVER skip the flush().
        self.logger = ExecutionLogger(execution_id, workflow_id, db)

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def run(self, plan: list) -> dict:
        """
        Execute the workflow plan.

        Parameters
        ----------
        plan : list of dicts, each with:
            "phase"      : str              Human-readable name logged to DB.
            "tool"       : BaseTool         Tool instance to call.
            "params"     : dict             Keyword args passed to tool.execute().
            "validator"  : BaseValidator    Validator instance (or None).
            "max_retries": int (optional)   Override the default from config.py.

        Returns
        -------
        dict  {"success": bool, "execution_id": str}
        """
        # Record this execution in the database BEFORE running any steps so
        # SmallBrain can always find it even if the run crashes halfway.
        self._record_execution_start()

        overall_success = True

        try:
            for step in plan:
                step_success = self._run_step(step)
                if not step_success:
                    overall_success = False
                    # Template behaviour: log the failure and keep going.
                    # Change to `break` if you want to abort on first failure.

            self._record_execution_end(overall_success)

        finally:
            # ==================================================================
            # CRITICAL: flush() MUST be in a finally block.
            #
            # ExecutionLogger keeps events in a memory buffer (_buffer list).
            # flush() is the only thing that writes them to the database.
            # If an exception happens before flush(), ALL logs are lost.
            # SmallBrain then has blind spots and generates wrong proposals.
            # ==================================================================
            self.logger.flush()

        return {"success": overall_success, "execution_id": self.execution_id}

    # -------------------------------------------------------------------------
    # Private helpers
    # -------------------------------------------------------------------------

    def _run_step(self, step: dict) -> bool:
        """Run one step of the plan (tool + validator + retries)."""
        phase_name = step["phase"]
        tool = step["tool"]
        params = step.get("params", {})
        validator = step.get("validator")
        retries = step.get("max_retries", MAX_RETRIES)

        # -- Phase start -------------------------------------------------------
        # Marks the beginning of this logical section in the logs.
        self.logger.phase_start(phase_name)

        step_success = False

        for attempt in range(1, retries + 1):
            # -- Tool call -----------------------------------------------------
            # Log the intent *before* calling the tool so we have a record even
            # if the tool hangs or crashes.
            self.logger.tool_call(tool.get_name(), params)

            start_time = time.time()
            result = tool.execute(**params)
            duration_ms = int((time.time() - start_time) * 1000)

            # -- Tool result ---------------------------------------------------
            self.logger.tool_result(
                tool.get_name(),
                result,
                result["success"],
                duration_ms,
            )

            if not result["success"]:
                # The tool itself failed (exception caught inside the tool).
                # No point running the validator on bad output.
                if attempt == retries:
                    break       # out of retry loop, step_success stays False
                continue        # try again

            # -- Validation ----------------------------------------------------
            if validator is None:
                # No validator configured — trust the tool's success flag.
                step_success = True
                break

            val_result = validator.validate(result.get("data") or {})

            # Log the validation outcome so SmallBrain can compute pass rates.
            self.logger.validation_event(
                validator.get_name(),
                val_result["passed"],
                val_result["issues"],
            )

            if val_result["passed"]:
                step_success = True
                break

            if not val_result["needs_more"] or attempt == retries:
                # Validator says retrying won't help, or we've hit the limit.
                break
            # else: loop again — the validator wants another attempt

        # -- Phase end ---------------------------------------------------------
        self.logger.phase_end(phase_name, step_success)
        return step_success

    def _record_execution_start(self):
        """Insert a row in the executions table with status='running'."""
        self.db.table("executions").insert({
            "id": self.execution_id,
            "workflow_id": self.workflow_id,
            "started_at": datetime.utcnow().isoformat(),
            "status": "running",
        }).execute()

    def _record_execution_end(self, success: bool):
        """Update the executions row with final status and completion time."""
        self.db.table("executions").update({
            "status": "completed" if success else "failed",
            "completed_at": datetime.utcnow().isoformat(),
        }).eq("id", self.execution_id).execute()
