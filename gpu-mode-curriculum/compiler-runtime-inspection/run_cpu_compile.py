"""Execute Inductor compilation of an existing teaching operation on CPU.

Uses a PyTorch 2.4.1 private code-capture hook; not a stable cross-version API.
Compiler failure is a failed report, never an eager fallback performance result.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

REPO = Path(__file__).resolve().parents[2]
OUT = Path(__file__).with_name("reports") / "cpu-compile.json"


def worker():
    import torch
    from torch._inductor.utils import run_and_get_code
    sys.path.insert(0, str(REPO / "gpu-mode-curriculum/custom-ops"))
    sys.path.insert(0, str(REPO / "gpu-kernels-serving-lab"))
    from custom_ops.fused_bias_gelu_residual import reference_bias_gelu_residual
    from common.bench import sample_seconds
    from common.provenance import source_provenance
    torch.set_num_threads(1)
    gen = torch.Generator().manual_seed(161)
    rows = []
    for shape, strided in (((7, 33), False), ((7, 33), True), ((32, 128), False)):
        x = torch.randn((shape[0], shape[1] * (2 if strided else 1)), generator=gen)
        if strided:
            x = x[:, ::2]
        bias = torch.randn(shape[-1], generator=gen)
        residual = torch.randn(shape, generator=gen)
        compiled = torch.compile(reference_bias_gelu_residual, backend="inductor", fullgraph=True)
        start = time.perf_counter()
        result, sources = run_and_get_code(compiled, x, bias, residual)
        first_call = time.perf_counter() - start
        oracle = reference_bias_gelu_residual(x.double(), bias.double(), residual.double()).float()
        torch.testing.assert_close(result, oracle, atol=2e-6, rtol=2e-5)
        # Held-out values reuse the compiled shape/layout, not calibration inputs.
        held = x.clone(memory_format=torch.preserve_format).copy_(x * -3.25)
        if strided:
            held = (x * -3.25).repeat_interleave(2, dim=-1)[:, ::2]
        actual = compiled(held, bias, residual)
        expected = reference_bias_gelu_residual(held.double(), bias.double(), residual.double()).float()
        torch.testing.assert_close(actual, expected, atol=2e-6, rtol=2e-5)
        if not sources:
            raise RuntimeError("compiled execution produced no captured generated source")
        train_inputs = tuple(t.detach().requires_grad_(True) for t in (x, bias, residual))
        upstream = torch.randn(shape, generator=gen)
        training = torch.compile(reference_bias_gelu_residual, backend="inductor", fullgraph=True)

        def step(fn, inputs, grad):
            output = fn(*inputs)
            return output, torch.autograd.grad(output, inputs, grad)

        started = time.perf_counter()
        (train_output, train_grads), train_sources = run_and_get_code(
            lambda: step(training, train_inputs, upstream))
        training_first_call = time.perf_counter() - started
        ref_inputs = tuple(t.detach().double().requires_grad_(True) for t in train_inputs)
        ref_output, ref_grads = step(reference_bias_gelu_residual, ref_inputs, upstream.double())
        torch.testing.assert_close(train_output, ref_output.float(), atol=2e-6, rtol=2e-5)
        grad_errors = {}
        for name, a, b in zip(("input", "bias", "residual"), train_grads, ref_grads):
            torch.testing.assert_close(a, b.float(), atol=2e-6, rtol=2e-5)
            grad_errors[name] = float((a - b.float()).abs().max())
        if len(train_sources) < 2:
            raise RuntimeError("expected captured forward and backward generated modules")
        rows.append({"shape": list(shape), "input_stride": list(x.stride()),
                     "evidence_kind": "measured_cpu", "correct": True,
                     "compile_and_first_call_seconds": first_call,
                     "eager_seconds": sample_seconds(lambda: reference_bias_gelu_residual(x, bias, residual)),
                     "compiled_seconds": sample_seconds(lambda: compiled(x, bias, residual)),
                     "max_abs_error": float((result - oracle).abs().max()),
                     "held_out_max_abs_error": float((actual - expected).abs().max()),
                     "training": {"correct": True, "gradient_max_abs_errors": grad_errors,
                         "compile_and_first_step_seconds": training_first_call,
                         "eager_forward_backward_seconds": sample_seconds(lambda: step(reference_bias_gelu_residual, train_inputs, upstream)),
                         "compiled_forward_backward_seconds": sample_seconds(lambda: step(training, train_inputs, upstream)),
                         "generated_sources": [{"sha256": hashlib.sha256(s.encode()).hexdigest(), "text": s} for s in train_sources]},
                     "generated_sources": [{"sha256": hashlib.sha256(s.encode()).hexdigest(), "text": s} for s in sources]})
    report = {"status": "passed", "rows": rows, "torch_version": torch.__version__,
              "seed": 161, "gpu_execution_accepted": False,
              "compiler": subprocess.run(["g++", "--version"], capture_output=True, text=True, check=True).stdout,
              "scope": "CPU forward and first-order backward Inductor compilation of bias+tanh-GELU+residual; fullgraph forward with compiled autograd backward; FP64 eager oracle; 3 warmups and 10 host-wall samples; first-call timing includes compilation; no optimizer, GPU or application speedup acceptance",
              "provenance": source_provenance(REPO, [Path(__file__)])}
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")


if __name__ == "__main__":
    if "--worker" in sys.argv:
        worker()
    else:
        with tempfile.TemporaryDirectory(prefix="gpu-cpu-compile-") as cache:
            env = dict(os.environ, TORCHINDUCTOR_CACHE_DIR=cache, TORCHINDUCTOR_COMPILE_THREADS="1")
            try:
                # First-use Inductor/AOTAutograd compilation can exceed five
                # minutes on a constrained CPU.  Keep the isolated worker
                # bounded, but do not classify a slow legitimate compile as a
                # compiler failure before the surrounding checkpoint timeout.
                result = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--worker"],
                                        env=env, capture_output=True, text=True, timeout=900)
                if result.returncode:
                    raise RuntimeError(result.stderr)
            except (subprocess.TimeoutExpired, RuntimeError) as exc:
                OUT.parent.mkdir(exist_ok=True)
                OUT.write_text(json.dumps({"status": "failed", "error": str(exc), "rows": [],
                                           "gpu_execution_accepted": False}, indent=2) + "\n")
                raise SystemExit(1)
        print("passed", OUT)
