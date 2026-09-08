"""Training-block latency and optional CUDA allocator peak, with no CPU fallback."""
import argparse
import copy
import json
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

import torch

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "gpu-kernels-serving-lab"))
from common.bench import sample_seconds
from common.provenance import source_provenance
from model_integration.tiny_transformer import TinyTransformerBlock


def benchmark(device="cpu", sequence=64, repeat=7):
    if device not in ("cpu", "cuda") or sequence < 1 or repeat < 1:
        raise ValueError("device must be cpu/cuda and sequence/repeat positive")
    if device == "cuda" and not torch.cuda.is_available():
        return {"status": "unavailable", "requested_device": "cuda", "rows": [],
                "reason": "torch.cuda.is_available() is false", "gpu_execution_accepted": False}
    with torch.random.fork_rng(devices=[]):
        torch.manual_seed(91)
        base = TinyTransformerBlock(32, 4, False, attention_backend="sdpa")
    generator = torch.Generator().manual_seed(92)
    input_cpu = torch.randn((2, sequence, 32), generator=generator)
    target_cpu = torch.randn((2, sequence, 32), generator=generator)
    reference = copy.deepcopy(base).double()
    ref_input = input_cpu.double().requires_grad_()
    ref_out = reference(ref_input)
    (ref_out - target_cpu.double()).square().mean().backward()
    rows = []
    sync = (lambda: torch.cuda.synchronize()) if device == "cuda" else None
    for backend in ("materialized", "sdpa", "recomputed"):
        model = copy.deepcopy(base).to(device)
        model.attention_backend = backend
        x = input_cpu.to(device).detach().requires_grad_()
        target = target_cpu.to(device)
        output = model(x)
        (output - target).square().mean().backward()
        comparisons = {"output": (output.detach().cpu().double(), ref_out.detach()),
                       "input_gradient": (x.grad.cpu().double(), ref_input.grad)}
        for (name, param), (_, ref_param) in zip(model.named_parameters(), reference.named_parameters()):
            if param.grad is None or ref_param.grad is None:
                raise AssertionError(f"missing gradient: {name}")
            comparisons[f"gradient:{name}"] = (param.grad.cpu().double(), ref_param.grad)
        errors = {}
        for name, (actual, expected) in comparisons.items():
            torch.testing.assert_close(actual, expected, atol=3e-6, rtol=3e-5)
            if not torch.isfinite(actual).all():
                raise AssertionError(f"nonfinite {name}")
            errors[name] = float((actual - expected).abs().max())
        del comparisons, output

        def step():
            model.zero_grad(set_to_none=True)
            x.grad = None
            (model(x) - target).square().mean().backward()

        samples = sample_seconds(step, warmup=2, repeat=repeat, synchronize=sync)
        model.zero_grad(set_to_none=True)
        x.grad = None
        memory = {"status": "unavailable", "reason": "CPU allocator peak not instrumented"}
        if device == "cuda":
            sync()
            baseline = torch.cuda.memory_allocated()
            torch.cuda.reset_peak_memory_stats()
            step()
            sync()
            peak = torch.cuda.max_memory_allocated()
            memory = {"status": "measured_gpu", "baseline_allocated_bytes": baseline,
                      "peak_allocated_bytes": peak, "increment_above_baseline_bytes": peak - baseline,
                      "scope": "PyTorch allocated tensor memory during one forward/backward after warmup; excludes cached reservation and non-PyTorch allocations"}
        rows.append({"backend": backend, "status": "passed", "evidence_kind": f"measured_{'gpu' if device == 'cuda' else 'cpu'}",
            "errors_vs_cpu_fp64": errors, "atol": 3e-6, "rtol": 3e-5,
            "samples_seconds": samples, "median_seconds": statistics.median(samples),
            "warmup": 2, "repeat": repeat, "memory": memory})
        # Do not retain the previous backend's device tensors in the next peak.
        del step, model, x, target, param, ref_param
    return {"status": "passed", "requested_device": device, "rows": rows,
        "shape": [2, sequence, 32], "heads": 4, "dtype": "float32", "model_seed": 91, "data_seed": 92,
        "timing_scope": "host wall clock: zero gradients, forward, MSE loss, backward; inputs preallocated; no optimizer step; CUDA synchronized when requested",
        "gpu_execution_accepted": device == "cuda",
        "acceptance_scope": "this small training-block experiment only; not fused custom kernels or full curriculum acceptance"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    parser.add_argument("--sequence", type=int, default=64)
    parser.add_argument("--repeat", type=int, default=7)
    args = parser.parse_args()
    threads = torch.get_num_threads()
    tf32 = torch.backends.cuda.matmul.allow_tf32
    torch.set_num_threads(1)
    torch.backends.cuda.matmul.allow_tf32 = False
    try:
        report = benchmark(args.device, args.sequence, args.repeat)
    finally:
        torch.set_num_threads(threads)
        torch.backends.cuda.matmul.allow_tf32 = tf32
    report.update({"timestamp": datetime.now(timezone.utc).isoformat(), "torch_version": torch.__version__,
        "torch_cuda_build": torch.version.cuda, "cpu_threads": 1, "allow_tf32": False,
        "device_name": torch.cuda.get_device_name() if args.device == "cuda" and torch.cuda.is_available() else None,
        "provenance": source_provenance(REPO, [Path(__file__), HERE / "model_integration/tiny_transformer.py",
            HERE.parent / "flash-attention-backward/flash_attention_backward/recomputed.py",
            HERE.parent / "flash-attention-backward/flash_attention_backward/reference.py",
            HERE.parent / "autotune-db/autotune-db.json",
            REPO / "gpu-kernels-serving-lab/common/bench.py", REPO / "gpu-kernels-serving-lab/common/provenance.py"])})
    path = HERE / f"reports/attention-benchmark-{args.device}.json"
    path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(report["status"], path)
    for row in report["rows"]:
        print(row["backend"], row["median_seconds"], "seconds")
    return 0 if report["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
