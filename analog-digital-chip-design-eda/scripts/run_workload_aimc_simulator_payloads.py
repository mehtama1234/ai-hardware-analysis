#!/usr/bin/env python3
from __future__ import annotations

import csv
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MEASURE = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "measurements"
OUT_DIR = ROOT / "evidence" / "aimc-simulator-adapters"
SUMMARY_OUT = OUT_DIR / "workload-simulator-payload-run-summary.json"
AIHWKIT_OUT = OUT_DIR / "aihwkit-workload-analog-error-simulation.json"
CROSSSIM_OUT = OUT_DIR / "crosssim-workload-analog-error-simulation.json"


WEIGHTS = [
    [0.8, -0.4, 0.2, 0.1],
    [-0.1, 0.7, 0.3, -0.5],
    [0.2, 0.1, -0.6, 0.9],
    [0.5, -0.2, 0.4, 0.3],
]
INPUT = [0.25, -0.75, 0.50, 0.10]


def module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


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


def allowed_candidates() -> list[dict[str, str]]:
    rows = read_rows(MEASURE / "model-impact-governor-requests.csv")
    return [row for row in rows if row.get("analog_candidate") == "1" and row.get("governor_decision") == "1"]


def final_nonideality() -> dict[str, str]:
    rows = read_rows(MEASURE / "analog-nonideality-stack.csv")
    if not rows:
        raise SystemExit("missing analog nonideality stack rows")
    return rows[-1]


def output_vector(row: dict[str, str]) -> list[float]:
    return [as_float(row, f"out{idx}") for idx in range(4)]


def relative_l2(reference: list[float], observed: list[float]) -> float:
    import math

    diff = math.sqrt(sum((a - b) ** 2 for a, b in zip(reference, observed)))
    denom = math.sqrt(sum(a * a for a in reference))
    return diff / denom if denom else diff


def base_payload(tool: str, tool_version: str, observed: list[float], final: dict[str, str], candidates: list[dict[str, str]]) -> dict[str, object]:
    ideal = [
        0.61,
        -0.45,
        -0.235,
        0.505,
    ]
    local_final = output_vector(final)
    simulator_residual = relative_l2(ideal, observed)
    local_residual = as_float(final, "residual_relative")
    combined_residual = max(simulator_residual, local_residual)
    candidate_ids = [row.get("policy", "unknown") for row in candidates]
    now = datetime.now(timezone.utc).isoformat()
    return {
        "result_type": "analog_simulator_adapter_output",
        "workload_run": True,
        "error_model": {
            "name": f"{tool}-backend-candidate-workload-v0",
            "tool": f"{tool} workload-shaped optional adapter run",
            "target_object": "backend-selected analog matmul candidates: " + ", ".join(candidate_ids),
            "adc_bits": as_int(final, "adc_bits"),
            "dac_bits": as_int(final, "dac_bits"),
            "final_residual_relative": combined_residual,
            "final_residual_q8": int(round(combined_residual * 128)),
            "device_assumptions": {
                "source": "backend analog-candidate workload replay",
                "programming_error": "represented by simulator output difference plus local nonideality residual boundary",
                "drift": "carried from local nonideality stack boundary, not independently swept in this workload run",
                "read_noise": "carried from simulator/default local fixture behavior",
                "boundary": "tool-executed workload-shaped fixture, not calibrated silicon",
            },
            "array_assumptions": {
                "source": "4x4 matrix-vector workload mapped to backend analog matmul candidates",
                "candidate_ids": candidate_ids,
                "candidate_shapes": [row.get("interpretation", "") for row in candidates],
                "adc_bits": as_int(final, "adc_bits"),
                "dac_bits": as_int(final, "dac_bits"),
                "row_drop_case_ohm": as_float(final, "row_drop_case_ohm"),
                "boundary": "named backend candidates with a compact 4x4 replay, not full transformer tensor shapes or analog macro layout",
            },
            "simulator_observed_output": observed,
            "ideal_output": ideal,
            "local_nonideality_output": local_final,
            "simulator_residual_relative": simulator_residual,
            "local_residual_relative": local_residual,
        },
        "temperature_range": {
            "mode": "fixed-condition",
            "ambient_c": 25.0,
            "boundary": "no temperature sweep in workload-shaped adapter run",
        },
        "voltage_range": {
            "mode": "fixture-cases",
            "row_voltage_v": [0.8],
            "boundary": "row voltage inherited from local SPICE row-drop fixture",
        },
        "accuracy_impact": {
            "estimated_drop": combined_residual,
            "pass": combined_residual <= 0.15,
            "metric": "relative_l2_output_difference_on_backend_analog_candidate_replay",
            "baseline_reference": "ideal digital 4x4 matvec replay for backend analog candidates",
            "simulated_reference": f"{tool} workload-shaped adapter output plus local nonideality boundary",
            "boundary": "backend-selected analog candidate replay only; not dataset accuracy, long-context behavior, or silicon behavior",
        },
        "calibration_profile": f"{tool}-backend-candidate-workload-v0",
        "provenance": {
            "tool": f"{tool} workload-shaped optional adapter run",
            "tool_version": tool_version,
            "measurement_level": "external_simulator_backend_candidate_workload",
            "not_measured_silicon": True,
            "generated_at": now,
            "repo": str(ROOT),
            "artifacts": [
                str((MEASURE / "model-impact-governor-requests.csv").relative_to(ROOT)),
                str((MEASURE / "analog-nonideality-stack.csv").relative_to(ROOT)),
            ],
            "claim_boundary": "strict simulator payload for backend-selected analog candidate replay; not full model accuracy, measured silicon, board runtime, measured power, physical signoff, or production readiness",
        },
    }


def run_aihwkit(final: dict[str, str], candidates: list[dict[str, str]]) -> dict[str, object]:
    if not module_available("aihwkit"):
        return {"tool": "aihwkit", "status": "skipped", "reason": "aihwkit is not importable", "payload": None}
    try:
        import torch
        import aihwkit
        from aihwkit.nn import AnalogLinear
        from aihwkit.simulator.configs import TorchInferenceRPUConfig

        torch.manual_seed(0)
        layer = AnalogLinear(4, 4, bias=False, rpu_config=TorchInferenceRPUConfig())
        weight = torch.tensor(WEIGHTS, dtype=torch.float32)
        layer.set_weights(weight)
        sample_input = torch.tensor([INPUT], dtype=torch.float32)
        observed = [float(value) for value in layer(sample_input).detach().reshape(-1).tolist()]
        payload = base_payload("aihwkit", getattr(aihwkit, "__version__", "unknown"), observed, final, candidates)
        payload["provenance"]["artifacts"].append(str(AIHWKIT_OUT.relative_to(ROOT)))
        AIHWKIT_OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if payload["accuracy_impact"]["pass"]:
            return {"tool": "aihwkit", "status": "wrote_payload", "reason": "AIHWKIT ran backend-candidate workload replay", "payload": str(AIHWKIT_OUT.relative_to(ROOT))}
        return {"tool": "aihwkit", "status": "wrote_payload_threshold_fail", "reason": "AIHWKIT ran backend-candidate workload replay; payload exceeds positive-claim residual threshold", "payload": str(AIHWKIT_OUT.relative_to(ROOT))}
    except Exception as exc:
        return {"tool": "aihwkit", "status": "failed", "reason": str(exc), "payload": None}


def run_crosssim(final: dict[str, str], candidates: list[dict[str, str]]) -> dict[str, object]:
    if not module_available("simulator"):
        return {"tool": "crosssim", "status": "skipped", "reason": "CrossSim simulator module is not importable", "payload": None}
    try:
        import numpy as np
        import simulator
        from simulator import AnalogCore, CrossSimParameters

        params = CrossSimParameters()
        matrix = np.array(WEIGHTS, dtype=float)
        vector = np.array(INPUT, dtype=float)
        core = AnalogCore(matrix, params=params)
        observed = [float(value) for value in (core @ vector).tolist()]
        payload = base_payload("crosssim", getattr(simulator, "__version__", "unknown"), observed, final, candidates)
        payload["provenance"]["artifacts"].append(str(CROSSSIM_OUT.relative_to(ROOT)))
        CROSSSIM_OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if payload["accuracy_impact"]["pass"]:
            return {"tool": "crosssim", "status": "wrote_payload", "reason": "CrossSim ran backend-candidate workload replay", "payload": str(CROSSSIM_OUT.relative_to(ROOT))}
        return {"tool": "crosssim", "status": "wrote_payload_threshold_fail", "reason": "CrossSim ran backend-candidate workload replay; payload exceeds positive-claim residual threshold", "payload": str(CROSSSIM_OUT.relative_to(ROOT))}
    except Exception as exc:
        return {"tool": "crosssim", "status": "failed", "reason": str(exc), "payload": None}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    final = final_nonideality()
    candidates = allowed_candidates()
    if not candidates:
        raise SystemExit("no allowed analog candidates found")
    results = [run_aihwkit(final, candidates), run_crosssim(final, candidates)]
    summary = {
        "result_type": "workload_aimc_simulator_payload_run_summary",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "candidate_count": len(candidates),
        "candidate_ids": [row.get("policy", "unknown") for row in candidates],
        "results": results,
        "claim_boundary": {
            "allowed": "records workload-shaped simulator payload generation for backend-selected analog matmul candidates",
            "not_allowed": "does not prove full model accuracy, measured silicon, board runtime, board power, physical signoff, or production readiness",
        },
        "next_handoff": "validate wrote_payload outputs, then expand the replay from compact 4x4 candidate shape to real model tensor shapes",
    }
    SUMMARY_OUT.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("workload_aimc_simulator_payloads")
    for result in results:
        print(f"{result['tool']},{result['status']},{result['reason']}")
    print(f"candidates,{len(candidates)}")
    print(f"summary,{SUMMARY_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
