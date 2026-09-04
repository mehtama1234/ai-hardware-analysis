# Sky130 Sample-Hold Design Target

- status: `sky130_sample_hold_design_target_has_one_passing_decision_voltage_not_converter_proof`
- half LSB 12b V: `2.197265625e-04`
- best measured source: `sky130-differential-dummy-candidate-input-sweep`
- best measured hold error V: `6.300000000e-05`
- best measured passes half LSB 12b: `True`
- required reduction from best measured x: `0.287`
- remaining margin from best measured x: `3.488`
- required cancellation percent from best measured: `0.00`
- required capacitance multiplier if charge is unchanged: `0.287`
- estimated capacitance pF if starting from 1 pF: `0.287`
- candidate post-layout written: `False`
- accepted post-layout written: `False`

## First Principle

The hold error is voltage movement on a capacitor. If the unwanted charge stays the same, voltage movement falls only when capacitance rises. If capacitance stays the same, the only way to pass is to cancel or avoid most of the unwanted charge.

That gives the next design a hard target. If the best measured result is still above the line, the circuit needs less injected charge, more capacitance, or both. If the input-sweep result is below the line, the next question changes: the circuit must prove the same behavior under mismatch, noise, energy accounting, and layout extraction.

## Measured Inputs

| measurement | source | hold error V | reduction needed to reach half LSB |
|---|---|---:|---:|
| `plain_hold_worst` | `sky130-sample-switch-hold-mode-ngspice` | `5.557000000e-03` | `25.291x` |
| `larger_cap_best` | `sky130-sample-switch-hold-mitigation-sweep` | `2.107000000e-03` | `9.589x` |
| `dummy_cancellation_best` | `sky130-sample-switch-dummy-cancellation-ngspice` | `1.481300000e-03` | `6.742x` |
| `clock_edge_mid_input_baseline` | `sky130-sample-switch-clock-edge-sweep` | `1.049100000e-03` | `4.775x` |
| `differential_dummy_decision_voltage` | `sky130-differential-dummy-cancellation-ngspice` | `4.060000000e-05` | `0.185x` |
| `differential_dummy_input_sweep_worst` | `sky130-differential-dummy-candidate-input-sweep` | `6.300000000e-05` | `0.287x` |
| `differential_dummy_mismatch_sweep_worst` | `sky130-differential-dummy-candidate-mismatch-sweep` | `5.090000000e-05` | `0.232x` |

## What This Means

The best measured decision-voltage movement is `6.300000000e-05`. The 12-bit half-LSB line is `2.197265625e-04`.

The best measured row has `3.49x` margin against the half-LSB line.

That does not make it an accepted converter. It makes it the next candidate front end. It has cleared the nominal low, mid, and high input gate, but it still needs mismatch checks, comparator tolerance, noise, supply energy, and extracted layout before it can support a converter replacement claim.
The controlled width-mismatch sweep also passes in its tested cases. That still does not model random mismatch statistics or post-layout parasitics. It moves the next proof to noise, comparator tolerance, supply energy, and extraction.

## Refused Claim

does not prove comparator behavior, SAR conversion, mismatch tolerance, noise tolerance, extracted layout, DRC/LVS signoff, or accepted replacement economics
