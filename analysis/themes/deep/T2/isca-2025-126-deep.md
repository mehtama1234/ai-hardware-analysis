# AIM: Software and Hardware Co-design for Architecture-level IR-drop Mitigation in High-performance PIM

**Venue:** ISCA · **Theme:** IR-Driven Mixed-Precision

## What It Does

High-performance SRAM PIM chips operating at high frequency and density suffer severe IR-drop (up to 140 mV on a production 7nm 256-TOPS chip), which degrades performance and threatens reliability. Conventional circuit-level mitigations (power plane widening, decoupling capacitors, clock-tree slack management) are resource-intensive, compromise PPA, and are overly pessimistic because they target the signoff worst-case Rtog=100% rather than actual workload-driven IR-drop.

SRAM PIM is the leading candidate for commercial AI accelerators, but the IR-drop problem forces conservative V-f operating points that sacrifice energy efficiency and throughput; an architecture-level approach exploiting PIM's predictable, weight-stationary workloads can close this gap without expensive circuit-level redesign.

AIM introduces two architecture-level IR-drop metrics: Rtog (instantaneous toggle rate of bitstreams in a PIM bank, correlated with dynamic current) and HR (Hamming Rate — average fraction of '1' bits in quantized weights, the theoretical upper bound of Rtog). Software optimization reduces HR via (1) LHR (Lower Hamming Rate), a differentiable regularization term added to QAT loss that steers weights toward low-HR integer values; and (2) WDS (Weight Distribution Shift), which adds a constant offset delta offline to shift weights into low-HR positive ranges and corrects the numerical error via a pipelined shift compensator placed beside PIM macro banks. At runtime, IR-Booster extends DVFS with HR-aware V-f pair selection: pre-compiled HR bounds determine a safe operating level, while a hardware IR Monitor (VCO-based voltage detector embedded near LDOs) triggers IRFailure signals that drive fine-grained aggressive-level adjustment. Finally, an HR-aware simulated-annealing task mapping assigns operators to macro groups to minimize inter-group HR interference. Evaluated via post-layout simulation (RedHawk/HSPICE) on a 7nm 256-TOPS DPIM chip.

## The Key Experiment

- **speedup:** 1.152x on 7nm 256-TOPS SRAM PIM chip
- **energy or tops w:** 2.29x energy efficiency improvement
- **area:** <1% overhead from shift compensator hardware
- **ppa:** None
- **accuracy:** HR reduced 23-31% (LHR alone), up to 41-46% (LHR+WDS); accuracy loss <0.1% across ResNet18, MobileNetV2, YOLOv5, ViT, Llama3, GPT2
- **other:** IR-drop mitigated by up to 69.2% vs. worst-case signoff baseline

**Compared against:** Circuit-level DVFS baseline (signoff worst-case Rtog=100%); Graphcore Bow IPU (wafer-on-wafer DTC approach); Standard QAT without LHR/WDS

**Hardware:** CIM; ASIC · **Workloads:** CNN; transformer; LLM-inference

## Why This Approach

First architecture-level IR-drop mitigation for SRAM PIM that correlates weight Hamming Rate to dynamic IR-drop and co-optimizes quantization, weight distribution, runtime V-f control, and task mapping to exploit real workload IR-drop margins rather than worst-case circuit signoff.

This paper sits in the **quantization** subtheme. The core tension: lower precision = smaller model = less memory bandwidth, but at the cost of rounding error that compounds across layers. This paper's bet: Rtog and HR: two architecture-level metrics establishing a direct, quantifiable correlation between PIM workload weight statistics and IR-drop..

## What It Leaves Open

- Evaluation relies on post-layout simulation rather than silicon measurements
- IR-Booster's recomputing mechanism introduces pipeline stalls whose impact on end-to-end latency in production workloads is not fully quantified.

**Tags:** sram-pim, ir-drop, quantization, dvfs, weight-distribution, sw-hw-codesign
