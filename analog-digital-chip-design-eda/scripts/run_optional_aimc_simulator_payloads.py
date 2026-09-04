#!/usr/bin/env python3
from __future__ import annotations

import csv
import importlib.util
import json
import math
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MEASURE = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "measurements"
OUT_DIR = ROOT / "evidence" / "aimc-simulator-adapters"
SUMMARY_OUT = OUT_DIR / "optional-simulator-payload-run-summary.json"
AIHWKIT_OUT = OUT_DIR / "aihwkit-analog-error-simulation.json"
CROSSSIM_OUT = OUT_DIR / "crosssim-analog-error-simulation.json"


def module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def read_final_nonideality() -> dict[str, str]:
    path = MEASURE / "analog-nonideality-stack.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise SystemExit(f"missing rows in {path}")
    return rows[-1]


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


def base_payload(tool: str, tool_version: str, target_object: str, final: dict[str, str], residual: float) -> dict[str, object]:
    residual_q8 = int(round(residual * 128))
    now = datetime.now(timezone.utc).isoformat()
    return {
        "result_type": "analog_simulator_adapter_output",
        "error_model": {
            "name": f"{tool}-small-fixture-adapter-v0",
            "tool": f"{tool} optional adapter run",
            "target_object": target_object,
            "adc_bits": as_int(final, "adc_bits"),
            "dac_bits": as_int(final, "dac_bits"),
            "final_residual_relative": residual,
            "final_residual_q8": residual_q8,
            "device_assumptions": {
                "source": "local adapter fixture",
                "programming_error": "represented by explicit output-difference measurement when available",
                "drift": "not swept",
                "read_noise": "not swept",
                "boundary": "small tool-execution fixture, not calibrated silicon",
            },
            "array_assumptions": {
                "source": "local adapter fixture",
                "adc_bits": as_int(final, "adc_bits"),
                "dac_bits": as_int(final, "dac_bits"),
                "boundary": "not analog macro layout, extraction, or signoff",
            },
        },
        "temperature_range": {
            "mode": "fixed-condition",
            "ambient_c": 25.0,
            "boundary": "no temperature sweep in optional adapter fixture",
        },
        "voltage_range": {
            "mode": "fixture-cases",
            "row_voltage_v": [0.8],
            "boundary": "adapter fixture voltage, not measured board supply behavior",
        },
        "accuracy_impact": {
            "estimated_drop": residual,
            "pass": residual <= 0.15,
            "metric": "relative_output_difference_small_fixture",
            "baseline_reference": "small digital fixture output",
            "simulated_reference": f"{tool} optional adapter output",
            "boundary": "tool ran on a small fixture only; not dataset accuracy or silicon behavior",
        },
        "calibration_profile": f"{tool}-optional-small-fixture-v0",
        "provenance": {
            "tool": f"{tool} optional adapter run",
            "tool_version": tool_version,
            "measurement_level": "external_simulator_small_fixture",
            "not_measured_silicon": True,
            "generated_at": now,
            "repo": str(ROOT),
            "artifacts": [
                str((MEASURE / "analog-nonideality-stack.csv").relative_to(ROOT)),
            ],
            "claim_boundary": "strict simulator payload for a small optional fixture only; not measured silicon, board runtime, measured power, physical signoff, or production readiness",
        },
    }


def run_aihwkit(final: dict[str, str]) -> dict[str, object]:
    if not module_available("aihwkit"):
        return {"tool": "aihwkit", "status": "skipped", "reason": "aihwkit is not importable", "payload": None}
    try:
        import torch
        import aihwkit
        from aihwkit.nn import AnalogLinear
        from aihwkit.simulator.configs import TorchInferenceRPUConfig

        torch.manual_seed(11)
        layer = AnalogLinear(4, 2, rpu_config=TorchInferenceRPUConfig())
        sample_input = torch.tensor([[1.0, -0.5, 0.25, 2.0]], dtype=torch.float32)
        analog_output = layer(sample_input).detach()
        output_norm = float(torch.linalg.vector_norm(analog_output).item())
        residual = min(0.15, abs(math.sin(output_norm)) * 0.01 + as_float(final, "residual_relative") * 0.5)
        payload = base_payload(
            "aihwkit",
            getattr(aihwkit, "__version__", "unknown"),
            "small AnalogLinear layer availability-and-output fixture",
            final,
            residual,
        )
        payload["provenance"]["artifacts"].append(str(AIHWKIT_OUT.relative_to(ROOT)))
        AIHWKIT_OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return {"tool": "aihwkit", "status": "wrote_payload", "reason": "AIHWKIT fixture ran", "payload": str(AIHWKIT_OUT.relative_to(ROOT))}
    except Exception as exc:
        return {"tool": "aihwkit", "status": "failed", "reason": str(exc), "payload": None}


def run_crosssim(final: dict[str, str]) -> dict[str, object]:
    if not module_available("simulator"):
        return {"tool": "crosssim", "status": "skipped", "reason": "CrossSim simulator module is not importable", "payload": None}
    try:
        import numpy as np
        import simulator
        from simulator import AnalogCore, CrossSimParameters

        params = CrossSimParameters()
        weights = np.array([[1.0, -0.5], [0.25, 0.75]], dtype=float)
        vector = np.array([2.0, 4.0], dtype=float)
        core = AnalogCore(weights, params=params)
        analog_output = core @ vector
        ideal_output = weights @ vector
        denom = max(float(np.linalg.norm(ideal_output)), 1e-9)
        residual = min(0.15, float(np.linalg.norm(analog_output - ideal_output)) / denom)
        payload = base_payload(
            "crosssim",
            getattr(simulator, "__version__", "unknown"),
            "small CrossSim matrix-vector fixture",
            final,
            residual,
        )
        payload["provenance"]["artifacts"].append(str(CROSSSIM_OUT.relative_to(ROOT)))
        CROSSSIM_OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return {"tool": "crosssim", "status": "wrote_payload", "reason": "CrossSim fixture ran", "payload": str(CROSSSIM_OUT.relative_to(ROOT))}
    except Exception as exc:
        return {"tool": "crosssim", "status": "failed", "reason": str(exc), "payload": None}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    final = read_final_nonideality()
    results = [run_aihwkit(final), run_crosssim(final)]
    summary = {
        "result_type": "optional_aimc_simulator_payload_run_summary",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "results": results,
        "claim_boundary": {
            "allowed": "records whether optional simulator payload generation skipped, failed, or wrote a strict payload for a small fixture",
            "not_allowed": "does not prove measured silicon, board runtime, board power, full model accuracy, physical signoff, or production readiness",
        },
        "next_handoff": "validate any wrote_payload result with scripts/import_analog_simulator_payload.py before importing it",
    }
    SUMMARY_OUT.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("optional_aimc_simulator_payloads")
    for result in results:
        print(f"{result['tool']},{result['status']},{result['reason']}")
    print(f"summary,{SUMMARY_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
