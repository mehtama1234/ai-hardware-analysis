# ρHammer: Reviving RowHammer Attacks on New Architectures via Prefetching

**Venue:** MICRO · **Subtheme:** DRAM Row-Hammer Attack Evolution Under Microarchitectural Defenses

## What It Does

ρHammer introduces a novel prefetch-based Rowhammer attack that bypasses the microarchitectural defenses of recent Intel processors (Alder Lake, Raptor Lake) where conventional load-based Rowhammer attacks (using MOV instructions with CLFLUSHOPT) have become completely ineffective. The attack combines three coordinated techniques: (1) A reverse-engineering algorithm for DRAM address mappings using structured pairwise SBDR (Same-Bank Different-Row) timing measurements—a Duet/Trios/Quartet deduction process that recovers full bank interleaving functions in polynomial time without prior knowledge of bank bit assignments. (2) A prefetch-based hammering paradigm exploiting x86 PREFETCHT2/PREFETCHNTA instructions, which retire from the CPU pipeline after forwarding to the L1 LFB (Line Fill Buffer) without blocking the CPU, enabling asynchronous row activation. Crucially, prefetch instructions cannot be ordered by memory barriers (per Intel SDM), giving them orthogonal timing properties compared to loads. (3) A counter-speculation technique combining control-flow obfuscation (indirect addressing) and NOP-based pseudo-barriers that mitigate the impact of out-of-order execution and branch prediction reordering, which would otherwise scatter prefetch issuance and break the hammering pattern.

The attack works by issuing sequences of prefetch instructions targeting different DRAM rows in the same bank, exploiting multi-bank parallelism to maximize per-tREFI (refresh interval) row activation count while also spreading activations across banks to avoid triggering per-bank thresholds. Unlike load-based attacks which serialize on cache misses, prefetch instructions pipeline aggressively: the CPU issues many prefetches in quick succession, and the async LFB handles fetches in parallel. On Comet Lake and Rocket Lake, ρHammer achieves 187K and 47K bit flips per minute, respectively—112x and 47x higher than load-based baselines. Critically, ρHammer is the first to successfully demonstrate working Rowhammer attacks on Raptor Lake (14th-gen Intel), achieving 2,291 flips/minute where all prior load-based methods produce zero flips.

## The Key Result

On Comet Lake, ρHammer achieves 187K bit flips per minute with prefetch-based hammering versus ~1.7K for conventional load-based attacks (112.4x improvement). On Rocket Lake, it achieves 47K flips/min vs. 1K for loads (47.1x). On Raptor Lake, ρHammer achieves 2,291 flips/min in 2-hour fuzzing sessions, enabling end-to-end exploitation—setting a critical baseline for modern CPU Rowhammer exploitability. The address mapping reverse-engineering completes in under 10 seconds on Alder/Raptor Lake systems where all existing reverse-engineering tools fail.

## Why This Approach

Rowhammer remains a fundamental DRAM vulnerability on every processor with out-of-order execution and prefetch engines. Prior attacks relied on high load throughput (many MOV + CLFLUSH sequences per refresh interval) to trigger bit flips. Modern CPUs mitigate this through: (1) load address prediction and reordering that disrupts hammering sequences, (2) more aggressive out-of-order execution that unpredictably orders memory operations, and (3) TRR (Targeted Row Refresh) firmware that detects suspicious row activation patterns. However, CPUs cannot easily disable prefetching—it is critical for performance—and prefetch instructions have asymmetric properties: they bypass memory barriers and retire asynchronously, making them harder to rate-limit with traditional countermeasures. ρHammer exploits this asymmetry. The prefetch-based paradigm is CPU-vendor agnostic (prefetching exists on all modern x86); address mapping reverse-engineering is generic (no prior knowledge of bank functions needed). This work demonstrates that architectural defenses must specifically account for prefetch instructions, and that Rowhammer remains a viable threat on the newest processors.

## What It Leaves Open

- Reverse-engineering and attack execution require Linux pagemap access (root privileges); the attack does not work unprivileged on hardened systems with pagemap restrictions.
- DDR5 (with PRAC+ABO mitigation) and DDR4 with TRR are explicitly out of scope; unclear whether prefetch-based attacks generalize to these protected DRAM types.
- RowPress attacks (exploiting refresh command timing) are not addressed; complementary prefetch-based RowPress attacks are unexplored.
- Microarchitectural variation: the attack was demonstrated on Intel (Comet/Rocket/Raptor Lake) and AMD Ryzen, but effective prefetch patterns likely differ across other vendors and future architectures.
- Defenses specific to prefetch-based attacks (e.g., rate-limiting prefetch queue depth, randomizing prefetch latencies) are not evaluated.
