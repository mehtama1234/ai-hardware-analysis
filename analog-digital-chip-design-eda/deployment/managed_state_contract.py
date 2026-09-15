"""PostgreSQL migration contract for the production state boundary.

This module intentionally does not claim to be a database driver. It defines
the schema and validates a managed DSN so a future provider implementation can
be tested against the same durable semantics as the SQLite pilot.
"""
from __future__ import annotations

import argparse
import json
from urllib.parse import urlparse, urlunparse

SCHEMA_VERSION = "verification-managed-state-v1"

MIGRATION_STATEMENTS: tuple[str, ...] = (
    "CREATE TABLE IF NOT EXISTS verification_projects (id TEXT PRIMARY KEY, name TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL)",
    "CREATE TABLE IF NOT EXISTS verification_collateral (id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES verification_projects(id), name TEXT NOT NULL, kind TEXT NOT NULL, version TEXT NOT NULL, sha256 CHAR(64) NOT NULL, bytes BIGINT NOT NULL, object_key TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL)",
    "CREATE TABLE IF NOT EXISTS verification_jobs (id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES verification_projects(id), kind TEXT NOT NULL, status TEXT NOT NULL, payload JSONB NOT NULL, created_at TIMESTAMPTZ NOT NULL, updated_at TIMESTAMPTZ NOT NULL)",
    "CREATE TABLE IF NOT EXISTS verification_job_events (id BIGSERIAL PRIMARY KEY, job_id TEXT NOT NULL REFERENCES verification_jobs(id), project_id TEXT NOT NULL REFERENCES verification_projects(id), event_type TEXT NOT NULL, request_id TEXT, status TEXT, created_at TIMESTAMPTZ NOT NULL, details JSONB NOT NULL)",
    "CREATE INDEX IF NOT EXISTS verification_jobs_project_status_idx ON verification_jobs(project_id, status, created_at)",
    "CREATE INDEX IF NOT EXISTS verification_events_job_created_idx ON verification_job_events(job_id, created_at, id)",
)


def validate_postgres_dsn(value: str) -> str:
    """Return a redacted normalized DSN or raise ValueError."""
    parsed = urlparse(str(value or ""))
    if parsed.scheme not in {"postgres", "postgresql"} or not parsed.hostname:
        raise ValueError("managed state DSN must use postgres:// or postgresql:// with a host")
    if not parsed.path or parsed.path == "/":
        raise ValueError("managed state DSN must name a database")
    redacted = parsed._replace(netloc=(parsed.hostname if not parsed.port else f"{parsed.hostname}:{parsed.port}"))
    return urlunparse(redacted)


def migration_plan(dsn: str) -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "dsn": validate_postgres_dsn(dsn),
        "statement_count": len(MIGRATION_STATEMENTS),
        "statements": list(MIGRATION_STATEMENTS),
        "claim_boundary": "Schema contract only; provider connection, migrations, backups, and restart/restore evidence remain required.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dsn", required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(migration_plan(args.dsn), indent=2))
    except ValueError as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

