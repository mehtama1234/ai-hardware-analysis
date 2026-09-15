#!/usr/bin/env python3
"""Verify the profile-aware multi-module governor is fail-closed."""

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
    report_path = args.package / "profile_governor_report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    manifest = json.loads((args.package / "manifest.json").read_text(encoding="utf-8"))
    route_cost_path = args.package / "route_cost_trace.jsonl"
    failures = []
    for entry in manifest.get("files", []):
        path = Path(entry["path"])
        if not path.is_absolute():
            path = Path.cwd() / path
        if not path.is_file() or digest(path) != entry.get("sha256"):
            failures.append(f"manifest hash mismatch: {path}")
    if report.get("decision") != "full_digital_fallback":
        failures.append("governor did not select the required current full-digital policy")
    enforced = report.get("enforced_policy", {})
    if report.get("analog_authorized") is not False or enforced.get("route") != "digital_fallback":
        failures.append("governor exposed an unauthorized analog route")
    trace = report.get("trace", [])
    if len(trace) != 4 or any(row.get("command") != "RUN_DIGITAL_FALLBACK" for row in trace):
        failures.append("governor trace does not cover all four evaluation cases with fallback")
    if not any(not row.get("screen_pass") for row in report.get("candidate_routes", [])):
        failures.append("governor has no rejected route evidence")
    if report.get("recommended_policy", {}).get("analog_modules"):
        failures.append("governor recommended an analog route despite failed disjoint stress validation")
    if any(row.get("stress_screen_pass") for row in report.get("candidate_routes", [])):
        failures.append("governor found an unexpected stress-passing candidate")
    if report.get("quality_threshold", {}).get("maximum_final_logit_relative_l2") != 0.002:
        failures.append("final-logit propagation guard threshold is not pinned")
    if not route_cost_path.is_file():
        failures.append("governor route cost trace is missing")
    else:
        cost_rows = [json.loads(line) for line in route_cost_path.read_text(encoding="utf-8").splitlines() if line]
        if len(cost_rows) != 162 or any(row.get("enforced_route") != "digital_fallback" for row in cost_rows):
            failures.append("governor route cost trace does not cover 162 fallback vectors")
    if "no hardware latency" not in report.get("claim_boundary", ""):
        failures.append("governor claim boundary is incomplete")
    result = {"status": "passed" if not failures else "failed", "failures": failures,
              "finding": "isolated numerical candidates pass, but no authorized analog route exists; full digital fallback is enforced.",
              "claim_boundary": report.get("claim_boundary")}
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
