# COMET: Fine-grained Computation-communication Overlapping for Mixture-of-Experts

**Venue:** MLSYS 2025 · **Subtheme:** Communication-Computation Overlap in Distributed MoE

## What It Does

COMET optimizes distributed Mixture-of-Experts training by fine-grained overlapping of inter-device all-to-all token routing communication with expert computation. The bottleneck: sparse expert activation requires routing tokens to different GPUs via all-to-all collectives, occupying 30-47% of execution time. Naive pipelining chunks expert computation and communication, but granularity mismatch causes inefficiency—token-level communication (all-to-all happens atomically) and tile-level GEMM computation (matrix multiply processes 128×128 tiles) operate at different granularities, making deterministic scheduling difficult.

COMET introduces two mechanisms: (1) Shared Tensor Based Dependency Resolving: analyzes the shared buffer (output token matrix) between communication producer (all-to-all dispatch) and computation consumer (expert layer GEMM), then decomposes this tensor along independent dimensions. For layer-0 GEMMs, decompose along M-axis (split output tokens into row groups); for layer-1 top-K selection, decompose along N-axis (split dimension for reduction). Then reschedule computation tiles to begin as early as possible using locally available data. (2) Adaptive Workload Assignment: fuses communication and computation in a single GPU kernel, then thread-block specialization isolates them in separate streaming multiprocessor (SM) groups. Adaptive thread-block allocation is profiled per input shape and parallelism strategy to determine the optimal split (e.g., 40% SMs for communication, 60% for computation, tuned per configuration).

Mechanically: fused kernel receives producer (all-to-all) and consumer (GEMM) operations as input, decomposes shared tensors into independent blocks, runs producer and consumer concurrently on separate SM groups, and uses NVSHMEM (GPU-initiated communication) for fine-grained remote data access. Hopper TMA (tensor memory accelerator) overlaps data movement with computation.

## The Key Result

On NVIDIA H800 GPUs (NVLink) training Mixtral 8x7B and Qwen2-MoE, COMET achieves 1.96x speedup on a single MoE layer, 1.71x end-to-end speedup, and hides 86.5% of communication latency (versus 68.6% for Tutel and 29.2% for FasterMoE). Deployed in production on 10,000+ GPU clusters saving millions of GPU hours. Latency reduction versus Megatron-CUTLASS: 34.1%; versus Megatron-TE: 42.6%; versus FasterMoE: 44.4%.

## Why This Approach

Existing MoE systems (Tutel, FasterMoE, Megatron) treat all-to-all and expert computation as separate pipeline stages, missing fine-grained overlapping opportunities. Token routing collectives are all-to-all (all devices exchange tokens), creating data dependencies that span all devices; naive pipelining waits for the full all-to-all to complete before GEMM begins, leaving communication latency unexploited. COMET's insight is that GEMM can begin on the first tokens that arrive via all-to-all, before the full collective completes. Shared tensor decomposition enables this: by splitting output token matrix into M-axis or N-axis slices, the scheduler can identify which tile computations depend only on which token slices, then trigger GEMM tiles as soon as their data arrives.

Adaptive SM allocation further optimizes: communication (all-to-all dispatch) and computation (GEMM) both consume SM resources; if too many SMs do communication, computation stalls; if too few, communication takes all the time. COMET profiles per shape/parallelism configuration to find the optimal split. Hopper TMA hardware offloads memory copy work to a dedicated engine, freeing compute SMs for actual GEMM.

## What It Leaves Open

- Requires pre-profiling per (input shape, parallelism configuration) to determine optimal thread-block split; profiling database size grows with model variants, and profiling must be rerun when hardware topology changes.
- NVSHMEM memory overhead is small but non-zero; impact on memory pressure in production clusters with large batch sizes not quantified.
- Primarily validated on H800 (NVLink, high bandwidth); L20 (PCIe) gains much smaller (1.19-1.46x vs 1.28-2.37x on H100), indicating method sensitivity to network topology.
- Evaluation focused on Mixtral-8x7B and Qwen2-MoE; behavior on other MoE variants (e.g., GShard, Switch Transformers with 2000+ experts) or mixture ratios unknown.
- Assumes static expert assignment; dynamic load balancing (reassigning experts at runtime based on token distribution) not addressed.
