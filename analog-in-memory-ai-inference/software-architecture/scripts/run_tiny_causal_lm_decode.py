#!/usr/bin/env python3
"""Run tokenizer-like next-token comparison on the tiny causal LM fixture."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import onnx
from onnx import numpy_helper
from onnx.reference import ReferenceEvaluator

from build_transformer_execution_contract import build_contract


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


def load_weights(model: onnx.ModelProto) -> dict[str, np.ndarray]:
    return {item.name: numpy_helper.to_array(item).astype(np.float32) for item in model.graph.initializer}


def softmax(values: np.ndarray) -> np.ndarray:
    shifted = values - np.max(values)
    exp_values = np.exp(shifted)
    return exp_values / np.sum(exp_values)


def step(
    token_id: int,
    cache_k: list[np.ndarray],
    cache_v: list[np.ndarray],
    params: dict[str, np.ndarray],
) -> tuple[np.ndarray, np.ndarray]:
    embedding = params["embedding"][token_id]
    q = embedding @ params["w_q"]
    k = embedding @ params["w_k"]
    v = embedding @ params["w_v"]
    cache_k.append(k)
    cache_v.append(v)
    keys = np.stack(cache_k, axis=0)
    values = np.stack(cache_v, axis=0)
    scores = (keys @ q) / float(params["scale"].reshape(()))
    weights = softmax(scores)
    context = weights @ values
    attention_output = context @ params["w_o"]
    hidden = embedding + attention_output
    logits = hidden @ params["lm_head"] + params["lm_bias"]
    return logits, weights


def apply_error_model(
    base: dict[str, np.ndarray],
    candidate_ids: list[str],
    scale: float,
    seed: int,
) -> tuple[dict[str, np.ndarray], list[dict[str, Any]]]:
    result = {name: value.copy() for name, value in base.items()}
    mapping = {
        "attn.q.matmul": "w_q",
        "attn.k.matmul": "w_k",
        "attn.v.matmul": "w_v",
        "attn.out.matmul": "w_o",
        "lm_head.matmul": "lm_head",
    }
    rng = np.random.default_rng(seed)
    applied = []
    for operator_id in candidate_ids:
        weight_name = mapping.get(operator_id)
        if weight_name is None:
            continue
        noise = rng.normal(0.0, scale, size=result[weight_name].shape).astype(np.float32)
        result[weight_name] *= 1.0 + noise
        applied.append({"operator_id": operator_id, "weight": weight_name, "relative_error_scale": scale})
    return result, applied


def logits_metrics(reference: np.ndarray, candidate: np.ndarray) -> dict[str, float | int]:
    delta = candidate.astype(np.float64) - reference.astype(np.float64)
    denominator = max(float(np.linalg.norm(reference)), 1e-12)
    return {
        "relative_l2_error": float(np.linalg.norm(delta) / denominator),
        "max_absolute_error": float(np.max(np.abs(delta))),
        "next_token_agreement": int(np.argmax(reference) == np.argmax(candidate)),
    }


def teacher_forced_trace(token_ids: list[int], digital: dict[str, np.ndarray], hybrid: dict[str, np.ndarray]) -> list[dict[str, Any]]:
    digital_k: list[np.ndarray] = []
    digital_v: list[np.ndarray] = []
    hybrid_k: list[np.ndarray] = []
    hybrid_v: list[np.ndarray] = []
    rows = []
    for index, token_id in enumerate(token_ids[:-1]):
        digital_logits, digital_attention = step(token_id, digital_k, digital_v, digital)
        hybrid_logits, hybrid_attention = step(token_id, hybrid_k, hybrid_v, hybrid)
        metrics = logits_metrics(digital_logits, hybrid_logits)
        rows.append(
            {
                "step": index,
                "input_token_id": token_id,
                "target_next_token_id": token_ids[index + 1],
                "digital_next_token_id": int(np.argmax(digital_logits)),
                "hybrid_next_token_id": int(np.argmax(hybrid_logits)),
                "cache_length": index + 1,
                "attention_entropy": float(-np.sum(digital_attention * np.log(np.maximum(digital_attention, 1e-12)))),
                **metrics,
            }
        )
    return rows


def free_running_trace(prompt: list[int], steps: int, digital: dict[str, np.ndarray], hybrid: dict[str, np.ndarray]) -> dict[str, Any]:
    digital_k: list[np.ndarray] = []
    digital_v: list[np.ndarray] = []
    hybrid_k: list[np.ndarray] = []
    hybrid_v: list[np.ndarray] = []
    for token_id in prompt:
        step(token_id, digital_k, digital_v, digital)
        step(token_id, hybrid_k, hybrid_v, hybrid)
    digital_tokens = []
    hybrid_tokens = []
    digital_input = prompt[-1]
    hybrid_input = prompt[-1]
    for index in range(steps):
        digital_logits, _ = step(digital_input, digital_k, digital_v, digital)
        hybrid_logits, _ = step(hybrid_input, hybrid_k, hybrid_v, hybrid)
        digital_next = int(np.argmax(digital_logits))
        hybrid_next = int(np.argmax(hybrid_logits))
        digital_tokens.append(digital_next)
        hybrid_tokens.append(hybrid_next)
        digital_input = digital_next
        hybrid_input = hybrid_next
    return {
        "prompt_token_ids": prompt,
        "digital_generated_token_ids": digital_tokens,
        "hybrid_generated_token_ids": hybrid_tokens,
        "exact_sequence_agreement": int(digital_tokens == hybrid_tokens),
        "generated_token_agreement_rate": float(np.mean(np.array(digital_tokens) == np.array(hybrid_tokens))),
    }


def run(
    model_path: Path,
    prompt: list[int],
    generated_steps: int,
    error_scale: float,
    seed: int,
    target_profile: str,
    calibration_profile: str,
    physical_gate: dict[str, Any] | None,
    enforce_physical_gate: bool,
) -> dict[str, Any]:
    model = onnx.load(model_path)
    base = load_weights(model)
    contract = build_contract(model_path, target_profile, calibration_profile, "decode", physical_gate, enforce_physical_gate)
    candidates = [
        row["operator_id"]
        for row in contract["operator_inventory"]["operators"]
        if row.get("placement") == "analog"
    ]
    hybrid, applied = apply_error_model(base, candidates, error_scale, seed + 1)
    vocabulary_size = int(base["embedding"].shape[0])
    if any(token < 0 or token >= vocabulary_size for token in prompt):
        raise ValueError(f"prompt token IDs must be in [0, {vocabulary_size})")
    if len(prompt) + generated_steps > 6:
        raise ValueError("fixture context length is 6; reduce prompt or generated steps")
    teacher_tokens = prompt[:]
    # Build the teacher-forced target sequence from the digital path first.
    digital_k: list[np.ndarray] = []
    digital_v: list[np.ndarray] = []
    for token_id in prompt:
        digital_logits, _ = step(token_id, digital_k, digital_v, base)
    for _ in range(generated_steps):
        next_token = int(np.argmax(digital_logits))
        teacher_tokens.append(next_token)
        digital_logits, _ = step(next_token, digital_k, digital_v, base)
    teacher = teacher_forced_trace(teacher_tokens, base, hybrid)
    reference_logits = ReferenceEvaluator(model).run(
        None, {"token_ids": np.asarray(teacher_tokens, dtype=np.int64)}
    )[0]
    prefill_k: list[np.ndarray] = []
    prefill_v: list[np.ndarray] = []
    manual_prefill = []
    for token_id in teacher_tokens:
        logits, _ = step(token_id, prefill_k, prefill_v, base)
        manual_prefill.append(logits)
    manual_prefill_array = np.stack(manual_prefill, axis=0)
    prefill_delta = manual_prefill_array.astype(np.float64) - np.asarray(reference_logits, dtype=np.float64)
    prefill_reference_max_error = float(np.max(np.abs(prefill_delta)))
    prefill_reference_relative_error = float(
        np.linalg.norm(prefill_delta) / max(float(np.linalg.norm(reference_logits)), 1e-12)
    )
    free = free_running_trace(prompt, generated_steps, base, hybrid)
    cache_dim = int(base["w_k"].shape[1])
    bytes_per_value = 4
    total_steps = len(prompt) + generated_steps
    cache_read = sum(2 * index * cache_dim * bytes_per_value for index in range(total_steps))
    cache_write = sum(2 * cache_dim * bytes_per_value for _ in range(total_steps))
    return {
        "schema_version": "tiny-causal-lm-token-decode-v0.1",
        "result_type": "token_level_causal_decode_comparison",
        "provenance": {
            "model": model_path.name,
            "model_sha256": sha256(model_path),
            "vocabulary_size": vocabulary_size,
            "hidden_dimension": cache_dim,
            "prompt_token_ids": prompt,
            "generated_steps": generated_steps,
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
        "cache_and_movement": {
            "bytes_per_value": bytes_per_value,
            "total_tokens_processed": total_steps,
            "total_kv_cache_read_bytes": cache_read,
            "total_kv_cache_write_bytes": cache_write,
            "total_kv_cache_bytes_moved": cache_read + cache_write,
            "formula": "read at token t = 2*t*hidden_dim*bytes; write = 2*hidden_dim*bytes",
        },
        "teacher_forced_trace": teacher,
        "prefill_reference_parity": {
            "reference": "ONNX ReferenceEvaluator full causal graph",
            "manual_decode": "same weights with explicit per-token K/V cache",
            "max_absolute_error": prefill_reference_max_error,
            "relative_l2_error": prefill_reference_relative_error,
            "passed": bool(prefill_reference_relative_error <= 1e-5),
        },
        "free_running_trace": free,
        "summary": {
            "teacher_forced_steps": len(teacher),
            "teacher_forced_next_token_agreement_rate": float(np.mean([row["next_token_agreement"] for row in teacher])),
            "teacher_forced_max_relative_l2_error": float(max(row["relative_l2_error"] for row in teacher)),
            "free_running_generated_token_agreement_rate": free["generated_token_agreement_rate"],
            "free_running_exact_sequence_agreement": free["exact_sequence_agreement"],
            "prefill_reference_relative_l2_error": prefill_reference_relative_error,
        },
        "acceptance": {
            "relative_l2_error_limit": 0.01,
            "teacher_forced_next_token_agreement_required": True,
            "free_running_exact_sequence_required": True,
            "passed": bool(
                all(row["relative_l2_error"] <= 0.01 and row["next_token_agreement"] == 1 for row in teacher)
                and free["exact_sequence_agreement"] == 1
                and prefill_reference_relative_error <= 1e-5
            ),
        },
        "claim_boundary": {
            "allowed": "Token-ID decode comparison on the checked-in tiny causal-LM fixture with explicit digital KV-cache accounting.",
            "refused": "This is not a production tokenizer, full LLM, measured latency/energy, or silicon evidence.",
            "next_gate": "Run the same trace on a real small causal model and replace synthetic projection error with measured per-tile calibration.",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, default=ROOT / "samples" / "tiny-causal-lm.onnx")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--prompt", default="1,2")
    parser.add_argument("--generated-steps", type=int, default=4)
    parser.add_argument("--error-scale", type=float, default=0.001)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--target-profile", default="robotics", choices=["wearable", "camera", "robotics"])
    parser.add_argument("--calibration-profile", default="sim-wearable-v0")
    parser.add_argument("--physical-gate", type=Path)
    parser.add_argument("--enforce-physical-gate", action="store_true")
    args = parser.parse_args()
    prompt = [int(item) for item in args.prompt.split(",") if item.strip()]
    if not args.model.exists():
        raise SystemExit(f"model not found: {args.model}")
    if args.error_scale < 0:
        raise SystemExit("--error-scale must be non-negative")
    gate = load_gate(args.physical_gate)
    result = run(args.model, prompt, args.generated_steps, args.error_scale, args.seed, args.target_profile, args.calibration_profile, gate, args.enforce_physical_gate)
    args.output.mkdir(parents=True, exist_ok=True)
    path = args.output / "tiny_causal_lm_decode.json"
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(path), "summary": result["summary"], "passed": result["acceptance"]["passed"]}, indent=2))


if __name__ == "__main__":
    main()
