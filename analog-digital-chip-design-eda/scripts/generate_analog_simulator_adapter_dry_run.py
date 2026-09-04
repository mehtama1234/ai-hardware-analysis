#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MEASURE = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "measurements"
OUT_DIR = ROOT / "evidence" / "aimc-simulator-adapters" / "dry-run"
AIHWKIT_OUT = OUT_DIR / "aihwkit-analog-error-simulation.dry-run.json"
CROSSSIM_OUT = OUT_DIR / "crosssim-analog-error-simulation.dry-run.json"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def as_float(row: dict[str, str], key: str, default: float = 0.0) -> float:
    try:
        return float(row.get(key, default))
    except (TypeError, ValueError):
        return default


def as_int(row: dict[str, str], key: str, default: int = 0) -> int:
    try:
        return int(float(row.get(key, default)))
    except (TypeError, ValueError):
        return default


def build_payload(tool: str, target_object: str, final: dict[str, str]) -> dict[str, object]:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "result_type": "analog_simulator_adapter_dry_run",
        "dry_run": True,
        "error_model": {
            "name": f"{tool}-adapter-dry-run-v0",
            "tool": f"{tool} dry-run placeholder",
            "target_object": target_object,
            "adc_bits": as_int(final, "adc_bits"),
            "dac_bits": as_int(final, "dac_bits"),
            "final_residual_relative": as_float(final, "residual_relative"),
            "final_residual_q8": as_int(final, "residual_q8"),
            "device_assumptions": {
                "source": "copied from local nonideality stack for payload-shape testing",
                "boundary": "not produced by a real external simulator run",
            },
            "array_assumptions": {
                "source": "copied from local row-drop and converter assumptions for payload-shape testing",
                "boundary": "not produced by a real CrossSim or AIHWKIT run",
            },
        },
        "temperature_range": {
            "mode": "dry-run-fixed-condition",
            "ambient_c": 25.0,
            "boundary": "placeholder only; no simulator temperature sweep ran",
        },
        "voltage_range": {
            "mode": "dry-run-fixture-cases",
            "row_voltage_v": [0.8],
            "boundary": "placeholder only; no simulator voltage sweep ran",
        },
        "accuracy_impact": {
            "estimated_drop": as_float(final, "residual_relative"),
            "pass": False,
            "metric": "dry_run_shape_check_only",
            "baseline_reference": "local ideal digital fixture",
            "simulated_reference": "no external simulator executed",
            "boundary": "dry-run payload shape only; must not be imported as strict simulator evidence",
        },
        "calibration_profile": f"{tool}-dry-run-no-calibration",
        "provenance": {
            "tool": f"{tool} dry-run placeholder",
            "tool_version": "not-run",
            "measurement_level": "dry_run",
            "not_measured_silicon": True,
            "generated_at": now,
            "repo": str(ROOT),
            "artifacts": [
                "labs/analog/analog-in-memory-foundation-model-hardware/measurements/analog-nonideality-stack.csv",
            ],
            "claim_boundary": "payload shape example only; no simulator executed and no claim may be upgraded",
        },
    }


def main() -> int:
    rows = read_rows(MEASURE / "analog-nonideality-stack.csv")
    if not rows:
        raise SystemExit("missing analog nonideality rows")
    final = rows[-1]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    aihwkit = build_payload("aihwkit", "backend dense matmul analog candidate", final)
    crosssim = build_payload("crosssim", "selected AIMC crossbar matrix-vector case", final)
    AIHWKIT_OUT.write_text(json.dumps(aihwkit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    CROSSSIM_OUT.write_text(json.dumps(crosssim, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("analog_simulator_adapter_dry_run")
    print(f"aihwkit,{AIHWKIT_OUT}")
    print(f"crosssim,{CROSSSIM_OUT}")
    print("strict_import_ready,False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
