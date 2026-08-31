# Kernel Benchmark Lesson Map

Lessons covered: 118 / 118

## Vector memory, coalescing, striding, and bandwidth

- ID: `memory`
- CUDA: `kernel-benchmarks/kernels/cuda/memory.cu`
- Triton: `kernel-benchmarks/kernels/triton/memory.py`
- Lessons mapped: 116

| Lesson | Title | Score |
|---|---|---|
| 1 | Lecture 113: Every Microsecond Matters: Achieving Near Speed-of-Light Latency in GPU Collectives | 30 |
| 2 | Lecture 112: Production Megakernels for Real-World Inference | 30 |
| 5 | Lecture 109: TIRx | 30 |
| 7 | Lecture 107: PithTrain | 30 |
| 10 | Lecture 104: Gluon and Linear Layouts | 30 |
| 13 | Lecture 101: Learning CUTLASS the hard way | 30 |
| 17 | Lecture 97: HipKittens | 30 |
| 18 | Lecture 96: TLX | 30 |
| 26 | Lecture 89: cuTile (from friends at NVIDIA) | 30 |
| 32 | Lecture 82 Helion: A high-level DSL for ML kernels | 30 |
| 34 | Lecture 80: How FlashAttention 4 Works | 30 |
| 35 | Lecture 79 Mirage (MPK): Compiling LLMs into Mega Kernels | 30 |
| 36 | Lecture 78 Iris: Multi-GPU Programming in Triton | 30 |
| 37 | Lecture 77: Domain Specific Languages for GPU Kernels | 30 |
| 39 | Lecture 75 [ScaleML Series] GPU Programming Fundamentals + ThunderKittens | 30 |
| 45 | Lecture 68: Landscape of GPU Centric communication | 30 |

## Block reductions, warp reductions, scans, and aggregation

- ID: `reduction`
- CUDA: `kernel-benchmarks/kernels/cuda/reduction.cu`
- Triton: `kernel-benchmarks/kernels/triton/reduction.py`
- Lessons mapped: 110

| Lesson | Title | Score |
|---|---|---|
| 2 | Lecture 112: Production Megakernels for Real-World Inference | 24 |
| 3 | Lecture 111: Spectral Compute: Compile CUDA everywhere | 24 |
| 4 | Lecture 110: The 4-bitter lesson: Balancing Stability and Performance in NVFP4 RL | 24 |
| 5 | Lecture 109: TIRx | 24 |
| 9 | Lecture 105: cuDNN mxfp8 attention | 24 |
| 10 | Lecture 104: Gluon and Linear Layouts | 24 |
| 11 | Lecture 103: Fundamentals of CuTe Layout Algebra and Category-theoretic Interpretation | 24 |
| 13 | Lecture 101: Learning CUTLASS the hard way | 24 |
| 16 | Lecture 98: GPU Observability | 24 |
| 17 | Lecture 97: HipKittens | 24 |
| 18 | Lecture 96: TLX | 24 |
| 26 | Lecture 89: cuTile (from friends at NVIDIA) | 24 |
| 28 | Lecture 86: Getting Started with CuTe DSL | 24 |
| 32 | Lecture 82 Helion: A high-level DSL for ML kernels | 24 |
| 34 | Lecture 80: How FlashAttention 4 Works | 24 |
| 37 | Lecture 77: Domain Specific Languages for GPU Kernels | 24 |

## Softmax and layernorm row kernels

- ID: `normalization`
- CUDA: `kernel-benchmarks/kernels/cuda/softmax_layernorm.cu`
- Triton: `kernel-benchmarks/kernels/triton/softmax_layernorm.py`
- Lessons mapped: 56

| Lesson | Title | Score |
|---|---|---|
| 2 | Lecture 112: Production Megakernels for Real-World Inference | 30 |
| 8 | Lecture 106: Hugging Face Kernels | 30 |
| 9 | Lecture 105: cuDNN mxfp8 attention | 30 |
| 31 | Lecture 83: Formalized Kernel Derivation | 30 |
| 34 | Lecture 80: How FlashAttention 4 Works | 30 |
| 42 | Lecture 72: [ScaleML Series] Efficient & Effective Long-Context Modeling for Large Language Models | 30 |
| 43 | Lecture 71: [ScaleML Series] FlexOlmo: Open Language Models for Flexible Data Use | 30 |
| 54 | Lecture 60: Optimizing Linear Attention | 30 |
| 55 | Lecture 59: FastVideo | 30 |
| 67 | Lecture 48: The Ultra Scale Playbook | 30 |
| 70 | Lecture 46: Distributed GEMM | 30 |
| 75 | Lecture 41: FlashInfer | 30 |
| 80 | Lecture 36: CUTLASS and Flash Attention 3 | 30 |
| 88 | GPU MODE IRL 2024 Keynotes | 30 |
| 93 | Lecture 25: Speaking Composable Kernel (CK) | 30 |
| 96 | Lecture 22: Hacker's Guide to Speculative Decoding in VLLM | 30 |

## Tiled matmul and tensor-core promotion path

- ID: `matmul`
- CUDA: `kernel-benchmarks/kernels/cuda/matmul_mlp.cu`
- Triton: `kernel-benchmarks/kernels/triton/matmul_mlp.py`
- Lessons mapped: 106

| Lesson | Title | Score |
|---|---|---|
| 2 | Lecture 112: Production Megakernels for Real-World Inference | 40 |
| 5 | Lecture 109: TIRx | 40 |
| 9 | Lecture 105: cuDNN mxfp8 attention | 40 |
| 10 | Lecture 104: Gluon and Linear Layouts | 40 |
| 11 | Lecture 103: Fundamentals of CuTe Layout Algebra and Category-theoretic Interpretation | 40 |
| 16 | Lecture 98: GPU Observability | 40 |
| 17 | Lecture 97: HipKittens | 40 |
| 18 | Lecture 96: TLX | 40 |
| 26 | Lecture 89: cuTile (from friends at NVIDIA) | 40 |
| 34 | Lecture 80: How FlashAttention 4 Works | 40 |
| 35 | Lecture 79 Mirage (MPK): Compiling LLMs into Mega Kernels | 40 |
| 55 | Lecture 59: FastVideo | 40 |
| 57 | Lecture 57: CuTe | 40 |
| 69 | Lecture 47: KernelBot Benchmark GPU Kernels on Discord | 40 |
| 70 | Lecture 46: Distributed GEMM | 40 |
| 75 | Lecture 41: FlashInfer | 40 |

## Fused MLP, activation, and compiler/autotune path

- ID: `fusion`
- CUDA: `kernel-benchmarks/kernels/cuda/matmul_mlp.cu`
- Triton: `kernel-benchmarks/kernels/triton/matmul_mlp.py`
- Lessons mapped: 104

| Lesson | Title | Score |
|---|---|---|
| 18 | Lecture 96: TLX | 50 |
| 37 | Lecture 77: Domain Specific Languages for GPU Kernels | 50 |
| 74 | Lecture 42: Mosaic GPU | 50 |
| 5 | Lecture 109: TIRx | 40 |
| 32 | Lecture 82 Helion: A high-level DSL for ML kernels | 40 |
| 35 | Lecture 79 Mirage (MPK): Compiling LLMs into Mega Kernels | 40 |
| 36 | Lecture 78 Iris: Multi-GPU Programming in Triton | 40 |
| 49 | Lecture 65: Neighborhood Attention | 40 |
| 56 | Lecture 58: Disaggregated LLM Inference | 40 |
| 62 | Bonus Lecture: AMD Developer Challenge | 40 |
| 63 | Lecture 53: torch.compile Q&A | 40 |
| 66 | Lecture 50: A learning journey CUDA, Triton, Flash Attention | 40 |
| 82 | Lecture 34: Low Bit Triton Kernels | 40 |
| 83 | Lecture 33: Bitblas | 40 |
| 84 | Lecture 32: Unsloth | 40 |
| 90 | Lecture 28: Liger Kernel - Efficient Triton Kernels for LLM Training | 40 |
