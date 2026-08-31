#!/usr/bin/env python3
"""Verify the GPU-host promotion manifest."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "gpu-promotion" / "gpu-host-promotion-manifest.json"
RUNBOOK = ROOT / "gpu-promotion" / "reports" / "gpu-host-promotion-runbook.md"
SITE_PAGE = ROOT / "site" / "gpu-promotion.html"
REQUIRED_STEPS = {
    "cuda-kernel-compile",
    "triton-kernel-sweep",
    "tensor-core-gemm",
    "persistent-kernels",
    "parallel-primitives",
    "torch-custom-extension",
    "model-integration-gpu",
    "vllm-serving-trace",
    "attention-serving-stack",
    "flash-attention-backward",
    "sparse-attention-kernels",
    "fused-training-kernels",
    "speculative-decoding-serving",
    "profiler-capture",
    "rocm-hip-port",
    "distributed-collectives",
    "full-gpu-regression",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    if not MANIFEST.exists():
        subprocess.run([sys.executable, "scripts/build_gpu_promotion.py"], cwd=ROOT, check=True)
    manifest = load_json(MANIFEST)
    steps = manifest.get("steps", [])
    step_ids = {step.get("id") for step in steps}
    require(REQUIRED_STEPS.issubset(step_ids), f"missing promotion steps: {sorted(REQUIRED_STEPS - step_ids)}")
    require(manifest.get("step_count") == len(steps), "promotion step count mismatch")
    require(manifest.get("ready_on_gpu_host", 0) >= 4, "expected GPU-host promotion steps on this machine")
    require(manifest.get("local_capabilities", {}).get("python") is True, "python capability missing")
    for step in steps:
        require(step.get("commands"), f"{step.get('id')} missing commands")
        require(step.get("expected_evidence"), f"{step.get('id')} missing expected evidence")
        require(step.get("validation"), f"{step.get('id')} missing validation")
        require(step.get("status") in {"ready-on-this-host", "ready-on-gpu-host"}, f"{step.get('id')} invalid status")
    require(RUNBOOK.exists(), "missing GPU-host promotion runbook")
    runbook = RUNBOOK.read_text(encoding="utf-8")
    require("GPU Host Promotion Runbook" in runbook, "runbook missing title")
    require("cuda-kernel-compile" in runbook and "persistent-kernels" in runbook and "parallel-primitives" in runbook and "flash-attention-backward" in runbook and "sparse-attention-kernels" in runbook and "fused-training-kernels" in runbook and "speculative-decoding-serving" in runbook and "full-gpu-regression" in runbook, "runbook missing key steps")
    if SITE_PAGE.exists():
        page = SITE_PAGE.read_text(encoding="utf-8")
        require("GPUMODE GPU promotion" in page, "GPU promotion site page missing title")
        require("cuda-kernel-compile" in page and "tensor-core-gemm" in page and "persistent-kernels" in page and "parallel-primitives" in page and "attention-serving-stack" in page and "flash-attention-backward" in page and "sparse-attention-kernels" in page and "fused-training-kernels" in page and "speculative-decoding-serving" in page and "profiler-capture" in page, "GPU promotion site page missing steps")
    facts = {
        "steps": manifest["step_count"],
        "ready_on_this_host": manifest["ready_on_this_host"],
        "ready_on_gpu_host": manifest["ready_on_gpu_host"],
        "missing_accelerator_caps": sorted(
            name
            for name in ["nvcc", "hipcc", "nvidia_smi", "nsys", "ncu", "rocprof"]
            if not manifest.get("local_capabilities", {}).get(name)
        ),
    }
    print(json.dumps({"facts": facts, "failures": []}, indent=2))
    print("GPUMODE GPU promotion verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
