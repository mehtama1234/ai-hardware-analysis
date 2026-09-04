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
MODEL = OLD_ROOT / "samples" / "attention-block.onnx"
OUT_DIR = ROOT / "evidence" / "aimc-simulator-adapters"
SUMMARY_OUT = OUT_DIR / "attention-block-simulator-payload-run-summary.json"
AIHWKIT_OUT = OUT_DIR / "aihwkit-attention-block-analog-error-simulation.json"
CROSSSIM_OUT = OUT_DIR / "crosssim-attention-block-analog-error-simulation.json"
INPUT = [
    [0.10, -0.20, 0.30, -0.40, 0.50, -0.60, 0.70, -0.80],
    [-0.15, 0.25, -0.35, 0.45, -0.55, 0.65, -0.75, 0.85],
    [0.05, 0.15, -0.25, -0.35, 0.45, 0.55, -0.65, -0.75],
]


def module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def flatten(value):
    if not value:
        return []
    if isinstance(value[0], list):
        return [item for row in value for item in row]
    return value


def extract_onnx() -> dict[str, object]:
    code = r"""
import json
import onnx
from onnx import numpy_helper
from pathlib import Path
model = onnx.shape_inference.infer_shapes(onnx.load(Path(__import__("sys").argv[1])))
payload = {"nodes": [], "initializers": {}}
for node in model.graph.node:
    payload["nodes"].append({"name": node.name, "op_type": node.op_type, "inputs": list(node.input), "outputs": list(node.output)})
for init in model.graph.initializer:
    arr = numpy_helper.to_array(init)
    payload["initializers"][init.name] = {"shape": list(arr.shape), "values": arr.astype(float).tolist()}
print(json.dumps(payload))
"""
    result = subprocess.run([str(ONNX_PYTHON), "-c", code, str(MODEL)], text=True, capture_output=True, check=True)
    return json.loads(result.stdout)


def matmul(a, b):
    if not isinstance(a[0], list):
        a = [a]
    if not isinstance(b[0], list):
        b = [[value] for value in b]
    out = []
    for row in a:
        out.append([sum(row[idx] * b[idx][col] for idx in range(len(row))) for col in range(len(b[0]))])
    return out


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def softmax(matrix):
    out = []
    for row in matrix:
        m = max(row)
        exp = [math.exp(value - m) for value in row]
        denom = sum(exp)
        out.append([value / denom for value in exp])
    return out


def attention_from_projections(q, k, v, scale):
    scores_raw = matmul(q, transpose(k))
    scores = div(scores_raw, scale)
    weights = softmax(scores)
    return matmul(weights, v)


def div(left, right):
    scalar = right if isinstance(right, (int, float)) else right[0]
    return [[value / scalar for value in row] for row in left]


def relative_l2(reference, observed) -> float:
    ref = flatten(reference)
    obs = flatten(observed)
    diff = math.sqrt(sum((a - b) ** 2 for a, b in zip(ref, obs)))
    denom = math.sqrt(sum(a * a for a in ref))
    return diff / denom if denom else diff


def forward(model: dict[str, object], analog_outputs: dict[str, object] | None = None):
    tensors = {"input": INPUT}
    weights = model["initializers"]
    trace = []
    for node in model["nodes"]:
        name = node["name"]
        op = node["op_type"]
        inputs = node["inputs"]
        output = node["outputs"][0]
        if op == "MatMul":
            if analog_outputs and name in analog_outputs:
                result = analog_outputs[name]
            else:
                right = weights[inputs[1]]["values"] if inputs[1] in weights else tensors[inputs[1]]
                result = matmul(tensors[inputs[0]], right)
            tensors[output] = result
            if inputs[1] in weights:
                trace.append({
                    "candidate_id": name,
                    "weight_name": inputs[1],
                    "input_name": inputs[0],
                    "output_name": output,
                    "weight_shape_in_out": weights[inputs[1]]["shape"],
                    "input_shape": [len(tensors[inputs[0]]), len(tensors[inputs[0]][0])],
                    "ideal_output": matmul(tensors[inputs[0]], weights[inputs[1]]["values"]),
                })
        elif op == "Transpose":
            tensors[output] = transpose(tensors[inputs[0]])
        elif op == "Div":
            tensors[output] = div(tensors[inputs[0]], weights[inputs[1]]["values"])
        elif op == "Softmax":
            tensors[output] = softmax(tensors[inputs[0]])
        else:
            raise SystemExit(f"unsupported attention-block op: {op}")
    return tensors, trace


def attention_trace(model: dict[str, object]):
    weights = model["initializers"]
    q = matmul(INPUT, weights["w_q"]["values"])
    k = matmul(INPUT, weights["w_k"]["values"])
    v = matmul(INPUT, weights["w_v"]["values"])
    context = attention_from_projections(q, k, v, weights["scale"]["values"])
    output = matmul(context, weights["w_o"]["values"])
    return {
        "ideal_tensors": {
            "q": q,
            "k": k,
            "v": v,
            "context": context,
            "output": output,
        },
        "static_trace": [
            {
                "candidate_id": "attn.q.matmul",
                "weight_name": "w_q",
                "input_name": "input",
                "output_name": "q",
                "weight_shape_in_out": weights["w_q"]["shape"],
                "input_shape": [len(INPUT), len(INPUT[0])],
                "input_matrix": INPUT,
                "ideal_output": q,
            },
            {
                "candidate_id": "attn.k.matmul",
                "weight_name": "w_k",
                "input_name": "input",
                "output_name": "k",
                "weight_shape_in_out": weights["w_k"]["shape"],
                "input_shape": [len(INPUT), len(INPUT[0])],
                "input_matrix": INPUT,
                "ideal_output": k,
            },
            {
                "candidate_id": "attn.v.matmul",
                "weight_name": "w_v",
                "input_name": "input",
                "output_name": "v",
                "weight_shape_in_out": weights["w_v"]["shape"],
                "input_shape": [len(INPUT), len(INPUT[0])],
                "input_matrix": INPUT,
                "ideal_output": v,
            },
            {
                "candidate_id": "attn.out.matmul",
                "weight_name": "w_o",
                "input_name": "context",
                "output_name": "output",
                "weight_shape_in_out": weights["w_o"]["shape"],
                "input_shape": [len(context), len(context[0])],
                "input_matrix": context,
                "ideal_output": output,
            },
        ],
    }


def make_payload(tool: str, version: str, per_candidate, final_output, ideal_final):
    residual = max(relative_l2(ideal_final, final_output), max(float(item["simulator_residual_relative"]) for item in per_candidate))
    return {
        "result_type": "analog_simulator_adapter_output",
        "attention_block_run": True,
        "error_model": {
            "name": f"{tool}-attention-block-trained-weight-v0",
            "tool": f"{tool} attention-block trained-weight adapter run",
            "target_object": "attention-block.onnx static projection weights q, k, v, out",
            "adc_bits": 8,
            "dac_bits": 8,
            "final_residual_relative": residual,
            "final_residual_q8": int(round(residual * 128)),
            "device_assumptions": {
                "source": "external simulator replay using attention-block ONNX initializer weights",
                "programming_error": "measured as simulator output residual against digital projection matmul",
                "drift": "not swept in attention-block replay",
                "read_noise": "not independently swept in attention-block replay",
                "boundary": "static projection weights through simulator APIs, not calibrated silicon",
            },
            "array_assumptions": {
                "source": "attention-block.onnx initializers",
                "candidate_ids": [str(item["candidate_id"]) for item in per_candidate],
                "candidate_shapes": [str(item["weight_shape_in_out"]) for item in per_candidate],
                "digital_only_attention_ops": ["attn.scores.matmul", "attn.scale", "attn.softmax", "attn.value.matmul"],
                "boundary": "analog replay covers static projection weights only; dynamic score/value attention remains digital",
            },
            "per_candidate_results": per_candidate,
            "ideal_output": flatten(ideal_final),
            "simulator_observed_output": flatten(final_output),
            "simulator_residual_relative": relative_l2(ideal_final, final_output),
        },
        "temperature_range": {"mode": "fixed-condition", "ambient_c": 25.0, "boundary": "no temperature sweep"},
        "voltage_range": {"mode": "fixture-cases", "row_voltage_v": [0.8], "boundary": "no voltage sweep"},
        "accuracy_impact": {
            "estimated_drop": residual,
            "pass": residual <= 0.15,
            "metric": "relative_l2_output_difference_on_attention_block_trained_weight_replay",
            "baseline_reference": "digital ONNX-weight attention block",
            "simulated_reference": f"{tool} for static projection MatMul operators, digital arithmetic for dynamic attention",
            "boundary": "attention-shaped fixture only; not token accuracy, calibrated silicon, board runtime, measured power, or production readiness",
        },
        "calibration_profile": f"{tool}-attention-block-trained-weight-v0",
        "provenance": {
            "tool": f"{tool} attention-block trained-weight adapter run",
            "tool_version": version,
            "measurement_level": "external_simulator_attention_block_trained_weight_replay",
            "not_measured_silicon": True,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "repo": str(ROOT),
            "artifacts": [str(MODEL)],
            "claim_boundary": "strict simulator payload for static projection weights in an attention-shaped ONNX fixture; not pretrained foundation-model behavior, measured silicon, board runtime, measured power, physical signoff, or production readiness",
        },
    }


def run_aihwkit(model, ideal_tensors, trace):
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

        for item in trace[:3]:
            torch.manual_seed(0)
            weight = weights[item["weight_name"]]["values"]
            layer = AnalogLinear(len(weight), len(weight[0]), bias=False, rpu_config=TorchInferenceRPUConfig())
            layer.set_weights(torch.tensor(transpose(weight), dtype=torch.float32))
            observed = layer(torch.tensor(item["input_matrix"], dtype=torch.float32)).detach().tolist()
            analog_outputs[item["candidate_id"]] = observed
            row = dict(item)
            row.pop("input_matrix")
            row["simulator_output"] = flatten(observed)
            row["ideal_output"] = flatten(item["ideal_output"])
            row["simulator_residual_relative"] = relative_l2(item["ideal_output"], observed)
            per_candidate.append(row)

        context = attention_from_projections(analog_outputs["attn.q.matmul"], analog_outputs["attn.k.matmul"], analog_outputs["attn.v.matmul"], weights["scale"]["values"])
        out_item = dict(trace[3])
        out_item["input_matrix"] = context
        weight = weights[out_item["weight_name"]]["values"]
        torch.manual_seed(0)
        layer = AnalogLinear(len(weight), len(weight[0]), bias=False, rpu_config=TorchInferenceRPUConfig())
        layer.set_weights(torch.tensor(transpose(weight), dtype=torch.float32))
        final_output = layer(torch.tensor(context, dtype=torch.float32)).detach().tolist()
        out_row = dict(out_item)
        out_row.pop("input_matrix")
        out_row["simulator_output"] = flatten(final_output)
        out_row["ideal_output"] = flatten(trace[3]["ideal_output"])
        out_row["simulator_residual_relative"] = relative_l2(trace[3]["ideal_output"], final_output)
        per_candidate.append(out_row)

        body = make_payload("aihwkit", getattr(aihwkit, "__version__", "unknown"), per_candidate, final_output, ideal_tensors["output"])
        body["provenance"]["artifacts"].append(str(AIHWKIT_OUT.relative_to(ROOT)))
        AIHWKIT_OUT.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        status = "wrote_payload" if body["accuracy_impact"]["pass"] else "wrote_payload_threshold_fail"
        reason = "AIHWKIT ran attention-block ONNX trained-weight replay"
        if status != "wrote_payload":
            reason += "; payload exceeds positive-claim residual threshold"
        return {"tool": "aihwkit", "status": status, "reason": reason, "payload": str(AIHWKIT_OUT.relative_to(ROOT))}
    except Exception as exc:
        return {"tool": "aihwkit", "status": "failed", "reason": str(exc), "payload": None}


def run_crosssim(model, ideal_tensors, trace):
    if not module_available("simulator"):
        return {"tool": "crosssim", "status": "skipped", "reason": "CrossSim simulator module is not importable", "payload": None}
    try:
        import numpy as np
        import simulator
        from simulator import AnalogCore, CrossSimParameters

        weights = model["initializers"]
        analog_outputs = {}
        per_candidate = []

        for item in trace[:3]:
            weight = weights[item["weight_name"]]["values"]
            core = AnalogCore(np.array(transpose(weight), dtype=float), params=CrossSimParameters())
            observed = [(core @ np.array(row, dtype=float)).tolist() for row in item["input_matrix"]]
            analog_outputs[item["candidate_id"]] = observed
            row = dict(item)
            row.pop("input_matrix")
            row["simulator_output"] = flatten(observed)
            row["ideal_output"] = flatten(item["ideal_output"])
            row["simulator_residual_relative"] = relative_l2(item["ideal_output"], observed)
            per_candidate.append(row)

        context = attention_from_projections(analog_outputs["attn.q.matmul"], analog_outputs["attn.k.matmul"], analog_outputs["attn.v.matmul"], weights["scale"]["values"])
        out_item = dict(trace[3])
        out_item["input_matrix"] = context
        weight = weights[out_item["weight_name"]]["values"]
        core = AnalogCore(np.array(transpose(weight), dtype=float), params=CrossSimParameters())
        final_output = [(core @ np.array(row, dtype=float)).tolist() for row in context]
        out_row = dict(out_item)
        out_row.pop("input_matrix")
        out_row["simulator_output"] = flatten(final_output)
        out_row["ideal_output"] = flatten(trace[3]["ideal_output"])
        out_row["simulator_residual_relative"] = relative_l2(trace[3]["ideal_output"], final_output)
        per_candidate.append(out_row)

        body = make_payload("crosssim", getattr(simulator, "__version__", "unknown"), per_candidate, final_output, ideal_tensors["output"])
        body["provenance"]["artifacts"].append(str(CROSSSIM_OUT.relative_to(ROOT)))
        CROSSSIM_OUT.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        status = "wrote_payload" if body["accuracy_impact"]["pass"] else "wrote_payload_threshold_fail"
        reason = "CrossSim ran attention-block ONNX trained-weight replay"
        if status != "wrote_payload":
            reason += "; payload exceeds positive-claim residual threshold"
        return {"tool": "crosssim", "status": status, "reason": reason, "payload": str(CROSSSIM_OUT.relative_to(ROOT))}
    except Exception as exc:
        return {"tool": "crosssim", "status": "failed", "reason": str(exc), "payload": None}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    model = extract_onnx()
    replay = attention_trace(model)
    ideal = replay["ideal_tensors"]
    static_trace = replay["static_trace"]
    if len(static_trace) != 4:
        raise SystemExit(f"expected 4 static projection MatMul nodes, got {len(static_trace)}")
    results = [run_aihwkit(model, ideal, static_trace), run_crosssim(model, ideal, static_trace)]
    summary = {
        "result_type": "attention_block_aimc_simulator_payload_run_summary",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_model": str(MODEL),
        "candidate_count": len(static_trace),
        "candidate_ids": [item["candidate_id"] for item in static_trace],
        "digital_only_attention_ops": ["attn.scores.matmul", "attn.scale", "attn.softmax", "attn.value.matmul"],
        "results": results,
        "claim_boundary": {
            "allowed": "records simulator payload generation for static projection weights in an attention-shaped ONNX fixture",
            "not_allowed": "does not prove pretrained foundation-model accuracy, calibrated silicon, board runtime, board power, physical signoff, or production readiness",
        },
    }
    SUMMARY_OUT.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("attention_block_aimc_simulator_payloads")
    for result in results:
        print(f"{result['tool']},{result['status']},{result['reason']}")
    print(f"candidates,{len(static_trace)}")
    print(f"summary,{SUMMARY_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
