"""Compile the existing transformer; verify three paired optimizer steps on CPU."""
import hashlib
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUT = HERE / "reports/compiled-training-cpu.json"


def worker():
    import torch
    from torch._inductor.utils import run_and_get_code
    from model_integration.attention_training import run_training_case
    sys.path.insert(0, str(REPO / "gpu-kernels-serving-lab"))
    from common.provenance import source_provenance
    torch.set_num_threads(1)
    started = time.perf_counter()
    case, sources = run_and_get_code(lambda: run_training_case(17, 3, compile_candidate=True, benchmark=True))
    if len(sources) < 2:
        raise RuntimeError("expected generated forward and backward modules")
    report = {"status": "passed", "cases": [case], "torch_version": torch.__version__,
              "compile_validation_and_benchmark_seconds": time.perf_counter() - started,
              "generated_sources": [{"sha256": hashlib.sha256(s.encode()).hexdigest(), "text": s} for s in sources],
              "gpu_execution_accepted": False,
              "scope": "CPU whole-transformer forward compiled fullgraph with AOTAutograd backward; three paired SGD momentum steps check output/loss/input and all parameter gradients/updates/momentum; optimizer remains eager; ten reset-state timed training steps per backend after three warmups; total wall time includes compilation and validation, not a throughput metric; synthetic data, no quality claim",
              "provenance": source_provenance(REPO, [Path(__file__)])}
    OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")


if __name__ == "__main__":
    if "--worker" in sys.argv:
        worker()
    else:
        with tempfile.TemporaryDirectory(prefix="gpu-compiled-training-") as cache:
            env = dict(os.environ, TORCHINDUCTOR_CACHE_DIR=cache, TORCHINDUCTOR_COMPILE_THREADS="1")
            try:
                result = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--worker"],
                                        env=env, capture_output=True, text=True, timeout=900)
                if result.returncode:
                    raise RuntimeError(result.stderr)
            except (subprocess.TimeoutExpired, RuntimeError) as exc:
                OUT.write_text(json.dumps({"status": "failed", "error": str(exc), "cases": [],
                                           "gpu_execution_accepted": False,
                                           "provenance": {"source_sha256": {
                                               str(Path(__file__).resolve().relative_to(REPO.parent)): hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
                                           }}}, indent=2) + "\n")
                raise SystemExit(1)
        print("passed", OUT)
