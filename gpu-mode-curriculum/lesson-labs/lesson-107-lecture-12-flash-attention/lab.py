#!/usr/bin/env python3
"""Lesson-specific local proxy program for GPUMODE lesson 107."""

from __future__ import annotations

import json
import math


LESSON = {
  "index": 107,
  "title": "Lecture 12: Flash Attention",
  "topics": [
    "cuda",
    "attention",
    "hardware"
  ],
  "concepts": [
    "shared memory tiling",
    "tensor cores",
    "online softmax",
    "kernel fusion",
    "autotuning",
    "compiler lowering"
  ],
  "tools": [
    "CUDA",
    "TVM"
  ],
  "exercise_candidates": [
    "implement naive vs tiled matrix multiplication",
    "implement numerically stable online softmax and compare to materialized softmax",
    "fuse bias, activation, and normalization into one measured path",
    "sweep block sizes and record the winning kernel configuration"
  ],
  "candidate_lab_links": [
    "gpumode-lab-01-coalescing",
    "gpumode-lab-02-warp-reductions",
    "gpumode-lab-04-online-softmax",
    "gpumode-lab-06-vllm-scheduler",
    "gpumode-lab-07-quantized-kernels",
    "gpumode-lab-08-nsight-to-roofline",
    "gpumode-lab-09-shared-memory-gemm",
    "gpumode-lab-10-tensor-core-cutlass",
    "gpumode-lab-11-rocm-hip-portability",
    "gpumode-lab-12-distributed-communication"
  ]
}
def memory_stride_score(length: int = 4096, stride: int = 4) -> dict[str, float | int | str]:
    contiguous_transactions = math.ceil(length / 32)
    strided_transactions = math.ceil(length * stride / 32)
    ratio = strided_transactions / max(1, contiguous_transactions)
    return {"kind": "memory-access", "length": length, "stride": stride, "transaction_ratio": round(ratio, 4)}


def online_softmax(values: list[float]) -> list[float]:
    running_max = -float("inf")
    running_sum = 0.0
    for value in values:
        next_max = max(running_max, value)
        running_sum = running_sum * math.exp(running_max - next_max) + math.exp(value - next_max)
        running_max = next_max
    return [math.exp(value - running_max) / running_sum for value in values]


def kv_cache_mb(batch: int = 1, sequence: int = 4096, layers: int = 32, hidden: int = 4096) -> float:
    return round(batch * sequence * layers * hidden * 2 * 2 / 1e6, 3)


def collective_latency_us(ranks: int = 8, payload_mb: int = 128) -> float:
    link_gbps = 300.0
    hop_latency_us = 4.0
    bytes_per_rank = payload_mb * 1024 * 1024
    seconds = 2 * (ranks - 1) * hop_latency_us / 1e6 + 2 * bytes_per_rank * (ranks - 1) / ranks / (link_gbps * 1e9)
    return round(seconds * 1e6, 3)


def run_proxy() -> dict[str, object]:
    topics = set(LESSON.get("topics", []))
    concepts = set(LESSON.get("concepts", []))
    checks: list[dict[str, object]] = []
    if "cuda" in topics or "memory coalescing" in concepts:
        checks.append(memory_stride_score())
    if "attention" in topics or "online softmax" in concepts:
        probs = online_softmax([0.2, 0.7, -0.4, 1.1])
        checks.append({"kind": "online-softmax", "probability_sum": round(sum(probs), 8), "max_probability": round(max(probs), 8)})
    if "serving" in topics or "kv cache" in concepts:
        checks.append({"kind": "serving-kv-cache", "kv_cache_mb": kv_cache_mb()})
    if "distributed" in topics or "collectives" in concepts:
        checks.append({"kind": "collective-model", "ring_latency_us": collective_latency_us()})
    if "quantization" in topics or "quantized numerics" in concepts:
        checks.append({"kind": "quantization", "int4_levels": 16, "symmetric_zero_point": 0})
    if not checks:
        checks.append({"kind": "triage", "exercise_count": len(LESSON.get("exercise_candidates", []))})
    return {
        "status": "ran-cpu-proxy",
        "lesson_index": LESSON["index"],
        "title": LESSON["title"],
        "topics": sorted(topics),
        "concepts": sorted(concepts),
        "checks": checks,
    }


if __name__ == "__main__":
    print(json.dumps(run_proxy(), indent=2, ensure_ascii=False))
