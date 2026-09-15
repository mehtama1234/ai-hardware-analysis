#!/usr/bin/env python3
"""Verify cross-split affine versus quadratic transfer-model evidence."""

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
    report_path = args.run / "transfer_model_sweep_report.json"
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
    expected = {"affine_original", "affine_stress", "quadratic_original", "quadratic_stress"}
    if set(results) != expected:
        failures.append("transfer-model split matrix is incomplete")
    if results.get("affine_original", {}).get("quality", {}).get("screen_pass") is not False:
        failures.append("affine original split unexpectedly passed")
    if results.get("affine_stress", {}).get("quality", {}).get("screen_pass") is not True:
        failures.append("affine stress split unexpectedly failed")
    if results.get("quadratic_original", {}).get("quality", {}).get("screen_pass") is not True:
        failures.append("quadratic original split unexpectedly failed")
    if results.get("quadratic_stress", {}).get("quality", {}).get("screen_pass") is not False:
        failures.append("quadratic stress split unexpectedly passed")
    if report.get("analog_authorized") is not False or len(report.get("passing_results", [])) != 2:
        failures.append("transfer sweep authorization or passing-set boundary changed")
    if "no measured hardware" not in report.get("claim_boundary", ""):
        failures.append("transfer sweep claim boundary is incomplete")
    result = {"status": "passed" if not failures else "failed", "failures": failures,
              "finding": "affine and quadratic transfer models each pass only one split; no single calibrated transfer model generalizes across both.",
              "claim_boundary": report.get("claim_boundary")}
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
