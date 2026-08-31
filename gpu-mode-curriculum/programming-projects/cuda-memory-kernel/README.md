# CUDA kernels: Memory bandwidth / layout bottleneck

Query: `cuda memory coalescing shared memory roofline`

## Build Target

Suspect memory layout, HBM bandwidth, KV-cache growth, or avoidable materialization before changing math.

## Starter Files

- `starter.py`: local harness that runs or classifies the starter source.
- `kernel.cu`: first source file to modify.
- `measure.py`: experiment harness that writes `measurements.json`.
- `tasks.json`: concrete reading, programming, measurement, and comparison tasks.
- `measurements.json`: durable local starter measurement after `python3 measure.py`.
- `measurement-contract.json`: expected evidence shape for this project.
- `project.json`: generated metadata linking lessons, sources, papers, labs, and measurements.

## Existing Lab To Compare Against

- `gpu-kernels-serving-lab/23-gpumode-shared-memory-gemm`
- `cd ../gpu-kernels-serving-lab/23-gpumode-shared-memory-gemm && python3 run.py && python3 build_page.py`
- measurement: `23-gpumode-shared-memory-gemm/out_gpumode_shared_memory_gemm.json`

## Lessons
- Lesson 115: [Lecture 4 Compute and Memory Basics](https://www.youtube.com/watch?v=lTmYrKwjSOU)
- Lesson 2: [Lecture 112: Production Megakernels for Real-World Inference](https://www.youtube.com/watch?v=loZ4xQ5RZuU)
- Lesson 17: [Lecture 97: HipKittens](https://www.youtube.com/watch?v=jsYyF03Fs3o)
- Lesson 16: [Lecture 98: GPU Observability](https://www.youtube.com/watch?v=-6FlMJ-AP74)

## External Tutorials
- JAX Scaling Book: [All About Rooflines](https://jax-ml.github.io/scaling-book/roofline/)
- JAX Scaling Book: [All About Transformer Inference](https://jax-ml.github.io/scaling-book/inference/)
- JAX Scaling Book: [How to Think About GPUs](https://jax-ml.github.io/scaling-book/gpus/)
- NVIDIA: [CUDA C++ Best Practices Guide](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html)

## Paper Cross-Checks
- ISCA: Hybe: GPU-NPU Hybrid System for Efficient LLM Inference with Million-Token Context Window
  - `analysis/per-paper/isca-2025-080.json`
- ISCA: Insights into DeepSeek-V3: Scaling Challenges and Reflections on Hardware for AI Architectures
  - `analysis/per-paper/isca-2025-130.json`
- MICRO: Stratum: System-Hardware Co-Design with Tiered Monolithic 3D-Stackable DRAM for Efficient MoE Serving
  - `analysis/per-paper/micro-2025-012.json`
- SC: Benchmark-driven Models for Energy Analysis and Attribution of GPU-Accelerated Supercomputing
  - `analysis/per-paper/sc-2025-029.json`

## Local Run

```bash
python3 starter.py
python3 measure.py
```
