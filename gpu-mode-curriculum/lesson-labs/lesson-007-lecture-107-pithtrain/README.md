# Lesson Lab 7: Lecture 107: PithTrain

Source video: https://www.youtube.com/watch?v=tBYm9PI5Jw0

## Why This Lab Exists

This lab closes per-lesson coverage for the GPUMODE curriculum. It starts as a local CPU proxy so it can be verified on this machine, and it is structured for promotion into CUDA, Triton, HIP, JAX, or serving-runtime code.

## Coverage Before This Generated Lab

- Existing deep lab candidates: `gpumode-lab-01-coalescing, gpumode-lab-02-warp-reductions, gpumode-lab-03-triton-autotune, gpumode-lab-04-online-softmax, gpumode-lab-05-torch-compile, gpumode-lab-06-vllm-scheduler, gpumode-lab-07-quantized-kernels, gpumode-lab-08-nsight-to-roofline, gpumode-lab-09-shared-memory-gemm, gpumode-lab-10-tensor-core-cutlass, gpumode-lab-11-rocm-hip-portability, gpumode-lab-12-distributed-communication`
- Existing programming projects that directly anchor this lesson: `none`

## Lesson Signals

- Topics: `cuda, triton, profiling, quantization, serving, hardware, distributed`
- Concepts: `autotuning, quantized numerics, compiler lowering, profiling workflow`
- Tools: `Triton, PyTorch, CUTLASS/CuTe, ROCm/HIP, TVM`

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
