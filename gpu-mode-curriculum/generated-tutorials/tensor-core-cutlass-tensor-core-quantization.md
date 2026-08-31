# Tensor Core / CUTLASS matmul path

Query: `tensor core quantization`

## Diagnosis

Suspect missing Tensor Core eligibility, low-precision numerical drift, layout mismatch, or missing CUTLASS/CuTe production kernel coverage.

Next action: Run gpu-kernels-serving-lab/24-gpumode-tensor-core-cutlass and compare its latest artifact against the recommended lessons.

## Read First
- JAX Scaling Book: [How to Think About GPUs](https://jax-ml.github.io/scaling-book/gpus/)
  - Use this as the hardware mental model for SMs, HBM, Tensor Cores, and GPU interconnects.
- NVIDIA: [CUDA C++ Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/index.html)
  - Use this as the official CUDA programming-model reference behind the memory, warp, and matmul kernel labs.
- Hugging Face: [Transformers Quantization](https://huggingface.co/docs/transformers/en/quantization/overview)
  - Use this to compare framework quantization choices with the local numerical-drift and kernel-readiness labs.
- NVIDIA: [CUDA C++ Best Practices Guide](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html)
  - Use this to turn profiler symptoms into concrete CUDA optimization checks.

## GPUMODE Anchors
- Lesson 80: [Lecture 36: CUTLASS and Flash Attention 3](https://www.youtube.com/watch?v=JwUcZwPOCpA)
- Lesson 2: [Lecture 112: Production Megakernels for Real-World Inference](https://www.youtube.com/watch?v=loZ4xQ5RZuU)
- Lesson 4: [Lecture 110: The 4-bitter lesson: Balancing Stability and Performance in NVFP4 RL](https://www.youtube.com/watch?v=wiaUh82NEoE)
- Lesson 9: [Lecture 105: cuDNN mxfp8 attention](https://www.youtube.com/watch?v=HcnybHRbTcc)
- Lesson 12: [Lecture 102: quartet v2](https://www.youtube.com/watch?v=E0G3hf4DneA)

## Run The Lab

Lab: `gpu-kernels-serving-lab/24-gpumode-tensor-core-cutlass`

```bash
cd ../gpu-kernels-serving-lab/24-gpumode-tensor-core-cutlass && python3 run.py && python3 build_page.py
```

## Measurement To Inspect

- Artifact: `24-gpumode-tensor-core-cutlass/out_gpumode_tensor_core_cutlass.json`
- Summary: Tensor Core kernels buy throughput by using low-precision inputs with controlled accumulation. On this CPU proxy, fp16 relative L2 error is 0.035858% and bf16 relative L2 error is 0.287636% against fp32.

## Steps
- Read JAX Scaling Book - How to Think About GPUs and write down the claimed bottleneck model.
- Open GPUMODE lesson #80: Lecture 36: CUTLASS and Flash Attention 3 and extract the kernel/runtime concept that should be measurable.
- Run gpu-kernels-serving-lab/24-gpumode-tensor-core-cutlass and preserve the generated JSON artifact.
- Compare 24-gpumode-tensor-core-cutlass/out_gpumode_tensor_core_cutlass.json against the source model and the GPUMODE lesson concept.
- Use LUT Tensor Core: A Software-Hardware Co-Design for LUT-Based Low-Bit LLM Inference as the research cross-check for whether this bottleneck appears in current AI systems work.

## Success Checks
- Correctness status is passed or the artifact records an explicit environment-gated skip.
- The generated tutorial page names the same bottleneck class as the workbench profile.
- The measurement summary explains what changed or why real GPU execution was unavailable.
- At least one GPUMODE lesson, external tutorial source, and corpus paper can be traversed from the profile page.

## Research Cross-Checks
- ISCA: LUT Tensor Core: A Software-Hardware Co-Design for LUT-Based Low-Bit LLM Inference
  - `analysis/per-paper/isca-2025-079.json`
- MLSYS 2025: TurboAttention: Efficient Attention Approximation for High Throughput LLMs
  - `analysis/per-paper/mlsys-2025-025.json`
- DAC: Precon: A Precision-Convertible Architecture for Accelerating Quantized Deep Learning Models across Various Domains Including LLMs
  - `analysis/per-paper/dac-2025-273.json`
- HPCA: VQ-LLM: High-performance Code Generation for Vector Quantization Augmented LLM Inference
  - `analysis/per-paper/hpca-2025-003.json`
