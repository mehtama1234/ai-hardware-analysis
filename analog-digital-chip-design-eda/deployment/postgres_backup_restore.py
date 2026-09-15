"""Credential-safe PostgreSQL backup and restore helper for deployment drills."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from urllib.parse import urlparse

from deployment.managed_state_contract import validate_postgres_dsn


def _command_args(dsn: str) -> tuple[list[str], dict[str, str]]:
    parsed = urlparse(dsn)
    validate_postgres_dsn(dsn)
    args = ["--host", parsed.hostname, "--port", str(parsed.port or 5432), "--username", parsed.username or "", "--dbname", parsed.path.lstrip("/")]
    env = os.environ.copy()
    if parsed.password is not None:
        env["PGPASSWORD"] = parsed.password
    return args, env


def backup_database(dsn: str, output: Path) -> dict[str, object]:
    if output.exists():
        raise ValueError("backup output already exists")
    output.parent.mkdir(parents=True, exist_ok=True)
    args, env = _command_args(dsn)
    completed = subprocess.run(["pg_dump", "--format=custom", "--file", str(output), *args], env=env, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"pg_dump failed: {completed.stderr[-500:]}")
    payload = output.read_bytes()
    return {"format": "pg_dump-custom", "backup": str(output), "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest(), "dsn": validate_postgres_dsn(dsn)}


def restore_database(dsn: str, backup: Path) -> dict[str, object]:
    if not backup.is_file():
        raise ValueError("backup file does not exist")
    args, env = _command_args(dsn)
    completed = subprocess.run(["pg_restore", "--clean", "--if-exists", "--no-owner", *args, str(backup)], env=env, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"pg_restore failed: {completed.stderr[-500:]}")
    payload = backup.read_bytes()
    return {"format": "pg_dump-custom", "backup": str(backup), "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest(), "dsn": validate_postgres_dsn(dsn), "restored": True}


def ensure_distinct_restore_target(source_dsn: str, restore_dsn: str) -> None:
    """Reject a restore target that resolves to the source database."""
    source = urlparse(validate_postgres_dsn(source_dsn))
    target = urlparse(validate_postgres_dsn(restore_dsn))
    source_identity = (source.hostname, source.port or 5432, source.path.lstrip("/"), source.username or "")
    target_identity = (target.hostname, target.port or 5432, target.path.lstrip("/"), target.username or "")
    if source_identity == target_identity:
        raise ValueError("restore target must be distinct from source database")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dsn", required=True)
    parser.add_argument("--backup", type=Path, required=True)
    parser.add_argument("--restore-dsn", type=str)
    args = parser.parse_args()
    try:
        result = backup_database(args.dsn, args.backup)
        if args.restore_dsn:
            ensure_distinct_restore_target(args.dsn, args.restore_dsn)
            result["restore"] = restore_database(args.restore_dsn, args.backup)
    except Exception as error:
        print(f"postgres backup/restore failed: {type(error).__name__}: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
