#!/usr/bin/env python3
"""Verify GPU-host run import evidence."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "gpu-runs" / "gpu-run-report.json"
REPORT_MD = ROOT / "gpu-runs" / "reports" / "gpu-run-report.md"
IMPORT_LINT = ROOT / "gpu-runs" / "import-lint-report.json"
COLLECTOR = ROOT / "scripts" / "collect_gpu_run.py"
LOCAL_COLLECTOR_SMOKE = ROOT / "gpu-runs" / "imports" / "local-cpu-collector-smoke.json"
SITE_PAGE = ROOT / "site" / "gpu-runs.html"
REQUIRED_STEPS = {
    "cuda-kernel-compile",
    "triton-kernel-sweep",
    "persistent-kernels",
    "parallel-primitives",
    "torch-custom-extension",
    "model-integration-gpu",
    "vllm-serving-trace",
    "flash-attention-backward",
    "sparse-attention-kernels",
    "fused-training-kernels",
    "speculative-decoding-serving",
    "profiler-capture",
    "rocm-hip-port",
    "distributed-collectives",
    "distributed-training-optimizer",
    "full-gpu-regression",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    if not REPORT.exists():
        subprocess.run([sys.executable, "scripts/build_gpu_runs.py"], cwd=ROOT, check=True)
    if not IMPORT_LINT.exists():
        subprocess.run([sys.executable, "scripts/lint_gpu_run_imports.py"], cwd=ROOT, check=True)
    report = load_json(REPORT)
    lint = load_json(IMPORT_LINT)
    coverage = report.get("coverage", {})
    validation = report.get("validation", {})
    rows = report.get("rows", [])
    require(report.get("status") == "import-ready", "GPU run report is not import-ready")
    require(lint.get("status") == "lint-clean", "GPU import lint report is not clean")
    require(lint.get("error_count") == 0, "GPU import lint errors present")
    require(report.get("fixture_count", 0) >= 2, "too few GPU run fixtures")
    require(report.get("import_count", 0) >= 1, "missing collected GPU-run import")
    require(coverage.get("run_count", 0) >= 2, "too few GPU runs")
    require(coverage.get("vendor_count", 0) >= 2, "GPU runs must cover NVIDIA and AMD-style hosts")
    require(coverage.get("sample_run_count", 0) >= 2, "sample GPU fixtures are not marked as samples")
    require(coverage.get("host_collected_run_count", 0) >= 1, "host-collected GPU run import is not marked")
    require(coverage.get("measured_run_count", -1) >= 0, "measured GPU run count missing")
    require(REQUIRED_STEPS.issubset(set(coverage.get("promotion_steps", []))), f"missing GPU promotion steps: {sorted(REQUIRED_STEPS - set(coverage.get('promotion_steps', [])))}")
    require(coverage.get("failed_steps") == 0, "GPU run imports contain failed steps")
    require(coverage.get("unknown_steps") == 0, "GPU run imports contain unknown promotion steps")
    require(validation.get("all_rows_have_evidence") is True, "GPU run rows missing evidence")
    require(validation.get("all_rows_have_metrics") is True, "GPU run rows missing metrics")
    require(REPORT_MD.exists(), "GPU run markdown report missing")
    require((ROOT / "gpu-runs" / "reports" / "import-lint-report.md").exists(), "GPU import lint markdown report missing")
    require(COLLECTOR.exists(), "GPU run collector script missing")
    require(LOCAL_COLLECTOR_SMOKE.exists(), "local collector smoke import missing")
    for row in rows:
        require(row.get("known_promotion_step") is True, f"{row.get('step_id')} is not linked to the promotion manifest")
        require(row.get("metric_count", 0) > 0, f"{row.get('step_id')} missing metric count")
        require(row.get("provenance_kind") in {"sample-fixture", "host-collected", "real-measured"}, f"{row.get('run_id')} missing valid provenance")
        require(isinstance(row.get("measured"), bool), f"{row.get('run_id')} missing measured flag")
    if SITE_PAGE.exists():
        page = SITE_PAGE.read_text(encoding="utf-8")
        require("GPUMODE GPU run imports" in page, "GPU runs site page missing title")
        require("sample-a100-gpu-run" in page and "sample-mi300-gpu-run" in page, "GPU runs site page missing imported runs")
    facts = {
        "runs": coverage["run_count"],
        "vendors": coverage["vendors"],
        "promotion_steps": coverage["promotion_step_count"],
        "imports": report.get("import_count", 0),
        "measured_runs": coverage["measured_run_count"],
        "lint_status": lint["status"],
        "status": report["status"],
    }
    print(json.dumps({"facts": facts, "failures": []}, indent=2))
    print("GPUMODE GPU run import verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
