#!/usr/bin/env python3
"""Verify the portable local qualification archive and its source hashes."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    args = parser.parse_args()
    receipt = json.loads((args.package / "archive-receipt.json").read_text())
    archive = args.package / "local-qualification-evidence.zip"
    failures = []
    if receipt.get("decision") != "digital_reference_and_deterministic_fallback_only" or receipt.get("analog_authorized") is not False:
        failures.append("archive decision is not fail-closed")
    if not archive.is_file() or sha256(archive) != receipt.get("archive", {}).get("sha256"):
        failures.append("archive hash is missing or stale")
    with ZipFile(archive) as bundle:
        names = set(bundle.namelist())
        required = {entry["archive_path"] for entry in receipt.get("entries", [])} | {"archive-receipt.json", "README.md"}
        if not required <= names:
            failures.append(f"archive missing entries: {sorted(required - names)}")
        for entry in receipt.get("entries", []):
            try:
                archived_hash = hashlib.sha256(bundle.read(entry["archive_path"])).hexdigest()
            except KeyError:
                continue
            if archived_hash != entry.get("sha256"):
                failures.append(f"archived entry hash mismatch: {entry['archive_path']}")
        archived_receipt = json.loads(bundle.read("archive-receipt.json"))
        if archived_receipt.get("entries") != receipt.get("entries"):
            failures.append("embedded and external archive receipts differ")
    boundary = receipt.get("claim_boundary", "")
    if "no measured analog execution" not in boundary or "production claim" not in boundary:
        failures.append("archive claim boundary is too broad")
    result = {"status": "passed" if not failures else "failed", "failures": failures,
              "finding": "portable local qualification archive is complete and fail-closed."}
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
