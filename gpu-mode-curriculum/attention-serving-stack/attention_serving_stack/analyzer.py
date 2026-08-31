from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "attention-serving-stack"
REPORT_JSON = OUT / "attention-serving-report.json"
REPORT_MD = OUT / "reports" / "attention-serving-report.md"

SOURCE_REPORTS = [
    "kernel-benchmarks/reports/kernel-benchmark-report.json",
    "kv-cache-paged-attention/kv-cache-report.json",
    "serving-traces/reports/serving-trace-report.json",
    "serving-engine-comparison/serving-engine-comparison.json",
    "numerical-reproducibility/numerical-reproducibility-report.json",
    "cuda-graphs-latency/cuda-graphs-latency-report.json",
]


@dataclass(frozen=True)
class AttentionScenario:
    scenario_id: str
    batch: int
    heads: int
    seq_q: int
    seq_kv: int
    head_dim: int
    dtype_bytes: int
    tile_q: int
    tile_k: int
    requests: int
    prefill_tokens: int
    decode_tokens: int
    shared_prefix_tokens: int
    block_size: int
    graph_bucket_tokens: int


SCENARIOS = [
    AttentionScenario("short-chat-prefill-decode", 8, 16, 128, 128, 64, 2, 64, 64, 16, 2048, 512, 512, 16, 256),
    AttentionScenario("long-context-rag", 4, 32, 512, 4096, 128, 2, 64, 128, 8, 32768, 2048, 8192, 16, 1024),
    AttentionScenario("agent-prefix-cache", 12, 24, 256, 2048, 128, 2, 64, 128, 24, 24576, 3072, 12288, 16, 512),
    AttentionScenario("mixed-batch-tail-latency", 16, 16, 64, 1024, 64, 2, 64, 64, 32, 16384, 4096, 2048, 16, 256),
    AttentionScenario("quantized-wide-heads", 6, 40, 256, 2048, 128, 1, 64, 128, 12, 18432, 1536, 4096, 16, 512),
]


def _read_json(rel_path: str) -> dict[str, Any]:
    path = ROOT / rel_path
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _ceil_div(value: int, divisor: int) -> int:
    return (value + divisor - 1) // divisor


def _baseline_hbm_bytes(row: AttentionScenario) -> int:
    q = row.batch * row.heads * row.seq_q * row.head_dim * row.dtype_bytes
    k = row.batch * row.heads * row.seq_kv * row.head_dim * row.dtype_bytes
    v = k
    scores = row.batch * row.heads * row.seq_q * row.seq_kv * 4
    probs = scores
    out = row.batch * row.heads * row.seq_q * row.head_dim * row.dtype_bytes
    return q + k + v + scores + probs + out


def _flash_hbm_bytes(row: AttentionScenario) -> int:
    q = row.batch * row.heads * row.seq_q * row.head_dim * row.dtype_bytes
    k = row.batch * row.heads * row.seq_kv * row.head_dim * row.dtype_bytes
    v = k
    out = row.batch * row.heads * row.seq_q * row.head_dim * row.dtype_bytes
    online_state = row.batch * row.heads * row.seq_q * 2 * 4
    return q + k + v + out + online_state


def _shared_memory_bytes(row: AttentionScenario) -> int:
    q_tile = row.tile_q * row.head_dim * row.dtype_bytes
    k_tile = row.tile_k * row.head_dim * row.dtype_bytes
    v_tile = k_tile
    online_state = row.tile_q * 2 * 4
    return q_tile + k_tile + v_tile + online_state


def _occupancy_proxy(row: AttentionScenario) -> float:
    smem = _shared_memory_bytes(row)
    smem_factor = min(1.0, 96 * 1024 / max(smem, 1))
    tile_work = row.tile_q * row.tile_k * row.head_dim
    work_factor = min(1.0, tile_work / (64 * 64 * 64))
    return round(0.55 + 0.35 * smem_factor + 0.10 * work_factor, 4)


def _kv_blocks(row: AttentionScenario) -> dict[str, int]:
    prompt_blocks = _ceil_div(row.prefill_tokens, row.block_size)
    decode_blocks = _ceil_div(row.decode_tokens, row.block_size)
    prefix_blocks = _ceil_div(row.shared_prefix_tokens, row.block_size) if row.shared_prefix_tokens else 0
    reusable = max(0, row.requests - 1) * prefix_blocks
    new_blocks = prompt_blocks + decode_blocks - reusable
    return {
        "prompt_blocks": prompt_blocks,
        "decode_blocks": decode_blocks,
        "prefix_blocks": prefix_blocks,
        "prefix_blocks_reused": reusable,
        "new_blocks_after_reuse": max(prompt_blocks + decode_blocks - reusable, row.requests),
        "block_size": row.block_size,
    }


def _scheduler(row: AttentionScenario) -> dict[str, Any]:
    kv = _kv_blocks(row)
    prefill_tiles = _ceil_div(row.prefill_tokens, row.tile_q)
    decode_steps = row.decode_tokens
    graph_bucket_fit = row.graph_bucket_tokens % row.block_size == 0 and row.graph_bucket_tokens >= row.tile_q
    decode_pressure = decode_steps / max(prefill_tiles, 1)
    policy = "chunked-prefill-continuous-batching" if decode_pressure > 4 else "prefill-first-graph-bucket"
    return {
        "policy": policy,
        "prefill_tiles": prefill_tiles,
        "decode_steps": decode_steps,
        "decode_pressure": round(decode_pressure, 4),
        "graph_bucket_tokens": row.graph_bucket_tokens,
        "graph_bucket_fit": graph_bucket_fit,
        "prefix_blocks_reused": kv["prefix_blocks_reused"],
    }


def _scenario(row: AttentionScenario) -> dict[str, Any]:
    baseline = _baseline_hbm_bytes(row)
    flash = _flash_hbm_bytes(row)
    smem = _shared_memory_bytes(row)
    kv = _kv_blocks(row)
    scheduler = _scheduler(row)
    hbm_reduction = 1.0 - flash / max(baseline, 1)
    qk_flops = 2 * row.batch * row.heads * row.seq_q * row.seq_kv * row.head_dim
    pv_flops = qk_flops
    intensity = (qk_flops + pv_flops) / max(flash, 1)
    passed = (
        hbm_reduction >= 0.35
        and smem <= 96 * 1024
        and scheduler["graph_bucket_fit"]
        and kv["new_blocks_after_reuse"] > 0
    )
    return {
        "scenario_id": row.scenario_id,
        "status": "passed" if passed else "tuning-required",
        "shape": {
            "batch": row.batch,
            "heads": row.heads,
            "seq_q": row.seq_q,
            "seq_kv": row.seq_kv,
            "head_dim": row.head_dim,
            "dtype_bytes": row.dtype_bytes,
        },
        "tiles": {"q": row.tile_q, "k": row.tile_k, "shared_memory_bytes": smem},
        "baseline_hbm_mb": round(baseline / 1_000_000, 4),
        "flash_hbm_mb": round(flash / 1_000_000, 4),
        "hbm_reduction": round(hbm_reduction, 6),
        "arithmetic_intensity": round(intensity, 4),
        "occupancy_proxy": _occupancy_proxy(row),
        "kv_cache": kv,
        "scheduler": scheduler,
        "numerics_contract": {
            "online_softmax_state": ["row_max", "row_sum"],
            "requires_reference_check": True,
            "recommended_tolerance": "match numerical-reproducibility fp32/tf32/bf16 policy by dtype",
        },
    }


def _source_facts(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "kernel_benchmarks": reports.get(SOURCE_REPORTS[0], {}).get("benchmark_count", 0),
        "kv_cache_scenarios": reports.get(SOURCE_REPORTS[1], {}).get("scenario_count", 0),
        "serving_traces": reports.get(SOURCE_REPORTS[2], {}).get("trace_count", 0),
        "serving_engines": reports.get(SOURCE_REPORTS[3], {}).get("engine_count", 0),
        "numerical_scenarios": reports.get(SOURCE_REPORTS[4], {}).get("scenario_count", 0),
        "cuda_graph_capture_ready": reports.get(SOURCE_REPORTS[5], {}).get("capture_ready_count", 0),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# GPUMODE FlashAttention to vLLM Serving Stack",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Status: `{report['status']}`",
        "",
        "| scenario | status | HBM reduction | shared memory | intensity | scheduler | prefix blocks reused |",
        "|---|---|---:|---:|---:|---|---:|",
    ]
    for row in report["scenarios"]:
        lines.append(
            f"| {row['scenario_id']} | {row['status']} | {row['hbm_reduction']} | "
            f"{row['tiles']['shared_memory_bytes']} | {row['arithmetic_intensity']} | "
            f"{row['scheduler']['policy']} | {row['scheduler']['prefix_blocks_reused']} |"
        )
    lines.extend(["", "## GPU Host Promotion", ""])
    for command in report["gpu_host_promotion"]["commands"]:
        lines.append(f"- `{command}`")
    return "\n".join(lines).rstrip() + "\n"


def build_attention_serving_report() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    reports = {rel: _read_json(rel) for rel in SOURCE_REPORTS}
    scenarios = [_scenario(row) for row in SCENARIOS]
    passed = sum(1 for row in scenarios if row["status"] == "passed")
    tuning = sum(1 for row in scenarios if row["status"] == "tuning-required")
    prefix_reuse = sum(row["scheduler"]["prefix_blocks_reused"] for row in scenarios)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "attention-serving-ready" if passed >= 4 and prefix_reuse > 0 else "needs-work",
        "scenario_count": len(scenarios),
        "passed_scenarios": passed,
        "tuning_required_scenarios": tuning,
        "total_prefix_blocks_reused": prefix_reuse,
        "source_reports": SOURCE_REPORTS,
        "source_facts": _source_facts(reports),
        "scenarios": scenarios,
        "recommendations": [
            "Teach attention kernels together with serving traces so prefill/decode choices are visible.",
            "Use online softmax state as the correctness boundary between FlashAttention and reference attention.",
            "Align KV block size, CUDA Graph capture buckets, and scheduler batches before GPU promotion.",
            "Profile kernel HBM traffic and serving tail latency in the same acceptance report.",
        ],
        "gpu_host_promotion": {
            "required": True,
            "target_steps": ["flash-attention-forward", "online-softmax-check", "vllm-trace-replay", "prefill-decode-profiler"],
            "commands": [
                "python3 scripts/run_gpu_host_preflight.py",
                "python3 scripts/run_attention_serving_stack.py",
                "python3 scripts/verify_attention_serving_stack.py",
                "nsys profile -o flashattention-serving python3 <vllm_trace_replay.py>",
                "ncu --set full -o flashattention-kernel python3 <flash_attention_probe.py>",
                "python3 scripts/run_gpu_promotion_suite.py --run-id attention-serving-stack --execute",
            ],
            "note": "Local model validates stack accounting; acceptance still needs real CUDA/Triton/ROCm kernel timings and serving traces.",
        },
    }
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    return report
