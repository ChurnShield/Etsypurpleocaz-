# =============================================================================
# templates/workflow_template/run.py
#
# Entry point — run this file to execute the workflow.
#
#   python templates/workflow_template/run.py
#
# What this script does (in order)
# ---------------------------------
# 1. Adds the project root and template directory to sys.path.
# 2. Connects to the SQLite database via SQLiteClient.
# 3. Registers the workflow in the `workflows` table (first run only).
# 4. Generates a unique execution_id (UUID) for this run.
# 5. Defines the execution plan (list of steps).
# 6. Creates a SimpleOrchestrator and runs the plan.
# 7. Updates workflow statistics (total_runs, successful_runs, etc.).
# 8. Optionally runs SmallBrain to check for improvement proposals.
# 9. Prints a success/failure summary.
# =============================================================================

import sys
import os
import uuid
from datetime import datetime

# ---------------------------------------------------------------------------
# Path setup — MUST happen before any other local imports
# ---------------------------------------------------------------------------
# run.py lives at: templates/workflow_template/run.py
# We need two directories on sys.path:
#
#   _here         = templates/workflow_template   → for config, orchestrator, etc.
#   _project_root = project root                  → for lib/ imports
#
# _here is inserted at index 0 so that 'import config' finds the TEMPLATE's
# config.py, not the root-level config.py.
# ---------------------------------------------------------------------------
_here = os.path.dirname(os.path.abspath(__file__))
# run.py is at: templates/workflow_template/run.py
#   dirname(_here) → templates/
#   dirname(dirname(_here)) → project root  ✅
_project_root = os.path.dirname(os.path.dirname(_here))

sys.path.insert(0, _here)          # template-local imports (config, orchestrator…)
sys.path.insert(1, _project_root)  # lib/ imports

# ---------------------------------------------------------------------------
# Imports — template config
# ---------------------------------------------------------------------------
from config import WORKFLOW_NAME, DATABASE_PATH, PROPOSAL_THRESHOLD_RUNS

# ---------------------------------------------------------------------------
# Imports — project infrastructure
# ---------------------------------------------------------------------------
# SQLiteClient connects to SQLite in development.
# The same query-builder API works unchanged with Supabase in production.
from lib.common_tools.sqlite_client import SQLiteClient

# ---------------------------------------------------------------------------
# Imports — this workflow's components
# ---------------------------------------------------------------------------
from orchestrator import SimpleOrchestrator
from brain import SmallBrain
from tools.example_tool import ExampleTool
from validators.example_validator import ExampleValidator


# =============================================================================
# Helper functions
# =============================================================================

def ensure_workflow_registered(db, workflow_id: str):
    """
    Insert a row in the `workflows` table the first time this workflow runs.

    Why? SmallBrain counts total_runs to know when to start analysing.
    The orchestrator needs the workflow to exist before it inserts executions
    (foreign-key constraint).
    """
    existing = (
        db.table("workflows")
        .select("id")
        .eq("id", workflow_id)
        .execute()
    )
    if not existing:
        db.table("workflows").insert({
            "id": workflow_id,
            "name": workflow_id,
            "description": "Auto-registered on first run.",
            "created_at": datetime.utcnow().isoformat(),
            "total_runs": 0,
            "successful_runs": 0,
            "failed_runs": 0,
        }).execute()
        print(f"  Registered new workflow: '{workflow_id}'")


def update_workflow_stats(db, workflow_id: str, success: bool):
    """
    Increment run counters after each execution.

    SmallBrain reads total_runs to decide whether it has enough data.
    """
    rows = (
        db.table("workflows")
        .select("total_runs, successful_runs, failed_runs")
        .eq("id", workflow_id)
        .execute()
    )
    if not rows:
        return

    row = rows[0]
    db.table("workflows").update({
        "total_runs":      row["total_runs"] + 1,
        "successful_runs": row["successful_runs"] + (1 if success else 0),
        "failed_runs":     row["failed_runs"]     + (0 if success else 1),
        "last_run_at":     datetime.utcnow().isoformat(),
    }).eq("id", workflow_id).execute()


# =============================================================================
# Main
# =============================================================================

def main():
    print(f"\n{'=' * 55}")
    print(f"  Workflow : {WORKFLOW_NAME}")
    print(f"  Database : {DATABASE_PATH}")
    print(f"{'=' * 55}")

    # ── 1. Connect to the database ────────────────────────────────────────────
    # SQLiteClient opens a connection and gives us a query-builder API.
    # Call get_client() instead if you want the global singleton from config.py.
    db = SQLiteClient(DATABASE_PATH)
    print(f"\n[1] Connected to database")

    # ── 2. Register workflow (first run only) ─────────────────────────────────
    ensure_workflow_registered(db, WORKFLOW_NAME)
    print(f"[2] Workflow registered")

    # ── 3. Generate a unique ID for this execution ────────────────────────────
    # Every run gets its own UUID so its logs stay separate from every other run.
    execution_id = str(uuid.uuid4())
    print(f"[3] Execution ID: {execution_id}")

    # ── 4. Define the execution plan ──────────────────────────────────────────
    # The plan is a list of steps. Each step is a dict with:
    #
    #   "phase"      : str            → logged to DB, appears in SmallBrain reports
    #   "tool"       : BaseTool       → called with execute(**params)
    #   "params"     : dict           → keyword args forwarded to tool.execute()
    #   "validator"  : BaseValidator  → checks tool output; triggers retry on fail
    #
    # ✏️  Add or remove steps here to define your workflow.
    plan = [
        {
            "phase": "Phase 1: Process Text",
            "tool": ExampleTool(),
            "params": {"text": "hello world — this is my workflow input"},
            "validator": ExampleValidator(),
        },
        # Add more steps below:
        # {
        #     "phase": "Phase 2: Do Something Else",
        #     "tool": AnotherTool(),
        #     "params": {"key": "value"},
        #     "validator": AnotherValidator(),
        # },
    ]
    print(f"[4] Plan defined - {len(plan)} step(s)")

    # ── 5. Run the orchestrator ───────────────────────────────────────────────
    # SimpleOrchestrator:
    #   - Creates an ExecutionLogger
    #   - Iterates the plan, running tool → validate → retry
    #   - Calls logger.flush() in a finally block (logs go to DB here)
    print(f"[5] Running orchestrator...\n")
    orchestrator = SimpleOrchestrator(WORKFLOW_NAME, execution_id, db)
    result = orchestrator.run(plan)

    # ── 6. Update workflow statistics ─────────────────────────────────────────
    update_workflow_stats(db, WORKFLOW_NAME, result["success"])
    print(f"\n[6] Workflow stats updated")

    # ── 7. Run SmallBrain (optional) ──────────────────────────────────────────
    # SmallBrain checks whether PROPOSAL_THRESHOLD_RUNS have been reached.
    # If yes, it analyses logs and saves proposals to the proposals table.
    # Remove this block if you don't want analysis after every run.
    print(f"[7] Running SmallBrain analysis...")
    brain = SmallBrain(workflow_id=WORKFLOW_NAME, db=db)
    proposals = brain.analyze()
    if proposals:
        print(f"    {len(proposals)} proposal(s) saved to the proposals table.")
        print(f"    Query: SELECT title, description FROM proposals "
              f"WHERE workflow_id = '{WORKFLOW_NAME}';")

    # ── 8. Final result ───────────────────────────────────────────────────────
    print(f"\n{'=' * 55}")
    if result["success"]:
        print("  RESULT : SUCCESS")
    else:
        print("  RESULT : FAILED")
        print("  Tip    : Run the query below to see what went wrong:")
        print(f"  SELECT event_type, tool_name, validator_name, success, error_message")
        print(f"  FROM   execution_logs")
        print(f"  WHERE  execution_id = '{execution_id}';")
    print(f"{'=' * 55}\n")

    return result


if __name__ == "__main__":
    main()
