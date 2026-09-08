#!/usr/bin/env python3
"""Compare uncached and KV-cached batch-1 autoregressive decode."""

from __future__ import annotations

import hashlib
import json
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import torch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO = ROOT if (ROOT / "gpu-kernels-serving-lab").exists() else ROOT.parent
SERVING = REPO / "gpu-kernels-serving-lab" / "13-capstone-mini-serving-engine"
sys.path.insert(0, str(SERVING))
from neural_generator import NeuralGenerator  # noqa: E402

REPORT = HERE / "reports" / "decode-comparison.json"
WORKLOADS = (
    {"id": "short-context", "prompt": "attention cache", "max_tokens": 12, "repeats": 7},
    {"id": "long-context", "prompt": "attention cache " * 5, "max_tokens": 24, "repeats": 7},
    {"id": "long-decode", "prompt": "attention cache", "max_tokens": 96, "repeats": 3},
)
WARMUPS = 2
MODEL_HIDDEN = 128
MODEL_HEADS = 8


def _median(values: list[float]) -> float:
    return float(statistics.median(values))


def _run_once(generator: NeuralGenerator, prompt: str, max_tokens: int, cached: bool, cache_storage: str = "dynamic") -> dict:
    started = time.perf_counter()
    generated, logits = generator.generate(prompt, max_tokens, cached=cached, cache_storage=cache_storage)
    wall_ms = (time.perf_counter() - started) * 1000.0
    return {"tokens": generated, "logits": logits, "wall_ms": wall_ms}


def _cuda_run_once(generator: NeuralGenerator, prompt: str, max_tokens: int, cached: bool, cache_storage: str = "dynamic") -> dict:
    if generator.device.type != "cuda":
        return _run_once(generator, prompt, max_tokens, cached, cache_storage)
    start = torch.cuda.Event(enable_timing=True)
    end = torch.cuda.Event(enable_timing=True)
    started = time.perf_counter()
    start.record()
    generated, logits = generator.generate(prompt, max_tokens, cached=cached, cache_storage=cache_storage)
    end.record()
    end.synchronize()
    return {
        "tokens": generated,
        "logits": logits,
        "wall_ms": (time.perf_counter() - started) * 1000.0,
        "cuda_event_ms": float(start.elapsed_time(end)),
    }


def _compare_logits(left: list[torch.Tensor], right: list[torch.Tensor]) -> dict:
    errors = [float((a - b).abs().max().item()) for a, b in zip(left, right)]
    return {
        "steps": len(errors),
        "max_abs_error": max(errors, default=0.0),
        "all_finite": all(torch.isfinite(torch.tensor(errors))),
        "passed": len(left) == len(right) and max(errors, default=0.0) <= 2e-6,
    }


def _path_report(generator: NeuralGenerator, prompt: str, max_tokens: int, repeats: int, cached: bool, cache_storage: str = "dynamic") -> dict:
    for _ in range(WARMUPS):
        _cuda_run_once(generator, prompt, max_tokens, cached, cache_storage)
    samples = [_cuda_run_once(generator, prompt, max_tokens, cached, cache_storage) for _ in range(repeats)]
    return {
        "cached": cached,
        "wall_ms_samples": [row["wall_ms"] for row in samples],
        "wall_ms_median": _median([row["wall_ms"] for row in samples]),
        "cuda_event_ms_samples": [row["cuda_event_ms"] for row in samples if "cuda_event_ms" in row],
        "cuda_event_ms_median": _median([row["cuda_event_ms"] for row in samples]) if "cuda_event_ms" in samples[0] else None,
        "tokens": samples[-1]["tokens"],
        "logits": samples[-1]["logits"],
    }


def main() -> int:
    previous_threads = torch.get_num_threads()
    torch.set_num_threads(1)
    try:
        generator = NeuralGenerator("cuda" if torch.cuda.is_available() else "cpu", hidden=MODEL_HIDDEN, heads=MODEL_HEADS)
        rows = []
        for workload in WORKLOADS:
            prompt = workload["prompt"]
            max_tokens = workload["max_tokens"]
            repeats = workload["repeats"]
            uncached = _path_report(generator, prompt, max_tokens, repeats, cached=False)
            cached = _path_report(generator, prompt, max_tokens, repeats, cached=True, cache_storage="dynamic")
            preallocated = _path_report(generator, prompt, max_tokens, repeats, cached=True, cache_storage="preallocated")
            parity = {
                "tokens_equal": uncached["tokens"] == cached["tokens"],
                "logits": _compare_logits(uncached["logits"], cached["logits"]),
                "preallocated_tokens_equal": uncached["tokens"] == preallocated["tokens"],
                "preallocated_logits": _compare_logits(uncached["logits"], preallocated["logits"]),
            }
            rows.append({
                "workload": workload["id"],
                "prompt": prompt,
                "prompt_tokens": len(generator.encode(prompt)),
                "max_tokens": max_tokens,
                "repeats": repeats,
                "uncached": {k: v for k, v in uncached.items() if k not in {"tokens", "logits"}},
                "cached": {k: v for k, v in cached.items() if k not in {"tokens", "logits"}},
                "preallocated": {k: v for k, v in preallocated.items() if k not in {"tokens", "logits"}},
                "parity": parity,
                "speedup_wall": uncached["wall_ms_samples"][-1] / max(cached["wall_ms_samples"][-1], 1e-9),
                "preallocated_speedup_wall": uncached["wall_ms_samples"][-1] / max(preallocated["wall_ms_samples"][-1], 1e-9),
            })
        checks = {
            "workload_count": len(rows) == len(WORKLOADS),
            "all_token_parity": all(row["parity"]["tokens_equal"] for row in rows),
            "all_logit_parity": all(row["parity"]["logits"]["passed"] for row in rows),
            "all_preallocated_token_parity": all(row["parity"]["preallocated_tokens_equal"] for row in rows),
            "all_preallocated_logit_parity": all(row["parity"]["preallocated_logits"]["passed"] for row in rows),
            "raw_samples_present": all(len(row["cached"]["wall_ms_samples"]) == row["repeats"] for row in rows),
            "preallocated_raw_samples_present": all(len(row["preallocated"]["wall_ms_samples"]) == row["repeats"] for row in rows),
        }
        device = str(generator.device)
        evidence_kind = "measured_gpu" if generator.device.type == "cuda" else "measured_cpu"
        report = {
            "experiment": "batch1_decode_cached_vs_uncached",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "passed" if all(checks.values()) else "failed",
            "evidence_kind": evidence_kind,
            "device": device,
            "gpu_execution_accepted": generator.device.type == "cuda" and all(checks.values()),
            "protocol": {"workloads": list(WORKLOADS), "model_hidden": MODEL_HIDDEN, "model_heads": MODEL_HEADS, "warmups": WARMUPS, "threads": 1},
            "rows": rows,
            "checks": checks,
            "timing_scope": "complete autoregressive generator call including prefill, decode, sampling, and Python orchestration; CUDA event covers the same call on the default stream",
            "reference": "same seeded character transformer with full-prefix recomputation",
            "candidate": "same seeded character transformer with append-only KV cache",
            "optimized_candidate": "same seeded character transformer with preallocated append-only KV storage (no per-token K/V cat)",
            "limitations": ["untrained character model", "single request batch-1 direct generation", "not a production language-quality claim", "HTTP serving and profiler promotion are separate gates"],
            "source_sha256": {str(path.relative_to(REPO)): hashlib.sha256(path.read_bytes()).hexdigest() for path in (Path(__file__).resolve(), SERVING / "neural_generator.py", ROOT / "model-integration/model_integration/tiny_transformer.py")},
        }
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        print(json.dumps({"status": report["status"], "evidence_kind": evidence_kind, "device": device, "checks": checks}, indent=2))
        return 0 if report["status"] == "passed" else 1
    finally:
        torch.set_num_threads(previous_threads)


if __name__ == "__main__":
    raise SystemExit(main())
