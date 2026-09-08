# GPUMODE Kernel Benchmarks

This layer adds a real benchmark harness for the core kernel families implied by the GPUMODE curriculum:

- vector copy and strided memory access;
- reductions;
- softmax;
- layernorm;
- matrix multiplication;
- fused MLP block.

The local runner uses PyTorch tensor implementations when available and CPU fallback code otherwise. CUDA and Triton source files are included as accelerator-facing starting points. On this machine, `nvcc`, `hipcc`, and `nvidia-smi` are not available, so accelerator compilation/runtime checks are recorded as explicit caveats.

Run:

```bash
python3 scripts/build_kernel_benchmark_plan.py
python3 scripts/run_kernel_benchmarks.py
python3 scripts/verify_kernel_benchmarks.py
```

Outputs:

- `kernel-benchmarks/plan.json`
- `kernel-benchmarks/PLAN.md`
- `kernel-benchmarks/reports/kernel-benchmark-report.json`
- `kernel-benchmarks/reports/kernel-benchmark-report.md`
- `kernel-benchmarks/kernels/cuda/*.cu`
- `kernel-benchmarks/kernels/triton/*.py`

## Native CUDA promotion

On a CUDA host, the local PyTorch harness can be complemented by the executable
family probe:

```bash
python3 gpu-mode-curriculum/kernel-benchmarks/run_native.py
```

`native_family_runner.cu` launches shared-memory reduction, numerically stable
row softmax, and row layernorm kernels on a T4/Ampere-compatible CUDA runtime.
It compares reductions with double-precision host references and compares
softmax/layernorm elementwise, recording seven CUDA-event samples per family.
The output is `reports/native-family-execution.json`; unavailable toolchains are
reported explicitly and are never treated as native GPU passes.

The fused-MLP family has a separate native probe:

```bash
python3 gpu-mode-curriculum/kernel-benchmarks/run_native_mlp.py
```

It executes a `16x128x256` two-linear-layer GELU block, compares every output
against a host double-precision reference, and records seven CUDA-event
samples in `reports/native-mlp-execution.json`.
