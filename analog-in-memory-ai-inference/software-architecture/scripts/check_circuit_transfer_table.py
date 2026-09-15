#!/usr/bin/env python3
"""Verify the partial circuit transfer table remains fail-closed."""

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
    report = json.loads((args.package / "circuit_transfer_table.json").read_text(encoding="utf-8"))
    manifest = json.loads((args.package / "manifest.json").read_text(encoding="utf-8"))
    failures = []
    for entry in manifest.get("files", []):
        path = Path(entry["path"])
        if not path.is_absolute():
            path = Path.cwd() / path
        if not path.is_file() or digest(path) != entry.get("sha256"):
            failures.append(f"manifest hash mismatch: {path}")
    if report.get("requested_code_count") != 16 or report.get("measured_code_count") != 6:
        failures.append("unexpected circuit table coverage")
    if report.get("complete_code_map") is not False or len(report.get("missing_codes", [])) != 10:
        failures.append("incomplete code map was not preserved")
    binding = report.get("adapter_binding", {})
    if binding.get("status") != "refused_incomplete_code_map" or binding.get("bound_to_workload") is not False:
        failures.append("partial circuit map was bound to workload")
    if report.get("analog_authorized") is not False:
        failures.append("partial circuit map authorized analog execution")
    boundary = report.get("claim_boundary", "")
    if "incomplete map" not in boundary or "analog authorization" not in boundary:
        failures.append("claim boundary is too broad")
    print(json.dumps({"status": "passed" if not failures else "failed", "failures": failures,
                      "finding": "only 6 of 16 circuit codes are locally available; workload binding is refused until the map is complete.",
                      "claim_boundary": boundary}, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
