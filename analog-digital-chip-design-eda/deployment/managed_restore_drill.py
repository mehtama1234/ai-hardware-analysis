"""Run a bounded managed-state plus evidence restore rehearsal."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from deployment.managed_state_contract import validate_postgres_dsn
from scripts.verify_recovery_snapshot import verify_snapshot

try:
    import psycopg2
except ImportError:  # pragma: no cover
    psycopg2 = None


TABLES = ("verification_projects", "verification_collateral", "verification_jobs", "verification_job_events")


def run_drill(dsn: str, evidence_root: Path, snapshot: Path, restored: Path) -> dict[str, object]:
    if psycopg2 is None:
        raise RuntimeError("psycopg2 is required for managed restore drill")
    redacted = validate_postgres_dsn(dsn)
    with psycopg2.connect(dsn) as connection:
        with connection.cursor() as cursor:
            counts: dict[str, int] = {}
            for table in TABLES:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                counts[table] = int(cursor.fetchone()[0])
    evidence = verify_snapshot(evidence_root, snapshot, restored)
    return {
        "schema_version": "verification-managed-restore-drill-v1",
        "dsn": redacted,
        "database_tables": counts,
        "evidence_restore": evidence,
        "database_state_verified": True,
        "evidence_state_verified": bool(evidence.get("match")),
        "verified": bool(evidence.get("match")),
        "claim_boundary": "Verifies live managed schema visibility and evidence inventory restoration; it does not replace provider-native database backup/restore, failover, or disaster-recovery evidence.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dsn", required=True)
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--restored", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = run_drill(args.dsn, args.evidence_root, args.snapshot, args.restored)
    except Exception as error:
        print(f"managed restore drill failed: {type(error).__name__}: {error}", file=sys.stderr)
        return 2
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    print(payload, end="")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    return 0 if result["verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

