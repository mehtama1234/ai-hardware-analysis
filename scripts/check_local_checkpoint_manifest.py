#!/usr/bin/env python3
"""Verify a non-destructive local checkpoint manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(path: Path, root: Path) -> list[str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read checkpoint: {exc}"]
    errors: list[str] = []
    stored = payload.get("manifest_sha256")
    body = {key: value for key, value in payload.items() if key != "manifest_sha256"}
    actual = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if not isinstance(stored, str) or stored != actual:
        errors.append("checkpoint manifest digest is invalid")
    if payload.get("schema_version") != "local-checkpoint-manifest-v1":
        errors.append("unexpected checkpoint schema")
    if payload.get("non_destructive") is not True:
        errors.append("checkpoint is not marked non-destructive")
    artifacts = payload.get("artifacts") if isinstance(payload.get("artifacts"), dict) else {}
    for name, record in artifacts.items():
        if not isinstance(record, dict) or not isinstance(record.get("path"), str):
            errors.append(f"invalid artifact record: {name}")
            continue
        relative = Path(record["path"])
        candidate = (root / relative).resolve()
        if relative.is_absolute() or root.resolve() not in candidate.parents:
            errors.append(f"unsafe artifact path: {record['path']}")
        elif not candidate.is_file():
            errors.append(f"missing artifact: {record['path']}")
        elif candidate.is_file() and digest(candidate) != record.get("sha256"):
            errors.append(f"artifact digest mismatch: {record['path']}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkpoint", type=Path, nargs="?", default=ROOT / ".artifacts/local-checkpoints/20260912-local-unified-reference.json")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    errors = verify(args.checkpoint, args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"verified local checkpoint: {args.checkpoint}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
