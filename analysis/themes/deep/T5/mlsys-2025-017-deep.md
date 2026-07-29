# Dynamic Input Pruning for Efficient LLM Inference on Mobile Devices

**Venue:** MLSYS 2025 · **Subtheme:** Activation-Aware Pruning for Mobile Inference

## What It Does

Dynamic Input Pruning (DIP) exploits activation sparsity in SwiGLU MLP layers (the dominant bottleneck in modern LLMs on mobile). For each token, the MLP computes three projections: up (d → 2d expansion), gate (d → d), and down (2d → d contraction). All three weight matrices must be loaded from DRAM even though only a subset of inputs are significant. DIP applies top-K selection on input activation magnitudes: it selects the K largest elements of the input activation and prunes (skips) the corresponding columns in all three weight matrices, never loading irrelevant weights.

Crucially, DIP requires no separate predictor network: the magnitude selection is computed on-the-fly during inference. A cache-aware variant (DIP-CA) uses a gamma multiplier (gamma=0.2) to bias selection toward weight columns already resident in the L1/L2 cache, coordinating column selection with the hardware memory hierarchy. The method is compatible with LoRA adapters for accuracy recovery if needed.

## The Key Result

On Apple A18 simulation (60 GB/s DRAM bandwidth, 1 GB/s Flash storage), DIP achieves 40% throughput increase and 46% DRAM reduction on Phi-3-Medium inference. Perplexity increases by less than 0.1 at optimal sparsity ratios, indicating negligible accuracy loss.

## Why This Approach

Mobile SoCs like Apple A18 and Snapdragon have 60 GB/s DRAM bandwidth versus desktop/server GPUs with 900+ GB/s (NVLink) or 600+ GB/s (PCIe), making DRAM the critical bottleneck. SwiGLU MLPs are memory-bandwidth bound: the compute-to-bandwidth ratio is low, so every byte of weight loading directly impacts latency and energy. Existing approaches (e.g., DejaVu) train separate predictor networks to decide which columns to keep, but this adds inference latency and model size. DIP's key insight is that input magnitudes are a sufficient signal: large-magnitude inputs produce significant contributions regardless of weight values, so pruning low-magnitude input elements automatically minimizes impact. The top-K operation is trivial to compute on mobile CPUs/NPUs (sorting K=16 or K=32 elements is microseconds), avoiding predictor overhead entirely.

DIP-CA further optimizes by observing that mobile memory hierarchies are tiny (1-2 MB L2): if a weight column is already in cache (loaded for a previous token), loading it again is free, so the gamma multiplier biases selection to prefer cached columns, reducing DRAM refetch.

## What It Leaves Open

- Evaluation is simulation-based on A18; no real hardware measurement on actual Apple devices or Snapdragon SoCs, leaving real-world DRAM/cache behavior uncertain.
- Accuracy-efficiency tradeoff is data-dependent: optimal sparsity ratio varies by prompt, model size, and task; no adaptive mechanism to automatically tune K.
- DIP-CA benefit depends critically on cache hit rate and memory access patterns; behavior on different MLP sizes or batch configurations not characterized.
- Currently only handles SwiGLU architecture; does not extend to attention layers (which also consume DRAM but with different access patterns), limiting applicability to full-model inference.
- LoRA adapter compatibility mentioned but not evaluated; impact on sparsity patterns and accuracy when LoRA is active unknown.
