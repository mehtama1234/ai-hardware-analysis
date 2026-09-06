# Sky130 PMOS-Input Dynamic Latch

The existing latch used an NMOS input pair with high-output precharge. A structurally different candidate was tested: a PMOS input pair, low-output precharge, and cross-coupled PMOS/NMOS regeneration.

The extracted two-stage preamp drove the latch after a same-run zero-input trim. Both target cases completed, but only `1/2` resolved with the expected polarity. Regeneration reached full rail separation, so the failure is polarity dominance rather than timeout or insufficient output swing.

Evidence: [sky130-pmos-input-dynamic-latch.json](../../evidence/aimc-simulator-adapters/sky130-pmos-input-dynamic-latch.json).

## Decision

Changing the latch input-device polarity and output precharge level does not solve the interface. The next circuit must control input-referred offset and common-mode through a genuinely balanced preamplifier/calibration path before regeneration.

## Boundary

This is a schematic transistor architectural diagnostic. It does not prove noise, mismatch, statistical offset, sampled-node kickback, DRC/LVS, SAR conversion, or accepted converter evidence.
