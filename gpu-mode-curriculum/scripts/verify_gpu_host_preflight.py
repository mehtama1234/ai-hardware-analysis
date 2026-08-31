#!/usr/bin/env python3
"""Verify GPU-host preflight report."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "gpu-handoff" / "gpu-host-preflight.json"
REPORT_MD = ROOT / "gpu-handoff" / "reports" / "gpu-host-preflight.md"
SITE_PAGE = ROOT / "site" / "gpu-host-preflight.html"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    if not REPORT.exists():
        subprocess.run([sys.executable, "scripts/run_gpu_host_preflight.py"], cwd=ROOT, check=True)
    report = load_json(REPORT)
    steps = report.get("steps", [])
    require(report.get("status") == "preflight-complete", "GPU host preflight did not complete")
    require(report.get("step_count") == len(steps) >= 9, "preflight step count mismatch")
    require(report.get("runnable_step_count", -1) + report.get("blocked_step_count", -1) == len(steps), "preflight runnable/blocked counts mismatch")
    require(report.get("capabilities", {}).get("python") is True, "preflight must detect python")
    for step in steps:
        require(step.get("step_id"), "preflight step missing id")
        require(step.get("command_count", 0) > 0, f"{step.get('step_id')} missing commands")
        require(isinstance(step.get("missing_capabilities"), list), f"{step.get('step_id')} missing capability list")
    require(REPORT_MD.exists(), "preflight markdown report missing")
    if SITE_PAGE.exists():
        page = SITE_PAGE.read_text(encoding="utf-8")
        require("GPUMODE GPU host preflight" in page, "preflight site page missing title")
        require("cuda-kernel-compile" in page and "persistent-kernels" in page and "parallel-primitives" in page and "flash-attention-backward" in page and "sparse-attention-kernels" in page and "fused-training-kernels" in page and "speculative-decoding-serving" in page and "full-gpu-regression" in page, "preflight site page missing steps")
    facts = {
        "status": report["status"],
        "accelerator_ready": report["accelerator_ready"],
        "steps": report["step_count"],
        "runnable": report["runnable_step_count"],
        "blocked": report["blocked_step_count"],
    }
    print(json.dumps({"facts": facts, "failures": []}, indent=2))
    print("GPUMODE GPU host preflight verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
