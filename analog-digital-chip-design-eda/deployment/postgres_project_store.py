"""PostgreSQL project and collateral repositories for managed state."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
from pathlib import Path

from deployment.collateral_store import MAX_CONTENT_BYTES
from deployment.managed_state_contract import MIGRATION_STATEMENTS

try:
    import psycopg2
except ImportError:  # pragma: no cover
    psycopg2 = None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class _PostgresBase:
    def __init__(self, dsn: str, *, migrate: bool = False):
        if psycopg2 is None:
            raise RuntimeError("psycopg2 is required for PostgreSQL repositories")
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


class PostgresProjectStore(_PostgresBase):
    def ensure(self, project_id: str, name: str | None = None) -> dict[str, str]:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO verification_projects (id, name, created_at) VALUES (%s, %s, %s) ON CONFLICT (id) DO NOTHING", (project_id, name or project_id, _now()))
        return self.get(project_id)

    def create(self, project_id: str, name: str) -> dict[str, str]:
        try:
            with self._connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("INSERT INTO verification_projects (id, name, created_at) VALUES (%s, %s, %s)", (project_id, name, _now()))
        except Exception as error:
            if psycopg2 is not None and isinstance(error, psycopg2.errors.UniqueViolation):
                raise ValueError("project already exists") from error
            raise
        return self.get(project_id)

    def get(self, project_id: str) -> dict[str, str]:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, name, created_at FROM verification_projects WHERE id=%s", (project_id,))
                row = cursor.fetchone()
                if row is None:
                    raise KeyError(project_id)
                return dict(zip(("id", "name", "created_at"), row))

    def list(self) -> list[dict[str, str]]:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, name, created_at FROM verification_projects ORDER BY created_at, id")
                return [dict(zip(("id", "name", "created_at"), row)) for row in cursor.fetchall()]


class PostgresCollateralStore(_PostgresBase):
    def __init__(self, dsn: str, root: str | Path, *, object_store=None, migrate: bool = False):
        super().__init__(dsn, migrate=migrate)
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.object_store = object_store

    @staticmethod
    def _decode(row) -> dict[str, object]:
        result = dict(zip(("id", "project_id", "name", "kind", "version", "sha256", "bytes", "object_key", "created_at"), row))
        result["path"] = str(Path(str(result["object_key"])).relative_to("collateral"))
        return result

    def add(self, project_id: str, name: str, kind: str, version: str, content: str) -> dict[str, object]:
        encoded = content.encode("utf-8")
        if len(encoded) > MAX_CONTENT_BYTES:
            raise ValueError("collateral exceeds 1 MB limit")
        digest = hashlib.sha256(encoded).hexdigest()
        artifact_id = f"{project_id}-{digest[:16]}"
        relative = Path("projects") / project_id / "collateral" / f"{digest}.txt"
        destination = self.root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() and destination.read_bytes() != encoded:
            raise ValueError("immutable collateral object differs from existing content")
        object_key = f"collateral/{relative.as_posix()}"
        if self.object_store is not None:
            self.object_store.put(object_key, encoded)
        if not destination.exists():
            destination.write_bytes(encoded)
        values = (artifact_id, project_id, name, kind, version, digest, len(encoded), object_key, _now())
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO verification_collateral (id, project_id, name, kind, version, sha256, bytes, object_key, created_at) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING", values)
                cursor.execute("SELECT id, project_id, name, kind, version, sha256, bytes, object_key AS path, created_at FROM verification_collateral WHERE id=%s", (artifact_id,))
                row = cursor.fetchone()
        return self._decode(row)

    def list(self, project_id: str) -> list[dict[str, object]]:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, project_id, name, kind, version, sha256, bytes, object_key AS path, created_at FROM verification_collateral WHERE project_id=%s ORDER BY created_at, id", (project_id,))
                return [self._decode(row) for row in cursor.fetchall()]

    def get(self, artifact_id: str) -> dict[str, object]:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, project_id, name, kind, version, sha256, bytes, object_key AS path, created_at FROM verification_collateral WHERE id=%s", (artifact_id,))
                row = cursor.fetchone()
                if row is None:
                    raise KeyError(artifact_id)
                return self._decode(row)
