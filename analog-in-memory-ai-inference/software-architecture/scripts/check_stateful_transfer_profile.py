#!/usr/bin/env python3
"""Verify the stateful transfer profile across both fixed workload splits."""

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
    report_path = args.run / "stateful_transfer_report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    manifest = json.loads((args.run / "manifest.json").read_text(encoding="utf-8"))
    failures = []
    for entry in manifest.get("files", []):
        path = Path(entry["path"])
        if not path.is_absolute():
            path = Path.cwd() / path
        if not path.is_file() or digest(path) != entry.get("sha256"):
            failures.append(f"manifest hash mismatch: {path}")
    results = report.get("results", {})
    if set(results) != {"affine_original", "affine_stress", "stateful_previous_token_original", "stateful_previous_token_stress"}:
        failures.append("stateful transfer split matrix is incomplete")
    if results.get("affine_original", {}).get("quality", {}).get("screen_pass") is not False:
        failures.append("affine original control unexpectedly passed")
    for name in ("stateful_previous_token_original", "stateful_previous_token_stress"):
        if results.get(name, {}).get("quality", {}).get("screen_pass") is not True:
            failures.append(f"stateful profile failed required split: {name}")
    if report.get("passing_results") != ["affine_stress", "stateful_previous_token_original", "stateful_previous_token_stress"]:
        failures.append("stateful passing set changed unexpectedly")
    if report.get("analog_authorized") is not False:
        failures.append("stateful transfer run authorized analog execution")
    result = {"status": "passed" if not failures else "failed", "failures": failures,
              "finding": "previous-token state correction is the first tested transfer profile to pass both original and disjoint stress splits.",
              "claim_boundary": report.get("claim_boundary")}
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
