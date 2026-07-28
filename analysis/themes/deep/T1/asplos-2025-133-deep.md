# CoServe: Efficient Collaboration-of-Experts (CoE) Model Inference with Limited Memory

**Venue:** ASPLOS · **Theme:** Sparse / MoE Attention

## What It Does

Collaboration-of-Experts (CoE) inference on memory-constrained edge devices (e.g., RTX 3080Ti with 12 GB GPU memory) requires serving hundreds of expert models (e.g., 300+ ResNet101/YOLOv5 experts totaling 60 GB) that cannot fit in GPU memory, forcing expert swapping from CPU or SSD where switching latency accounts for over 90% of total inference latency.

CoE systems achieve higher accuracy than single large models (99.9% vs. 92% for circuit board defect detection) and must run at the edge for privacy and latency reasons, but the memory-constrained expert-switching bottleneck makes existing MoE-style management strategies (LRU, FCFS) severely inefficient for CoE's deterministic routing structure.

CoServe exploits expert dependency, a key property of CoE inference where the routing module determines expert sequences offline (unlike MoE where routing is runtime-only). Three mechanisms are combined: (1) dependency-aware request scheduling that groups requests using the same expert together within a queue window and assigns requests to minimize total inference time across parallel CPU+GPU executors; (2) dependency-aware expert management with a two-stage eviction policy that first evicts dependency-orphaned subsequent experts (sorted by memory footprint) and then evicts by ascending usage probability (computed offline from routing rules); (3) an offline profiler using microbenchmarks to determine optimal memory allocation (via a CDF-based sliding decay window search over expert count) and executor configuration per device.

## The Key Experiment

- **speedup:** 4.5x to 12x throughput over Samba-CoE on NUMA and UMA devices
- **energy or tops w:** None
- **area:** None
- **ppa:** None
- **accuracy:** None
- **other:** expert switching reduced by up to 93.87% (1060 to 65 switches); expert switching latency is 90%+ of total inference latency in baseline

**Compared against:** Samba-CoE (LRU+FCFS); Samba-CoE FIFO; Samba-CoE Parallel

**Hardware:** GPU; CPU · **Workloads:** vision; CNN

## Why This Approach

Exploiting the deterministic routing structure of CoE (pre-assessable expert usage probabilities and dependency graphs) to enable dependency-aware request scheduling and expert eviction that is impossible in MoE systems where routing is only known at runtime.

This paper sits in the **attention efficiency** subtheme. The core constraint: generating one token requires reading all past key-value vectors from memory — O(n) bandwidth per step. This paper's angle: Identification of expert dependency as the key overlooked property enabling efficient CoE serving, distinct from MoE.

## What It Leaves Open

- Evaluation uses only circuit board inspection workloads with ResNet101/YOLOv5 experts
- generalization to language-model CoE or highly dynamic routing distributions is not demonstrated.

**Tags:** collaboration-of-experts, edge-inference, expert-switching, memory-management, request-scheduling, heterogeneous-cpu-gpu
