# GPUMODE Deep Build Plan

The goal is not to mirror lectures as notes. The goal is to convert the lecture
corpus into executable GPU-systems work.

## Build Tracks

1. Transcript corpus
   - capture channel/playlist metadata
   - download VTT captions
   - clean captions into stable text files
   - index lessons with title, URL, duration, transcript status, word count, and topics

2. Kernel progression
   - CUDA vector/reduction correctness and memory coalescing
   - shared-memory tiled matmul
   - warp-level reductions and scans
   - Tensor Core and WMMA/CUTLASS follow-up
   - Triton equivalents for matmul, softmax, layernorm, and attention

3. Attention and serving progression
   - naive attention
   - tiled attention
   - online softmax
   - fused attention in Triton
   - KV-cache allocation
   - prefix-cache batching
   - vLLM/TGI benchmark when accelerator runtime is available

4. Profiling progression
   - PyTorch profiler baseline
   - Nsight Systems launch timeline
   - Nsight Compute memory/coalescing counters
   - occupancy and register-pressure experiments
   - roofline interpretation

5. Compiler/runtime progression
   - `torch.compile` before and after graphs
   - generated Triton kernels
   - custom PyTorch C++/CUDA extension
   - Inductor/Triton debugging workflow

6. Cross-corpus bridge
   - link GPUMODE lessons to the local conference corpus
   - map tutorial work to MLSys, ASPLOS, ISCA, MICRO, HPCA, SC, and Hot Chips themes
   - identify which papers deserve runnable reproductions

## First Ten Candidate Labs

1. CUDA memory coalescing microscope
2. Warp reductions and prefix scans
3. Shared-memory tiled GEMM with arithmetic-intensity accounting
4. Tensor Core matmul via WMMA or CUTLASS
5. Triton matmul autotuning workbench
6. Triton softmax and layernorm fusion
7. FlashAttention-style online softmax
8. PyTorch profiler to Nsight workflow
9. `torch.compile` graph-break and fusion lab
10. vLLM scheduler/KV-cache load lab

Each lab must produce a JSON artifact, a generated page, correctness checks, and
skip evidence when local GPU tooling is unavailable.
