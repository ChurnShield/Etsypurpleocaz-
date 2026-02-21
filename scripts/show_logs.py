"""
scripts/show_logs.py

Reads workflow execution logs from the database and generates an HTML report.

Usage
-----
    python scripts/show_logs.py                        # all logs, all workflows
    python scripts/show_logs.py my_workflow            # one workflow only
    python scripts/show_logs.py --last 10              # last 10 executions
    python scripts/show_logs.py my_workflow --last 5   # combined filter
"""

import os
import sys
import json
import webbrowser
from datetime import datetime

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
# scripts/show_logs.py lives one level below the project root.
#   dirname(abspath(__file__)) → scripts/
#   dirname(dirname(...))      → project root  ✅
# This lets us import from lib/ and from config.py.
# ---------------------------------------------------------------------------
_scripts_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_scripts_dir)
sys.path.insert(0, _project_root)

from lib.common_tools.sqlite_client import SQLiteClient
from config import DATABASE_PATH

# The HTML report is written here (relative to the project root).
OUTPUT_FILE = os.path.join(_project_root, "logs_report.html")


# =============================================================================
# 1. Command-line argument parsing
# =============================================================================

def parse_args():
    """
    Parse sys.argv without any third-party libraries.

    Understands:
        workflow_id      (any positional argument)
        --last N         (integer: show only the N most recent executions)

    Returns
    -------
    (workflow_filter: str|None, last_n: int|None)
    """
    workflow_filter = None
    last_n = None

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--last":
            # --last must be followed by a number
            if i + 1 >= len(args):
                print("Error: --last requires a number after it.  Example: --last 10")
                sys.exit(1)
            try:
                last_n = int(args[i + 1])
            except ValueError:
                print(f"Error: --last expects a whole number, got '{args[i + 1]}'")
                sys.exit(1)
            i += 2
        elif not args[i].startswith("--"):
            # Treat any non-flag argument as the workflow_id filter
            workflow_filter = args[i]
            i += 1
        else:
            print(f"Unknown argument: {args[i]}")
            print("Usage: python scripts/show_logs.py [workflow_id] [--last N]")
            sys.exit(1)

    return workflow_filter, last_n


# =============================================================================
# 2. Database queries
#    We use SQLiteClient (not raw sqlite3) so the code is compatible with
#    both SQLite (development) and Supabase (production).
# =============================================================================

def fetch_executions(db, workflow_filter, last_n):
    """
    Fetch execution records, newest first.

    Parameters
    ----------
    db              : SQLiteClient
    workflow_filter : str or None   — if given, only rows matching workflow_id
    last_n          : int or None   — if given, only return this many rows

    Returns
    -------
    list of dicts
    """
    query = db.table("executions").select("*").order("started_at", desc=True)

    if workflow_filter:
        query = query.eq("workflow_id", workflow_filter)

    if last_n:
        query = query.limit(last_n)

    return query.execute()


def fetch_logs_for_execution(db, execution_id):
    """
    Fetch all log events for one execution in time order.

    Returns
    -------
    list of dicts  (each dict is one row from execution_logs)
    """
    return (
        db.table("execution_logs")
        .select("*")
        .eq("execution_id", execution_id)
        .order("timestamp")
        .execute()
    )


# =============================================================================
# 3. Data processing helpers
# =============================================================================

def compute_summary(executions):
    """
    Calculate headline statistics from the list of executions.

    Returns a dict:
        total         — total number of executions
        completed     — how many finished successfully
        failed        — how many failed
        success_rate  — integer percentage (0-100)
        avg_duration_s — average seconds, or None if no timing data
    """
    total = len(executions)
    if total == 0:
        return {
            "total": 0, "completed": 0, "failed": 0,
            "success_rate": 0, "avg_duration_s": None,
        }

    completed = sum(1 for e in executions if e.get("status") == "completed")
    failed    = sum(1 for e in executions if e.get("status") == "failed")

    # Compute duration for executions that have both start and end timestamps
    durations = []
    for e in executions:
        if e.get("started_at") and e.get("completed_at"):
            try:
                start = datetime.fromisoformat(e["started_at"])
                end   = datetime.fromisoformat(e["completed_at"])
                durations.append((end - start).total_seconds())
            except ValueError:
                pass  # malformed timestamp — skip

    avg_duration = sum(durations) / len(durations) if durations else None

    return {
        "total": total,
        "completed": completed,
        "failed": failed,
        "success_rate": round(completed / total * 100),
        "avg_duration_s": round(avg_duration, 2) if avg_duration is not None else None,
    }


def parse_metadata(raw):
    """
    The metadata column is stored as a JSON string.
    Parse it and return a Python dict, or None if empty/invalid.
    """
    if not raw:
        return None
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None


def short_timestamp(ts):
    """
    Turn '2026-02-19T07:46:28.201344' into '07:46:28.201' for compact display.
    """
    if not ts:
        return ""
    if "T" in ts:
        return ts.split("T")[1][:12]
    return ts


def escape_html(text):
    """
    Escape characters that would break HTML rendering.
    """
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


# =============================================================================
# 4. HTML building helpers
# =============================================================================

# Map each event_type to a CSS class that controls the row background colour.
ROW_CLASSES = {
    "phase_start":  "row-phase",
    "phase_end":    "row-phase",
    "tool_call":    "row-tool-call",
    "error":        "row-error",
}


def row_css_class(event_type, success):
    """Return the CSS class for a log row based on event type and outcome."""
    if event_type in ("phase_start", "phase_end"):
        return "row-phase"
    if event_type == "tool_call":
        return "row-tool-call"
    if event_type in ("tool_result", "validation"):
        return "row-success" if success else "row-fail"
    if event_type == "error":
        return "row-error"
    return ""


def badge(label, css_class):
    return f'<span class="badge {css_class}">{label}</span>'


EVENT_BADGES = {
    "phase_start":  ("PHASE START",  "bdg-phase"),
    "phase_end":    ("PHASE END",    "bdg-phase"),
    "tool_call":    ("TOOL CALL",    "bdg-tool"),
    "tool_result":  ("TOOL RESULT",  "bdg-tool"),
    "validation":   ("VALIDATE",     "bdg-validate"),
    "error":        ("ERROR",        "bdg-error"),
}


def event_badge(event_type):
    label, css = EVENT_BADGES.get(event_type, (event_type or "?", "bdg-phase"))
    return badge(label, css)


def success_badge(success):
    if success is None:
        return ""
    if success in (1, True):
        return badge("PASS", "bdg-pass")
    return badge("FAIL", "bdg-fail")


def render_metadata(meta):
    """
    Render a metadata dict as a compact two-column HTML table.
    Nested dicts/lists are shown as indented JSON strings.
    """
    if not meta:
        return '<span class="none">—</span>'

    rows = []
    for key, value in meta.items():
        if isinstance(value, (dict, list)):
            val_str = escape_html(json.dumps(value, indent=2))
        else:
            val_str = escape_html(str(value))
        rows.append(
            f"<tr>"
            f'<td class="mk">{escape_html(key)}</td>'
            f'<td class="mv">{val_str}</td>'
            f"</tr>"
        )

    return (
        '<table class="meta-tbl">'
        + "".join(rows)
        + "</table>"
    )


def render_log_table(logs):
    """
    Build the full <table> of log events for one execution.
    Each row is one entry from execution_logs.
    """
    if not logs:
        return '<p class="none">No log events recorded for this execution.</p>'

    header = (
        "<table>"
        "<thead><tr>"
        "<th>Time</th>"
        "<th>Phase</th>"
        "<th>Event</th>"
        "<th>Tool / Validator</th>"
        "<th>Result</th>"
        "<th>Duration</th>"
        "<th>Metadata</th>"
        "<th>Error</th>"
        "</tr></thead>"
        "<tbody>"
    )

    rows = []
    for log in logs:
        event_type  = log.get("event_type", "")
        raw_success = log.get("success")

        # SQLite returns booleans as 0/1 integers — convert to real bool
        success = bool(raw_success) if raw_success is not None else None

        meta   = parse_metadata(log.get("metadata"))
        css    = row_css_class(event_type, success)
        actor  = log.get("tool_name") or log.get("validator_name") or ""
        dur    = log.get("duration_ms")
        dur_str = f"{dur}&thinsp;ms" if dur is not None else "—"
        err     = log.get("error_message") or ""
        err_html = f'<span class="err">{escape_html(err)}</span>' if err else "—"

        rows.append(
            f'<tr class="{css}">'
            f"<td>{short_timestamp(log.get('timestamp', ''))}</td>"
            f"<td>{escape_html(log.get('phase') or '—')}</td>"
            f"<td>{event_badge(event_type)}</td>"
            f"<td>{escape_html(actor)}</td>"
            f"<td>{success_badge(success)}</td>"
            f"<td>{dur_str}</td>"
            f'<td class="meta-cell">{render_metadata(meta)}</td>'
            f"<td>{err_html}</td>"
            f"</tr>"
        )

    return header + "".join(rows) + "</tbody></table>"


def render_execution_block(execution, logs):
    """
    Build one collapsible <details> block for a single execution.
    Click the summary bar to expand/collapse.
    """
    exec_id     = execution.get("id", "")
    workflow_id = execution.get("workflow_id", "")
    status      = execution.get("status", "unknown")
    started_at  = execution.get("started_at", "")
    completed_at = execution.get("completed_at", "")

    # Human-readable duration
    duration_str = ""
    if started_at and completed_at:
        try:
            secs = (
                datetime.fromisoformat(completed_at)
                - datetime.fromisoformat(started_at)
            ).total_seconds()
            duration_str = f"&nbsp;|&nbsp; {secs:.2f}s"
        except ValueError:
            pass

    header_css = {
        "completed": "hdr-completed",
        "failed":    "hdr-failed",
        "running":   "hdr-running",
    }.get(status, "hdr-unknown")

    short_id   = exec_id[:8] + "…"
    started_fmt = started_at[:19] if started_at else "unknown time"
    n_events    = len(logs)

    log_table = render_log_table(logs)

    return f"""
<details>
  <summary class="exec-summary {header_css}">
    <span class="wf-name">{escape_html(workflow_id)}</span>
    <span class="sep">|</span>
    <span class="ts">{started_fmt}</span>
    {duration_str}
    <span class="sep">|</span>
    <span class="status-label">{status.upper()}</span>
    <span class="sep">|</span>
    <span class="exec-id">{short_id}</span>
    <span class="sep">|</span>
    <span class="event-count">{n_events} event(s) &mdash; click to expand</span>
  </summary>
  <div class="exec-body">
    <p class="full-id">Full execution ID: <code>{escape_html(exec_id)}</code></p>
    {log_table}
  </div>
</details>
"""


def render_summary_box(summary, workflow_filter, last_n):
    """
    Build the statistics banner shown at the top of the page.
    """
    filters = []
    if workflow_filter:
        filters.append(badge(escape_html(workflow_filter), "bdg-validate"))
    if last_n:
        filters.append(badge(f"last {last_n}", "bdg-tool"))
    if not filters:
        filters.append(badge("all workflows", "bdg-phase"))

    avg_str = (
        f"{summary['avg_duration_s']}s"
        if summary["avg_duration_s"] is not None
        else "n/a"
    )

    return f"""
<div class="summary-box">
  <h1>Workflow Log Report</h1>
  <div class="filter-row">Filters:&nbsp; {"&nbsp;".join(filters)}</div>
  <div class="stats-row">
    <div class="stat">
      <div class="stat-val">{summary['total']}</div>
      <div class="stat-lbl">Total Runs</div>
    </div>
    <div class="stat">
      <div class="stat-val ok">{summary['completed']}</div>
      <div class="stat-lbl">Completed</div>
    </div>
    <div class="stat">
      <div class="stat-val fail">{summary['failed']}</div>
      <div class="stat-lbl">Failed</div>
    </div>
    <div class="stat">
      <div class="stat-val">{summary['success_rate']}%</div>
      <div class="stat-lbl">Success Rate</div>
    </div>
    <div class="stat">
      <div class="stat-val">{avg_str}</div>
      <div class="stat-lbl">Avg Duration</div>
    </div>
  </div>
</div>
"""


# =============================================================================
# 5. Full HTML page assembly
# =============================================================================

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-size: 13px;
  background: #f0f2f5;
  color: #222;
  padding: 20px;
}

/* ── Summary box ───────────────────────────────── */
.summary-box {
  background: white;
  padding: 20px 24px;
  border-radius: 8px;
  margin-bottom: 18px;
  box-shadow: 0 1px 4px rgba(0,0,0,.12);
}
.summary-box h1 { font-size: 20px; margin-bottom: 10px; }
.filter-row { margin-bottom: 14px; }
.stats-row  { display: flex; gap: 32px; flex-wrap: wrap; }
.stat-val   { font-size: 28px; font-weight: 700; }
.stat-val.ok   { color: #2e7d32; }
.stat-val.fail { color: #c62828; }
.stat-lbl   { font-size: 11px; color: #777; margin-top: 2px; }

/* ── Execution collapsible blocks ─────────────── */
details { margin-bottom: 8px; border-radius: 6px; overflow: hidden; }
details summary::-webkit-details-marker { display: none; }

.exec-summary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  cursor: pointer;
  list-style: none;
  color: white;
  font-size: 12px;
  flex-wrap: wrap;
}
.exec-summary:hover { filter: brightness(1.08); }
.hdr-completed { background: #2e7d32; }
.hdr-failed    { background: #c62828; }
.hdr-running   { background: #1565c0; }
.hdr-unknown   { background: #555; }
.wf-name  { font-weight: 700; font-size: 13px; }
.sep      { opacity: 0.4; }
.ts       { opacity: 0.9; }
.status-label { font-weight: 700; letter-spacing: .5px; }
.exec-id  { opacity: 0.65; font-family: monospace; }
.event-count { opacity: 0.8; }

.exec-body {
  background: white;
  border: 1px solid #ddd;
  border-top: none;
  padding: 12px;
}
.full-id { font-size: 11px; color: #888; margin-bottom: 10px; }
code {
  background: #f5f5f5;
  padding: 1px 4px;
  border-radius: 3px;
  font-size: 11px;
  font-family: monospace;
}

/* ── Log event table ───────────────────────────── */
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
  font-family: monospace;
}
thead th {
  background: #f5f5f5;
  padding: 6px 8px;
  text-align: left;
  border-bottom: 2px solid #ddd;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: .5px;
  white-space: nowrap;
}
tbody td {
  padding: 5px 8px;
  border-bottom: 1px solid #eee;
  vertical-align: top;
}

/* Row background colours by event type */
.row-phase       { background: #e3f2fd; }   /* blue — phase markers      */
.row-tool-call   { background: #fff8e1; }   /* amber — before tool runs  */
.row-success     { background: #e8f5e9; }   /* green — passed            */
.row-fail        { background: #ffebee; }   /* red — failed              */
.row-error       { background: #ffcdd2; }   /* dark red — exceptions     */

/* ── Badges ────────────────────────────────────── */
.badge {
  display: inline-block;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: .5px;
  white-space: nowrap;
}
.bdg-pass     { background: #4caf50; color: white; }
.bdg-fail     { background: #f44336; color: white; }
.bdg-phase    { background: #1e88e5; color: white; }
.bdg-tool     { background: #f57c00; color: white; }
.bdg-validate { background: #6a1b9a; color: white; }
.bdg-error    { background: #c62828; color: white; }

/* ── Metadata mini-table ───────────────────────── */
.meta-cell { max-width: 320px; }
.meta-tbl  { border-left: 3px solid #ddd; padding-left: 4px; width: 100%; }
.meta-tbl td { padding: 1px 4px; border: none; vertical-align: top; }
.mk { color: #888; white-space: nowrap; padding-right: 8px; }
.mv { color: #333; word-break: break-all; white-space: pre-wrap; }

/* ── Misc ──────────────────────────────────────── */
.none { color: #bbb; font-style: italic; }
.err  { color: #c62828; }
.hint { font-size: 12px; color: #666; margin-bottom: 10px; }
.footer {
  margin-top: 24px;
  text-align: center;
  font-size: 11px;
  color: #aaa;
}
"""


def build_full_html(executions, logs_by_exec, summary, workflow_filter, last_n):
    """
    Assemble the complete HTML document from all the pieces.
    """
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    summary_html = render_summary_box(summary, workflow_filter, last_n)

    if executions:
        blocks = [
            render_execution_block(e, logs_by_exec.get(e["id"], []))
            for e in executions
        ]
        executions_html = "\n".join(blocks)
    else:
        executions_html = '<p class="none">No executions found.</p>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Workflow Log Report</title>
  <style>{CSS}</style>
</head>
<body>
  {summary_html}

  <p class="hint">
    Showing {len(executions)} execution(s), newest first &mdash;
    click any bar to expand its event log.
  </p>

  {executions_html}

  <div class="footer">
    Generated {generated_at} &mdash; source: {escape_html(DATABASE_PATH)}
  </div>
</body>
</html>"""


# =============================================================================
# 6. Entry point
# =============================================================================

def main():
    workflow_filter, last_n = parse_args()

    # Make sure the database actually exists before trying to open it
    if not os.path.exists(DATABASE_PATH):
        print(f"Database not found: {DATABASE_PATH}")
        print("Run:  python scripts/init_db.py")
        sys.exit(1)

    # Connect using SQLiteClient (not raw sqlite3) so the code stays
    # compatible if you later switch to Supabase.
    db = SQLiteClient(DATABASE_PATH)

    print(f"Reading from:  {DATABASE_PATH}")
    if workflow_filter:
        print(f"  workflow:    {workflow_filter}")
    if last_n:
        print(f"  limit:       last {last_n} executions")

    # Fetch executions
    executions = fetch_executions(db, workflow_filter, last_n)
    print(f"  executions:  {len(executions)} found")

    if not executions:
        print("\nNo executions found. Run a workflow first:")
        print("  python templates/workflow_template/run.py")
        sys.exit(0)

    # Fetch all log events, one query per execution
    logs_by_exec = {}
    for execution in executions:
        exec_id = execution["id"]
        logs = fetch_logs_for_execution(db, exec_id)
        logs_by_exec[exec_id] = logs
        status = execution.get("status", "?")
        print(f"  {exec_id[:8]}  [{status:^9}]  {len(logs)} event(s)")

    # Compute summary statistics from the execution list
    summary = compute_summary(executions)

    # Build and write the HTML report
    html = build_full_html(executions, logs_by_exec, summary, workflow_filter, last_n)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    abs_path = os.path.abspath(OUTPUT_FILE)
    print(f"\nReport written: {abs_path}")

    # Open in the system's default browser
    webbrowser.open(f"file:///{abs_path.replace(os.sep, '/')}")
    print("Opened in browser.")


if __name__ == "__main__":
    main()
