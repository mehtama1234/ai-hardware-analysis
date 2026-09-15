#!/usr/bin/env python3
"""Verify the stateful numerical candidate and enforced fallback route."""

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
    report = json.loads((args.package / "stateful_profile_governor.json").read_text(encoding="utf-8"))
    manifest = json.loads((args.package / "manifest.json").read_text(encoding="utf-8"))
    failures = []
    for entry in manifest.get("files", []):
        path = Path(entry["path"])
        if not path.is_absolute():
            path = Path.cwd() / path
        if not path.is_file() or digest(path) != entry.get("sha256"):
            failures.append(f"manifest hash mismatch: {path}")
    candidate = report.get("numerical_candidate", {})
    if candidate.get("original_screen_pass") is not True or candidate.get("stress_screen_pass") is not True:
        failures.append("stateful candidate does not pass both workload splits")
    enforced = report.get("enforced_policy", {})
    if report.get("decision") != "stateful_profile_numerically_qualified_but_digital_fallback_enforced":
        failures.append("unexpected stateful governor decision")
    if enforced.get("route") != "digital_fallback" or enforced.get("analog_authorized") is not False:
        failures.append("stateful governor is not fail-closed")
    trace_path = args.package / "stateful_route_cost_trace.jsonl"
    rows = [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines() if line]
    if len(rows) != 162 or any(row.get("enforced_route") != "digital_fallback" for row in rows):
        failures.append("stateful route trace does not cover 162 fallback vectors")
    result = {"status": "passed" if not failures else "failed", "failures": failures,
              "finding": "stateful profile passes both fixed workload splits numerically; authorization remains closed and fallback is enforced.",
              "claim_boundary": report.get("claim_boundary")}
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
