#!/usr/bin/env python3
"""Verify coverage-aware governance remains fail-closed."""

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
    report = json.loads((args.package / "coverage_aware_profile_governor.json").read_text(encoding="utf-8"))
    manifest = json.loads((args.package / "manifest.json").read_text(encoding="utf-8"))
    failures = []
    for entry in manifest.get("files", []):
        path = Path(entry["path"])
        if not path.is_absolute():
            path = Path.cwd() / path
        if not path.is_file() or digest(path) != entry.get("sha256"):
            failures.append(f"manifest hash mismatch: {path}")
    if not report.get("coverage_gate", {}).get("out_of_envelope"):
        failures.append("coverage-aware governor did not retain an out-of-envelope finding")
    if report.get("coverage_gate", {}).get("pass") is not False:
        failures.append("coverage gate unexpectedly passed")
    policy = report.get("enforced_policy", {})
    if (report.get("decision") != "coverage_out_of_envelope_full_digital_fallback"
            or policy.get("route") != "digital_fallback"
            or policy.get("analog_authorized") is not False
            or report.get("analog_authorized") is not False):
        failures.append("coverage-aware governor is not fail-closed")
    trace_path = args.package / "coverage_aware_route_cost_trace.jsonl"
    rows = [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines() if line]
    if len(rows) != 162 or any(row.get("enforced_route") != "digital_fallback" for row in rows):
        failures.append("coverage-aware route trace does not cover 162 digital fallback vectors")
    boundary = report.get("claim_boundary", "")
    if "Local CPU" not in boundary or "analog authorization" not in boundary:
        failures.append("coverage-aware claim boundary is too broad")
    print(json.dumps({"status": "passed" if not failures else "failed", "failures": failures,
                      "finding": "held-out activation coverage is outside calibration for at least one module/context, so digital fallback is enforced.",
                      "claim_boundary": boundary}, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
