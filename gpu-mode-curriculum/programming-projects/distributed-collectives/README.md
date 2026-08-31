# Distributed communication: Distributed communication / collective bottleneck

Query: `nccl nvshmem all reduce bandwidth topology`

## Build Target

Suspect collective latency, bandwidth regime, topology, NCCL/NVSHMEM runtime readiness, or lack of multi-device parallelism.

## Starter Files

- `starter.py`: local harness that runs or classifies the starter source.
- `collective_model.py`: first source file to modify.
- `measure.py`: experiment harness that writes `measurements.json`.
- `tasks.json`: concrete reading, programming, measurement, and comparison tasks.
- `measurements.json`: durable local starter measurement after `python3 measure.py`.
- `measurement-contract.json`: expected evidence shape for this project.
- `project.json`: generated metadata linking lessons, sources, papers, labs, and measurements.

## Existing Lab To Compare Against

- `gpu-kernels-serving-lab/26-gpumode-distributed-communication`
- `cd ../gpu-kernels-serving-lab/26-gpumode-distributed-communication && python3 run.py && python3 build_page.py`
- measurement: `26-gpumode-distributed-communication/out_gpumode_distributed_communication.json`

## Lessons
- Lesson 1: [Lecture 113: Every Microsecond Matters: Achieving Near Speed-of-Light Latency in GPU Collectives](https://www.youtube.com/watch?v=TZnJYRTSGVk)
- Lesson 101: [Lecture 17: NCCL](https://www.youtube.com/watch?v=T22e3fgit-A)
- Lesson 57: [Lecture 57: CuTe](https://www.youtube.com/watch?v=vzUhbDO_0qk)
- Lesson 90: [Lecture 28: Liger Kernel - Efficient Triton Kernels for LLM Training](https://www.youtube.com/watch?v=gWble4FreV4)

## External Tutorials
- JAX Scaling Book: [All About Rooflines](https://jax-ml.github.io/scaling-book/roofline/)
- JAX Scaling Book: [How to Parallelize a Transformer for Training](https://jax-ml.github.io/scaling-book/training/)
- Hugging Face: [Text Generation Inference Documentation](https://huggingface.co/docs/text-generation-inference/index)
- JAX Scaling Book: [Programming TPUs in JAX](https://jax-ml.github.io/scaling-book/jax-stuff/)

## Paper Cross-Checks
- HPCA: TidalMesh: Topology-Driven AllReduce Collective Communication for Mesh Topology
  - `analysis/per-paper/hpca-2025-058.json`
- HPCA: Enhancing Large-Scale AI Training Efficiency: The C4 Solution for Real-Time Anomaly Detection and Communication Optimization
  - `analysis/per-paper/hpca-2025-024.json`
- ASPLOS: Concerto: Automatic Communication Optimization and Scheduling for Large-Scale Deep Learning
  - `analysis/per-paper/asplos-2025-028.json`
- HOTCHIPS: UB-mesh: An New Interconnection Technology for Large AI SuperNode
  - `analysis/per-paper/hotchips-2025-021.json`

## Local Run

```bash
python3 starter.py
python3 measure.py
```
