"""Executable backup policy and PostgreSQL client compatibility checks."""
from __future__ import annotations

from dataclasses import dataclass
import os
import re
import subprocess

from deployment.managed_state_contract import validate_postgres_dsn


@dataclass(frozen=True)
class BackupPolicy:
    retention_days: int
    rpo_minutes: int
    rto_minutes: int
    schedule: str


def load_backup_policy() -> BackupPolicy:
    retention = os.environ.get("VERIFICATION_BACKUP_POLICY", "").strip().lower()
    match = re.fullmatch(r"daily-(\d+)d", retention)
    if not match or int(match.group(1)) < 7:
        raise ValueError("VERIFICATION_BACKUP_POLICY must be daily-Nd with N>=7")
    try:
        rpo, rto = int(os.environ["VERIFICATION_DR_RPO_MINUTES"]), int(os.environ["VERIFICATION_DR_RTO_MINUTES"])
    except (KeyError, ValueError) as error:
        raise ValueError("DR RPO/RTO must be integer minutes") from error
    if not 1 <= rpo <= 1440 or not 1 <= rto <= 1440:
        raise ValueError("DR RPO/RTO must be between 1 and 1440 minutes")
    schedule = os.environ.get("VERIFICATION_BACKUP_SCHEDULE", "0 * * * *").strip()
    if len(schedule.split()) != 5:
        raise ValueError("VERIFICATION_BACKUP_SCHEDULE must be a five-field cron expression")
    return BackupPolicy(int(match.group(1)), rpo, rto, schedule)


def client_major(binary: str = "pg_dump") -> int:
    output = subprocess.run([binary, "--version"], capture_output=True, text=True, check=False)
    if output.returncode != 0:
        raise RuntimeError(f"{binary} --version failed")
    match = re.search(r"(?:PostgreSQL|pg_dump)\)\s+(\d+)", output.stdout)
    if not match:
        raise ValueError(f"cannot parse {binary} version")
    return int(match.group(1))


def compatibility_plan(dsn: str, *, dump_binary: str = "pg_dump") -> dict[str, object]:
    validate_postgres_dsn(dsn)
    try:
        import psycopg2
    except ImportError as error:  # pragma: no cover
        raise RuntimeError("psycopg2 is required for compatibility checks") from error
    client = client_major(dump_binary)
    with psycopg2.connect(dsn) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SHOW server_version")
            server_text = str(cursor.fetchone()[0])
    server = int(server_text.split(".", 1)[0])
    if client != server:
        raise RuntimeError(f"PostgreSQL client/server major mismatch: client {client}, server {server}")
    policy = load_backup_policy()
    return {"client_major": client, "server_major": server, "compatible": True, "policy": policy.__dict__, "dsn": validate_postgres_dsn(dsn), "command": "pg_dump --format=custom with provider retention and encryption"}

