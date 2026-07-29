# TileLink: Generating Efficient Compute-Communication Overlapping Kernels using Tile-Centric Primitives

**Venue:** MLSYS 2025 · **Subtheme:** Compute-Communication Overlap

## What It Does

TileLink solves a fundamental bottleneck in distributed LLM training: inter-GPU communication (all-reduce, all-gather, reduce-scatter) for tensor parallelism blocks GPU compute. The naive approach launches compute kernels, waits for completion, then launches communication. The expert approach fuses communication into compute kernels so that while one GPU thread group transfers tensors over NVLink, another thread group continues computing — but this requires ~2000 lines of hand-written CUDA exploiting NVSHMEM barriers and channel priorities, and is error-prone. TileLink provides a tile-centric abstraction: the programmer writes kernels using nine primitives at the tile (not individual element) level: producer_tile_notify/consumer_tile_wait synchronize tile-level data readiness; peer_tile_notify/peer_tile_wait coordinate cross-rank dependencies; tile_push_data/tile_pull_data transfer tiles between GPUs; rank_copy_data/rank_notify/rank_wait handle rank-level collective coordination. The backend then compiles these to overlapping kernels in three stages. First, **shape mapping** assigns tile dimensions to compute and communication workloads (e.g., a 256×128 tile for GEMM and a 128×256 slice for all-reduce). Second, **rank mapping** determines which GPU rank computes/receives each tile via either affine transforms (for regular collectives) or runtime lookup tables (for irregular patterns like expert dispatch). Third, **channel mapping** assigns each tile to a specific NVLink or InfiniBand channel to avoid congestion. The backend compiles these mappings to PTX via Triton extended with NVSHMEM primitives, generating a single CUDA kernel where compute threads and communication threads are interleaved at the warp granularity.

Data flow: Input tensor arrives → rank_mapper determines tile ownership → compute threads execute GEMM on their assigned tile → at barrier, producer_tile_notify signals completion → peer_tile_wait on rank N+1 unblocks that rank's communication threads → tile_push_data sends result over NVLink channel → next rank overlaps receiving with its GEMM compute. The key is that no rank stalls; NVLink latency is hidden by compute overlap.

## The Key Result

On LLM training workloads, TileLink achieves 1.17× to 20.76× speedup versus non-overlapping (sequential compute + communicate) baseline. Performance is comparable to FLUX (expert-written library) with approximately 200 Python lines of code versus ~2000 CUDA lines in FLUX. Demonstrates 10× code reduction while matching expert-tuned performance on GEMM+all-reduce, GEMM+all-gather, MoE expert dispatch, and attention+communication kernels.

## Why This Approach

Distributed LLM training spends 30-50% of iteration time on collective communication (all-reduce for gradient averaging in data parallelism, all-gather for tensor parallelism). Traditional distributed frameworks decompose this into separate stages: compute each layer, then synchronize and communicate. Even pipelined approaches that overlap one layer's communication with the next layer's compute leave a gap. The expert solution (FLUX) fuses communication directly into kernels, creating fine-grained interleaving, but this requires deep CUDA/NVSHMEM expertise and produces non-portable code. TileLink's tile-centric abstraction lifts this to a higher level: tiles are natural units that can be independently computed and communicated without global coordination. By exposing tile synchronization primitives, TileLink lets a compiler handle the scheduling complexity. The rank mapping abstraction handles both regular collectives (affine patterns) and irregular ones (expert routing), making it general-purpose. The alternative — requiring every distributed framework to hand-optimize kernels, or accepting lower utilization from simpler decomposition — limits innovation velocity and wastes GPU time.

## What It Leaves Open

- Static shape mapping requires recompilation for different tensor dimensions; no adaptive tile sizing for multi-batch inference with varying sequence lengths.
- Dynamic lookup-table mapping for irregular collectives (e.g., MoE expert dispatch) adds runtime overhead to build the rank mapping; scalability to thousands of tokens or experts unclear.
- NVSHMEM dependency limits portability to non-NVIDIA platforms (AMD MI300, Intel GPU, CPU clusters); no path to generalize.
- Tile granularity is architecture and model-dependent and must be tuned manually per model; no autotuning pass to search the tile-size design space.
- Evaluation focuses on dense layers; sparse patterns (activation sparsity, token pruning in inference) and their interaction with tile-centric mapping not explored.
