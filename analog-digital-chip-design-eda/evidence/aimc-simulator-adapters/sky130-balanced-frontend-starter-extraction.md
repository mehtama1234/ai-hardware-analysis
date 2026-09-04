# Sky130 Balanced Frontend Starter Extraction

- status: `balanced_frontend_starter_extracted_not_comparator_proof`
- sense capacitance delta fF: `0.000000`
- required bias reduction factor: `144.33x`
- accepted ready now: `False`

## First Principle

The earlier extracted cell failed because the latch-gate nodes were not balanced measuring nodes. Before asking whether a latch can decide, the physical frontend must show that its two balanced measuring nodes see the same kind of surroundings.

This starter extraction checks only that first physical condition. It creates a named Sky130 Magic cell, extracts it, and measures the total capacitance connected to each sense node. Equal totals do not prove a comparator, but unequal totals would make the next proof meaningless.

## Files

| object | path | present | bytes |
|---|---|---:|---:|
| `magic_cell` | `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells/sky130_balanced_capacitive_isolation_frontend.mag` | `True` | `1087` |
| `magic_ext` | `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells/sky130_balanced_capacitive_isolation_frontend.ext` | `True` | `4953` |
| `extracted_spice` | `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/sky130_balanced_capacitive_isolation_frontend_extracted.spice` | `True` | `2849` |
| `extraction_tcl` | `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/extract-sky130_balanced_capacitive_isolation_frontend-smoke.tcl` | `True` | `398` |

## Extracted Ports

`vss vdd sample_p sense_p clk_sample vcm_reset clk_latch sense_n sample_n`

## Capacitance Totals

| node | total extracted capacitance fF |
|---|---:|
| `vss` | `4.326820` |
| `vdd` | `4.373310` |
| `sample_p` | `1.561190` |
| `sense_p` | `1.544460` |
| `clk_sample` | `1.809250` |
| `vcm_reset` | `1.828970` |
| `clk_latch` | `1.809330` |
| `sense_n` | `1.544460` |
| `sample_n` | `1.561190` |

## Refused Claim

does not prove sign preservation, does not include active reset devices, does not prove latch resolution, does not run DRC/LVS, and does not write accepted post-layout evidence
