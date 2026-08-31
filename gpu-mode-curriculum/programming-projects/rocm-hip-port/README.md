# ROCm/HIP portability: ROCm/HIP portability path

Query: `rocm hip cuda portability wmma`

## Build Target

Suspect CUDA-specific runtime calls, warp-size assumptions, WMMA/Tensor Core dependencies, or missing ROCm compiler/runtime support.

## Starter Files

- `starter.py`: local harness that runs or classifies the starter source.
- `kernel.hip.cpp`: first source file to modify.
- `measure.py`: experiment harness that writes `measurements.json`.
- `tasks.json`: concrete reading, programming, measurement, and comparison tasks.
- `measurements.json`: durable local starter measurement after `python3 measure.py`.
- `measurement-contract.json`: expected evidence shape for this project.
- `project.json`: generated metadata linking lessons, sources, papers, labs, and measurements.

## Existing Lab To Compare Against

- `gpu-kernels-serving-lab/25-gpumode-rocm-hip-portability`
- `cd ../gpu-kernels-serving-lab/25-gpumode-rocm-hip-portability && python3 run.py && python3 build_page.py`
- measurement: `25-gpumode-rocm-hip-portability/out_gpumode_rocm_hip_portability.json`

## Lessons
- Lesson 80: [Lecture 36: CUTLASS and Flash Attention 3](https://www.youtube.com/watch?v=JwUcZwPOCpA)
- Lesson 57: [Lecture 57: CuTe](https://www.youtube.com/watch?v=vzUhbDO_0qk)
- Lesson 70: [Lecture 46: Distributed GEMM](https://www.youtube.com/watch?v=NHRTCQBZokg)
- Lesson 95: [Lecture 23: Tensor Cores](https://www.youtube.com/watch?v=hQ9GPnV0-50)

## External Tutorials
- AMD ROCm: [HIP Documentation](https://rocm.docs.amd.com/projects/HIP/en/latest/)
- AMD ROCm: [Introduction to the HIP Programming Model](https://rocm.docs.amd.com/projects/HIP/en/latest/understand/programming_model.html)

## Paper Cross-Checks
- SC: A Study of Performance Portability of Low-bit Fused Matrix-Vector Multiplication Kernels in SYCL
  - `analysis/per-paper/sc-2025-165.json`
- SC: DiOMP-Offloading: Toward Portable Distributed Heterogeneous OpenMP
  - `analysis/per-paper/sc-2025-310.json`
- SC: Mojo: MLIR-based Performance-Portable HPC Science Kernels on GPUs for the Python Ecosystem
  - `analysis/per-paper/sc-2025-117.json`
- SC: Scabbard: LLVM Instrumentation-aided Race Checking in CPU/GPU Unified Memory for AMD GPUs
  - `analysis/per-paper/sc-2025-255.json`

## Local Run

```bash
python3 starter.py
python3 measure.py
```
