"""Durable project registry for the verification service."""
from __future__ import annotations
from datetime import datetime, timezone
import sqlite3
from pathlib import Path

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

class ProjectStore:
    def __init__(self, database: str | Path):
        self.database = str(database)
        Path(self.database).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS projects (id TEXT PRIMARY KEY, name TEXT NOT NULL, created_at TEXT NOT NULL)")

    def _connect(self):
        db = sqlite3.connect(self.database, timeout=30)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA busy_timeout=30000")
        return db

    def ensure(self, project_id: str, name: str | None = None) -> dict[str, str]:
        with self._connect() as db:
            db.execute("INSERT OR IGNORE INTO projects (id, name, created_at) VALUES (?, ?, ?)", (project_id, name or project_id, _now()))
        return self.get(project_id)

    def create(self, project_id: str, name: str) -> dict[str, str]:
        try:
            with self._connect() as db:
                db.execute("INSERT INTO projects (id, name, created_at) VALUES (?, ?, ?)", (project_id, name, _now()))
        except sqlite3.IntegrityError as error:
            raise ValueError("project already exists") from error
        return self.get(project_id)

    def get(self, project_id: str) -> dict[str, str]:
        with self._connect() as db:
            row = db.execute("SELECT id, name, created_at FROM projects WHERE id=?", (project_id,)).fetchone()
        if row is None:
            raise KeyError(project_id)
        return dict(row)

    def list(self) -> list[dict[str, str]]:
        with self._connect() as db:
            rows = db.execute("SELECT id, name, created_at FROM projects ORDER BY created_at, id").fetchall()
        return [dict(row) for row in rows]
