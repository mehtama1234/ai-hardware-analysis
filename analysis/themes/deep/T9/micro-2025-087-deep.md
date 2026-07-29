# Flexing RISC-V Instruction Subset Processors to Extreme Edge

**Venue:** MICRO · **Subtheme:** Extreme Edge Processors

## What It Does

Flexing proposes RISC-V Instruction Subset Processors (RISSPs)—custom processors generated automatically by selecting only the ISA instructions needed for a specific extreme-edge application (e.g., healthcare wearable, RFID tag, smart label). The methodology: (1) static analysis of application binary to count instruction frequencies, (2) automated instruction selection using a library of pre-verified Verilog macro units (ALU, load-store, branch, 16 instruction variants), (3) formal verification that the custom subset preserves correctness, and (4) synthesis to 28 nm or 65 nm technology.

For example, a healthcare monitor might use only add, sub, load, store, branch—eliminating multiply, divide, float. A temperature sensor might omit branches entirely. The generated RISSP fuses these units into a compact 2-stage pipeline, reducing area and power relative to full RISC-V cores (e.g., RiscyBoy, Rocket).

Data path: instruction fetch (ROM) → decode (instruction subset, eliminates unused decoders) → execute (only active ALU slices) → writeback.

## The Key Result

RISSPs reduce die area by 50–75% compared to minimal full-RISC-V cores and power by 40–60%. A healthcare monitor core achieves 1.2 GOPS in 0.05 mm² (28 nm), vs. 0.8 mm² for Rocket Core. On an RFID tag (65 nm), an RISSP runs at 100 MHz in <0.01 mm², consuming 1.5 mW—suitable for passive tag harvesting scenarios.

## Why This Approach

General-purpose processors waste area and power implementing instructions never used in specific applications. An RFID tag's firmware uses ~20 ISA instructions; a full RISC-V core implements 200+. By pruning unused instructions at design time, RISSPs eliminate decoder logic, ALU slices, and control structures, shrinking die area. This is critical for extreme edge devices (smart labels cost <$0.10, wearables <1 mm²) where area and power dominate cost and battery life.

## What It Leaves Open

- Instruction selection assumes static workloads; dynamic application switching (e.g., RFID reading multiple tag types) requires multi-mode processors
- Formal verification scales linearly with instruction count; verifying 200-instruction subset takes hours; unclear if approach scales to 1000+ instructions (RISC-V with extensions)
- Generalization to other ISAs (ARM Thumb, x86-64) requires new macro libraries; RISC-V modularity may not transfer
- Power gating and DVFS not explored; extreme edge often requires variable voltage for energy scavenging
- Compilation and debugging tools for custom subsets: standard RISC-V toolchains expect full ISA; retargeting GCC/LLVM not addressed

