#!/usr/bin/env python3
"""Verify the targeted c_proj ADC mitigation result."""

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
    report = json.loads((args.package / "targeted_cproj_adc_report.json").read_text(encoding="utf-8"))
    manifest = json.loads((args.package / "manifest.json").read_text(encoding="utf-8"))
    failures = []
    for entry in manifest.get("files", []):
        path = Path(entry["path"])
        if not path.is_absolute():
            path = Path.cwd() / path
        if not path.is_file() or digest(path) != entry.get("sha256"):
            failures.append(f"manifest hash mismatch: {path}")
    expected_mitigation = {"original": True, "stress": False, "third_holdout": False}
    for dataset in ("original", "stress", "third_holdout"):
        control = report.get("results", {}).get(f"uniform_adc14_control_{dataset}", {})
        mitigation = report.get("results", {}).get(f"c_proj_adc16_only_{dataset}", {})
        if control.get("adc_bits", {}).get("transformer.h.0.mlp.c_proj") != 14:
            failures.append(f"control is not ADC14 for {dataset}")
        if mitigation.get("adc_bits", {}).get("transformer.h.0.mlp.c_proj") != 16:
            failures.append(f"mitigation is not c_proj ADC16 for {dataset}")
        if mitigation.get("quality", {}).get("screen_pass") is not expected_mitigation[dataset]:
            failures.append(f"c_proj ADC16 expected screen_pass={expected_mitigation[dataset]} for {dataset}")
        quadratic = report.get("results", {}).get(f"c_proj_quadratic_only_{dataset}", {})
        expected_quadratic = dataset == "original"
        if quadratic.get("quality", {}).get("screen_pass") is not expected_quadratic:
            failures.append(f"c_proj quadratic expected screen_pass={expected_quadratic} for {dataset}")
        for label, expected_set in {
            "c_proj_settling_001": dataset != "third_holdout",
            "c_proj_settling_01": dataset != "third_holdout",
            "c_proj_settling_05": False,
        }.items():
            settling = report.get("results", {}).get(f"{label}_{dataset}", {})
            if settling.get("quality", {}).get("screen_pass") is not expected_set:
                failures.append(f"{label} expected screen_pass={expected_set} for {dataset}")
        for label, expected_set in {
            "c_proj_state_machine_095_01": False,
            "c_proj_state_machine_1_01": dataset != "third_holdout",
        }.items():
            state_machine = report.get("results", {}).get(f"{label}_{dataset}", {})
            if state_machine.get("quality", {}).get("screen_pass") is not expected_set:
                failures.append(f"{label} expected screen_pass={expected_set} for {dataset}")
    if (report.get("decision") != "c_proj_adc16_does_not_generalize"
            or report.get("quadratic_decision") != "c_proj_quadratic_does_not_generalize"
            or any(value != "does_not_generalize" for value in report.get("settling_decisions", {}).values())
            or report.get("analog_authorized") is not False):
        failures.append("targeted mitigation decision is unsafe")
    boundary = report.get("claim_boundary", "")
    if "Local CPU" not in boundary or "analog authorization" not in boundary:
        failures.append("claim boundary is too broad")
    print(json.dumps({"status": "passed" if not failures else "failed", "failures": failures,
                      "finding": "raising ADC resolution only at c_proj does not generalize across the frozen workload splits.",
                      "claim_boundary": boundary}, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
