#!/usr/bin/env python3
"""Verify the redesigned profile on disjoint stress inputs."""

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
    if report.get("profile") != {"weight_bits": 16, "dac_bits": 16, "adc_bits": 14}:
        failures.append("stress receipt is not for the selected redesigned profile")
    if len(report.get("evaluation_split", [])) != 6:
        failures.append("redesigned-profile stress set is incomplete")
    if any(row.get("screen_pass") for row in report.get("results", {}).values()):
        failures.append("redesigned profile unexpectedly passed stress screening")
    full = report.get("results", {}).get("full_three_module", {}).get("quality", {})
    if full.get("teacher_forced_argmax_agreement") != 0.958904109589041:
        failures.append("full redesigned-profile stress result changed unexpectedly")
    if report.get("analog_authorized") is not False:
        failures.append("redesigned-profile stress run authorized analog execution")
    result = {"status": "passed" if not failures else "failed", "failures": failures,
              "finding": "weight16/DAC16/ADC14 improves stress quality but remains below the 0.99 screen; precision redesign alone is insufficient.",
              "claim_boundary": report.get("claim_boundary")}
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
