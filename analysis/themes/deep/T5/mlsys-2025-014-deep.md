# N:M Sparse DNN Kernels for RISC-V MCUs via Custom ISA Extension

**Venue:** MLSYS 2025 · **Subtheme:** Hardware-Accelerated Semi-Structured Sparsity on Edge

## What It Does

This work introduces xDecimate, a custom RISC-V ISA instruction that performs hardware-accelerated N:M sparse selection and multiply-accumulate (MAC) in a single operation. N:M sparsity enforces that among every N consecutive weight values, at most M are nonzero (e.g., 2:4 means 2 nonzeros per 4 weights). Standard RISC-V cores lack primitives to exploit this pattern, so software extraction (checking which weights are nonzero, loading only those, adjusting indices) introduces 5-10x overhead.

The xDecimate instruction accepts an N:M weight vector, input activation values, and a sparsity pattern, then outputs the sparsity-reduced MAC result directly in hardware. Decimate Im2col reformulates 2D convolution to enable xDecimate on im2col-transformed feature maps: instead of multiple 1D convolutions, the input is flattened into a matrix where xDecimate can process multiple channels efficiently. The MATCH compiler generates xDecimate-aware kernels automatically. The design is synthesized at 22nm targeting the Vega PULP SoC (commercial product GAP9).

## The Key Result

On ResNet-18 at 1:16 sparsity, xDecimate achieves 3.21x speedup over dense baseline inference. ViT achieves 1.81x speedup at the same sparsity ratio. The xDecimate hardware adds only 5% area overhead to a baseline RISC-V core, making it practical for area-constrained MCUs.

## Why This Approach

Edge MCUs (IoT, wearable, embedded) have severe power (5-50mW) and area budgets (a few mm²). N:M sparsity can reduce inference compute 16x at 1:16 ratio, but realizing this speedup requires ISA-level support—standard load/store instructions cannot directly skip nonzero elements. Prior work relied on software loops over sparsity patterns, creating unpredictable branch behavior and irregular memory access. xDecimate solves this by adding a single dedicated instruction that the hardware executes without branches: the instruction knows the N:M pattern, fetches exactly M values per N-element group, computes MACs, and writes the result in parallel, eliminating software loop overhead.

## Why This Approach

Decimate Im2col converts convolution kernels into a form where xDecimate naturally applies: each row of the im2col matrix contains one neuron's neighborhood, and consecutive columns group input channels, allowing xDecimate to process multiple channels' worth of sparse weights in one pass instead of iterating layer-by-layer.

## What It Leaves Open

- xDecimate requires retraining with N:M sparsity constraints; cannot be applied to pre-trained dense models without fine-tuning or pruning-aware retraining.
- Speedup diminishes significantly for ViT (1.81x) compared to ResNet-18 (3.21x) due to attention's irregular memory access patterns; xDecimate cannot mask the core bottleneck of attention computation.
- Custom ISA extension requires toolchain modifications (compiler, assembler); adoption limited to platforms with xDecimate support or willing to fork RISC-V toolchains.
- Evaluation limited to two model architectures (ResNet-18, ViT); results on RNNs, GRUs, or other sparsity-friendly architectures unknown.
- Sparsity ratios tested only at 1:4, 1:8, 1:16; different sparsity granularities (2:8, 4:16) not evaluated.
