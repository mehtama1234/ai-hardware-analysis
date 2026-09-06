# Sky130 Continuous SAR Split-MSB Diagnostic

The next physical revision split the `8 pF` MSB capacitor into two matched
`4 pF` plates with independent bottom-plate switches. The total MSB
capacitance is unchanged, so this experiment isolates charge-transfer
topology from DAC scaling. The branch is selected with
`AIMC_CONTINUOUS_SPLIT_MSB=1`; the original binary topology remains the
default.

## Measured result

| MSB timing | Expected code | Final code | Comparator decisions | DAC range | Bottom-plate range |
|---|---:|---:|---|---|---|
| simultaneous (`0 ns`) | 2 | 0 | `[1, 1, 1, 1]` | legal | fail |
| staggered (`0.25 ns`) | 2 | 0 | `[1, 1, 1, 1]` | legal | fail |

The one-conversion runs complete electrically and produce measurements, so
the split netlist and measurement contract are valid. However, splitting the
MSB does not repair the decision sequence: the code-2 case remains code 0 and
the bottom plates still show negative excursions. The five-conversion
staggered replay also encounters a late transient timestep failure, so it is
not a valid full-suite result.

Evidence:

- `evidence/aimc-simulator-adapters/sky130-continuous-split-msb-nmos64-bank8-single-nodelay-diagnostic.json`
- `evidence/aimc-simulator-adapters/sky130-continuous-split-msb-nmos64-bank8-single-diagnostic.json`
- `evidence/aimc-simulator-adapters/sky130-continuous-split-msb-nmos64-bank8-full-diagnostic.json`

## Decision

This split-MSB branch is rejected as the current acceptance candidate. It is
retained as a reproducible diagnostic option because it changes the physical
charge-transfer path without changing total capacitance. The best accepted
continuous-DAC baseline remains the banked PMOS / `64 um` low-side NMOS
configuration, which measures `3/5` representative codes with legal
bottom-plate voltages. The next redesign must address the comparator input
common-mode and per-bit redistribution trajectory rather than only dividing
the MSB capacitor.
