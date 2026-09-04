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
MODEL = OLD_ROOT / "samples" / "transformer-mlp-block.onnx"
MAKER = OLD_ROOT / "samples" / "make-transformer-mlp-block-onnx.py"
OUT_DIR = ROOT / "evidence" / "aimc-simulator-adapters"
SUMMARY_OUT = OUT_DIR / "transformer-mlp-block-simulator-payload-run-summary.json"
AIHWKIT_OUT = OUT_DIR / "aihwkit-transformer-mlp-block-analog-error-simulation.json"
CROSSSIM_OUT = OUT_DIR / "crosssim-transformer-mlp-block-analog-error-simulation.json"
INPUT = [0.08, -0.12, 0.16, -0.20, 0.24, -0.28, 0.32, -0.36, 0.40, -0.44, 0.48, -0.52, 0.56, -0.60, 0.64, -0.68]


def module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def ensure_model() -> None:
    if not MODEL.exists():
        subprocess.run([str(ONNX_PYTHON), str(MAKER)], check=True)


def extract_onnx() -> dict[str, object]:
    ensure_model()
    code = r"""
import json
import onnx
from onnx import numpy_helper
from pathlib import Path
model = onnx.shape_inference.infer_shapes(onnx.load(Path(__import__("sys").argv[1])))
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


def matvec(vector: list[float], weight_in_out: list[list[float]]) -> list[float]:
    return [sum(vector[row] * weight_in_out[row][col] for row in range(len(vector))) for col in range(len(weight_in_out[0]))]


def add(left: list[float], right: list[float]) -> list[float]:
    return [a + b for a, b in zip(left, right)]


def mul(left: list[float], right: list[float]) -> list[float]:
    return [a * b for a, b in zip(left, right)]


def relu(values: list[float]) -> list[float]:
    return [max(0.0, value) for value in values]


def transpose(weight_in_out: list[list[float]]) -> list[list[float]]:
    return [list(row) for row in zip(*weight_in_out)]


def relative_l2(reference: list[float], observed: list[float]) -> float:
    diff = math.sqrt(sum((a - b) ** 2 for a, b in zip(reference, observed)))
    denom = math.sqrt(sum(a * a for a in reference))
    return diff / denom if denom else diff


def digital_forward(model: dict[str, object], analog_outputs: dict[str, list[float]] | None = None) -> tuple[dict[str, list[float]], list[dict[str, object]]]:
    tensors: dict[str, list[float]] = {"input": INPUT}
    trace: list[dict[str, object]] = []
    weights = model["initializers"]
    for node in model["nodes"]:
        name = str(node["name"])
        op = node["op_type"]
        inputs = node["inputs"]
        output = node["outputs"][0]
        if op == "MatMul":
            source = tensors[inputs[0]]
            result = analog_outputs[name] if analog_outputs and name in analog_outputs else matvec(source, weights[inputs[1]]["values"])
            tensors[output] = result
            trace.append({
                "candidate_id": name,
                "weight_name": inputs[1],
                "input_name": inputs[0],
                "output_name": output,
                "weight_shape_in_out": weights[inputs[1]]["shape"],
                "input": source,
                "ideal_output": matvec(source, weights[inputs[1]]["values"]),
            })
        elif op == "Add":
            right = weights[inputs[1]]["values"] if inputs[1] in weights else tensors[inputs[1]]
            tensors[output] = add(tensors[inputs[0]], right)
        elif op == "Relu":
            tensors[output] = relu(tensors[inputs[0]])
        elif op == "Mul":
            tensors[output] = mul(tensors[inputs[0]], tensors[inputs[1]])
        else:
            raise SystemExit(f"unsupported transformer-mlp op: {op}")
    return tensors, trace


def make_payload(tool: str, version: str, per_candidate: list[dict[str, object]], final_output: list[float], ideal_final: list[float]) -> dict[str, object]:
    final_residual = relative_l2(ideal_final, final_output)
    residual = max(final_residual, max(float(item["simulator_residual_relative"]) for item in per_candidate))
    return {
        "result_type": "analog_simulator_adapter_output",
        "transformer_mlp_block_run": True,
        "error_model": {
            "name": f"{tool}-transformer-mlp-block-trained-weight-v0",
            "tool": f"{tool} transformer MLP block trained-weight adapter run",
            "target_object": "transformer-mlp-block.onnx fixed-weight MatMuls with digital nonlinear and residual operations",
            "adc_bits": 8,
            "dac_bits": 8,
            "final_residual_relative": residual,
            "final_residual_q8": int(round(residual * 128)),
            "device_assumptions": {
                "source": "external simulator replay using transformer-mlp-block ONNX initializer weights",
                "programming_error": "measured as simulator output residual against digital MatMul",
                "drift": "not swept in transformer MLP replay",
                "read_noise": "not independently swept in transformer MLP replay",
                "boundary": "real ONNX fixture weights through simulator APIs, not calibrated silicon",
            },
            "array_assumptions": {
                "source": "transformer-mlp-block.onnx initializers",
                "candidate_ids": [str(item["candidate_id"]) for item in per_candidate],
                "candidate_shapes": [str(item["weight_shape_in_out"]) for item in per_candidate],
                "digital_only_ops": ["bias Add", "Relu", "elementwise Mul", "residual Add"],
                "boundary": "larger transformer-MLP-shaped ONNX fixture; not a pretrained foundation model",
            },
            "per_candidate_results": per_candidate,
            "ideal_output": ideal_final,
            "simulator_observed_output": final_output,
            "simulator_residual_relative": final_residual,
        },
        "temperature_range": {"mode": "fixed-condition", "ambient_c": 25.0, "boundary": "no temperature sweep"},
        "voltage_range": {"mode": "fixture-cases", "row_voltage_v": [0.8], "boundary": "no voltage sweep"},
        "accuracy_impact": {
            "estimated_drop": residual,
            "pass": residual <= 0.15,
            "metric": "relative_l2_output_difference_on_transformer_mlp_block_replay",
            "baseline_reference": "digital ONNX-weight transformer MLP block",
            "simulated_reference": f"{tool} for fixed-weight MatMul operators, digital arithmetic for nonlinear and residual operators",
            "boundary": "transformer-MLP-shaped fixture only; not token accuracy, calibrated silicon, board runtime, measured power, or production readiness",
        },
        "calibration_profile": f"{tool}-transformer-mlp-block-trained-weight-v0",
        "provenance": {
            "tool": f"{tool} transformer MLP block trained-weight adapter run",
            "tool_version": version,
            "measurement_level": "external_simulator_transformer_mlp_block_trained_weight_replay",
            "not_measured_silicon": True,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "repo": str(ROOT),
            "artifacts": [str(MODEL)],
            "claim_boundary": "strict simulator payload for real ONNX fixture weights in a transformer-MLP-shaped block; not pretrained foundation-model behavior, measured silicon, board runtime, measured power, physical signoff, or production readiness",
        },
    }


def run_aihwkit(model: dict[str, object], ideal_tensors: dict[str, list[float]], trace: list[dict[str, object]]) -> dict[str, object]:
    if not module_available("aihwkit"):
        return {"tool": "aihwkit", "status": "skipped", "reason": "aihwkit is not importable", "payload": None}
    try:
        import torch
        import aihwkit
        from aihwkit.nn import AnalogLinear
        from aihwkit.simulator.configs import TorchInferenceRPUConfig

        weights = model["initializers"]
        analog_outputs = {}
        per_candidate = []
        for item in trace:
            torch.manual_seed(0)
            weight = weights[item["weight_name"]]["values"]
            layer = AnalogLinear(len(item["input"]), len(weight[0]), bias=False, rpu_config=TorchInferenceRPUConfig())
            layer.set_weights(torch.tensor(transpose(weight), dtype=torch.float32))
            observed = [float(value) for value in layer(torch.tensor([item["input"]], dtype=torch.float32)).detach().reshape(-1).tolist()]
            analog_outputs[item["candidate_id"]] = observed
            row = dict(item)
            row["simulator_output"] = observed
            row["simulator_residual_relative"] = relative_l2(item["ideal_output"], observed)
            per_candidate.append(row)
        simulated_tensors, _ = digital_forward(model, analog_outputs)
        body = make_payload("aihwkit", getattr(aihwkit, "__version__", "unknown"), per_candidate, simulated_tensors["output"], ideal_tensors["output"])
        body["provenance"]["artifacts"].append(str(AIHWKIT_OUT.relative_to(ROOT)))
        AIHWKIT_OUT.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        status = "wrote_payload" if body["accuracy_impact"]["pass"] else "wrote_payload_threshold_fail"
        reason = "AIHWKIT ran transformer-MLP ONNX trained-weight replay"
        if status != "wrote_payload":
            reason += "; payload exceeds positive-claim residual threshold"
        return {"tool": "aihwkit", "status": status, "reason": reason, "payload": str(AIHWKIT_OUT.relative_to(ROOT))}
    except Exception as exc:
        return {"tool": "aihwkit", "status": "failed", "reason": str(exc), "payload": None}


def run_crosssim(model: dict[str, object], ideal_tensors: dict[str, list[float]], trace: list[dict[str, object]]) -> dict[str, object]:
    if not module_available("simulator"):
        return {"tool": "crosssim", "status": "skipped", "reason": "CrossSim simulator module is not importable", "payload": None}
    try:
        import numpy as np
        import simulator
        from simulator import AnalogCore, CrossSimParameters

        weights = model["initializers"]
        analog_outputs = {}
        per_candidate = []
        for item in trace:
            weight = weights[item["weight_name"]]["values"]
            core = AnalogCore(np.array(transpose(weight), dtype=float), params=CrossSimParameters())
            observed = [float(value) for value in (core @ np.array(item["input"], dtype=float)).tolist()]
            analog_outputs[item["candidate_id"]] = observed
            row = dict(item)
            row["simulator_output"] = observed
            row["simulator_residual_relative"] = relative_l2(item["ideal_output"], observed)
            per_candidate.append(row)
        simulated_tensors, _ = digital_forward(model, analog_outputs)
        body = make_payload("crosssim", getattr(simulator, "__version__", "unknown"), per_candidate, simulated_tensors["output"], ideal_tensors["output"])
        body["provenance"]["artifacts"].append(str(CROSSSIM_OUT.relative_to(ROOT)))
        CROSSSIM_OUT.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        status = "wrote_payload" if body["accuracy_impact"]["pass"] else "wrote_payload_threshold_fail"
        reason = "CrossSim ran transformer-MLP ONNX trained-weight replay"
        if status != "wrote_payload":
            reason += "; payload exceeds positive-claim residual threshold"
        return {"tool": "crosssim", "status": status, "reason": reason, "payload": str(CROSSSIM_OUT.relative_to(ROOT))}
    except Exception as exc:
        return {"tool": "crosssim", "status": "failed", "reason": str(exc), "payload": None}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    model = extract_onnx()
    ideal_tensors, trace = digital_forward(model)
    if len(trace) != 4:
        raise SystemExit(f"expected 4 transformer MLP MatMul nodes, got {len(trace)}")
    results = [run_aihwkit(model, ideal_tensors, trace), run_crosssim(model, ideal_tensors, trace)]
    summary = {
        "result_type": "transformer_mlp_block_aimc_simulator_payload_run_summary",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_model": str(MODEL),
        "candidate_count": len(trace),
        "candidate_ids": [item["candidate_id"] for item in trace],
        "digital_only_ops": ["bias Add", "Relu", "elementwise Mul", "residual Add"],
        "results": results,
        "claim_boundary": {
            "allowed": "records simulator payload generation for a transformer-MLP-shaped ONNX fixture with real initializer weights",
            "not_allowed": "does not prove pretrained foundation-model accuracy, calibrated silicon, board runtime, board power, physical signoff, or production readiness",
        },
    }
    SUMMARY_OUT.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("transformer_mlp_block_aimc_simulator_payloads")
    for result in results:
        print(f"{result['tool']},{result['status']},{result['reason']}")
    print(f"candidates,{len(trace)}")
    print(f"summary,{SUMMARY_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
