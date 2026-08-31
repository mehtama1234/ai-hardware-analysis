# Profiler-to-roofline evidence: Profiler counters / roofline triage

Query: `nsight roofline dram sm stall counters`

## Build Target

Suspect the next optimization is unclear until counters are mapped to memory, compute, synchronization, launch, or communication limits.

## Starter Files

- `starter.py`: local harness that runs or classifies the starter source.
- `classify_counters.py`: first source file to modify.
- `measure.py`: experiment harness that writes `measurements.json`.
- `tasks.json`: concrete reading, programming, measurement, and comparison tasks.
- `measurements.json`: durable local starter measurement after `python3 measure.py`.
- `measurement-contract.json`: expected evidence shape for this project.
- `project.json`: generated metadata linking lessons, sources, papers, labs, and measurements.

## Existing Lab To Compare Against

- `gpu-kernels-serving-lab/22-gpumode-nsight-roofline`
- `cd ../gpu-kernels-serving-lab/22-gpumode-nsight-roofline && python3 run.py && python3 build_page.py`
- measurement: `22-gpumode-nsight-roofline/out_gpumode_nsight_roofline.json`

## Lessons
- Lesson 111: [Lecture 8: CUDA Performance Checklist](https://www.youtube.com/watch?v=SGhfUhlowB4)
- Lesson 17: [Lecture 97: HipKittens](https://www.youtube.com/watch?v=jsYyF03Fs3o)
- Lesson 97: [Lecture 21: Scan Algorithm Part 2](https://www.youtube.com/watch?v=MH5_FeSSdIE)
- Lesson 102: [Lecture 16: On Hands Profiling](https://www.youtube.com/watch?v=SKV6kDk1s94)

## External Tutorials
- JAX Scaling Book: [How to Profile TPU Programs](https://jax-ml.github.io/scaling-book/profiling/)
- NVIDIA: [CUDA C++ Best Practices Guide](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html)
- JAX Scaling Book: [All About Rooflines](https://jax-ml.github.io/scaling-book/roofline/)
- JAX Scaling Book: [How to Think About GPUs](https://jax-ml.github.io/scaling-book/gpus/)

## Paper Cross-Checks
- SC: Profiling Application-Specific Properties of Irregular Graph Algorithms on GPUs
  - `analysis/per-paper/sc-2025-311.json`
- SC: RedSan: A Redundant Memory Instruction Sanitizer for GPU Programs
  - `analysis/per-paper/sc-2025-427.json`
- ASPLOS: MoE-Lightning: High-Throughput MoE Inference on Memory-constrained GPUs
  - `analysis/per-paper/asplos-2025-024.json`
- ISCA: HPVM-HDC: A Heterogeneous Programming System for Accelerating Hyperdimensional Computing
  - `analysis/per-paper/isca-2025-014.json`

## Local Run

```bash
python3 starter.py
python3 measure.py
```
