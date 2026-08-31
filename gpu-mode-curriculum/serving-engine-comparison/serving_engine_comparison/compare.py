from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TRACE_REPORT = ROOT / "serving-traces" / "reports" / "serving-trace-report.json"
OUT = ROOT / "serving-engine-comparison"
REPORT_JSON = OUT / "serving-engine-comparison.json"
REPORT_MD = OUT / "reports" / "serving-engine-comparison.md"


ENGINES: list[dict[str, Any]] = [
    {
        "id": "vllm",
        "label": "vLLM",
        "runtime": "python-cuda-rocm",
        "features": ["paged-attention", "continuous-batching", "prefix-cache", "openai-api", "tensor-parallel"],
        "throughput_multiplier": 1.18,
        "ttft_multiplier": 0.92,
        "memory_multiplier": 0.82,
        "operability": 0.84,
        "portability": 0.78,
        "gpu_requirements": ["nvidia_smi or rocm_smi", "cuda or rocm wheel", "model weights"],
    },
    {
        "id": "tgi",
        "label": "Hugging Face TGI",
        "runtime": "rust-python-cuda-rocm",
        "features": ["continuous-batching", "hf-hub", "tensor-parallel", "quantization", "openai-compatible-api"],
        "throughput_multiplier": 1.08,
        "ttft_multiplier": 1.02,
        "memory_multiplier": 0.9,
        "operability": 0.92,
        "portability": 0.86,
        "gpu_requirements": ["container runtime", "cuda or rocm image", "hf token for gated models"],
    },
    {
        "id": "sglang",
        "label": "SGLang",
        "runtime": "python-cuda",
        "features": ["radix-cache", "structured-output", "speculative-decoding", "continuous-batching", "openai-api"],
        "throughput_multiplier": 1.14,
        "ttft_multiplier": 0.88,
        "memory_multiplier": 0.86,
        "operability": 0.78,
        "portability": 0.68,
        "gpu_requirements": ["nvidia_smi", "cuda wheel", "serving benchmark client"],
    },
    {
        "id": "tensorrt-llm",
        "label": "TensorRT-LLM",
        "runtime": "compiled-cuda",
        "features": ["engine-build", "tensor-parallel", "fp8", "inflight-batching", "kernel-fusion"],
        "throughput_multiplier": 1.32,
        "ttft_multiplier": 0.82,
        "memory_multiplier": 0.78,
        "operability": 0.62,
        "portability": 0.46,
        "gpu_requirements": ["nvidia_smi", "cuda", "tensorrt-llm", "engine build cache"],
    },
    {
        "id": "hf-transformers",
        "label": "HF Transformers Baseline",
        "runtime": "python-pytorch",
        "features": ["hf-hub", "eager-debugging", "torch-compile-option", "quantization-baseline"],
        "throughput_multiplier": 0.62,
        "ttft_multiplier": 1.2,
        "memory_multiplier": 1.12,
        "operability": 0.88,
        "portability": 0.9,
        "gpu_requirements": ["python", "torch", "transformers"],
    },
]


SCENARIOS: list[dict[str, Any]] = [
    {
        "id": "interactive-chat",
        "trace_id": "short-chat",
        "weights": {"throughput": 0.25, "ttft": 0.35, "memory": 0.15, "operability": 0.15, "portability": 0.1},
    },
    {
        "id": "long-context-rag",
        "trace_id": "long-context-prefix-cache",
        "weights": {"throughput": 0.2, "ttft": 0.15, "memory": 0.35, "operability": 0.15, "portability": 0.15},
    },
    {
        "id": "mixed-prefill-decode",
        "trace_id": "mixed-prefill-decode",
        "weights": {"throughput": 0.3, "ttft": 0.2, "memory": 0.2, "operability": 0.15, "portability": 0.15},
    },
    {
        "id": "offline-throughput",
        "trace_id": "mixed-prefill-decode",
        "weights": {"throughput": 0.5, "ttft": 0.05, "memory": 0.2, "operability": 0.15, "portability": 0.1},
    },
    {
        "id": "portable-amd-nvidia",
        "trace_id": "long-context-prefix-cache",
        "weights": {"throughput": 0.2, "ttft": 0.1, "memory": 0.2, "operability": 0.2, "portability": 0.3},
    },
]


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _continuous_summary(trace_report: dict[str, Any], trace_id: str) -> dict[str, Any]:
    for trace in trace_report.get("traces", []):
        if trace.get("trace_id") != trace_id:
            continue
        for policy in trace.get("policies", []):
            summary = policy.get("summary", {})
            if summary.get("policy") == "continuous-batching-prefix-cache":
                return summary
    return {}


def _score_engine(engine: dict[str, Any], summary: dict[str, Any], weights: dict[str, float]) -> dict[str, Any]:
    baseline_tps = float(summary.get("output_tokens_per_second", 0.0))
    baseline_ttft = float(summary.get("p50_ttft_ms", 0.0))
    baseline_kv_blocks = float(summary.get("peak_live_kv_blocks", 0.0))
    estimated_tps = baseline_tps * engine["throughput_multiplier"]
    estimated_ttft = baseline_ttft * engine["ttft_multiplier"]
    estimated_kv_blocks = baseline_kv_blocks * engine["memory_multiplier"]
    throughput_score = min(engine["throughput_multiplier"] / 1.32, 1.0)
    ttft_score = min(0.82 / engine["ttft_multiplier"], 1.0)
    memory_score = min(0.78 / engine["memory_multiplier"], 1.0)
    score = (
        weights["throughput"] * throughput_score
        + weights["ttft"] * ttft_score
        + weights["memory"] * memory_score
        + weights["operability"] * engine["operability"]
        + weights["portability"] * engine["portability"]
    )
    return {
        "engine_id": engine["id"],
        "engine": engine["label"],
        "score": round(score, 4),
        "estimated_output_tokens_per_second": round(estimated_tps, 4),
        "estimated_p50_ttft_ms": round(estimated_ttft, 4),
        "estimated_peak_kv_blocks": round(estimated_kv_blocks, 4),
        "features": engine["features"],
        "gpu_requirements": engine["gpu_requirements"],
        "subscores": {
            "throughput": round(throughput_score, 4),
            "ttft": round(ttft_score, 4),
            "memory": round(memory_score, 4),
            "operability": engine["operability"],
            "portability": engine["portability"],
        },
    }


def build_engine_comparison() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    trace_report = load_json(TRACE_REPORT, {})
    rows = []
    scenario_recommendations = []
    for scenario in SCENARIOS:
        summary = _continuous_summary(trace_report, scenario["trace_id"])
        engine_rows = sorted(
            (_score_engine(engine, summary, scenario["weights"]) for engine in ENGINES),
            key=lambda row: (-row["score"], row["engine_id"]),
        )
        rows.append(
            {
                "scenario_id": scenario["id"],
                "trace_id": scenario["trace_id"],
                "weights": scenario["weights"],
                "baseline_policy": summary.get("policy", "missing"),
                "baseline_output_tokens_per_second": summary.get("output_tokens_per_second", 0),
                "baseline_p50_ttft_ms": summary.get("p50_ttft_ms", 0),
                "baseline_peak_kv_blocks": summary.get("peak_live_kv_blocks", 0),
                "engines": engine_rows,
            }
        )
        scenario_recommendations.append(
            {
                "scenario_id": scenario["id"],
                "recommended_engine": engine_rows[0]["engine_id"] if engine_rows else "missing",
                "runner_up": engine_rows[1]["engine_id"] if len(engine_rows) > 1 else "missing",
                "why": _why_recommended(scenario["id"], engine_rows[0] if engine_rows else {}),
            }
        )
    engine_wins: dict[str, int] = {}
    for recommendation in scenario_recommendations:
        engine = recommendation["recommended_engine"]
        engine_wins[engine] = engine_wins.get(engine, 0) + 1
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "comparison-ready" if len(rows) == len(SCENARIOS) and all(row["baseline_policy"] != "missing" for row in rows) else "incomplete",
        "engine_count": len(ENGINES),
        "scenario_count": len(SCENARIOS),
        "source_trace_report": str(TRACE_REPORT.relative_to(ROOT)),
        "engine_ids": [engine["id"] for engine in ENGINES],
        "scenario_recommendations": scenario_recommendations,
        "engine_wins": engine_wins,
        "scenarios": rows,
        "gpu_host_promotion": {
            "required": True,
            "target_steps": ["serving-trace-replay", "profiler-capture", "full-gpu-regression"],
            "note": "Scores are deterministic local estimates from trace replay; production acceptance requires measured vLLM/TGI/SGLang/TensorRT-LLM runs on a GPU host.",
        },
    }
    write_json(REPORT_JSON, report)
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    return report


def _why_recommended(scenario_id: str, row: dict[str, Any]) -> str:
    if scenario_id == "interactive-chat":
        return f"{row.get('engine', 'missing')} balances low TTFT with enough throughput for request/response latency."
    if scenario_id == "long-context-rag":
        return f"{row.get('engine', 'missing')} wins on KV-cache pressure and long-context memory efficiency."
    if scenario_id == "offline-throughput":
        return f"{row.get('engine', 'missing')} prioritizes output-token throughput over interactive latency."
    if scenario_id == "portable-amd-nvidia":
        return f"{row.get('engine', 'missing')} has the strongest cross-vendor and operations-weighted score."
    return f"{row.get('engine', 'missing')} has the best weighted score for mixed prefill/decode traffic."


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Serving Engine Comparison",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Status: `{report['status']}`",
        f"Engines: `{report['engine_count']}`",
        f"Scenarios: `{report['scenario_count']}`",
        f"Source trace report: `{report['source_trace_report']}`",
        "",
        "## Scenario Recommendations",
        "",
        "| scenario | recommended | runner up | why |",
        "|---|---|---|---|",
    ]
    for row in report["scenario_recommendations"]:
        lines.append(f"| {row['scenario_id']} | {row['recommended_engine']} | {row['runner_up']} | {row['why']} |")
    lines.extend(["", "## Engine Scores", "", "| scenario | engine | score | tok/s | p50 TTFT ms | peak KV blocks | features |", "|---|---|---:|---:|---:|---:|---|"])
    for scenario in report["scenarios"]:
        for engine in scenario["engines"]:
            lines.append(
                f"| {scenario['scenario_id']} | {engine['engine']} | {engine['score']} | "
                f"{engine['estimated_output_tokens_per_second']} | {engine['estimated_p50_ttft_ms']} | "
                f"{engine['estimated_peak_kv_blocks']} | {', '.join(engine['features'][:4])} |"
            )
    lines.extend(["", "## GPU Host Promotion", "", report["gpu_host_promotion"]["note"]])
    return "\n".join(lines).rstrip() + "\n"
