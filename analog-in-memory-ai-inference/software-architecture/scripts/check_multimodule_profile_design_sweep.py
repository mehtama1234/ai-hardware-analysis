#!/usr/bin/env python3
"""Verify the fixed-workload converter profile design sweep."""

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
    report_path = args.run / "profile_design_sweep_report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    manifest = json.loads((args.run / "manifest.json").read_text(encoding="utf-8"))
    failures = []
    for entry in manifest.get("files", []):
        path = Path(entry["path"])
        if not path.is_absolute():
            path = Path.cwd() / path
        if not path.is_file() or digest(path) != entry.get("sha256"):
            failures.append(f"manifest hash mismatch: {path}")
    if report.get("design_count") != 11 or len(report.get("designs", {})) != 11:
        failures.append("profile sweep does not contain 11 designs")
    if report.get("passing_designs") != ["weight16_dac16_adc14", "all16"]:
        failures.append("profile sweep passing set changed unexpectedly")
    for name in ("current_profile", "adc14", "adc16", "dac14_adc12", "dac16_adc12",
                 "adc12_range025", "adc12_range050", "adc12_range075", "adc12_range125"):
        if report["designs"][name]["quality"]["screen_pass"] is not False:
            failures.append(f"unexpected passing design: {name}")
    if report.get("analog_authorized") is not False:
        failures.append("profile sweep authorized analog execution")
    if "no measured hardware" not in report.get("claim_boundary", ""):
        failures.append("profile sweep claim boundary is incomplete")
    result = {"status": "passed" if not failures else "failed", "failures": failures,
              "finding": "weight16/DAC16/ADC14 and all16 pass the original three-module screen; the current profile and range-only changes do not.",
              "claim_boundary": report.get("claim_boundary")}
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
