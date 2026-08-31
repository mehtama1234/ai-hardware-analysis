"""Session 09: vLLM serving readiness and benchmark placeholder.

This session is intentionally strict: if vLLM is not installed or no accelerator is
visible, it records a skip artifact instead of substituting a different serving engine.
"""

from __future__ import annotations

import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.gpu_info import collect_inventory


HERE = Path(__file__).resolve().parent


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> None:
    import torch  # type: ignore

    has_vllm = importlib.util.find_spec("vllm") is not None
    has_cuda = torch.cuda.is_available()
    if not has_vllm:
        result = {
            "status": "skipped",
            "reason": "vLLM is not installed in this Python environment.",
            "recommended_next": "Install vLLM in a GPU-enabled environment for real serving benchmarks.",
            "boundary": (
                "This page records vLLM readiness only. It does not benchmark serving throughput "
                "until vLLM and a supported accelerator backend are available."
            ),
        }
    elif not has_cuda:
        result = {
            "status": "skipped",
            "reason": "vLLM is installed, but no CUDA device is visible to PyTorch.",
            "recommended_next": "Expose a CUDA GPU or use a vLLM-supported backend, then rerun this session.",
            "boundary": (
                "vLLM exists, but the current machine cannot run the intended GPU serving path."
            ),
        }
    else:
        # Keep the first vLLM slice conservative. Later work can add a subprocess server and load generator.
        result = {
            "status": "ready",
            "reason": "vLLM and CUDA are available; benchmark implementation is the next task.",
            "recommended_next": "Launch vLLM OpenAI-compatible server and run the local load generator.",
            "boundary": "Readiness is proven; throughput is not measured yet.",
        }

    out = {
        "session": "09-vllm-serving",
        "timestamp": now(),
        "inventory": collect_inventory("09-vllm-serving"),
        "result": result,
    }
    path = HERE / "out_vllm_serving.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("wrote", path.name, result["status"])


if __name__ == "__main__":
    main()

