# Boosting Task Scheduling Data Locality with Low-latency, HW-accelerated Label Propagation

**Venue:** MICRO · **Theme:** KV Cache Scheduling

## What It Does

Hardware-accelerated task schedulers dispatch ready tasks to the first available core without locality awareness, causing cache misses when dependent tasks execute on different cores. Existing locality-aware policies require static programmer hints or incur high scheduling overhead incompatible with fine-grained tasks.

Fine-grained task-parallel workloads on many-core systems suffer from data cache misses that negate parallelism gains because conventional task schedulers ignore data dependency graphs when making placement decisions.

The paper introduces Task-LP, a hardware label propagation (LP) accelerator that clusters up to 128 in-flight tasks by running a semi-synchronous graph clustering algorithm on the dynamic task dependency graph built by Picos. Task-LP uses a bitmask adjacency matrix, color-iteration parallelism (First-Fit online graph coloring), and bitwise popcount to compute label popularity; it converges in under 300 cycles for typical inputs. A Task Placement Engine (TPE) combines LP cluster labels with core-idleness signals via a tunable relaxation policy (cycle-length parameter R_len) to balance locality and core utilization. The full system is prototyped on a 24-core RISC-V (Rocket Chip) mapped to an Alveo U55C FPGA, interfaced via custom RoCC instructions and the Phentos task scheduling API.

## The Key Experiment

- **speedup:** up to 1.50x program execution time improvement on 24 cores
- **energy or tops w:** None
- **area:** 0.313 mm2 at GF 12 nm for 128-node Task-LP configuration
- **ppa:** 600+ MHz timing met in ASIC synthesis
- **accuracy:** clustering modularity statistically indistinguishable from software LP
- **other:** LP accelerator 581x faster than equivalent software LP; task size reduction up to 1.81x

**Compared against:** Random Task Stealing (GNU OpenMP / Nanos baseline); Immediate Successor (IS) locality policy; software label propagation; Fast Greedy clustering

**Hardware:** RISC-V; FPGA; ASIC · **Workloads:** graph-analytics; HPC

## Why This Approach

A hardware label-propagation accelerator that clusters dynamic task dependency graphs in under 300 cycles (up to 581x faster than software), enabling runtime data-locality-aware task placement with negligible scheduling overhead.

This paper sits in the **attention efficiency** subtheme. The core constraint: generating one token requires reading all past key-value vectors from memory — O(n) bandwidth per step. This paper's angle: Task-LP: a parametrized HW label-propagation accelerator clustering 128-node task graphs in under 600 cycles, synthesized at 0.313 mm2 in GF 12 nm.

## What It Leaves Open

- The 128-node context window limits visibility of long-range task dependencies
- larger windows grow area super-linearly (~N^1.58), and gains diminish for compute-bound workloads where random placement already achieves high core utilization.

**Tags:** task-scheduling, data-locality, graph-clustering, label-propagation, risc-v, fpga
