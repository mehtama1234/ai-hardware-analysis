#!/usr/bin/env python3
"""Compare two claim-scoped GPU serving tail-load reports."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from run_serving_tail_load_cuda import tail_report_contract  # noqa: E402


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def compare(eager: dict, graphs: dict, *, eager_path: Path, graph_path: Path) -> dict:
    levels = eager.get("concurrency_levels", [])
    graph_levels = graphs.get("concurrency_levels", [])
    rows = []
    for left, right in zip(eager.get("rows", []), graphs.get("rows", [])):
        if left["concurrency"] != right["concurrency"]:
            raise ValueError("reports have different concurrency row ordering")
        p95_eager = left["latency_ms"]["p95_nearest_rank"]
        p95_graph = right["latency_ms"]["p95_nearest_rank"]
        wave_eager = left["wave_elapsed_ms"]
        wave_graph = right["wave_elapsed_ms"]
        tps_eager = left["output_tokens_per_second"]
        tps_graph = right["output_tokens_per_second"]
        rows.append({
            "concurrency": left["concurrency"],
            "eager_p50_ms": left["latency_ms"]["p50"],
            "graph_p50_ms": right["latency_ms"]["p50"],
            "eager_p95_ms": p95_eager,
            "graph_p95_ms": p95_graph,
            "p95_improvement_ratio": p95_eager / max(p95_graph, 1e-9),
            "eager_wave_ms": wave_eager,
            "graph_wave_ms": wave_graph,
            "wave_improvement_ratio": wave_eager / max(wave_graph, 1e-9),
            "eager_tokens_per_second": tps_eager,
            "graph_tokens_per_second": tps_graph,
            "throughput_improvement_ratio": tps_graph / max(tps_eager, 1e-9),
            "eager_batch_modes": left["batch_modes"],
            "graph_batch_modes": right["batch_modes"],
            "eager_output_parity": left["output_parity"],
            "graph_output_parity": right["output_parity"],
        })
    checks = {
        "both_reports_passed": eager.get("status") == "passed" and graphs.get("status") == "passed",
        "both_reports_measured_gpu": all(
            report.get("measured") is True and report.get("gpu_execution_accepted") is True
            for report in (eager, graphs)
        ),
        "same_device": eager.get("device_name") == graphs.get("device_name"),
        "same_load_contract": levels == graph_levels and eager.get("requests_per_level") == graphs.get("requests_per_level"),
        "eager_contract": tail_report_contract(eager),
        "graph_contract": tail_report_contract(graphs),
        "all_output_parity": all(row["eager_output_parity"] and row["graph_output_parity"] for row in rows),
        "graph_vectorized_above_concurrency_one": any(
            row["concurrency"] > 1 and any("vectorized" in mode for mode in row["graph_batch_modes"])
            for row in rows
        ),
        "graph_p95_not_worse_at_majority_levels": sum(
            row["graph_p95_ms"] <= row["eager_p95_ms"] for row in rows
        ) >= max(1, (len(rows) + 1) // 2),
    }
    return {
        "experiment": "serving_tail_load_comparison",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "passed" if all(checks.values()) else "failed",
        "evidence_kind": "measured_gpu",
        "device_name": eager.get("device_name"),
        "concurrency_levels": levels,
        "requests_per_level": eager.get("requests_per_level"),
        "eager_mode": eager.get("mode"),
        "graph_mode": graphs.get("mode"),
        "rows": rows,
        "checks": checks,
        "scope": "paired single-process loopback HTTP sweeps on one accelerator; untrained model; no production capacity or multi-GPU claim",
        "source_sha256": {
            str(eager_path): hashlib.sha256(eager_path.read_bytes()).hexdigest(),
            str(graph_path): hashlib.sha256(graph_path.read_bytes()).hexdigest(),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--eager", type=Path, required=True)
    parser.add_argument("--graphs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = compare(load(args.eager), load(args.graphs), eager_path=args.eager, graph_path=args.graphs)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "checks": report["checks"]}, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
