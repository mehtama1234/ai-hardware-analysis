"""Apply and verify the managed PostgreSQL state schema contract."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys

from deployment.managed_state_contract import MIGRATION_STATEMENTS, SCHEMA_VERSION, migration_plan

try:
    import psycopg2
except ImportError:  # pragma: no cover - exercised in minimal pilot images
    psycopg2 = None

TABLES = ("verification_projects", "verification_collateral", "verification_jobs", "verification_job_events")
INDEXES = ("verification_jobs_project_status_idx", "verification_events_job_created_idx")


def apply_migration(dsn: str) -> dict[str, object]:
    if psycopg2 is None:
        raise RuntimeError("psycopg2 is required for managed-state migration")
    plan = migration_plan(dsn)
    with psycopg2.connect(dsn) as connection:
        with connection.cursor() as cursor:
            for statement in MIGRATION_STATEMENTS:
                cursor.execute(statement)
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema=current_schema() AND table_name = ANY(%s)", (list(TABLES),))
            tables = sorted(row[0] for row in cursor.fetchall())
            cursor.execute("SELECT indexname FROM pg_indexes WHERE schemaname=current_schema() AND indexname = ANY(%s)", (list(INDEXES),))
            indexes = sorted(row[0] for row in cursor.fetchall())
    verified = tables == sorted(TABLES) and indexes == sorted(INDEXES)
    return {
        "schema_version": SCHEMA_VERSION,
        "dsn": plan["dsn"],
        "tables": tables,
        "indexes": indexes,
        "verified": verified,
        "migration_sha256": hashlib.sha256("\n".join(MIGRATION_STATEMENTS).encode()).hexdigest(),
        "claim_boundary": "Migration and schema verification only; application provider cutover and backup/restore evidence remain required.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dsn", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        result = migration_plan(args.dsn) if args.dry_run else apply_migration(args.dsn)
    except Exception as error:
        print(f"managed-state migration failed: {type(error).__name__}: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if args.dry_run or result["verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

