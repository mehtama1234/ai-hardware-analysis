# Reconfigurable Stream Network Architecture

**Venue:** ISCA · **Subtheme:** DNN Overlay Architectures

## What It Does

Reconfigurable Stream Network (RSN) replaces von Neumann instruction-issue models in FPGA-based DNN overlays with a circuit-switched streaming network abstraction. Traditional FPGA overlays serialize DNN layers: compute L1 → stall → memory flush → compute L2. RSN introduces a streaming ISA where each layer produces a stream of data blocks (e.g., 8×8 tiles) that flow through multiple processing engines (PE) wired as a static dataflow graph. The key innovation: inter-layer dataflow edges can be "wired" at configuration time, allowing L1→L2 streams to flow through a PE network without materializing intermediate results to memory.

Data path: input stream → bank of stateful processing elements → output stream. Configuration specifies which PEs form the dataflow, their connections, and reuse patterns. The circuit-switched fabric automatically pipes data across layers in a single clock cycle per tile, eliminating intermediate materialization.

## The Key Result

RSN achieves 2.3x–3.8x speedup over layer-serial FPGA overlays and 1.4x–2.1x over single-layer GPU baselines on benchmark DNNs (ResNet, VGG, MobileNet). Memory bandwidth usage drops 2.8x because intermediate tensors stay in the dataflow fabric. Latency per inference reduced from 100+ ms (layer-serial) to 30–50 ms. Area utilization 15%–30% higher than layer-serial due to additional routing, but speedup offsets cost.

## Why This Approach

FPGA overlays suffer from layer-granularity serialization: completing layer L1 requires materializing all output activations to BRAM/HBM before layer L2 can start. This serialization wastes 60%+ of memory bandwidth and introduces 10–50 ms latency per layer. RSN's circuit-switched abstraction mimics systolic-array designs (e.g., TPU) but on FPGAs, enabling dynamic layer fusion and multi-layer pipelining. Unlike fixed-topology systolics, RSN is reconfigurable per DNN, making it suitable for edge deployment where models change frequently.

## What It Leaves Open

- Configuration overhead: reconfiguring the dataflow graph between different DNNs incurs 5–10 ms latency; streaming architectures may not suit rapid model swaps
- Sparsity support: streams assume dense tiles; exploiting structured sparsity (pruning) requires new tile formats and routing logic
- Generalization to non-convolution layers (attention, recurrent) unclear; streaming assumes feed-forward dataflow
- Power profile on real FPGA platforms (Xilinx, Altera) not characterized; dataflow routing may increase leakage
- Comparison against domain-specific overlays (e.g., Eyeriss, HAM) missing; unclear if RSN beats fixed-dataflow designs
