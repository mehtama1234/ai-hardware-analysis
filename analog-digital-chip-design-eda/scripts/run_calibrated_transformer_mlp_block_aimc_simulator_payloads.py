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

from run_transformer_mlp_block_aimc_simulator_payloads import (  # noqa: E402
    AIHWKIT_OUT as RAW_AIHWKIT_OUT,
    CROSSSIM_OUT as RAW_CROSSSIM_OUT,
    INPUT,
    MODEL,
    OUT_DIR,
    add,
    digital_forward,
    extract_onnx,
    matvec,
    mul,
    relative_l2,
    relu,
    transpose,
)


SUMMARY_OUT = OUT_DIR / "calibrated-transformer-mlp-block-simulator-payload-run-summary.json"
AIHWKIT_OUT = OUT_DIR / "aihwkit-calibrated-transformer-mlp-block-analog-error-simulation.json"
CROSSSIM_OUT = OUT_DIR / "crosssim-calibrated-transformer-mlp-block-analog-error-simulation.json"

CALIBRATION_INPUTS = [
    [((idx + 1) % 7 - 3) / 9.0 for idx in range(16)],
    [math.sin((idx + 1) * 0.7) * 0.45 for idx in range(16)],
    [math.cos((idx + 2) * 0.5) * 0.38 for idx in range(16)],
    [((idx * 3) % 11 - 5) / 12.0 for idx in range(16)],
    [math.sin(idx + 1) * math.cos((idx + 1) / 3.0) * 0.42 for idx in range(16)],
]


def module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def fit_affine(observed_cases: list[list[float]], ideal_cases: list[list[float]]) -> list[dict[str, float]]:
    columns = len(observed_cases[0])
    profile = []
    for col in range(columns):
        xs = [case[col] for case in observed_cases]
        ys = [case[col] for case in ideal_cases]
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


def apply_affine(vector: list[float], profile: list[dict[str, float]]) -> list[float]:
    return [vector[idx] * profile[idx]["gain"] + profile[idx]["offset"] for idx in range(len(vector))]


def ideal_projection(weights: dict[str, object], input_vector: list[float], weight_name: str) -> list[float]:
    return matvec(input_vector, weights[weight_name]["values"])


def ideal_sources_for_case(weights: dict[str, object], input_vector: list[float]) -> dict[str, list[float]]:
    gate = relu(add(ideal_projection(weights, input_vector, "w_gate"), weights["b_gate"]["values"]))
    up = relu(add(ideal_projection(weights, input_vector, "w_up"), weights["b_up"]["values"]))
    mixed = mul(gate, up)
    down = add(ideal_projection(weights, mixed, "w_down"), weights["b_down"]["values"])
    residual = add(input_vector, down)
    return {
        "w_gate": input_vector,
        "w_up": input_vector,
        "w_down": mixed,
        "w_out": residual,
    }


def forward_with_calibrated_outputs(model: dict[str, object], raw, profiles: dict[str, list[dict[str, float]]]):
    weights = model["initializers"]
    gate_raw = raw("w_gate", INPUT)
    up_raw = raw("w_up", INPUT)
    gate = relu(add(apply_affine(gate_raw, profiles["w_gate"]), weights["b_gate"]["values"]))
    up = relu(add(apply_affine(up_raw, profiles["w_up"]), weights["b_up"]["values"]))
    mixed = mul(gate, up)
    down_raw = raw("w_down", mixed)
    down = add(apply_affine(down_raw, profiles["w_down"]), weights["b_down"]["values"])
    residual = add(INPUT, down)
    out_raw = raw("w_out", residual)
    output = add(apply_affine(out_raw, profiles["w_out"]), weights["b_out"]["values"])
    return {
        "mlp.gate.matmul": {"weight_name": "w_gate", "source": INPUT, "observed": apply_affine(gate_raw, profiles["w_gate"])},
        "mlp.up.matmul": {"weight_name": "w_up", "source": INPUT, "observed": apply_affine(up_raw, profiles["w_up"])},
        "mlp.down.matmul": {"weight_name": "w_down", "source": mixed, "observed": apply_affine(down_raw, profiles["w_down"])},
        "mlp.out.matmul": {"weight_name": "w_out", "source": residual, "observed": apply_affine(out_raw, profiles["w_out"])},
        "output": output,
    }


def make_payload(tool, version, model, per_candidate, final_output, ideal_final, calibration_summary):
    residual = max(relative_l2(ideal_final, final_output), max(float(item["simulator_residual_relative"]) for item in per_candidate))
    return {
        "result_type": "analog_simulator_adapter_output",
        "calibrated_transformer_mlp_block_run": True,
        "error_model": {
            "name": f"{tool}-calibrated-transformer-mlp-block-v0",
            "tool": f"{tool} calibrated transformer MLP block adapter run",
            "target_object": "transformer-mlp-block.onnx fixed-weight MatMuls with held-out affine calibration",
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
                "source": "transformer-mlp-block.onnx initializers",
                "candidate_ids": [str(item["candidate_id"]) for item in per_candidate],
                "candidate_shapes": [str(item["weight_shape_in_out"]) for item in per_candidate],
                "digital_only_ops": ["bias Add", "Relu", "elementwise Mul", "residual Add"],
                "calibration_summary": calibration_summary,
                "boundary": "calibration is learned from separate fixture inputs; nonlinear and residual operations remain digital",
            },
            "per_candidate_results": per_candidate,
            "ideal_output": ideal_final,
            "simulator_observed_output": final_output,
            "simulator_residual_relative": relative_l2(ideal_final, final_output),
        },
        "temperature_range": {"mode": "fixed-condition", "ambient_c": 25.0, "boundary": "no temperature sweep"},
        "voltage_range": {"mode": "fixture-cases", "row_voltage_v": [0.8], "boundary": "no voltage sweep"},
        "accuracy_impact": {
            "estimated_drop": residual,
            "pass": residual <= 0.15,
            "metric": "relative_l2_output_difference_on_calibrated_transformer_mlp_block_replay",
            "baseline_reference": "digital ONNX-weight transformer MLP block",
            "simulated_reference": f"{tool} fixed-weight MatMul outputs after held-out affine calibration",
            "boundary": "transformer-MLP-shaped fixture calibration only; not token accuracy, calibrated silicon, board runtime, measured power, or production readiness",
        },
        "calibration_profile": f"{tool}-held-out-affine-transformer-mlp-block-v0",
        "provenance": {
            "tool": f"{tool} calibrated transformer MLP block adapter run",
            "tool_version": version,
            "measurement_level": "external_simulator_calibrated_transformer_mlp_block_replay",
            "not_measured_silicon": True,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "repo": str(ROOT),
            "artifacts": [str(MODEL)],
            "claim_boundary": "strict simulator payload for calibrated fixed-weight MatMuls in a transformer-MLP-shaped ONNX fixture; not pretrained foundation-model behavior, measured silicon, board runtime, measured power, physical signoff, or production readiness",
        },
    }


def run_calibrated_tool(tool, version, model, raw, out_path, raw_path):
    weights = model["initializers"]
    profiles = {}
    for weight_name in ["w_gate", "w_up", "w_down", "w_out"]:
        observed_cases = []
        ideal_cases = []
        for case in CALIBRATION_INPUTS:
            source = ideal_sources_for_case(weights, case)[weight_name]
            observed_cases.append(raw(weight_name, source))
            ideal_cases.append(ideal_projection(weights, source, weight_name))
        profiles[weight_name] = fit_affine(observed_cases, ideal_cases)

    ideal_tensors, _ = digital_forward(model)
    replay = forward_with_calibrated_outputs(model, raw, profiles)
    per_candidate = []
    for candidate_id, item in replay.items():
        if candidate_id == "output":
            continue
        weight_name = item["weight_name"]
        source = item["source"]
        observed = item["observed"]
        ideal_output = ideal_projection(weights, source, weight_name)
        per_candidate.append({
            "candidate_id": candidate_id,
            "weight_name": weight_name,
            "weight_shape_in_out": weights[weight_name]["shape"],
            "input_shape": [len(source)],
            "ideal_output": ideal_output,
            "simulator_output": observed,
            "simulator_residual_relative": relative_l2(ideal_output, observed),
            "calibration": {
                "mode": "per-output affine",
                "calibration_cases": len(CALIBRATION_INPUTS),
                "fit_target": "digital MatMul output",
            },
        })
    calibration_summary = {
        "mode": "per-output affine",
        "calibration_cases": len(CALIBRATION_INPUTS),
        "held_out_input": INPUT,
        "raw_payload": str(raw_path.relative_to(ROOT)),
    }
    body = make_payload(tool, version, model, per_candidate, replay["output"], ideal_tensors["output"], calibration_summary)
    body["provenance"]["artifacts"].append(str(out_path.relative_to(ROOT)))
    out_path.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    status = "wrote_payload" if body["accuracy_impact"]["pass"] else "wrote_payload_threshold_fail"
    reason = f"{tool} ran calibrated transformer-MLP replay"
    if status != "wrote_payload":
        reason += "; payload exceeds positive-claim residual threshold"
    return {"tool": tool, "status": status, "reason": reason, "payload": str(out_path.relative_to(ROOT))}


def run_aihwkit(model):
    if not module_available("aihwkit"):
        return {"tool": "aihwkit", "status": "skipped", "reason": "aihwkit is not importable", "payload": None}
    try:
        import torch
        import aihwkit
        from aihwkit.nn import AnalogLinear
        from aihwkit.simulator.configs import TorchInferenceRPUConfig

        weights = model["initializers"]

        def raw(weight_name, input_vector):
            torch.manual_seed(0)
            weight = weights[weight_name]["values"]
            layer = AnalogLinear(len(input_vector), len(weight[0]), bias=False, rpu_config=TorchInferenceRPUConfig())
            layer.set_weights(torch.tensor(transpose(weight), dtype=torch.float32))
            return [float(value) for value in layer(torch.tensor([input_vector], dtype=torch.float32)).detach().reshape(-1).tolist()]

        return run_calibrated_tool("aihwkit", getattr(aihwkit, "__version__", "unknown"), model, raw, AIHWKIT_OUT, RAW_AIHWKIT_OUT)
    except Exception as exc:
        return {"tool": "aihwkit", "status": "failed", "reason": str(exc), "payload": None}


def run_crosssim(model):
    if not module_available("simulator"):
        return {"tool": "crosssim", "status": "skipped", "reason": "CrossSim simulator module is not importable", "payload": None}
    try:
        import numpy as np
        import simulator
        from simulator import AnalogCore, CrossSimParameters

        weights = model["initializers"]

        def raw(weight_name, input_vector):
            weight = weights[weight_name]["values"]
            core = AnalogCore(np.array(transpose(weight), dtype=float), params=CrossSimParameters())
            return [float(value) for value in (core @ np.array(input_vector, dtype=float)).tolist()]

        return run_calibrated_tool("crosssim", getattr(simulator, "__version__", "unknown"), model, raw, CROSSSIM_OUT, RAW_CROSSSIM_OUT)
    except Exception as exc:
        return {"tool": "crosssim", "status": "failed", "reason": str(exc), "payload": None}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    model = extract_onnx()
    results = [run_aihwkit(model), run_crosssim(model)]
    summary = {
        "result_type": "calibrated_transformer_mlp_block_aimc_simulator_payload_run_summary",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_model": str(MODEL),
        "candidate_count": 4,
        "candidate_ids": ["mlp.gate.matmul", "mlp.up.matmul", "mlp.down.matmul", "mlp.out.matmul"],
        "calibration": {
            "mode": "per-output affine",
            "calibration_cases": len(CALIBRATION_INPUTS),
            "held_out_input": INPUT,
        },
        "results": results,
        "claim_boundary": {
            "allowed": "records calibrated simulator payload generation for fixed-weight MatMuls in a transformer-MLP-shaped ONNX fixture",
            "not_allowed": "does not prove pretrained foundation-model accuracy, calibrated silicon, board runtime, board power, physical signoff, or production readiness",
        },
    }
    SUMMARY_OUT.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("calibrated_transformer_mlp_block_aimc_simulator_payloads")
    for result in results:
        print(f"{result['tool']},{result['status']},{result['reason']}")
    print("candidates,4")
    print(f"summary,{SUMMARY_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
