# USENIX ATC 2025: Where Systems Software Meets the Machine

## What USENIX ATC Is

USENIX Annual Technical Conference is the broadest systems venue in computing — covering operating systems, storage, networking, distributed systems, and increasingly, the systems software infrastructure for machine learning. Unlike OSDI which focuses on research systems, ATC has a strong tradition of papers about production deployments: systems that are running at scale, with real workload traces, at companies large enough to have measured the gap between what their infrastructure theoretically delivers and what users actually experience. The 100 papers at ATC 2025 span from classical systems (key-value stores, file systems, storage engines) to the new problems created by LLM serving at scale (KV cache management, inference scheduling, disaggregated memory).

## The Central Problem

ATC 2025's corpus divides into two distinct worlds that are colliding: the mature world of distributed systems (databases, file systems, consensus protocols, network stacks) and the new world of LLM infrastructure (inference serving, KV cache tiering, memory-disaggregated model loading). The collision is productive — LLM systems have made the old problems (scheduling, caching, memory management) newly urgent by scaling them by two orders of magnitude and adding hard latency constraints that batch-processing infrastructure never had.

The central problem is resource sharing under heterogeneity. An LLM serving cluster at a major provider handles requests with contexts ranging from 100 tokens to 100,000 tokens; KV cache entries for a 100K-token context are 1,000× larger than for a 100-token context. A scheduler designed for uniform request sizes either over-provisions memory for short requests or starves long requests. The same heterogeneity appears in storage (fast SSDs and slow HDDs sharing the same pool), in networks (RDMA and TCP coexisting), and in compute (CPU and GPU sharing the same physical server). ATC 2025's dominant question: how do you build systems that work well across this range?

## Main Approaches

### KV Cache and LLM Serving Infrastructure

The largest cluster in the corpus addresses the operational reality of running LLMs in production. "KVCache Cache in the Wild" provides something rare in systems research: a characterization of production LV cache access patterns from a leading LLM provider at scale. The key finding: LLM serving workloads have a prefix-dominant reuse pattern (many requests share the same system prompt prefix) that conventional LRU eviction misses, and a tiered policy that identifies and pins shared prefixes increases hit rates by 2.3×. Primus, from a major tech company, addresses the heterogeneity of recommendation model training: these models have embedding tables that are 10-100× larger than the compute graph, and a unified training system that treats embeddings as first-class citizens (sharded differently from parameters, communicated differently from gradients) achieves 1.8× throughput over generic frameworks. Several papers address the scheduling problem for inference: given variable request sizes and hard SLA constraints (P99 latency under 500ms), how do you schedule prefill (the expensive prompt processing) and decode (the incremental token generation) without blocking short requests behind long ones?

### Storage and KV Stores for Modern Hardware

The traditional ATC core — storage systems and key-value stores — remains strong, now heavily influenced by NVMe SSDs and RDMA networking. "Mitigating Resource Usage Dependency in Sorting-based KV Stores" addresses a structural problem in LSM-tree databases (the design underlying LevelDB and RocksDB): compaction, writes, and reads all compete for I/O bandwidth in ways that create unpredictable latency spikes. The solution — decoupling these operations onto separate I/O paths — requires restructuring the storage engine but eliminates P99 latency spikes entirely. "Fast Distributed Transactions for RDMA-based Disaggregated Memory" exploits the key property of RDMA: one-sided reads complete without involving the remote CPU, enabling sub-microsecond reads. The paper designs a distributed transaction protocol specifically for this model, achieving 3-5× lower latency than RDMA-unaware protocols for read-heavy workloads.

### Memory Disaggregation and CXL

CXL (Compute Express Link) appears throughout the corpus as a hardware capability that systems software hasn't fully exploited yet. Several papers characterize CXL memory latency in production (140–410 nanoseconds for remote memory vs. 60–80 nanoseconds for local DRAM) and show that tiering policies must account for latency variance, not just latency mean. HybridTier uses a two-dimensional hotness metric — long-term frequency plus short-term "momentum" (whether accesses are increasing or decreasing) — to predict which pages to keep in fast local DRAM, achieving 2–7.8× lower memory management overhead than Linux's default NUMA balancing. A separate paper shows that sub-page granularity migration (moving 64-byte words rather than 4KB pages) recovers 14% additional throughput on workloads with fine-grained hot data.

### Reliability and Observability for Large-Scale ML

Running ML training across thousands of GPUs means hardware failures are not exceptional events — they happen multiple times per hour. ATC 2025 has a cluster of papers addressing the operational burden: detecting failures, checkpointing efficiently, and recovering without losing training progress. The challenge is that many ML framework failures are silent: a NaN in one gradient tensor doesn't crash the job, it simply corrupts the model, and the corruption may not be visible until model quality evaluations run hours later. Papers in this cluster focus on lightweight invariant monitoring (checking gradient norms and activation ranges every step, not every hour) combined with efficient rollback to the last clean checkpoint.

## What This Adds to the Hardware Picture

The hardware conferences (ISCA, MICRO, HPCA) optimize peak throughput; ATC optimizes sustained, real-world throughput. The gap between the two is often 50-70% for production ML workloads. The reasons are almost entirely in the systems layer: memory fragmentation, scheduling inefficiency, suboptimal caching, and communication serialization. ATC's contribution to the AI hardware picture is precise quantification of these gaps and deployable software fixes that don't require new silicon.

The KV cache characterization paper is a good example: HBM capacity on an H100 is 80GB, and optimizing the 80GB you have with a workload-aware eviction policy is equivalent (in throughput terms) to having 1.8× the HBM, but costs zero dollars in hardware. Systems software is the cheapest hardware upgrade.

## Open Problems

- **Unified scheduling for prefill and decode**: current inference systems treat prefill (quadratic compute) and decode (linear memory-bandwidth) as separate phases, requiring separate scheduling policies; a unified policy that handles the transition between phases without resource waste doesn't exist
- **KV cache consistency across inference replicas**: when the same KV cache entry is needed by multiple replicas serving different users, coherence protocols from distributed databases may apply, but adapting them to the microsecond timescales of LLM inference is unsolved
- **Automatic policy synthesis for heterogeneous storage**: choosing between tiering policies, prefetching strategies, and migration granularities for a specific workload currently requires manual tuning; learned policies that generalize across workload types remain brittle
- **ML training failure attribution**: detecting that a training run has failed is solved; attributing the failure to a specific GPU, a specific batch, or a specific gradient computation — automatically and within seconds — is not
- **Resource allocation under unknown future context length**: inference schedulers must allocate KV cache space when a request arrives, but context length isn't known until generation completes; scheduling under this uncertainty without over-provisioning is an open problem with no clean solution
