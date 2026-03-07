# Security Rules

## Credentials
- NEVER hardcode API keys, model names, file paths, or thresholds
- NEVER commit `.env` files, credential JSON files, or OAuth tokens
- NEVER log API keys or secrets in execution_logs metadata
- All secrets come from environment variables via `config.py`

## Protected Files
Do NOT modify or delete these files — they are system contracts:
- `lib/orchestrator/base_tool.py`
- `lib/orchestrator/base_validator.py`
- `lib/orchestrator/execution_logger.py`
- `lib/common_tools/sqlite_client.py`
- `scripts/init_db.py`
- `config.py`
- `data/system.db`

## Brain System
- NEVER auto-apply SmallBrain or BigBrain proposals
- Human-in-the-loop is required for all Brain-generated changes
