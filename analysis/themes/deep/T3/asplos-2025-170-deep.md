# PUSHtap: PIM-based In-Memory HTAP with Unified Data Storage Format

**Venue:** ASPLOS · **Theme:** In-Memory HTAP

## What It Does

Hybrid transaction/analytical processing (HTAP) systems cannot simultaneously achieve workload-specific optimization, performance isolation, and data freshness because OLTP demands row-store format while OLAP demands column-store format, and existing solutions (single format, multi-instance with rebuilding, or mixed delta-store) compromise at least one goal.

The emergence of PIM (Processing-in-Memory) DRAM devices creates a new access dimension—CPU interleaving across devices (ADE) versus localized PIM access inside devices (IDE)—that can simultaneously satisfy row-access and column-access requirements in a single data instance without format replication.

PUSHtap maps HTAP rows to the CPU's interleaved access dimension (ADE) and columns to the PIM's localized access dimension (IDE) in a single-instance DRAM store. A compact aligned format uses a bin-packing algorithm with a tunable threshold to group columns of similar width into parts, minimizing zero-padding while preserving alignment for both CPU and PIM bandwidth efficiency. Block-circulant placement rotates column-to-PIM-device mapping every 1024-row block, ensuring uniform PIM parallelism load balance across all columns. MVCC is implemented with a data region and delta region; snapshotting encodes row visibility as compact bitmaps that are written to each device in parallel, and defragmentation is offloaded to PIM units when row width exceeds a computed threshold. A modified memory controller adds a scheduler and polling module to support fine-grained interleaved CPU/PIM concurrent access, with a two-phase load/compute OLAP execution model that limits CPU access blocking to 300 microseconds per load phase.

## The Key Experiment

- **speedup:** 3.4x OLAP and 4.4x OLTP throughput vs. multi-instance PIM-based HTAP; PUSHtap (HBM) achieves 1.4x additional OLAP speedup vs. DIMM at 8M transactions
- **other:** PIM effective bandwidth 97.4% at th=0.6; snapshot bitmap overhead 2.3% of storage; zero-padding overhead 0.8% of storage; memory controller derived at TSMC 90nm 2.4GHz

**Compared against:** multi-instance PIM-based HTAP (MI, Polynesia-style); row-store single format; column-store single format; ideal (no MVCC overhead)

**Hardware:** PIM (processing-in-memory); CPU · **Workloads:** database

## Why This Approach

Exploiting the orthogonality of CPU interleaved access (ADE, row-dimension) and PIM localized access (IDE, column-dimension) to implement a single unified data format that simultaneously serves both OLTP and OLAP without format duplication or rebuilding.

This paper sits in the **memory hierarchy** subtheme. The core constraint: compute starves waiting for data — arithmetic throughput far outpaces DRAM bandwidth. This paper's solution: Unified HTAP data storage format combining compact aligned format (bin-packing) and block-circulant placement for co-optimized CPU and PIM bandwidth.

## What It Leaves Open

- Block-circulant placement and compact aligned format assume a relatively stable OLAP query workload to classify key columns
- highly dynamic query patterns requiring frequent threshold adjustment are not fully addressed.

**Tags:** pim, htap, database, dram, mvcc, unified-format
