# Sky130 Continuous SAR Banked-DAC Composition

The strongest existing continuous-DAC controls were combined in one full
five-conversion transient: an eight-device PMOS bank for high-side charging
and a `64 um` low-side NMOS device for bottom-plate discharge.

## Result

| Expected code | Final code | Bottom-plate range |
|---:|---:|---|
| 0 | 0 | pass |
| 2 | 1 | pass |
| 4 | 3 | pass |
| 6 | 6 | pass |
| 7 | 7 | pass |

The combined topology measures all five conversions, keeps every measured
bottom-plate node within the legal `0..1.8 V` range, and decodes `3/5`
representative workloads. It is an improvement over the default path, but it
is not a converter acceptance result because two codes remain wrong.

Evidence:

- `evidence/aimc-simulator-adapters/sky130-continuous-nmos64-bank8-full-diagnostic.json`

## Reference Sweep

For the expected code-2 conversion, reference values of `0.65`, `0.75`, and
`0.90 V` were tested on the same banked topology. They returned codes `0`, `1`,
and `1`, respectively. The measured trial levels remain approximately
`[1.49, 1.02, 0.79, 0.68] V`, so changing the reference does not independently
repair the retained-bit sequence.

Evidence:

- `evidence/aimc-simulator-adapters/sky130-continuous-nmos64-bank8-ref065-diagnostic.json`
- `evidence/aimc-simulator-adapters/sky130-continuous-nmos64-bank8-ref075-diagnostic.json`
- `evidence/aimc-simulator-adapters/sky130-continuous-nmos64-bank8-ref090-diagnostic.json`

## Decision

The banked/strong-low-side settings are retained as the best current legal
continuous-DAC baseline. The remaining failure is per-bit charge-transfer
trajectory and threshold shape, not simply bottom-plate rail excursion or a
single reference value. The next physical revision must change the MSB/bit
control topology and then repeat the complete five-conversion gate.
