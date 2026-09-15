#!/usr/bin/env python3
"""Verify the stateful profile's third-holdout generalization boundary."""

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
    if len(report.get("results", {}).get("stateful_previous_token_original", {}).get("quality", {}).get("rows", [])) != 6:
        failures.append("third holdout does not contain six texts")
    for name in ("affine_original", "stateful_previous_token_original"):
        if report.get("results", {}).get(name, {}).get("quality", {}).get("screen_pass") is not False:
            failures.append(f"third holdout unexpectedly passed: {name}")
    if report.get("results", {}).get("stateful_previous_token_original", {}).get("quality", {}).get("teacher_forced_argmax_agreement") != 0.9753086419753086:
        failures.append("third-holdout stateful quality changed unexpectedly")
    if report.get("analog_authorized") is not False:
        failures.append("third holdout authorized analog execution")
    result = {"status": "passed" if not failures else "failed", "failures": failures,
              "finding": "stateful correction passes the original and prior stress split but fails the third holdout at 0.975309; generalization remains unproven.",
              "claim_boundary": report.get("claim_boundary")}
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
