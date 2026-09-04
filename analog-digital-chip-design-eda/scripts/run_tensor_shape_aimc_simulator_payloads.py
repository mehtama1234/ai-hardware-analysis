#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import math
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MEASURE = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "measurements"
OUT_DIR = ROOT / "evidence" / "aimc-simulator-adapters"
SUMMARY_OUT = OUT_DIR / "tensor-shape-simulator-payload-run-summary.json"
AIHWKIT_OUT = OUT_DIR / "aihwkit-tensor-shape-analog-error-simulation.json"
CROSSSIM_OUT = OUT_DIR / "crosssim-tensor-shape-analog-error-simulation.json"
PLACEMENT = MEASURE / "backend-hardware-placement.json"


def module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def parse_shape(value: object) -> list[int]:
    if not isinstance(value, str):
        return []
    try:
        parsed = ast.literal_eval(value)
    except (SyntaxError, ValueError):
        return []
    if not isinstance(parsed, list):
        return []
    return [int(item) for item in parsed if isinstance(item, int)]


def deterministic_unit(key: str) -> float:
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    raw = int.from_bytes(digest[:4], "big") / 0xFFFFFFFF
    return (raw * 2.0) - 1.0


def deterministic_matrix(candidate_id: str, out_dim: int, in_dim: int) -> list[list[float]]:
    return [
        [round(deterministic_unit(f"{candidate_id}:w:{row}:{col}"), 6) for col in range(in_dim)]
        for row in range(out_dim)
    ]


def deterministic_vector(candidate_id: str, in_dim: int) -> list[float]:
    return [round(deterministic_unit(f"{candidate_id}:x:{idx}"), 6) for idx in range(in_dim)]


def matvec(matrix: list[list[float]], vector: list[float]) -> list[float]:
    return [sum(weight * value for weight, value in zip(row, vector)) for row in matrix]


def relative_l2(reference: list[float], observed: list[float]) -> float:
    diff = math.sqrt(sum((a - b) ** 2 for a, b in zip(reference, observed)))
    denom = math.sqrt(sum(a * a for a in reference))
    return diff / denom if denom else diff


def analog_candidates() -> list[dict[str, object]]:
    placement = json.loads(PLACEMENT.read_text(encoding="utf-8"))
    rows = placement.get("placement_rows")
    if not isinstance(rows, list):
        raise SystemExit("backend hardware placement has no placement_rows list")
    candidates = [
        row
        for row in rows
        if isinstance(row, dict)
        and row.get("analog_candidate") is True
        and row.get("placement") == "analog"
        and row.get("operator_kind") == "MatMul"
    ]
    if not candidates:
        raise SystemExit("no analog MatMul candidates found in backend hardware placement")
    return candidates


def candidate_fixtures(candidates: list[dict[str, object]]) -> list[dict[str, object]]:
    previous_out_dim = 4
    fixtures = []
    for row in candidates:
        candidate_id = str(row.get("operator_id", "unknown"))
        shape = parse_shape(row.get("shape"))
        out_dim = shape[-1] if shape else previous_out_dim
        in_dim = previous_out_dim
        weights = deterministic_matrix(candidate_id, out_dim, in_dim)
        input_vector = deterministic_vector(candidate_id, in_dim)
        ideal = matvec(weights, input_vector)
        fixtures.append(
            {
                "candidate_id": candidate_id,
                "block": row.get("block"),
                "declared_shape": row.get("shape"),
                "input_dim": in_dim,
                "output_dim": out_dim,
                "weights": weights,
                "input": input_vector,
                "ideal_output": ideal,
                "governor_fields": row.get("governor_fields"),
            }
        )
        previous_out_dim = out_dim
    return fixtures


def payload(tool: str, version: str, measurement_level: str, per_candidate: list[dict[str, object]]) -> dict[str, object]:
    max_residual = max(float(item["simulator_residual_relative"]) for item in per_candidate)
    candidate_ids = [str(item["candidate_id"]) for item in per_candidate]
    now = datetime.now(timezone.utc).isoformat()
    return {
        "result_type": "analog_simulator_adapter_output",
        "tensor_shape_run": True,
        "error_model": {
            "name": f"{tool}-backend-tensor-shape-v0",
            "tool": f"{tool} tensor-shaped optional adapter run",
            "target_object": "backend analog MatMul candidates: " + ", ".join(candidate_ids),
            "adc_bits": 8,
            "dac_bits": 8,
            "final_residual_relative": max_residual,
            "final_residual_q8": int(round(max_residual * 128)),
            "device_assumptions": {
                "source": "external simulator replay for backend analog MatMul candidates",
                "programming_error": "whatever the simulator applies for this fixture, measured as output residual",
                "drift": "not swept in this tensor-shaped replay",
                "read_noise": "not independently swept in this tensor-shaped replay",
                "boundary": "simulator-executed deterministic tensor fixture, not calibrated silicon",
            },
            "array_assumptions": {
                "source": "backend hardware placement shapes",
                "candidate_ids": candidate_ids,
                "candidate_shapes": [str(item["declared_shape"]) for item in per_candidate],
                "boundary": "uses the backend candidate chain shape; uses deterministic weights because trained package weights are not present in the local placement artifact",
            },
            "per_candidate_results": per_candidate,
            "simulator_residual_relative": max_residual,
            "ideal_output": per_candidate[-1]["ideal_output"],
            "simulator_observed_output": per_candidate[-1]["simulator_output"],
        },
        "temperature_range": {
            "mode": "fixed-condition",
            "ambient_c": 25.0,
            "boundary": "no temperature sweep in tensor-shaped replay",
        },
        "voltage_range": {
            "mode": "fixture-cases",
            "row_voltage_v": [0.8],
            "boundary": "no voltage sweep in tensor-shaped replay",
        },
        "accuracy_impact": {
            "estimated_drop": max_residual,
            "pass": max_residual <= 0.15,
            "metric": "relative_l2_output_difference_on_backend_tensor_shape_replay",
            "baseline_reference": "digital matrix-vector result for each backend analog MatMul candidate",
            "simulated_reference": f"{tool} tensor-shaped adapter output",
            "boundary": "candidate tensor-shape agreement only; not dataset accuracy, full model behavior, calibrated silicon, board runtime, or measured power",
        },
        "calibration_profile": f"{tool}-backend-tensor-shape-v0",
        "provenance": {
            "tool": f"{tool} tensor-shaped optional adapter run",
            "tool_version": version,
            "measurement_level": measurement_level,
            "not_measured_silicon": True,
            "generated_at": now,
            "repo": str(ROOT),
            "artifacts": [str(PLACEMENT.relative_to(ROOT))],
            "claim_boundary": "strict simulator payload for backend analog MatMul candidate tensor shapes with deterministic fixture weights; not trained-weight true, full model true, measured silicon, board runtime, measured power, physical signoff, or production readiness",
        },
    }


def run_aihwkit(fixtures: list[dict[str, object]]) -> dict[str, object]:
    if not module_available("aihwkit"):
        return {"tool": "aihwkit", "status": "skipped", "reason": "aihwkit is not importable", "payload": None}
    try:
        import torch
        import aihwkit
        from aihwkit.nn import AnalogLinear
        from aihwkit.simulator.configs import TorchInferenceRPUConfig

        results = []
        for fixture in fixtures:
            layer = AnalogLinear(int(fixture["input_dim"]), int(fixture["output_dim"]), bias=False, rpu_config=TorchInferenceRPUConfig())
            weight = torch.tensor(fixture["weights"], dtype=torch.float32)
            layer.set_weights(weight)
            sample = torch.tensor([fixture["input"]], dtype=torch.float32)
            observed = [float(value) for value in layer(sample).detach().reshape(-1).tolist()]
            ideal = [float(value) for value in fixture["ideal_output"]]
            result = dict(fixture)
            result["simulator_output"] = observed
            result["simulator_residual_relative"] = relative_l2(ideal, observed)
            results.append(result)
        body = payload("aihwkit", getattr(aihwkit, "__version__", "unknown"), "external_simulator_backend_tensor_shape_replay", results)
        body["provenance"]["artifacts"].append(str(AIHWKIT_OUT.relative_to(ROOT)))
        AIHWKIT_OUT.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if body["accuracy_impact"]["pass"] is True:
            status = "wrote_payload"
            reason = "AIHWKIT ran backend tensor-shape replay"
        else:
            status = "wrote_payload_threshold_fail"
            reason = "AIHWKIT ran backend tensor-shape replay; payload exceeds positive-claim residual threshold"
        return {"tool": "aihwkit", "status": status, "reason": reason, "payload": str(AIHWKIT_OUT.relative_to(ROOT))}
    except Exception as exc:
        return {"tool": "aihwkit", "status": "failed", "reason": str(exc), "payload": None}


def run_crosssim(fixtures: list[dict[str, object]]) -> dict[str, object]:
    if not module_available("simulator"):
        return {"tool": "crosssim", "status": "skipped", "reason": "CrossSim simulator module is not importable", "payload": None}
    try:
        import numpy as np
        import simulator
        from simulator import AnalogCore, CrossSimParameters

        results = []
        for fixture in fixtures:
            params = CrossSimParameters()
            core = AnalogCore(np.array(fixture["weights"], dtype=float), params=params)
            observed = [float(value) for value in (core @ np.array(fixture["input"], dtype=float)).tolist()]
            ideal = [float(value) for value in fixture["ideal_output"]]
            result = dict(fixture)
            result["simulator_output"] = observed
            result["simulator_residual_relative"] = relative_l2(ideal, observed)
            results.append(result)
        body = payload("crosssim", getattr(simulator, "__version__", "unknown"), "external_simulator_backend_tensor_shape_replay", results)
        body["provenance"]["artifacts"].append(str(CROSSSIM_OUT.relative_to(ROOT)))
        CROSSSIM_OUT.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if body["accuracy_impact"]["pass"] is True:
            status = "wrote_payload"
            reason = "CrossSim ran backend tensor-shape replay"
        else:
            status = "wrote_payload_threshold_fail"
            reason = "CrossSim ran backend tensor-shape replay; payload exceeds positive-claim residual threshold"
        return {"tool": "crosssim", "status": status, "reason": reason, "payload": str(CROSSSIM_OUT.relative_to(ROOT))}
    except Exception as exc:
        return {"tool": "crosssim", "status": "failed", "reason": str(exc), "payload": None}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fixtures = candidate_fixtures(analog_candidates())
    results = [run_aihwkit(fixtures), run_crosssim(fixtures)]
    summary = {
        "result_type": "tensor_shape_aimc_simulator_payload_run_summary",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "candidate_count": len(fixtures),
        "candidate_ids": [str(item["candidate_id"]) for item in fixtures],
        "results": results,
        "claim_boundary": {
            "allowed": "records simulator payload generation for backend analog MatMul candidates using the candidate chain tensor shapes",
            "not_allowed": "this tensor-shaped fixture does not prove trained package weights, full model accuracy, measured silicon, board runtime, board power, physical signoff, or production readiness",
        },
    }
    SUMMARY_OUT.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("tensor_shape_aimc_simulator_payloads")
    for result in results:
        print(f"{result['tool']},{result['status']},{result['reason']}")
    print(f"candidates,{len(fixtures)}")
    print(f"summary,{SUMMARY_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
