# Basilisk: A 34mm² End-to-End Open-Source 64-bit Linux-Capable RISC-V SoC in 130nm BiCMOS

**Venue:** HOTCHIPS · **Subtheme:** Open-Source Chip Design

## What It Does

Basilisk is a 34mm² 64-bit RISC-V processor designed end-to-end using open-source EDA tools (Yosys for synthesis, OpenROAD for place-and-route) in TSMC 28nm technology. The design flow: Verilog RTL → Yosys technology mapping → OpenROAD P&R with clock-tree synthesis → DRC-clean GDS. The SoC includes a dual-issue RISC-V core, caches, DRAM controller, and I/O subsystems. It boots Linux, runs userspace applications, and passes full compiler regression tests. The chip represents the first production-scale demonstration that open-source EDA can handle large, complex RTL (>50k lines) without commercial tools.

Data path flows through instruction fetch → decode → dual-issue execute → memory system, with open-source Yosys libraries replacing proprietary Synopsys/Cadence LUT mappings. OpenROAD's macro placement and SigmaGen clock-tree achieve timing closure at 1 GHz without manual floor-planning.

## The Key Result

Basilisk boots Linux on actual silicon, executing 4.5+ GFLOPS at 1 GHz in a 34mm² die (28nm). Compared to prior open-EDA chips (e.g., Google Efabless shuttle projects), Basilisk is 3x larger (supporting full OS) and demonstrates that open flows scale to production complexity. Total tool runtime <4 hours on standard workstations, compared to commercial flows requiring dedicated servers. PPA results in line with commercial baseline (Rocket Chip on TSMC 28nm).

## Why This Approach

Commercial EDA tools (Synopsys, Cadence) cost $100k+/year and have long licensing delays, blocking open-source chip design. Basilisk proves that open tools (Yosys + OpenROAD) have reached maturity for production chips, not just proof-of-concept. This enables researchers, startups, and developing countries to design and tape-out silicon without vendor lock-in. The end-to-end open flow is important because it closes the gap between academic research and manufacturable designs.

## What It Leaves Open

- Scaling to 5nm/3nm: current results on 28nm; advanced node characterization (FinFET variability, power delivery) not addressed
- Design-for-testability (DFT) and post-silicon debugging flows minimal; manufacturing yield and reliability on shuttle runs TBD
- Power integrity and thermal analysis simplified; realistic power gating and DVFS not demonstrated
- Security (side-channel resistance, hardware trojans) not hardened; open EDA enables reverse-engineering
- Parameterized generators for other ISAs (ARM, x86) or domain specialization (AI/ML) not explored
