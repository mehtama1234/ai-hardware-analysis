#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from run_attention_block_aimc_simulator_payloads import (  # noqa: E402
    CROSSSIM_OUT as RAW_CROSSSIM_OUT,
    AIHWKIT_OUT as RAW_AIHWKIT_OUT,
    INPUT,
    MODEL,
    OUT_DIR,
    attention_from_projections,
    attention_trace,
    extract_onnx,
    flatten,
    matmul,
    relative_l2,
    transpose,
)


SUMMARY_OUT = OUT_DIR / "calibrated-attention-block-simulator-payload-run-summary.json"
AIHWKIT_OUT = OUT_DIR / "aihwkit-calibrated-attention-block-analog-error-simulation.json"
CROSSSIM_OUT = OUT_DIR / "crosssim-calibrated-attention-block-analog-error-simulation.json"

CALIBRATION_INPUTS = [
    [[((row + 1) * (col + 2) % 7 - 3) / 10.0 for col in range(8)] for row in range(3)],
    [[math.sin((row + 1) * (col + 1)) * 0.4 for col in range(8)] for row in range(3)],
    [[math.cos((row + 2) + (col + 1)) * 0.35 for col in range(8)] for row in range(3)],
    [[((row - col) % 5 - 2) / 8.0 for col in range(8)] for row in range(3)],
]


def module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def fit_affine(observed_cases, ideal_cases):
    columns = len(observed_cases[0][0])
    profile = []
    for col in range(columns):
        xs = [row[col] for case in observed_cases for row in case]
        ys = [row[col] for case in ideal_cases for row in case]
        x_mean = sum(xs) / len(xs)
        y_mean = sum(ys) / len(ys)
        var = sum((x - x_mean) ** 2 for x in xs)
        if var < 1e-12:
            gain = 1.0
        else:
            gain = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)) / var
        offset = y_mean - gain * x_mean
        profile.append({"gain": gain, "offset": offset})
    return profile


def apply_affine(matrix, profile):
    return [[row[col] * profile[col]["gain"] + profile[col]["offset"] for col in range(len(row))] for row in matrix]


def ideal_projection(weights, input_matrix, weight_name):
    return matmul(input_matrix, weights[weight_name]["values"])


def make_payload(tool, version, per_candidate, final_output, ideal_final, calibration_summary):
    residual = max(relative_l2(ideal_final, final_output), max(float(item["simulator_residual_relative"]) for item in per_candidate))
    return {
        "result_type": "analog_simulator_adapter_output",
        "calibrated_attention_block_run": True,
        "error_model": {
            "name": f"{tool}-calibrated-attention-block-v0",
            "tool": f"{tool} calibrated attention-block adapter run",
            "target_object": "attention-block.onnx static projection weights with held-out affine calibration",
            "adc_bits": 8,
            "dac_bits": 8,
            "final_residual_relative": residual,
            "final_residual_q8": int(round(residual * 128)),
            "device_assumptions": {
                "source": "external simulator replay plus held-out per-output affine calibration",
                "programming_error": "estimated from calibration inputs and checked on separate replay input",
                "drift": "not swept after calibration",
                "read_noise": "not independently swept after calibration",
                "boundary": "software calibration of simulator outputs, not calibrated silicon",
            },
            "array_assumptions": {
                "source": "attention-block.onnx initializers",
                "candidate_ids": [str(item["candidate_id"]) for item in per_candidate],
                "candidate_shapes": [str(item["weight_shape_in_out"]) for item in per_candidate],
                "digital_only_attention_ops": ["attn.scores.matmul", "attn.scale", "attn.softmax", "attn.value.matmul"],
                "calibration_summary": calibration_summary,
                "boundary": "calibration is learned from separate fixture inputs; static projections are corrected, dynamic attention remains digital",
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
            "metric": "relative_l2_output_difference_on_calibrated_attention_block_replay",
            "baseline_reference": "digital ONNX-weight attention block",
            "simulated_reference": f"{tool} static projection MatMul outputs after held-out affine calibration",
            "boundary": "attention-shaped fixture calibration only; not token accuracy, calibrated silicon, board runtime, measured power, or production readiness",
        },
        "calibration_profile": f"{tool}-held-out-affine-attention-block-v0",
        "provenance": {
            "tool": f"{tool} calibrated attention-block adapter run",
            "tool_version": version,
            "measurement_level": "external_simulator_calibrated_attention_block_replay",
            "not_measured_silicon": True,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "repo": str(ROOT),
            "artifacts": [str(MODEL)],
            "claim_boundary": "strict simulator payload for calibrated static projection weights in an attention-shaped ONNX fixture; not pretrained foundation-model behavior, measured silicon, board runtime, measured power, physical signoff, or production readiness",
        },
    }


def run_aihwkit(model, ideal):
    if not module_available("aihwkit"):
        return {"tool": "aihwkit", "status": "skipped", "reason": "aihwkit is not importable", "payload": None}
    try:
        import torch
        import aihwkit
        from aihwkit.nn import AnalogLinear
        from aihwkit.simulator.configs import TorchInferenceRPUConfig

        weights = model["initializers"]

        def raw(weight_name, input_matrix):
            torch.manual_seed(0)
            weight = weights[weight_name]["values"]
            layer = AnalogLinear(len(weight), len(weight[0]), bias=False, rpu_config=TorchInferenceRPUConfig())
            layer.set_weights(torch.tensor(transpose(weight), dtype=torch.float32))
            return layer(torch.tensor(input_matrix, dtype=torch.float32)).detach().tolist()

        return run_calibrated_tool("aihwkit", getattr(aihwkit, "__version__", "unknown"), model, ideal, raw, AIHWKIT_OUT, RAW_AIHWKIT_OUT)
    except Exception as exc:
        return {"tool": "aihwkit", "status": "failed", "reason": str(exc), "payload": None}


def run_crosssim(model, ideal):
    if not module_available("simulator"):
        return {"tool": "crosssim", "status": "skipped", "reason": "CrossSim simulator module is not importable", "payload": None}
    try:
        import numpy as np
        import simulator
        from simulator import AnalogCore, CrossSimParameters

        weights = model["initializers"]

        def raw(weight_name, input_matrix):
            weight = weights[weight_name]["values"]
            core = AnalogCore(np.array(transpose(weight), dtype=float), params=CrossSimParameters())
            return [(core @ np.array(row, dtype=float)).tolist() for row in input_matrix]

        return run_calibrated_tool("crosssim", getattr(simulator, "__version__", "unknown"), model, ideal, raw, CROSSSIM_OUT, RAW_CROSSSIM_OUT)
    except Exception as exc:
        return {"tool": "crosssim", "status": "failed", "reason": str(exc), "payload": None}


def run_calibrated_tool(tool, version, model, ideal, raw, out_path, raw_path):
    weights = model["initializers"]
    profiles = {}
    for weight_name in ["w_q", "w_k", "w_v", "w_o"]:
        observed_cases = []
        ideal_cases = []
        for case in CALIBRATION_INPUTS:
            if weight_name == "w_o":
                q = ideal_projection(weights, case, "w_q")
                k = ideal_projection(weights, case, "w_k")
                v = ideal_projection(weights, case, "w_v")
                source = attention_from_projections(q, k, v, weights["scale"]["values"])
            else:
                source = case
            observed_cases.append(raw(weight_name, source))
            ideal_cases.append(ideal_projection(weights, source, weight_name))
        profiles[weight_name] = fit_affine(observed_cases, ideal_cases)

    q_raw = raw("w_q", INPUT)
    k_raw = raw("w_k", INPUT)
    v_raw = raw("w_v", INPUT)
    q = apply_affine(q_raw, profiles["w_q"])
    k = apply_affine(k_raw, profiles["w_k"])
    v = apply_affine(v_raw, profiles["w_v"])
    context = attention_from_projections(q, k, v, weights["scale"]["values"])
    out_raw = raw("w_o", context)
    output = apply_affine(out_raw, profiles["w_o"])

    mapping = [
        ("attn.q.matmul", "w_q", INPUT, ideal["q"], q),
        ("attn.k.matmul", "w_k", INPUT, ideal["k"], k),
        ("attn.v.matmul", "w_v", INPUT, ideal["v"], v),
        ("attn.out.matmul", "w_o", context, ideal["output"], output),
    ]
    per_candidate = []
    for candidate_id, weight_name, source, ideal_output, observed in mapping:
        per_candidate.append({
            "candidate_id": candidate_id,
            "weight_name": weight_name,
            "weight_shape_in_out": weights[weight_name]["shape"],
            "input_shape": [len(source), len(source[0])],
            "ideal_output": flatten(ideal_output),
            "simulator_output": flatten(observed),
            "simulator_residual_relative": relative_l2(ideal_output, observed),
            "calibration": {
                "mode": "per-output affine",
                "calibration_cases": len(CALIBRATION_INPUTS),
                "fit_target": "digital projection output",
            },
        })
    calibration_summary = {
        "mode": "per-output affine",
        "calibration_cases": len(CALIBRATION_INPUTS),
        "held_out_input": INPUT,
        "raw_payload": str(raw_path.relative_to(ROOT)),
    }
    body = make_payload(tool, version, per_candidate, output, ideal["output"], calibration_summary)
    body["provenance"]["artifacts"].append(str(out_path.relative_to(ROOT)))
    out_path.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    status = "wrote_payload" if body["accuracy_impact"]["pass"] else "wrote_payload_threshold_fail"
    reason = f"{tool} ran calibrated attention-block replay"
    if status != "wrote_payload":
        reason += "; payload exceeds positive-claim residual threshold"
    return {"tool": tool, "status": status, "reason": reason, "payload": str(out_path.relative_to(ROOT))}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    model = extract_onnx()
    replay = attention_trace(model)
    ideal = replay["ideal_tensors"]
    results = [run_aihwkit(model, ideal), run_crosssim(model, ideal)]
    summary = {
        "result_type": "calibrated_attention_block_aimc_simulator_payload_run_summary",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_model": str(MODEL),
        "candidate_count": 4,
        "candidate_ids": ["attn.q.matmul", "attn.k.matmul", "attn.v.matmul", "attn.out.matmul"],
        "calibration": {
            "mode": "per-output affine",
            "calibration_cases": len(CALIBRATION_INPUTS),
            "held_out_input": INPUT,
        },
        "results": results,
        "claim_boundary": {
            "allowed": "records calibrated simulator payload generation for static projection weights in an attention-shaped ONNX fixture",
            "not_allowed": "does not prove pretrained foundation-model accuracy, calibrated silicon, board runtime, board power, physical signoff, or production readiness",
        },
    }
    SUMMARY_OUT.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("calibrated_attention_block_aimc_simulator_payloads")
    for result in results:
        print(f"{result['tool']},{result['status']},{result['reason']}")
    print("candidates,4")
    print(f"summary,{SUMMARY_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
