# ASPLOS 2025 — The Big Picture

## What ASPLOS is

ASPLOS (Architectural Support for Programming Languages and Operating Systems) is the conference where hardware engineers and systems software engineers come together to solve the same problem from both sides. It exists because good hardware is useless if nobody can actually program it—and software abstractions break down if they ignore what hardware really does.

Unlike pure hardware conferences (like ISCA) or pure software conferences (like PLDI), ASPLOS sits in the gap. It asks: When you build a new processor, memory hierarchy, interconnect, or security mechanism, what does the OS need to do? What does the compiler need to know? What abstraction lets programmers get performance without writing assembly? The papers here don't just design hardware, and don't just write software—they design the contract between them.

This is where real systems get built. A new cache replacement policy without an OS implementation that exploits it is just a bench curiosity. A compiler optimization that ignores the memory subsystem will leave performance on the table. ASPLOS demands both halves.

## The one problem this community is organized around

At the core is a fundamental constraint: the speed of light and the width of a bus have not changed, but the things we want to compute have exploded in complexity and scale.

Here's the concrete mechanics. Inside a modern computer, data moves physically. A CPU instruction needs data from memory. That data travels through caches, then through interconnects, then across the memory bus, then from DRAM cells. Each step takes time. The further away the data lives, the longer you wait. Meanwhile, you have to fill up pipelines, keep cores busy, and do this for billions of requests in a datacenter.

The problem manifests as a widening gap: compute got fast (instruction-level parallelism, out-of-order execution, vector units, specialized accelerators like GPUs). Memory got wider (multi-level caches, prefetching, higher bandwidth). But the gap between compute speed and memory latency keeps growing. Data movement—just moving bits around—increasingly dominates both energy and time.

ASPLOS people attack this gap from both sides. Hardware designers add routers, caches, prefetchers, and dedicated compute-near-data units (like PIM, CIM) to move data less. Compilers figure out what data to move when and reorder computation to hide latency. Operating systems manage virtual memory, placement, and sharing to make sure data lives close to where it's used. Runtime schedulers decide which task runs on which piece of hardware given contention. Security researchers figure out how to keep data private while all this movement happens.

The stakes are real. In a warehouse datacenter, saving one byte of data movement per query saves megawatts of power. In a phone, it's seconds of battery life. In AI inference, which is now eating datacenters, it's the difference between a model you can serve profitably and one you cannot.

## The main approaches in 2025

### Scheduling: Assigning Work to Hardware

With CPUs, GPUs, specialized memory (PIM), and network processors coexisting, the question becomes: which kernel runs where, and when? The 81 scheduling papers in this year's crop show this is the dominant approach.

Static scheduling—deciding at compile time—works only if you know the input at compile time. But LLM batches change size at runtime. Quantum error correction success rates are probabilistic. So the real papers here do dynamic scheduling: profile the workload at runtime, measure what's slow, and move work. *vAttention* uses OS demand paging (the OS's own mechanism for allocating memory on demand) to give LLM attention kernels a contiguous virtual address space for their KV cache, so standard attention implementations work without custom memory management. *PAPI* watches LLM decoding and decides frame-by-frame whether to route matrix-vector products to PIM units (which are embedded in memory and fast for memory-bound ops) or to the GPU (which is fast for compute). *RESCQ* dynamically redistributes resources in quantum error correction systems when state preparation fails, minimizing wasted cycles.

The pattern: measure, predict, reassign. This is where machine learning is making its way in—learning models that predict which hardware will be fastest given the kernel and the current system state.

### Memory Systems: Data Placement and Movement

60 papers target memory. The reason is simple: it's the bottleneck. Caches were invented to move data closer to compute. But caches have limits—they're small and require coherence overhead. So the new frontier is: how do we make memory both large and fast?

The main threads are tiering (fast tier + slow tier, move data between them based on access patterns), compression (fewer bytes to move), and near-data compute (move computation to memory instead). *PAPI* embeds compute inside DRAM—a PIM (processing-in-memory) unit that executes small kernels right where the data lives. *vAttention* leverages the OS's existing virtual memory system to manage KV cache memory without fragmentation. Dozens of papers optimize CXL (Compute Express Link)—a standard that lets you disaggregate memory: compute nodes connect to memory pools over high-speed interconnect, letting you decouple memory capacity from compute density.

Compression is subtle: high-throughput lossless compression of floating-point data reduces bytes on the wire, but compression/decompression itself takes compute and introduces latency. The winning papers characterize the trade-off precisely for their target hardware.

### Compilers and Code Synthesis: Making Hardware Programmable

49 papers target compilation. The reason is that hardware is constantly changing—new ISAs, new instructions, new execution models. Manually writing code for each is unsustainable.

*Velosiraptor* synthesizes OS memory translation code from formal hardware specifications: instead of manually writing a new OS driver when you add a new memory translation mechanism to your CPU, you write a formal model of the hardware and let synthesis generate the code automatically. *SmoothE* reformulates the compiler's e-graph extraction problem (choosing the best sequence of optimizations from a giant search space) as a differentiable continuous optimization, enabling gradient-based search and learned cost models. *Exo 2* lets programmers write scheduling libraries that extend the compiler without modifying the compiler internals, so when you build a new accelerator, you can define your own scheduling primitives instead of waiting for a compiler update.

The unifying theme: abstract the hardware design into a machine-readable model (formal spec, e-graph, scheduling primitives), then generate or optimize the code against it.

### Parallelism: Exploiting Task and Operator Structure

40 papers directly address parallelism—how to use multiple cores, GPUs, specialized units to do more work at once. The challenge is that not all parallelism is obvious. Some tasks have long dependency chains. Attention has quadratic complexity and doesn't map cleanly to a single hardware unit. Transformers have layers, within layers are matrix operations, within those are fine-grained operations.

Papers here orchestrate parallelism across multiple levels: intra-node (threading), inter-node (distributed), and heterogeneous (CPU+GPU+PIM+SmartNIC). The key insight is that the optimal parallelism strategy depends on the operator, the data size, and current system load, so runtime adaptation beats static choices.

### Security: Isolation at Every Layer

34 papers address security—a major ASPLOS theme. The reason is that hardware and OS are the foundation of isolation. If you can break isolation in hardware (e.g., via speculative execution side channels), all software security is compromised.

The papers split into two camps. First: defending against known attacks. Spectre, Rowhammer, side-channel attacks via cache and memory contention—the papers measure these precisely, formalize the threat, and design countermeasures (randomization, special cache replacement, side-channel-free memory controllers). Second: verifying that new hardware is actually secure. Formal verification of speculative execution, formal proofs of coherence protocols (especially for CXL), verified compiler defenses—the assumption is: if it's not formally proven secure, it's not secure.

### Virtualization and Resource Management: Sharing Hardware

21 papers focus on virtualization and container/cloud resource management. The problem: in a cloud, hundreds of tenants share the same physical hardware. Isolation must be bulletproof (security threat), and performance must be predictable (business requirement).

The papers optimize container placement, dynamic memory allocation for serverless functions, and zero-copy address translation for rapid process cloning. A key trend: CXL-enabled architectures that let you dynamically reassign memory and compute resources at fine granularity, so workloads don't waste hardware when demand is uneven.

## How it connects to the broader field

ASPLOS is the consumer of research from other venues and the producer of primitives that others build on.

From below: ASPLOS depends on microarchitecture research (MICRO) for detailed CPU pipeline behavior, on circuit design (ISCA, DAC) for physical feasibility, and on formal methods (PLDI, CAV) for verification tools. A compiler optimization in an ASPLOS paper uses formal methods invented elsewhere; a new PIM architecture relies on circuit techniques from DAC.

To the side: ASPLOS coordinates with compilers conferences (PLDI, CGO) and programming languages (POPL, OOPSLA). PLDI people invent new IR representations; ASPLOS papers use them to build better schedulers. POPL people prove theorems about language semantics; ASPLOS people verify those properties against actual hardware.

To above: ASPLOS produces the abstractions that application developers and ML systems use. A paper on dynamic KV cache memory management becomes a primitive in LLM serving frameworks. A compiler optimization becomes a backend pass. A new scheduling mechanism becomes a tuning knob in a resource manager.

ASPLOS deliberately does not answer: "How do I write a good machine learning model?" That's on ML conferences. "How do I design a good algorithm?" That's SODA, STOC, FOCS. ASPLOS answers: "Given this algorithm and this hardware, how do I make it fast, efficient, and secure?"

## What's open

The gap between the pace of hardware change and the pace of abstraction development is still wide. Quantum computing, analog accelerators, and photonic processors are emerging, but the ASPLOS community's abstractions for these are nascent. Formal verification is expensive and scales poorly—today's proofs of security or correctness are often for small toy models, not production hardware. The boundary between hardware and software keeps blurring (increasingly with ML-based decisions), but we don't yet have principled ways to verify end-to-end co-designed systems. And the proliferation of specialized hardware (accelerators for every workload, from quantum to zero-knowledge proofs) is starting to overwhelm the compilation and scheduling machinery—there may be a hard limit to how many hardware targets one compiler can efficiently target.
