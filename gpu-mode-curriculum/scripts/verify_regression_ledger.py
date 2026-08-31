#!/usr/bin/env python3
"""Verify the performance regression ledger."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "regression-ledger" / "regression-ledger.json"
SITE_PAGE = ROOT / "site" / "regression-ledger.html"
REQUIRED_LAYERS = {"kernel-benchmarks", "custom-ops", "tensor-core-gemm", "persistent-kernels", "parallel-primitives", "autotune-db", "model-integration", "serving-traces", "kv-cache-paged-attention", "attention-serving-stack", "flash-attention-backward", "sparse-attention-kernels", "fused-training-kernels", "speculative-decoding-serving", "quantization-memory-formats", "numerical-reproducibility", "cuda-graphs-latency", "distributed-collectives", "distributed-training-optimizer", "moe-routing-all-to-all", "multi-tenant-gpu-scheduling"}
REQUIRED_METRICS = {"median_seconds", "max_abs_error", "estimated_speedup_vs_measured", "tokens_per_second", "output_tokens_per_second", "compression_vs_fp32", "cosine_similarity", "p95_latency_reduction", "fairness_index", "waste_ratio", "prefix_blocks_reused", "drop_rate", "estimated_all_to_all_ms", "repeat_max_abs_drift", "max_order_delta", "hbm_reduction", "arithmetic_intensity", "shared_memory_bytes", "register_pressure_proxy", "tensor_core_eligible", "epilogue_fused", "bandwidth_efficiency", "overlap_gain", "exposed_comm_ms", "memory_gb_per_gpu", "optimizer_state_savings", "reduce_scatter_ms", "all_gather_ms", "pipeline_bubble_ms", "step_time_ms", "speedup_vs_baseline", "resident_ctas_per_sm", "launch_savings_ms", "persistent_compute_ms", "baseline_ms", "work_efficiency", "memory_traffic_mb", "bandwidth_proxy_gbps", "atomic_pressure_millions", "stable_order_required", "recompute_overhead_ratio", "saved_activation_reduction", "backward_ms", "speedup_vs_dense", "metadata_overhead", "load_balance_proxy", "sparse_ms", "speedup_vs_unfused", "launch_reduction", "fused_ms", "baseline_hbm_mb", "fused_hbm_mb", "acceptance_rate", "accepted_tokens_per_verify", "speculative_tpot_ms", "estimated_ttft_ms", "wasted_draft_ratio", "rollback_pressure"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    if not LEDGER.exists():
        subprocess.run([sys.executable, "scripts/build_regression_ledger.py"], cwd=ROOT, check=True)
    ledger = load_json(LEDGER)
    metrics = ledger.get("metrics", [])
    require(ledger.get("metric_count") == len(metrics), "regression metric count mismatch")
    require(ledger.get("metric_count", 0) >= 720, "expected metrics across benchmark, custom-op, tensor-core GEMM, persistent kernels, parallel primitives, autotune, model, serving, KV-cache, attention-serving, FlashAttention backward, sparse attention, fused training, speculative decoding, quantization, numerics, CUDA Graphs, distributed collectives, distributed training optimizer, MoE, and multi-tenant scheduling layers")
    require(ledger.get("failed") == 0, "regression ledger has failed metrics")
    layers = {row.get("layer") for row in metrics}
    metric_names = {row.get("metric") for row in metrics}
    require(REQUIRED_LAYERS.issubset(layers), f"missing regression layers: {sorted(REQUIRED_LAYERS - layers)}")
    require(REQUIRED_METRICS.issubset(metric_names), f"missing regression metrics: {sorted(REQUIRED_METRICS - metric_names)}")
    for row in metrics:
        require(row.get("status") in {"passed", "warning", "failed"}, f"{row.get('id')} invalid status")
        require(row.get("source"), f"{row.get('id')} missing source")
        require(isinstance(row.get("value"), (int, float)), f"{row.get('id')} has nonnumeric value")
    if SITE_PAGE.exists():
        page = SITE_PAGE.read_text(encoding="utf-8")
        require("GPUMODE regression ledger" in page, "regression ledger site page missing title")
        require("kernel-benchmarks" in page and "tensor-core-gemm" in page and "persistent-kernels" in page and "parallel-primitives" in page and "serving-traces" in page and "kv-cache-paged-attention" in page and "attention-serving-stack" in page and "flash-attention-backward" in page and "sparse-attention-kernels" in page and "fused-training-kernels" in page and "speculative-decoding-serving" in page and "quantization-memory-formats" in page and "numerical-reproducibility" in page and "cuda-graphs-latency" in page and "distributed-collectives" in page and "distributed-training-optimizer" in page and "moe-routing-all-to-all" in page and "multi-tenant-gpu-scheduling" in page, "regression ledger site page missing layers")
    facts = {
        "metrics": ledger["metric_count"],
        "passed": ledger["passed"],
        "warnings": ledger["warnings"],
        "failed": ledger["failed"],
        "layers": sorted(layers),
    }
    print(json.dumps({"facts": facts, "failures": []}, indent=2))
    print("GPUMODE regression ledger verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
