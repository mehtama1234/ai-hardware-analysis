#!/usr/bin/env python3
"""Independently verify the portable local model-to-chip qualification archive."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import BadZipFile, ZipFile


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    args = parser.parse_args()
    receipt_path = args.receipt.resolve()
    errors: list[str] = []
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "blocked", "errors": [str(exc)]}, sort_keys=True))
        return 1
    if receipt.get("schema_version") != "local-qualification-archive-v0.1":
        errors.append("unsupported archive receipt schema")
    if receipt.get("decision") != "digital_reference_and_deterministic_fallback_only":
        errors.append("archive decision is not fail-closed")
    if receipt.get("analog_authorized") is not False:
        errors.append("archive authorizes analog execution")
    archive_entry = receipt.get("archive", {})
    archive_path = receipt_path.parent / Path(archive_entry.get("path", "")).name
    if not archive_path.is_file():
        errors.append("archive file is missing")
    elif sha256_bytes(archive_path.read_bytes()) != archive_entry.get("sha256"):
        errors.append("archive digest mismatch")
    else:
        try:
            with ZipFile(archive_path) as archive:
                names = set(archive.namelist())
                inner = json.loads(archive.read("archive-receipt.json"))
                if inner.get("schema_version") != receipt.get("schema_version"):
                    errors.append("embedded receipt schema mismatch")
                for entry in receipt.get("entries", []):
                    name = entry.get("archive_path", "")
                    if not name or name not in names or name.startswith("/") or ".." in Path(name).parts:
                        errors.append(f"unsafe or missing archive entry: {name}")
                        continue
                    if sha256_bytes(archive.read(name)) != entry.get("sha256"):
                        errors.append(f"archive entry digest mismatch: {name}")
                required = {"qualification-package.json", "counterfactual-advantage.json", "end-to-end-manifest.json", "qualification-handoff.md", "model-to-chip-goal.md"}
                if not required.issubset(names):
                    errors.append("portable archive is missing required model-to-chip documents")
        except (BadZipFile, KeyError, json.JSONDecodeError) as exc:
            errors.append(f"invalid portable archive: {exc}")
    if "no measured analog execution" not in receipt.get("claim_boundary", "").lower():
        errors.append("claim boundary is missing measured-analog limit")
    result = {"schema_version": "local-qualification-archive-check-v1", "status": "passed" if not errors else "blocked", "receipt": str(receipt_path), "entries": len(receipt.get("entries", [])), "errors": sorted(set(errors))}
    result["check_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    print(json.dumps(result, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
