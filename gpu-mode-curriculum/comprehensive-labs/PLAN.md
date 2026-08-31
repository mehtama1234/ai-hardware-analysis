# GPUMODE Comprehensive Lab Code Plan

This is the one-by-one implementation plan for the real code layer. The 118 per-lesson labs remain coverage scaffolds; these comprehensive labs are the deliberate programs to build and extend.

Lessons covered by comprehensive labs: 118 / 118

## 1. Memory hierarchy, coalescing, bank conflicts, occupancy, roofline

- ID: `comp-lab-01-memory-hierarchy`
- Code: `comprehensive-labs/gpumode_lab_suite/memory_hierarchy.py`
- Module: `gpumode_lab_suite.memory_hierarchy`
- Lessons mapped: 116
- Reason: Most lessons touch CUDA/hardware. This lab makes memory traffic, bank conflicts, occupancy, and roofline constraints measurable before deeper kernels.
- First lesson anchors:
  - Lesson 13: Lecture 101: Learning CUTLASS the hard way
  - Lesson 17: Lecture 97: HipKittens
  - Lesson 18: Lecture 96: TLX
  - Lesson 58: Lecture 56: Kernel Benchmarking Tales
  - Lesson 80: Lecture 36: CUTLASS and Flash Attention 3
  - Lesson 97: Lecture 21: Scan Algorithm Part 2
  - Lesson 111: Lecture 8: CUDA Performance Checklist
  - Lesson 115: Lecture 4 Compute and Memory Basics

## 2. Tiled matmul, online softmax, and attention memory behavior

- ID: `comp-lab-02-tiled-attention`
- Code: `comprehensive-labs/gpumode_lab_suite/tiled_attention.py`
- Module: `gpumode_lab_suite.tiled_attention`
- Lessons mapped: 103
- Reason: Attention lessons need one code path that joins matmul tiling, stable softmax, and IO-aware attention accounting.
- First lesson anchors:
  - Lesson 2: Lecture 112: Production Megakernels for Real-World Inference
  - Lesson 5: Lecture 109: TIRx
  - Lesson 9: Lecture 105: cuDNN mxfp8 attention
  - Lesson 10: Lecture 104: Gluon and Linear Layouts
  - Lesson 17: Lecture 97: HipKittens
  - Lesson 18: Lecture 96: TLX
  - Lesson 26: Lecture 89: cuTile (from friends at NVIDIA)
  - Lesson 34: Lecture 80: How FlashAttention 4 Works

## 3. Compiler lowering, fusion, Triton-style autotuning, schedule search

- ID: `comp-lab-03-compiler-autotune`
- Code: `comprehensive-labs/gpumode_lab_suite/compiler_autotune.py`
- Module: `gpumode_lab_suite.compiler_autotune`
- Lessons mapped: 104
- Reason: Compiler and Triton material should be evaluated through schedule candidates and fusion decisions, not just syntax examples.
- First lesson anchors:
  - Lesson 18: Lecture 96: TLX
  - Lesson 37: Lecture 77: Domain Specific Languages for GPU Kernels
  - Lesson 74: Lecture 42: Mosaic GPU
  - Lesson 5: Lecture 109: TIRx
  - Lesson 32: Lecture 82 Helion: A high-level DSL for ML kernels
  - Lesson 35: Lecture 79 Mirage (MPK): Compiling LLMs into Mega Kernels
  - Lesson 36: Lecture 78 Iris: Multi-GPU Programming in Triton
  - Lesson 49: Lecture 65: Neighborhood Attention

## 4. Quantized numerics across int8, int4, fp8-like, and nvfp4-like formats

- ID: `comp-lab-04-quantization-formats`
- Code: `comprehensive-labs/gpumode_lab_suite/quantization_formats.py`
- Module: `gpumode_lab_suite.quantization_formats`
- Lessons mapped: 42
- Reason: Quantization lectures need error and format behavior that can be measured before porting into tensor-core kernels.
- First lesson anchors:
  - Lesson 2: Lecture 112: Production Megakernels for Real-World Inference
  - Lesson 4: Lecture 110: The 4-bitter lesson: Balancing Stability and Performance in NVFP4 RL
  - Lesson 6: Lecture 108: One Layer Deeper competition
  - Lesson 7: Lecture 107: PithTrain
  - Lesson 9: Lecture 105: cuDNN mxfp8 attention
  - Lesson 12: Lecture 102: quartet v2
  - Lesson 15: Lecture 99: Distributed ML on consumer devices
  - Lesson 18: Lecture 96: TLX

## 5. Serving scheduler, paged KV cache, prefix sharing, continuous batching

- ID: `comp-lab-05-serving-kv-cache`
- Code: `comprehensive-labs/gpumode_lab_suite/serving_kv_cache.py`
- Module: `gpumode_lab_suite.serving_kv_cache`
- Lessons mapped: 56
- Reason: Serving lectures are best combined into an allocator/scheduler lab because latency comes from the interaction of requests, cache blocks, and batching.
- First lesson anchors:
  - Lesson 1: Lecture 113: Every Microsecond Matters: Achieving Near Speed-of-Light Latency in GPU Collectives
  - Lesson 2: Lecture 112: Production Megakernels for Real-World Inference
  - Lesson 14: Lecture 100: InferenceX Continuous OSS Inference Benchmarking
  - Lesson 15: Lecture 99: Distributed ML on consumer devices
  - Lesson 16: Lecture 98: GPU Observability
  - Lesson 17: Lecture 97: HipKittens
  - Lesson 21: Lecture 93: Cornserve Easy, Fast and Scalable Multimodal AI
  - Lesson 34: Lecture 80: How FlashAttention 4 Works

## 6. CUDA-to-HIP portability scanner and migration plan

- ID: `comp-lab-06-portability-rocm-hip`
- Code: `comprehensive-labs/gpumode_lab_suite/portability_rocm_hip.py`
- Module: `gpumode_lab_suite.portability_rocm_hip`
- Lessons mapped: 96
- Reason: Portability needs a code migration/checking pass that records what can be rewritten and what remains manual.
- First lesson anchors:
  - Lesson 3: Lecture 111: Spectral Compute: Compile CUDA everywhere
  - Lesson 5: Lecture 109: TIRx
  - Lesson 7: Lecture 107: PithTrain
  - Lesson 8: Lecture 106: Hugging Face Kernels
  - Lesson 14: Lecture 100: InferenceX Continuous OSS Inference Benchmarking
  - Lesson 17: Lecture 97: HipKittens
  - Lesson 18: Lecture 96: TLX
  - Lesson 19: Lecture 95: Single controller programming with Monarch

## 7. Distributed collective algorithm and topology model

- ID: `comp-lab-07-distributed-collectives`
- Code: `comprehensive-labs/gpumode_lab_suite/distributed_collectives.py`
- Module: `gpumode_lab_suite.distributed_collectives`
- Lessons mapped: 44
- Reason: Collective lessons require algorithm/topology models before moving into NCCL, NVSHMEM, or cluster measurements.
- First lesson anchors:
  - Lesson 1: Lecture 113: Every Microsecond Matters: Achieving Near Speed-of-Light Latency in GPU Collectives
  - Lesson 19: Lecture 95: Single controller programming with Monarch
  - Lesson 27: Lecture 87: Low Latency Communication Kernels with NVSHMEM
  - Lesson 36: Lecture 78 Iris: Multi-GPU Programming in Triton
  - Lesson 44: Lecture 70: PCCL Fault tolerant collectives
  - Lesson 47: Lecture 67: NCCL and NVSHMEM
  - Lesson 50: Lecture 64: Multi-GPU programming
  - Lesson 57: Lecture 57: CuTe

## 8. Profiler counter triage, roofline evidence, remediation plan

- ID: `comp-lab-08-profiler-evidence`
- Code: `comprehensive-labs/gpumode_lab_suite/profiler_evidence.py`
- Module: `gpumode_lab_suite.profiler_evidence`
- Lessons mapped: 83
- Reason: Every kernel lab needs a profiler evidence loop that turns counters into bottleneck diagnoses and next code changes.
- First lesson anchors:
  - Lesson 7: Lecture 107: PithTrain
  - Lesson 10: Lecture 104: Gluon and Linear Layouts
  - Lesson 14: Lecture 100: InferenceX Continuous OSS Inference Benchmarking
  - Lesson 16: Lecture 98: GPU Observability
  - Lesson 22: Lecture 92: Smol Training Playbook
  - Lesson 23: Mega Lecture 91: Reinforcement Learning, Agents & OpenEnv
  - Lesson 26: Lecture 89: cuTile (from friends at NVIDIA)
  - Lesson 29: Lecture 85: Factorio Learning Environment
