# Sky130 Extracted Frontend Latch Coupling Comparison

The connected extracted-frontend-to-latch runner was applied to three physical frontend candidates:

| candidate | standalone role | latch-connected result | sense bias before evaluation |
|---|---|---:|---:|
| balanced | sign-preserving starter | `1/2` polarities | about `16.7 mV` |
| strong | higher sample-to-sense coupling | `1/2` polarities | about `9.1 mV` |
| ultra | highest tested sample-to-sense coupling | `1/2` polarities | about `0.7 mV` |

The connected artifacts are:

- [balanced result](../../evidence/aimc-simulator-adapters/sky130-balanced-extracted-latch-kickback.json)
- [strong result](../../evidence/aimc-simulator-adapters/sky130-strong-extracted-latch-kickback.json)
- [ultra result](../../evidence/aimc-simulator-adapters/sky130-ultra-extracted-latch-kickback.json)

## First-Principles Reading

Increasing coupling improves the extracted sense transfer, but it does not establish a valid latch interface. In all three connected tests, the positive and negative input cases produce the same final output polarity. The latch input devices and their parasitic environment dominate the tiny differential before the decision is made.

This rules out “add more coupling” as the complete repair. The next physical object must isolate the sense nodes from the latch input capacitance or actively regenerate the sense difference before the latch. That buffer must itself be extracted and tested for input loading, common-mode range, both polarity directions, and kickback.

## Boundary

These are connected transient diagnostics, not accepted converter evidence. They do not prove offset, noise, mismatch, DRC/LVS, SAR bit cycling, full converter behavior, or post-layout energy/area economics. The sample-side sources are ideal, so the zero reported sampled-node movement is not a complete source-impedance kickback result.
