"""Run eager-vs-Inductor paired training equivalence on a CUDA device."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import torch

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUT = HERE / "reports/compiled-training-cuda.json"
sys.path.insert(0, str(REPO / "gpu-kernels-serving-lab"))


def main() -> int:
    if not torch.cuda.is_available():
        report = {"status": "unavailable", "gpu_execution_accepted": False,
                  "reason": "torch.cuda.is_available() is false"}
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        return 2

    from common.provenance import source_provenance
    from model_integration.attention_training import run_training_case

    previous_threads = torch.get_num_threads()
    previous_tf32 = torch.backends.cuda.matmul.allow_tf32
    torch.set_num_threads(1)
    torch.backends.cuda.matmul.allow_tf32 = False
    try:
        case = run_training_case(sequence=17, steps=3, compile_candidate=True,
                                 benchmark=True, device="cuda")
    finally:
        torch.set_num_threads(previous_threads)
        torch.backends.cuda.matmul.allow_tf32 = previous_tf32

    report = {
        "status": case["status"],
        "gpu_execution_accepted": case["status"] == "passed" and case["device"] == "cuda",
        "device_name": torch.cuda.get_device_name(),
        "torch_version": torch.__version__,
        "torch_cuda_build": torch.version.cuda,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "case": case,
        "scope": "CUDA eager SDPA versus fullgraph Inductor SDPA; three optimizer steps compare outputs, losses, input and parameter gradients, updated parameters and SGD momentum; benchmark includes synchronized forward/backward/optimizer step after compilation",
        "provenance": source_provenance(REPO, [
            Path(__file__), HERE / "model_integration/attention_training.py",
            HERE / "model_integration/tiny_transformer.py",
            HERE.parent / "flash-attention-backward/flash_attention_backward/recomputed.py",
            HERE.parent / "flash-attention-backward/flash_attention_backward/reference.py",
            HERE.parent / "autotune-db/autotune-db.json",
            HERE.parent / "custom-ops/custom_ops/fused_bias_gelu_residual.py",
            REPO / "gpu-kernels-serving-lab/common/provenance.py",
        ]),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print("passed", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
