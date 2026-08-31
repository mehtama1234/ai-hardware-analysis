#!/usr/bin/env python3
"""Replay serving traces and write TTFT/TPOT/KV-cache reports."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SERVING_ROOT = ROOT / "serving-traces"
FIXTURES = SERVING_ROOT / "fixtures"
REPORT_JSON = SERVING_ROOT / "reports" / "serving-trace-report.json"
REPORT_MD = SERVING_ROOT / "reports" / "serving-trace-report.md"
sys.path.insert(0, str(SERVING_ROOT))

from serving_traces import replay_trace  # noqa: E402


def load_trace(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Serving Trace Replay Report",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Traces: `{report['trace_count']}`",
        f"Policies: `{', '.join(report['policy_ids'])}`",
        "",
        "| trace | policy | completed | throughput tok/s | p50 TTFT ms | p95 TTFT ms | mean TPOT ms | peak KV blocks | prefix blocks saved |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for trace in report["traces"]:
        for policy in trace["policies"]:
            summary = policy["summary"]
            lines.append(
                "| "
                f"{trace['trace_id']} | {summary['policy']} | {summary['completed_count']}/{summary['request_count']} | "
                f"{summary['output_tokens_per_second']} | {summary['p50_ttft_ms']} | {summary['p95_ttft_ms']} | "
                f"{summary['mean_tpot_ms']} | {summary['peak_live_kv_blocks']} | {summary['prefix_cache_blocks_saved']} |"
            )
    lines.extend(["", "## Checks", ""])
    for trace in report["traces"]:
        checks = ", ".join(f"{name}={value}" for name, value in trace["checks"].items())
        lines.append(f"- `{trace['trace_id']}`: `{trace['status']}` ({checks})")
    return "\n".join(lines).rstrip() + "\n"


def build_report() -> dict[str, Any]:
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    traces = [replay_trace(load_trace(path)) for path in sorted(FIXTURES.glob("*.json"))]
    policy_ids = sorted({policy["summary"]["policy"] for trace in traces for policy in trace["policies"]})
    comparisons = []
    for trace in traces:
        by_policy = {policy["summary"]["policy"]: policy["summary"] for policy in trace["policies"]}
        static = by_policy["static-batching"]
        continuous = by_policy["continuous-batching-prefix-cache"]
        comparisons.append(
            {
                "trace_id": trace["trace_id"],
                "throughput_speedup": round(
                    continuous["output_tokens_per_second"] / max(static["output_tokens_per_second"], 1e-9),
                    4,
                ),
                "p50_ttft_delta_ms": round(continuous["p50_ttft_ms"] - static["p50_ttft_ms"], 4),
                "prefix_cache_blocks_saved": continuous["prefix_cache_blocks_saved"],
                "peak_live_kv_blocks": continuous["peak_live_kv_blocks"],
            }
        )
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "trace_count": len(traces),
        "policy_ids": policy_ids,
        "passed_traces": sum(1 for trace in traces if trace["status"] == "passed"),
        "failed_traces": sum(1 for trace in traces if trace["status"] != "passed"),
        "comparisons": comparisons,
        "traces": traces,
    }
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    return report


def main() -> int:
    report = build_report()
    print(
        f"wrote {REPORT_JSON.relative_to(ROOT)} and {REPORT_MD.relative_to(ROOT)} "
        f"({report['passed_traces']}/{report['trace_count']} traces passed)"
    )
    return 0 if report["failed_traces"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
