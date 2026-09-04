#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import math
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OLD_ROOT = ROOT.parent / "analog-in-memory-ai-inference" / "software-architecture"
ONNX_PYTHON = OLD_ROOT / "backend" / ".venv" / "bin" / "python"
MODEL = OLD_ROOT / "samples" / "deep-transformer-mlp-stack.onnx"
MAKER = OLD_ROOT / "samples" / "make-deep-transformer-mlp-stack-onnx.py"
OUT_DIR = ROOT / "evidence" / "aimc-simulator-adapters"
SUMMARY_OUT = OUT_DIR / "calibrated-deep-transformer-mlp-stack-simulator-payload-run-summary.json"
AIHWKIT_OUT = OUT_DIR / "aihwkit-calibrated-deep-transformer-mlp-stack-analog-error-simulation.json"
CROSSSIM_OUT = OUT_DIR / "crosssim-calibrated-deep-transformer-mlp-stack-analog-error-simulation.json"
DIM = 32
INPUT = [math.sin((idx + 1) * 0.31) * 0.42 + math.cos((idx + 2) * 0.17) * 0.19 for idx in range(DIM)]
CALIBRATION_INPUTS = [
    [math.sin((idx + 1) * (case + 2) * 0.13) * 0.35 + math.cos((idx + 3) * (case + 1) * 0.07) * 0.21 for idx in range(DIM)]
    for case in range(7)
]


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


def digital_forward(model: dict[str, object], input_vector: list[float], analog_outputs: dict[str, list[float]] | None = None) -> tuple[dict[str, list[float]], list[dict[str, object]]]:
    tensors: dict[str, list[float]] = {"input": input_vector}
    trace: list[dict[str, object]] = []
    weights = model["initializers"]
    for node in model["nodes"]:
        name = str(node["name"])
        op = str(node["op_type"])
        inputs = list(node["inputs"])
        output = str(node["outputs"][0])
        if op == "MatMul":
            source = tensors[inputs[0]]
            ideal = matvec(source, weights[inputs[1]]["values"])
            tensors[output] = analog_outputs[name] if analog_outputs and name in analog_outputs else ideal
            trace.append(
                {
                    "candidate_id": name,
                    "weight_name": inputs[1],
                    "input_name": inputs[0],
                    "output_name": output,
                    "weight_shape_in_out": weights[inputs[1]]["shape"],
                    "input_shape": [len(source)],
                    "input": source,
                    "ideal_output": ideal,
                }
            )
        elif op == "Add":
            right = weights[inputs[1]]["values"] if inputs[1] in weights else tensors[inputs[1]]
            tensors[output] = add(tensors[inputs[0]], right)
        elif op == "Relu":
            tensors[output] = relu(tensors[inputs[0]])
        elif op == "Mul":
            tensors[output] = mul(tensors[inputs[0]], tensors[inputs[1]])
        else:
            raise SystemExit(f"unsupported deep transformer MLP op: {op}")
    return tensors, trace


def fit_affine(observed_cases: list[list[float]], ideal_cases: list[list[float]]) -> list[dict[str, float]]:
    columns = len(observed_cases[0])
    profile = []
    for col in range(columns):
        xs = [case[col] for case in observed_cases]
        ys = [case[col] for case in ideal_cases]
        x_mean = sum(xs) / len(xs)
        y_mean = sum(ys) / len(ys)
        var = sum((x - x_mean) ** 2 for x in xs)
        gain = 1.0 if var < 1e-12 else sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)) / var
        profile.append({"gain": gain, "offset": y_mean - gain * x_mean})
    return profile


def apply_affine(vector: list[float], profile: list[dict[str, float]]) -> list[float]:
    return [vector[idx] * profile[idx]["gain"] + profile[idx]["offset"] for idx in range(len(vector))]


def build_profiles(model: dict[str, object], raw) -> dict[str, list[dict[str, float]]]:
    observed_by_candidate: dict[str, list[list[float]]] = {}
    ideal_by_candidate: dict[str, list[list[float]]] = {}
    for case in CALIBRATION_INPUTS:
        _, trace = digital_forward(model, case)
        for item in trace:
            candidate_id = str(item["candidate_id"])
            weight_name = str(item["weight_name"])
            observed_by_candidate.setdefault(candidate_id, []).append(raw(weight_name, item["input"]))
            ideal_by_candidate.setdefault(candidate_id, []).append(item["ideal_output"])
    return {
        candidate_id: fit_affine(observed_by_candidate[candidate_id], ideal_by_candidate[candidate_id])
        for candidate_id in sorted(observed_by_candidate)
    }


def run_with_calibrated_matmuls(model: dict[str, object], raw, profiles: dict[str, list[dict[str, float]]]) -> tuple[dict[str, list[float]], list[dict[str, object]]]:
    _, digital_trace = digital_forward(model, INPUT)
    analog_outputs: dict[str, list[float]] = {}
    for item in digital_trace:
        analog_outputs[str(item["candidate_id"])] = apply_affine(raw(str(item["weight_name"]), item["input"]), profiles[str(item["candidate_id"])])
    return digital_forward(model, INPUT, analog_outputs)


def make_payload(tool: str, version: str, per_candidate: list[dict[str, object]], final_output: list[float], ideal_final: list[float]) -> dict[str, object]:
    final_residual = relative_l2(ideal_final, final_output)
    residual = max(final_residual, max(float(item["simulator_residual_relative"]) for item in per_candidate))
    return {
        "result_type": "analog_simulator_adapter_output",
        "calibrated_deep_transformer_mlp_stack_run": True,
        "error_model": {
            "name": f"{tool}-calibrated-deep-transformer-mlp-stack-v0",
            "tool": f"{tool} calibrated deep transformer MLP stack adapter run",
            "target_object": "deep-transformer-mlp-stack.onnx 12 fixed-weight MatMuls with digital nonlinear and residual operations",
            "adc_bits": 8,
            "dac_bits": 8,
            "final_residual_relative": residual,
            "final_residual_q8": int(round(residual * 128)),
            "device_assumptions": {
                "source": "external simulator replay plus per-output affine calibration",
                "programming_error": "estimated from calibration inputs and checked on a held-out replay input",
                "drift": "not swept after calibration",
                "read_noise": "not independently swept after calibration",
                "boundary": "software calibration of simulator outputs, not calibrated silicon",
            },
            "array_assumptions": {
                "source": "deep-transformer-mlp-stack.onnx initializers",
                "candidate_ids": [str(item["candidate_id"]) for item in per_candidate],
                "candidate_shapes": [str(item["weight_shape_in_out"]) for item in per_candidate],
                "digital_only_ops": ["bias Add", "Relu", "elementwise Mul", "residual Add"],
                "calibration_cases": len(CALIBRATION_INPUTS),
                "held_out_input": INPUT,
                "boundary": "three repeated MLP-style blocks; not a pretrained foundation model",
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
            "metric": "relative_l2_output_difference_on_calibrated_deep_transformer_mlp_stack_replay",
            "baseline_reference": "digital ONNX-weight deep transformer MLP stack",
            "simulated_reference": f"{tool} fixed-weight MatMul outputs after held-out affine calibration",
            "boundary": "deep MLP-stack fixture only; not token accuracy, calibrated silicon, board runtime, measured power, or production readiness",
        },
        "calibration_profile": f"{tool}-held-out-affine-deep-transformer-mlp-stack-v0",
        "provenance": {
            "tool": f"{tool} calibrated deep transformer MLP stack adapter run",
            "tool_version": version,
            "measurement_level": "external_simulator_calibrated_deep_transformer_mlp_stack_replay",
            "not_measured_silicon": True,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "repo": str(ROOT),
            "artifacts": [str(MODEL)],
            "claim_boundary": "strict simulator payload for calibrated fixed-weight MatMuls in a deeper transformer-MLP-style ONNX fixture; not pretrained foundation-model behavior, measured silicon, board runtime, measured power, physical signoff, or production readiness",
        },
    }


def run_tool(tool: str, version: str, raw, out_path: Path) -> dict[str, object]:
    model = extract_onnx()
    profiles = build_profiles(model, raw)
    ideal_tensors, _ = digital_forward(model, INPUT)
    simulated_tensors, trace = run_with_calibrated_matmuls(model, raw, profiles)
    per_candidate = []
    for item in trace:
        row = dict(item)
        row["simulator_output"] = simulated_tensors[str(item["output_name"])]
        row["simulator_residual_relative"] = relative_l2(item["ideal_output"], row["simulator_output"])
        row["calibration"] = {
            "mode": "per-output affine",
            "calibration_cases": len(CALIBRATION_INPUTS),
            "fit_target": "digital MatMul output",
        }
        per_candidate.append(row)
    body = make_payload(tool, version, per_candidate, simulated_tensors[str(model["nodes"][-1]["outputs"][0])], ideal_tensors[str(model["nodes"][-1]["outputs"][0])])
    body["provenance"]["artifacts"].append(str(out_path.relative_to(ROOT)))
    out_path.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    status = "wrote_payload" if body["accuracy_impact"]["pass"] else "wrote_payload_threshold_fail"
    reason = f"{tool} ran calibrated deep transformer-MLP stack replay"
    if status != "wrote_payload":
        reason += "; payload exceeds positive-claim residual threshold"
    return {"tool": tool, "status": status, "reason": reason, "payload": str(out_path.relative_to(ROOT))}


def run_aihwkit() -> dict[str, object]:
    if not module_available("aihwkit"):
        return {"tool": "aihwkit", "status": "skipped", "reason": "aihwkit is not importable", "payload": None}
    try:
        import aihwkit
        import torch
        from aihwkit.nn import AnalogLinear
        from aihwkit.simulator.configs import TorchInferenceRPUConfig

        model = extract_onnx()
        weights = model["initializers"]

        def raw(weight_name: str, input_vector: list[float]) -> list[float]:
            torch.manual_seed(0)
            weight = weights[weight_name]["values"]
            layer = AnalogLinear(len(input_vector), len(weight[0]), bias=False, rpu_config=TorchInferenceRPUConfig())
            layer.set_weights(torch.tensor(transpose(weight), dtype=torch.float32))
            return [float(value) for value in layer(torch.tensor([input_vector], dtype=torch.float32)).detach().reshape(-1).tolist()]

        return run_tool("aihwkit", getattr(aihwkit, "__version__", "unknown"), raw, AIHWKIT_OUT)
    except Exception as exc:
        return {"tool": "aihwkit", "status": "failed", "reason": str(exc), "payload": None}


def run_crosssim() -> dict[str, object]:
    if not module_available("simulator"):
        return {"tool": "crosssim", "status": "skipped", "reason": "CrossSim simulator module is not importable", "payload": None}
    try:
        import numpy as np
        import simulator
        from simulator import AnalogCore, CrossSimParameters

        model = extract_onnx()
        weights = model["initializers"]

        def raw(weight_name: str, input_vector: list[float]) -> list[float]:
            weight = weights[weight_name]["values"]
            core = AnalogCore(np.array(transpose(weight), dtype=float), params=CrossSimParameters())
            return [float(value) for value in (core @ np.array(input_vector, dtype=float)).tolist()]

        return run_tool("crosssim", getattr(simulator, "__version__", "unknown"), raw, CROSSSIM_OUT)
    except Exception as exc:
        return {"tool": "crosssim", "status": "failed", "reason": str(exc), "payload": None}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    model = extract_onnx()
    _, trace = digital_forward(model, INPUT)
    if len(trace) != 12:
        raise SystemExit(f"expected 12 deep transformer MLP MatMul nodes, got {len(trace)}")
    results = [run_aihwkit(), run_crosssim()]
    summary = {
        "result_type": "calibrated_deep_transformer_mlp_stack_aimc_simulator_payload_run_summary",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_model": str(MODEL),
        "candidate_count": len(trace),
        "candidate_ids": [str(item["candidate_id"]) for item in trace],
        "calibration": {
            "mode": "per-output affine",
            "calibration_cases": len(CALIBRATION_INPUTS),
            "held_out_input": INPUT,
        },
        "digital_only_ops": ["bias Add", "Relu", "elementwise Mul", "residual Add"],
        "results": results,
        "claim_boundary": {
            "allowed": "records calibrated simulator payload generation for 12 fixed-weight MatMuls in a three-block transformer-MLP-style ONNX fixture",
            "not_allowed": "does not prove pretrained foundation-model accuracy, calibrated silicon, board runtime, board power, physical signoff, or production readiness",
        },
    }
    SUMMARY_OUT.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("calibrated_deep_transformer_mlp_stack_aimc_simulator_payloads")
    for result in results:
        print(f"{result['tool']},{result['status']},{result['reason']}")
    print(f"candidates,{len(trace)}")
    print(f"summary,{SUMMARY_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
