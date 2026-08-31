from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "speculative-decoding-serving"
REPORT_JSON = OUT / "speculative-decoding-report.json"
REPORT_MD = OUT / "reports" / "speculative-decoding-report.md"

SOURCE_REPORTS = [
    "serving-traces/reports/serving-trace-report.json",
    "kv-cache-paged-attention/kv-cache-report.json",
    "attention-serving-stack/attention-serving-report.json",
    "serving-engine-comparison/serving-engine-comparison.json",
    "cuda-graphs-latency/cuda-graphs-latency-report.json",
    "profiler-evidence/reports/profiler-evidence-report.json",
]


@dataclass(frozen=True)
class SpecDecodeScenario:
    scenario_id: str
    workload: str
    engine_hint: str
    requests: int
    prompt_tokens: int
    target_tokens: int
    draft_width: int
    draft_latency_ms: float
    target_verify_ms: float
    baseline_decode_ms: float
    acceptance_rate: float
    prefix_reuse_blocks: int
    graph_bucket_fit: bool
    memory_headroom_gb: float


SCENARIOS = [
    SpecDecodeScenario("chat-medusa-draft", "interactive-chat", "vllm-or-sglang", 32, 768, 256, 4, 0.18, 0.46, 1.05, 0.72, 384, True, 19.0),
    SpecDecodeScenario("rag-eagle-long-context", "long-context-rag", "vllm", 12, 8192, 512, 6, 0.24, 0.82, 1.78, 0.66, 6144, True, 34.0),
    SpecDecodeScenario("code-assistant-bursty", "mixed-prefill-decode", "sglang", 24, 2048, 384, 5, 0.22, 0.64, 1.32, 0.61, 1152, True, 16.0),
    SpecDecodeScenario("offline-throughput-ngram", "offline-throughput", "tgi-or-vllm", 64, 512, 1024, 8, 0.15, 0.92, 1.44, 0.58, 512, True, 27.0),
    SpecDecodeScenario("portable-hf-assisted", "portable-amd-nvidia", "hf-transformers", 8, 1024, 192, 3, 0.20, 0.52, 1.10, 0.69, 128, False, 8.0),
    SpecDecodeScenario("low-acceptance-rollback", "adversarial-domain-shift", "vllm", 16, 1536, 256, 6, 0.25, 0.74, 1.22, 0.43, 256, True, 11.0),
]


def _read_json(rel_path: str) -> dict[str, Any]:
    path = ROOT / rel_path
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _scenario(row: SpecDecodeScenario) -> dict[str, Any]:
    accepted_per_step = max(row.draft_width * row.acceptance_rate, 0.01)
    verifier_steps = row.target_tokens / accepted_per_step
    speculative_decode_ms = verifier_steps * (row.draft_latency_ms + row.target_verify_ms)
    baseline_decode_ms = row.target_tokens * row.baseline_decode_ms
    speedup = baseline_decode_ms / max(speculative_decode_ms, 1e-9)
    wasted_draft_tokens = row.target_tokens * row.draft_width * (1.0 - row.acceptance_rate) / accepted_per_step
    wasted_ratio = wasted_draft_tokens / max(row.target_tokens + wasted_draft_tokens, 1e-9)
    tpot_ms = speculative_decode_ms / max(row.target_tokens, 1)
    baseline_tpot_ms = baseline_decode_ms / max(row.target_tokens, 1)
    ttft_ms = 0.18 * row.prompt_tokens / max(row.requests, 1) + (0.35 if row.graph_bucket_fit else 0.90)
    throughput_tokens_s = 1000.0 * row.requests * row.target_tokens / max(speculative_decode_ms, 1e-9)
    rollback_pressure = (1.0 - row.acceptance_rate) * row.draft_width
    scheduler = "speculative-continuous-batching" if row.acceptance_rate >= 0.55 else "rollback-aware-target-first"
    status = "passed" if speedup >= 1.25 and row.acceptance_rate >= 0.50 and row.memory_headroom_gb >= 8.0 else "review"
    if not row.graph_bucket_fit:
        status = "review"
    return {
        "scenario_id": row.scenario_id,
        "workload": row.workload,
        "engine_hint": row.engine_hint,
        "status": status,
        "requests": row.requests,
        "prompt_tokens": row.prompt_tokens,
        "target_tokens": row.target_tokens,
        "draft_width": row.draft_width,
        "acceptance_rate": row.acceptance_rate,
        "accepted_tokens_per_verify": round(accepted_per_step, 4),
        "baseline_decode_ms": round(baseline_decode_ms, 4),
        "speculative_decode_ms": round(speculative_decode_ms, 4),
        "speedup_vs_baseline": round(speedup, 4),
        "baseline_tpot_ms": round(baseline_tpot_ms, 4),
        "speculative_tpot_ms": round(tpot_ms, 4),
        "estimated_ttft_ms": round(ttft_ms, 4),
        "estimated_output_tokens_per_second": round(throughput_tokens_s, 4),
        "wasted_draft_tokens": round(wasted_draft_tokens, 4),
        "wasted_draft_ratio": round(wasted_ratio, 6),
        "rollback_pressure": round(rollback_pressure, 4),
        "prefix_reuse_blocks": row.prefix_reuse_blocks,
        "graph_bucket_fit": row.graph_bucket_fit,
        "memory_headroom_gb": row.memory_headroom_gb,
        "scheduler_policy": scheduler,
        "kernel_paths": ["draft-forward", "target-verify", "kv-commit", "rollback-mask", "scheduler-admit"],
        "gpu_evidence_required": ["acceptance_rate", "draft_tokens_wasted", "target_verify_ms", "tpot_ms", "ttft_ms", "kv_blocks_committed", "rollback_count"],
    }


def _source_facts(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "serving_traces": reports.get(SOURCE_REPORTS[0], {}).get("trace_count", 0),
        "kv_cache_scenarios": reports.get(SOURCE_REPORTS[1], {}).get("scenario_count", 0),
        "attention_serving_scenarios": reports.get(SOURCE_REPORTS[2], {}).get("scenario_count", 0),
        "serving_engines": reports.get(SOURCE_REPORTS[3], {}).get("engine_count", 0),
        "cuda_graph_capture_ready": reports.get(SOURCE_REPORTS[4], {}).get("capture_ready_count", 0),
        "profiler_rows": reports.get(SOURCE_REPORTS[5], {}).get("row_count", 0),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# GPUMODE speculative decoding serving",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Status: `{report['status']}`",
        "",
        "| scenario | workload | engine | status | draft | accept | speedup | wasted ratio | scheduler |",
        "|---|---|---|---|---:|---:|---:|---:|---|",
    ]
    for row in report["scenarios"]:
        lines.append(
            f"| {row['scenario_id']} | {row['workload']} | {row['engine_hint']} | {row['status']} | "
            f"{row['draft_width']} | {row['acceptance_rate']} | {row['speedup_vs_baseline']} | "
            f"{row['wasted_draft_ratio']} | {row['scheduler_policy']} |"
        )
    lines.extend(["", "## GPU Host Promotion", ""])
    for command in report["gpu_host_promotion"]["commands"]:
        lines.append(f"- `{command}`")
    return "\n".join(lines).rstrip() + "\n"


def build_speculative_decoding_report() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    reports = {rel: _read_json(rel) for rel in SOURCE_REPORTS}
    scenarios = [_scenario(row) for row in SCENARIOS]
    passed = sum(1 for row in scenarios if row["status"] == "passed")
    engines = sorted({row["engine_hint"] for row in scenarios})
    scheduler_policies = sorted({row["scheduler_policy"] for row in scenarios})
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "speculative-decoding-ready" if len(scenarios) >= 6 and passed >= 4 and len(engines) >= 4 else "needs-work",
        "scenario_count": len(scenarios),
        "passed_scenarios": passed,
        "review_scenarios": len(scenarios) - passed,
        "engine_count": len(engines),
        "engine_hints": engines,
        "scheduler_policy_count": len(scheduler_policies),
        "scheduler_policies": scheduler_policies,
        "min_acceptance_rate": round(min(row["acceptance_rate"] for row in scenarios), 4),
        "max_wasted_draft_ratio": round(max(row["wasted_draft_ratio"] for row in scenarios), 6),
        "max_speedup_vs_baseline": round(max(row["speedup_vs_baseline"] for row in scenarios), 4),
        "source_reports": SOURCE_REPORTS,
        "source_facts": _source_facts(reports),
        "scenarios": scenarios,
        "recommendations": [
            "Teach speculative decoding as a scheduler and verification system, not just a model trick.",
            "Gate promotion on accepted tokens per target verification, rollback pressure, TTFT, TPOT, KV commits, and wasted draft work.",
            "Keep low-acceptance domain-shift cases in the lab so students see when speculative decoding should be disabled.",
            "Run the GPU version in Colab or a remote GPU host with vLLM/SGLang/HF assisted generation traces.",
        ],
        "gpu_host_promotion": {
            "required": True,
            "target_steps": ["draft-forward", "target-verify", "rollback-mask", "kv-commit", "continuous-batching"],
            "commands": [
                "python3 scripts/run_speculative_decoding_serving.py",
                "python3 scripts/verify_speculative_decoding_serving.py",
                "python3 scripts/run_serving_traces.py",
                "python3 scripts/run_serving_engine_comparison.py",
                "nsys profile -o speculative-decoding-serving python3 <speculative_serving_probe.py>",
                "ncu --set full -o speculative-target-verify python3 <target_verify_probe.py>",
                "python3 scripts/run_gpu_promotion_suite.py --run-id speculative-decoding-serving --execute",
            ],
            "note": "Local report models speculative decoding accounting; final acceptance requires measured draft/target serving traces, KV commit telemetry, and profiler evidence on a GPU host or Colab GPU runtime.",
        },
    }
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    return report
