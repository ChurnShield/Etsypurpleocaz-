# SYSTEM_ARCHITECTURE.md

## 3-Layer Dual Learning Agentic AI System

---

## 1. System Overview

A three-tier intelligent workflow automation system where an **Orchestrator** executes tasks, a **Small Brain** learns per-workflow patterns, and a **Big Brain** detects cross-workflow insights. Every execution is logged, analysed, and used to generate improvement proposals — making the system smarter with every run.

**Key Innovation:** Dual learning loops. The Small Brain learns from individual workflow executions and proposes per-workflow improvements. The Big Brain connects patterns across all workflows and proposes system-wide optimisations. Together, they transform static automation into a self-improving system.

**Tech Stack:**

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| Database (Dev) | SQLite |
| Database (Prod) | Supabase |
| LLM | Claude API (Anthropic) |
| API Layer | FastAPI |
| Config | python-dotenv |

---

## 2. Three-Tier Architecture

```
┌─────────────────────────────────────────────────────────┐
│  BIG BRAIN (CTO / System Manager)                       │
│                                                         │
│  Scope: ALL workflows                                   │
│  Runs: Scheduled (daily/weekly) or on-demand            │
│  Reads: execution_logs, executions, workflows           │
│  Writes: proposals (system-wide, workflow_id = NULL)    │
│                                                         │
│  Responsibilities:                                      │
│  - Cross-workflow pattern detection                     │
│  - System-wide monitoring (15 categories)               │
│  - Security issue tracking                              │
│  - Brain memory storage                                 │
│  - System-wide improvement proposals                    │
│                                                         │
│  Proposes:                                              │
│  - Shared tool optimisations                            │
│  - System-wide error patterns                           │
│  - Infrastructure improvements                          │
│  - Cross-workflow insights                              │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  SMALL BRAIN (Manager / Per-Workflow Intelligence)      │
│                                                         │
│  Scope: ONE workflow at a time                          │
│  Runs: After every N executions (default: 15)           │
│  Reads: execution_logs for its workflow                 │
│  Writes: proposals (workflow-specific)                  │
│                                                         │
│  Responsibilities:                                      │
│  - Per-workflow pattern analysis                        │
│  - Learns from every execution                          │
│  - Decision-making (tools, params, validators)          │
│  - Domain knowledge accumulation                        │
│                                                         │
│  Proposes:                                              │
│  - Validator threshold adjustments                      │
│  - Tool parameter optimisations                         │
│  - Prompt improvements                                  │
│  - Workflow step reordering                             │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  ORCHESTRATOR (Worker Bee / Execution Layer)            │
│                                                         │
│  Scope: ONE execution at a time                         │
│  Runs: On trigger (webhook, schedule, manual)           │
│  Reads: Workflow config + Small Brain instructions      │
│  Writes: execution_logs, executions                     │
│                                                         │
│  Responsibilities:                                      │
│  - Mechanical execution (zero thinking)                 │
│  - Takes instructions from Small Brain                  │
│  - Validator loops (until pass or max retries)          │
│  - Mechanical retry handling                            │
│  - Logs EVERYTHING for Brain analysis                   │
│                                                         │
│  Logs:                                                  │
│  - Phase start/end timestamps                           │
│  - Tool calls + results + duration                      │
│  - Validation pass/fail + issues                        │
│  - Errors + stack traces                                │
│  - Final outcome quality score                          │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Database Schema

All tables are SQLite-compatible and designed to work with Supabase in production via a shared client interface.

### Table: `workflows`

Stores workflow definitions and aggregate statistics.

```sql
CREATE TABLE workflows (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    domain TEXT,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_runs INTEGER DEFAULT 0,
    successful_runs INTEGER DEFAULT 0,
    failed_runs INTEGER DEFAULT 0,
    avg_duration_ms INTEGER,
    last_run_at DATETIME
);
```

### Table: `executions`

One row per workflow run. Links to the parent workflow.

```sql
CREATE TABLE executions (
    id TEXT PRIMARY KEY,
    workflow_id TEXT NOT NULL,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    status TEXT,  -- 'running', 'completed', 'failed'
    outcome_quality FLOAT,  -- 0.0 to 1.0
    input_summary TEXT,
    output_summary TEXT,
    error_message TEXT,
    metadata TEXT,  -- JSON field
    FOREIGN KEY (workflow_id) REFERENCES workflows(id)
);
```

### Table: `execution_logs`

Granular event log. Every tool call, validation, and phase transition is recorded here. This is the primary data source for both Brains.

```sql
CREATE TABLE execution_logs (
    id TEXT PRIMARY KEY,
    execution_id TEXT NOT NULL,
    workflow_id TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    phase TEXT,
    event_type TEXT,  -- 'tool_call', 'tool_result', 'validation', 'error', 'phase_start', 'phase_end'
    tool_name TEXT,
    validator_name TEXT,
    success BOOLEAN,
    duration_ms INTEGER,
    metadata TEXT,  -- JSON field
    error_message TEXT,
    FOREIGN KEY (execution_id) REFERENCES executions(id)
);
```

### Table: `proposals`

Improvement proposals generated by either Brain. Human-approved before being applied.

```sql
CREATE TABLE proposals (
    id TEXT PRIMARY KEY,
    workflow_id TEXT,  -- NULL = system-wide (Big Brain)
    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT,  -- 'pending', 'approved', 'rejected', 'applied'
    proposal_type TEXT,
    title TEXT,
    description TEXT,  -- Markdown
    pattern_data TEXT,  -- JSON with metrics that triggered the proposal
    proposed_changes TEXT,  -- JSON with specific changes
    applied_at DATETIME,
    applied_by TEXT,
    FOREIGN KEY (workflow_id) REFERENCES workflows(id)
);
```

### Indexes

```sql
CREATE INDEX idx_execution_logs_execution_id ON execution_logs(execution_id);
CREATE INDEX idx_execution_logs_workflow_id ON execution_logs(workflow_id);
CREATE INDEX idx_execution_logs_timestamp ON execution_logs(timestamp);
CREATE INDEX idx_executions_workflow_id ON executions(workflow_id);
```

---

## 4. ExecutionLogger Class

The ExecutionLogger is the most critical infrastructure component. Without comprehensive logging, the Brains have nothing to learn from. Every workflow execution must use it.

**Location:** `lib/orchestrator/execution_logger.py`

```python
import uuid
import json
from datetime import datetime


class ExecutionLogger:
    """Logs every step of workflow execution to database.

    CRITICAL: Always use in a try/finally block to ensure flush() is called.
    """

    def __init__(self, execution_id: str, workflow_id: str, db_client):
        self.execution_id = execution_id
        self.workflow_id = workflow_id
        self.db = db_client
        self._buffer = []
        self._current_phase = None

    def phase_start(self, phase_name: str):
        """Log when a phase begins."""
        self._current_phase = phase_name
        self._log_event(
            event_type="phase_start",
            phase=phase_name,
            success=True
        )

    def phase_end(self, phase_name: str, success: bool):
        """Log when a phase completes."""
        self._log_event(
            event_type="phase_end",
            phase=phase_name,
            success=success
        )
        self._current_phase = None

    def tool_call(self, tool_name: str, params: dict):
        """Log before calling a tool."""
        self._log_event(
            event_type="tool_call",
            tool_name=tool_name,
            metadata=params
        )

    def tool_result(self, tool_name: str, result: dict, success: bool, duration_ms: int):
        """Log after tool returns."""
        self._log_event(
            event_type="tool_result",
            tool_name=tool_name,
            success=success,
            duration_ms=duration_ms,
            metadata=result
        )

    def validation_event(self, validator_name: str, passed: bool, issues: list):
        """Log validator results."""
        self._log_event(
            event_type="validation",
            validator_name=validator_name,
            success=passed,
            metadata={"issues": issues}
        )

    def error(self, error_message: str, metadata: dict = None):
        """Log errors."""
        self._log_event(
            event_type="error",
            success=False,
            error_message=error_message,
            metadata=metadata or {}
        )

    def flush(self):
        """Write buffered logs to database. MUST be called in finally block."""
        for log_entry in self._buffer:
            self.db.table("execution_logs").insert(log_entry).execute()
        self._buffer = []

    def _log_event(self, event_type: str, phase: str = None,
                   tool_name: str = None, validator_name: str = None,
                   success: bool = None, duration_ms: int = None,
                   metadata: dict = None, error_message: str = None):
        """Internal: buffer a log event."""
        self._buffer.append({
            "id": str(uuid.uuid4()),
            "execution_id": self.execution_id,
            "workflow_id": self.workflow_id,
            "timestamp": datetime.utcnow().isoformat(),
            "phase": phase or self._current_phase,
            "event_type": event_type,
            "tool_name": tool_name,
            "validator_name": validator_name,
            "success": success,
            "duration_ms": duration_ms,
            "metadata": json.dumps(metadata) if metadata else None,
            "error_message": error_message
        })
```

### Critical Usage Pattern

```python
try:
    logger = ExecutionLogger(exec_id, workflow_id, db)
    logger.phase_start("Phase 1: Data Collection")
    # ... execution code ...
    logger.phase_end("Phase 1: Data Collection", success=True)
finally:
    logger.flush()  # ← ALWAYS in finally block
```

---

## 5. Base Classes

### BaseValidator

Standard interface for all validators. Every quality check in every workflow implements this.

**Location:** `lib/orchestrator/base_validator.py`

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseValidator(ABC):
    """Base class for all validators.

    Every validator returns a standard dict with:
    - passed: Did it meet the threshold?
    - issues: What problems were found?
    - needs_more: Should the Orchestrator retry?
    """

    @abstractmethod
    def validate(self, data: Any, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Returns:
            {
                'passed': bool,
                'issues': List[str],
                'needs_more': bool,
                'validator_name': str,
                'metadata': Dict[str, Any]
            }
        """
        pass

    def get_name(self) -> str:
        return self.__class__.__name__
```

### BaseTool

Standard interface for all tools. Every external interaction (API call, database query, LLM call) implements this.

**Location:** `lib/orchestrator/base_tool.py`

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseTool(ABC):
    """Base class for all tools.

    Every tool returns a standard dict with:
    - success: Did the tool execute without error?
    - data: The result payload
    - error: Error message if failed
    """

    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Returns:
            {
                'success': bool,
                'data': Any,
                'error': Optional[str],
                'tool_name': str,
                'metadata': Dict[str, Any]
            }
        """
        pass

    def get_name(self) -> str:
        return self.__class__.__name__
```

---

## 6. SQLite Client (Supabase-Compatible)

A database client that mirrors Supabase's query builder API. Develop locally with SQLite, deploy to Supabase without changing any query code.

**Location:** `lib/common_tools/sqlite_client.py`

```python
import sqlite3
import json
from typing import Any, Optional

_client = None


def get_client(db_path: str = None):
    """Get or create the database client singleton."""
    global _client
    if _client is None:
        from config import DATABASE_PATH
        _client = SQLiteClient(db_path or DATABASE_PATH)
    return _client


class SQLiteClient:
    """Supabase-compatible query builder for SQLite.

    Usage mirrors Supabase client:
        db.table('executions').select('*').eq('id', '123').execute()
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._reset()

    def _reset(self):
        self._table = None
        self._operation = None
        self._columns = "*"
        self._filters = []
        self._data = None
        self._order = ""
        self._limit = ""

    def table(self, table_name: str):
        self._reset()
        self._table = table_name
        return self

    def select(self, columns: str = "*"):
        self._operation = "SELECT"
        self._columns = columns
        return self

    def insert(self, data: dict):
        self._operation = "INSERT"
        self._data = data
        return self

    def update(self, data: dict):
        self._operation = "UPDATE"
        self._data = data
        return self

    def delete(self):
        self._operation = "DELETE"
        return self

    def eq(self, column: str, value: Any):
        self._filters.append((column, "=", value))
        return self

    def gt(self, column: str, value: Any):
        self._filters.append((column, ">", value))
        return self

    def gte(self, column: str, value: Any):
        self._filters.append((column, ">=", value))
        return self

    def lt(self, column: str, value: Any):
        self._filters.append((column, "<", value))
        return self

    def lte(self, column: str, value: Any):
        self._filters.append((column, "<=", value))
        return self

    def order(self, column: str, desc: bool = False):
        self._order = f"ORDER BY {column} {'DESC' if desc else 'ASC'}"
        return self

    def limit(self, count: int):
        self._limit = f"LIMIT {count}"
        return self

    def execute(self):
        cursor = self.conn.cursor()

        if self._operation == "SELECT":
            where = self._build_where()
            sql = f"SELECT {self._columns} FROM {self._table}{where}"
            sql = f"{sql} {self._order} {self._limit}".strip()
            values = [f[2] for f in self._filters]
            cursor.execute(sql, values)
            rows = cursor.fetchall()
            self._reset()
            return [dict(row) for row in rows]

        elif self._operation == "INSERT":
            cols = ", ".join(self._data.keys())
            placeholders = ", ".join(["?"] * len(self._data))
            sql = f"INSERT INTO {self._table} ({cols}) VALUES ({placeholders})"
            cursor.execute(sql, list(self._data.values()))
            self.conn.commit()
            self._reset()
            return [self._data]

        elif self._operation == "UPDATE":
            set_clause = ", ".join([f"{k} = ?" for k in self._data.keys()])
            where = self._build_where()
            sql = f"UPDATE {self._table} SET {set_clause}{where}"
            values = list(self._data.values()) + [f[2] for f in self._filters]
            cursor.execute(sql, values)
            self.conn.commit()
            self._reset()
            return []

        elif self._operation == "DELETE":
            where = self._build_where()
            sql = f"DELETE FROM {self._table}{where}"
            values = [f[2] for f in self._filters]
            cursor.execute(sql, values)
            self.conn.commit()
            self._reset()
            return []

    def _build_where(self) -> str:
        if not self._filters:
            return ""
        conditions = [f"{col} {op} ?" for col, op, val in self._filters]
        return " WHERE " + " AND ".join(conditions)
```

---

## 7. LLM Client

A thin wrapper around the Claude API that standardises LLM calls across the system.

**Location:** `lib/common_tools/llm_client.py`

```python
import anthropic
from config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL


def get_llm_client():
    """Get a configured Anthropic client."""
    return anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def call_llm(prompt: str, system: str = None, max_tokens: int = 4096,
             temperature: float = 0.7) -> dict:
    """Make a single LLM call and return structured result.

    Args:
        prompt: The user message content.
        system: Optional system prompt.
        max_tokens: Maximum response tokens.
        temperature: Creativity level (0.0 = deterministic, 1.0 = creative).

    Returns:
        {
            'success': bool,
            'content': str,        # The response text
            'usage': dict,         # Token usage stats
            'error': Optional[str]
        }
    """
    try:
        client = get_llm_client()
        kwargs = {
            "model": ANTHROPIC_MODEL,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}]
        }
        if system:
            kwargs["system"] = system

        response = client.messages.create(**kwargs)

        return {
            "success": True,
            "content": response.content[0].text,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            },
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "content": None,
            "usage": None,
            "error": str(e)
        }
```

---

## 8. Configuration Management

All settings live in `config.py`. Nothing is hardcoded in business logic.

**Location:** `config.py`

```python
import os
from dotenv import load_dotenv

load_dotenv()

# ── API Configuration ──
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

# ── Database ──
DATABASE_PATH = os.getenv("DATABASE_PATH", "data/system.db")

# ── Execution Settings ──
DEFAULT_TIMEOUT_SECONDS = 120
MAX_RETRIES = 3

# ── Small Brain Settings ──
PROPOSAL_THRESHOLD_RUNS = 15       # Generate proposals after N runs
MIN_PATTERN_CONFIDENCE = 0.7       # Only propose if 70%+ confidence

# ── Big Brain Settings ──
BIG_BRAIN_MIN_WORKFLOWS = 2        # Need at least 2 workflows to compare
BIG_BRAIN_MIN_RUNS_PER_WORKFLOW = 10  # Need enough data per workflow
```

**Location:** `.env.example`

```
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-sonnet-4-20250514
DATABASE_PATH=data/system.db
```

---

## 9. Directory Structure

```
agents_system/
├── lib/
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   ├── base_validator.py      # BaseValidator ABC
│   │   ├── base_tool.py           # BaseTool ABC
│   │   └── execution_logger.py    # ExecutionLogger class
│   ├── brain/
│   │   ├── __init__.py
│   │   ├── small_brain.py         # Per-workflow intelligence
│   │   └── big_brain.py           # Cross-workflow intelligence
│   └── common_tools/
│       ├── __init__.py
│       ├── sqlite_client.py       # Supabase-compatible DB client
│       └── llm_client.py          # Claude API wrapper
├── workflows/                      # Your workflows go here
│   └── README.md
├── data/
│   └── system.db                  # SQLite database (gitignored)
├── scripts/
│   ├── init_db.py                 # Creates tables and indexes
│   └── run_workflow.py            # CLI workflow runner
├── tests/
│   ├── __init__.py
│   ├── test_execution_logger.py
│   ├── test_sqlite_client.py
│   └── test_base_classes.py
├── config.py                       # All configuration
├── requirements.txt
├── .env                            # Local secrets (gitignored)
├── .env.example                    # Template for .env
└── .gitignore
```

---

## 10. Learning Mechanism

### Small Brain Process

The Small Brain runs after every N executions (default: 15) for a specific workflow.

```
1. QUERY    → Pull execution_logs for this workflow (last N runs)

2. ANALYSE  → Calculate metrics:
               - Validator pass rates per validator
               - Tool performance (avg duration, failure rate)
               - Outcome quality trends (improving? declining?)
               - Retry frequency per phase

3. DETECT   → Identify actionable patterns:
               - "ValidatorX fails 40% of the time"
               - "ToolY averages 3200ms but spiked to 8000ms last 5 runs"
               - "Outcome quality dropped from 0.8 to 0.6 over last 10 runs"

4. GENERATE → Use Claude API to create a structured proposal:
               - Title: Clear one-line summary
               - Description: Analysis + recommendation (Markdown)
               - Pattern data: Raw metrics (JSON)
               - Proposed changes: Specific config/code changes (JSON)

5. STORE    → Write to proposals table (status: 'pending')

6. AWAIT    → Human reviews and approves/rejects
```

### Big Brain Process

The Big Brain runs on a schedule (daily/weekly) and looks across all workflows.

```
1. QUERY     → Pull execution_logs for ALL workflows

2. AGGREGATE → Cross-workflow metrics:
                - Common error patterns across workflows
                - Shared tool performance comparisons
                - Time-based patterns (time-of-day, day-of-week)
                - System resource trends

3. DETECT    → System-wide patterns:
                - "LLM API latency increases 2x between 2-4am UTC"
                - "3 workflows share the same failing validation pattern"
                - "Workflow A's output could be Workflow B's input"

4. GENERATE  → System-level proposals (workflow_id = NULL):
                - Infrastructure improvements
                - Shared tool optimisations
                - New workflow suggestions
                - Security alerts

5. STORE     → Write to proposals table

6. AWAIT     → Human reviews and approves/rejects
```

### Key Principle: Human-in-the-Loop

Neither Brain applies changes automatically. All proposals require human approval. This is critical for safety and trust, especially when starting out. As confidence grows, you can selectively enable auto-apply for low-risk proposals.

---

## 11. Database Initialisation Script

**Location:** `scripts/init_db.py`

```python
"""Initialise the SQLite database with all required tables and indexes."""

import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATABASE_PATH


def init_db():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS workflows (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            domain TEXT,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            total_runs INTEGER DEFAULT 0,
            successful_runs INTEGER DEFAULT 0,
            failed_runs INTEGER DEFAULT 0,
            avg_duration_ms INTEGER,
            last_run_at DATETIME
        );

        CREATE TABLE IF NOT EXISTS executions (
            id TEXT PRIMARY KEY,
            workflow_id TEXT NOT NULL,
            started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            completed_at DATETIME,
            status TEXT,
            outcome_quality FLOAT,
            input_summary TEXT,
            output_summary TEXT,
            error_message TEXT,
            metadata TEXT,
            FOREIGN KEY (workflow_id) REFERENCES workflows(id)
        );

        CREATE TABLE IF NOT EXISTS execution_logs (
            id TEXT PRIMARY KEY,
            execution_id TEXT NOT NULL,
            workflow_id TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            phase TEXT,
            event_type TEXT,
            tool_name TEXT,
            validator_name TEXT,
            success BOOLEAN,
            duration_ms INTEGER,
            metadata TEXT,
            error_message TEXT,
            FOREIGN KEY (execution_id) REFERENCES executions(id)
        );

        CREATE TABLE IF NOT EXISTS proposals (
            id TEXT PRIMARY KEY,
            workflow_id TEXT,
            generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT,
            proposal_type TEXT,
            title TEXT,
            description TEXT,
            pattern_data TEXT,
            proposed_changes TEXT,
            applied_at DATETIME,
            applied_by TEXT,
            FOREIGN KEY (workflow_id) REFERENCES workflows(id)
        );

        CREATE INDEX IF NOT EXISTS idx_execution_logs_execution_id
            ON execution_logs(execution_id);
        CREATE INDEX IF NOT EXISTS idx_execution_logs_workflow_id
            ON execution_logs(workflow_id);
        CREATE INDEX IF NOT EXISTS idx_execution_logs_timestamp
            ON execution_logs(timestamp);
        CREATE INDEX IF NOT EXISTS idx_executions_workflow_id
            ON executions(workflow_id);
    """)

    conn.commit()
    conn.close()
    print(f"Database initialised at: {DATABASE_PATH}")


if __name__ == "__main__":
    init_db()
```

---

## 12. Tech Stack & Dependencies

**Location:** `requirements.txt`

```
anthropic>=0.18.0
python-dotenv>=1.0.0
pytest>=7.4.0
pytest-cov>=4.1.0
fastapi>=0.104.0
uvicorn>=0.24.0
requests>=2.31.0
```

---

## 13. Testing Strategy

Test-Driven Development (TDD). Write tests before implementation. Target: 80%+ code coverage.

### Example Tests

```python
# tests/test_sqlite_client.py
import pytest
from lib.common_tools.sqlite_client import SQLiteClient


@pytest.fixture
def db(tmp_path):
    """Create a fresh test database."""
    client = SQLiteClient(str(tmp_path / "test.db"))
    client.conn.execute("""
        CREATE TABLE executions (
            id TEXT PRIMARY KEY,
            workflow_id TEXT,
            status TEXT
        )
    """)
    return client


def test_insert_and_query(db):
    db.table("executions").insert({
        "id": "test_123",
        "workflow_id": "test_workflow",
        "status": "running"
    }).execute()

    result = db.table("executions").select("*").eq("id", "test_123").execute()
    assert len(result) == 1
    assert result[0]["status"] == "running"


def test_update(db):
    db.table("executions").insert({
        "id": "test_456",
        "workflow_id": "test_workflow",
        "status": "running"
    }).execute()

    db.table("executions").update({"status": "completed"}).eq("id", "test_456").execute()
    result = db.table("executions").select("*").eq("id", "test_456").execute()
    assert result[0]["status"] == "completed"


def test_delete(db):
    db.table("executions").insert({
        "id": "test_789",
        "workflow_id": "test_workflow",
        "status": "failed"
    }).execute()

    db.table("executions").delete().eq("id", "test_789").execute()
    result = db.table("executions").select("*").eq("id", "test_789").execute()
    assert len(result) == 0


def test_filter_by_workflow(db):
    db.table("executions").insert({"id": "a", "workflow_id": "wf1", "status": "completed"}).execute()
    db.table("executions").insert({"id": "b", "workflow_id": "wf2", "status": "completed"}).execute()
    db.table("executions").insert({"id": "c", "workflow_id": "wf1", "status": "failed"}).execute()

    result = db.table("executions").select("*").eq("workflow_id", "wf1").execute()
    assert len(result) == 2


def test_empty_query_returns_empty_list(db):
    result = db.table("executions").select("*").eq("id", "nonexistent").execute()
    assert result == []
```

```python
# tests/test_execution_logger.py
import pytest
from lib.orchestrator.execution_logger import ExecutionLogger
from lib.common_tools.sqlite_client import SQLiteClient


@pytest.fixture
def setup(tmp_path):
    """Create test database with execution_logs table."""
    db = SQLiteClient(str(tmp_path / "test.db"))
    db.conn.executescript("""
        CREATE TABLE execution_logs (
            id TEXT PRIMARY KEY,
            execution_id TEXT,
            workflow_id TEXT,
            timestamp TEXT,
            phase TEXT,
            event_type TEXT,
            tool_name TEXT,
            validator_name TEXT,
            success BOOLEAN,
            duration_ms INTEGER,
            metadata TEXT,
            error_message TEXT
        );
    """)
    logger = ExecutionLogger("exec_001", "wf_001", db)
    return logger, db


def test_phase_logging(setup):
    logger, db = setup
    logger.phase_start("Phase 1")
    logger.phase_end("Phase 1", success=True)
    logger.flush()

    logs = db.table("execution_logs").select("*").eq("execution_id", "exec_001").execute()
    assert len(logs) == 2
    assert logs[0]["event_type"] == "phase_start"
    assert logs[1]["event_type"] == "phase_end"


def test_tool_logging(setup):
    logger, db = setup
    logger.tool_call("my_tool", {"param": "value"})
    logger.tool_result("my_tool", {"data": "result"}, success=True, duration_ms=150)
    logger.flush()

    logs = db.table("execution_logs").select("*").eq("tool_name", "my_tool").execute()
    assert len(logs) == 2
    assert logs[1]["duration_ms"] == 150


def test_flush_clears_buffer(setup):
    logger, db = setup
    logger.phase_start("Phase 1")
    logger.flush()
    logger.flush()  # Second flush should write nothing

    logs = db.table("execution_logs").select("*").execute()
    assert len(logs) == 1
```

```python
# tests/test_base_classes.py
import pytest
from lib.orchestrator.base_validator import BaseValidator
from lib.orchestrator.base_tool import BaseTool


class MockValidator(BaseValidator):
    def validate(self, data, context=None):
        passed = len(data) > 5
        return {
            "passed": passed,
            "issues": [] if passed else ["Data too short"],
            "needs_more": not passed,
            "validator_name": self.get_name(),
            "metadata": {"length": len(data)}
        }


class MockTool(BaseTool):
    def execute(self, **kwargs):
        return {
            "success": True,
            "data": f"Processed: {kwargs.get('input', '')}",
            "error": None,
            "tool_name": self.get_name(),
            "metadata": {}
        }


def test_validator_pass():
    v = MockValidator()
    result = v.validate("long enough string")
    assert result["passed"] is True
    assert result["issues"] == []


def test_validator_fail():
    v = MockValidator()
    result = v.validate("short")
    assert result["passed"] is False
    assert len(result["issues"]) > 0


def test_validator_name():
    v = MockValidator()
    assert v.get_name() == "MockValidator"


def test_tool_execute():
    t = MockTool()
    result = t.execute(input="test data")
    assert result["success"] is True
    assert "test data" in result["data"]


def test_tool_name():
    t = MockTool()
    assert t.get_name() == "MockTool"
```

---

## 14. Implementation Checklist

### Database
- [ ] `data/system.db` created via `scripts/init_db.py`
- [ ] All 4 tables created with indexes
- [ ] Can manually insert and query data

### Core Classes
- [ ] `BaseValidator` class implemented
- [ ] `BaseTool` class implemented
- [ ] `ExecutionLogger` class implemented
- [ ] `SQLiteClient` class implemented
- [ ] `llm_client.py` wrapper created

### Tests
- [ ] 5+ tests for database operations
- [ ] 3+ tests for ExecutionLogger
- [ ] 2+ tests for base classes
- [ ] All tests passing
- [ ] 80%+ code coverage

### Configuration
- [ ] `config.py` created with all settings
- [ ] `.env.example` created
- [ ] `.env` created locally (not committed)
- [ ] `.gitignore` includes `.env`, `data/`, `__pycache__/`

### Documentation
- [ ] This `SYSTEM_ARCHITECTURE.md` reviewed
- [ ] Full directory structure created
- [ ] All `__init__.py` files in place

---

## What's Next

With this infrastructure in place, you are ready to build your first workflow. The architecture is completely workflow-agnostic — the same logging, validation, and learning system works regardless of what the workflow does.

Your first workflow will plug into this architecture by:

1. **Defining tools** — extend `BaseTool` for each external interaction
2. **Defining validators** — extend `BaseValidator` for each quality check
3. **Writing an orchestrator** — a script that chains tools together using `ExecutionLogger`
4. **Letting the Small Brain learn** — after 15+ executions, it analyses patterns and proposes improvements
5. **Adding the Big Brain** — once you have 2+ workflows with 10+ runs each, it connects insights across them
