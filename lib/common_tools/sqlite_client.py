import sqlite3
import json
from typing import Any, Optional

_client = None


def get_client(db_path: str = None):
    """Get or create the database client singleton."""
    global _client
    if _client is None:
        from config import DATABASE_PATH
        _client = SQLiteClient(db_path or DATABASE_PATH)
    return _client


class SQLiteClient:
    """Supabase-compatible query builder for SQLite.

    Usage mirrors Supabase client:
        db.table('executions').select('*').eq('id', '123').execute()
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._reset()

    def _reset(self):
        self._table = None
        self._operation = None
        self._columns = "*"
        self._filters = []
        self._data = None
        self._order = ""
        self._limit = ""

    def table(self, table_name: str):
        self._reset()
        self._table = table_name
        return self

    def select(self, columns: str = "*"):
        self._operation = "SELECT"
        self._columns = columns
        return self

    def insert(self, data: dict):
        self._operation = "INSERT"
        self._data = data
        return self

    def update(self, data: dict):
        self._operation = "UPDATE"
        self._data = data
        return self

    def delete(self):
        self._operation = "DELETE"
        return self

    def eq(self, column: str, value: Any):
        self._filters.append((column, "=", value))
        return self

    def gt(self, column: str, value: Any):
        self._filters.append((column, ">", value))
        return self

    def gte(self, column: str, value: Any):
        self._filters.append((column, ">=", value))
        return self

    def lt(self, column: str, value: Any):
        self._filters.append((column, "<", value))
        return self

    def lte(self, column: str, value: Any):
        self._filters.append((column, "<=", value))
        return self

    def order(self, column: str, desc: bool = False):
        self._order = f"ORDER BY {column} {'DESC' if desc else 'ASC'}"
        return self

    def limit(self, count: int):
        self._limit = f"LIMIT {count}"
        return self

    def execute(self):
        cursor = self.conn.cursor()

        if self._operation == "SELECT":
            where = self._build_where()
            sql = f"SELECT {self._columns} FROM {self._table}{where}"
            sql = f"{sql} {self._order} {self._limit}".strip()
            values = [f[2] for f in self._filters]
            cursor.execute(sql, values)
            rows = cursor.fetchall()
            self._reset()
            return [dict(row) for row in rows]

        elif self._operation == "INSERT":
            cols = ", ".join(self._data.keys())
            placeholders = ", ".join(["?"] * len(self._data))
            sql = f"INSERT INTO {self._table} ({cols}) VALUES ({placeholders})"
            cursor.execute(sql, list(self._data.values()))
            self.conn.commit()
            self._reset()
            return [self._data]

        elif self._operation == "UPDATE":
            set_clause = ", ".join([f"{k} = ?" for k in self._data.keys()])
            where = self._build_where()
            sql = f"UPDATE {self._table} SET {set_clause}{where}"
            values = list(self._data.values()) + [f[2] for f in self._filters]
            cursor.execute(sql, values)
            self.conn.commit()
            self._reset()
            return []

        elif self._operation == "DELETE":
            where = self._build_where()
            sql = f"DELETE FROM {self._table}{where}"
            values = [f[2] for f in self._filters]
            cursor.execute(sql, values)
            self.conn.commit()
            self._reset()
            return []

    def _build_where(self) -> str:
        if not self._filters:
            return ""
        conditions = [f"{col} {op} ?" for col, op, val in self._filters]
        return " WHERE " + " AND ".join(conditions)
