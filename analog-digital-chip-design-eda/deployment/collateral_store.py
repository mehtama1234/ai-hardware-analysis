"""Content-addressed project collateral storage for the pilot service."""
from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import sqlite3
from pathlib import Path

MAX_CONTENT_BYTES = 1_000_000

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

class CollateralStore:
    def __init__(self, database: str | Path, root: str | Path):
        self.database = str(database)
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS collateral (id TEXT PRIMARY KEY, project_id TEXT NOT NULL, name TEXT NOT NULL, kind TEXT NOT NULL, version TEXT NOT NULL, sha256 TEXT NOT NULL, bytes INTEGER NOT NULL, path TEXT NOT NULL, created_at TEXT NOT NULL)")

    def _connect(self):
        db = sqlite3.connect(self.database, timeout=30)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA busy_timeout=30000")
        return db

    def add(self, project_id: str, name: str, kind: str, version: str, content: str) -> dict[str, object]:
        encoded = content.encode("utf-8")
        if len(encoded) > MAX_CONTENT_BYTES:
            raise ValueError("collateral exceeds 1 MB limit")
        digest = hashlib.sha256(encoded).hexdigest()
        artifact_id = f"{project_id}-{digest[:16]}"
        relative = Path("projects") / project_id / "collateral" / f"{digest}.txt"
        destination = self.root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not destination.exists():
            destination.write_bytes(encoded)
        record = {"id": artifact_id, "project_id": project_id, "name": name, "kind": kind, "version": version, "sha256": digest, "bytes": len(encoded), "path": str(relative), "created_at": _now()}
        with self._connect() as db:
            db.execute("INSERT OR IGNORE INTO collateral VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", tuple(record.values()))
            row = db.execute("SELECT * FROM collateral WHERE id=?", (artifact_id,)).fetchone()
        return dict(row)

    def list(self, project_id: str) -> list[dict[str, object]]:
        with self._connect() as db:
            rows = db.execute("SELECT * FROM collateral WHERE project_id=? ORDER BY created_at, id", (project_id,)).fetchall()
        return [dict(row) for row in rows]

    def get(self, artifact_id: str) -> dict[str, object]:
        with self._connect() as db:
            row = db.execute("SELECT * FROM collateral WHERE id=?", (artifact_id,)).fetchone()
        if row is None:
            raise KeyError(artifact_id)
        return dict(row)
