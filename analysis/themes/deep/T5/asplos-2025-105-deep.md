# FSMoE: A Flexible and Scalable Training System for Sparse Mixture-of-Experts Models

**Venue:** ASPLOS · **Subtheme:** Communication Optimization in Distributed MoE Training

## What It Does

FSMoE addresses the core bottleneck in distributed MoE training: AlltoAll communication between devices accounts for 30-60% of total training time when tokens are routed to sparse sets of experts. The system decomposes each MoE layer into six sub-modules (Gate, Order, I-Order, Dispatch, Combine, Expert), then uses a two-phase profiler-scheduler that fits linear performance models for both GEMM operations and collective communication primitives (AllGather, ReduceScatter, AlltoAll). This model enables precise prediction of execution time across different configurations.

The key innovation is a three-stream pipeline scheduler that simultaneously overlaps three execution streams: (1) inter-node AlltoAll dispatch/combine communication, (2) intra-node ESP-AllGather/ReduceScatter collective operations, and (3) expert computation. The scheduler classifies each MoE execution into four cases (dominated by inter-node comm, expert compute, AlltoAll, or intra-node comm) and uses SLSQP optimization to find the optimal pipeline chunk degree r for each case. Additionally, an adaptive gradient partitioning algorithm slices Gradient-AllReduce work into chunks and assigns them to overlappable windows across MoE and dense layers, decoupling forward and backward pipeline degrees.

## The Key Result

On GPU clusters with up to 48 A6000/2080Ti GPUs connected via InfiniBand, FSMoE achieves 1.18x-1.22x speedup over Tutel+PipeMoE on 1458 configured MoE layer variants, and 1.19x-3.01x speedup over DeepSpeed-MoE on real-world GPT-2 and Mixtral models. Individual gating function benchmarks show up to 1.42x speedup versus DeepSpeed-MoE. The performance model itself achieves r² ≥ 0.9999 fitting accuracy across all collective operation types.

## Why This Approach

MoE systems are fundamentally communication-bound: sparse expert activation means only a subset of expert parameters are updated per step, but orchestrating token routing across multiple parallelism axes (data parallelism DP, model parallelism MP, expert parallelism EP, expert-split parallelism ESP) creates complex overlapping opportunities that existing systems (DeepSpeed-MoE, Tutel) cannot exploit. These systems use fixed or heuristic pipeline degrees and fail to co-design Gradient-AllReduce scheduling with MoE communication, leaving 50%+ communication overhead untapped. FSMoE's contribution is the modular abstraction with hooks for customizable routing functions combined with precise performance modeling and adaptive scheduling that collectively optimizes all three communication streams.

## What It Leaves Open

- Evaluation limited to clusters up to 48 GPUs; behavior on production-scale clusters (1000+ H100s with NVLink) is uncharacterized, which is critical for billion-parameter MoE models.
- The SLSQP optimization finds locally optimal pipeline chunk degrees per phase, but lacks global cross-layer optimization considering heterogeneous network topologies.
- Gradient partitioning uses differential evolution with greedy initialization, which may miss better partitions on cluster sizes beyond 48 nodes.
- No analysis of how routing function diversity (beyond the four pre-built options) affects performance model accuracy or scheduling decisions.
- Assumes homogeneous GPU hardware and network; heterogeneous clusters (mixed H100/A100) are not addressed.
