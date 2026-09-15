#!/usr/bin/env python3
"""Verify disjoint stress validation preserves the negative generalization result."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    report_path = args.run / "stress_validation_report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    manifest = json.loads((args.run / "manifest.json").read_text(encoding="utf-8"))
    failures = []
    for entry in manifest.get("files", []):
        path = Path(entry["path"])
        if not path.is_absolute():
            path = Path.cwd() / path
        if not path.is_file() or digest(path) != entry.get("sha256"):
            failures.append(f"manifest hash mismatch: {path}")
    if len(report.get("evaluation_split", [])) != 6 or len(report.get("results", {})) != 4:
        failures.append("stress validation coverage is incomplete")
    if report.get("decision") != "numerical_recommendation_does_not_generalize_and_hardware_authorization_remains_closed":
        failures.append("stress validation did not preserve the negative generalization decision")
    if any(row.get("screen_pass") for row in report.get("results", {}).values()):
        failures.append("a stress route passed unexpectedly")
    recommended = report.get("recommended_route", {})
    if recommended.get("screen_pass") is not False:
        failures.append("recommended route was incorrectly accepted on stress inputs")
    if report.get("analog_authorized") is not False:
        failures.append("stress validation authorized analog execution")
    result = {"status": "passed" if not failures else "failed", "failures": failures,
              "finding": "the original attn-only numerical recommendation does not generalize to the disjoint six-text stress set",
              "claim_boundary": report.get("claim_boundary")}
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
