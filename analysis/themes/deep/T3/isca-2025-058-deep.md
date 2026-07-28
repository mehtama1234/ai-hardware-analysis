# NMP-PaK: Near-Memory Processing Acceleration of Scalable De Novo Genome Assembly

**Venue:** ISCA · **Theme:** Near-Memory Genomics

## What It Does

De novo genome assembly using De Bruijn graph (DBG) algorithms is both memory-latency-bound and memory-footprint-intensive: processing 10% of the human genome (38.3 GB input) requires 528 GB of DRAM, and the Iterative Compaction step—which dominates 48% of runtime—achieves only 2.5% of available memory bandwidth due to fine-grained, irregular access patterns across large, dynamic MacroNode data structures.

Genomic datasets are growing faster than Moore's Law, and state-of-the-art distributed assemblers (e.g., PaKman) require tens of thousands of CPU cores and hundreds of terabytes of memory, making personalized medicine and microbiome analysis prohibitively costly on single-node systems.

NMP-PaK places pipelined systolic Processing Elements (PEs) inside DIMM buffer chips (channel-level NMP) to exploit high internal memory bandwidth and reduce data movement latency. Each PE implements a 3-stage pipeline (Invalidation Check, TransferNode Extraction, Routing and Update) operating at MacroNode granularity, with an intra-DIMM crossbar switch and an inter-DIMM network bridge routing TransferNodes between PEs. Software optimizations complement the hardware: customized batch processing divides the genome into 10% batches to reduce peak memory footprint by 14x, pointer-aliasing deduplication eliminates redundant MacroNode copies, and a hybrid CPU-NMP strategy offloads large MacroNodes (>1 KB) to the CPU to avoid PE buffer oversizing and workload imbalance.

## The Key Experiment

- **speedup:** 16x over CPU baseline; 5.7x over GPU (A100); 8.3x throughput vs PaKman supercomputer under same resources
- **energy or tops w:** None
- **area:** None
- **ppa:** None
- **accuracy:** 14x memory footprint reduction; 2.4x reduction in memory operations
- **other:** Memory bandwidth utilization: 44% (NMP-PaK) vs 6.5% (CPU baseline)

**Compared against:** Software-optimized PaKman CPU baseline (Intel Xeon Platinum 8380, 40 cores); NVIDIA A100 40GB GPU; PaKman on supercomputer (16,384 cores, 1,024 nodes)

**Hardware:** PIM (processing-in-memory); CPU · **Workloads:** genomics

## Why This Approach

Channel-level NMP with pipelined systolic PEs co-designed specifically for the MacroNode data structure of DBG assembly, enabling parallel MacroNode-granular Iterative Compaction with inter-DIMM TransferNode routing and a hybrid CPU-NMP offload policy for irregular outliers.

This paper sits in the **memory hierarchy** subtheme. The core constraint: compute starves waiting for data — arithmetic throughput far outpaces DRAM bandwidth. This paper's solution: Systematic analysis showing that PaKman's Iterative Compaction is memory-latency-bound (54.2% stall time) with severely underutilized bandwidth (2.5% of 204.8 GB/s), making it suitable for channel-level NMP..

## What It Leaves Open

- NMP-PaK targets a single-node system
- the 8.3x throughput advantage over the supercomputer reflects resource efficiency, not raw speed—the supercomputer completes full human genome assembly 123x faster in wall time.

**Tags:** genomics, near-memory-processing, de-novo-assembly, dram-buffer-chip, hardware-software-codesign, de-bruijn-graph
