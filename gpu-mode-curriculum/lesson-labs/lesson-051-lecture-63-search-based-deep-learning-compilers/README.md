# Lesson Lab 51: Lecture 63: Search-Based Deep Learning Compilers

Source video: https://www.youtube.com/watch?v=_aT2eo-0uWk

## Why This Lab Exists

This lab closes per-lesson coverage for the GPUMODE curriculum. It starts as a local CPU proxy so it can be verified on this machine, and it is structured for promotion into CUDA, Triton, HIP, JAX, or serving-runtime code.

## Coverage Before This Generated Lab

- Existing deep lab candidates: `gpumode-lab-01-coalescing, gpumode-lab-02-warp-reductions, gpumode-lab-04-online-softmax, gpumode-lab-07-quantized-kernels, gpumode-lab-09-shared-memory-gemm, gpumode-lab-10-tensor-core-cutlass, gpumode-lab-11-rocm-hip-portability`
- Existing programming projects that directly anchor this lesson: `none`

## Lesson Signals

- Topics: `cuda`
- Concepts: `memory coalescing, shared memory tiling, kernel fusion, autotuning, compiler lowering, profiling workflow`
- Tools: `CUDA, PyTorch, Nsight, TVM`

## Local Run

```bash
python3 starter.py
python3 measure.py
```

## Files

- `lab.py`: lesson-specific proxy program.
- `starter.py`: executable entry point.
- `measure.py`: writes `measurements.json`.
- `measurement-contract.json`: required evidence shape.
- `tasks.json`: reading, coding, measurement, promotion, and comparison tasks.
