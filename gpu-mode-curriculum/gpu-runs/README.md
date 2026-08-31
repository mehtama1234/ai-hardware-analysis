# GPUMODE GPU Run Imports

This layer defines the import shape for real accelerator-host validation. It accepts GPU-host run JSON files, links each row back to the GPU promotion manifest, and writes a consolidated report.

Run:

```bash
python3 scripts/build_gpu_runs.py
python3 scripts/verify_gpu_runs.py
```

On a real GPU host, collect an import file first:

```bash
torchrun --nproc_per_node=2 scripts/run_distributed_collectives_benchmark.py
python3 scripts/collect_gpu_run.py --run-id h100-node-001-2026-08-30
python3 scripts/build_gpu_runs.py
python3 scripts/verify_gpu_runs.py
```

Sample fixtures under `gpu-runs/fixtures/` model the expected structure for NVIDIA A100 and AMD MI300 hosts. Replace or extend them with real host exports after running CUDA, Triton, ROCm/HIP, profiler, serving, distributed collective, and full-regression promotion steps.
