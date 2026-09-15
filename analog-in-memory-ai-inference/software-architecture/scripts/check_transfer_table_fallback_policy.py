#!/usr/bin/env python3
"""Verify every missing transfer-table code is explicitly unsupported."""

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
    report = json.loads((args.package / "transfer_table_fallback_policy.json").read_text(encoding="utf-8"))
    manifest = json.loads((args.package / "manifest.json").read_text(encoding="utf-8"))
    failures = []
    for entry in manifest.get("files", []):
        path = Path(entry["path"])
        if not path.is_absolute():
            path = Path.cwd() / path
        if not path.is_file() or digest(path) != entry.get("sha256"):
            failures.append(f"manifest hash mismatch: {path}")
    if report.get("unsupported_codes") != [0, 2, 3, 4, 5, 6, 7, 9, 11, 12]:
        failures.append("unsupported code set changed")
    routes = report.get("routes", {})
    for code in report.get("unsupported_codes", []):
        if routes.get(str(code), {}).get("status") != "unsupported" or routes.get(str(code), {}).get("route") != "digital_fallback":
            failures.append(f"missing code {code} is not explicitly digital fallback")
    if any(route.get("route") != "digital_fallback" for route in routes.values()):
        failures.append("a code route bypasses digital fallback")
    if report.get("overall_route") != "digital_fallback" or report.get("analog_authorized") is not False:
        failures.append("overall fallback policy is unsafe")
    boundary = report.get("claim_boundary", "")
    if "incomplete circuit table" not in boundary or "analog workload" not in boundary:
        failures.append("claim boundary is too broad")
    print(json.dumps({"status": "passed" if not failures else "failed", "failures": failures,
                      "finding": "all 10 missing circuit codes are explicitly unsupported and every code routes to digital fallback.",
                      "claim_boundary": boundary}, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
