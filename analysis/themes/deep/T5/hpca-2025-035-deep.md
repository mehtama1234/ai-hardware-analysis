# EXION: Exploiting Inter-and Intra-Iteration Output Sparsity for Diffusion Models

**Venue:** HPCA · **Subtheme:** Temporal and Structural Sparsity in Iterative Workloads

## What It Does

EXION is a software-hardware co-design that exploits two dimensions of sparsity in diffusion model inference. First, the FFN-Reuse algorithm identifies temporal redundancy across denoising iterations: diffusion models run the same transformer blocks 1000 times with gradually changing noise. EXION observes that within FFN (feed-forward network) layers, GELU outputs have low-magnitude elements that persist across iterations. The algorithm computes the GELU output fully in one "dense" iteration, then reuses that output by skipping computation for low-magnitude elements (identified via magnitude thresholding) in the next N "sparse" iterations, achieving 70-97% output sparsity in the first FFN layer and 52-85% operation reduction overall.

Second, an improved eager prediction algorithm with two-step leading-one detection (TS-LOD) predicts which attention scores will be negligible by approximating attention computation in log-domain (summing log magnitudes instead of actual values). This identifies Q and KV projections that can be skipped entirely within each iteration, achieving 20-95% intra-iteration sparsity.

The ConMerge data compaction mechanism converts unstructured sparse outputs into compact dense matrices: column condensing removes all-zero columns, and block merging combines sparse and dense tiled blocks using conflict-vector tracking to identify safe merge points. Dedicated ASIC hardware (Diffusion-Sparsity Aware Core, or DSC) includes a Sparse-Dense Unified Engine (SDUE) with a 16x16 DPU array that switches per-DPU inputs/weights/conflict vectors to support ConMerge-aware dataflow, plus specialized units for eager prediction and special functions. Synthesized at 14nm, 800MHz, 0.8V.

## The Key Result

On a 14nm EXION ASIC with 24 DSC cores and 64MB global memory, the system achieves 3.2-379.3x speedup over an NVIDIA RTX 6000 Ada server GPU and 42.6-1090.9x speedup over an NVIDIA Jetson Orin Nano edge GPU across 7 diffusion model benchmarks. Energy efficiency gains are 45.1-3067.6x over RTX 6000 Ada and 196.9-4668.2x over edge GPU. Die area is 152.28 mm² (EXION24) versus 609 mm² for RTX 6000 Ada.

## Why This Approach

Diffusion models are 23.6x more energy-hungry than GANs due to repeated transformer execution across hundreds of iterations. Prior accelerators target only QKV projections and attention within a single iteration, ignoring both the iterative structure and the FFN layers (38-100% of transformer ops, up to 67% in some blocks). FFN-Reuse is the first algorithm to exploit that low-magnitude GELU outputs are temporally stable across iterations, enabling reuse without retraining. Two-step leading-one detection improves upon prior eager prediction by using log-domain arithmetic (not computing full magnitudes), reducing FLOPs in attention prediction itself. ConMerge solves the practical challenge: unstructured sparsity creates irregular data layouts that cause poor hardware utilization, so the mechanism compacts sparse patterns into dense matrices that maintain high DPU occupancy.

## What It Leaves Open

- ResBlock-containing architectures (Make-an-Audio, Stable Diffusion) don't benefit fully because sparsity optimizations apply only to transformer blocks, leaving ResBlocks unadjusted; efficiency gains are reduced for these models.
- FFN-Reuse assumes GELU outputs remain temporally coherent across iterations; applicability to other activation functions (Swish, GLU variants) is unexamined.
- Two-step leading-one detection relies on log-domain approximation; accuracy impact on models with highly skewed attention patterns not characterized.
- ConMerge conflict-vector tracking adds area (0.94% of DSC) but overhead scales with matrix width; handling wider attention heads may introduce efficiency cliffs.
- Evaluation on 7 model variants but evaluation on newer diffusion architectures (e.g., Flux, cascade models) not included.
