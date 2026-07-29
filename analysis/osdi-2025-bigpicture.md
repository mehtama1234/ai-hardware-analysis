# OSDI 2025: The Software Crisis of Hardware Diversity

## What OSDI Is

OSDI—the USENIX Operating Systems Design and Implementation conference—sits at a precise layer of the systems stack: one level above hardware, one level below applications. While hardware researchers (ISCA, MICRO, ASPLOS) design new processors, memory hierarchies, and accelerators, OSDI researchers build the runtime systems that *actually use* those resources. This includes kernels and OS abstractions, distributed schedulers, storage systems, compilers, database engines, and networking stacks. It's the layer that translates a pile of silicon into a usable machine.

The 68 papers at OSDI 2025 reveal a venue wrestling with a singular, systemic challenge: hardware has become radically heterogeneous and abundant, but the software systems that coordinate it have not kept pace. The result is inefficiency at scale—unused GPU cores, cold start delays in serverless, silent failures in distributed training, fragmented memory, underutilized network bandwidth, synchronization bottlenecks. This is not a problem of individual component performance; it is a problem of orchestration.

## The Central Problem: Heterogeneity Outpacing Abstraction

Five years ago, a data center housed GPUs, CPUs, and disks. Today it holds GPUs, TPUs, DPUs, specialized ASICs (for video, crypto, search), CXL-based pooled memory systems, NVMe-oF targets, and wafer-scale accelerators. And the software systems built to manage single homogeneous clusters no longer work.

Consider the concrete failures this heterogeneity creates:

**Scheduling breaks.** Modern ML clusters train with 4D parallelism (data, tensor, pipeline, sequence), but static allocation of parallelism dimensions leads to severe load imbalance. WLB-LLM measures the impact: naive workload distribution leaves GPU cores idle while waiting on synchronized barriers. The paper shows that adaptive re-balancing based on actual workload characterization can recover significant throughput. Similarly, XSched addresses a harder problem: how to preempt and migrate work across accelerators with completely different instruction sets and memory hierarchies. When a scheduler can't efficiently move work, hardware sits idle.

**Memory architecture assumptions break.** CXL memory pooling promises efficient resource sharing—applications no longer over-provision local memory for peak cases. But Tigon, a distributed database for CXL Pods, reveals that existing designs assumed tight memory-compute co-location. In a pooled architecture, the database must actively manage which data lives where, coordinate coherency across the pool, and reason about network latency between compute and pooled memory. FineMem surfaces a related problem: in disaggregated memory systems, if you allocate memory in large chunks to reduce overhead, you waste memory; if you allocate in small chunks to reduce waste, allocation overhead explodes. The paper demonstrates that no single granularity works; systems must adapt dynamically.

**Profiling and measurement become adversarial.** GPU profiling tools incur enormous overhead—they slow down the very kernels they measure, corrupting results. Tintin, KPerfIR, and Neutrino each address this from different angles: Tintin characterizes the intrinsic performance variability in modern hardware, KPerfIR integrates profiling directly into the Triton compiler to avoid explicit profiling overhead, and Neutrino embeds programmable probes into kernel execution. The underlying insight is that commodity hardware profiling tools were designed for homogeneous systems where you could afford to pause and sample globally; they fail in heterogeneous, always-on systems.

**Silent failures emerge at scale.** When distributed training spans hundreds of accelerators, silent errors accumulate: numerical instabilities from mixed-precision arithmetic, silent data corruption, misconfigured hyperparameters applied inconsistently across workers. TrainCheck and other papers show that traditional testing cannot catch these. Instead, systems must infer invariants from training code and monitor them at runtime.

These are not edge cases. They are the norm in production 2025. They happen because software abstractions—schedulers, compilers, file systems, networking stacks—were designed when hardware was simpler and more homogeneous. The new problem is not "how to use one GPU efficiently" but "how to use 1000 heterogeneous accelerators efficiently when their behavior is non-deterministic and their communication patterns are adversarial."

## Main Approaches

The papers at OSDI 2025 converge on four research directions that address this central tension.

### 1. Adaptive, Learned Scheduling and Orchestration

The first approach is to make schedulers *adaptive*—aware of actual workload behavior, capable of rebalancing, and learned from feedback.

**WLB-LLM** (Workload-Balanced 4D Parallelism) demonstrates the principle: instead of fixing parallelism dimensions at job submission time, the system monitors actual compute utilization and dynamically rebalances across dimensions. If the job is communication-bound in one dimension, shift parallelism to another. The result is measurable: on GPT-3 scale models, adaptive balancing recovers 10-15% throughput compared to static allocation.

**Quake** (Adaptive Indexing for Vector Search) applies similar ideas to database index structure. Static vector indexes like HNSW or DiskANN optimize for a fixed workload; they deteriorate as query and update patterns drift. Quake builds a learned cost model that observes workload shifts and dynamically repartitions the index. The system trades a small amount of overhead for continuous adaptation.

**Kamino** (Efficient VM Allocation at Scale) attacks scheduling from the cache perspective. Cache misses dominate latency in multi-tenant data centers; naive VM placement ignores this. Kamino instruments cache behavior and uses it to drive placement decisions—keeping co-located VMs whose working sets share cache lines, separating those that interfere. The paper shows that cache-aware scheduling recovers 15-20% latency improvement on latency-sensitive workloads.

The shared insight: *measurement-driven adaptation is necessary*. Static designs fail under heterogeneity. Systems must observe, learn, and adjust.

### 2. Measurement Without Overhead: Profiling and Error Detection Infrastructure

The second direction attacks a meta-problem: how do you measure a system without corrupting it? In classical OS/systems thinking, you could profile serially, or afford global synchronization. Modern systems cannot.

**KPerfIR** integrates profiling into the Triton GPU compiler itself. Instead of external profiling tools that instrument and slow kernels, KPerfIR collects performance data *as the compiler generates code*, capturing kernel metrics without runtime overhead. The result: fine-grained profiling of AI workloads becomes practical.

**Tintin** takes a statistical approach, characterizing the *inherent variability* in hardware performance. A GPU kernel executed twice rarely takes the same time; DRAM, CPU, and cache effects introduce jitter. Tintin quantifies this variability and provides it to higher-level systems (schedulers, resource managers) so they can reason probabilistically instead of assuming determinism.

**TrainCheck** and **Deriving Semantic Checkers from Tests** address silent failures by automating invariant inference. The systems analyze training or test code, extract properties that should hold (e.g., "loss should decrease monotonically in this phase," "gradient magnitudes stay in this range"), and monitor them at runtime. When an invariant breaks, the system alerts before results are corrupted. This is especially critical for distributed training: a single silently corrupt gradient update can skew model weights across the entire cluster before anyone notices.

The shared insight: *overhead-free or low-overhead observability is essential infrastructure*. Profiling, error detection, and monitoring must not themselves degrade the system they observe.

### 3. Rearchitecting Core Abstractions for New Constraints

The third direction recognizes that some problems cannot be solved by better scheduling alone; the abstractions themselves need to change.

**Tigon** redesigns distributed database architecture for CXL memory pools. Traditional databases optimize for disk or local memory; Tigon assumes memory is pooled, coherent, and network-distant. It rearchitects data placement, query execution, and consistency protocols around this model.

**Okapi** decouples data striping (for parallelism) from redundancy grouping (for fault tolerance). Traditional cluster file systems couple these—you stripe data across *the same physical servers* that hold replicas. Okapi shows this is suboptimal. Decoupling allows separate optimization: stripe for maximum parallelism *and* replicate for maximum fault tolerance without artificial alignment. The result is better disk utilization and improved recovery times.

**Write-Once File Systems** (Fast and Synchronous Crash Consistency) rethink crash recovery entirely. Instead of journals and undo logs, the system ensures metadata is written sequentially to permanent storage, guaranteeing that recovery simply replays the log. This simplifies correctness reasoning and eliminates journal overhead.

**EMT** (OS Framework for New Memory Translation Architectures) recognizes that page-based virtual memory is no longer universal. New architectures propose segmentation, multi-level translation, or hardware-accelerated table walks. EMT provides a flexible OS abstraction layer that can support diverse translation schemes without rewriting device drivers and applications.

The shared insight: *once hardware assumptions change, software abstractions must change too*. No amount of clever scheduling recovers the efficiency you get from rearchitecting for the new model.

### 4. Consistency, Correctness, and Safety Under Scale

The fourth direction addresses a subtle but critical problem: as systems grow and become heterogeneous, how do you ensure they remain correct?

**Mako** (Speculative Distributed Transactions with Geo-Replication) tackles geo-replication latency. Synchronous quorums are safe but slow; async replication is fast but risks data loss. Mako uses speculative execution: transactions tentatively commit at replica sites before waiting for full quorum acknowledgment, and the system detects conflicts speculatively. The result is low latency without sacrificing strong consistency.

**Picsou** (Replicated State Machines Communication) addresses a gap: RSMs are well-understood abstractions for fault tolerance, but they cannot communicate efficiently across cluster boundaries. Picsou introduces Cross-Cluster Consistent Broadcast (C3B), inspired by TCP's reliability principles but designed for cluster-to-cluster messaging.

**Basilisk** (Using Provenance Invariants to Automate Proofs) goes further: it automates correctness proofs of distributed protocols by reasoning about data flow origins. Provenance invariants—tracking where each piece of state came from—can guide automated verification of undecidable properties. This is essential for protocols like Byzantine consensus that defy traditional verification.

**KRR** (Efficient and Scalable Kernel Record Replay) enables deterministic replay of kernel-level execution for debugging. In multithreaded, multi-device systems, recording overhead is prohibitive. KRR uses selective event logging and optimized compression to make recording practical at scale.

The shared insight: *correctness becomes harder as systems grow; you cannot debug by hand*. Automated verification, replay, and invariant checking are necessary infrastructure.

## What This Adds to the Hardware Picture

Hardware conferences (ISCA, MICRO, ASPOLS) focus on *component innovation*: new cache hierarchies, specialized accelerators, improved interconnects. They ask "what can we build?" OSDI asks "how do we use what we've built?"

The relationship is complementary but tense. Hardware researchers often optimize for peak throughput or efficiency in idealized scenarios. A new GPU design might deliver 2x throughput when fully utilized—but if the scheduler cannot keep it fully utilized, the real-world gain is much smaller. Tigon, WLB-LLM, and Kamino reveal this gap. CXL memory is a hardware innovation that promises efficiency; Tigon shows that software must be redesigned to realize it. Speculative execution is a hardware feature that improves latency; Mako shows how to exploit it correctly at the software layer.

Conversely, OSDI papers reveal problems that hardware alone cannot solve. Heterogeneity is a permanent feature of modern data centers—you cannot design a single processor that is optimal for video encoding, cryptography, graph traversal, and matrix multiply. Instead, the OS layer must *multiplex* heterogeneous resources and adapt allocation based on workload. This is fundamentally a software problem.

Similarly, silent failures in distributed training stem from numerical properties of algorithms—mixed-precision arithmetic, stale gradient updates, consistency violations. No hardware feature can detect these; TrainCheck, Understanding Stragglers, and similar papers show that observability must be baked into the runtime.

The net effect: OSDI 2025 is a venue deeply engaged with *translating hardware capability into usable throughput*. It sits at the software-hardware interface and solves the problems that neither layer can solve alone.

## Open Problems

The papers leave several hard problems unsolved:

- **Unified profiling and adaptive control.** Papers like KPerfIR and Tintin measure subsystems independently; no system yet integrates profiling (kernel, network, memory, compute), builds a unified cost model, and uses it to drive scheduling decisions across all layers. How do you build a truly holistic profiler?

- **Correctness by design in heterogeneous systems.** Basilisk, TrainCheck, and others detect errors after they occur. Can systems be designed so errors become impossible? What invariants should be built into hardware and OS to prevent silent failures at scale?

- **Scheduling under uncertainty.** WLB-LLM and Kamino assume you can measure workload behavior and rebalance. But measurement is imperfect (Tintin shows inherent variability), and rebalancing has cost. How should a scheduler balance the cost of measurement and adaptation against the gain from better decisions?

- **Memory hierarchy rearchitecture.** CXL, wafer-scale accelerators, and disaggregated memory are new; software abstractions are immature. How should the OS model memory coherency, affinity, and allocation across radically different physical architectures? Should page-based virtual memory survive, or should new abstractions replace it?

- **Scaling verification and debugging.** KRR, Basilisk, and others make verification and replay practical; but as systems grow to thousands of nodes, even these optimized approaches become expensive. What scalable debugging and verification infrastructure do data center OS need?

These are not incremental improvements. They are fundamental rethinks of how software should be designed for 2025's hardware landscape.

---

**OSDI 2025 in one sentence:** The systems software community is learning to coordinate radically heterogeneous, high-variance hardware at scale—through adaptive scheduling, low-overhead observability, rearchitected abstractions, and automated correctness reasoning—because static designs no longer work.
