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
