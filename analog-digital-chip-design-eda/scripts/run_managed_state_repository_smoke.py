#!/usr/bin/env python3
"""Exercise the managed project/collateral/queue repositories against PostgreSQL."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from deployment.postgres_job_queue import PostgresJobQueue
from deployment.postgres_project_store import PostgresCollateralStore, PostgresProjectStore


def run(dsn: str, output: Path) -> dict[str, object]:
    suffix = uuid.uuid4().hex[:12]
    project_id = f"managed-smoke-{suffix}"
    job_id = f"managed-job-{suffix}"
    collateral_root = output.parent / f"managed-collateral-{suffix}"
    projects = PostgresProjectStore(dsn, migrate=True)
    queue = PostgresJobQueue(dsn, migrate=True)
    collateral = PostgresCollateralStore(dsn, collateral_root, migrate=True)
    project = projects.create(project_id, "Managed repository smoke")
    artifact = collateral.add(project_id, "smoke.sv", "rtl", "smoke-v1", "module smoke; endmodule\n")
    queued = queue.enqueue(job_id, project_id=project_id, kind="project-compile", payload={"artifact_id": artifact["id"]})
    claimed = queue.claim()
    finished = queue.finish(job_id, status="passed")
    counts = queue.counts()
    checks = {
        "project_round_trip": project["id"] == project_id and projects.get(project_id)["name"] == "Managed repository smoke",
        "collateral_round_trip": artifact["project_id"] == project_id and collateral.get(str(artifact["id"]))["sha256"] == artifact["sha256"],
        "queue_enqueue": queued["status"] == "queued",
        "queue_claim": bool(claimed) and claimed["id"] == job_id and claimed["status"] == "running",
        "queue_finish": finished["status"] == "passed",
    }
    verified = all(checks.values())
    # Clean only this rehearsal's rows; the migration and unrelated customer rows remain untouched.
    import psycopg2
    with psycopg2.connect(dsn) as connection, connection.cursor() as cursor:
        cursor.execute("DELETE FROM verification_jobs WHERE id=%s", (job_id,))
        cursor.execute("DELETE FROM verification_collateral WHERE id=%s", (artifact["id"],))
        cursor.execute("DELETE FROM verification_projects WHERE id=%s", (project_id,))
    shutil.rmtree(collateral_root, ignore_errors=True)
    payload = {
        "schema_version": "verification-managed-state-repository-smoke-v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "backend": "postgresql",
        "checks": checks,
        "verified": verified,
        "source_revision": "managed-state-repository-smoke-v1",
        "evidence_sha256": hashlib.sha256(json.dumps(checks, sort_keys=True).encode()).hexdigest(),
        "claim_boundary": "Disposable PostgreSQL repository semantics only; this does not prove managed availability, HA, backup, credentials, network policy, or customer production readiness.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dsn")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.dsn, args.output)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
