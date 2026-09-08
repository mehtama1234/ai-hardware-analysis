"""Run paired attention training correctness; not a performance benchmark."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
import torch

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "gpu-kernels-serving-lab"))
from common.provenance import source_provenance
from model_integration.attention_training import run_training_case


def main():
    threads = torch.get_num_threads()
    torch.set_num_threads(1)
    try:
        cases = [run_training_case(length) for length in (1, 17, 33)]
    finally:
        torch.set_num_threads(threads)
    report = {"timestamp": datetime.now(timezone.utc).isoformat(), "cases": cases,
        "torch_version": torch.__version__, "gpu_execution_accepted": False,
        "scope": "nine paired CPU optimizer steps on synthetic regression targets; no convergence, model quality, GPU speedup or serving claim",
        "provenance": source_provenance(REPO, [Path(__file__),
            HERE / "model_integration/attention_training.py", HERE / "model_integration/tiny_transformer.py",
            HERE.parent / "flash-attention-backward/flash_attention_backward/reference.py",
            HERE.parent / "flash-attention-backward/flash_attention_backward/recomputed.py"])}
    output = HERE / "reports/attention-training-cpu.json"
    output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(f"passed {len(cases)} cases, {sum(len(case['steps']) for case in cases)} paired training steps")


if __name__ == "__main__":
    main()
