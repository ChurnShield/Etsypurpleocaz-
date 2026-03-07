# Testing Rules

## Running Tests
- Always run `pytest tests/ -v` before claiming any change is complete
- Tests must pass — do not commit code with failing tests

## Writing Tests
- Test files live in `/tests/` and follow naming: `test_{module_name}.py`
- Use `pytest` with standard assertions — no unittest.TestCase
- Mock external APIs (Etsy, Gemini, Google Sheets) — never hit real endpoints
- Mock database access using in-memory SQLite when testing DB-dependent code

## Coverage
- Every new tool must have a corresponding test file
- Every new validator must have a corresponding test file
- Test both success and error paths (tools must return error dicts, not raise)

## Test Structure
- Use `describe`-style grouping with nested classes or clear function naming
- Fixtures go in `conftest.py` when shared across test files
- Keep test data inline unless it exceeds 20 lines — then use fixtures
