#!/usr/bin/env python3
"""Verify that the Colab handoff exposes the claim-scoped serving-tail path."""

from __future__ import annotations

import json
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / "scripts" / "run_colab_gpu_handoff_local.sh"
REMOTE = ROOT / "scripts" / "run_colab_gpu_handoff.py"
MANIFEST = ROOT / "gpu-promotion" / "gpu-host-promotion-manifest.json"
LOCAL_REPORT = ROOT / "model-integration" / "reports" / "serving-tail-load-cuda.json"
REPORT = ROOT / "gpu-runs" / "reports" / "colab-handoff-contract.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    local = LOCAL.read_text(encoding="utf-8")
    remote = REMOTE.read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    step = next((row for row in manifest.get("steps", []) if row.get("id") == "serving-tail-load-cuda"), None)
    report = json.loads(LOCAL_REPORT.read_text(encoding="utf-8"))

    require("COLAB_HANDOFF_MODE" in local and '"serving-tail"' in local,
            "local handoff does not expose serving-tail mode")
    require("serving-tail-graphs" in local,
            "local handoff does not expose CUDA-graph tail-load mode")
    require("serving-tail-load-cuda.json" in local,
            "local handoff does not download the serving-tail artifact")
    require('mode == "serving-tail"' in remote,
            "remote handoff does not branch on serving-tail mode")
    require('mode == "serving-tail-graphs"' in remote and "cuda_graph_microbatch" in remote,
            "remote handoff does not branch on CUDA-graph tail-load mode")
    require("model-integration/run_serving_tail_load_cuda.py" in remote,
            "remote handoff does not execute the CUDA tail-load runner")
    require(step is not None, "promotion manifest lacks serving-tail-load-cuda")
    require(step.get("expected_evidence") == ["model-integration/reports/serving-tail-load-cuda.json"],
            "promotion manifest has the wrong tail-load evidence path")
    require(str(report.get("status", "")).startswith("unavailable") and report.get("measured") is False,
            "local tail-load report must remain explicitly unavailable")
    require(report.get("gpu_execution_accepted") is False,
            "local unavailable tail-load report cannot accept GPU execution")
    result = {
        "status": "handoff-contract-valid",
        "evidence_kind": "contract",
        "measured": False,
        "gpu_execution_accepted": False,
        "mode": "serving-tail",
        "expected_evidence": step["expected_evidence"],
        "local_status": report["status"],
        "local_gpu_execution_accepted": report["gpu_execution_accepted"],
        "source_sha256": {
            str(path.relative_to(ROOT.parent)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (LOCAL, REMOTE, MANIFEST, LOCAL_REPORT)
        },
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
