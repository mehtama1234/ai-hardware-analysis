# FCCM 2025: The Reconfigurable Middle Ground

## What FCCM Is

The Field-Programmable Custom Computing Machines symposium is where researchers who build hardware from software meet researchers who optimize software for hardware. The venue sits at an unusual intersection: it is simultaneously a hardware conference (attendees care deeply about logic utilization, routing congestion, and clock frequency) and a software conference (attendees care about compilers, abstractions, and programmer productivity). This tension is not a weakness — it is the exact intellectual space that FPGAs inhabit.

FCCM is the premier academic venue for FPGA-based computing, covering everything from the FPGA fabric itself to the tools that program it to the applications that justify its existence. In 2025, that application landscape is dominated by machine learning — particularly large language model inference, transformer acceleration, and the growing demand to run billion-parameter models on devices that do not have data center power budgets.

## The Physical Reality: What an FPGA Actually Is

An FPGA is a chip whose function is not fixed at fabrication. Instead of burning in a circuit, the manufacturer ships a blank slate of programmable logic resources and lets the user download a *bitstream* — a configuration file — that connects those resources into a specific circuit. Power cycle the chip, load a different bitstream, and you have a different circuit.

The blank slate consists of four building blocks. *Look-up tables* (LUTs) are small memories that implement arbitrary Boolean functions: a 6-input LUT is a 64-bit table that can compute any function of 6 binary inputs. A modern high-end FPGA (Xilinx Ultrascale+, Intel Agilex) has one to two million LUTs. *Flip-flops* (registers) store one bit of state; they sit alongside LUTs and enable sequential logic. *Block RAMs* (BRAMs) are on-chip memory tiles, typically 18Kb or 36Kb each, that implement buffers, FIFOs, and local scratchpads without consuming LUTs. *DSP blocks* (digital signal processor slices) are hardened multiply-accumulate units — typically an 18×27-bit multiplier feeding into a 48-bit accumulator — that perform the core operation of neural network inference without needing dozens of LUTs per multiply.

The resources are connected by a *routing fabric*: a grid of programmable switch matrices and wires. Routing is where FPGAs pay their overhead tax. A configurable interconnect cannot be as fast or as dense as a fixed wire in an ASIC; the routing fabric consumes 60-80% of the chip area and introduces cycle delays that a custom chip would avoid. This overhead is why FPGAs are 3-5x slower at the same clock frequency as a comparable ASIC and why they consume more power than a purpose-built chip.

So why use them? Because an FPGA can be fabricated once and reprogrammed for many different workloads. An ASIC designed for ResNet-50 cannot run GPT-4. An FPGA running ResNet-50 can be reconfigured tonight to run GPT-4 tomorrow. This flexibility has a price — it is slower and less efficient than either a GPU (optimized for parallelism) or an ASIC (optimized for one workload) — but it hits a sweet spot for applications that need customization, low latency, or power budgets that rule out GPUs.

## The Central Problem: The Productivity Gap

The fundamental constraint that drives FCCM research is the *productivity gap*. An FPGA can be 10-100x more energy-efficient than a GPU for a well-matched workload. But writing the bitstream to exploit that efficiency requires hardware description language (HDL) expertise — Verilog, VHDL — that most software engineers do not have. It also requires understanding of pipeline depth, timing closure, resource constraints, and the specific quirks of the FPGA vendor's implementation tools. A skilled GPU programmer writes CUDA in a day; implementing the same operation in HDL takes weeks.

High-level synthesis (HLS) tools — Vitis HLS from AMD/Xilinx, Intel HLS Compiler, Catapult — promise to close this gap. They compile C, C++, or SystemC into RTL (register-transfer level) descriptions that can be synthesized into FPGA bitstreams. In principle, you write a loop, annotate it with pragmas for pipelining and unrolling, and the tool generates the hardware. In practice, the generated hardware is often 2-5x worse than hand-written HDL in resource efficiency and frequency, and the debugging experience — understanding why the tool made specific choices — remains opaque.

The 2025 FCCM corpus shows the research community attacking this gap from both ends: making the tools smarter (better HLS, better placement and routing, ML-guided optimization) and making the hardware more amenable to high-level programming (domain-specific overlays, flexible soft-processors, reconfigurable compute tiles).

## Subtheme 1: LLM Inference on FPGAs

The dominant application thread at FCCM 2025 is deploying large language models on FPGAs for edge inference — running billion-parameter models without data center infrastructure. The motivation is real: a hospital cannot send patient data to the cloud; an autonomous vehicle cannot tolerate 50ms network round-trips; a satellite has 50 watts of power.

The challenge: a 7B-parameter model in FP16 requires 14GB of storage. A high-end FPGA (Alveo U280) has 8GB of HBM on board. The model does not fit. The research response is to aggressively quantize: INT4 brings a 7B model to 3.5GB, which fits. But FPGA DSP blocks are designed for 18-bit multipliers, not INT4 multiplications. Packing four INT4 multiplies into one DSP requires careful bit-manipulation — *DSP packing* — to avoid wasting 80% of each DSP's compute.

Several FCCM 2025 papers attack transformer inference directly. One demonstrates FP8 approximate multipliers that exploit the FPGA's LUT resources to trade a small accuracy loss for a 2x reduction in area versus exact FP8 multiplication — leveraging FPGAs' flexibility (you can build arbitrary arithmetic in LUTs) for something an ASIC cannot do cheaply. Another implements linear-attention mechanisms (replacing O(n²) softmax attention with O(n) recurrent formulations) in an FPGA dataflow pipeline where the entire computation fits in on-chip BRAMs without DRAM access. A third implements FPGA-native MoE (mixture-of-experts) routing, arguing that the dynamic expert-selection logic — which is irregular and hard to vectorize on GPUs — maps naturally onto FPGA lookup tables.

The tradeoff: FPGA inference is slower than an A100 (GHz clocks vs 1.4GHz, and far fewer parallelism opportunities) but wins on latency-per-watt and total cost of ownership for edge deployments where you cannot provision a GPU cluster.

## Subtheme 2: High-Level Synthesis and Compiler Advances

If LLM inference is what justifies FPGA investment, HLS is what makes it accessible. The FCCM 2025 corpus has a substantial thread on making HLS-generated circuits competitive with hand-written HDL.

The fundamental limit of current HLS tools is that they work at function boundaries. They can pipeline a loop within a function, but they cannot automatically identify that two adjacent functions should share a BRAM or that three separate loops should be fused to avoid redundant DRAM access. This is the *locality problem*: HLS operates locally, but efficiency requires global reasoning.

Papers this year address several facets. One explores *dynamic scheduling* in HLS — abandoning the assumption of static, compile-time-determined pipeline initiation intervals (II) and allowing memory-dependent loops to stall dynamically. This is harder to implement but generates smaller circuits because you do not have to pessimistically over-provision for worst-case memory latency. Another uses equality saturation (the e-graph technique from the compiler theme) to explore the space of equivalent dataflow schedules and pick the one that minimizes resource usage — the first application of equality saturation to HLS that this corpus shows. A third studies the interaction between HLS pragmas and the routing stage downstream, showing that pragma choices that reduce LUT usage can increase routing congestion and reduce maximum clock frequency, motivating *timing-aware HLS* that models downstream routing constraints at compile time.

FPGA-specific DSL compilers — domain-specific languages that target the FPGA dataflow model rather than general sequential semantics — appear repeatedly. These languages expose the FPGA's pipeline structure directly to the programmer, trading generality for predictable performance.

## Subtheme 3: Sparse and Approximate Computation

Sparsity and approximation are natural fits for FPGAs. A GPU SIMD unit wastes cycles on zero multiplications in a sparse matrix because the hardware cannot skip them without breaking SIMD alignment. An FPGA, by contrast, can implement a fully custom sparse processing unit that skips zeros at the cost of some routing and control logic — and it can do so with exactly the granularity the application needs, not whatever the GPU vendor decided was worth accelerating.

The 2025 corpus shows this clearly. Papers implement sparse attention with hardware-native token selection (deciding which KV pairs to compute without going through a softmax over all pairs), sparse matrix accelerators where the sparsity pattern is stored explicitly and the compute units are wired directly to the relevant data, and approximate arithmetic (FP8 multipliers, stochastic rounding, truncated accumulators) where the FPGA's LUT flexibility lets you build non-standard number representations that no GPU or ASIC would support.

The recurrent theme is *workload-specific customization*: because you can change the bitstream, you can design arithmetic and memory access patterns that perfectly match your specific model's sparsity structure. This is impossible on a GPU (fixed hardware) and expensive on an ASIC (requires re-tapeout). The FPGA occupies a unique position: post-deployment customization at hardware speed.

The tradeoff: developing the custom sparse hardware is still non-trivial. Even with HLS, building a correct, timing-closure-meeting sparse accelerator takes more engineering effort than writing a CUDA sparse kernel. The papers in this category are mostly research demonstrations, not production deployments.

## Subtheme 4: Placement, Routing, and Physical Design Optimization

The FPGA toolchain's most compute-intensive steps — placement (assigning each LUT to a physical tile on the chip) and routing (connecting those tiles through the programmable fabric) — are classical combinatorial optimization problems that the FPGA vendors have been solving with heuristics for 40 years. They are also, increasingly, being solved with machine learning.

FCCM 2025 shows several papers using GNNs (graph neural networks) as *timing predictors*: given a partial placement, predict the critical path delay before completing the full routing, and use that prediction to guide the placer toward better solutions. Traditional timers require the full routing to be complete before they can report timing; a learned predictor can give feedback during placement, enabling placement to account for timing rather than optimizing only for wire length.

Other papers optimize *DSP cascade chains* (connecting multiple DSP blocks to implement higher-precision arithmetic without LUT overhead), improve legalization in analytical placement (where the continuous relaxation of placement must be rounded to discrete tile positions without violating resource constraints), and explore *heterogeneous placement* for FPGAs with different resource types (BRAMs, UltraRAMs, DSPs, AI engines in Versal devices) that require careful co-placement to avoid routing bottlenecks.

The underlying tension: placement and routing are NP-hard optimization problems. The heuristics that vendors ship have been tuned for typical workloads over decades. ML-based approaches outperform these heuristics on specific workload families — particularly the regular array structures that ML accelerators generate — but may degrade on other workloads, making deployment risk-averse.

## Subtheme 5: Overlay Architectures and Domain-Specific Hardware

An *overlay* is a soft processor or soft accelerator implemented on the FPGA fabric — a virtual machine layer that makes the FPGA look like a different kind of programmable device. Overlays trade some efficiency for dramatically better programmability: instead of running the full place-and-route toolchain (which takes minutes to hours), you program the overlay in a high-level language and the overlay's fixed datapath executes it.

The archetypal FPGA overlay for ML is a systolic array: a grid of processing elements where data flows in a regular pattern (matrix rows from the left, column weights from the top, partial sums accumulate rightward). A systolic array overlay can be programmed at the matrix operation level without re-synthesizing the FPGA; new model weights are simply loaded as new configuration data for the overlay's memories.

FCCM 2025 shows overlays being applied to emerging architectures: Kolmogorov-Arnold Networks (KANs, which replace fixed activation functions with learnable spline functions), state space models (Mamba, RWKV, which replace transformer attention with recurrent dynamics), and multi-modal inference pipelines where different modalities (text, vision, audio) need different compute patterns that can be scheduled onto overlay tiles. The research question is always the same: how close can you get to hand-optimized HDL efficiency while maintaining the programmability that makes overlays useful?

## How the Pieces Fit Together

The FCCM 2025 corpus reveals a field in the middle of a bet. The bet is that FPGAs will become the preferred inference substrate for edge ML as model sizes stabilize and as quantization makes models small enough to fit on FPGA HBM. This would make the toolchain investment (better HLS, better routing) worthwhile for a large enough market.

The pieces connect in a clear chain: better HLS (Subtheme 2) makes it feasible to implement custom sparse (Subtheme 3) and approximate arithmetic; better physical design optimization (Subtheme 4) makes those implementations meet timing; overlay architectures (Subtheme 5) let the deployed hardware be reprogrammed for new models without re-synthesis; and LLM inference applications (Subtheme 1) provide the demand that justifies all of it.

The tension is between the two ends of this chain. The HLS and physical design work requires FPGA expertise and does not transfer to other hardware. The LLM inference work requires ML expertise and could alternatively run on GPUs or on an ASIC for the same task. The justification for FPGAs — low-power, low-latency, customizable edge inference — is real but narrower than the full-scale training and large-batch inference market that dominates GPU investment.

## What Remains Hard

- **Closing the HLS efficiency gap**: hand-written HDL consistently outperforms HLS-generated circuits by 2-5x. The gap has narrowed but not closed in 20 years of HLS research; it is not clear whether it can be closed without exposing the programmer to more hardware detail, defeating the purpose of HLS.
- **FPGA timing closure at scale**: building an accelerator that uses 90%+ of a large FPGA's resources and still closes timing (meets the target clock frequency after routing) remains a fragile art. Small changes to HLS pragmas or to the model being accelerated can trigger routing congestion that causes timing failures, and debugging these is opaque.
- **Multi-FPGA scaling**: a single FPGA has enough compute for a 7B-parameter model at INT4. A 70B model requires ten FPGAs. The communication infrastructure (PCIe or custom inter-FPGA links) needed to run inference across ten FPGAs without communication becoming the bottleneck is an open research problem.
- **Dynamic reconfiguration for multi-model serving**: deploying multiple models on one FPGA requires either a large enough overlay to fit all of them simultaneously, or the ability to partially reconfigure the FPGA fabric (replacing the accelerator for model A with the one for model B without resetting the whole chip). Partial reconfiguration exists but adds configuration time overhead and requires careful design partitioning.
- **Benchmark standardization**: FCCM papers measure on a variety of FPGA boards, using different clock frequencies and resource budgets, making it difficult to compare across papers. The field lacks a standard inference benchmark suite for FPGAs analogous to MLPerf for GPUs.
