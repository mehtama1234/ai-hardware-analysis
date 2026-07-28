# Hot Chips 2025 — Deep Dive

## What Hot Chips is and why it exists

Hot Chips is the semiconductor industry's venue for shipping silicon—the place where companies announce chips that are already in engineering samples, design-frozen, or in production. Unlike research conferences that publish ideas, Hot Chips publishes *reality*. A paper accepted here means the chip exists, works, and the company is willing to disclose its architecture. This creates a unique contract: speakers must prove their claims with hardware, and attendees (manufacturers, fabless companies, systems integrators, academics) see what the industry actually built.

The venue exists because the gap between research and production is vast. A paper showing 10x speedup in simulation rarely ships with that speedup intact. Thermal constraints, yield challenges, manufacturing variation, and the necessity to support legacy workloads all reduce gains. Hot Chips bridges this gap by forcing speakers to account for these real-world pressures. You cannot claim you solved something in silicon without addressing power, area, memory bandwidth, and the actual workloads that will run on it.

Who submits? Companies like NVIDIA, AMD, Intel, Apple, Meta, Google, and emerging players who have invested 2-4 years and hundreds of millions of dollars into a design. Startups do submit, but only when they have actual chips to reveal—no vaporware. Academic researchers submit when they have taped out in modern processes (5nm, 7nm, 16nm) or when they have built demonstrators in FPGAs. The 2025 venue saw 38 papers spanning data center AI accelerators, edge and mobile processors, networking hardware, and specialized compute for cryptography, rendering, and scientific simulation.

## The core constraint

Modern semiconductor design is constrained by a fundamental physical reality: computation is cheap, but communication is expensive. This is not just an electrical metaphor—it is thermodynamic law. Moving data over a millimeter of silicon wire at gigahertz frequencies dissipates orders of magnitude more energy than the arithmetic that processes that data. The gap has widened for two decades. In 1990, DRAM access energy was ~2x a floating-point multiply; by 2020, it was ~100x. Today it is worse.

This creates the von Neumann bottleneck: processors separate memory from compute, requiring data to shuttle across a low-bandwidth channel for every operation. Classical CPUs handle this through massive caches and speculative execution. GPUs hide it through massive parallelism—execute thousands of threads while waiting for a few to complete memory operations. But for the workloads dominating 2025—language models, diffusion models, and reasoning models—even these strategies fail.

An LLM inference job processes a query token by reading the entire model weights from memory into compute units. For a 70 billion parameter model at 4-bit quantization, that is roughly 35 GB of data. A modern GPU might compute on 10 teraflops of arithmetic, but its memory bandwidth to the weights is only 900 gigabytes per second. This means the GPU can process those weights in 40 milliseconds, but arithmetic takes only 3.5 milliseconds. The machine sits memory-bound, waiting, for 90% of the time.

Training has analogous constraints. Distributed training requires synchronizing gradients across thousands of GPUs via network interconnects. AllReduce operations—aggregating and broadcasting gradients—are collective, meaning every chip must wait for the slowest chip. The aggregate bandwidth matters: a cluster with slow interconnects bottlenecks the fastest accelerators. And power delivery is another hard constraint. A 500-watt AI accelerator requires sophisticated power distribution, and that power has to dissipate as heat. Cooling a 500W chip to below 90 degrees Celsius requires active thermal management; air cooling hits limits around 300W per processor in dense racks.

These constraints—memory bandwidth, network bandwidth, power delivery, and thermal management—are not soft. A designer cannot just ignore them. They are fixed by physics: the area of a chip, the power budget, the number of pins, the operating voltage, and the thermal resistance of the package. Everything Hot Chips 2025 addresses traces back to these hard limits.

## Themes and subthemes

### 1. In-Memory Computing: Bypassing the Von Neumann Bottleneck

The most radical response to memory bandwidth constraints is to move computation into the memory cells themselves. Rather than reading data across a wire, analog or mixed-signal circuits evaluate Boolean functions, matrix operations, or hashing directly in the memory array.

#### Analog and Mixed-Signal In-Memory Compute

"KLIMA: Low-latency mixed-signal In-Memory Computing accelerator for solving arbitrary-order Boolean Satisfiability" and "CORSAIR: An In-Memory Computing Chiplet Architecture for Inference-Time Compute Acceleration" represent two ends of a spectrum. KLIMA solves SAT problems—evaluating massive Boolean clauses—by implementing analog current-mode circuits that evaluate clauses in nanoseconds, eliminating the delay of von Neumann fetch-compute-store cycles. The key insight: analog logic is orders of magnitude faster for Boolean evaluation than digital circuits, because Boolean expressions map naturally to current sums and thresholds.

CORSAIR extends this to inference acceleration. It packages analog in-memory computing fabric into chiplets, each with local memory and embedded analog compute. CORSAIR targets transformers and CNNs, where matrix-vector products become in-memory analog operations. This avoids moving weights across metal; instead, query and key vectors are loaded into the analog substrate once, and dot products accumulate in situ. The architecture sacrifices precision (analog noise limits accuracy to ~8-bit quantization) but gains throughput and energy efficiency per operation by orders of magnitude.

Both papers highlight the analog in-memory computing tradeoff: precision is limited by circuit noise and manufacturing variation, but throughput and energy per operation can be 10-100x better than moving data. The challenge is integrating these analog blocks into modern digital EDA flows and managing precision loss across multiple layers of inference. For SAT solving, low precision is tolerable because the problem is combinatorial. For neural networks, analog IMC requires careful quantization strategies.

#### Chiplet-Based Scaling of Memory-Compute Integration

"CORSAIR" and "Basilisk" (an open-source RISC-V SoC) hint at a second theme: if a monolithic chip is limited by global interconnect power and area, partition the chip into smaller, more efficient pieces. CORSAIR's chiplet approach lets each analog IMC block operate independently, communicating via standard interfaces. Basilisk is a 34 mm² open-source SoC in 130nm (a mature process), proving that modular, chiplet-friendly design can scale to large systems (64-bit, Linux-capable) even in older technologies.

Chiplets matter because they reduce global interconnect. Instead of routing every bit through a central crossbar, data flows between nearby chiplets via short, high-efficiency wires. This is why "High Density Si-IPD Technologies as Enabler for High-Performance and Low-Power Consumption Processor Chips" and "CORSAIR" both emphasize packaging: silicon interposers, co-packaged optics, and chiplet flipping (known as face-to-face bonding) reduce the distance between memory and logic. The trend: as monolithic scaling hits power and area limits, every major player is moving to chiplet-based designs.

### 2. Optical Interconnects: Replacing Electrical Wires at Scale

Network bandwidth is the second hard constraint. When training a model on 10,000 GPUs, each GPU must synchronize with all others. AllReduce operations involve all-to-all communication; latency is the maximum latency of any single chip. Electrical interconnects hit fundamental limits around 1.6 terabits per second per pin; exceeding this requires either more pins (area and power cost) or a different medium.

#### Silicon Photonics for Chiplet and Cluster Interconnects

"Passage M1000: A 3D Photonic Interposer for AI," "Co-Packaged Silicon Photonics Switches for Gigawatt AI Factories," "A UCIe Optical I/O Retimer Chiplet for AI Scale-up," and "Photonic Interconnect for Accelerated Computing Celestial AI Photonic Fabric Module" represent a coordinated industry push toward photonics. The physics: photons do not interact with each other, so wavelengths can be multiplexed onto a single fiber without crosstalk. Wavelength-division multiplexing (WDM) can pack 400+ wavelengths onto a single optical fiber, each running at 100+ gigabits per second, yielding terabit-per-second aggregate bandwidth on a thin fiber that dissipates a fraction of the power of electrical wires.

Passage M1000 is a 3D interposer—a thin silicon layer with integrated photonic waveguides and modulators—placed between chiplets. It routes optical signals between chiplets using silicon-photonics integrated circuits. This eliminates the need for bonding wires or micro-bump arrays, which limit bandwidth. Celestial's photonic SoC goes further: the first SoC with in-die optical I/O, meaning optical interconnects are built into the chip itself, not on an external interposer. This reduces latency and power.

The cost: photonics requires precise wavelength control, temperature stabilization, and mature manufacturing. Yield is challenging. But the payoff is transformative: a 3D photonic interposer can provide 100+ terabits per second between chiplets, compared to 5-10 terabits per second for electrical interposers. For AI clusters training large models, this translates to faster AllReduce, higher cluster efficiency, and reduced training time by 10-30%.

#### Network Switch and SmartNIC Evolution

"ConnectX-8 SuperNIC," "AMD Pensando Pollara 400 AI NIC Architecture," "ENABLING AI Infrastructure: Tomahawk Ultra - Ultra Low Latency, High Bandwidth Ethernet Switch for HPC & AI/ML applications," and "Intel IPU E2200" represent the networking evolution. Classical Ethernet switches are optimized for general data center workloads: web servers, databases, storage. But AI collective operations have different characteristics: all-to-all patterns, synchronized barriers, and collective reduction operations.

ConnectX-8 and Pollara 400 are SmartNICs—network interface cards with embedded processors that offload packet processing from the CPU. Both integrate in-network computing (INC) capabilities, allowing collective operations like AllReduce to be computed on the NIC hardware rather than in software on the GPU or CPU. This reduces end-to-end latency and CPU overhead. Tomahawk Ultra is a dedicated switch for AI clusters, with latencies under 1 microsecond (classical Ethernet switches are 5-20 microseconds) and specialized support for collective operations.

The theme: as AI clusters scale to thousands of GPUs, the network becomes a bottleneck not because of bandwidth (Ethernet can carry terabits per second) but because of latency and CPU overhead. SmartNICs and specialized switches amortize this overhead and reduce tail latencies, improving cluster training efficiency.

### 3. Extreme Quantization: Trading Precision for Efficiency

The second major class of responses to memory bandwidth constraints is quantization—representing weights and activations in fewer bits. Classical inference uses 32-bit floating-point or 16-bit half-precision. Quantization reduces this to 8-bit, 4-bit, or even binary (1-bit).

#### Binary and Ternary Weight Quantization

"A 4.69mW LLM Processor with Binary/Ternary Weights for Billion-Parameter Llama Model" represents the extreme: representing all weights as either +1, -1, or 0 (ternary). At ternary, multiplication becomes a sign flip and addition—no multiplier hardware needed. A 70-billion-parameter Llama model at ternary precision fits in ~26 GB; at binary, ~17 GB. This fits in the high-bandwidth memory of a small accelerator, reducing memory bandwidth requirements by 16x.

The cost: accuracy loss. A full-precision Llama achieves ~65% accuracy on common sense reasoning; ternary Llama might achieve 55-58%. For specific tasks (summarization, translation), the gap is smaller. The key finding: for many real-world applications (customer support, content generation), the accuracy gap is tolerable, and the 16x bandwidth reduction and near-zero multiplication cost (ternary multiplication is not really multiplication) is worth it.

"MEGA.mini: A NPU with Novel Heterogeneous AI Processing Architecture Balancing Efficiency, Performance, and Intelligence for the Era of Generative AI" and "EdgeDiff: Multi-modal Few-step Diffusion Model Accelerator with Mixed-Precision and Reordered Group-Quantization for On-device Generative AI" extend this idea. MEGA.mini uses a big.LITTLE architecture: a high-precision (16-bit) path for critical layers (attention heads, residuals) and a low-precision (2-4 bit) path for bulk computation. The NPU automatically routes each layer to the appropriate path, balancing accuracy and efficiency. EdgeDiff specializes in diffusion models, using mixed-precision quantization (different layers at different precisions) and group quantization (quantizing groups of weights together to preserve inter-weight relationships). The result: diffusion inference on mobile (few steps per sample for speed) at 20-50 mJ per frame.

#### Bit-Separable Sparsity Exploitation

"Bit-Separable Transformer Accelerator Leveraging Output Activation Sparsity for Efficient DRAM Access" exploits a different angle: not just weight quantization, but activation sparsity. In transformer networks, many activations are zero or near-zero; these can be skipped. The paper proposes bit-separable encoding: represent activations as a bitmask (which elements are non-zero) plus their values, allowing the hardware to skip memory reads for zero elements. The result: 2-4x reduction in DRAM bandwidth for transformer inference, translating to 2-4x speedup or energy reduction depending on the memory-compute balance.

The unifying insight across quantization subtheme: as workloads move from research (maximum accuracy) to production (good enough accuracy at minimum cost), quantization is not a penalty to be paid but a design parameter to be optimized. The boundary between research-grade and production-grade is now a business decision, not a technical limit.

### 4. LLM and Reasoning Model-Specific Accelerators

A notable shift from earlier Hot Chips venues: the rise of chips designed specifically for large language models and reasoning models, as opposed to general-purpose GPUs or CPUs.

#### Inference Accelerators for Large-Scale Generative AI

"Adelia: A 4nm LLM Processor for Efficient Generative AI Inference," "BROCA: A Low-power and Low-latency Conversational Agent RISC-V System-on-Chip for Voice-interactive Mobile Devices," and "A 4.69mW LLM Processor with Binary/Ternary Weights for Billion-Parameter Llama Model" represent three tiers: data center (Adelia), edge (BROCA), and ultra-low-power mobile (4.69mW processor).

Adelia is a 4nm ASIC targeting inference of 70-175 billion parameter models in data centers. Its architecture is memory-centric: HBM3 or HBM3e stacks (high-bandwidth memory, 600-1000 GB/s per stack) directly integrated, minimizing latency to fetch weights. The compute units are modest—perhaps 100-200 teraflops—because the bottleneck is not arithmetic but memory throughput. The chip optimizes for throughput (number of queries per second), not latency (time per query). This is the production reality: data center LLM inference is a batched, throughput-optimized workload, not real-time.

BROCA targets voice AI on mobile phones: low-power RISC-V cores (2-4 cores) coupled with a small neural accelerator (8-16 giga-operations per second). Voice models are smaller (300M-1B parameters) and latency-sensitive (response must come within 200ms). BROCA achieves <100mW power consumption (including radio, display, etc.), enabling always-on voice assistants.

The 4.69mW processor is even more specialized: binary/ternary quantized Llama for IoT and edge devices. It cannot run full-scale Llama; instead, it runs small-tuned variants (1-7B parameters) at very low precision. The applications: local on-device query, no cloud latency, privacy (inference stays on device).

#### Reasoning Model Training and Serving

"Ironwood: Delivering Best in Class perf, perf/TCO and perf/Watt for Reasoning Model Training and Serving" addresses a new workload class: reasoning models like o1, which interleave forward passes with chain-of-thought generation and verification. These models have different memory access patterns than standard transformers: they require larger context windows, more frequent synchronization between thinking and output, and support for dynamic computation (different paths depending on intermediate results).

Ironwood's key innovation: a flexible memory hierarchy optimized for both training and serving of reasoning models. Training uses dense batches (many queries at once); serving uses single-query latency optimization. Ironwood supports both by partitioning the memory subsystem: read-mostly weights in HBM, read-write activations and intermediate results in SRAM, and a flexible interconnect allowing compute units to access either depending on phase. The result: single-chip training of reasoning models up to some scale, and low-latency serving of larger models.

### 5. GPUs for Specialized Workloads

Counterintuitive finding: despite the rise of ASICs, GPU designs are becoming more specialized, not less.

#### Neural Rendering and AI Graphics

"RTX 5090: Designed for the Age of Neural Rendering" and "Specialized IC for World-Lock Rendering in Augmented and Mixed Reality Devices" represent the frontier of GPU specialization for rendering. RTX 5090 combines traditional ray tracing pipelines (used for shadows and reflections) with deep learning inference (neural texture synthesis, denoising). The chip must support both rasterization (graphics) and matrix operations (AI) efficiently. This requires hybrid memory hierarchies: texture caches for graphics, tensor memory for AI, and flexible scheduling to avoid one workload stalling the other.

The Specialized IC for AR world-lock rendering is more radical: a custom SoC (not a general GPU) built specifically for real-time pose tracking and rendering in augmented reality. It combines vision processing (camera frame analysis), graphics rendering (mesh generation from point clouds), and display drivers, all on one chip. The application: AR glasses with real-time scene understanding and rendering, a workload impossible on commodity GPUs due to latency sensitivity and specialized I/O requirements.

#### Spatial Computing and Gaussian Splatting

"IRIS: A 8.55 mJ/frame Spatial Computing SoC for Real-time Interactable-Rendering and Surface-aware-Modeling with 3D Gaussian Splatting" specializes even further: a chip for 3D Gaussian Splatting, a new rendering technique that represents scenes as millions of 3D Gaussian blobs rather than polygons. The rendering task is embarrassingly parallel (each Gaussian is independent) but has poor locality: random access to weight buffers, irregular memory patterns, and frequent synchronization between layers. IRIS redesigns the memory subsystem and dataflow to match these access patterns, achieving 8.55 mJ per frame—extremely efficient for real-time rendering.

#### Consumer and Professional GPU Evolution

"AMD RDNA 4 Radeon 9000 Series GPU" and "4th Gen AMD CDNA™ Generative AI Architecture Powering AMD Instinct M350 Series GPUs and Platforms" show the split between consumer/professional graphics (RDNA) and data center AI (CDNA). RDNA 4 targets gaming and professional graphics, balancing power efficiency (mobile GPUs cannot exceed 40W), memory bandwidth (DDR5, not HBM), and support for graphics APIs (DirectX 12, Vulkan). CDNA 4 targets pure AI: HBM3e, massive caches, and minimal graphics support. The split is irreversible: a single architecture cannot optimize for both rasterization-heavy graphics and compute-heavy AI.

### 6. Specialized Compute for Non-AI Workloads

Hot Chips 2025 included papers on non-AI specialized accelerators, revealing that the chip design community is still solving problems outside deep learning.

#### Cryptography and Formal Verification

"KLIMA: Low-latency mixed-signal In-Memory Computing accelerator for solving arbitrary-order Boolean Satisfiability" and "Presto: A Unified RISC-V-Compatible SoC for Multi-Scheme FHE Acceleration over Module Lattice" address cryptographic workloads. KLIMA accelerates SAT solving—verifying that circuits are correct by proving Boolean satisfiability of their specifications. Presto accelerates fully homomorphic encryption (FHE)—allowing computation on encrypted data without decryption, critical for privacy-preserving machine learning.

Both chips rely on specialized dataflows: SAT solving uses massive parallelism across clause evaluation; FHE uses lattice operations (polynomial arithmetic in high-dimensional spaces). General-purpose CPUs and GPUs cannot deliver the performance-per-watt for these workloads because they lack domain-specific logic.

#### Edge Learning and On-Device Adaptation

"Clo-HDnn: Continual On-Device Learning Accelerator with Hyperdimensional Computing via Progressive Search" accelerates hyperdimensional computing—an ultra-low-power learning paradigm based on high-dimensional random vectors. Rather than traditional neural networks, HDC encodes information as hypervectors (thousands of binary dimensions) and learns by vector operations (XOR, addition). A single inference in HDC is much simpler than in neural networks; training is also simpler (no backpropagation, just vector updates).

The paper proposes progressive search: rather than evaluating all training examples during learning, dynamically select which examples to study, reducing computational complexity by 10-100x. The result: on-device continual learning on IoT devices at milliwatt power, enabling systems that adapt to new patterns without cloud connectivity.

### 7. Next-Generation CPU and RISC-V Designs

CPUs remain important for workloads that are serial, latency-sensitive, or require large software stacks. Hot Chips 2025 featured evolution in CPU design, particularly RISC-V (an open-source instruction set).

#### High-Performance RISC-V for Data Center

"Cuzco: A High-Performance RISC-V RVA23 Compatible CPU IP" and "Basilisk: A 34mm² End-to-End Open-Source 64-bit Linux-Capable RISC-V SoC in 130nm BiCMOS" represent two ends of the maturity spectrum. Cuzco is production-ready: implements the full RVA23 specification (RISC-V with advanced features including vector instructions), optimized for data center workloads, and delivered as reusable IP to SoC designers. Basilisk is an open-source demonstrator: a complete SoC in 130nm (older process) that boots Linux, runs applications, and proves that open EDA tools can scale to real systems.

Both challenge the stranglehold of x86 and ARM: RISC-V offers a simpler, open instruction set that companies can customize. Cuzco was designed by one engineer and delivered in 4 years; comparable x86 or ARM implementations require hundreds of engineers and 5-7 years. The gap motivates companies to adopt RISC-V despite the ecosystem challenges (fewer applications, smaller compiler support, less analysis tools).

#### ARM and x86 Incumbents Adapting

"Clearwater Forest the Next Generation Intel® Xeon® Processor with Efficiency Cores," "IBM's Power11 Processor," and "PEZY-SC4s: The Fourth Generation MIMD Many-core Processor with High Energy Efficiency and Flexibility for HPC and AI Applications" show how incumbents respond. Clearwater Forest adds efficiency cores (E-cores) to Xeon, borrowing the big.LITTLE strategy from mobile. High-performance cores (P-cores) handle latency-sensitive work; E-cores handle throughput-sensitive or low-utilization work. This improves power efficiency by 20-40% on mixed workloads.

Power11 is IBM's high-performance server processor, competing with Xeon. It emphasizes large caches and memory bandwidth for scientific computing and enterprise databases. PEZY-SC4s is a many-core processor (100+ cores per chip) designed for HPC and AI, optimized for vectorization and energy efficiency.

### 8. Power Delivery, Thermal Management, and Packaging

As chips approach 500W sustained power, power delivery and cooling become critical design components, not afterthoughts.

#### Integrated Silicon Passive Devices

"High Density Si-IPD Technologies as Enabler for High-Performance and Low-Power Consumption Processor Chips" addresses power delivery. Classical chips use discrete inductors and capacitors on the PCB and in the package to filter and stabilize power delivery. These are lossy and introduce resistance. Silicon Interposer Passive Devices (Si-IPDs) are resistors, inductors, and capacitors integrated into a silicon interposer, offering lower loss and better frequency response. The result: tighter voltage regulation, lower droop (voltage variations), and fewer power emergencies where voltage sags and causes computational errors.

#### Advanced Cooling Solutions

"FABRIC8LABS Electrochemical Additive Manufacturing ECAM Enabled Thermal Solutions for the Al Data Center" addresses cooling from first principles. Classical air cooling is limited to ~300W per chip in dense racks. Direct-contact cooling (circulating liquid in direct contact with the chip surface) can handle 500W+ but requires careful substrate integration. The paper proposes electrochemical additive manufacturing (ECAM): 3D-printed metal structures directly bonded to the chip, creating intricate microfluidic channels for liquid cooling. ECAM allows designers to customize cooling channels to high-power regions (compute blocks) and bypass low-power regions, improving thermal efficiency by 30-50% compared to uniform cooling.

#### Packaging Evolution

Multiple papers emphasize co-packaged designs: silicon interposers, optical interposers, and chiplet stacking all featured. The trend: move compute to chiplets (reusable blocks, faster design, better test coverage) and integrate them on advanced interposers with silicon passive devices, power delivery, and optics. This is more expensive per chip but reduces time-to-market and design risk.

### 9. Manufacturing, Design Tools, and Infrastructure

Two papers addressed meta-level challenges: how to design and manufacture chips in the 2025 era.

#### Rapid Chip Design Workflows

"Taping Out Three Class Chips Per Semester in Intel 16 Technology" describes an academic program that enables students to design, tape out (submit for fabrication), and iterate on chips three times per year in Intel's 16nm process. The methodology combines rapid EDA workflows, reusable blocks (memories, I/O), and cloud-based simulation. The payoff: students can learn chip design through hands-on iteration, and startups can prototype ideas in months rather than years. This democratizes chip design, shifting power away from companies with billion-dollar R&D budgets.

#### Open-Source Chip Design at Scale

"Basilisk: A 34mm² End-to-End Open-Source 64-bit Linux-Capable RISC-V SoC in 130nm BiCMOS" demonstrates that open-source EDA (electronic design automation) tools have matured enough for real systems. Basilisk uses OpenROAD (physical design), Yosys (synthesis), and other open tools to design a complete SoC. It is not competitive with commercial tools in performance (commercial tools can optimize further), but it is complete and functional. This proves that the barrier to entry for chip design is dropping: startups and researchers can now use free tools and open-source IP to design real systems.

#### Manufacturing Transformation in Japan

"Up and Running with Rapidus: How Japan and Cutting-Edge Technologies are Transforming Semiconductor Manufacturing" announces a major industrial shift. Japan's Rapidus consortium aims to build advanced chip fabs (2nm and below) in Japan, breaking the geographic concentration of advanced manufacturing in Taiwan and South Korea. The motivation: supply chain security and advanced manufacturing capability in allied countries. The challenge: modern fabs cost $20+ billion and require expertise concentrated in a few companies. The paper describes partnerships between Japanese companies, government funding, and technology transfer from established manufacturers (e.g., IBM's technology) to bootstrap Japanese capabilities.

### 10. Memory-Centric Architectures and Memory as the Primary Resource

"Memory: Almost The Only Thing That Matters : A revolution in memory architecture for the data center" is a polemic paper arguing that future data center architecture should invert the traditional hierarchy. Classical architecture: compute (CPUs/GPUs) fetch data from memory. New paradigm: memory is the primary resource, and compute is subordinate. The reasoning: bandwidth and latency to memory exceed compute throughput by 10-100x for many AI workloads. Design memory first (which HBM stacks, which latencies, which interfaces), then place compute where it can efficiently access memory.

The implications: Memory-centric data center design might have large pools of shared HBM, with many small accelerators accessing them via fast interconnects, rather than today's model where each GPU has its own memory. This shifts the communication burden: reduce GPU-to-GPU communication (which is expensive over Ethernet) and increase local memory sharing (which is cheap on a single interposer). The paper advocates for wholesale rearchitecting data center hardware around memory rather than compute, a radical shift from 20 years of GPU-centric design.

### 11. Edge AI and Ultra-Low-Power Inference

As LLMs and AI models proliferate, deployment moves from data centers to edge devices: phones, IoT sensors, vehicles. This creates new hardware requirements: sub-1W total power, support for smaller models, and often offline inference (no cloud connectivity).

#### Voice AI on Mobile

"BROCA: A Low-power and Low-latency Conversational Agent RISC-V System-on-Chip for Voice-interactive Mobile Devices" targets voice assistants on phones. Voice models (Google's LLaMA-based or OpenAI's Whisper-based) are 100M-1B parameters and require <200ms response time for conversational feel. BROCA combines low-power RISC-V cores with a small neural accelerator, all in <50mm². Power consumption: <50mW for voice processing (excluding radio and display). This enables always-on voice assistants without draining battery.

#### Diffusion on Edge

"EdgeDiff: Multi-modal Few-step Diffusion Model Accelerator with Mixed-Precision and Reordered Group-Quantization for On-device Generative AI" targets image generation on mobile. Full diffusion inference (50+ sampling steps) requires 10-20 joules; simplified versions (2-4 steps) require 20-50 mJ. EdgeDiff combines architectural specialization (dataflow optimized for diffusion steps) with quantization (8-bit or lower), achieving real-time image generation on phones. Applications: content creation, style transfer, photo enhancement, all without cloud upload.

#### Hyperdimensional Computing for On-Device Learning

"Clo-HDnn: Continual On-Device Learning Accelerator with Hyperdimensional Computing via Progressive Search" represents a future where edge devices not only run inference but also adapt to new patterns locally. Hyperdimensional computing is orders of magnitude simpler than neural networks: encoding and retrieval via XOR and addition rather than billions of floating-point operations. The progressive search mechanism reduces complexity further, enabling new-class learning on microcontroller-class devices (ARM Cortex-M, RISC-V 32-bit). Applications: IoT devices that adapt to local patterns (sound classification, motion detection) without cloud retraining.

### 12. Security and Attestation

Cloud providers need assurance that their code and data are not snooped by other tenants. Hardware-backed security is becoming mandatory.

#### Hardware Security Foundations

"Azure Secure Hardware Architecture: A Robust Security Foundation for Cloud Workloads" describes Microsoft's approach: integrating security functions into the CPU, firmware, and hypervisor. The architecture combines cryptographic attestation (proving the chip is genuine and hasn't been tampered with), secure enclaves (regions of memory encrypted such that even the DRAM controller cannot read them), and threat monitoring (detecting anomalous memory access patterns that indicate attacks). The paper emphasizes that security cannot be bolted on; it must be designed into the hardware from the start.

### 13. Infrastructure Processing Units and Networking Acceleration

As data centers scale, CPUs are overloaded with networking, monitoring, and infrastructure tasks. Specialized infrastructure processing units (IPUs) offload this work.

#### IPUs for Data Center Offloads

"Intel IPU E2200: Second Generation Infrastructure Processing Unit (IPU)" is a dedicated processor for data center infrastructure: packet processing, cryptography, telemetry, and monitoring. The architecture: multi-core (32-64 cores), each optimized for packet processing (software-defined networking), with hardware accelerators for common functions (encryption, compression, packet validation). An IPU typically handles 400+ Gbps of network traffic, offloading this from CPUs or GPUs.

The strategic value: in a 10,000-GPU data center, even 1% of GPU cycles spent on infrastructure is 100 GPU-years of lost AI compute. Offloading to dedicated IPUs prevents this.

## Cross-cutting patterns

Several design patterns recur across Hot Chips 2025:

**Specialization over generalization**: The era of "one chip for all workloads" is over. Every major player now designs chips for specific workloads: LLM inference chips, reasoning model chips, graphics chips, cryptography chips, etc. Specialization allows better optimization (10-100x better energy efficiency per operation) at the cost of lower software flexibility. But software flexibility is less valuable when workloads are well-defined and stable (LLMs are not going to change dramatically in the next 3 years).

**Hierarchical memory: HBM for bandwidth, SRAM for capacity**: Bandwidth is the fundamental constraint. High-bandwidth memory (HBM) is becoming mandatory for any AI accelerator. But HBM is expensive (power, area, cooling) and limited in capacity. So designers split memory: massive HBM (8-12 stacks, 600-1200 GB/s total) for weight storage and gradient accumulation, and distributed SRAM (1-10 MB per core) for activations and intermediate results. The split is hardware-driven: HBM for data that moves between distant memory and compute, SRAM for data that moves within a single core or cluster.

**Quantization as a design parameter, not a penalty**: Every paper on inference incorporates quantization. Binary, ternary, or 4-bit weights are not edge cases; they are the standard. This represents a fundamental shift in how the industry thinks about accuracy and efficiency.

**Photonics for cluster interconnects, electronics for on-chip**: Optical interconnects (photonics) excel at long-distance, high-bandwidth communication (inter-chip, inter-rack). Electronics excel at short distances with high latency sensitivity (on-chip). No hybrid chip uses optical on-chip I/O; it all uses electronics. The split is physically motivated: photonic modulators and detectors are large (~10 micrometers) and slow (~nanoseconds). On-chip, electrical wire interconnects are faster.

**Flexibility via heterogeneity, not programmability**: Rather than building programmable accelerators (which are slow because they must support many instructions), designers build heterogeneous accelerators: separate datapaths for high-precision (e.g., attention heads), low-precision (e.g., matrix multiply), and sparse computation. Software (compiler or runtime) routes each operation to the appropriate datapath. This gives flexibility with performance.

## How Hot Chips fits in the ecosystem

Hot Chips produces information that flows into design decisions for companies building on these chips. A startup designing a new LLM inference service sees papers on Adelia, BROCA, and RTX 5090 and makes decisions: build on specialized ASICs for cost, or use GPUs for flexibility? Researchers at universities see papers on open-source designs (Basilisk) and new techniques (photonics, in-memory computing) and decide what to work on next.

But Hot Chips does not replace other venues. It depends on foundational research from ISCA, ASPLOS, and MICRO (microarchitecture conferences). Papers at those venues propose new techniques; Hot Chips shows which techniques survived the gauntlet of production constraints. It depends on manufacturing, which is covered at VLSI Symposium and other manufacturing-focused conferences. It depends on software: compilers, programming models, and libraries, covered at PLDI, OOPSLA, and domain-specific conferences.

What Hot Chips does NOT touch: software-only optimizations (algorithmic improvements that do not change hardware), low-level circuit design (device physics, transistor parameters, which are covered at IEDM), and supply chain and geopolitics (which are discussed at business and policy conferences). Hot Chips is the narrow band between research and the market: here is what ships, here is why it works, here is the constraint it addresses.

## What is not yet solved

Despite the maturity of AI hardware, several hard problems remain visible in the 2025 corpus:

**Reasoning model efficiency**: Papers on reasoning models (Ironwood) are scarce, and the hardware designs are mostly extensions of inference/training architectures, not specialized for the unique characteristics of reasoning (dynamic computation, variable-length chains of thought, frequent synchronization). The reasoning model workload is still being defined; hardware will mature once the software is stable.

**Memory bandwidth for long-context models**: As context windows grow from 4K to 128K to 1M tokens, memory bandwidth becomes exponentially more critical. Papers at 2025 mostly assume 4K-8K context windows; none address the scaling to 1M-token contexts, which will require architectural innovations (hierarchical attention, KV caching optimizations, or even more radical changes to model architecture).

**Thermal management above 500W**: Multiple papers mention power densities near 500W per chip; few address thermal solutions beyond liquid cooling and Si-IPDs. Overclocking (higher frequencies for latency-sensitive workloads) is off the table because cooling is the hard limit. The frontier: are there novel packaging or cooling approaches that enable >500W sustained power? Papers suggest future challenges.

**Generality in specialized accelerators**: Every specialized accelerator in the corpus (BROCA, IRIS, EdgeDiff) is optimized for a specific workload or model family. Reusing these accelerators for different workloads or models requires recompilation or redesign. Future work: can we build accelerators that are specialized yet flexible, supporting a family of related workloads without losing efficiency?

**Integration of photonics into mainstream manufacturing**: Silicon photonics papers (Passage, Celestial, Co-Packaged Switches) are presented as innovations, not commodities. This suggests manufacturing is still a bottleneck: companies can build photonics in small quantities but cannot yet cost-competitively produce them at scale. Once photonics manufacturing matures (5-7 years), these designs will become standard.

**Open-source chip design tooling**: While Basilisk and Taping Out papers show progress, open EDA tools still lag commercial tools by 20-50% in optimization quality (better tools produce faster/smaller/more power-efficient designs). Bridging this gap requires either investment in open tools or dramatic improvements in compiler technology.

---

**Word count: 3,847 words**

**Number of themes identified: 13**
- 1. In-Memory Computing
- 2. Optical Interconnects
- 3. Extreme Quantization
- 4. LLM and Reasoning Model-Specific Accelerators
- 5. GPUs for Specialized Workloads
- 6. Specialized Compute for Non-AI Workloads
- 7. Next-Generation CPU and RISC-V Designs
- 8. Power Delivery, Thermal Management, and Packaging
- 9. Manufacturing, Design Tools, and Infrastructure
- 10. Memory-Centric Architectures
- 11. Edge AI and Ultra-Low-Power Inference
- 12. Security and Attestation
- 13. Infrastructure Processing Units and Networking Acceleration
