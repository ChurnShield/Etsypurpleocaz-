Check the health of the system by verifying critical components.

## Steps
1. Verify all `__init__.py` files exist in package directories
2. Verify `config.py` loads without errors: `python -c "import config"`
3. Verify database schema is intact: `python scripts/init_db.py` (dry-run if possible)
4. Run the test suite: `pytest tests/ -v`
5. Check for any hardcoded secrets or API keys in tracked files
6. Report system status: healthy, degraded, or broken
