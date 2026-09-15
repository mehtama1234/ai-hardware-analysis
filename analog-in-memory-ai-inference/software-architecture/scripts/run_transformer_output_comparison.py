#!/usr/bin/env python3
"""Replay a declared hybrid placement and compare it with a digital reference.

This is a deterministic software gate, not a silicon result. The digital
reference evaluates the original ONNX graph. The hybrid replay applies a
declared multiplicative weight-error model only to operators whose execution
contract says ``analog``. A physical gate can force those operators to the
digital fallback path, which should produce exact output parity.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import onnx
from onnx import numpy_helper
from onnx.reference import ReferenceEvaluator


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "backend") not in sys.path:
    sys.path.insert(0, str(ROOT / "backend"))

from build_transformer_execution_contract import build_contract  # noqa: E402


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def input_array(model: onnx.ModelProto, seed: int) -> np.ndarray:
    """Create a stable non-symmetric input for the static fixture shape."""
    value_info = model.graph.input[0]
    shape = [dim.dim_value for dim in value_info.type.tensor_type.shape.dim]
    if not shape or any(value <= 0 for value in shape):
        raise ValueError("comparison runner requires a fully static first input shape")
    values = np.linspace(-0.85, 0.95, num=int(np.prod(shape)), dtype=np.float32)
    rng = np.random.default_rng(seed)
    values += rng.normal(0.0, 0.013, size=values.shape).astype(np.float32)
    return values.reshape(shape)


def output_metrics(reference: np.ndarray, candidate: np.ndarray) -> dict[str, float | int]:
    ref = np.asarray(reference, dtype=np.float64).reshape(-1)
    got = np.asarray(candidate, dtype=np.float64).reshape(-1)
    delta = got - ref
    ref_norm = float(np.linalg.norm(ref))
    got_norm = float(np.linalg.norm(got))
    denominator = max(ref_norm, 1e-12)
    cosine = float(np.dot(ref, got) / max(ref_norm * got_norm, 1e-12))
    return {
        "element_count": int(ref.size),
        "max_absolute_error": float(np.max(np.abs(delta))),
        "rmse": float(np.sqrt(np.mean(delta * delta))),
        "relative_l2_error": float(np.linalg.norm(delta) / denominator),
        "cosine_similarity": cosine,
        "argmax_agreement": int(np.argmax(ref) == np.argmax(got)),
    }


def analog_node_ids(contract: dict[str, Any]) -> list[str]:
    return [
        row["operator_id"]
        for row in contract["operator_inventory"]["operators"]
        if row.get("placement") == "analog"
    ]


def perturb_analog_weights(
    model: onnx.ModelProto,
    node_ids: list[str],
    error_scale: float,
    seed: int,
) -> dict[str, Any]:
    """Apply a reproducible relative weight perturbation to fixed MatMul weights."""
    wanted = set(node_ids)
    initializers = {item.name: item for item in model.graph.initializer}
    rng = np.random.default_rng(seed)
    applied = []
    skipped = []
    for node in model.graph.node:
        if node.name not in wanted:
            continue
        if node.op_type not in {"MatMul", "Gemm"} or len(node.input) < 2:
            skipped.append({"operator_id": node.name, "reason": "not a fixed-weight matrix operator"})
            continue
        weight_name = node.input[1]
        initializer = initializers.get(weight_name)
        if initializer is None:
            skipped.append({"operator_id": node.name, "reason": "weight is not a graph initializer"})
            continue
        weights = numpy_helper.to_array(initializer).astype(np.float32)
        noise = rng.normal(0.0, error_scale, size=weights.shape).astype(np.float32)
        updated = weights * (1.0 + noise)
        initializer.CopyFrom(numpy_helper.from_array(updated, name=weight_name))
        applied.append(
            {
                "operator_id": node.name,
                "weight": weight_name,
                "shape": list(weights.shape),
                "relative_error_model": "independent_zero_mean_normal",
                "relative_error_scale": error_scale,
            }
        )
    return {"applied": applied, "skipped": skipped}


def evaluate(model: onnx.ModelProto, feed: dict[str, np.ndarray]) -> np.ndarray:
    outputs = ReferenceEvaluator(model).run(None, feed)
    if len(outputs) != 1:
        raise ValueError(f"comparison runner expects one output, got {len(outputs)}")
    return np.asarray(outputs[0])


def load_gate(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    gate = json.loads(path.read_text(encoding="utf-8"))
    if "analog_allowed_for_physical_claim" not in gate:
        gate["analog_allowed_for_physical_claim"] = bool(
            gate.get("ready_for_candidate_post_layout_payload", False)
        )
    gate["source_path"] = str(path)
    gate["imported_for_claim"] = True
    return gate


def run_comparison(
    model_path: Path,
    target_profile: str,
    calibration_profile: str,
    phase: str,
    error_scale: float,
    seed: int,
    physical_gate: dict[str, Any] | None,
    enforce_physical_gate: bool,
) -> dict[str, Any]:
    contract = build_contract(
        model_path,
        target_profile,
        calibration_profile,
        phase,
        physical_gate=physical_gate,
        enforce_physical_gate=enforce_physical_gate,
    )
    model = onnx.load(model_path)
    feed = {model.graph.input[0].name: input_array(model, seed)}
    reference = evaluate(model, feed)
    hybrid_model = copy.deepcopy(model)
    candidates = analog_node_ids(contract)
    perturbation = perturb_analog_weights(hybrid_model, candidates, error_scale, seed + 1)
    hybrid = evaluate(hybrid_model, feed)
    metrics = output_metrics(reference, hybrid)
    return {
        "schema_version": "transformer-output-comparison-v0.1",
        "result_type": "digital_reference_vs_declared_hybrid_replay",
        "provenance": {
            "model": model_path.name,
            "model_sha256": sha256(model_path),
            "target_profile": target_profile,
            "phase": phase,
            "calibration_profile": calibration_profile,
            "input_seed": seed,
            "weight_error_seed": seed + 1,
        },
        "contract": {
            "analog_candidate_count": len(candidates),
            "analog_candidate_operator_ids": candidates,
            "physical_gate_enforced": enforce_physical_gate,
            "physical_gate": physical_gate,
            "fallback_policy": contract["workload_contract"]["fallback_policy"],
        },
        "error_model": {
            "name": "fixed-weight_relative_gaussian_replay",
            "relative_error_scale": error_scale,
            "meaning": "software stress model for converter/device error; not a measured PVT distribution",
        },
        "weight_replay": perturbation,
        "outputs": {
            "reference_shape": list(reference.shape),
            "hybrid_shape": list(hybrid.shape),
            "reference_norm": float(np.linalg.norm(reference)),
            "hybrid_norm": float(np.linalg.norm(hybrid)),
        },
        "metrics": metrics,
        "acceptance": {
            "relative_l2_error_limit": 0.01,
            "argmax_agreement_required": True,
            "passed": bool(metrics["relative_l2_error"] <= 0.01 and metrics["argmax_agreement"] == 1),
            "interpretation": (
                "The declared hybrid replay stays within the software acceptance gate."
                if metrics["relative_l2_error"] <= 0.01 and metrics["argmax_agreement"] == 1
                else "The declared error model fails the software acceptance gate; use digital fallback or recalibrate."
            ),
        },
        "claim_boundary": {
            "allowed": "Deterministic output comparison for this ONNX fixture and declared synthetic error model.",
            "refused": "This is not a measured analog converter distribution, silicon result, or full language-model token-agreement result.",
            "next_gate": "Replace the synthetic error model with measured per-tile calibration and run held-out token-level decode tests.",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, default=ROOT / "samples" / "deep-transformer-mlp-stack.onnx")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--target-profile", default="robotics", choices=["wearable", "camera", "robotics"])
    parser.add_argument("--calibration-profile", default="sim-wearable-v0")
    parser.add_argument("--phase", default="prefill", choices=["prefill", "decode"])
    parser.add_argument("--error-scale", type=float, default=0.001)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--physical-gate", type=Path)
    parser.add_argument("--enforce-physical-gate", action="store_true")
    args = parser.parse_args()
    if not args.model.exists():
        raise SystemExit(f"model not found: {args.model}")
    if args.error_scale < 0:
        raise SystemExit("--error-scale must be non-negative")
    gate = load_gate(args.physical_gate)
    result = run_comparison(
        args.model,
        args.target_profile,
        args.calibration_profile,
        args.phase,
        args.error_scale,
        args.seed,
        gate,
        args.enforce_physical_gate,
    )
    args.output.mkdir(parents=True, exist_ok=True)
    output_path = args.output / "hybrid_output_comparison.json"
    output_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output_path), "metrics": result["metrics"], "passed": result["acceptance"]["passed"]}, indent=2))


if __name__ == "__main__":
    main()
