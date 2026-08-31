# Triton kernels: Triton custom-kernel / autotuning path

Query: `triton fused softmax autotune`

## Build Target

Suspect block sizes, masks, fusion boundaries, or compiler-generated kernel choices.

## Starter Files

- `starter.py`: local harness that runs or classifies the starter source.
- `kernel.py`: first source file to modify.
- `measure.py`: experiment harness that writes `measurements.json`.
- `tasks.json`: concrete reading, programming, measurement, and comparison tasks.
- `measurements.json`: durable local starter measurement after `python3 measure.py`.
- `measurement-contract.json`: expected evidence shape for this project.
- `project.json`: generated metadata linking lessons, sources, papers, labs, and measurements.

## Existing Lab To Compare Against

- `gpu-kernels-serving-lab/17-gpumode-triton-autotune`
- `cd ../gpu-kernels-serving-lab/17-gpumode-triton-autotune && python3 run.py && python3 build_page.py`
- measurement: `23-gpumode-shared-memory-gemm/out_gpumode_shared_memory_gemm.json`

## Lessons
- Lesson 13: [Lecture 101: Learning CUTLASS the hard way](https://www.youtube.com/watch?v=jGouxuAHIfQ)
- Lesson 26: [Lecture 89: cuTile (from friends at NVIDIA)](https://www.youtube.com/watch?v=_b4I4rKpsGA)
- Lesson 35: [Lecture 79 Mirage (MPK): Compiling LLMs into Mega Kernels](https://www.youtube.com/watch?v=sXDdRCy137c)
- Lesson 39: [Lecture 75 [ScaleML Series] GPU Programming Fundamentals + ThunderKittens](https://www.youtube.com/watch?v=Cl2B_hmg4gA)

## External Tutorials
- Triton: [Triton Tutorials](https://triton-lang.org/main/getting-started/tutorials/)
- Triton: [Fused Softmax Tutorial](https://triton-lang.org/main/getting-started/tutorials/02-fused-softmax.html)
- NVIDIA: [CUDA C++ Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/index.html)
- AMD ROCm: [Introduction to the HIP Programming Model](https://rocm.docs.amd.com/projects/HIP/en/latest/understand/programming_model.html)

## Paper Cross-Checks
- MLSys 2025: FlexAttention: A Programming Model for Generating Optimized Attention Kernels
  - `analysis/per-paper/mlsys-2025-015.json`
- DAC: A Cross-model Fusion-aware Framework for Optimizing (gather-matmul-scatter)s Workload
  - `analysis/per-paper/dac-2025-196.json`
- HPCA: VQ-LLM: High-performance Code Generation for Vector Quantization Augmented LLM Inference
  - `analysis/per-paper/hpca-2025-003.json`
- ISCA: LUT Tensor Core: A Software-Hardware Co-Design for LUT-Based Low-Bit LLM Inference
  - `analysis/per-paper/isca-2025-079.json`

## Local Run

```bash
python3 starter.py
python3 measure.py
```
