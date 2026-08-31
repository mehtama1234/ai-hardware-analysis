# Triton custom-kernel / autotuning path Roadmap

Query: `triton fused softmax`

## Outcome

Suspect block sizes, masks, fusion boundaries, or compiler-generated kernel choices.

## Phase 1: Source Model
- Triton: [Triton Tutorials](https://triton-lang.org/main/getting-started/tutorials/)
- Triton: [Fused Softmax Tutorial](https://triton-lang.org/main/getting-started/tutorials/02-fused-softmax.html)
- NVIDIA: [CUDA C++ Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/index.html)

## Phase 2: GPUMODE Lessons
- Lesson 13: [Lecture 101: Learning CUTLASS the hard way](https://www.youtube.com/watch?v=jGouxuAHIfQ)
  - concepts: memory coalescing, shared memory tiling, warp execution, occupancy, tensor cores
- Lesson 26: [Lecture 89: cuTile (from friends at NVIDIA)](https://www.youtube.com/watch?v=_b4I4rKpsGA)
  - concepts: memory coalescing, shared memory tiling, warp execution, tensor cores, online softmax
- Lesson 35: [Lecture 79 Mirage (MPK): Compiling LLMs into Mega Kernels](https://www.youtube.com/watch?v=sXDdRCy137c)
  - concepts: shared memory tiling, tensor cores, online softmax, kernel fusion, autotuning
- Lesson 39: [Lecture 75 [ScaleML Series] GPU Programming Fundamentals + ThunderKittens](https://www.youtube.com/watch?v=Cl2B_hmg4gA)
  - concepts: shared memory tiling, warp execution, occupancy, tensor cores, kv cache
- Lesson 59: [Lecture 55: Modular’s unified device accelerator language](https://www.youtube.com/watch?v=5gPG7SXoBag)
  - concepts: shared memory tiling, tensor cores, autotuning, compiler lowering, profiling workflow
- Lesson 62: [Bonus Lecture: AMD Developer Challenge](https://www.youtube.com/watch?v=DOXx3QRZuR8)
  - concepts: memory coalescing, shared memory tiling, tensor cores, kv cache, kernel fusion

## Phase 3: Program And Run

- Lab: `gpu-kernels-serving-lab/17-gpumode-triton-autotune`

```bash
cd ../gpu-kernels-serving-lab/17-gpumode-triton-autotune && python3 run.py && python3 build_page.py
```

## Phase 4: Evidence

- Measurement artifact: `23-gpumode-shared-memory-gemm/out_gpumode_shared_memory_gemm.json`
- Measurement summary: A 8x8 tile raises modeled arithmetic intensity from 0.2462 to 1.7778 FLOP/byte and cuts modeled global-memory traffic by 86.154%.

## Phase 5: Research Cross-Check
- MLSys 2025: FlexAttention: A Programming Model for Generating Optimized Attention Kernels
  - `analysis/per-paper/mlsys-2025-015.json`
- DAC: A Cross-model Fusion-aware Framework for Optimizing (gather-matmul-scatter)s Workload
  - `analysis/per-paper/dac-2025-196.json`
- HPCA: VQ-LLM: High-performance Code Generation for Vector Quantization Augmented LLM Inference
  - `analysis/per-paper/hpca-2025-003.json`
- ISCA: LUT Tensor Core: A Software-Hardware Co-Design for LUT-Based Low-Bit LLM Inference
  - `analysis/per-paper/isca-2025-079.json`
- MLSYS 2025: TileLink: Generating Efficient Compute-Communication Overlapping Kernels using Tile-Centric Primitives
  - `analysis/per-paper/mlsys-2025-002.json`
