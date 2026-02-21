# ChurnShield AI Coding Instructions

## Project Overview
ChurnShield is a SaaS platform for churn prevention with a 3-layer AI system:
- **Orchestrator**: Executes workflows mechanically using tools and validators
- **Small Brain**: Learns per-workflow patterns after 15+ executions
- **Big Brain**: Detects cross-workflow insights across all workflows

Backend: Python 3.10+ with SQLite (dev)/Supabase (prod), Claude API
Frontend: React/TypeScript with Vite, shadcn-ui, Tailwind, Supabase client

## Critical Patterns

### Backend Execution Logging
**Always use ExecutionLogger with try/finally** for workflow execution. Logs are buffered and must be flushed to enable AI learning.

```python
from lib.orchestrator.execution_logger import ExecutionLogger
from lib.common_tools.sqlite_client import get_client

try:
    db = get_client()
    logger = ExecutionLogger(exec_id, workflow_id, db)
    logger.phase_start("Data Collection")
    # ... workflow logic ...
    logger.phase_end("Data Collection", success=True)
finally:
    logger.flush()  # Critical: enables Small/Big Brain analysis
```

**Reference**: `lib/orchestrator/execution_logger.py`

### Tool & Validator Interfaces
**All tools must extend BaseTool**, return standardized dict format for AI analysis.

```python
from lib.orchestrator.base_tool import BaseTool

class MyTool(BaseTool):
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

**All validators must extend BaseValidator** with standardized validation response.

**Reference**: `lib/orchestrator/base_tool.py`, `lib/orchestrator/base_validator.py`

### Database Access
**Never use raw sqlite3** - use SQLiteClient query builder for Supabase compatibility.

```python
from lib.common_tools.sqlite_client import get_client

db = get_client()
results = db.table('executions') \
    .select('*') \
    .eq('workflow_id', workflow_id) \
    .order('started_at', desc=True) \
    .limit(10) \
    .execute()
```

**Reference**: `lib/common_tools/sqlite_client.py`

### Configuration Management
**Import all settings from config.py** - never hardcode values.

```python
from config import ANTHROPIC_API_KEY, DATABASE_PATH, MAX_RETRIES
```

**Reference**: `config.py`

## Frontend Patterns

### Component Structure
Use shadcn-ui components with Tailwind classes. Follow established patterns in `src/components/`.

### Data Fetching
Use React Query for server state management. Supabase client for database operations.

**Reference**: `src/hooks/`, `src/integrations/supabase/`

## Development Workflow

- **Backend**: Write tests first (pytest), target 80%+ coverage
- **Frontend**: Use TypeScript strictly, lazy load routes for performance
- **Database**: Run `python scripts/init_db.py` to initialize schema
- **Testing**: `pytest tests/ -v` for backend, `npm run lint` for frontend

## Key Files
- `SYSTEM_ARCHITECTURE.md`: Complete system design and learning mechanisms
- `CLAUDE.md`: Detailed AI assistant guidelines (read first)
- `workflows/`: Custom workflow implementations go here
- `keep-them-happy/src/pages/`: Frontend pages and routing
- `lib/brain/`: AI learning components (future development)

## Integration Points
- **Stripe**: Payment processing and webhook handling
- **Supabase**: Production database and real-time subscriptions
- **Claude API**: AI-powered workflow intelligence
- **Cancel Widget**: Customer-facing churn prevention interface

Avoid modifying base classes without permission. Focus on extending interfaces rather than changing contracts.