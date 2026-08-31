from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "kv-cache-paged-attention"
REPORT_JSON = OUT / "kv-cache-report.json"
REPORT_MD = OUT / "reports" / "kv-cache-report.md"

SOURCE_REPORTS = [
    "serving-traces/reports/serving-trace-report.json",
    "serving-engine-comparison/serving-engine-comparison.json",
    "cuda-graphs-latency/cuda-graphs-latency-report.json",
    "multi-tenant-gpu-scheduling/multi-tenant-scheduling-report.json",
]


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    prompt_tokens: list[int]
    output_tokens: list[int]
    shared_prefix_tokens: int
    capacity_blocks: int
    block_size: int
    eviction_window: int


SCENARIOS = [
    Scenario("chat-short-mixed", [128, 160, 96, 224, 180], [64, 80, 48, 96, 72], 64, 128, 16, 3),
    Scenario("long-context-rag", [3072, 4096, 3584, 2048], [256, 320, 256, 192], 1024, 512, 16, 2),
    Scenario("prefix-heavy-agents", [1536, 1600, 1664, 1728, 1792, 1856], [128, 128, 160, 160, 192, 192], 1408, 384, 16, 4),
    Scenario("fragmented-adapters", [257, 513, 769, 1025, 129], [33, 65, 97, 129, 17], 0, 256, 16, 3),
    Scenario("capacity-pressure", [4096, 4096, 4096], [512, 512, 512], 0, 640, 16, 1),
]


def _read_json(rel_path: str) -> dict[str, Any]:
    path = ROOT / rel_path
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _ceil_div(value: int, divisor: int) -> int:
    return (value + divisor - 1) // divisor


def _simulate_contiguous(scenario: Scenario) -> dict[str, Any]:
    reservations = []
    live_blocks = 0
    evictions = 0
    rejected = 0
    peak_blocks = 0
    for index, (prompt, output) in enumerate(zip(scenario.prompt_tokens, scenario.output_tokens, strict=True)):
        needed_tokens = prompt + output
        needed_blocks = _ceil_div(needed_tokens, scenario.block_size)
        if live_blocks + needed_blocks > scenario.capacity_blocks:
            evictions += 1
            live_blocks = max(0, live_blocks - sum(row["blocks"] for row in reservations[:1]))
            reservations = reservations[1:]
        if live_blocks + needed_blocks > scenario.capacity_blocks:
            rejected += 1
            continue
        live_blocks += needed_blocks
        peak_blocks = max(peak_blocks, live_blocks)
        reservations.append({"request": index, "blocks": needed_blocks, "tokens": needed_tokens})
        if len(reservations) > scenario.eviction_window:
            live_blocks -= reservations.pop(0)["blocks"]
    useful_tokens = sum(scenario.prompt_tokens) + sum(scenario.output_tokens)
    reserved_tokens = sum(_ceil_div(prompt + output, scenario.block_size) * scenario.block_size for prompt, output in zip(scenario.prompt_tokens, scenario.output_tokens, strict=True))
    return {
        "policy": "contiguous-request-kv",
        "peak_blocks": peak_blocks,
        "reserved_tokens": reserved_tokens,
        "useful_tokens": useful_tokens,
        "waste_ratio": round((reserved_tokens - useful_tokens) / max(reserved_tokens, 1), 6),
        "eviction_count": evictions,
        "rejected_count": rejected,
        "prefix_blocks_reused": 0,
    }


def _simulate_paged(scenario: Scenario) -> dict[str, Any]:
    reservations = []
    live_blocks = 0
    evictions = 0
    rejected = 0
    peak_blocks = 0
    prefix_blocks = _ceil_div(scenario.shared_prefix_tokens, scenario.block_size) if scenario.shared_prefix_tokens else 0
    prefix_loaded = False
    prefix_reused = 0
    reserved_tokens = 0
    useful_tokens = 0
    for index, (prompt, output) in enumerate(zip(scenario.prompt_tokens, scenario.output_tokens, strict=True)):
        private_prompt = max(0, prompt - scenario.shared_prefix_tokens)
        private_tokens = private_prompt + output
        private_blocks = _ceil_div(private_tokens, scenario.block_size)
        new_prefix_blocks = 0 if prefix_loaded else prefix_blocks
        needed_blocks = private_blocks + new_prefix_blocks
        while live_blocks + needed_blocks > scenario.capacity_blocks and reservations:
            evictions += 1
            live_blocks -= reservations.pop(0)["blocks"]
        if live_blocks + needed_blocks > scenario.capacity_blocks:
            rejected += 1
            continue
        prefix_reused += prefix_blocks if prefix_loaded and prefix_blocks else 0
        prefix_loaded = prefix_loaded or prefix_blocks > 0
        live_blocks += needed_blocks
        peak_blocks = max(peak_blocks, live_blocks)
        reservations.append({"request": index, "blocks": private_blocks, "tokens": private_tokens})
        reserved_tokens += needed_blocks * scenario.block_size
        useful_tokens += private_tokens + new_prefix_blocks * scenario.block_size
        if len(reservations) > scenario.eviction_window:
            live_blocks -= reservations.pop(0)["blocks"]
    return {
        "policy": "paged-attention-block-table",
        "peak_blocks": peak_blocks,
        "reserved_tokens": reserved_tokens,
        "useful_tokens": useful_tokens,
        "waste_ratio": round((reserved_tokens - useful_tokens) / max(reserved_tokens, 1), 6),
        "eviction_count": evictions,
        "rejected_count": rejected,
        "prefix_blocks_reused": prefix_reused,
    }


def _scenario(row: Scenario) -> dict[str, Any]:
    contiguous = _simulate_contiguous(row)
    paged = _simulate_paged(row)
    saved_blocks = contiguous["peak_blocks"] - paged["peak_blocks"]
    waste_reduction = contiguous["waste_ratio"] - paged["waste_ratio"]
    status = "passed" if paged["rejected_count"] <= contiguous["rejected_count"] and (saved_blocks >= 0 or paged["prefix_blocks_reused"] > 0) else "needs-work"
    return {
        "scenario_id": row.scenario_id,
        "status": status,
        "request_count": len(row.prompt_tokens),
        "block_size": row.block_size,
        "capacity_blocks": row.capacity_blocks,
        "shared_prefix_tokens": row.shared_prefix_tokens,
        "contiguous": contiguous,
        "paged": paged,
        "peak_block_savings": saved_blocks,
        "waste_ratio_reduction": round(waste_reduction, 6),
        "admission_delta": contiguous["rejected_count"] - paged["rejected_count"],
    }


def _source_facts(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    serving = reports.get(SOURCE_REPORTS[0], {})
    engine = reports.get(SOURCE_REPORTS[1], {})
    graphs = reports.get(SOURCE_REPORTS[2], {})
    scheduling = reports.get(SOURCE_REPORTS[3], {})
    return {
        "serving_traces": serving.get("trace_count", 0),
        "serving_prefix_blocks_saved": sum(row.get("prefix_cache_blocks_saved", 0) for row in serving.get("comparisons", [])),
        "serving_engines": engine.get("engine_count", 0),
        "cuda_graph_capture_ready": graphs.get("capture_ready_count", 0),
        "scheduling_tenants": scheduling.get("tenant_count", 0),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# GPUMODE KV Cache and PagedAttention",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Status: `{report['status']}`",
        "",
        "| scenario | status | peak block savings | waste reduction | admission delta | prefix blocks reused |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in report["scenarios"]:
        lines.append(
            f"| {row['scenario_id']} | {row['status']} | {row['peak_block_savings']} | "
            f"{row['waste_ratio_reduction']} | {row['admission_delta']} | {row['paged']['prefix_blocks_reused']} |"
        )
    lines.extend(["", "## GPU Host Promotion", ""])
    for command in report["gpu_host_promotion"]["commands"]:
        lines.append(f"- `{command}`")
    return "\n".join(lines).rstrip() + "\n"


def build_kv_cache_report() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    reports = {rel: _read_json(rel) for rel in SOURCE_REPORTS}
    scenarios = [_scenario(row) for row in SCENARIOS]
    passed = sum(1 for row in scenarios if row["status"] == "passed")
    prefix_reused = sum(row["paged"]["prefix_blocks_reused"] for row in scenarios)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "kv-cache-ready" if passed >= 4 and prefix_reused > 0 else "needs-work",
        "scenario_count": len(scenarios),
        "passed_scenarios": passed,
        "policy_count": 2,
        "total_prefix_blocks_reused": prefix_reused,
        "source_reports": SOURCE_REPORTS,
        "source_facts": _source_facts(reports),
        "scenarios": scenarios,
        "recommendations": [
            "Use paged block tables for variable-length and prefix-heavy serving traffic.",
            "Track internal fragmentation with reserved tokens versus useful tokens, not only peak bytes.",
            "Keep CUDA Graph capture buckets aligned with KV block sizes to avoid allocator churn.",
            "Promote on a GPU host with vLLM/SGLang traces, memory snapshots, and per-request admission logs.",
        ],
        "gpu_host_promotion": {
            "required": True,
            "target_steps": ["vllm-kv-block-stats", "paged-attention-profiler", "prefix-cache-hit-rate", "allocator-fragmentation-trace"],
            "commands": [
                "python3 scripts/run_gpu_host_preflight.py",
                "vllm serve <model> --enable-prefix-caching --block-size 16",
                "python3 scripts/run_serving_traces.py",
                "nsys profile -o paged-attention python3 <vllm_trace_replay.py>",
                "ncu --set full -o kv-cache-kernels python3 <paged_attention_probe.py>",
                "python3 scripts/run_gpu_promotion_suite.py --run-id kv-cache-paged-attention --execute",
            ],
            "note": "Local allocator model validates accounting; real acceptance requires GPU serving traces with block-table, prefix-cache, and memory-fragmentation telemetry.",
        },
    }
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    return report
