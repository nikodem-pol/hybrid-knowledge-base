import sqlite3
from typing import Any, Dict, List, Optional
from .base import BaseDBAdapter


class SQLiteAdapter(BaseDBAdapter):
    """
    SQLite adapter implementing BaseDBAdapter.
    
    Config example:
    {
        "database": "path/to/database.db"
    }
    """

    def __init__(self):
        self.conn: Optional[sqlite3.Connection] = None

    def connect(self, config: Dict[str, Any]) -> None:
        database = config.get("database")
        if not database:
            raise ValueError("SQLite config must include 'database' path")

        self.conn = sqlite3.connect(database)
        self.conn.row_factory = sqlite3.Row  # Enables dict-like row access

    def query(
        self,
        query: str,
        params: Optional[tuple] = None
    ) -> List[Dict[str, Any]]:
        if not self.conn:
            raise RuntimeError("Database not connected")

        cursor = self.conn.cursor()
        cursor.execute(query, params or ())
        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    def execute(
        self,
        query: str,
        params: Optional[tuple] = None
    ) -> int:
        """
        Use for INSERT/UPDATE/DELETE.
        Returns number of affected rows.
        """
        if not self.conn:
            raise RuntimeError("Database not connected")

        cursor = self.conn.cursor()
        cursor.execute(query, params or ())
        self.conn.commit()
        return cursor.rowcount

    def get_schema(self):
        schema = {}
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT name 
            FROM sqlite_master 
            WHERE type='table' 
            AND name NOT LIKE 'sqlite_%';
        """)
        tables = cursor.fetchall()
        print(tables)

        for (table_name,) in tables:
            cursor.execute(f"PRAGMA table_info('{table_name}')")
            columns_info = cursor.fetchall()
            columns = [col[1] for col in columns_info]  # column name is index 1
            schema[table_name] = columns

        return schema
    
    def get_schema_with_types(self):
        schema = {}
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            AND name NOT LIKE 'sqlite_%';
        """)
        tables = cursor.fetchall()

        for (table_name,) in tables:
            cursor.execute(f"PRAGMA table_info('{table_name}')")
            columns_info = cursor.fetchall()

            columns = []
            for col in columns_info:
                columns.append({
                    "name": col[1],   # column name
                    "type": col[2],   # data type
                })

            schema[table_name] = columns
        return schema

    def close(self) -> None:
        if self.conn:
            self.conn.close()
            self.conn = None

    # Optional: Context manager support
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.conn.rollback()
        self.close()