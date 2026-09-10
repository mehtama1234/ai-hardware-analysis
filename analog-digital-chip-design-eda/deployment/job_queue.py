"""Small durable SQLite queue for verification jobs."""
from __future__ import annotations
from datetime import datetime, timezone, timedelta
import json, sqlite3
from pathlib import Path
from typing import Any

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

class DurableJobQueue:
    def __init__(self, database: str | Path):
        self.database = str(database)
        Path(self.database).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("PRAGMA synchronous=NORMAL")
            db.execute("PRAGMA busy_timeout=30000")
            db.execute("CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, project_id TEXT NOT NULL, kind TEXT NOT NULL, status TEXT NOT NULL, payload TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL)")

    def _connect(self):
        db = sqlite3.connect(self.database, timeout=30, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA busy_timeout=30000")
        return db

    def enqueue(self, job_id: str, *, project_id: str, kind: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        now = _now()
        with self._connect() as db:
            db.execute("INSERT INTO jobs VALUES (?, ?, ?, 'queued', ?, ?, ?)", (job_id, project_id, kind, json.dumps(payload or {}, sort_keys=True), now, now))
        return self.get(job_id)

    def get(self, job_id: str) -> dict[str, Any]:
        with self._connect() as db:
            row = db.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        if row is None:
            raise KeyError(job_id)
        result = dict(row); result["payload"] = json.loads(result["payload"]); return result

    def counts(self) -> dict[str, int]:
        with self._connect() as db:
            rows = db.execute("SELECT status, COUNT(*) AS count FROM jobs GROUP BY status").fetchall()
        return {row["status"]: int(row["count"]) for row in rows}

    def claim(self) -> dict[str, Any] | None:
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT id FROM jobs WHERE status='queued' ORDER BY created_at LIMIT 1").fetchone()
            if row is None:
                db.execute("COMMIT"); return None
            now = _now(); db.execute("UPDATE jobs SET status='running', updated_at=? WHERE id=?", (now, row["id"])); db.execute("COMMIT")
        return self.get(row["id"])

    def requeue_stale(self, *, max_age_seconds: float = 900.0) -> int:
        """Return abandoned running jobs to the queue after a worker crash."""
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=max_age_seconds)
        with self._connect() as db:
            cursor = db.execute(
                "UPDATE jobs SET status='queued', updated_at=? "
                "WHERE status='running' AND updated_at < ?",
                (_now(), cutoff.isoformat()),
            )
            return cursor.rowcount

    def start(self, job_id: str) -> dict[str, Any]:
        with self._connect() as db:
            # A failed job may be explicitly retried by the API.
            db.execute("UPDATE jobs SET status='running', updated_at=? WHERE id=? AND status IN ('queued', 'failed')", (_now(), job_id))
        return self.get(job_id)

    def finish(self, job_id: str, *, status: str) -> dict[str, Any]:
        if status not in {"passed", "failed", "blocked", "cancelled"}:
            raise ValueError("invalid terminal status")
        with self._connect() as db:
            db.execute("UPDATE jobs SET status=?, updated_at=? WHERE id=? AND status='running'", (status, _now(), job_id))
        return self.get(job_id)

    def cancel(self, job_id: str) -> dict[str, Any]:
        with self._connect() as db:
            db.execute("UPDATE jobs SET status='cancelled', updated_at=? WHERE id=? AND status='queued'", (_now(), job_id))
        return self.get(job_id)
