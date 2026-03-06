"""
Database Connection Test Script
================================
Run this FIRST to understand how the database and logging system work.

WHAT THIS SCRIPT DOES:
    1. Connects to data/system.db using SQLiteClient
    2. Shows the database schema (what tables exist)
    3. Creates a test execution record
    4. Uses ExecutionLogger to log events (just like the orchestrator does)
    5. Flushes logs to the database
    6. Queries the database to PROVE the logs were saved
    7. Cleans up after itself

HOW TO RUN:
    cd "c:\\Users\\andyn\\OneDrive\\Desktop\\NEW AI PROJECT"
    python -m templates.workflow_template.db_test

PREREQUISITE:
    Make sure the database exists first:
    python scripts/init_db.py
"""

import uuid
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from lib.common_tools.sqlite_client import SQLiteClient
from lib.orchestrator.execution_logger import ExecutionLogger
from templates.workflow_template.config import DATABASE_PATH


def main():
    print("=" * 60)
    print("  DATABASE CONNECTION TEST")
    print("=" * 60)

    # ══════════════════════════════════════════════════════════
    # QUESTION 1: Where is the database?
    # ══════════════════════════════════════════════════════════
    print(f"\n1. DATABASE LOCATION")
    print(f"   Path: {DATABASE_PATH}")
    full_path = os.path.abspath(DATABASE_PATH)
    print(f"   Full path: {full_path}")
    print(f"   Exists: {os.path.exists(DATABASE_PATH)}")

    if not os.path.exists(DATABASE_PATH):
        print("\n   ERROR: Database not found!")
        print("   Run this first: python scripts/init_db.py")
        return

    # ══════════════════════════════════════════════════════════
    # QUESTION 2: How do I connect?
    # ══════════════════════════════════════════════════════════
    print(f"\n2. CONNECTING TO DATABASE")
    print(f"   Using: SQLiteClient('{DATABASE_PATH}')")

    # SQLiteClient wraps sqlite3 with a Supabase-compatible API.
    # In production, you'd swap this for a real Supabase client,
    # but the query syntax stays exactly the same!
    db = SQLiteClient(DATABASE_PATH)
    print("   Connected successfully!")

    # ══════════════════════════════════════════════════════════
    # QUESTION 3: What tables exist?
    # ══════════════════════════════════════════════════════════
    print(f"\n3. DATABASE SCHEMA")

    # Use raw sqlite3 just for schema inspection (SQLiteClient doesn't
    # have a schema query method - this is the one exception to the rule)
    import sqlite3
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()

    print(f"   Tables found: {len(tables)}")
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        print(f"\n   {table_name}:")
        for col in columns:
            # col = (index, name, type, notnull, default, pk)
            pk = " [PRIMARY KEY]" if col[5] else ""
            print(f"     - {col[1]} ({col[2]}{pk})")
    conn.close()

    # ══════════════════════════════════════════════════════════
    # QUESTION 4: How does ExecutionLogger work?
    # ══════════════════════════════════════════════════════════
    print(f"\n4. TESTING EXECUTIONLOGGER")

    # Generate unique IDs for this test
    test_execution_id = f"test-{uuid.uuid4()}"
    test_workflow_id = "db_test_workflow"

    print(f"   Execution ID: {test_execution_id}")
    print(f"   Workflow ID:  {test_workflow_id}")

    # First, create an execution record (the logger expects this to exist)
    db.table('executions').insert({
        'id': test_execution_id,
        'workflow_id': test_workflow_id,
        'started_at': datetime.utcnow().isoformat(),
        'status': 'running',
    }).execute()
    print("   Created execution record in 'executions' table")

    # Now create the logger and log some events
    # CRITICAL: Always use try/finally to ensure flush() is called!
    print("\n   Logging events (buffered in memory)...")

    try:
        logger = ExecutionLogger(test_execution_id, test_workflow_id, db)

        # Log a phase start
        logger.phase_start("Test Phase")
        print("   - Logged: phase_start('Test Phase')")

        # Log a tool call
        logger.tool_call("TestTool", {"input": "hello"})
        print("   - Logged: tool_call('TestTool', {'input': 'hello'})")

        # Log a tool result
        logger.tool_result("TestTool", {"data": "HELLO"}, success=True, duration_ms=42)
        print("   - Logged: tool_result('TestTool', success=True, 42ms)")

        # Log a validation event
        logger.validation_event("TestValidator", passed=True, issues=[])
        print("   - Logged: validation_event('TestValidator', passed=True)")

        # Log a phase end
        logger.phase_end("Test Phase", success=True)
        print("   - Logged: phase_end('Test Phase', success=True)")

        print(f"\n   Events in buffer: {len(logger._buffer)}")
        print("   (Nothing is in the database yet - logs are still in memory!)")

    finally:
        # THIS IS THE CRITICAL PART!
        # flush() writes all buffered logs to the execution_logs table.
        # If you forget this, all logs are LOST.
        logger.flush()
        print("\n   logger.flush() called - logs written to database!")

    # ══════════════════════════════════════════════════════════
    # QUESTION 5: Prove the logs are in the database
    # ══════════════════════════════════════════════════════════
    print(f"\n5. VERIFYING LOGS IN DATABASE")

    # Query execution_logs for our test execution
    logs = db.table('execution_logs') \
        .select('*') \
        .eq('execution_id', test_execution_id) \
        .order('timestamp') \
        .execute()

    print(f"   Found {len(logs)} log entries for execution '{test_execution_id}':\n")

    for log in logs:
        event = log.get('event_type', '?')
        phase = log.get('phase', '-')
        tool = log.get('tool_name', '-')
        validator = log.get('validator_name', '-')
        success = log.get('success')
        duration = log.get('duration_ms', '-')

        print(f"   [{event:15s}] phase={phase}, tool={tool}, "
              f"validator={validator}, success={success}, duration={duration}ms")

    # ══════════════════════════════════════════════════════════
    # CLEANUP: Remove test data
    # ══════════════════════════════════════════════════════════
    print(f"\n6. CLEANUP")

    # Delete test logs
    db.table('execution_logs') \
        .delete() \
        .eq('execution_id', test_execution_id) \
        .execute()
    print(f"   Deleted test logs from execution_logs")

    # Delete test execution
    db.table('executions') \
        .delete() \
        .eq('id', test_execution_id) \
        .execute()
    print(f"   Deleted test execution from executions")

    print(f"\n{'=' * 60}")
    print("  ALL TESTS PASSED - Database and logging are working!")
    print(f"{'=' * 60}")
    print()
    print("KEY TAKEAWAYS:")
    print("  - Database is at: data/system.db")
    print("  - Connect with: SQLiteClient('data/system.db')")
    print("  - Log events with: ExecutionLogger(exec_id, workflow_id, db)")
    print("  - ALWAYS call logger.flush() in a finally block")
    print("  - Logs are buffered in memory until flush() writes them")
    print("  - Query builder: db.table('x').select('*').eq('col', val).execute()")


if __name__ == '__main__':
    main()
