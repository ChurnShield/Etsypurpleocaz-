**For AI Assistants**: Read this file first before working with this codebase. It contains critical rules, patterns, and the reasoning behind them.

---

## Contents

1. [Purpose & Overview](#purpose--overview)
2. [Critical Rules (Must Follow)](#critical-rules-must-follow)
3. [Architecture & Structure](#architecture--structure)
4. [Project Conventions](#project-conventions)
5. [Development Workflow](#development-workflow)
6. [Common Commands](#common-commands)
7. [The WHY (Important Context)](#the-why-important-context)
8. [Boundaries & Constraints](#boundaries--constraints)
9. [Reference Files](#reference-files)
10. [Out of Scope](#out-of-scope)
11. [Emergency Procedures](#emergency-procedures)

---

## Purpose & Overview

**What this project does**: 3-Layer Dual Learning Agentic AI System - A self-improving workflow automation platform where an Orchestrator executes tasks mechanically, a Small Brain learns per-workflow patterns, and a Big Brain detects cross-workflow insights.

**Tech Stack**:

- Language: Python 3.10+
- Database: SQLite (development), Supabase (production)
- Framework: FastAPI 0.104.0+
- LLM: Anthropic Claude API (claude-sonnet-4-20250514)
- Server: uvicorn 0.24.0+
- Testing: pytest 7.4.0+, pytest-cov 4.1.0+
- Config: python-dotenv 1.0.0+
- HTTP Client: requests 2.31.0+

**Key Innovation**: Dual learning loops. The Small Brain analyzes individual workflow executions after 15+ runs and proposes per-workflow improvements. The Big Brain connects patterns across all workflows (2+ workflows with 10+ runs each) and proposes system-wide optimizations. Together, they transform static automation into a self-improving system.

---

## Critical Rules (Must Follow)

### 🚫 DO NOT Modify or Delete

**Critical Files** (never modify without explicit user permission):

- `c:\Users\andyn\OneDrive\Desktop\NEW AI PROJECT\lib\orchestrator\base_validator.py` → Base contract for all validators; changing breaks all workflows
- `c:\Users\andyn\OneDrive\Desktop\NEW AI PROJECT\lib\orchestrator\base_tool.py` → Base contract for all tools; changing breaks all workflows
- `c:\Users\andyn\OneDrive\Desktop\NEW AI PROJECT\lib\orchestrator\execution_logger.py` → Critical for learning system; modifications break Brain analysis
- `c:\Users\andyn\OneDrive\Desktop\NEW AI PROJECT\lib\common_tools\sqlite_client.py` → Supabase compatibility layer; changes break production deployment
- `c:\Users\andyn\OneDrive\Desktop\NEW AI PROJECT\scripts\init_db.py` → Database schema definition; changes require migration strategy
- `c:\Users\andyn\OneDrive\Desktop\NEW AI PROJECT\config.py` → System configuration; changes cascade throughout system
- `c:\Users\andyn\OneDrive\Desktop\NEW AI PROJECT\data\system.db` → Production data; corruption is unrecoverable

**WHY**: These files form the foundation infrastructure. The entire learning system depends on consistent logging interfaces, standardized tool/validator contracts, and stable database schemas. Modifying them without careful migration planning will break all existing workflows and invalidate historical learning data.

### ✅ ALWAYS Do

**Pattern 1: ExecutionLogger with try/finally**:

```python
from lib.orchestrator.execution_logger import ExecutionLogger
from lib.common_tools.sqlite_client import get_client

try:
    db = get_client()
    logger = ExecutionLogger(exec_id, workflow_id, db)
    logger.phase_start("Phase 1: Data Collection")
    # ... your workflow code ...
    logger.phase_end("Phase 1: Data Collection", success=True)
finally:
    logger.flush()  # CRITICAL: Always in finally block
```

**WHY**: Logs are buffered in memory for performance (batched writes). Small Brain depends on complete execution logs to detect patterns. Without flush() in a finally block, the buffer is lost on exceptions. Lost logs = blind spots in the learning system, and the system appears to work but never improves.

**Pattern 2: Extend Base Classes**:

```python
from lib.orchestrator.base_tool import BaseTool

class MyCustomTool(BaseTool):
    def execute(self, **kwargs) -> dict:
        try:
            result = perform_operation(**kwargs)
            return {
                'success': True,
                'data': result,
                'error': None,
                'tool_name': self.get_name(),
                'metadata': {}
            }
        except Exception as e:
            return {
                'success': False,
                'data': None,
                'error': str(e),
                'tool_name': self.get_name(),
                'metadata': {'exception_type': type(e).__name__}
            }
```

**WHY**: Standardized return format enables Brain to analyze ANY tool. The `get_name()` method is used for grouping in analytics. Consistent interfaces allow the Orchestrator to treat all tools uniformly. Future Brain features depend on this contract.

**Pattern 3: Use SQLiteClient Query Builder**:

```python
from lib.common_tools.sqlite_client import get_client

db = get_client()  # Singleton pattern
results = db.table('executions') \
    .select('*') \
    .eq('workflow_id', 'my_workflow') \
    .order('started_at', desc=True) \
    .limit(10) \
    .execute()
```

**WHY**: Development uses SQLite, production uses Supabase. Query builder API is identical for both. Code written with SQLiteClient works unchanged in production. Chainable methods prevent SQL injection.

**Pattern 4: Import from config.py**:

```python
from config import (
    ANTHROPIC_MODEL,
    DATABASE_PATH,
    MAX_RETRIES,
    PROPOSAL_THRESHOLD_RUNS
)
# Never hardcode these values
```

**WHY**: All settings live in config.py. Nothing is hardcoded in business logic. This ensures environment-specific values are managed centrally and prevents security risks from hardcoded credentials.

### ❌ NEVER Do

**Anti-pattern 1: Forgetting ExecutionLogger.flush()**:

```python
# WRONG - No finally block
logger = ExecutionLogger(exec_id, workflow_id, db)
logger.phase_start("Phase 1")
risky_operation()  # Exception here loses all logs

# RIGHT - Always use try/finally
try:
    logger = ExecutionLogger(exec_id, workflow_id, db)
    logger.phase_start("Phase 1")
    risky_operation()
finally:
    logger.flush()  # ALWAYS executes
```

**WHY**: Without flush() in a finally block, partial logs are written (only successful phases logged). Brain analyzes incomplete data and proposes incorrect changes. Pattern detection fails because it can't see failure patterns. System appears to work but never improves.

**Anti-pattern 2: Bypassing base classes**:

```python
# WRONG - Custom implementation
class MyValidator:
    def check(self, data):
        return True

# RIGHT - Extend BaseValidator
from lib.orchestrator.base_validator import BaseValidator

class MyValidator(BaseValidator):
    def validate(self, data, context=None):
        return {
            'passed': True,
            'issues': [],
            'needs_more': False,
            'validator_name': self.get_name(),
            'metadata': {}
        }
```

**WHY**: Inconsistent interfaces break Brain analysis. Analytics queries fail because they expect specific dict structures. Workflow orchestration fails due to inconsistent error handling. Brain can't generate proposals without proper metadata.

**Anti-pattern 3: Hardcoding configuration values**:

```python
# WRONG - Hardcoded values
api_key = "sk-ant-xxx"
model = "claude-sonnet-4-20250514"
timeout = 120

# RIGHT - Import from config
from config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL, DEFAULT_TIMEOUT_SECONDS
```

**WHY**: Hardcoded values cause environment-specific failures (dev works, prod fails). Security risks from exposed credentials in code. Can't adjust thresholds without code changes. Configuration should be centralized and environment-aware.

**Anti-pattern 4: Direct database access**:

```python
# WRONG - Raw SQL with sqlite3
import sqlite3
conn = sqlite3.connect("data/system.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM executions WHERE id = ?", (exec_id,))

# RIGHT - Use SQLiteClient query builder
from lib.common_tools.sqlite_client import get_client
db = get_client()
results = db.table('executions').select('*').eq('id', exec_id).execute()
```

**WHY**: Different code for dev vs prod creates a maintenance nightmare. Raw SQL is vulnerable to SQL injection. Manual query building is error-prone. Can't swap databases without rewriting all queries.

---

## Architecture & Structure

**Main Language**: Python 3.10+

**Key Directories**:

```
c:\Users\andyn\OneDrive\Desktop\NEW AI PROJECT\
├── lib/                       → Core system libraries
│   ├── orchestrator/          → Execution layer (mechanical worker)
│   │   ├── base_tool.py       → Abstract base class for all tools
│   │   ├── base_validator.py  → Abstract base class for all validators
│   │   └── execution_logger.py → Critical: logs everything for Brain analysis
│   ├── common_tools/          → Shared utilities
│   │   ├── sqlite_client.py   → Supabase-compatible DB client (query builder)
│   │   └── llm_client.py      → Claude API wrapper
│   └── brain/                 → Intelligence layer (future development)
│       ├── small_brain.py     → Per-workflow pattern learning
│       └── big_brain.py       → Cross-workflow insights
├── workflows/                 → Custom workflow implementations go here
├── data/                      → SQLite database storage (gitignored)
│   └── system.db              → Main database (created by init_db.py)
├── scripts/                   → Utility scripts
│   └── init_db.py             → Database initialization (run first)
├── tests/                     → Test suite (pytest)
│   ├── test_base_classes.py   → Tests for BaseTool, BaseValidator
│   ├── test_execution_logger.py → Tests for ExecutionLogger
│   └── test_sqlite_client.py  → Tests for SQLiteClient
├── config.py                  → All configuration (thresholds, API keys)
├── main.py                    → Entry point (example usage)
├── requirements.txt           → Python dependencies
├── .env                       → Local secrets (gitignored)
├── .env.example               → Template for environment variables
└── SYSTEM_ARCHITECTURE.md     → Complete architecture documentation (35KB)
```

**Entry Points**:

- Initialize database: `python scripts/init_db.py`
- Run tests: `pytest tests/ -v`
- Run with coverage: `pytest tests/ --cov=lib --cov-report=html`
- Example execution: `python main.py` (currently a demo)

**Data Flow**:

```
Workflow Trigger → Orchestrator (logs via ExecutionLogger) → Tools/Validators → Database
                                                                                  ↓
Small Brain (analyzes after 15 runs) ← execution_logs ← ExecutionLogger
                   ↓
         Proposals (human approval required)

Big Brain (scheduled analysis) ← ALL execution_logs ← Multiple workflows
                   ↓
    System-wide proposals (human approval required)
```

---

## Project Conventions

**Naming Style**:

- Files: `snake_case.py` (e.g., `execution_logger.py`, `base_tool.py`)
- Classes: `PascalCase` (e.g., `ExecutionLogger`, `SQLiteClient`)
- Base classes: `Base*` prefix (e.g., `BaseValidator`, `BaseTool`)
- Functions/variables: `snake_case` (e.g., `phase_start`, `get_client`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`, `DATABASE_PATH`)
- Private methods: `_prefixed` (e.g., `_reset`, `_log_event`, `_build_where`)

**File Organization**:

- One class per file (ExecutionLogger in execution_logger.py)
- Tests mirror source structure (test_execution_logger.py for execution_logger.py)
- All packages have `__init__.py` files (even if empty)
- Abstract base classes in `/orchestrator` directory

**Error Handling**:

```python
# Standard pattern: Always return structured dicts, never raise in tools
def execute(self, **kwargs) -> dict:
    try:
        result = perform_operation(**kwargs)
        return {
            'success': True,
            'data': result,
            'error': None,
            'tool_name': self.get_name(),
            'metadata': {}
        }
    except Exception as e:
        return {
            'success': False,
            'data': None,
            'error': str(e),
            'tool_name': self.get_name(),
            'metadata': {'exception_type': type(e).__name__}
        }
```

**Configuration**:

- Configuration file: `c:\Users\andyn\OneDrive\Desktop\NEW AI PROJECT\config.py`
- Environment variables loaded via `python-dotenv` from `.env`
- Required vars: `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL`, `DATABASE_PATH`
- Never hardcode: API keys, model names, file paths, thresholds

**Database/Storage Access**:

```python
# ALWAYS use SQLiteClient, NEVER raw sqlite3
from lib.common_tools.sqlite_client import get_client

db = get_client()  # Singleton pattern
results = db.table('execution_logs') \
    .select('event_type, success, duration_ms') \
    .eq('workflow_id', workflow_id) \
    .gte('timestamp', start_date) \
    .order('timestamp', desc=False) \
    .execute()
```

---

## Development Workflow

### Test-Driven Development (TDD)

**When to write tests first**:

- New base classes or core infrastructure
- New tools or validators
- Bug fixes that broke existing functionality
- Database schema changes

**Test Structure**:

```
tests/
├── test_base_classes.py       → Tests for BaseTool, BaseValidator
├── test_execution_logger.py   → Tests for ExecutionLogger
├── test_sqlite_client.py      → Tests for SQLiteClient
└── test_llm_client.py         → Tests for LLM wrapper (future)
```

**Run tests**:

```shell
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_execution_logger.py -v

# With coverage report
pytest tests/ --cov=lib --cov-report=html

# Specific test function
pytest tests/test_sqlite_client.py::test_insert_and_query -v
```

### Git Workflow

**Branch naming**:

- Features: `feature/description` (e.g., `feature/add-validation`)
- Bugs: `fix/description` (e.g., `fix/logger-flush`)
- Brain work: `brain/description` (e.g., `brain/pattern-detection`)
- Main branch: `main`

**Commit message format**:

```
type: description

Examples:
- feat: add user authentication workflow
- fix: resolve ExecutionLogger buffer not flushing
- test: add tests for SQLiteClient query builder
- docs: update CLAUDE.md with new patterns
- refactor: simplify query builder interface
```

**Before committing**:

- [ ] Run all tests: `pytest tests/ -v`
- [ ] Check coverage: `pytest tests/ --cov=lib` (target: 80%+)
- [ ] Update documentation if interfaces changed
- [ ] Verify .env not committed (check .gitignore)

---

## Common Commands

**Development**:

```shell
# Initialize database (run once or to reset)
python scripts/init_db.py

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=lib --cov-report=html

# Verify configuration
python -c "from config import *; print(f'Model: {ANTHROPIC_MODEL}')"
```

**Database**:

```shell
# Initialize/reset database (WARNING: LOSES ALL DATA)
python scripts/init_db.py

# Query database (SQLite CLI)
sqlite3 data/system.db "SELECT COUNT(*) FROM execution_logs;"

# Backup database
cp data/system.db data/system_backup_$(date +%Y%m%d).db

# View schema
sqlite3 data/system.db ".schema"

# View recent executions
sqlite3 data/system.db "SELECT id, workflow_id, status FROM executions ORDER BY started_at DESC LIMIT 10;"
```

**Testing**:

```shell
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_sqlite_client.py -v

# Run specific test function
pytest tests/test_sqlite_client.py::test_insert_and_query -v

# Generate coverage report
pytest tests/ --cov=lib --cov-report=html

# View coverage report (open in browser)
# HTML report will be in htmlcov/index.html
```

---

## The WHY (Important Context)

### Why ExecutionLogger must use try/finally with flush()

**We require this because**:

- Logs are buffered in memory for performance (batched writes to database)
- Small Brain depends on complete execution logs to detect patterns
- Without flush(), buffer is lost on exceptions
- Lost logs = blind spots in learning system

**What happens without it**:

- ❌ Partial logs written (only successful phases logged)
- ❌ Brain analyzes incomplete data, proposes incorrect changes
- ❌ Pattern detection fails (can't see failure patterns)
- ❌ System appears to work but never improves

**Example**:

```python
# CORRECT: Guaranteed flush even on exception
try:
    logger = ExecutionLogger(exec_id, workflow_id, db)
    logger.phase_start("Critical Phase")
    risky_operation()  # might raise exception
    logger.phase_end("Critical Phase", success=True)
finally:
    logger.flush()  # ALWAYS executes
```

### Why all tools/validators must extend base classes

**We require this because**:

- Standardized return format enables Brain to analyze ANY tool
- `get_name()` method used for grouping in analytics
- Consistent interfaces allow Orchestrator to treat all tools uniformly
- Future Brain features depend on this contract

**What happens without it**:

- ❌ Brain can't parse tool results (expects specific dict structure)
- ❌ Analytics queries break (no tool_name field)
- ❌ Workflow orchestration fails (inconsistent error handling)
- ❌ Can't generate proposals (no metadata to analyze)

### Why SQLiteClient instead of raw sqlite3

**We require this because**:

- Development uses SQLite, production uses Supabase
- Query builder API is identical for both
- Code written with SQLiteClient works unchanged in production
- Chainable methods prevent SQL injection

**What happens without it**:

- ❌ Different code for dev vs prod (maintenance nightmare)
- ❌ SQL injection vulnerabilities
- ❌ Manual query building is error-prone
- ❌ Can't swap databases without rewriting queries

---

## Boundaries & Constraints

### Never Access Directly

- Database → Use `SQLiteClient` query builder (via `get_client()`)
- Environment variables → Import from `config.py`
- Claude API → Use `call_llm()` from `llm_client.py`

### Avoid These Patterns

**Raw SQL queries**:

```python
# ❌ WRONG
import sqlite3
cursor.execute("SELECT * FROM executions WHERE id = ?", (exec_id,))

# ✅ RIGHT
from lib.common_tools.sqlite_client import get_client
db = get_client()
results = db.table('executions').select('*').eq('id', exec_id).execute()
```

**Skipping validation logging**:

```python
# ❌ WRONG
if not validator.validate(data)['passed']:
    retry()

# ✅ RIGHT
result = validator.validate(data)
logger.validation_event(validator.get_name(), result['passed'], result['issues'])
if not result['passed']:
    retry()
```

**Hardcoding configuration**:

```python
# ❌ WRONG
TIMEOUT = 120
API_KEY = "sk-ant-xxx"

# ✅ RIGHT
from config import DEFAULT_TIMEOUT_SECONDS, ANTHROPIC_API_KEY
```

### Required Patterns

**All Tools MUST**:

1. Extend `BaseTool`
2. Implement `execute(**kwargs)` returning standard dict
3. Include `get_name()` (inherited from BaseTool)
4. Never raise exceptions (return error in dict instead)

**Example**:

```python
from lib.orchestrator.base_tool import BaseTool

class MyTool(BaseTool):
    def execute(self, **kwargs) -> dict:
        try:
            result = self.do_work(**kwargs)
            return {
                'success': True,
                'data': result,
                'error': None,
                'tool_name': self.get_name(),
                'metadata': {}
            }
        except Exception as e:
            return {
                'success': False,
                'data': None,
                'error': str(e),
                'tool_name': self.get_name(),
                'metadata': {'exception_type': type(e).__name__}
            }
```

**All Validators MUST**:

1. Extend `BaseValidator`
2. Implement `validate(data, context)` returning standard dict
3. Include `get_name()` (inherited from BaseValidator)
4. Return `passed`, `issues`, `needs_more`, `validator_name`, `metadata`

**Example**:

```python
from lib.orchestrator.base_validator import BaseValidator

class MyValidator(BaseValidator):
    def validate(self, data, context=None):
        passed = len(data) > 10  # Example validation
        return {
            'passed': passed,
            'issues': [] if passed else ['Data too short'],
            'needs_more': not passed,
            'validator_name': self.get_name(),
            'metadata': {'length': len(data)}
        }
```

**All Workflows MUST**:

1. Use `ExecutionLogger` with try/finally
2. Log `phase_start`, `phase_end`, `tool_call`, `tool_result`, `validation_event`
3. Store execution record in `executions` table
4. Update workflow statistics after completion

---

## Reference Files

### Documentation

- `c:\Users\andyn\OneDrive\Desktop\NEW AI PROJECT\SYSTEM_ARCHITECTURE.md` → Complete architecture specification (35KB) - definitive reference for database schema, Brain mechanisms, and system design
- `c:\Users\andyn\OneDrive\Desktop\NEW AI PROJECT\CLAUDE.md` → This file (AI assistant guide)
- `c:\Users\andyn\OneDrive\Desktop\NEW AI PROJECT\.env.example` → Environment variable template

### Code Examples

- `c:\Users\andyn\OneDrive\Desktop\NEW AI PROJECT\lib\orchestrator\execution_logger.py` → Reference implementation of buffered logging with try/finally pattern
- `c:\Users\andyn\OneDrive\Desktop\NEW AI PROJECT\lib\common_tools\sqlite_client.py` → Reference query builder pattern (Supabase-compatible)
- `c:\Users\andyn\OneDrive\Desktop\NEW AI PROJECT\lib\orchestrator\base_tool.py` → Reference ABC implementation for tools
- `c:\Users\andyn\OneDrive\Desktop\NEW AI PROJECT\lib\orchestrator\base_validator.py` → Reference ABC implementation for validators
- `c:\Users\andyn\OneDrive\Desktop\NEW AI PROJECT\tests\test_base_classes.py` → Reference test implementation

### Configuration Files

- `c:\Users\andyn\OneDrive\Desktop\NEW AI PROJECT\config.py` → All system configuration (API keys, thresholds, paths)
- `c:\Users\andyn\OneDrive\Desktop\NEW AI PROJECT\.env` → Local secrets (gitignored, not committed)
- `c:\Users\andyn\OneDrive\Desktop\NEW AI PROJECT\requirements.txt` → Python dependencies with versions

---

## Out of Scope

Claude should NOT:

- **Modify base classes** unless explicitly requested
  - Example: "Change BaseValidator interface"
  - Why: Breaks all existing workflows and validators

- **Add new dependencies** without approval
  - Example: "pip install new-library"
  - Why: Must maintain minimal dependency footprint, avoid bloat

- **Change database schema** without migration strategy
  - Example: "ALTER TABLE executions ADD COLUMN"
  - Why: Breaks existing data, requires careful migration planning

- **Auto-apply proposals** from Brain
  - Example: "Apply all pending proposals automatically"
  - Why: Human-in-the-loop is critical safety mechanism

- **Refactor working workflows** without explicit request
  - Example: "Improve code style in workflow files"
  - Why: If it works and logs properly, don't break it

### How Claude Should Behave Here

- **Prefer small, safe changes** over large refactors
- **Match existing code style** (snake_case, Base\* prefixes, etc.)
- **Ask before structural changes** (new directories, moving files)
- **Explain reasoning** when suggesting non-obvious changes
- **Run tests** before claiming code is complete
- **Always verify ExecutionLogger.flush()** is in finally blocks

---

## Emergency Procedures

### Database corruption (system.db unreadable)

**Problem**: SQLite database file corrupted, workflows can't execute

**Solution**:

```shell
# Stop all running workflows first

# Option 1: Restore from backup
cp data/system_backup_YYYYMMDD.db data/system.db

# Option 2: Reinitialize (WARNING: LOSES ALL DATA)
rm data/system.db
python scripts/init_db.py
```

**Prevention**: Regular backups, never interrupt sqlite3 writes, use proper transactions

### Missing ExecutionLogger.flush() causing lost logs

**Problem**: Workflow executes successfully but no logs appear in execution_logs table

**Solution**:

```python
# Find the workflow file
# Add try/finally if missing:

try:
    logger = ExecutionLogger(exec_id, workflow_id, db)
    # ... workflow code ...
finally:
    logger.flush()  # ADD THIS
```

**Prevention**: Use template pattern for all new workflows, code review checklist

### Import errors after adding new files

**Problem**: `ModuleNotFoundError: No module named 'lib.orchestrator'`

**Solution**:

```shell
# Ensure __init__.py exists in all directories
touch lib/__init__.py
touch lib/orchestrator/__init__.py
touch lib/common_tools/__init__.py
touch lib/brain/__init__.py

# Verify PYTHONPATH includes project root (if needed)
export PYTHONPATH="${PYTHONPATH}:c:\Users\andyn\OneDrive\Desktop\NEW AI PROJECT"
```

**Prevention**: Always create `__init__.py` when adding new directories

### Tests pass locally but fail in CI/CD

**Problem**: Hardcoded paths or missing environment variables

**Solution**:

```python
# Use relative imports and config.py
from config import DATABASE_PATH  # NOT hardcoded path

# In tests, use tmp_path fixture
@pytest.fixture
def db(tmp_path):
    return SQLiteClient(str(tmp_path / "test.db"))
```

**Prevention**: Never hardcode absolute paths, always use config.py or fixtures

---

## Quick Start for AI Assistants

1. **Read this file** (CLAUDE.md) - 10-15 minutes
2. **Check `c:\Users\andyn\OneDrive\Desktop\NEW AI PROJECT\SYSTEM_ARCHITECTURE.md`** for deep architecture context
3. **Always use ExecutionLogger with try/finally** when modifying workflows
4. **Never modify base classes** without explicit permission
5. **Run tests** (`pytest tests/ -v`) before claiming completion

**Most Common Mistakes**:

1. **Forgetting ExecutionLogger.flush() in finally block** → Lost logs, no learning
2. **Not extending BaseValidator/BaseTool** → Inconsistent interfaces, Brain can't analyze
3. **Hardcoding config values instead of importing from config.py** → Environment issues
4. **Using raw sqlite3 instead of SQLiteClient** → Breaks Supabase compatibility
5. **Not logging every tool_call/tool_result** → Incomplete data for pattern analysis
6. **Modifying critical files without understanding cascading effects** → System-wide breakage

---

*This file is the single source of truth for AI assistants working with this codebase. When in doubt, refer to this file first.*
