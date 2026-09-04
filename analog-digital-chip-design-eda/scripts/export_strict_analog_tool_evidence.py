#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MEASURE = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "measurements"
OUT_DIR = ROOT / "evidence" / "aimc-hardware-lab"
OLD_BACKEND = (
    ROOT.parent
    / "analog-in-memory-ai-inference"
    / "software-architecture"
    / "backend"
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def as_float(row: dict[str, str], key: str) -> float:
    return float(row[key])


def as_int(row: dict[str, str], key: str) -> int:
    return int(float(row[key]))


def build_payload() -> dict[str, object]:
    stack_rows = read_csv(MEASURE / "analog-nonideality-stack.csv")
    row_drop_rows = read_csv(MEASURE / "spice-row-drop-comparison.csv")
    final = stack_rows[-1]
    row_voltages = sorted({round(as_float(row, "v_in"), 6) for row in row_drop_rows})
    row_drop_cases = [
        {
            "rseg_ohm": as_float(row, "rseg_ohm"),
            "input_v": as_float(row, "v_in"),
            "current_loss_pct": as_float(row, "row_drop_current_loss_pct"),
            "distributed_model_relative_error": as_float(row, "distributed_model_relative_error"),
        }
        for row in row_drop_rows
    ]
    return {
        "error_model": {
            "name": "ngspice-local-row-drop-plus-aimc-nonideality-v0",
            "tool": "ngspice local row-drop comparison plus AIMC nonideality stack",
            "target_object": "selected AIMC analog projection tile and backend dense matmul candidates",
            "adc_bits": as_int(final, "adc_bits"),
            "dac_bits": as_int(final, "dac_bits"),
            "final_residual_relative": as_float(final, "residual_relative"),
            "final_residual_q8": as_int(final, "residual_q8"),
            "row_drop_case_ohm": as_float(final, "row_drop_case_ohm"),
            "spice_row_drop_loss_pct": as_float(final, "spice_row_drop_loss_pct"),
            "device_assumptions": {
                "signed_weight_encoding": "differential conductance pair",
                "programming_error": "included in local nonideality stack",
                "drift": "included in local nonideality stack",
                "read_noise": "included through local residual stack",
                "boundary": "fixture assumptions, not calibrated silicon measurements",
            },
            "array_assumptions": {
                "row_drop_cases_ohm": sorted({as_float(row, "rseg_ohm") for row in row_drop_rows}),
                "row_voltage_v": row_voltages,
                "bit_slicing": "not modeled as a full CrossSim array",
                "boundary": "row-drop fixture plus local AIMC residual stack, not analog macro layout",
            },
            "stages": [row["stage"] for row in stack_rows],
            "row_drop_cases": row_drop_cases,
        },
        "temperature_range": {
            "mode": "fixed-condition",
            "ambient_c": 25.0,
            "boundary": "local educational row-drop and nonideality fixture; not swept across temperature",
        },
        "voltage_range": {
            "mode": "fixture-cases",
            "row_voltage_v": row_voltages,
            "boundary": "row voltage comes from the local SPICE row-drop comparison fixture",
        },
        "accuracy_impact": {
            "estimated_drop": as_float(final, "residual_relative"),
            "pass": as_int(final, "residual_q8") <= 16,
            "metric": "task_accuracy_delta_proxy",
            "baseline_reference": "ideal digital dot-product fixture",
            "simulated_reference": "ngspice row-drop and local AIMC nonideality fixture",
            "boundary": "proxy impact from analog residual; not dataset-backed task accuracy",
        },
        "calibration_profile": "ngspice-local-aimc-row-drop-profile-v0",
        "provenance": {
            "tool": "ngspice local row-drop comparison plus AIMC nonideality stack",
            "tool_version": "local-script-fixture",
            "measurement_level": "calibrated_simulation",
            "not_measured_silicon": True,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "repo": str(ROOT),
            "artifacts": [
                "measurements/spice-row-drop-comparison.csv",
                "measurements/analog-nonideality-stack.csv",
            ],
            "claim_boundary": "strict simulator/tool evidence for a bounded local fixture; not measured silicon, board runtime, measured power, physical signoff, or production readiness",
        },
    }


def validate_with_backend(payload: dict[str, object]) -> dict[str, object]:
    sys.path.insert(0, str(OLD_BACKEND))
    from evidence_imports import build_tool_readiness_report, validate_imported_evidence

    errors = validate_imported_evidence("analog_error_simulation", payload)
    readiness = build_tool_readiness_report("analog_error_simulation", payload)
    if errors:
        raise SystemExit(f"strict analog tool payload failed structural validation: {errors}")
    if not readiness["tool_ready"]:
        raise SystemExit(f"strict analog tool payload failed readiness: {readiness['issues']}")
    return readiness


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = build_payload()
    readiness = validate_with_backend(payload)
    output = OUT_DIR / "analog_error_simulation_strict_tool.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("strict_analog_tool_evidence")
    print(f"output,{output}")
    print(f"tool_ready,{readiness['tool_ready']}")
    print(f"issues,{len(readiness['issues'])}")
    print(f"final_residual_relative,{payload['error_model']['final_residual_relative']}")
    print(f"calibration_profile,{payload['calibration_profile']}")


if __name__ == "__main__":
    main()
