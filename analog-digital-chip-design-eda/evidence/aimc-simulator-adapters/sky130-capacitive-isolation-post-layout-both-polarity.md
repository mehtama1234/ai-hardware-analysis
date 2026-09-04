# Sky130 Capacitive Isolation Post-Layout Both-Polarity Rerun

- status: `extracted_rc_both_polarity_characterized_not_confirmed`
- extracted frontend: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/sky130_capacitive_isolation_frontend_extracted.spice`
- model include: `evidence/aimc-simulator-adapters/candidate-post-layout/models/sky130-capacitive-isolation-ngspice.includes`
- case count: `2`
- passing case count: `1`
- worst kickback V: `0.00010480000000001599`
- hard kickback limit V: `0.0002197265625`
- accepted ready now: `False`

## First Principle

The earlier pass used an ideal capacitor value in a generated schematic deck. This rerun uses the Magic-extracted RC frontend cell. That changes the question from whether a chosen capacitor value can work to whether this starter physical object still lets the latch read both signs without moving the sampled decision voltage too much.

This is still not accepted comparator evidence. The extracted cell is a starter physical object. It has parasitic capacitance and named ports, but it does not yet prove offset, noise, DRC/LVS, device matching, or a full SAR conversion loop.

The current result is useful because it separates two effects. The sampled-node kickback stays below the hard line, but the extracted frontend presents the same latch-gate sign for both input directions. The next diagnostic should test port mapping and physical symmetry before treating this as a comparator candidate.

## Results

| case | input diff mV | kickback V | hard limit V | output diff V | expected sign | measured sign | pass |
|---|---:|---:|---:|---:|---:|---:|---|
| `extracted_rc_negative_target` | `-0.152971` | `1.047000000e-04` | `2.197265625e-04` | `-1.366210000e+00` | `-1` | `-1` | `True` |
| `extracted_rc_positive_target` | `0.152971` | `1.048000000e-04` | `2.197265625e-04` | `-1.366210000e+00` | `1` | `-1` | `False` |

## Refused Claim

does not prove comparator offset, comparator noise, DRC/LVS, mismatch, SAR bit cycling, full converter behavior, or accepted replacement economics
