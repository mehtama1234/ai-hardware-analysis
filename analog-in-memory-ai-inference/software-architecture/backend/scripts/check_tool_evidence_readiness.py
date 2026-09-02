#!/usr/bin/env python3
"""Regression check for analog simulator evidence boundaries."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRENT_LAB_EVIDENCE = (
    ROOT.parents[3] / "analog-digital-chip-design-eda" / "evidence" / "aimc-hardware-lab"
)
IMPORT_TEMPLATES = ROOT.parent / "review-package-demo" / "import-templates"
sys.path.insert(0, str(ROOT))

from evidence_imports import build_import_record, build_tool_readiness_report, validate_imported_evidence  # noqa: E402


def load_current(source_file: str) -> dict:
    path = CURRENT_LAB_EVIDENCE / source_file
    if not path.exists():
        raise SystemExit(f"missing current lab evidence: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_template(template_file: str) -> dict:
    path = IMPORT_TEMPLATES / template_file
    if not path.exists():
        raise SystemExit(f"missing import template: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def calibrated_simulator_payload() -> dict:
    return {
        "error_model": {
            "name": "crosssim-rram-v1",
            "adc_bits": 6,
            "dac_bits": 4,
            "final_residual_relative": 0.031,
            "conductance_noise_sigma": 0.012,
            "drift_model": "power-law-24h",
        },
        "temperature_range": {"mode": "fixed-condition", "ambient_c": 25.0, "boundary": "bench fixture only"},
        "voltage_range": {"mode": "sweep", "row_voltage_v": [0.15, 0.20, 0.25]},
        "accuracy_impact": {
            "estimated_drop": 0.018,
            "pass": True,
            "metric": "task_accuracy_delta",
        },
        "calibration_profile": "crosssim-rram-bench-profile-v1",
        "provenance": {
            "tool": "CrossSim calibrated analog simulator",
            "tool_version": "test-fixture",
            "not_measured_silicon": True,
            "measurement_level": "calibrated_simulation",
        },
    }


def expect(name: str, condition: bool, details: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL {name}: {details}")
    print(f"PASS {name}: {details}")


def check_source(payload: dict, expected_ready: bool, label: str) -> None:
    ordinary_errors = validate_imported_evidence("analog_error_simulation", payload)
    readiness = build_tool_readiness_report("analog_error_simulation", payload)
    expect(f"{label} ordinary validation", not ordinary_errors, "structural schema accepted")
    expect(
        f"{label} analog simulator readiness",
        readiness["tool_ready"] is expected_ready,
        f"tool_ready={readiness['tool_ready']} issues={len(readiness['issues'])}",
    )
    if readiness["tool_ready"]:
        record = build_import_record("analog_error_simulation", payload, package_id="pkg-tool-test")
        expect(
            f"{label} strict tool import record",
            record["summary"]["status"] == "accepted" and record["source_id"] == "analog_error_simulation",
            f"import_id={record['import_id']}",
        )
    else:
        expect(
            f"{label} strict tool import rejection",
            bool(readiness["issues"]),
            "strict tool path keeps this as ordinary/local evidence only",
        )


def main() -> None:
    check_source(load_current("analog_error_simulation.json"), expected_ready=False, label="current local lab analog evidence")
    check_source(calibrated_simulator_payload(), expected_ready=True, label="calibrated simulator sample")
    check_source(load_template("analog-simulator-tool-evidence.template.json"), expected_ready=True, label="strict simulator template")


if __name__ == "__main__":
    main()
