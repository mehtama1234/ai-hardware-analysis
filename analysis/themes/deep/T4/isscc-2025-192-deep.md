# 36.5 A Low-Latency 200Gb/s PAM-4 Heterogeneous Transceiver in 0.13µm SiGe BiCMOS and 28nm CMOS for Retimed Pluggable Optics

**Venue:** ISSCC · **Subtheme:** Low-Latency Physical Interconnect

## What It Does

This paper solves a fundamental conflict in AI data-center interconnects: 200G/lane serial links must transmit over very-short-reach (VSR) optical channels, which exhibit severe insertion loss (-14dB at 200Gbps). Traditional retimed solutions use analog-to-digital converters (ADCs) with digital signal processing (DSP) to compensate for channel loss, but DSP introduces pipeline delay — incompatible with ultra-low-latency AI inference. The paper proposes a heterogeneous transceiver that splits the burden: a 0.13µm SiGe BiCMOS analog front-end performs aggressive analog equalization (before ADC/DSP), while 28nm CMOS digital logic handles clock/data recovery and link-layer functions. The SiGe circuitry directly compensates the VSR insertion loss in the analog domain using precision equalization filters, eliminating the need for heavy DSP post-processing. 28nm CMOS handles the remaining clock synchronization and protocol overhead, which are latency-sensitive but computationally simpler. This split allows analog equalization to run in parallel with clock recovery, compressing overall receiver latency.

The data flow is: incoming 200Gbps PAM-4 signal → SiGe analog equalization front-end (compensates -14dB loss) → 28nm CMOS receiver (CDR, frame alignment, lane assembly) → AI cluster. By handling the highest-loss frequencies purely in analog, the architecture avoids the ADC quantization and DSP compute bottleneck, reducing end-to-end latency while maintaining link margin.

## The Key Result

200Gbps transmission rate over very-short-reach VSR optical channels with significantly lower latency than retimed DSP-based solutions. Energy efficiency is comparable to standard retimed approaches, but with near-zero additional latency penalty. This enables compliance with ultra-low-latency inference requirements (sub-microsecond fabric delays) while maintaining throughput density.

## Why This Approach

AI inference workloads are latency-bound — a few microseconds of unexpected delay can render inference results stale or cause request timeouts. Standard 200G pluggable optics with DSP compensation add 10-20 cycles of pipeline delay to recover from severe VSR channel loss, which violates inference SLA requirements. The heterogeneous approach exploits a key insight: analog circuits are inherently lower-latency for equalization than digital ADC+DSP chains (analog filters respond in nanoseconds; ADC sampling + DSP convolution adds microseconds). By using mature 0.13µm SiGe BiCMOS technology (proven for analog RF/analog front-ends in telecom) alongside 28nm CMOS (for clock recovery and protocol), the design leverages each process node's strengths. SiGe provides the high-frequency analog performance needed for VSR equalization; 28nm CMOS provides the power-efficient digital integration. The alternative — scaling a fully digital DSP solution to sub-microsecond latency or using higher-bandwidth channels with additional fiber count — does not address the fundamental latency-throughput tradeoff.

## What It Leaves Open

- No discussion of transceiver power consumption, area, or integration density compared to pure-digital retimed solutions or higher-bandwidth serial links (400G/lane).
- Reliability and equalization robustness across temperature, voltage, and process corners for the analog front-end are not explored; analog circuits are process-sensitive.
- Scalability from single 200G lane to multi-lane deserializers (16x 200G on a single chip) and how die-to-die or package-level heat dissipation affects analog equalization margin.
- Does not specify exact latency numbers (sub-microsecond claimed but no cycle count breakdown between SiGe equalization, CDR, and 28nm framing).
- No comparison of error rates or bit error ratio (BER) versus baseline retimed solutions across the full temperature/voltage envelope.
