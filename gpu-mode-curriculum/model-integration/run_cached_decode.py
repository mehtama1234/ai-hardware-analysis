"""CPU cached-block replay: fixed supplied inputs, not generated text or HTTP serving."""
import copy
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import torch

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "gpu-kernels-serving-lab"))
from common.provenance import source_provenance
from model_integration.tiny_transformer import TinyTransformerBlock


def run():
    threads = torch.get_num_threads()
    torch.set_num_threads(1)
    try:
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(111)
            base = TinyTransformerBlock(32, 4, False, "sdpa").eval()
        generator = torch.Generator().manual_seed(112)
        x = torch.randn((2, 25, 32), generator=generator)
        rows = []
        with torch.no_grad():
            expected = base(x)
            for backend in ("materialized", "sdpa", "recomputed"):
                model = copy.deepcopy(base)
                model.attention_backend = backend
                sessions = []
                for repetition in range(9):  # two complete warm-up sessions
                    start = time.perf_counter()
                    output, cache = model.forward_cached(x[:, :17])
                    prefill = time.perf_counter() - start
                    torch.testing.assert_close(output, expected[:, :17], atol=2e-6, rtol=2e-5)
                    token_samples = []
                    for position in range(17, 25):
                        start = time.perf_counter()
                        output, cache = model.forward_cached(x[:, position:position + 1], cache)
                        token_samples.append(time.perf_counter() - start)
                        torch.testing.assert_close(output, expected[:, position:position + 1], atol=2e-6, rtol=2e-5)
                    if repetition >= 2:
                        sessions.append({"prefill_seconds": prefill, "decode_seconds": token_samples,
                            "final_cache_length": cache[0].shape[-2],
                            "cache_logical_bytes": sum(t.numel() * t.element_size() for t in cache)})
                rows.append({"backend": backend, "evidence_kind": "measured_cpu",
                    "status": "passed", "warmup_sessions": 2, "sessions": sessions})
    finally:
        torch.set_num_threads(threads)
    report = {"timestamp": datetime.now(timezone.utc).isoformat(), "rows": rows,
        "shape": {"batch": 2, "prefill": 17, "decode_steps": 8, "hidden": 32, "heads": 4},
        "model_seed": 111, "data_seed": 112, "torch_version": torch.__version__, "cpu_threads": 1,
        "reference": "full causal PyTorch SDPA block with identical weights and supplied input vectors",
        "timing_scope": "CPU block calls including input slicing, concatenation and cache allocation; excludes correctness checks; no network, queue or tokenizer",
        "limitations": ["not generated tokens", "not TTFT or serving throughput", "cache bytes are logical payload, not peak memory", "contiguous concatenating cache, not paged or shared", "no GPU execution"],
        "gpu_execution_accepted": False,
        "provenance": source_provenance(REPO, [Path(__file__), HERE / "model_integration/tiny_transformer.py",
            HERE.parent / "flash-attention-backward/flash_attention_backward/reference.py",
            HERE.parent / "flash-attention-backward/flash_attention_backward/recomputed.py",
            REPO / "gpu-kernels-serving-lab/common/provenance.py"])}
    output = HERE / "reports/cached-decode-cpu.json"
    output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print("passed 3 backends, 7 recorded replays each, 8 checked decode steps per replay")


if __name__ == "__main__":
    run()
