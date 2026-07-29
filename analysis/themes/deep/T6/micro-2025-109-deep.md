# StreamTensor: Make Tensors Stream in Dataflow Accelerators for LLMs

**Venue:** MICRO · **Subtheme:** Dataflow Compilation

## What It Does

StreamTensor is an MLIR-based compiler that introduces an iterative tensor (itensor) type encoding element shape, iteration space, and iteration map to uniquely capture a kernel's stream access order. The compilation pipeline proceeds through: (1) Linalg tiling and conversion to dataflow IR with itensor-typed kernel boundaries; (2) stream-based kernel fusion that compares producer/consumer itensor types — matching types are connected by FIFOs directly, mismatched types get minimal ping-pong buffer layout converters sized analytically from itensor types; (3) itensor folding to merge adjacent producer-consumer buffers; (4) iterative tensor vectorization to align FIFO bandwidth with kernel parallelism; (5) LP-based FIFO sizing that formulates token flow as a scheduling problem and solves it with linear programming to minimize FIFO depth while preventing deadlock; and (6) ILP graph partitioning for resource allocation. Three hierarchical design spaces (Linalg tiling, kernel fusion, resource allocation) are explored with Optuna blackbox optimization, intensity-aware unrolling, and heuristic permutation.

The iterative tensor (itensor) type system that explicitly encodes streaming access order (iteration space + iteration map), enabling automated correctness-verified stream-based kernel fusion, minimal layout converter generation, and LP-based FIFO sizing for dataflow accelerators.

## The Key Result

- **Speedup:** Up to 0.76x lower latency than state-of-the-art FPGA LLM accelerators; 0.64x lower latency than GPUs
- **Energy Or Tops W:** Up to 1.99x higher energy efficiency compared to GPUs

## Why This Approach

First PyTorch-to-device dataflow compiler (StreamTensor) that automatically generates stream-based dataflow accelerators and runtime systems from high-level models. Iterative tensor (itensor) type system encoding stream layout for automated kernel fusion, buffer sizing, and correctness verification. Three hierarchical design space exploration algorithms: intensity-aware Linalg tiling, heuristic kernel fusion with memory constraints, and LP-based FIFO sizing. Up to 0.76x lower latency vs. state-of-the-art FPGA LLM accelerators, 0.64x vs. GPUs, and 1.99x higher energy efficiency vs. GPUs on LLM benchmarks

This work addresses the fundamental problem: Dataflow accelerators for LLMs (e.g., AMD Versal, SambaNova SN40L, IBM AIU) require manual effort to wire together kernels via on-chip FIFOs, manage external DMA access patterns, size FIFOs to prevent...

## What It Leaves Open

- Evaluated only on FPGA platforms; the itensor type system and LP FIFO sizing scalability for very large LLMs or multi-chip systems is not demonstrated.
