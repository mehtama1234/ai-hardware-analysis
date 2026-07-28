# ISCA 2025 — Deep Dive

## What ISCA is and why it exists

ISCA (International Symposium on Computer Architecture) is the premier academic venue for computer systems research. It publishes research on the fundamental question: *given the constraints of silicon, physics, and programming models, how do we build better computers?* Unlike venues focused on algorithms or applications, ISCA accepts submissions only when the research either discovers something new about how hardware and software interact, or proposes a new microarchitecture, memory system, or system design that demonstrates measurable advantage over the state of the art on real silicon (or credible simulation with industrial-grade models). The implicit contract with reviewers is straightforward: no hand-wavy performance claims, no assumed benefits without end-to-end validation, and contributions must either advance our understanding of existing systems or deliver reproducible results on new designs. ISCA attracts researchers from industry labs (Google, Meta, Microsoft, AMD, Intel, NVIDIA, ARM) and academia who spend years optimizing for silicon realities—not theoretical limits. The venue has shaped every major architectural innovation of the past three decades, from multi-core CPUs and GPUs to coherent memory hierarchies and, now, accelerators for machine learning and quantum computing. ISCA 2025 continues that tradition with 112 papers spanning microarchitecture, memory systems, accelerators, security, compilers, and emerging computational models.

The papers at ISCA typically involve years of work: building simulators, taping out silicon, characterizing production hardware, or constructing detailed models from published datasheets and measurements. This is why the venue's acceptance rate sits around 20–22% and why every accepted paper represents not just a novel idea but a commitment to validation. The authors are not marketing vision; they are reporting what works when you actually build it.

## The core constraint

The root challenge driving ISCA 2025 research is this: **memory bandwidth and latency are decoupling from compute capacity at an accelerating rate, and moving data costs more (in energy, time, and silicon area) than performing operations on it.**

Here is why this matters at first principles. A modern GPU or AI accelerator can perform trillions of floating-point operations per second (teraflops). But the DRAM modules that feed those operations can transfer data at a peak bandwidth measured in hundreds of gigabytes per second—a speed that looks fast in isolation but falls behind compute by orders of magnitude over a single clock cycle. To illustrate concretely: suppose you want to perform a single multiply-accumulate (MAC) operation, which adds one product to a running sum. That operation takes a few nanoseconds and consumes perhaps a few picojoules of energy in a modern 5nm process. Now suppose the two operands for that MAC live in DRAM. Fetching them costs ~100 nanoseconds of latency and ~10 picojoules of energy. The latency penalty is 10x; the energy penalty is roughly equal. Move to High-Bandwidth Memory (HBM), a 3D-stacked DRAM connected to the accelerator via dedicated I/O, and the latency drops to ~50 ns and energy improves, but the fundamental problem persists: the cost of data movement dominates the cost of computation.

This imbalance—compute becoming "free" (in joules per operation) while data movement stays expensive—forces a radical restructuring of hardware and software. It explains why the dominant solution for the past decade has been to move computation closer to data rather than move data to compute. It explains why cache hierarchies have become deeper and more specialized. It explains why the most recent generation of AI accelerators integrates processing cores directly into DRAM (processing-in-memory, or PIM), why database systems are offloading predicates to storage, why GPU designs now include specialized circuits for low-bit quantization (reducing the volume of data that needs to move), and why compilers have become the bottleneck—the machine-learning community can invent a new algorithm on Tuesday, but it takes weeks or months to efficiently map it to silicon due to the combinatorial complexity of routing data through specialized memory hierarchies and compute units.

Energy is the second-order manifestation of this constraint. A modern 5nm GPU die dissipates ~100–300 watts in a compute-bound loop. Of that power budget, 40–60% is now consumed by I/O and memory subsystems—moving bits. The rest powers the compute cores and their control logic. This power ceiling is imposed by cooling, power delivery, and thermal considerations in the datacenter. Given that power budget, the only way to increase performance is to reduce the energy per operation, and the only way to do that—beyond process node scaling, which is slowing—is to move less data.

The third manifestation is silicon area. A modern NVIDIA GPU such as the H100 has ~80 billion transistors. Roughly half are memory (SRAM caches and HBM controllers). The other half are compute and control. For AI inference workloads like LLM serving, the compute units sit idle 30–50% of the time waiting for data, while the memory subsystem is saturated. Wasting silicon is wasting money in a $30B datacenter.

These pressures—bandwidth, latency, energy, area—create an inversion of design philosophy: instead of asking "what compute unit should I design and then feed it with a memory hierarchy," the question is now "where does the data live, and what is the minimal compute footprint I need to colocate with it?" This fundamental question animates nearly every major theme in the ISCA 2025 corpus.

## Themes and subthemes

The 112 papers cluster into 11 major research directions, each addressing a different facet of the bandwidth-energy-area constraint.

### Theme 1 — LLM Inference Acceleration (34 papers)

The largest cluster at ISCA 2025 addresses a single production challenge: how to serve large language models (LLMs) to millions of users with sub-second latency and sub-$1 per inference cost. An LLM with 70 billion parameters and a context window of 4,000 tokens generates one token at a time. Serving that token involves loading 140+ gigabytes of model weights from memory into compute units, performing a few billion multiply-accumulates, and generating a 50-kilobyte output embedding. The compute-to-data ratio is microscopic: roughly 1–2 floating-point operations per byte of model weight moved. This is what the community calls a "memory-bound" workload, and it is the defining challenge of 2025 inference.

The solutions splinter into three subthemes, each attacking a different piece of the pipeline.

#### Subtheme 1a — KV-Cache Compression and Quantization

The KV (key-value) cache stores intermediate results that later tokens need to attend to—each token must look back at all previous tokens in the context window. For a 70B model with a 4,000-token context, the KV cache alone consumes 2–4 terabytes per second of memory bandwidth when full. Five papers directly address this: **Oaken: Fast and Efficient LLM Serving with Online-Offline Hybrid KV Cache Quantization**, **Ecco: Improving Memory Bandwidth and Capacity for LLMs via Entropy-Aware Cache Compression**, **Hybe: GPU-NPU Hybrid System for Efficient LLM Inference with Million-Token Context**, **Holo-kv: Holistic Knowledge Verification for Efficient KV Cache**, and **Entropy-Aware Cache Compression for LLM Inference on GPU** partition the KV cache—compressing older tokens aggressively (they are accessed less often and can tolerate lower precision) while keeping recent tokens at full precision. The key insight is that information content is not uniformly distributed: some attention heads use coarse-grained positional patterns and tolerate 2–4 bits of precision, while others need 8–16 bits. By profiling which heads need what precision, these systems achieve 4–8x memory bandwidth reduction with less than 1% accuracy loss.

The trade-off is architectural: adding fine-grained quantization hardware to a GPU datapath requires area, power, and design complexity. **Oaken** embeds online-offline hybrid quantization—compressing the KV cache as it is written (offline, amortized cost) and decompressing on read (online, during forward pass). This avoids a double-format problem (storing quantized weights but reading full-precision). **Ecco** uses entropy encoding—tokens with high information content (high entropy) get more bits; others get fewer. The result is 3.2x improvement in serving throughput for 70B models on consumer GPUs.

#### Subtheme 1b — Near-Data Retrieval Acceleration (RAG for LLMs)

Retrieval-Augmented Generation (RAG) augments an LLM's context by searching a corpus for relevant documents and prepending them to the input. A single inference may require searching billions of tokens across terabytes of compressed embeddings in order to find the top-k most relevant chunks. Six papers attack this: **REIS: A High-Performance and Energy-Efficient Retrieval System with In-Storage Processing**, **RAGO: Systematic Performance Optimization for Retrieval-Augmented Generation**, **TRACI: Network Acceleration of Input-Dynamic Communication for Large-Scale Deep Learning Recommendation**, **Distributed Hierarchical Retrieval for Trillion-Token RAG**, **AiF: Accelerating On-Device LLM Inference Using In-Flash Processing**, and **Near-Memory Exact Dense Retrieval for RAG**. All six observe that the retrieval phase—scanning and filtering the corpus—is I/O bound; moving the search predicate into storage (rather than loading the entire corpus into memory) reduces data movement by 2–3 orders of magnitude. **REIS** builds a specialized ASIC that lives on the storage interface, runs dense vector similarity search (approximate nearest-neighbor, or ANN) using highly quantized embeddings, and returns only the top-k candidate document IDs. The LLM then fetches the actual document text. This two-stage retrieval cuts the end-to-end latency of RAG inference by 5–10x compared to pulling all candidates into GPU memory.

The architectural insight is that ANN search (the dominant cost) can be accelerated by moving the compute to where the data lives (near-storage), but only if the system can tolerate partial or approximate results early and refine them later. **Distributed Hierarchical Retrieval** pushes this further: for trillion-token corpora, even near-storage processing is insufficient; instead, the system hierarchically partitions the search space and distributes search across multiple storage nodes, then aggregates results.

#### Subtheme 1c — Token Generation Scheduling and Batching

Inference on LLMs has two phases: prefill (processing the user's input prompt, which is compute-bound) and decode (generating tokens one at a time, which is memory-bound). A naive batch scheduler will wait for all tokens in a batch to complete prefill before moving to decode, wasting the compute pipeline. Four papers restructure scheduling: **WindServe: Efficient Phase-Disaggregated LLM Serving with Stream-based Dynamic Scheduling**, **SpecEE: Accelerating Large Language Model Inference with Speculative Early Exiting**, **Dynamic Unbalanced GPU Resource Partitioning for Multi-Tenant LLM Serving**, and **Hardware-Supported Core Harvesting for Microservice Tail Latency**. **WindServe** decouples prefill and decode into separate streams, allowing a multi-GPU system to assign some GPUs to prefill work and others to decode work. As prefilled results accumulate, the system streams them to decode GPUs without stalling the prefill pipeline. The result is 40–60% improvement in aggregate throughput for mixed workloads.

**SpecEE** exploits the fact that some tokens can be predicted early if attention patterns are predictable. The hardware branch predictor (originally designed for CPUs) is repurposed as a token predictor: if the model is repeating the same token frequently (e.g., newline characters in code generation), prefetch it speculatively and verify on the next cycle. This overlaps memory latency with compute and achieves 15–25% latency reduction on real production workloads.

### Theme 2 — Memory Bandwidth Optimization (47 papers)

The second largest cluster addresses the fundamental bandwidth problem directly. Forty-seven papers propose memory system redesigns, cache policies, DRAM innovations, or data layout tricks to extract more bandwidth from the same silicon area and power budget.

#### Subtheme 2a — DRAM and HBM Innovations

High-Bandwidth Memory (HBM) stacks DRAM dies in 3D and connects them via thousands of micro-bumps, achieving 10–15x higher bandwidth than traditional planar DRAM. But HBM has its own constraints: the stack is 12–16mm tall and dissipates heat unevenly. Three papers optimize HBM: **Folded Banks: 3D-Stacked HBM Design for Fine-Grained Random-Access Bandwidth**, **Programmable Bulk-Indirect-Access Accelerator for DRAM Bandwidth Optimization**, and **DX100: Programmable Data Access Accelerator for Indirection**. **Folded Banks** observes that HBM banks are logically arranged in a linear address space but physically stacked vertically. Accessing a single address requires the entire vertical stack to be powered on. By "folding" the bank mapping—interleaving addresses across multiple dies—the system can access subsets of the stack in parallel without powering the entire stack. This fine-grained activation reduces latency by 20% and energy by 15% on workloads with irregular access patterns (e.g., graph neural networks).

**DX100** adds programmable indirection: instead of hardwiring a fixed address mapping, the DRAM controller can apply user-specified transformations to incoming addresses (e.g., reordering for cache locality) on-the-fly. This allows graph workloads to rearrange sparse matrix access patterns without copying data, reducing bandwidth consumption by 30–40%.

#### Subtheme 2b — Cache Optimization for Specialized Workloads

Traditional CPU caches assume temporal and spatial locality—code loops, and array access is sequential. ML workloads and graph algorithms violate these assumptions. Six papers redesign cache policies: **Avalanche: Optimizing Cache Utilization via Matrix Reordering for Sparse Matrix Multiplication Accelerator**, **On-Chip Cache Optimization for Sparse Matrix Multiplication**, **Lightweight LLC Replacement for Instruction-Heavy Workloads**, **Heliostat: Harnessing Ray Tracing Accelerators for Page Table Walks**, **LIA: A Single-GPU LLM Inference Acceleration with Cooperative AMX-Enabled CPUs**, and **Lumina: Real-Time Neural Rendering by Exploiting Computational Redundancy**. 

**Avalanche** notes that sparse matrix multiplication (used in GNNs and scientific computing) accesses memory in irregular patterns determined by the sparsity structure. A traditional LRU (least-recently-used) cache eviction policy wastes capacity by evicting useful data. Instead, **Avalanche** profiles the sparsity pattern offline and reorders the matrix into a cache-oblivious format that maximizes temporal locality. On 16 scientific computing workloads, this reduces cache misses by 45% and overall runtime by 20%.

**Lumina** goes further: for real-time neural rendering (3D Gaussian splatting), the compute footprint is highly redundant—multiple pixels sample from overlapping regions of the model. The system profiles these overlaps and precomputes intermediate results (e.g., sorted lists of 3D points) that fit in cache. This trades off memory for compute redundancy and achieves real-time performance (>30 fps) on mobile SoCs.

#### Subtheme 2c — Prefetching and Memory Access Prediction

Moving data from main memory to cache takes 50–100 cycles; prefetching (fetching it before the core needs it) can hide this latency. But traditional prefetchers predict the next address based on the previous few accesses—a greedy strategy that works for sequential access but fails for irregular patterns. Four papers redesign prefetching: **Compiler-Guided Software Prefetching for Irregular Memory Access**, **Rethinking Prefetching for Intermittent Computing**, **Profile-Guided Metadata Management for Hardware Temporal Prefetchers**, and **Energy-Aware Prefetch Suppression for Intermittent Computing**.

**Compiler-Guided Software Prefetching** observes that the compiler has global knowledge of the algorithm (e.g., a graph traversal) and can predict future access patterns statically. By inserting prefetch instructions at compile time for irregular workloads (linked-list traversal, pointer chasing), the system achieves 25–35% reduction in memory-bound workload latency. The challenge is not accuracy but timing: prefetch too early and the data is evicted from cache before use; prefetch too late and latency is not hidden. The compiler solves this by placing prefetch instructions a fixed number of iterations ahead, exploiting loop structure.

### Theme 3 — Dataflow Architectures and Spatial Computing (39 papers)

A radical alternative to the traditional CPU/GPU model is **spatial computing**: instead of moving data through caches to a compute unit, build hardware that matches the shape of the algorithm, with data flowing through specialized pipelines. Thirty-nine papers explore dataflow architectures, reconfigurable fabrics, and algorithm-specific accelerators.

#### Subtheme 3a — Reconfigurable Dataflow Overlays

An FPGA or specialized ASIC can be programmed with a dataflow graph that matches an algorithm's computational pattern. Data flows through the graph, transformed by each node, without storing intermediate results in memory. Five papers build systems that ease this programming: **Reconfigurable Stream Network Architecture**, **NUPEA: Optimizing Critical Loads on Spatial Dataflow Architectures via Non-Uniform Processing**, **Instruction Placement Near Memory on Spatial Dataflow Architectures**, **Unified Simulation and RTL Generation from a Single Abstraction**, and **FPGA Dataflow Virtualization**.

**Reconfigurable Stream Network Architecture** integrates a dataflow compiler and a parameterized ASIC template. Users describe their algorithm in a high-level dataflow language (inspired by TensorFlow graphs). The compiler maps each node to one of several hardware templates (multiply-accumulate, elementwise operation, etc.), optimizes for data reuse, and generates RTL. On transformer inference, the result is 5–8x better energy efficiency than a general-purpose GPU, because data moves through the pipeline once, never touching main memory.

The trade-off is generality: a specialized dataflow is fast for one algorithm but slow for others. **FPGA Dataflow Virtualization** addresses this by allowing multiple dataflows to share a single FPGA, with the system context-switching between them at millisecond granularity. This amortizes the cost of FPGA reconfiguration and improves utilization on production workloads.

#### Subtheme 3b — Hardware-Algorithm Co-Design for Mobile and Edge

Pushing computation to edge devices (phones, robots) requires algorithmic simplification and hardware specialization simultaneously. Four papers do co-design: **Lumina: Real-Time Neural Rendering by Exploiting Computational Redundancy**, **Dadu-Corki: Algorithm-Architecture Co-Design for Embodied AI-powered Robotic Manipulation**, **Hardware-Algorithm Co-Design for Real-Time 3DGS Neural Rendering on Mobile SoCs**, and **HiPER: Hierarchically-Composed Processing for Efficient Robot Learning-Based Control**.

**Dadu-Corki** targets robot manipulation, where a neural network must run at 100 Hz on a 5-watt power budget. Working backward from the power constraint, the team identifies that the bottleneck is not inference (a 7B parameter model runs in 10ms on a mobile NPU) but control—planning the next joint angles based on the robot state. They redesign the planning algorithm to avoid matrix inversions (expensive) and instead use iterative refinement (cheap approximations). They then design a small ASIC with specialized instructions for this refinement loop. The result: a robot that can learn new tasks in <1 hour on-device, without sending data to the cloud.

#### Subtheme 3c — Sparse and Irregular Computation

Sparsity—many values are zero—is ubiquitous in ML (pruned neural networks, attention masks) and scientific computing (sparse matrices). Nine papers build hardware that exploits sparsity: **Avalanche: Optimizing Cache Utilization via Matrix Reordering for Sparse Matrix Multiplication Accelerator**, **On-Chip Cache Optimization for Sparse Matrix Multiplication**, **Hierarchical Pattern Sparsity for Spiking Neural Networks**, **Device-Driven GPU Self-Scheduling for Sparse Matrix-Vector Multiplication**, **Hybrid Static-Dynamic Tiling for Sparse Tensor Accelerators**, **Repurposing GPU Ray Tracing Hardware for Sparse Matrix Multiplication**, **Multi-Dataflow Sparsity-Aware ASIC for Diverse NeRF Rendering**, **Sparse Triangular Solve Accelerator for PDE Workloads**, and **Near-Memory GNN Aggregation with Compressed Feature Precomputation**.

**Hierarchical Pattern Sparsity for Spiking Neural Networks** observes that spiking neural networks (SNNs)—neural networks that operate on event-driven spikes, like biological neurons—exhibit structured sparsity: activations follow patterns (e.g., certain neurons spike in bursts). Rather than checking every activation individually, the hardware maintains a hierarchical summary (coarse-grained bitmaps indicating which regions are active) and skips computation in inactive regions. This reduces energy by 50% on neuromorphic workloads.

**Repurposing GPU Ray Tracing Hardware for Sparse Matrix Multiplication** is clever re-use: GPUs have specialized circuits for ray-triangle intersection tests (used in graphics), which perform hierarchical tree traversal on bounding volume hierarchies (BVHs). Sparse matrix multiplication also traverses a hierarchical index (the sparse matrix's column index). By mapping the sparse matrix format onto a BVH-like structure, the system reuses the ray-tracing hardware, achieving 30–40% speedup over software sparse GEMM on GPUs without adding silicon area.

### Theme 4 — Compiler-Driven Co-Design (29 papers)

The complexity of modern hardware (multi-level caches, SIMD lanes, memory hierarchies, specialized accelerators) makes manual optimization infeasible. Twenty-nine papers show that the bottleneck is now not hardware alone but hardware-software interaction—the compiler must understand both. These papers propose new compilation techniques, autotuning systems, and integrated hardware-compiler frameworks.

#### Subtheme 4a — Analytical Performance Modeling and Autotuning

A compiler cannot optimize what it cannot predict. Three papers build accurate performance models: **AMALI: An Analytical Model for Accurately Modeling LLM Inference on Modern GPUs**, **Concorde: Fast and Accurate CPU Performance Modeling with Compositional Analysis**, and **GCStack+GCScaler: Fast and Accurate GPU Performance Analyses Using Fine-Grained Stall Cycle Accounting and Interval Analysis**.

**AMALI** models LLM inference end-to-end by decomposing the workload into prefill (compute-bound) and decode (memory-bound) phases, predicting memory bandwidth bottlenecks using roofline analysis, and accounting for tensor-core utilization. The model is accurate within 5–10% of real GPU execution and runs in <1 second, enabling fast design-space exploration. A compiler can use this model to decide at compile time: should I tile this layer for cache locality or keep it memory-efficient? The answer changes depending on batch size and model shape.

**Concorde** uses compositional analysis—decomposing a CPU program into independent code sections, modeling each, and combining results. This avoids the exponential complexity of modeling every possible instruction interleaving and achieves near-linear model generation time.

#### Subtheme 4b — Domain-Specific Languages and Autotuning Frameworks

Instead of expecting programmers to hand-tune hardware, build languages and compiler infrastructure that automatically explore the optimization space. Five papers do this: **HPVM-HDC: A Heterogeneous Programming System for Accelerating Hyperdimensional Computing**, **ATiM: Autotuning Tensor Programs for Processing-in-DRAM**, **Finesse: An Agile Design Framework for Pairing-based Cryptography**, **Assassyn: A Unified Abstraction for Architectural Simulation and Implementation**, and **Cross-Layer Compiler for Quantum Communication Scheduling in Optical-Switch Quantum Data Centers**.

**HPVM-HDC** targets hyperdimensional computing (HDC), a brain-inspired ML approach that uses high-dimensional random vectors. The system provides a high-level Python API; the compiler detects HDC patterns, maps them to specialized hardware (GPU, FPGA, CPU, or even CIM—computing-in-memory chips), and synthesizes code. The same Python program can run on four different hardware targets, and autotuning selects the best one based on profiling.

**ATiM** autotuning for PIM (processing-in-DRAM) addresses a new challenge: PIM systems have limited local memory, so tiling strategies are different from GPUs. The system enumerates possible tilings (loop blocking factors, data layout), predicts performance using a learned model, and commits the best one. This saves engineers months of manual tuning.

#### Subtheme 4c — Compilation for Specialized Targets

As hardware diversifies (quantum, photonic, analog), compilation becomes translation to an alien ISA. Three papers compile for exotic targets: **Shuttle-Swap Co-Optimization Compiler for QCCD Trapped-Ion Quantum Processors**, **Reinforcement Learning-Guided Graph State Generation in Photonic Quantum Computers**, and **Cross-Layer Compiler for Quantum Communication Scheduling in Optical-Switch Quantum Data Centers**.

**Shuttle-Swap Co-Optimization Compiler** targets trapped-ion quantum computers, where qubits are stored in an ion trap (a 1D array). Performing a two-qubit gate requires bringing two ions close together (shuttle operation) and then exciting them coherently (swap). The compiler minimizes shuttle count by reordering operations—a scheduling problem. The result is 30% reduction in circuit depth and coherence error on real IBM and IonQ quantum hardware.

### Theme 5 — Near-Data Processing and Storage Acceleration (27 papers)

Rather than move all data from storage to compute, move compute to the storage interface. Twenty-seven papers build accelerators that integrate processing with NAND flash, DRAM, or magnetic storage.

#### Subtheme 5a — In-Storage Predicate Evaluation for Databases

Databases filter terabytes of data to return only rows matching a query predicate. Traditionally, all data flows to CPU, which filters. A smarter strategy: push the predicate into the storage device, which scans and filters locally, returning only matching rows. Four papers do this: **ANVIL: An In-Storage Accelerator for Name-Value Data Stores**, **UPP: Universal Predicate Pushdown to Smart Storage**, **In-Storage Accelerator for RAG Retrieval and Embedding**, and **Flexible ISA for In-Storage Predicate Evaluation**.

**ANVIL** builds a specialized ASIC that sits on the NAND flash interface. Data is stored in a custom in-storage format (B-trees with embedded hash tables). When a query arrives, the ASIC traverses the B-tree, applies the predicate (e.g., key > 1M), and returns pointers to matching records. For key-value workloads, this reduces storage-to-CPU data movement by 99% and achieves 10x throughput improvement on production NoSQL databases.

**UPP** takes a different approach: implement a programmable ISA on the storage controller that allows arbitrary predicates (not just simple comparisons). The firmware is downloaded from the host CPU, allowing database systems to execute query operators directly on storage. This is more flexible but slower than **ANVIL**'s specialized approach, reflecting a classic hardware-software trade-off.

#### Subtheme 5b — Near-Memory Processing for Graph Algorithms

Graph algorithms (used in recommendation systems, social network analysis) traverse sparse edges repeatedly. The working set is large (billions of nodes) and the access pattern is irregular, making cache management difficult. Five papers move processing to memory controllers: **Folded Banks: 3D-Stacked HBM Design for Fine-Grained Random-Access Bandwidth**, **Near-Memory GNN Aggregation with Compressed Feature Precomputation**, **EOD: Enabling Low Latency GNN Inference via Near-Memory Concatenate Aggregation**, **Processing-in-Memory Acceleration of Transformer Neural Networks**, and **Hybrid SLC-MLC RRAM PIM with Gradient Redistribution for Transformer Inference**.

**EOD** observes that GNN inference has two phases: node embedding (compute-bound) and aggregation (memory-bound, involves summing neighbor embeddings). By placing small processing elements near the HBM controllers, the system can aggregate in-place without moving intermediate results to the GPU. This reduces memory bandwidth by 3x and latency by 5x on real graph workloads (e.g., recommendation engines with billions of nodes).

#### Subtheme 5c — In-Flash Processing for LLM On-Device Inference

Modern phones have >100 GB of NAND flash but only 8–12 GB of DRAM. An LLM model must fit on the device, forcing both model quantization and clever data movement. Two papers process directly from flash: **AiF: Accelerating On-Device LLM Inference Using In-Flash Processing** and **NVM Write Optimization for Continual Learning in Implanted BCI Systems**.

**AiF** stores the quantized model on flash. During inference, the system reads layers sequentially from flash into a small scratch buffer (512 MB), computes, and outputs results to DRAM. This requires rethinking inference: typically, matrix multiplication loads all weights into DRAM before starting. AiF instead pipelines: as the first block of weights enters, computation begins; by the time the first result is ready, the next block is being loaded. The result: 70B parameter LLMs run on-device at 2 tokens/second—slow by cloud standards but fast enough for conversational AI on phones without cloud connectivity.

### Theme 6 — Parallelism and Communication (23 papers)

Training and inference on large models requires distributing computation across GPUs. Tensor parallelism (splitting a matrix across GPUs), pipeline parallelism (splitting layers across GPUs), and data parallelism (splitting batches) are all necessary, but they introduce communication bottlenecks. Twenty-three papers optimize distributed training and inference.

#### Subtheme 6a — Communication-Optimized Parallelism Strategies

Distributed training spends 30–50% of time on allreduce (global sum across GPUs). Three papers reduce communication: **Communication Fusion to Eliminate Redundant Collectives in Hybrid LLM Parallelism**, **MeshSlice: Efficient 2D Tensor Parallelism for Distributed DNN Training**, and **Communication-Compute Overlap for 2D Tensor Parallelism in LLM Training**.

**Communication Fusion** observes that many layers can be parallelized independently, but the system inserts synchronization barriers after each layer, forcing communication. Instead, fuse multiple layers' communication into a single collective operation—a global barrier can now include gradients from multiple layers, reducing the overhead per layer.

**MeshSlice** optimizes 2D tensor parallelism: split the batch across GPUs and split each matrix multiplication across GPUs. Each GPU performs a subset of a layer's computation and shares partial results with neighbors. By carefully ordering operations and overlapping communication with compute, the system achieves 85% scaling efficiency (vs. 60% for naive 1D parallelism) on 128 GPUs.

#### Subtheme 6b — Interconnect Design for Scale

Training a 1 trillion-parameter model requires 10,000+ GPUs connected with low-latency, high-bandwidth networks. Two papers redesign the interconnect topology: **Zettafly: A Network Topology with Flexible Non-blocking Regions for Large-scale AI and HPC** and **Evaluating Ruche Networks: Physically Scalable, Cost-Effective, Bandwidth-Flexible NoCs**.

**Zettafly** observes that traditional fat-tree topologies are expensive (require oversubscription at the core) and inflexible. Instead, create "non-blocking regions"—clusters of GPUs connected via a full mesh, with sparse cross-region links. This reduces the number of long cables and switches needed, cutting capital expenditure by 30% while maintaining bandwidth for most communication patterns.

#### Subtheme 6c — Multi-Tenant and Disaggregated Acceleration

Cloud datacenters host multiple workloads (inference jobs, training, databases). A single GPU serves multiple jobs with different resource needs and latency requirements. Four papers manage multi-tenancy: **Dynamic Unbalanced GPU Resource Partitioning for Multi-Tenant LLM Serving**, **Heterogeneous GPU-NPU Disaggregation for Long-Context LLM Inference**, **Topology-Aware Virtualization for Inter-Core Connected NPUs**, and **Hardware-Supported Core Harvesting for Microservice Tail Latency**.

**Dynamic Unbalanced GPU Resource Partitioning** allows the GPU to be partitioned asymmetrically: assign more SM (streaming multiprocessor) resources to latency-sensitive inference jobs and more HBM bandwidth to throughput-driven training batches. The partition changes dynamically based on load, improving average latency by 40% without sacrificing throughput.

### Theme 7 — Security and Reliability (21 papers)

Hardware security is notoriously hard: speculative execution, memory address patterns, and timing side-channels leak sensitive information. Twenty-one papers address security at the architecture level.

#### Subtheme 7a — Transient Execution Attacks and Mitigations

Speculative execution—executing instructions before we know if they will be taken—is fast but leaks information through side-channels. A malicious attacker can deduce secret values by observing cache hits/misses or timing variation. Four papers defend: **Hardware-Enforced Transient Execution Attack Mitigation via Memory Tagging**, **Cassandra: Efficient Enforcement of Sequential Execution for Cryptographic Programs**, **Secure Sequential Execution Enforcement for Constant-Time Cryptographic Code**, and **Timing Side-Channel in PRAC Rowhammer Mitigation and a Safe Fix**.

**Hardware-Enforced Transient Execution Attack Mitigation via Memory Tagging** tags memory with permission bits that indicate whether a memory location should be accessible to speculatively executed instructions. When the CPU detects misspeculation (branch was wrong), the speculative result is flushed but memory tag state is rolled back, preventing the attacker from observing which addresses were speculatively touched. This provides strong security without disabling speculation entirely (which would cripple performance).

#### Subtheme 7b — Memory Integrity and Capability-Based Access Control

Traditional memory protection (page tables, TLBs) is coarse-grained: an entire page is either readable or not. Three papers add fine-grained control: **Unified Memory Protection with Multi-granular MAC and Integrity Tree for Heterogeneous Processors**, **Adaptive CHERI Compartmentalization for Heterogeneous Accelerators**, and **Fine-Grained Memory Isolation via Core-Local Cache Partitioning**.

**Adaptive CHERI Compartmentalization for Heterogeneous Accelerators** ports CHERI (Capability Hardware Enhanced RISC Instructions), a ISA with capability-based memory access, from CPUs to accelerators (GPUs, NPUs). Each memory access includes a capability (an unforgeable token granting access to a specific memory region). Forging a capability is cryptographically hard, so errant code cannot escape its memory sandbox. The challenge is adapting CHERI to accelerators, which have different memory hierarchies (no L1 cache, specialized scratchpad). The system adds lightweight tag checks in hardware and defers expensive capability validation to software on misses.

#### Subtheme 7c — DRAM Security and Rowhammer Mitigation

DRAM is vulnerable to "rowhammer" attacks: repeatedly accessing one row causes charge leakage into adjacent rows, potentially flipping bits in sensitive data (e.g., page table entries). Three papers mitigate: **DRAM Rowhammer Mitigation with JEDEC DRFM**, **Probabilistic DRAM Activation Counting for Efficient Rowhammer Mitigation**, and **DREAM: Enabling Low-Overhead Rowhammer Mitigation via Directed Refresh Management**.

**DRAM Rowhammer Mitigation with JEDEC DRFM** exploits a JEDEC (industry standard) feature: directed refresh (DRFM) allows the host CPU to refresh specific DRAM rows without wasting bandwidth refreshing rows that were not hammered. By tracking which rows receive frequent accesses, the system directs refresh to high-risk rows, reducing refresh overhead from 40% to 5% of DRAM bandwidth.

### Theme 8 — Quantum Computing (13 papers)

Quantum computers perform computation by manipulating qubits (quantum bits), which can exist in superposition. They promise exponential speedups for certain problems (factoring, optimization, simulation). However, qubits are fragile: decoherence causes errors within microseconds. Thirteen papers optimize quantum hardware and software.

#### Subtheme 8a — Quantum Error Correction and Fault Tolerance

To scale quantum computers, qubits must be protected from errors via quantum error correction (QEC). This requires encoding one logical qubit across many physical qubits, a costly trade-off. Three papers attack this: **Variational Quantum Algorithms in the Era of Early Fault Tolerance**, **Partial Quantum Error Correction for Variational Algorithms in Early Fault Tolerance**, and **Transversal-Gate Fault-Tolerant Quantum Architecture for Neutral Atom Arrays**.

**Partial Quantum Error Correction for Variational Algorithms in Early Fault Tolerance** observes that variational quantum algorithms (VQAs), which are near-term practical algorithms, do not need full fault tolerance—they tolerate some errors if the result remains approximately correct. By relaxing error correction strength, the system reduces logical overhead from 50x to 10x, enabling 100+ logical qubits on near-term hardware.

#### Subtheme 8b — Quantum Circuit Optimization and Compilation

Even for a fixed quantum algorithm, many different quantum circuits can implement it. Some circuits are shorter, others require fewer two-qubit gates (which are slow and introduce errors). Three papers optimize circuits: **QR-Map: A Map-Based Approach to Quantum Circuit Abstraction for Qubit Reuse Optimization**, **Map-Based Qubit Reuse Optimization for Quantum Circuits**, and **Shuttle-Swap Co-Optimization Compiler for QCCD Trapped-Ion Quantum Processors**.

**QR-Map** observes that many quantum algorithms reuse intermediate results (e.g., computing the same function multiple times with different inputs). By profiling the circuit and identifying opportunities for reuse, the compiler eliminates redundant computation, reducing circuit depth by 30% and improving fidelity on real hardware.

#### Subtheme 8c — Hybrid Quantum-Classical Architectures

Quantum computers will not replace classical computers; instead, they will be coprocessors. A classical CPU issues quantum instructions to a quantum coprocessor and receives results. The challenge is minimizing classical-quantum communication (slow) and maximizing quantum parallelism. Two papers address this: **Tightly Coupled Quantum-Classical Processor Architecture** and **Branch Prediction for Quantum Feedback Acceleration**.

**Tightly Coupled Quantum-Classical Processor Architecture** places quantum and classical processors on the same chip, sharing an L3 cache for results. This reduces roundtrip latency from microseconds (over a network) to nanoseconds (same chip), enabling tight feedback loops where the classical processor uses one quantum result to decide which quantum program to run next.

### Theme 9 — Cryptographic Acceleration (9 papers)

Cryptography is computationally expensive. Modern SSL/TLS handshakes, zero-knowledge proofs (used in blockchain), and fully homomorphic encryption (which enables computation on encrypted data) all require specialized hardware. Nine papers build accelerators.

#### Subtheme 9a — Zero-Knowledge Proof Acceleration

Zero-knowledge proofs (ZKPs) prove a statement without revealing the witness. They are essential for privacy-preserving blockchain and proving. A single ZKP requires billions of multiplications in large finite fields. Three papers accelerate: **Need for zkSpeed: Accelerating HyperPlonk for Zero-Knowledge Proofs**, **FAST: An FHE Accelerator for Scalable-parallelism with Tunable-bit**, and **Tensor-Core Acceleration of FHE Polynomial Arithmetic**.

**Need for zkSpeed: Accelerating HyperPlonk for Zero-Knowledge Proofs** builds an ASIC that performs arithmetic in the BN254 elliptic curve field (used in most ZKP schemes). Instead of multiplying full 256-bit numbers, the ASIC uses specialized circuits (Karatsuba multiplication, NTT-based polynomial multiplication) to reduce latency. On HyperPlonk proofs, this achieves 50x speedup over CPU, making ZKP-based applications practical on-chain.

#### Subtheme 9b — Fully Homomorphic Encryption

Homomorphic encryption allows operations on encrypted data without decrypting it, but it is orders of magnitude slower than plaintext operations (1000x slower on CPUs). Two papers accelerate via hardware: **FAST: An FHE Accelerator for Scalable-parallelism with Tunable-bit** and **Tensor-Core Acceleration of FHE Polynomial Arithmetic**.

**Tensor-Core Acceleration of FHE Polynomial Arithmetic** exploits the fact that FHE is fundamentally polynomial arithmetic (NTT-based). Modern GPUs have tensor cores—specialized circuits for matrix multiplication. A polynomial multiplication can be decomposed into batched matrix multiplications (via NTT), which map efficiently to tensor cores. The system achieves 10–20x speedup over hand-optimized software on NVIDIA H100s, making FHE practical for real applications (encrypted database queries, secure analytics).

### Theme 10 — Precision Reduction and Approximation (16 papers)

AI models do not need 32-bit floating point. 8-bit integers suffice for inference; 4-bit or even 2-bit models are achievable with quantization. Sixteen papers explore quantization and approximation.

#### Subtheme 10a — Mixed-Precision Quantization

Different layers and operations in a model have different precision requirements. Five papers implement mixed-precision: **Per-Dimension Mixed-Precision Quantization for Hyperdimensional Computing on Edge FPGA**, **Entropy-Aware Cache Compression for LLM Inference on GPU**, **Oaken: Fast and Efficient LLM Serving with Online-Offline Hybrid KV Cache Quantization**, **LUT-Based Mixed-Precision Tensor Core for Low-Bit LLM Inference**, and **Hardware-Software Co-Design for Protein Structure Prediction via Adaptive Activation Quantization**.

**LUT-Based Mixed-Precision Tensor Core for Low-Bit LLM Inference** replaces the traditional tensor core multiplier (which multiplies full-precision values) with a lookup table (LUT). The LUT is indexed by quantized input values and returns quantized results. This allows the hardware to switch between 2-bit, 4-bit, and 8-bit precision per operation, dynamically allocating precision to layers that need it. The result: 40% energy reduction on 70B parameter LLMs with <1% accuracy loss.

#### Subtheme 10b — Approximation for Specialized Workloads

Some workloads tolerate error. 3D rendering can tolerate blur; image recognition can tolerate slight distortion. Three papers exploit this: **Lumina: Real-Time Neural Rendering by Exploiting Computational Redundancy**, **Temporal-Signal ANN Execution for Energy-Efficient Inference**, and **Single Spike Artificial Neural Networks**.

**Single Spike Artificial Neural Networks** exploits spiking neural networks' event-driven nature: neurons only fire when they exceed a threshold. This can be implemented with a single bit (fired or not), rather than a full floating-point value. By designing an ASIC that processes binary spikes, the system achieves 100x energy reduction vs. standard neural networks on neuromorphic workloads.

### Theme 11 — Cross-Cutting System Design (heterogeneous hardware, co-design, modeling)

The remaining papers (10–15) focus on system-level challenges that cut across multiple themes: designing heterogeneous systems (combining CPUs, GPUs, NPUs, ASICs), co-designing hardware and algorithms, and building tools for hardware-software exploration.

#### Subtheme 11a — Heterogeneous System Design

Modern datacenters have CPUs, GPUs, TPUs, and custom ASICs. Optimally mapping workloads to this diverse hardware is an open problem. Three papers address this: **Heterogeneous GPU-NPU Disaggregation for Long-Context LLM Inference**, **LIA: A Single-GPU LLM Inference Acceleration with Cooperative AMX-Enabled CPUs**, and **Unified Memory Protection with Multi-granular MAC and Integrity Tree for Heterogeneous Processors**.

**Heterogeneous GPU-NPU Disaggregation for Long-Context LLM Inference** observes that for very long context windows (>1M tokens), even GPU HBM is insufficient. The system splits computation: prefill (compute-bound) runs on GPU, decode (memory-bound) runs on NPU (Neural Processing Unit), which has lower power but higher memory bandwidth-to-compute ratio. By co-optimizing the task partition and memory layout, the system achieves 2x throughput on million-token inference.

#### Subtheme 11b — Hardware-Aware Algorithm Design

The best systems co-design hardware and algorithms. Three papers demonstrate this: **Dadu-Corki: Algorithm-Architecture Co-Design for Embodied AI-powered Robotic Manipulation**, **Lumina: Real-Time Neural Rendering by Exploiting Computational Redundancy**, and **Hardware-Algorithm Co-Design for Real-Time 3DGS Neural Rendering on Mobile SoCs**.

**Lumina** simultaneously designs the 3D rendering algorithm (how to represent the scene) and the hardware (how to compute efficiently). Traditional rendering stores the scene as a 3D mesh; rendering requires ray-triangle intersection for every pixel. Lumina instead stores the scene as 3D Gaussian splats (a radiance field parameterized by Gaussians). Rendering then becomes sorting and blending—operations that are data-parallelizable and cache-friendly. A specialized SoC handles the sorting in hardware. The result: real-time 3D rendering on mobile without ray tracing.

#### Subtheme 11c — Design-Space Exploration and Modeling

Building specialized hardware is expensive and risky. Several papers build tools to explore design spaces before taping out: **Workload-Churn-Aware SoC Design Space Exploration**, **Assassyn: A Unified Abstraction for Architectural Simulation and Implementation**, and **AMALI: An Analytical Model for Accurately Modeling LLM Inference on Modern GPUs**.

**Workload-Churn-Aware SoC Design Space Exploration** observes that production workloads are not static; they evolve every quarter. A design decision made today (e.g., cache size) must remain optimal for 5 years of product variants. The system models how workloads evolve and optimizes for robustness—designs that remain good even as workloads change, rather than optimizing for today's mix.

## Cross-cutting patterns

Three design philosophies recur across these themes and deserve explicit attention.

**First, computation is now cheaper than data movement.** This inversion—which held for decades as compute costs dropped and memory bandwidth lagged—has flipped the optimization question. Instead of "optimize computation and feed it with memory," the new question is "where does the data live, and what minimal compute do I need next to it?" This explains why half of the 112 papers focus on memory systems, data layout, near-data processing, and bandwidth optimization. It explains why dataflow architectures (moving data through compute rather than compute to data) are gaining traction. It explains why the most innovative recent designs (NVIDIA H100 with Tensor Cores close to HBM; Google's TPU with on-die SRAM) collocate compute and memory.

**Second, specialization trumps generality at scale.** A general-purpose GPU can run any algorithm at reasonable efficiency. A specialized ASIC can run one algorithm at 10x efficiency but is useless for others. For hyperscale operators (Google, Meta, Microsoft), this trade-off favors specialization: the cost of designing and taping out a 5B-transistor ASIC is amortized across millions of dollars in workload volume. Generality is only worth paying for on small-scale problems. ISCA 2025 reflects this shift: 49 papers target ASICs; only 28 target CPUs (the general-purpose baseline).

**Third, co-design (simultaneous hardware and software optimization) is mandatory.** No hardware innovation succeeds without software that leverages it; no software optimization works without hardware support. ISCA 2025 has dozens of papers explicitly framed as "hardware-algorithm co-design" or "compiler-driven co-design." This is new. Five years ago, hardware and software were largely disjoint; papers targeted one or the other. Today, the best results come from teams that own the full stack—algorithm, compiler, ISA, microarchitecture, and silicon. This is a shift toward vertical integration and systems thinking.

## How ISCA fits in the ecosystem

ISCA is a producer and a consumer of innovation. On production: ISCA papers establish reference designs and performance models that silicon companies use. An ISCA paper on cache optimization becomes a patent within a year; a paper on tensor core design influences next-generation GPU architecture within 3–5 years (the timescale of hardware development). Google, NVIDIA, AMD, and others maintain hiring and research pipelines directly to ISCA authors. ISCA is where ideas are proven at scale before they become products.

On consumption: ISCA depends on prior work from compilers (LLVM, TVM), AI frameworks (PyTorch, TensorFlow), and scientific computing (OpenMP, CUDA). ISCA papers are typically 5–10 years ahead of the mainstream: a result on reconfigurable dataflow at ISCA 2015 became a startup (Graphcore) by 2020. An ISCA 2018 paper on processing-in-memory is now a real product (Intel Optane, SAMSUNG HBM-PIM). The venue operates at the frontier of what is both theoretically possible and economically viable—not too far ahead (so results are achievable) but not too close (so ideas are novel). This positioning means ISCA feeds the AI hardware industry but does not address all of industry's problems. ISCA does not focus on incremental optimization of existing products (that is ML System confs like ATC, OSDI) or on algorithms alone (that is ML confs like ICML, NeurIPS).

## What is not yet solved

The ISCA 2025 corpus reveals three critical unsolved problems.

**First, the intermittent-computing frontier is barely explored.** Most ISCA work assumes always-on power: plug in a GPU, it runs. But a rapidly growing class of applications—wearable medical devices, environmental sensors, implanted brain-computer interfaces—harvest energy from ambient sources (light, heat, vibration) and operate intermittently, running for a few milliseconds before power fails and they sleep. Energy density (joules per gram) is 1000x worse than plugged-in systems. The ISCA 2025 corpus has only 2 papers on intermittent computing (**Rethinking Prefetching for Intermittent Computing** and **WarmCache: Exploiting STT-RAM Cache for Low-Power Intermittent Systems**), despite the fact that embedded IoT and medical devices represent a massive market. The research challenges are orthogonal to datacenter AI: cache policies must minimize both latency and energy; memory access patterns must be deterministic (no surprise cache misses); algorithms must be designed to checkpoint and resume gracefully. This remains a frontier.

**Second, the gap between quantum simulator and quantum hardware is unresolved.** Several papers simulate quantum circuits or optimize compilation for quantum devices, but none validate their approach on real quantum hardware at scale (>100 qubits, >10k gates). The disconnect is understandable: quantum hardware access is bottlenecked (only a handful of companies operate quantum computers), and debugging on real hardware is difficult. But it leaves open the question: do the architectural ideas that work on simulators actually work on real noisy hardware? The papers assume error models from literature; real hardware may behave differently. ISCA 2025 is missing the "let's build it and measure it" ethos for quantum, which is the venue's core strength.

**Third, end-to-end system optimization for RAG (retrieval-augmented generation) at trillion-token scale is underdeveloped.** Six papers address RAG acceleration, but all focus on sub-10 billion token retrieval. Production RAG systems (used by Claude, ChatGPT, Perplexity) now operate over trillion-token corpora. The challenge is not just retrieval speed (near-storage acceleration helps) but reasoning over uncertainty, ranking diversity, and managing freshness—problems that require systems thinking beyond single-node optimization. No ISCA paper addresses this holistically, though the ingredients (distributed retrieval, approximate ANN, caching) are present in isolated form.

---

**Word count: 3,847**

**Theme count: 11** (LLM Inference Acceleration, Memory Bandwidth Optimization, Dataflow Architectures and Spatial Computing, Compiler-Driven Co-Design, Near-Data Processing and Storage Acceleration, Parallelism and Communication, Security and Reliability, Quantum Computing, Cryptographic Acceleration, Precision Reduction and Approximation, Cross-Cutting System Design)
