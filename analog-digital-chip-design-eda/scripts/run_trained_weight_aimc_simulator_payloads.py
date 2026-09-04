#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import math
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OLD_ROOT = ROOT.parent / "ai-hardware-analysis" / "analog-in-memory-ai-inference" / "software-architecture"
ONNX_PYTHON = OLD_ROOT / "backend" / ".venv" / "bin" / "python"
MODEL = OLD_ROOT / "samples" / "tiny-mlp.onnx"
PLACEMENT = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "measurements" / "backend-hardware-placement.json"
OUT_DIR = ROOT / "evidence" / "aimc-simulator-adapters"
SUMMARY_OUT = OUT_DIR / "trained-weight-simulator-payload-run-summary.json"
AIHWKIT_OUT = OUT_DIR / "aihwkit-trained-weight-analog-error-simulation.json"
CROSSSIM_OUT = OUT_DIR / "crosssim-trained-weight-analog-error-simulation.json"

INPUT = [0.25, -0.75, 0.50, 0.10]


def module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def extract_onnx() -> dict[str, object]:
    if not ONNX_PYTHON.exists():
        raise SystemExit(f"ONNX Python is missing: {ONNX_PYTHON}")
    code = r"""
import json
import onnx
from onnx import numpy_helper
from pathlib import Path
model = onnx.load(Path(__import__("sys").argv[1]))
payload = {"nodes": [], "initializers": {}}
for node in model.graph.node:
    payload["nodes"].append({
        "name": node.name,
        "op_type": node.op_type,
        "inputs": list(node.input),
        "outputs": list(node.output),
    })
for init in model.graph.initializer:
    arr = numpy_helper.to_array(init)
    payload["initializers"][init.name] = {
        "shape": list(arr.shape),
        "values": arr.astype(float).tolist(),
    }
print(json.dumps(payload))
"""
    result = subprocess.run([str(ONNX_PYTHON), "-c", code, str(MODEL)], text=True, capture_output=True, check=True)
    return json.loads(result.stdout)


def matvec_onnx_weight(vector: list[float], weight_in_out: list[list[float]]) -> list[float]:
    out_dim = len(weight_in_out[0])
    return [sum(vector[row] * weight_in_out[row][col] for row in range(len(vector))) for col in range(out_dim)]


def add(left: list[float], right: list[float]) -> list[float]:
    return [a + b for a, b in zip(left, right)]


def relu(values: list[float]) -> list[float]:
    return [max(0.0, value) for value in values]


def transpose(weight_in_out: list[list[float]]) -> list[list[float]]:
    return [list(row) for row in zip(*weight_in_out)]


def relative_l2(reference: list[float], observed: list[float]) -> float:
    diff = math.sqrt(sum((a - b) ** 2 for a, b in zip(reference, observed)))
    denom = math.sqrt(sum(a * a for a in reference))
    return diff / denom if denom else diff


def digital_reference(weights: dict[str, object]) -> dict[str, list[float]]:
    w1 = weights["w1"]["values"]
    b1 = weights["b1"]["values"]
    w2 = weights["w2"]["values"]
    b2 = weights["b2"]["values"]
    hidden_mm = matvec_onnx_weight(INPUT, w1)
    hidden_add = add(hidden_mm, b1)
    hidden_relu = relu(hidden_add)
    logits_mm = matvec_onnx_weight(hidden_relu, w2)
    output = add(logits_mm, b2)
    return {
        "input": INPUT,
        "dense1.matmul": hidden_mm,
        "dense1.bias": hidden_add,
        "dense1.relu": hidden_relu,
        "dense2.matmul": logits_mm,
        "dense2.bias": output,
    }


def placement_candidates() -> list[dict[str, object]]:
    placement = json.loads(PLACEMENT.read_text(encoding="utf-8"))
    rows = placement.get("placement_rows")
    if not isinstance(rows, list):
        return []
    return [
        row
        for row in rows
        if isinstance(row, dict)
        and row.get("operator_kind") == "MatMul"
        and row.get("placement") == "analog"
        and row.get("analog_candidate") is True
    ]


def payload(tool: str, version: str, per_candidate: list[dict[str, object]], final_output: list[float], ideal_final: list[float]) -> dict[str, object]:
    final_residual = relative_l2(ideal_final, final_output)
    max_candidate_residual = max(float(item["simulator_residual_relative"]) for item in per_candidate)
    residual = max(final_residual, max_candidate_residual)
    now = datetime.now(timezone.utc).isoformat()
    return {
        "result_type": "analog_simulator_adapter_output",
        "trained_weight_run": True,
        "error_model": {
            "name": f"{tool}-backend-trained-weight-v0",
            "tool": f"{tool} trained-weight optional adapter run",
            "target_object": "uploaded tiny-mlp.onnx analog MatMul weights: dense1.matmul, dense2.matmul",
            "adc_bits": 8,
            "dac_bits": 8,
            "final_residual_relative": residual,
            "final_residual_q8": int(round(residual * 128)),
            "device_assumptions": {
                "source": "external simulator replay using ONNX initializer weights",
                "programming_error": "measured as simulator output residual against digital matmul",
                "drift": "not swept in trained-weight replay",
                "read_noise": "not independently swept in trained-weight replay",
                "boundary": "real ONNX weights through simulator APIs, not calibrated silicon",
            },
            "array_assumptions": {
                "source": "source-model.onnx initializers plus backend hardware placement",
                "candidate_ids": [str(item["candidate_id"]) for item in per_candidate],
                "candidate_shapes": [str(item["weight_shape_in_out"]) for item in per_candidate],
                "boundary": "uses real tiny-mlp ONNX weights for analog MatMul operators; digital bias and ReLU are local reference arithmetic",
            },
            "per_candidate_results": per_candidate,
            "ideal_output": ideal_final,
            "simulator_observed_output": final_output,
            "simulator_residual_relative": final_residual,
        },
        "temperature_range": {
            "mode": "fixed-condition",
            "ambient_c": 25.0,
            "boundary": "no temperature sweep in trained-weight replay",
        },
        "voltage_range": {
            "mode": "fixture-cases",
            "row_voltage_v": [0.8],
            "boundary": "no voltage sweep in trained-weight replay",
        },
        "accuracy_impact": {
            "estimated_drop": residual,
            "pass": residual <= 0.15,
            "metric": "relative_l2_output_difference_on_tiny_mlp_trained_weight_replay",
            "baseline_reference": "digital ONNX-weight matrix operations with digital bias and ReLU",
            "simulated_reference": f"{tool} for analog MatMul operators, digital arithmetic for bias and ReLU",
            "boundary": "tiny MLP sample model only; not dataset accuracy, calibrated silicon, board runtime, measured power, or production readiness",
        },
        "calibration_profile": f"{tool}-backend-trained-weight-v0",
        "provenance": {
            "tool": f"{tool} trained-weight optional adapter run",
            "tool_version": version,
            "measurement_level": "external_simulator_backend_trained_weight_replay",
            "not_measured_silicon": True,
            "generated_at": now,
            "repo": str(ROOT),
            "artifacts": [str(MODEL), str(PLACEMENT.relative_to(ROOT))],
            "claim_boundary": "strict simulator payload for real ONNX weights in the current tiny MLP analog MatMul operators; not full foundation-model behavior, measured silicon, board runtime, measured power, physical signoff, or production readiness",
        },
    }


def run_aihwkit(model: dict[str, object], reference: dict[str, list[float]]) -> dict[str, object]:
    if not module_available("aihwkit"):
        return {"tool": "aihwkit", "status": "skipped", "reason": "aihwkit is not importable", "payload": None}
    try:
        import torch
        import aihwkit
        from aihwkit.nn import AnalogLinear
        from aihwkit.simulator.configs import TorchInferenceRPUConfig

        torch.manual_seed(0)
        weights = model["initializers"]
        per_candidate = []
        activations = {"input": INPUT}
        for candidate_id, weight_name, source_name in [
            ("dense1.matmul", "w1", "input"),
            ("dense2.matmul", "w2", "dense1.relu"),
        ]:
            torch.manual_seed(0)
            weight_in_out = weights[weight_name]["values"]
            input_vector = activations[source_name]
            layer = AnalogLinear(len(input_vector), len(weight_in_out[0]), bias=False, rpu_config=TorchInferenceRPUConfig())
            layer.set_weights(torch.tensor(transpose(weight_in_out), dtype=torch.float32))
            observed = [float(value) for value in layer(torch.tensor([input_vector], dtype=torch.float32)).detach().reshape(-1).tolist()]
            ideal = reference[candidate_id]
            per_candidate.append({
                "candidate_id": candidate_id,
                "weight_name": weight_name,
                "weight_shape_in_out": weights[weight_name]["shape"],
                "input": input_vector,
                "ideal_output": ideal,
                "simulator_output": observed,
                "simulator_residual_relative": relative_l2(ideal, observed),
            })
            if candidate_id == "dense1.matmul":
                activations["dense1.relu"] = relu(add(observed, weights["b1"]["values"]))
            else:
                activations["dense2.bias"] = add(observed, weights["b2"]["values"])
        body = payload("aihwkit", getattr(aihwkit, "__version__", "unknown"), per_candidate, activations["dense2.bias"], reference["dense2.bias"])
        body["provenance"]["artifacts"].append(str(AIHWKIT_OUT.relative_to(ROOT)))
        AIHWKIT_OUT.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        status = "wrote_payload" if body["accuracy_impact"]["pass"] else "wrote_payload_threshold_fail"
        reason = "AIHWKIT ran ONNX trained-weight replay"
        if status != "wrote_payload":
            reason += "; payload exceeds positive-claim residual threshold"
        return {"tool": "aihwkit", "status": status, "reason": reason, "payload": str(AIHWKIT_OUT.relative_to(ROOT))}
    except Exception as exc:
        return {"tool": "aihwkit", "status": "failed", "reason": str(exc), "payload": None}


def run_crosssim(model: dict[str, object], reference: dict[str, list[float]]) -> dict[str, object]:
    if not module_available("simulator"):
        return {"tool": "crosssim", "status": "skipped", "reason": "CrossSim simulator module is not importable", "payload": None}
    try:
        import numpy as np
        import simulator
        from simulator import AnalogCore, CrossSimParameters

        weights = model["initializers"]
        per_candidate = []
        activations = {"input": INPUT}
        for candidate_id, weight_name, source_name in [
            ("dense1.matmul", "w1", "input"),
            ("dense2.matmul", "w2", "dense1.relu"),
        ]:
            weight_in_out = weights[weight_name]["values"]
            input_vector = activations[source_name]
            core = AnalogCore(np.array(transpose(weight_in_out), dtype=float), params=CrossSimParameters())
            observed = [float(value) for value in (core @ np.array(input_vector, dtype=float)).tolist()]
            ideal = reference[candidate_id]
            per_candidate.append({
                "candidate_id": candidate_id,
                "weight_name": weight_name,
                "weight_shape_in_out": weights[weight_name]["shape"],
                "input": input_vector,
                "ideal_output": ideal,
                "simulator_output": observed,
                "simulator_residual_relative": relative_l2(ideal, observed),
            })
            if candidate_id == "dense1.matmul":
                activations["dense1.relu"] = relu(add(observed, weights["b1"]["values"]))
            else:
                activations["dense2.bias"] = add(observed, weights["b2"]["values"])
        body = payload("crosssim", getattr(simulator, "__version__", "unknown"), per_candidate, activations["dense2.bias"], reference["dense2.bias"])
        body["provenance"]["artifacts"].append(str(CROSSSIM_OUT.relative_to(ROOT)))
        CROSSSIM_OUT.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        status = "wrote_payload" if body["accuracy_impact"]["pass"] else "wrote_payload_threshold_fail"
        reason = "CrossSim ran ONNX trained-weight replay"
        if status != "wrote_payload":
            reason += "; payload exceeds positive-claim residual threshold"
        return {"tool": "crosssim", "status": status, "reason": reason, "payload": str(CROSSSIM_OUT.relative_to(ROOT))}
    except Exception as exc:
        return {"tool": "crosssim", "status": "failed", "reason": str(exc), "payload": None}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    model = extract_onnx()
    candidates = placement_candidates()
    if [row.get("operator_id") for row in candidates] != ["dense1.matmul", "dense2.matmul"]:
        raise SystemExit("backend placement analog MatMul candidates do not match tiny MLP trained-weight replay")
    reference = digital_reference(model["initializers"])
    results = [run_aihwkit(model, reference), run_crosssim(model, reference)]
    summary = {
        "result_type": "trained_weight_aimc_simulator_payload_run_summary",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_model": str(MODEL),
        "candidate_count": len(candidates),
        "candidate_ids": [row["operator_id"] for row in candidates],
        "results": results,
        "claim_boundary": {
            "allowed": "records simulator payload generation for the uploaded tiny MLP ONNX weights on backend analog MatMul candidates",
            "not_allowed": "does not prove full foundation-model accuracy, calibrated silicon, board runtime, board power, physical signoff, or production readiness",
        },
    }
    SUMMARY_OUT.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("trained_weight_aimc_simulator_payloads")
    for result in results:
        print(f"{result['tool']},{result['status']},{result['reason']}")
    print(f"candidates,{len(candidates)}")
    print(f"summary,{SUMMARY_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
