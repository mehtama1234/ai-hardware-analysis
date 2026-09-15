#!/usr/bin/env python3
"""Verify a public reference archive and its sidecar inventory."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tarfile


def verify(archive: Path, sidecar: Path | None = None) -> list[str]:
    sidecar = sidecar or archive.with_suffix(archive.suffix + ".json")
    errors: list[str] = []
    try:
        payload = json.loads(sidecar.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f"cannot read sidecar: {exc}"]
    expected = payload.get("archive_sha256")
    actual = hashlib.sha256(archive.read_bytes()).hexdigest() if archive.is_file() else None
    if actual != expected:
        errors.append("archive digest does not match sidecar")
    inventory = payload.get("files")
    if not isinstance(inventory, dict) or payload.get("file_count") != len(inventory):
        errors.append("archive inventory count is invalid")
        inventory = {}
    try:
        with tarfile.open(archive, "r:gz") as bundle:
            names = set(bundle.getnames())
    except (OSError, tarfile.TarError) as exc:
        return errors + [f"cannot read archive: {exc}"]
    for path in inventory:
        if f"public-reference/{path}" not in names:
            errors.append(f"inventory file missing from archive: {path}")
    forbidden = ("/runs/", "/__pycache__/", "/.artifacts/")
    if any(any(token in name for token in forbidden) for name in names):
        errors.append("archive contains excluded generated content")
    if "public-reference/archive-manifest.json" not in names:
        errors.append("archive-manifest.json is missing")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    parser.add_argument("--sidecar", type=Path)
    args = parser.parse_args()
    errors = verify(args.archive, args.sidecar)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"verified public reference archive: {args.archive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
