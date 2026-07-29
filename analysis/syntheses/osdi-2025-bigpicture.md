# OSDI 2025: The Software That Makes Hardware Usable

## What OSDI Is

OSDI — the USENIX Symposium on Operating Systems Design and Implementation — sits one layer above the hardware in the computing stack. Where ISCA and MICRO design the chips, and ASPLOS maps computations to hardware, OSDI builds the systems that let thousands of people share those chips without colliding: schedulers that decide which job runs on which GPU, distributed training frameworks that coordinate gradient synchronization across a thousand nodes, storage systems that move model weights into GPU memory at the right moment, and observability tools that reveal why a training run is 40% slower than it should be. The 53 papers at OSDI 2025 collectively answer: given that we have fast hardware, why isn't it being used efficiently?

## The Central Problem

Modern ML infrastructure has a heterogeneity problem. A data center running large language model training in 2025 houses dozens of GPU types (A100, H100, H200, Grace-Hopper), multiple memory tiers (HBM, CXL-attached DRAM, NVMe), several networking fabrics (NVLink within a node, InfiniBand between nodes, Ethernet for storage), and increasingly, co-located CPU and GPU workloads sharing the same physical servers. Every scheduler, allocator, and communication library in use today was designed for a simpler, more homogeneous world.

The consequence is waste. WLB-LLM at OSDI 2025 quantifies the gap for 4D-parallel LLM training: pipeline parallelism, tensor parallelism, data parallelism, and expert parallelism all interact in ways that cause some GPUs to idle while others are saturated, and workload-aware balancing recovers 10–15% throughput on production training runs. At the storage layer, Tigon finds that distributing a database across a CXL Pod — where all nodes share a high-bandwidth memory fabric — with a scheduler designed for distributed DRAM creates unnecessary serialization. At the networking layer, FuseLink shows that static GPU-to-NIC binding leaves 40–60% of available bandwidth untapped when multiple NICs are available but not jointly managed.

The deeper pattern: hardware keeps adding capabilities (CXL, RDMA, NVLink, photonic interconnects) that systems software doesn't yet know how to exploit. The gap between raw hardware bandwidth and achieved system throughput is a software problem.

## Main Approaches

### Adaptive Scheduling for Heterogeneous Workloads

The most common response in the corpus is to replace static scheduling policies with dynamic, measurement-driven ones. WLB-LLM uses workload profiling to adaptively rebalance 4D parallelism at training time, handling the uneven computation that arises when sequences in a batch have different lengths. Quake identifies and handles training failure — silent gradient corruption, straggler nodes, NaN propagation — by combining lightweight statistical monitoring with automated checkpoint and restart, reducing the debugging overhead of large-scale training failures. KVCache Cache in the Wild characterizes production KV cache workload patterns from a leading LLM provider and uses those patterns to build a tiered caching policy that increases KV cache hit rates by 2.3× against LRU, with direct impact on inference cost.

### Rearchitecting Abstractions for New Hardware

Several papers recognize that existing abstractions were wrong for the hardware they're running on, not just poorly tuned. Tigon rebuilds a distributed database from scratch for a CXL Pod — a set of servers sharing CXL memory — treating CXL as a first-class memory tier rather than remote storage, and achieves 4.7× lower latency than conventional distributed databases on transaction workloads. Okapi decouples striping from replication in distributed file systems to handle heterogeneous storage devices, separating the data layout choice (how to spread data across devices) from the durability choice (how many copies to keep), enabling mixed SSD/HDD pools without the performance collapse conventional systems suffer. FuseLink builds a unified NIC management layer that lets GPU collective operations (all-reduce, broadcast) use all available NICs simultaneously, achieving 212 Gbps of inter-server bandwidth on servers with multiple 100G NICs.

### Correctness and Observability at Scale

At large scale, failures are not exceptional — they are continuous background noise. TrainCheck instruments distributed training jobs with lightweight invariant monitoring (gradient norms, activation ranges, loss curves) that can detect silent corruption in minutes rather than the hours a manual inspection would require. Tintin provides hardware performance counter infrastructure that reveals not just what a program is doing but why performance varies between runs — exposing sources of nondeterminism in GPU kernel scheduling that naive profiling misses. Kamino solves the distributed snapshot problem for long-running training: taking a consistent checkpoint of a training job's full state across a thousand GPUs without pausing training, using a variation of the Chandy-Lamport algorithm adapted for the collective-communication patterns of ML frameworks.

### Systems Software for Emerging Hardware Paradigms

A small but significant cluster of papers addresses hardware that barely existed two years ago. DecDEC at OSDI 2025 addresses on-device LLM inference under memory constraints: it stores a low-bit quantized model on the GPU but maintains a residual correction matrix in CPU DRAM, fetching residuals on demand for "salient" channels (those where quantization error is highest). The result: 3-bit Llama-3-8B achieves perplexity close to FP16 quality with only 1.7% latency overhead, by treating CPU DRAM as a fast spillover for the bits that matter most. Several papers also address quantum computing infrastructure: Quantum Virtual Machines introduces an intermediate representation layer between quantum programs and physical qubit control systems, analogous to what LLVM does for classical programs.

## What This Adds to the Hardware Picture

The hardware-focused venues (ISCA, MICRO, HPCA) design components that are individually fast; OSDI makes those components collectively efficient. A hundred-GPU cluster might have 100 TB/s of aggregate NVLink bandwidth — but if the collective communication library serializes all-reduces onto a single NIC, the effective inter-node bandwidth is 12.5 Gbps. FuseLink's contribution is not hardware design but systems engineering: recognizing that the scheduler's static assignment of GPU operations to network interfaces was the bottleneck, and fixing it in software.

The same pattern applies to memory. HBM3e has 3.35 TB/s of bandwidth per GPU — but if the KV cache eviction policy is LRU and production LLM serving workloads have a temporal reuse pattern that defeats LRU (short popular contexts interleaved with long unpopular ones), the effective cache efficiency is 30% of what's possible. KVCache Cache in the Wild's contribution is workload characterization: measuring what production traffic actually looks like, and discovering that workload-aware tiering almost doubles cache hit rates.

OSDI research turns hardware specifications into delivered performance.

## Open Problems

- **Unified profiling across the stack**: current tools profile either hardware (performance counters) or software (traces), but the interaction between GPU kernel scheduling and NIC DMA timing remains invisible; a joint observability layer doesn't exist
- **Scheduling under uncertainty**: adaptive schedulers require feedback about hardware state, but that feedback arrives with latency — a scheduler that reacts to a gradient imbalance detected 2 seconds ago may have already wasted a full training step
- **Correctness by construction for distributed ML**: TrainCheck and similar tools detect failures reactively; proactively designing distributed training protocols that cannot corrupt model state (not just detect when they have) is unsolved
- **Memory hierarchy rearchitecture for CXL scale**: Tigon shows CXL enables new database designs, but the right abstractions for a multi-tier memory hierarchy spanning HBM/DRAM/CXL/NVMe — at cache-coherence granularity — are not established
- **Quantum-classical resource management**: as quantum co-processors are attached to classical servers, the scheduler needs to reason about qubit availability, decoherence time, and quantum-classical data movement simultaneously; no general framework exists
