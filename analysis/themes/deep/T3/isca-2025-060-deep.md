# Garibaldi: A Pairwise Instruction-Data Management for Enhancing Shared Last-Level Cache Performance in Server Workloads

**Venue:** ISCA · **Theme:** Instruction-Data Management

## What It Does

Server workloads suffer from a 'instruction victim' problem in the shared LLC: cold instruction cachelines are evicted by competing hot data cachelines, yet each instruction miss stalls the CPU frontend regardless of how much hot data is already resident in the LLC. Existing LLC management policies (Mockingjay, Hawkeye, DRRIP) optimize for data reuse distance and ignore the cost asymmetry between instruction and data misses.

Server workloads exhibit a many-to-few access pattern (many cold instruction lines each accessing a few hot data lines), which means that existing data-hotness-driven eviction policies systematically sacrifice instructions whose miss cost is highest, causing frontend stall cycles to dominate multi-core server CPI.

Garibaldi introduces a pairwise instruction-data LLC management scheme built on three mechanisms: (1) a pair table (16K direct-mapped entries, 194 KB total) that tracks each instruction physical address alongside the hotness (miss_cost counter, 6-bit saturating) of the data cachelines it triggers; (2) a selective instruction protection policy using a query-based selection (QBS) mechanism that, at eviction time, queries the pair table and overrides the replacement policy to retain any instruction line whose aged miss_cost exceeds a dynamically adjusted threshold; (3) a pairwise prefetch that, upon serving an unprotected instruction miss, proactively issues prefetch requests for the associated cold data lines recorded in the pair table. Dynamic threshold adjustment uses a synchronized l-bit coloring timer that tracks P(D_miss | I_miss) every 100K LLC accesses and raises or lowers the protection threshold accordingly.

## The Key Experiment

- **speedup:** 13.2% geomean over LRU baseline (6.1% over Mockingjay alone) on 40-core server; up to 65.2% on verilator
- **energy or tops w:** 10.4% energy reduction vs LRU (5.0% below Mockingjay alone)
- **area:** 193.9 KB total storage overhead for 40 cores (0.6% of 30 MB LLC)
- **other:** 18% reduction in ifetch stall cycles vs LRU with Mockingjay+Garibaldi

**Compared against:** LRU; DRRIP; Hawkeye; Mockingjay

**Hardware:** CPU · **Workloads:** database; HPC

## Why This Approach

Garibaldi is the first LLC management scheme to quantify the opportunity cost of instruction misses in terms of the hotness of the data they trigger, propagating data-line hotness back to instruction lines via a pair table and using it to drive selective eviction protection and prefetching.

This paper sits in the **memory hierarchy** subtheme. The core constraint: compute starves waiting for data — arithmetic throughput far outpaces DRAM bandwidth. This paper's solution: Identification and analysis of the instruction victim problem in shared LLCs for server workloads, showing 95-99% instruction miss rates in the LLC even with advanced prefetching..

## What It Leaves Open

- Garibaldi can slightly hurt performance in workloads where both instructions and data are cold (e.g., kafka), and its pair table requires a large number of entries (16K) because instruction-data pairs do not share LLC sets, making set-sampling-based approaches inapplicable.

**Tags:** llc, cache-replacement, server-workloads, instruction-cache, frontend-bottleneck, pairwise-management
