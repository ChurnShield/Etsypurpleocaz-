# Database Rules

## Access Patterns
- ALL database access must go through `SQLiteClient` from `lib/common_tools/sqlite_client.py`
- NEVER use raw `sqlite3` — it breaks Supabase compatibility
- Use the chainable API: `.table().select().eq().execute()`

## Schema
- NEVER modify `scripts/init_db.py` without a migration strategy
- NEVER directly modify `data/system.db` — corruption is unrecoverable
- Schema changes require explicit permission and a rollback plan

## Query Patterns
- Import `SQLiteClient` — never instantiate sqlite3 connections directly
- Use parameterized queries via the client — never string-interpolate SQL values
- Always handle empty result sets gracefully
