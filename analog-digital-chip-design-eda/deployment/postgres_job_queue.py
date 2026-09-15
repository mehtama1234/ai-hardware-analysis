"""PostgreSQL durable queue implementation matching the pilot queue contract."""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
import json
from typing import Any

from deployment.managed_state_contract import MIGRATION_STATEMENTS

try:
    import psycopg2
    from psycopg2.extras import Json
except ImportError:  # pragma: no cover
    psycopg2 = None
    Json = None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class PostgresJobQueue:
    """A transactional queue for the managed-state migration boundary.

    The service does not select this class until all repositories share the
    managed database. Keeping it explicit prevents API/worker split-brain.
    """

    def __init__(self, dsn: str, *, migrate: bool = False):
        if psycopg2 is None:
            raise RuntimeError("psycopg2 is required for PostgreSQL queue")
        self.dsn = dsn
        if migrate:
            self.migrate()

    def _connect(self):
        return psycopg2.connect(self.dsn)

    def migrate(self) -> None:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                for statement in MIGRATION_STATEMENTS:
                    cursor.execute(statement)

    @staticmethod
    def _decode(row) -> dict[str, Any]:
        result = dict(row)
        payload = result.get("payload", {})
        result["payload"] = payload if isinstance(payload, dict) else json.loads(payload)
        return result

    def enqueue(self, job_id: str, *, project_id: str, kind: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        now = _now()
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO verification_jobs (id, project_id, kind, status, payload, created_at, updated_at) VALUES (%s, %s, %s, 'queued', %s, %s, %s)", (job_id, project_id, kind, Json(payload or {}), now, now))
        return self.get(job_id)

    def get(self, job_id: str) -> dict[str, Any]:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, project_id, kind, status, payload, created_at, updated_at FROM verification_jobs WHERE id=%s", (job_id,))
                row = cursor.fetchone()
                if row is None:
                    raise KeyError(job_id)
                columns = [item.name for item in cursor.description]
        return self._decode(dict(zip(columns, row)))

    def counts(self) -> dict[str, int]:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT status, COUNT(*) FROM verification_jobs GROUP BY status")
                return {row[0]: int(row[1]) for row in cursor.fetchall()}

    def claim(self) -> dict[str, Any] | None:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM verification_jobs WHERE status='queued' ORDER BY created_at, id FOR UPDATE SKIP LOCKED LIMIT 1")
                row = cursor.fetchone()
                if row is None:
                    return None
                cursor.execute("UPDATE verification_jobs SET status='running', updated_at=%s WHERE id=%s", (_now(), row[0]))
        return self.get(row[0])

    def requeue_stale(self, *, max_age_seconds: float = 900.0) -> int:
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=max_age_seconds)
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE verification_jobs SET status='queued', updated_at=%s WHERE status='running' AND updated_at < %s", (_now(), cutoff))
                return cursor.rowcount

    def start(self, job_id: str) -> dict[str, Any]:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE verification_jobs SET status='running', updated_at=%s WHERE id=%s AND status IN ('queued', 'failed')", (_now(), job_id))
        return self.get(job_id)

    def finish(self, job_id: str, *, status: str) -> dict[str, Any]:
        if status not in {"passed", "failed", "blocked", "cancelled"}:
            raise ValueError("invalid terminal status")
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE verification_jobs SET status=%s, updated_at=%s WHERE id=%s AND status='running'", (status, _now(), job_id))
        return self.get(job_id)

    def cancel(self, job_id: str) -> dict[str, Any]:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE verification_jobs SET status='cancelled', updated_at=%s WHERE id=%s AND status='queued'", (_now(), job_id))
        return self.get(job_id)

