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
