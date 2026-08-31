#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "distributed-collectives" / "reports" / "collective-benchmark-run.json"
REPORT_MD = ROOT / "distributed-collectives" / "reports" / "collective-benchmark-run.md"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    if not REPORT.exists():
        subprocess.run([sys.executable, "scripts/run_distributed_collectives_benchmark.py"], cwd=ROOT, check=True)
    report = load_json(REPORT)
    metrics = report.get("aggregate_metrics", {})
    require(report.get("status") == "passed" or str(report.get("status", "")).startswith("skipped:"), "benchmark status must be passed or an explicit skip")
    require(report.get("world_size", 0) >= 1, "world size missing")
    require(report.get("backend"), "backend missing")
    require(metrics.get("collective_scenarios", 0) >= 6, "model scenario coverage missing")
    require(metrics.get("collective_count", 0) >= 5, "model collective coverage missing")
    require(metrics.get("bandwidth_efficiency", 0) > 0, "bandwidth efficiency metric missing")
    require(metrics.get("overlap_gain", 0) >= 0, "overlap gain metric missing")
    if report.get("status") == "passed":
        require(report.get("measured") is True, "passed benchmark must be measured")
        require(metrics.get("torchrun") is True, "passed benchmark must be launched with torchrun")
        require(metrics.get("accelerator_ready") is True, "passed benchmark must have accelerator runtime")
        require(metrics.get("measured_collectives", 0) >= 3, "too few measured collectives")
        require(metrics.get("nccl_or_rccl") is True, "passed benchmark must use NCCL/RCCL-family backend")
        require(metrics.get("best_bus_gbps", 0) > 0, "passed benchmark missing bandwidth")
    else:
        require(report.get("skip_reason"), "skipped benchmark needs reason")
    require(REPORT_MD.exists(), "benchmark markdown report missing")
    print(
        json.dumps(
            {
                "facts": {
                    "status": report.get("status"),
                    "world_size": report.get("world_size"),
                    "backend": report.get("backend_family"),
                    "measured": report.get("measured"),
                    "measured_collectives": metrics.get("measured_collectives", 0),
                },
                "failures": [],
            },
            indent=2,
        )
    )
    print("GPUMODE distributed collectives benchmark verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
