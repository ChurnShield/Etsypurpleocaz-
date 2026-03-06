"""
PurpleOcaz Agentic AI Dashboard — FastAPI Server

Mobile-responsive web dashboard for monitoring and controlling
the 3-Layer Dual Learning Agentic AI System from any device.
"""

import os
import sys
import json
import uuid
import subprocess
import threading
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_here = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_here)

if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from config import DATABASE_PATH
from lib.common_tools.sqlite_client import SQLiteClient

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = FastAPI(title="PurpleOcaz AI Dashboard", version="1.0.0")

# Serve static files (dashboard)
_static_dir = os.path.join(_project_root, "static")
app.mount("/static", StaticFiles(directory=_static_dir), name="static")


def _get_db():
    """Create a fresh SQLiteClient per request (thread-safe)."""
    return SQLiteClient(os.path.join(_project_root, DATABASE_PATH))


def _log_activity(db, source: str, action: str, target_type: str = None,
                  target_id: str = None, detail: str = None,
                  metadata: dict = None):
    """Write an entry to the activity_log table.

    Args:
        db:          SQLiteClient instance.
        source:      Where the action originated (e.g. "dashboard", "api",
                     "scheduler").
        action:      What happened (e.g. "workflow_triggered",
                     "proposal_approved").
        target_type: Kind of object acted on ("workflow", "proposal").
        target_id:   ID of that object.
        detail:      Human-readable one-liner.
        metadata:    Extra JSON-safe dict for context.
    """
    db.table("activity_log").insert({
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "source": source,
        "action": action,
        "target_type": target_type,
        "target_id": target_id,
        "detail": detail,
        "metadata": json.dumps(metadata) if metadata else None,
    }).execute()


# ---------------------------------------------------------------------------
# Ensure activity_log table exists (safe migration — idempotent)
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def _ensure_activity_log_table():
    import sqlite3 as _sqlite3
    db_path = os.path.join(_project_root, DATABASE_PATH)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = _sqlite3.connect(db_path)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS activity_log (
            id TEXT PRIMARY KEY,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            source TEXT NOT NULL,
            action TEXT NOT NULL,
            target_type TEXT,
            target_id TEXT,
            detail TEXT,
            metadata TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_activity_log_timestamp
            ON activity_log(timestamp);
        CREATE INDEX IF NOT EXISTS idx_activity_log_source
            ON activity_log(source);
    """)
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Dashboard entry point
# ---------------------------------------------------------------------------
@app.get("/")
async def dashboard():
    return FileResponse(os.path.join(_static_dir, "index.html"))


# ---------------------------------------------------------------------------
# System Health
# ---------------------------------------------------------------------------
@app.get("/api/health")
async def system_health():
    """Get BigBrain system health overview."""
    try:
        from lib.big_brain.brain import BigBrain
        from dataclasses import asdict

        db = _get_db()
        brain = BigBrain(db_client=db)
        health = brain.analyze_system_health()
        return asdict(health)
    except Exception as e:
        return {
            "status": "unknown",
            "total_executions_24h": 0,
            "system_failure_rate": 0.0,
            "total_workflows": 0,
            "active_workflows_24h": 0,
            "problems": [],
            "cache_hit": False,
            "analyzed_at": datetime.utcnow().isoformat(),
            "error": str(e),
        }


# ---------------------------------------------------------------------------
# Workflows
# ---------------------------------------------------------------------------
@app.get("/api/workflows")
async def list_workflows():
    """List all registered workflows with stats."""
    db = _get_db()
    workflows = db.table("workflows").select("*").order("last_run_at", desc=True).execute()
    return {"workflows": workflows}


@app.get("/api/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Get details for a single workflow."""
    db = _get_db()
    rows = db.table("workflows").select("*").eq("id", workflow_id).execute()
    if not rows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return rows[0]


# ---------------------------------------------------------------------------
# Executions
# ---------------------------------------------------------------------------
@app.get("/api/executions")
async def list_executions(workflow_id: str = None, limit: int = 50):
    """List recent executions, optionally filtered by workflow."""
    db = _get_db()
    query = db.table("executions").select("*")
    if workflow_id:
        query = query.eq("workflow_id", workflow_id)
    executions = query.order("started_at", desc=True).limit(limit).execute()
    return {"executions": executions}


@app.get("/api/executions/{execution_id}")
async def get_execution(execution_id: str):
    """Get details for a single execution."""
    db = _get_db()
    rows = db.table("executions").select("*").eq("id", execution_id).execute()
    if not rows:
        raise HTTPException(status_code=404, detail="Execution not found")
    return rows[0]


@app.get("/api/executions/{execution_id}/logs")
async def get_execution_logs(execution_id: str):
    """Get all logs for a specific execution."""
    db = _get_db()
    logs = (
        db.table("execution_logs")
        .select("*")
        .eq("execution_id", execution_id)
        .order("timestamp")
        .execute()
    )
    return {"logs": logs}


# ---------------------------------------------------------------------------
# Proposals (SmallBrain + BigBrain)
# ---------------------------------------------------------------------------
@app.get("/api/proposals")
async def list_proposals(status: str = None, limit: int = 50):
    """List proposals, optionally filtered by status."""
    db = _get_db()
    query = db.table("proposals").select("*")
    if status:
        query = query.eq("status", status)
    proposals = query.order("generated_at", desc=True).limit(limit).execute()
    return {"proposals": proposals}


class ProposalAction(BaseModel):
    action: str  # "approved" or "rejected"


@app.post("/api/proposals/{proposal_id}/decide")
async def decide_proposal(proposal_id: str, body: ProposalAction):
    """Approve or reject a proposal."""
    if body.action not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="action must be 'approved' or 'rejected'")

    db = _get_db()
    rows = db.table("proposals").select("*").eq("id", proposal_id).execute()
    if not rows:
        raise HTTPException(status_code=404, detail="Proposal not found")

    proposal = rows[0]

    db.table("proposals").update({
        "status": body.action,
        "applied_at": datetime.utcnow().isoformat() if body.action == "approved" else None,
        "applied_by": "dashboard_user",
    }).eq("id", proposal_id).execute()

    _log_activity(
        db,
        source="dashboard",
        action=f"proposal_{body.action}",
        target_type="proposal",
        target_id=proposal_id,
        detail=f"{body.action.capitalize()} proposal: {proposal.get('title', proposal_id)}",
        metadata={
            "proposal_type": proposal.get("proposal_type"),
            "workflow_id": proposal.get("workflow_id"),
        },
    )

    return {"success": True, "proposal_id": proposal_id, "new_status": body.action}


# ---------------------------------------------------------------------------
# Workflow Trigger
# ---------------------------------------------------------------------------
# Track running workflows so we don't double-trigger
_running_workflows = {}


class TriggerResult(BaseModel):
    success: bool
    message: str
    execution_id: str = None


@app.post("/api/workflows/{workflow_id}/run")
async def trigger_workflow(workflow_id: str):
    """Trigger a workflow run in the background."""
    if workflow_id in _running_workflows and _running_workflows[workflow_id]:
        raise HTTPException(status_code=409, detail="Workflow is already running")

    # Find the workflow's run.py
    run_script = os.path.join(_project_root, "workflows", workflow_id, "run.py")
    if not os.path.exists(run_script):
        raise HTTPException(status_code=404, detail=f"No run.py found for workflow '{workflow_id}'")

    _running_workflows[workflow_id] = True

    _log_activity(
        _get_db(),
        source="dashboard",
        action="workflow_triggered",
        target_type="workflow",
        target_id=workflow_id,
        detail=f"Triggered workflow: {workflow_id}",
    )

    def _run_in_background():
        try:
            proc = subprocess.run(
                [sys.executable, run_script],
                cwd=_project_root,
                timeout=600,
                capture_output=True,
                text=True,
            )
            success = proc.returncode == 0
            _log_activity(
                _get_db(),
                source="system",
                action="workflow_completed" if success else "workflow_failed",
                target_type="workflow",
                target_id=workflow_id,
                detail=f"Workflow {workflow_id} {'completed' if success else 'failed'}",
                metadata={
                    "returncode": proc.returncode,
                    "stderr": (proc.stderr or "")[:500],
                },
            )
        except Exception as exc:
            _log_activity(
                _get_db(),
                source="system",
                action="workflow_error",
                target_type="workflow",
                target_id=workflow_id,
                detail=f"Workflow {workflow_id} error: {exc}",
            )
        finally:
            _running_workflows[workflow_id] = False

    thread = threading.Thread(target=_run_in_background, daemon=True)
    thread.start()

    return {"success": True, "message": f"Workflow '{workflow_id}' triggered"}


@app.get("/api/workflows/{workflow_id}/status")
async def workflow_running_status(workflow_id: str):
    """Check if a workflow is currently running."""
    return {"running": _running_workflows.get(workflow_id, False)}


# ---------------------------------------------------------------------------
# Dashboard Stats (aggregated)
# ---------------------------------------------------------------------------
@app.get("/api/stats")
async def dashboard_stats():
    """Aggregated stats for the dashboard home page."""
    db = _get_db()

    workflows = db.table("workflows").select("*").execute()
    total_workflows = len(workflows)
    total_runs = sum(w.get("total_runs", 0) for w in workflows)
    total_success = sum(w.get("successful_runs", 0) for w in workflows)
    total_failed = sum(w.get("failed_runs", 0) for w in workflows)

    pending_proposals = db.table("proposals").select("*").eq("status", "pending").execute()

    # Recent executions (last 24h)
    cutoff = (datetime.utcnow() - timedelta(hours=24)).isoformat()
    recent = db.table("executions").select("*").gt("started_at", cutoff).execute()
    recent_success = sum(1 for e in recent if e.get("status") == "completed")
    recent_failed = sum(1 for e in recent if e.get("status") == "failed")

    return {
        "total_workflows": total_workflows,
        "total_runs": total_runs,
        "total_success": total_success,
        "total_failed": total_failed,
        "success_rate": round(total_success / total_runs * 100, 1) if total_runs > 0 else 0,
        "pending_proposals": len(pending_proposals),
        "runs_24h": len(recent),
        "success_24h": recent_success,
        "failed_24h": recent_failed,
    }


# ---------------------------------------------------------------------------
# Activity Log
# ---------------------------------------------------------------------------
@app.get("/api/activity")
async def list_activity(source: str = None, limit: int = 50):
    """List recent activity log entries."""
    db = _get_db()
    query = db.table("activity_log").select("*")
    if source:
        query = query.eq("source", source)
    entries = query.order("timestamp", desc=True).limit(limit).execute()
    return {"activity": entries}
