#!/usr/bin/env python3
"""Verify all-code fallback invariants are bound to the transformer schedule."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    args = parser.parse_args()
    report = json.loads((args.package / "transformer_transfer_table_runtime_trace.json").read_text(encoding="utf-8"))
    manifest = json.loads((args.package / "manifest.json").read_text(encoding="utf-8"))
    failures = []
    for entry in manifest.get("files", []):
        path = Path(entry["path"])
        if not path.is_absolute():
            path = Path.cwd() / path
        if not path.is_file() or digest(path) != entry.get("sha256"):
            failures.append(f"manifest hash mismatch: {path}")
    events = report.get("events", [])
    if len(events) != 162 or report.get("workload_vectors") != 162:
        failures.append("transformer trace does not cover 162 workload vectors")
    if len(report.get("target_modules", [])) != 3:
        failures.append("transformer trace does not cover three modules")
    expected = [0, 2, 3, 4, 5, 6, 7, 9, 11, 12]
    if (report.get("all_routes_fallback") is not True
            or report.get("all_unsupported_codes_explicit") is not True
            or report.get("analog_instruction_count") != 0
            or any(event.get("unsupported_codes") != expected for event in events)
            or any(event.get("actual_route") != "digital_fallback" for event in events)):
        failures.append("transformer schedule contains an unsafe or incomplete fallback binding")
    boundary = report.get("claim_boundary", "")
    if "Local transformer compiler/runtime" not in boundary or "not claim physical analog execution" not in boundary:
        failures.append("claim boundary is too broad")
    print(json.dumps({"status": "passed" if not failures else "failed", "failures": failures,
                      "finding": "all 162 transformer vectors inherit explicit all-code converter fallback; unsupported codes cannot enter analog execution.",
                      "claim_boundary": boundary}, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
