"""Record CPU operation samples and saved-tensor payloads; not GPU peak memory."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import torch

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "gpu-kernels-serving-lab"))
from common.bench import sample_seconds
from common.provenance import source_provenance
from flash_attention_backward.reference import attention
from flash_attention_backward.recomputed import recomputed_attention


def run():
    previous_threads = torch.get_num_threads()
    torch.set_num_threads(1)
    rows = []
    try:
        for length in (32, 64, 128):
            generator = torch.Generator().manual_seed(19)
            inputs = tuple(torch.randn((1, length, 8), generator=generator).requires_grad_()
                           for _ in range(3))
            upstream = torch.randn((1, length, 8), generator=generator)
            reference = attention(*(tensor.double() for tensor in inputs), causal=True)
            reference_grads = torch.autograd.grad(reference, inputs, upstream.double())
            for name, operation in (("materialized", attention), ("recomputed", recomputed_attention)):
                saved = []
                def pack(tensor):
                    saved.append({"shape": list(tensor.shape), "dtype": str(tensor.dtype),
                                  "logical_bytes": tensor.numel() * tensor.element_size()})
                    return tensor
                with torch.autograd.graph.saved_tensors_hooks(pack, lambda tensor: tensor):
                    output = operation(*inputs, causal=True)
                gradients = torch.autograd.grad(output, inputs, upstream)
                torch.testing.assert_close(output.double(), reference, atol=2e-6, rtol=2e-5)
                for actual, expected in zip(gradients, reference_grads):
                    torch.testing.assert_close(actual, expected, atol=2e-6, rtol=2e-5)
                def step():
                    result = operation(*inputs, causal=True)
                    torch.autograd.grad(result, inputs, upstream)
                rows.append({"implementation": name, "sequence_length": length,
                    "evidence_kind": "measured_cpu", "correctness": "passed",
                    "seed": 19, "dtype": "float32", "head_dim": 8, "causal": True,
                    "block": 32 if name == "recomputed" else None,
                    "saved_tensors": saved,
                    "saved_logical_bytes": sum(item["logical_bytes"] for item in saved),
                    "samples_seconds": sample_seconds(step, warmup=2, repeat=7),
                    "warmup": 2, "repeat": 7,
                    "timing_scope": "synchronous CPU forward+backward including Python dispatch and output/gradient allocation"})
    finally:
        torch.set_num_threads(previous_threads)
    report = {"timestamp": datetime.now(timezone.utc).isoformat(), "rows": rows,
        "torch_version": torch.__version__, "measurement_cpu_threads": 1,
        "provenance": source_provenance(REPO, [Path(__file__),
            HERE / "flash_attention_backward/reference.py", HERE / "flash_attention_backward/recomputed.py",
            REPO / "gpu-kernels-serving-lab/common/bench.py",
            REPO / "gpu-kernels-serving-lab/common/provenance.py"]),
        "memory_scope": "sum of logical tensor payloads observed through autograd save hooks; includes retained inputs/output; not unique storage, allocation delta, process RSS or peak device memory",
        "gpu_execution_accepted": False}
    output = HERE / "reports/executable-reference-cpu.json"
    output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    for row in rows:
        print(row["sequence_length"], row["implementation"], row["saved_logical_bytes"], "saved logical bytes")
    return report


if __name__ == "__main__":
    run()
