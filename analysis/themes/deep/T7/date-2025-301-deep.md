# Hardware/Software Runtime for GPSA Protection in RISC-V Embedded Cores

**Venue:** DATE · **Subtheme:** Fault-Attack Mitigation Without Recompilation

## What It Does

This work implements Generalized Path Signature Analysis (GPSA)—a control-flow integrity verification scheme—as a hardware/software co-design that protects unmodified, off-the-shelf RISC-V binaries from fault injection attacks without requiring compiler modifications or binary recompilation. The approach adds dedicated hardware monitoring logic to the RISC-V core that observes every instruction execution and computes GPSA signatures: cryptographic fingerprints of the instruction sequence and jump targets taken during program execution. These signatures are computed in real time on the executing path (not a static pre-computed path) and validated against expected signatures; any divergence (caused by a fault flipping an instruction or corrupting a jump address) triggers a security exception, halting execution before the fault can corrupt the system.

The key innovation is that the hardware monitors and generates signatures without requiring binary recompilation: the RISC-V processor maintains an internal model of expected control flow for any standard RISC-V binary. The monitoring is purely runtime-based, capturing indirect jumps (JAL, JALR, branches with register targets) that prior compiler-based approaches could not protect. The hardware/software interface uses a small RISC-V extension to configure which memory regions are protected and to define signature boundaries (e.g., function entry/exit points).

## The Key Result

On a RISC-V embedded implementation, GPSA protection incurs 3.35× average slowdown and 1.86× area overhead for the monitoring and signature-computation logic. Despite the overhead, the system successfully protects unmodified binaries against fault injection attacks, supporting indirect jumps which prior CFI methods do not protect. The design demonstrates that comprehensive fault-attack defense is achievable without disrupting existing software supply chains.

## Why This Approach

Embedded systems and IoT devices are frequent targets for fault injection attacks: physical attacks (EM/laser pulses, power transients) induce bit flips in registers or memory, allowing attackers to bypass authentication, skip security checks, or corrupt cryptographic keys. Traditional countermeasures require compiler modifications (e.g., inserting software redundancy checks) or binary rewriting, both of which break compatibility with legacy code, complicate deployment, and introduce toolchain risks. GPSA-based hardware monitoring provides comprehensive protection without requiring software changes: any fault that alters the control-flow path (including indirect jumps) is detected. The hardware approach is inherently more reliable than software checks, which themselves can be faulted. RISC-V's modular ISA extension model makes adding GPSA hardware a clean architectural addition.

## What It Leaves Open

- The 3.35× slowdown may be prohibitive for latency-critical real-time systems; the paper does not discuss techniques for reducing overhead (e.g., selective protection, signature caching).
- Area overhead of 1.86× is significant; applicability to highly area-constrained embedded systems (microcontrollers) is unclear.
- Signature scheme details (hash function, key derivation) are not specified; crypto strength against advanced attackers with side-channel capabilities is not analyzed.
- No evaluation against higher-order fault attacks (e.g., multiple concurrent faults, EM glitching during signature computation itself).
- Generalization to other ISAs (ARM, x86) is not discussed; the design appears RISC-V-specific.
