# Hot Chips 2025: The Architecture of AI at Scale

## What Hot Chips is

Hot Chips is the venue where semiconductor companies announce chips they have already built or are building right now. NVIDIA, AMD, Intel, Apple, Google, Meta, and emerging players present silicon heading into data centers, devices, and edge systems within the next 12-18 months. It is not a forum for research ideas—it is a progress report on shipping silicon.

The community Hot Chips serves is product engineers: architects, design leads, and technical program managers who need to know what competitors are building, what manufacturing constraints they just solved, and what design patterns are working in practice. Industry presents here because Hot Chips reaches both peer engineers (who set the technical bar) and investors (who fund the next generation).

Unlike academic venues, Hot Chips answers one concrete question: Given the laws of physics, current manufacturing capabilities, and what we learned from the last generation, what can we actually build and deploy in the next 18 months? The answer is always constrained—by power walls, memory bottlenecks, yield limits, and supply-chain dependencies. Hot Chips is where you see how companies are carving that constraint space.

## The one problem this community is organized around

Modern AI requires moving enormous quantities of data: transformer models must load billions of parameters from memory, read input tokens, compute attention across them, and write outputs. A single large language model inference query might touch 50 gigabytes of weights. Training is worse—it can consume terabytes per day across a cluster.

The physical constraint is this: electrical wires and circuit paths have finite bandwidth. A modern data center interconnect moves roughly 800 gigabits per second between servers. A single GPU's memory interface might sustain 2-5 terabits per second—roughly 1000x the network link. But moving 50 gigabytes of weights into 8 trillion operations takes time: even at peak bandwidth, it is 10+ milliseconds just to load the model once.

Worse, the energy cost of moving data is orders of magnitude higher than computing with it. Moving one bit across a modern chip costs roughly 10 picojoules; doing one floating-point operation costs roughly 1 picojoule. So if your model is compute-bound, energy efficiency depends on reusing data as much as possible. If your model is data-bound, you waste power moving the same weights repeatedly through increasingly distant memory hierarchies.

Hot Chips is organized around solving two coupled problems: (1) getting data to compute faster and cheaper, and (2) specializing circuits so they do more useful work per joule. This is not unique to AI, but AI made it urgent. Training LLMs burns megawatts; inference at scale requires room-sized cooling systems. Every watt matters.

The third, often-unstated problem is latency. A cloud API call that takes 500ms instead of 100ms loses customers. A mobile voice assistant with 2-second delay feels broken. A real-time video codec must encode in microseconds. Datacenter interconnects with 100ns latency instead of 50ns cascade through entire clusters. Hot Chips includes designs optimizing for all three: throughput (terabits per second, petaFLOPS), energy (FLOPS per joule), and latency (nanoseconds, milliseconds depending on workload).

## The main approaches in 2025

### Heterogeneous memory systems and bandwidth multiplication

The traditional approach was to build a single deep memory hierarchy: fast on-chip SRAM, slower DRAM, even slower storage. This works for algorithms with predictable access patterns (like matrix multiply). Modern models don't. Attention mechanisms require sparse, irregular lookups into hundreds of megabytes of activation buffers.

Hot Chips 2025 sees a shift: instead of hierarchy, use spatial diversity. Place specialized memory closer to compute. NVIDIA's consumer GPUs now integrate HBM (high-bandwidth memory) directly on-package, running at petabits per second. Google's custom accelerators (revealed in prior years, now in production) separate model weights (stored in DRAM, fetched infrequently) from activations (stored on-chip SRAM, fed to tensor cores at full rate). Some designs add compute-in-memory: AMD and emerging startups now present analog in-memory accelerators that move computation directly into memory substrates, eliminating the cost of data movement for specific operations like Boolean satisfiability or polynomial arithmetic.

Papers here: "KLIMA: Low-latency mixed-signal In-Memory Computing accelerator for solving arbitrary-order Boolean Satisfiability", "Bit-Separable Transformer Accelerator Leveraging Output Activation Sparsity for Efficient DRAM Access". These designs admit they cannot hide all memory latency, so they exploit workload sparsity—if 80% of activations are zero, move only 20% of data.

### Optical and photonic interconnects replacing electrical traces

Single-socket designs hit power and thermal limits around 700W. Larger models need multiple sockets. Each electrical interconnect between sockets carries a few terabits per second and burns watts doing it. The alternative is photonics: route signals as light instead of electricity.

Several teams now present silicon photonics integrated on-die. Wavelength-division multiplexing (packing multiple independent data streams on different colors of light on the same fiber) multiplies bandwidth without proportionally increasing power. Chiplet-to-chiplet communication that used to require a 2.5-inch electrical interposer can now route through a thin photonic waveguide. This matters at scale: a thousand-GPU cluster might eliminate tens of megawatts of switching power.

Papers: "Passage M1000: A 3D Photonic Interposer for AI". The limitation is maturity—photonics-to-electronics coupling is still noisy, photonic chip yields are lower than digital—but multiple companies are shipping pre-production runs.

### Custom datapaths and instruction-level specialization

General-purpose CPUs and GPUs execute arbitrary instructions. But if you know your workload is 90% matrix multiplication and 5% normalization, why pay the area and power cost of conditional branching, load-store units, or virtual memory?

Hot Chips 2025 shows a shift toward "thin-waist" designs: processors with a narrow, fixed instruction set tuned to one workload family (inference, training, vision, cryptography, voice). RISC-V has become the favorite baseline—it is simple, open, and leaves room for custom extensions. Entries include dedicated dataflows for attention operations (NTT transform for cryptography, sparse gather-scatter for transformers), fixed-point arithmetic optimized for quantized models, and elimination of rarely-used instruction types.

Papers: "BROCA: A Low-power and Low-latency Conversational Agent RISC-V System-on-Chip for Voice-interactive Mobile Devices", "Presto: A Unified RISC-V-Compatible SoC for Multi-Scheme FHE Acceleration over Module Lattice". These designs run at lower clocks (300-800MHz versus 2-5GHz for general-purpose CPUs) but achieve higher throughput per watt because every cycle does useful work.

### Chiplets and packaging-as-architecture

Cramming 50 billion transistors into a monolithic die at cutting-edge nodes is expensive and risky—higher defect rates, longer design-to-silicon cycles, greater risk of a single flaw killing the whole chip. The shift is to chiplets: break the design into smaller, testable chunks, assemble them in a package.

This is not new at Hot Chips, but 2025 shows it becoming the standard for large designs. The constraint is the interconnect between chiplets. Electrical traces are fine for single-package designs; optical waveguides are still too immature for everyone. The dominant approach: chiplets in a single package with high-bandwidth electrical interposers (10-100 Tbps). Some designs add specialized switching chips or memory controllers that manage traffic between chiplets, reducing congestion.

Papers reference photonic interposers, co-packaged optics, and custom mesh topologies for AI cluster interconnects. The tangible question is: can you design chiplet layouts such that common operations (like attention or convolution) can distribute across multiple chiplets with minimal cross-chip communication? If 80% of data stays on-chip and only 20% crosses the boundary, the overhead is acceptable.

### Quantization and mixed-precision arithmetic

High-precision (FP32, FP64) arithmetic is expensive in area and energy. Most modern models train in FP32 but can infer in INT8 or lower. The challenge: achieving bit-width reduction without accuracy collapse, and doing it efficiently in hardware.

Hot Chips 2025 shows industry moving beyond simple INT8. Designs now support multiple precisions: FP4 for weights, INT8 for activations, and FP16 for intermediate results. Some chips include dedicated instruction types for sub-byte arithmetic (bit-level sparsity, structured pruning). Others add analog computing blocks for approximation-tolerant operations like distance metrics or probabilistic sampling.

Papers: "Ultra-low-power LLM inference via extreme quantization", "Efficient edge diffusion via mixed-precision acceleration". The tradeoff is software complexity: models must be retrained or fine-tuned to tolerate lower precision, and different hardware may have different precision capabilities, fragmenting the software ecosystem.

### Energy harvesting and perpetual computing for edge

Not all AI workloads run in hyperscale data centers. Edge devices—remote sensors, IoT gateways, mobile phones—need to run inference on batteries or ambient power. Some designs now integrate energy harvesting: scavenging RF, thermal, and mechanical energy to extend battery life or enable perpetual operation.

Papers: "Everactive: Self-Powered SoC with Energy Harvesting, Wakeup Receiver, and Energy-Aware Subsystem". The limitation is scale: harvested power is milliwatts at best, constraining workloads to tiny models and sparse inference schedules. But for always-on monitoring (heartbeat detection, acoustic anomaly detection), it works.

## How it connects to the broader field

Hot Chips depends on two upstream communities. Academic architecture research (ISCA, ASPLOS, MICRO) develops new techniques and validates them on simulators. CAD research and tools (DAC, ICCAD) solve the practical problems of designing, verifying, and manufacturing billion-transistor designs. Hot Chips takes both and says: "Here is what actually manufactures today and ships in 18 months."

In turn, Hot Chips drives demand downstream. Software teams at hyperscalers (Google, Meta, Microsoft) attend to understand what hardware capabilities they can rely on. Framework teams (PyTorch, TensorFlow) optimize for the tensor cores and memory hierarchies revealed at Hot Chips. Customers (enterprises, startups) decide whether to adopt new accelerators based on the chipsets shown here.

What Hot Chips does not answer: How do we make AI faster at the algorithm level? That belongs to ML conference (NeurIPS, ICML). How do we prove circuits are correct? That is FMCAD. How do we scale beyond exascale? That is SC and ISC. Hot Chips focuses narrowly on the near-term: the shipping product.

## What's open

Manufacturing remains the central constraint. Advancing to new nodes (3nm, 2nm, 1.4nm) is exponentially more difficult. Yield rates drop, design complexity explodes, and cost per wafer increases. Some Hot Chips 2025 papers acknowledge this explicitly (Rapidus on Japanese manufacturing, advanced cooling for data center power delivery), but the community has no clean solution. You either invest billions in a new fab (few companies can), or you depend on external foundries (TSMC, Samsung) whose capacity is finite and allocation is political.

Second: there is no consensus on the right abstraction for hardware-software co-design. CPUs have ISAs (instruction set architectures). GPUs have compute hierarchies (thread blocks, warps). Custom accelerators have domain-specific languages (CUDA, Triton, etc.). But a software engineer using NVIDIA, AMD, Google, and Apple hardware simultaneously sees completely different programming models. Hot Chips exposes the problem but offers no unifying answer.

Third: latency at scale remains unsolved. Moving data between 1000 GPUs in a cluster with submillisecond latency is hard—it requires custom switching, precise clock synchronization, and careful orchestration. Papers on this exist, but the solutions are point designs, not principles.

Finally: the energy-latency-throughput tradeoff is still fundamentally empirical. No principled way exists to predict, for a new workload and a new architecture, which is the right balance. You build a prototype, measure, and iterate. This is expensive and slow. The next breakthrough would be formal methods that predict hardware suitability from algorithm structure.
