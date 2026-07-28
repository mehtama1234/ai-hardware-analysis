# MEADOW: Memory Efficient Adaptable Dataflow for On-Device LLM Workloads

**Venue:** MLSYS 2025 · **Theme:** On-Device Adaptive Dataflow

## What It Does

Running LLM inference on edge FPGAs is severely constrained by the FPGA's limited on-chip SRAM and external DRAM bandwidth, making naive GEMM-based attention execution impractical at the bandwidth envelope of sub-10W devices.

Edge FPGAs like the Xilinx ZCU102 have <10 TOPS peak and narrow external memory busses; attention's bandwidth requirements dwarf what a single weight-streaming dataflow can achieve, necessitating a co-designed dataflow and weight compression scheme.

Token-Parallel Head-Sequential (TPHS) dataflow partitions attention across token dimension in parallel while sequencing across heads to fit SRAM; weight packing extracts unique chunks from weight tensors, applies packet-specific encoding precision, and uses frequency-aware reindexing to minimize DRAM traffic. W8A8 quantization applied throughout.

## The Key Experiment

- **speedup:** 1.5x decode latency, 2.5x prefill latency vs GEMM baseline; >40% improvement vs CTA/FlightLLM
- **energy or tops w:** Sub-10W device (Xilinx ZCU102)
- **area:** None
- **ppa:** None
- **accuracy:** W8A8 quantization with accuracy preserved
- **other:** None

**Compared against:** GEMM baseline; CTA; FlightLLM

**Hardware:** fpga; edge · **Workloads:** llm-inference

## Why This Approach

Combined TPHS dataflow and three-level weight packing (unique-chunk extraction + per-packet precision + frequency-aware reindexing) co-designed for sub-10W FPGA inference, achieving 1.5-2.5x latency reduction over GEMM baseline.

This paper sits in the **quantization** subtheme. The core tension: lower precision = smaller model = less memory bandwidth, but at the cost of rounding error that compounds across layers. This paper's bet: TPHS dataflow enabling token-level parallelism with head-sequential scheduling to fit attention within FPGA SRAM budget.

## What It Leaves Open

- Limited to Xilinx ZCU102 FPGA platform
- W8A8 quantization may not be sufficient for all model quality requirements
- evaluation focused on attention kernels.

**Tags:** fpga, edge-inference, attention, quantization, dataflow, weight-compression
