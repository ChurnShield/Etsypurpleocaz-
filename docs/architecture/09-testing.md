# Testing

**Version**: 1.0.0 | **Date**: 2026-02-25 | **Status**: 🚧 In Progress

> **Note**: This covers the testing approach, test organization, and running tests.
> For project-wide rules and conventions, see [CLAUDE.md](../../CLAUDE.md).
>
> **Cross-references**:
> - Tool patterns: [docs/architecture/03-tool-patterns.md](03-tool-patterns.md)
> - Validator patterns: [docs/architecture/04-validator-patterns.md](04-validator-patterns.md)
> - Database: [docs/architecture/05-database.md](05-database.md)

## Table of Contents

1. [Overview](#overview)
2. [Testing Approach](#testing-approach)
3. [Test Organization](#test-organization)
4. [What to Test](#what-to-test)
5. [Running Tests](#running-tests)
6. [Test Patterns](#test-patterns)

## Overview

Tests use pytest and focus on core infrastructure (base classes, logger, database client). Workflow tools are not unit-tested (they call external APIs).

### What it does

- Verify BaseTool and BaseValidator contracts (return format, get_name())
- Verify ExecutionLogger buffering and flush behavior
- Verify SQLiteClient CRUD operations and query builder

### What it does NOT do

- Test workflow tools (they depend on Etsy API, Google Sheets, RSS feeds)
- Integration/end-to-end tests (no test harness for full workflow runs)
- Mock external services

## Testing Approach

Test-Driven Development (TDD) for core infrastructure. Each infrastructure class has a corresponding test file that verifies the contract.

## Test Organization

```
tests/
|-- __init__.py
|-- test_base_classes.py       Tests for BaseTool and BaseValidator contracts
|-- test_execution_logger.py   Tests for ExecutionLogger buffering and flush
+-- test_sqlite_client.py      Tests for SQLiteClient query builder
```

Tests mirror source structure: `test_<module>.py` tests `<module>.py`.

## What to Test

**Always test**:
- New base classes or infrastructure changes
- Return format compliance (5-key tool dict, 5-key validator dict)
- ExecutionLogger flush behavior
- SQLiteClient query builder operations

**Don't unit-test**:
- Workflow tools that call external APIs (test manually via run.py)
- Configuration loading (tested implicitly by running workflows)

## Running Tests

```shell
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_execution_logger.py -v

# Specific test function
pytest tests/test_sqlite_client.py::test_insert_and_query -v

# With coverage report
pytest tests/ --cov=lib --cov-report=html

# Coverage report location: htmlcov/index.html
```

## Test Patterns

### Testing BaseTool implementations

From `tests/test_base_classes.py`:

```python
from lib.orchestrator.base_tool import BaseTool

class MockTool(BaseTool):
    def execute(self, **kwargs):
        return {
            'success': True,
            'data': kwargs.get('input', 'default'),
            'error': None,
            'tool_name': self.get_name(),
            'metadata': {}
        }

def test_tool_execute():
    tool = MockTool()
    result = tool.execute(input="test_data")
    assert result['success'] is True
    assert result['data'] == 'test_data'
    assert result['tool_name'] == 'MockTool'
```

### Testing BaseValidator implementations

```python
from lib.orchestrator.base_validator import BaseValidator

class MockValidator(BaseValidator):
    def validate(self, data, context=None):
        passed = data is not None and len(str(data)) > 0
        return {
            'passed': passed,
            'issues': [] if passed else ['Empty data'],
            'needs_more': not passed,
            'validator_name': self.get_name(),
            'metadata': {}
        }

def test_validator_passes():
    v = MockValidator()
    result = v.validate("some data")
    assert result['passed'] is True
    assert result['issues'] == []
```

### Testing ExecutionLogger

```python
def test_flush_writes_to_db(tmp_path):
    db = SQLiteClient(str(tmp_path / "test.db"))
    # ... init tables ...
    logger = ExecutionLogger("exec-1", "test_wf", db)
    logger.phase_start("Phase 1")
    logger.phase_end("Phase 1", True)
    logger.flush()
    logs = db.table("execution_logs").select("*").execute()
    assert len(logs) == 2  # phase_start + phase_end
```

### Testing SQLiteClient

```python
def test_insert_and_query(tmp_path):
    db = SQLiteClient(str(tmp_path / "test.db"))
    # ... create table ...
    db.table("test").insert({"id": "1", "name": "foo"}).execute()
    rows = db.table("test").select("*").eq("id", "1").execute()
    assert len(rows) == 1
    assert rows[0]["name"] == "foo"
```
