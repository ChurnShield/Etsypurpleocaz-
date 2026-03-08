"""Migration 001: Add feedback tracking columns to proposals table.

Adds columns needed for the self-improvement feedback loop:
  - outcome:           'improved' / 'no_change' / 'worsened' / NULL
  - outcome_notes:     Human notes on what happened after applying
  - metric_before:     JSON snapshot of metrics before applying (e.g. failure rate)
  - metric_after:      JSON snapshot of metrics after applying
  - resolved_at:       When the proposal was resolved (approved/rejected/applied)
  - feedback_score:    -1 to +1 numeric score for learning (-1=harmful, +1=helpful)

Safe to run multiple times (uses IF NOT EXISTS pattern via column check).
"""

import os
import sys
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATABASE_PATH


def _column_exists(cursor, table, column):
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())


def migrate():
    db_path = DATABASE_PATH
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}. Run init_db.py first.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    new_columns = [
        ("outcome", "TEXT"),              # improved / no_change / worsened
        ("outcome_notes", "TEXT"),         # human notes
        ("metric_before", "TEXT"),         # JSON snapshot
        ("metric_after", "TEXT"),          # JSON snapshot
        ("resolved_at", "DATETIME"),       # when outcome was recorded
        ("feedback_score", "REAL"),        # -1.0 to +1.0
    ]

    added = 0
    for col_name, col_type in new_columns:
        if not _column_exists(cursor, "proposals", col_name):
            cursor.execute(
                f"ALTER TABLE proposals ADD COLUMN {col_name} {col_type}"
            )
            added += 1
            print(f"  Added: proposals.{col_name} ({col_type})")

    conn.commit()
    conn.close()

    if added:
        print(f"Migration complete: {added} column(s) added to proposals table.")
    else:
        print("Migration: All columns already exist. Nothing to do.")


if __name__ == "__main__":
    migrate()
