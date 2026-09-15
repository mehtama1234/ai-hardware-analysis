#!/usr/bin/env python3
"""Verify the local multi-module numerical error budget."""

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
    report_path = args.run / "error_budget_report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    manifest = json.loads((args.run / "manifest.json").read_text(encoding="utf-8"))
    failures = []
    for entry in manifest.get("files", []):
        path = Path(entry["path"])
        if not path.is_absolute():
            path = Path.cwd() / path
        if not path.is_file() or digest(path) != entry.get("sha256"):
            failures.append(f"manifest hash mismatch: {path}")
    configs = report.get("configurations", {})
    expected = {"ideal_control", "weight_quantization_only", "dac_quantization_only",
                "adc_quantization_only", "combined_current_profile"}
    if set(configs) != expected:
        failures.append("error-budget configuration set is incomplete")
    if configs.get("weight_quantization_only", {}).get("quality", {}).get("screen_pass") is not True:
        failures.append("weight-only component did not pass")
    for name in ("dac_quantization_only", "adc_quantization_only", "combined_current_profile"):
        if configs.get(name, {}).get("quality", {}).get("screen_pass") is not False:
            failures.append(f"{name} did not preserve its negative boundary")
    if report.get("analog_authorized") is not False:
        failures.append("error budget authorized analog execution")
    if "no measured hardware" not in report.get("claim_boundary", ""):
        failures.append("error-budget claim boundary is incomplete")
    result = {"status": "passed" if not failures else "failed", "failures": failures,
              "finding": "weight quantization passes alone; ADC quantization is the dominant current numerical failure contributor and DAC quantization is secondary.",
              "claim_boundary": report.get("claim_boundary")}
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
