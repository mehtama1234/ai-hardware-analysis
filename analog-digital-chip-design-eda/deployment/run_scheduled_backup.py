"""Run one policy-validated PostgreSQL backup and emit an immutable manifest."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import os
import sys

from deployment.backup_policy import compatibility_plan, load_backup_policy
from deployment.evidence_store import S3EvidenceStore
from deployment.postgres_backup_restore import backup_database


def run_scheduled_backup(dsn: str, output_dir: Path, *, dump_binary: str = "pg_dump", evidence_store=None, bucket: str | None = None) -> dict[str, object]:
    policy = load_backup_policy()
    compatibility = compatibility_plan(dsn, dump_binary=dump_binary)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_dir.mkdir(parents=True, exist_ok=True)
    backup = output_dir / f"verification-{stamp}.dump"
    result = backup_database(dsn, backup)
    if bucket:
        evidence_store = evidence_store or S3EvidenceStore(bucket)
        published = evidence_store.put(f"backups/{backup.name}", backup.read_bytes())
        result = {**result, "object_key": published.key, "object_sha256": published.sha256}
    manifest = {"schema_version": "verification-scheduled-backup-v1", "created_at": stamp, "backup": result, "compatibility": compatibility, "policy": policy.__dict__, "claim_boundary": "One policy-validated backup execution; retention, replication, restore, and failover operations remain deployment responsibilities."}
    temporary = output_dir / f"{backup.name}.manifest.tmp"
    manifest_path = output_dir / f"{backup.name}.manifest.json"
    temporary.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(manifest_path)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dsn", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dump-binary", default="pg_dump")
    parser.add_argument("--bucket", default=os.environ.get("VERIFICATION_EVIDENCE_STORE_BUCKET"))
    args = parser.parse_args()
    try:
        result = run_scheduled_backup(args.dsn, args.output_dir, dump_binary=args.dump_binary, bucket=args.bucket)
    except Exception as error:
        print(f"scheduled backup failed: {type(error).__name__}: {error}", file=sys.stderr)
        return 2
    print(json.dumps({"backup": result["backup"]["backup"], "manifest": str(args.output_dir / (Path(result["backup"]["backup"]).name + ".manifest.json")), "sha256": result["backup"]["sha256"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
