from __future__ import annotations
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Iterable, Any
from config.settings import DB_PATH
from database.schema import SCHEMA_SQL

class Database:
    def __init__(self, path: Path | str = DB_PATH):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")

    def initialize(self) -> None:
        self.conn.executescript(SCHEMA_SQL)
        self.conn.commit()
        self.ensure_default_project()

    def ensure_default_project(self) -> int:
        row = self.fetchone("SELECT id FROM projects WHERE name = ?", ("Proyecto Principal",))
        if row:
            return int(row["id"])
        return self.execute(
            "INSERT INTO projects(name, description, created_at) VALUES(?,?,?)",
            ("Proyecto Principal", "Proyecto inicial", datetime.now().isoformat(timespec="seconds")),
        )

    def execute(self, sql: str, params: Iterable[Any] = ()) -> int:
        cur = self.conn.execute(sql, tuple(params))
        self.conn.commit()
        return int(cur.lastrowid)

    def executemany(self, sql: str, seq: Iterable[Iterable[Any]]) -> None:
        self.conn.executemany(sql, seq)
        self.conn.commit()

    def fetchone(self, sql: str, params: Iterable[Any] = ()): 
        return self.conn.execute(sql, tuple(params)).fetchone()

    def fetchall(self, sql: str, params: Iterable[Any] = ()): 
        return self.conn.execute(sql, tuple(params)).fetchall()

    def close(self) -> None:
        self.conn.close()
