# MOAT: Securely Mitigating Rowhammer with Per-Row Activation Counters

**Venue:** ASPLOS · **Subtheme:** DRAM Row-Hammer Attack Mitigation

## What It Does

MOAT implements the JEDEC PRAC+ABO (Per-Row Activation Counting + Alert-Back-Off) Rowhammer mitigation standard as a proven, secure DRAM-side design. Instead of prior Panopticon's approach of maintaining multi-entry per-bank queues to track hot rows, MOAT replaces this with a minimal single-entry tracking register (Current Tracked Addr, or CTA) that always points to the row with the highest activation counter. Whenever a row reaches the ETH (Eligibility Threshold), MOAT triggers proactive mitigation during DRAM refresh cycles; when it hits the ATH (ALERT Threshold), the hardware enforces Alert-Back-Off: mandatory RFM (Refresh Forced Migration) cycles that prevent further hammering. The design maintains only two 7-byte registers per bank (CTA and Current Mitigated Addr/CMA) and a boundary-row counter register mechanism to safely reset row counters across refresh groups without losing integrity.

Critically, MOAT exposes and defeats the "Jailbreak" attack—a fundamental flaw in Panopticon where attackers exploit queuing behavior to hide high-activation-count rows, tricking the mitigation into permitting 9x more row activations (1,152) than the configured 128-activation threshold. MOAT's fixed-target design eliminates this vulnerability. The authors also analyze the "Ratchet" attack, which exploits inter-ALERT activation windows tolerated by JEDEC's ABO specification, and prove that with ATH=64, MOAT can safely tolerate a Rowhammer threshold of only 99 row activations—a 40x reduction from historical thresholds.

## The Key Result

On SPEC2017 and GAP benchmarks with ATH=64 configuration, MOAT incurs only 0.28% average slowdown versus an unprotected baseline, with <0.5% total DRAM energy increase despite 2.3% additional DRAM activations. Hardware overhead is minimal: 7 bytes of SRAM per bank. Rowhammer attack evaluation shows that while Panopticon fails catastrophically (allowing 1,152 activations), MOAT maintains a provably secure bound: under the Ratchet attack, ATH=64 safely tolerates TRH=99.

## Why This Approach

Rowhammer represents a fundamental DRAM vulnerability where repeated row activations within a refresh interval induce bit flips in adjacent rows, enabling privilege escalation and data theft. With thresholds dropping from 139K to 4.8K over the past decade and continuing to fall, DRAM-side in-silo mitigation is essential to avoid pervasive kernel compromises. MOAT addresses the gap between JEDEC's theoretical PRAC+ABO framework and real secure implementations: prior work (Panopticon) is provably broken. MOAT's single-entry design elegantly avoids Panopticon's queue-based information hiding; the Ratchet analysis quantifies JEDEC specification gaps (the inter-ALERT window) that impact tolerable thresholds. Alternative approaches like TRR (Targeted Row Refresh, DDR4) and DSAC require significantly higher SRAM overhead; MOAT trades single-entry tracking precision for minimal hardware while maintaining proven security against modern attacks.

## What It Leaves Open

- MOAT is restricted to ABO mitigation level 1 (single RFM per ALERT trigger), limiting ability to handle higher aggressiveness levels needed if thresholds fall below ~99.
- RowPress attacks (which exploit the refresh command path itself) are explicitly out of scope and not mitigated.
- No analysis of interaction with DDR5 error-correction codes (ECC) or on-DIMM thermal sensors that may affect mitigation policy.
- Scalability to much higher-density future DRAMs (e.g., HBM stacks) where even single-entry tracking per bank may become expensive is not addressed.
- Counter reset semantics across REFRESH groups introduce implicit ordering assumptions not proven against out-of-order external attackers.
