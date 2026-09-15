#!/usr/bin/env python3
"""Run a small attention decode loop with explicit K/V-cache accounting.

The fixture is intentionally not a language model: its output channels are
used as a deterministic proxy for token decisions. The artifact therefore
reports output-channel agreement, not tokenizer-level language agreement.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import onnx
from onnx import numpy_helper

from build_transformer_execution_contract import build_contract
from import_attention_calibration_profile import import_profile


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_gate(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    gate = json.loads(path.read_text(encoding="utf-8"))
    gate.setdefault("analog_allowed_for_physical_claim", bool(gate.get("ready_for_candidate_post_layout_payload", False)))
    gate["source_path"] = str(path)
    gate["imported_for_claim"] = True
    return gate


def weights(model: onnx.ModelProto) -> dict[str, np.ndarray]:
    return {item.name: numpy_helper.to_array(item).astype(np.float32) for item in model.graph.initializer}


def softmax(values: np.ndarray) -> np.ndarray:
    shifted = values - np.max(values)
    exponent = np.exp(shifted)
    return exponent / np.sum(exponent)


def calibrated_residuals(profile_path: Path, model_path: Path, candidate_ids: list[str]) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    """Extract only the declared held-out residual vectors from a matching profile."""
    imported = import_profile(model_path, profile_path)
    if not imported["acceptance"]["passed"]:
        raise ValueError("calibration profile rejected: " + "; ".join(imported["acceptance"]["errors"]))
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    residuals = {}
    for row in profile["error_model"]["per_candidate_results"]:
        if row["candidate_id"] not in candidate_ids:
            continue
        shape = row["input_shape"]
        ideal = np.asarray(row["ideal_output"], dtype=np.float32).reshape(shape)
        simulated = np.asarray(row["simulator_output"], dtype=np.float32).reshape(shape)
        residuals[row["candidate_id"]] = np.mean(simulated - ideal, axis=0)
    metadata = {
        "profile": str(profile_path),
        "profile_sha256": imported["provenance"]["source_profile_sha256"],
        "application": "mean additive residual vector from declared per-candidate held-out outputs",
        "claim_level": imported["provenance"]["measurement_level"],
        "import_acceptance": imported["acceptance"],
    }
    return residuals, metadata


def attention_step(
    token: np.ndarray,
    cache_k: list[np.ndarray],
    cache_v: list[np.ndarray],
    params: dict[str, np.ndarray],
    residuals: dict[str, np.ndarray] | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    residuals = residuals or {}
    q = token @ params["w_q"] + residuals.get("attn.q.matmul", 0.0)
    k = token @ params["w_k"] + residuals.get("attn.k.matmul", 0.0)
    v = token @ params["w_v"] + residuals.get("attn.v.matmul", 0.0)
    cache_k.append(k)
    cache_v.append(v)
    keys = np.stack(cache_k, axis=0)
    values = np.stack(cache_v, axis=0)
    scores = (keys @ q) / float(params["scale"].reshape(()))
    probabilities = softmax(scores)
    context = probabilities @ values
    output = context @ params["w_o"] + residuals.get("attn.out.matmul", 0.0)
    return output, k, v, probabilities


def token_metrics(reference: np.ndarray, candidate: np.ndarray) -> dict[str, float | int]:
    delta = candidate.astype(np.float64) - reference.astype(np.float64)
    denominator = max(float(np.linalg.norm(reference)), 1e-12)
    return {
        "relative_l2_error": float(np.linalg.norm(delta) / denominator),
        "max_absolute_error": float(np.max(np.abs(delta))),
        "output_channel_agreement": int(np.argmax(reference) == np.argmax(candidate)),
    }


def run_decode(
    model_path: Path,
    sequence_length: int,
    error_scale: float,
    seed: int,
    target_profile: str,
    calibration_profile: str,
    physical_gate: dict[str, Any] | None,
    enforce_physical_gate: bool,
    calibration_profile_path: Path | None = None,
) -> dict[str, Any]:
    if sequence_length < 1:
        raise ValueError("sequence length must be positive")
    model = onnx.load(model_path)
    base = weights(model)
    contract = build_contract(
        model_path,
        target_profile,
        calibration_profile,
        "decode",
        physical_gate=physical_gate,
        enforce_physical_gate=enforce_physical_gate,
    )
    candidates = [
        item["operator_id"]
        for item in contract["operator_inventory"]["operators"]
        if item.get("placement") == "analog"
    ]
    rng = np.random.default_rng(seed + 1)
    hybrid = {name: value.copy() for name, value in base.items()}
    weight_map = {
        "attn.q.matmul": "w_q",
        "attn.k.matmul": "w_k",
        "attn.v.matmul": "w_v",
        "attn.out.matmul": "w_o",
    }
    applied = []
    for operator_id in candidates:
        weight_name = weight_map.get(operator_id)
        if weight_name is None:
            continue
        noise = rng.normal(0.0, error_scale, size=hybrid[weight_name].shape).astype(np.float32)
        hybrid[weight_name] *= 1.0 + noise
        applied.append({"operator_id": operator_id, "weight": weight_name, "relative_error_scale": error_scale})

    calibration_residuals = {}
    calibration_metadata = None
    if calibration_profile_path is not None and candidates:
        calibration_residuals, calibration_metadata = calibrated_residuals(calibration_profile_path, model_path, candidates)
        for operator_id in sorted(calibration_residuals):
            applied.append({"operator_id": operator_id, "mode": "imported_calibrated_residual_vector"})

    inputs = np.linspace(-0.9, 0.9, sequence_length * 8, dtype=np.float32).reshape(sequence_length, 8)
    inputs += np.random.default_rng(seed).normal(0.0, 0.017, size=inputs.shape).astype(np.float32)
    base["scale"] = base["scale"]
    hybrid["scale"] = base["scale"]
    digital_k: list[np.ndarray] = []
    digital_v: list[np.ndarray] = []
    hybrid_k: list[np.ndarray] = []
    hybrid_v: list[np.ndarray] = []
    rows = []
    for index, token in enumerate(inputs):
        digital_output, _, _, digital_attention = attention_step(token, digital_k, digital_v, base)
        hybrid_output, _, _, hybrid_attention = attention_step(token, hybrid_k, hybrid_v, hybrid, calibration_residuals)
        metrics = token_metrics(digital_output, hybrid_output)
        dimension = int(token.size)
        bytes_per_value = 4
        cache_read_bytes = 2 * index * dimension * bytes_per_value
        cache_write_bytes = 2 * dimension * bytes_per_value
        projection_bytes = 4 * dimension * dimension * bytes_per_value
        rows.append(
            {
                "token_index": index,
                "cache_length_after_write": index + 1,
                "kv_cache_read_bytes": cache_read_bytes,
                "kv_cache_write_bytes": cache_write_bytes,
                "projection_weight_bytes_reused": projection_bytes,
                "dynamic_attention": "digital",
                "digital_attention_entropy": float(-np.sum(digital_attention * np.log(np.maximum(digital_attention, 1e-12)))),
                "hybrid_attention_entropy": float(-np.sum(hybrid_attention * np.log(np.maximum(hybrid_attention, 1e-12)))),
                "digital_output_norm": float(np.linalg.norm(digital_output)),
                "hybrid_output_norm": float(np.linalg.norm(hybrid_output)),
                **metrics,
            }
        )
    total_cache_read = sum(row["kv_cache_read_bytes"] for row in rows)
    total_cache_write = sum(row["kv_cache_write_bytes"] for row in rows)
    total_bytes = total_cache_read + total_cache_write
    mean_error = float(np.mean([row["relative_l2_error"] for row in rows]))
    max_error = float(max(row["relative_l2_error"] for row in rows))
    agreement = float(np.mean([row["output_channel_agreement"] for row in rows]))
    return {
        "schema_version": "transformer-token-decode-comparison-v0.1",
        "result_type": "attention_decode_with_explicit_kv_cache",
        "provenance": {
            "model": model_path.name,
            "model_sha256": sha256(model_path),
            "sequence_length": sequence_length,
            "input_seed": seed,
            "weight_error_seed": seed + 1,
            "target_profile": target_profile,
            "calibration_profile": calibration_profile,
        },
        "contract": {
            "analog_candidate_operator_ids": candidates,
            "analog_candidate_count": len(candidates),
            "dynamic_attention_policy": "digital",
            "kv_cache_policy": "digital_memory",
            "physical_gate_enforced": enforce_physical_gate,
            "physical_gate": physical_gate,
        },
        "error_model": {
            "name": "fixed_projection_relative_gaussian_replay",
            "relative_error_scale": error_scale,
            "meaning": "software stress model; not measured converter or device data",
        },
        "weight_replay": {"applied": applied},
        "calibration_replay": calibration_metadata or {"status": "not_imported"},
        "cache_and_movement": {
            "bytes_per_value": 4,
            "key_value_layout": "one key and one value vector per decoded token",
            "total_kv_cache_read_bytes": total_cache_read,
            "total_kv_cache_write_bytes": total_cache_write,
            "total_kv_cache_bytes_moved": total_bytes,
            "formula": "read at token t = 2*t*hidden_dim*bytes; write = 2*hidden_dim*bytes",
        },
        "token_trace": rows,
        "summary": {
            "mean_relative_l2_error": mean_error,
            "max_relative_l2_error": max_error,
            "output_channel_agreement_rate": agreement,
            "all_output_channels_agree": bool(agreement == 1.0),
        },
        "acceptance": {
            "relative_l2_error_limit": 0.01,
            "output_channel_agreement_required": True,
            "passed": bool(max_error <= 0.01 and agreement == 1.0),
        },
        "claim_boundary": {
            "allowed": "Six-token attention-fixture decode with explicit digital KV-cache movement and synthetic fixed-projection error replay.",
            "refused": "This is not tokenizer-level LLM token agreement, measured latency/energy, or silicon evidence.",
            "next_gate": "Connect the same cache and trace schema to a real small causal language model and measured per-tile calibration.",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, default=ROOT / "samples" / "attention-block.onnx")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sequence-length", type=int, default=6)
    parser.add_argument("--error-scale", type=float, default=0.001)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--target-profile", default="robotics", choices=["wearable", "camera", "robotics"])
    parser.add_argument("--calibration-profile", default="sim-wearable-v0")
    parser.add_argument("--physical-gate", type=Path)
    parser.add_argument("--enforce-physical-gate", action="store_true")
    parser.add_argument("--calibration-profile-json", type=Path, help="matching calibrated attention simulator profile")
    args = parser.parse_args()
    if not args.model.exists():
        raise SystemExit(f"model not found: {args.model}")
    if args.error_scale < 0:
        raise SystemExit("--error-scale must be non-negative")
    gate = load_gate(args.physical_gate)
    result = run_decode(
        args.model,
        args.sequence_length,
        args.error_scale,
        args.seed,
        args.target_profile,
        args.calibration_profile,
        gate,
        args.enforce_physical_gate,
        args.calibration_profile_json,
    )
    args.output.mkdir(parents=True, exist_ok=True)
    path = args.output / "transformer_decode_comparison.json"
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(path), "summary": result["summary"], "passed": result["acceptance"]["passed"]}, indent=2))


if __name__ == "__main__":
    main()
