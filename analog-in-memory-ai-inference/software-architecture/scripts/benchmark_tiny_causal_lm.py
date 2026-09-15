#!/usr/bin/env python3
"""Benchmark the tiny causal-LM token trace with explicit cost denominators.

The wall-clock numbers measure this Python reference implementation only. The
digital/hybrid energy numbers are an explicit, configurable model so that
conversion and cache costs cannot disappear inside an analog-MAC headline.
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path
from typing import Any

import numpy as np
import onnx

from build_transformer_execution_contract import build_contract
from run_tiny_causal_lm_decode import apply_error_model, load_gate, load_weights, step


ROOT = Path(__file__).resolve().parents[1]


def generated_trace(params: dict[str, np.ndarray], prompt: list[int], generated_steps: int) -> list[int]:
    cache_k: list[np.ndarray] = []
    cache_v: list[np.ndarray] = []
    tokens = list(prompt)
    for token_id in prompt:
        logits, _ = step(token_id, cache_k, cache_v, params)
    for _ in range(generated_steps):
        next_token = int(np.argmax(logits))
        tokens.append(next_token)
        logits, _ = step(next_token, cache_k, cache_v, params)
    return tokens


def timed_teacher_forced(params: dict[str, np.ndarray], tokens: list[int], repeats: int, warmups: int) -> list[float]:
    def run_once() -> None:
        cache_k: list[np.ndarray] = []
        cache_v: list[np.ndarray] = []
        for token_id in tokens:
            step(token_id, cache_k, cache_v, params)

    for _ in range(warmups):
        run_once()
    samples = []
    for _ in range(repeats):
        start = time.perf_counter_ns()
        run_once()
        samples.append((time.perf_counter_ns() - start) / 1e6 / len(tokens))
    return samples


def cost_rows(
    token_count: int,
    hidden: int,
    vocabulary: int,
    analog_projection_count: int,
    bytes_per_value: int,
    digital_mac_pj: float,
    analog_mac_pj: float,
    converter_value_pj: float,
    memory_byte_pj: float,
) -> list[dict[str, Any]]:
    # The five fixed projections are Q/K/V/O and the vocabulary head. Their
    # output dimensions are hidden, hidden, hidden, hidden, vocabulary.
    projection_macs = 4 * hidden * hidden + hidden * vocabulary
    projection_values = 4 * (hidden + hidden) + hidden + vocabulary
    rows = []
    for index in range(token_count):
        dynamic_macs = 2 * (index + 1) * hidden
        cache_read = 2 * index * hidden * bytes_per_value
        cache_write = 2 * hidden * bytes_per_value
        analog_macs = projection_macs if analog_projection_count == 5 else 0
        digital_projection_macs = projection_macs - analog_macs
        digital_macs = digital_projection_macs + dynamic_macs
        converter_values = projection_values if analog_projection_count == 5 else 0
        cache_energy = (cache_read + cache_write) * memory_byte_pj
        digital_energy = (projection_macs + dynamic_macs) * digital_mac_pj + cache_energy
        hybrid_energy = (
            analog_macs * analog_mac_pj
            + digital_macs * digital_mac_pj
            + converter_values * converter_value_pj
            + cache_energy
        )
        rows.append(
            {
                "token_index": index,
                "cache_length": index + 1,
                "projection_macs": projection_macs,
                "dynamic_attention_macs": dynamic_macs,
                "digital_total_macs": projection_macs + dynamic_macs,
                "hybrid_analog_macs": analog_macs,
                "hybrid_digital_macs": digital_macs,
                "analog_converter_values": converter_values,
                "kv_cache_read_bytes": cache_read,
                "kv_cache_write_bytes": cache_write,
                "digital_energy_pj_estimate": digital_energy,
                "hybrid_energy_pj_estimate": hybrid_energy,
            }
        )
    return rows


def run_benchmark(
    model_path: Path,
    prompt: list[int],
    generated_steps: int,
    error_scale: float,
    seed: int,
    repeats: int,
    warmups: int,
    digital_mac_pj: float,
    analog_mac_pj: float,
    converter_value_pj: float,
    memory_byte_pj: float,
    physical_gate: dict[str, Any] | None,
    enforce_physical_gate: bool,
) -> dict[str, Any]:
    model = onnx.load(model_path)
    base = load_weights(model)
    contract = build_contract(model_path, "robotics", "benchmark-synthetic-v0", "decode", physical_gate, enforce_physical_gate)
    candidates = [row["operator_id"] for row in contract["operator_inventory"]["operators"] if row.get("placement") == "analog"]
    hybrid, _ = apply_error_model(base, candidates, error_scale, seed + 1)
    tokens = generated_trace(base, prompt, generated_steps)
    digital_samples = timed_teacher_forced(base, tokens, repeats, warmups)
    hybrid_samples = timed_teacher_forced(hybrid, tokens, repeats, warmups)
    hidden = int(base["embedding"].shape[1])
    vocabulary = int(base["embedding"].shape[0])
    rows = cost_rows(len(tokens), hidden, vocabulary, len(candidates), 4, digital_mac_pj, analog_mac_pj, converter_value_pj, memory_byte_pj)
    digital_energy = sum(row["digital_energy_pj_estimate"] for row in rows)
    hybrid_energy = sum(row["hybrid_energy_pj_estimate"] for row in rows)
    return {
        "schema_version": "tiny-causal-lm-cost-benchmark-v0.1",
        "result_type": "token_trace_runtime_and_energy_denominator",
        "provenance": {
            "model": model_path.name,
            "prompt_token_ids": prompt,
            "generated_steps": generated_steps,
            "token_trace": tokens,
            "seed": seed,
            "repeats": repeats,
            "warmups": warmups,
            "physical_gate_enforced": enforce_physical_gate,
        },
        "placement": {
            "analog_candidate_count": len(candidates),
            "analog_candidate_operator_ids": candidates,
            "dynamic_attention": "digital",
            "kv_cache": "digital_memory",
        },
        "energy_model": {
            "units": "pJ",
            "digital_mac_pj": digital_mac_pj,
            "analog_mac_pj": analog_mac_pj,
            "converter_value_pj": converter_value_pj,
            "memory_byte_pj": memory_byte_pj,
            "status": "assumption; replace with measured tile/converter/SRAM data",
        },
        "per_token_cost": rows,
        "summary": {
            "token_count": len(tokens),
            "digital_reference_wall_ms_per_token_median": statistics.median(digital_samples),
            "digital_reference_wall_ms_per_token_p95": float(np.percentile(digital_samples, 95)),
            "hybrid_reference_wall_ms_per_token_median": statistics.median(hybrid_samples),
            "hybrid_reference_wall_ms_per_token_p95": float(np.percentile(hybrid_samples, 95)),
            "digital_energy_pj_estimate": digital_energy,
            "hybrid_energy_pj_estimate": hybrid_energy,
            "modeled_energy_ratio_digital_over_hybrid": digital_energy / max(hybrid_energy, 1e-12),
            "total_kv_cache_bytes": sum(row["kv_cache_read_bytes"] + row["kv_cache_write_bytes"] for row in rows),
        },
        "claim_boundary": {
            "allowed": "Same-token-trace Python reference timing plus an explicit, reproducible energy cost model.",
            "refused": "Python wall time is not accelerator latency; modeled pJ is not measured chip energy or a vendor TOPS/W claim.",
            "next_gate": "Replace the four energy coefficients and wall-clock implementation with board/RTL/accelerator measurements using the same token trace.",
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
    parser.add_argument("--repeats", type=int, default=20)
    parser.add_argument("--warmups", type=int, default=3)
    parser.add_argument("--digital-mac-pj", type=float, default=3.0)
    parser.add_argument("--analog-mac-pj", type=float, default=0.6)
    parser.add_argument("--converter-value-pj", type=float, default=2.0)
    parser.add_argument("--memory-byte-pj", type=float, default=0.2)
    parser.add_argument("--physical-gate", type=Path)
    parser.add_argument("--enforce-physical-gate", action="store_true")
    args = parser.parse_args()
    prompt = [int(item) for item in args.prompt.split(",") if item.strip()]
    gate = load_gate(args.physical_gate)
    result = run_benchmark(
        args.model,
        prompt,
        args.generated_steps,
        args.error_scale,
        args.seed,
        args.repeats,
        args.warmups,
        args.digital_mac_pj,
        args.analog_mac_pj,
        args.converter_value_pj,
        args.memory_byte_pj,
        gate,
        args.enforce_physical_gate,
    )
    args.output.mkdir(parents=True, exist_ok=True)
    path = args.output / "tiny_causal_lm_cost_benchmark.json"
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(path), "summary": result["summary"]}, indent=2))


if __name__ == "__main__":
    main()
