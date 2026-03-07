# Tool & Validator Conventions

## Tools
- ALL tools MUST extend `BaseTool` from `lib/orchestrator/base_tool.py`
- Tools MUST return: `{success: bool, data: Any, error: str|None, tool_name: str, metadata: dict}`
- Tools catch ALL exceptions internally and return error dicts — never raise
- Use `ExecutionLogger` with `try/finally` — call `logger.flush()` in the finally block
- NEVER skip `logger.flush()` — logs are lost and Brain goes blind

## Validators
- ALL validators MUST extend `BaseValidator` from `lib/orchestrator/base_validator.py`
- Validators MUST return: `{passed: bool, issues: list, needs_more: bool, validator_name: str, metadata: dict}`
- Same logging rules apply: `try/finally` with `logger.flush()`

## Security
- NEVER log API keys or secrets in execution_logs metadata
- Import ALL config values from `config.py` — never hardcode keys, paths, or thresholds
- NEVER auto-apply Brain proposals without human approval
