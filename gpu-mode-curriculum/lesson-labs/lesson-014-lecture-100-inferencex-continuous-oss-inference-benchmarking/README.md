# Lesson Lab 14: Lecture 100: InferenceX Continuous OSS Inference Benchmarking

Source video: https://www.youtube.com/watch?v=kPBTBl7xvEY

## Why This Lab Exists

This lab closes per-lesson coverage for the GPUMODE curriculum. It starts as a local CPU proxy so it can be verified on this machine, and it is structured for promotion into CUDA, Triton, HIP, JAX, or serving-runtime code.

## Coverage Before This Generated Lab

- Existing deep lab candidates: `gpumode-lab-01-coalescing, gpumode-lab-03-triton-autotune, gpumode-lab-04-online-softmax, gpumode-lab-06-vllm-scheduler, gpumode-lab-08-nsight-to-roofline, gpumode-lab-09-shared-memory-gemm, gpumode-lab-12-distributed-communication`
- Existing programming projects that directly anchor this lesson: `vllm-kv-scheduler`

## Lesson Signals

- Topics: `profiling, attention, serving`
- Concepts: `kv cache, autotuning, quantized numerics, compiler lowering, profiling workflow`
- Tools: `torch.compile, vLLM, ROCm/HIP, TVM`

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
