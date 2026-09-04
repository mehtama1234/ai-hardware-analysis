# Sky130 Sample Switch Dummy Cancellation Ngspice

- status: `sky130_dummy_cancellation_sweep_complete_not_converter_proof`
- PDK model library: `/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice`
- generated deck: `labs/analog/analog-in-memory-foundation-model-hardware/spice/sky130_sample_switch_dummy_cancellation.sp`
- config count: `3`
- case count: `9`
- measured case count: `9`
- timed out case count: `0`
- ngspice timeout s: `20`
- half LSB 12b V: `2.197265625e-04`
- baseline config: `no_dummy_best_prior_1p0p_2x4`
- baseline worst hold abs delta V: `2.107000000e-03`
- best config: `dummy_0p50x_1p0p_2x4`
- best worst hold abs delta V: `1.481300000e-03`
- best hold improvement x: `1.422`
- best total error pass count: `1`
- candidate post-layout written: `False`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/sky130-sample-switch-dummy-cancellation-ngspice.csv`

## First Principle

When the switch turns off, the gate voltage moves quickly. Some of that movement couples through the MOS device capacitances into the stored node. The stored node is just charge on a capacitor, so a small injected charge becomes a voltage error.

A dummy device tries to inject charge with the opposite sign. It is not connected as a real signal switch. Its job is to let the clock edge push back on the stored node. This only works if the sign, size, and timing are close enough. Too little dummy charge does not cancel enough. Too much dummy charge pushes the error the other way.

This run tests that idea directly with Sky130 MOS models. It uses the best capacitor setting from the previous sweep as the baseline, then adds several dummy-device sizes. The result tells us whether simple cancellation is enough or whether the design must move to a stronger sampling topology.

## Config Summary

| config | dummy Wn um | dummy Wp um | Csample pF | measured cases | timed out cases | worst hold delta V | total error pass count |
|---|---:|---:|---:|---:|---:|---:|---:|
| `no_dummy_best_prior_1p0p_2x4` | `0.000` | `0.000` | `1.000` | `3` | `0` | `2.107000000e-03` | `0` |
| `dummy_0p25x_1p0p_2x4` | `0.500` | `1.000` | `1.000` | `3` | `0` | `1.569700000e-03` | `0` |
| `dummy_0p50x_1p0p_2x4` | `1.000` | `2.000` | `1.000` | `3` | `0` | `1.481300000e-03` | `1` |

## Reading

The best setting in this sweep is `dummy_0p50x_1p0p_2x4`. It changes worst hold movement by `1.422` times compared with the no-dummy baseline. The important question is not whether the table looks better; it is whether the held value reaches the 12-bit half-LSB line.

If the best row still misses that line, or if the dummy cases are not numerically well behaved enough to finish, simple dummy cancellation is not enough for this converter target. The next circuit move should be bottom-plate sampling or another timing method that disconnects the sensitive node before the largest clock-edge charge arrives.

## Refused Claim

does not prove a complete sample-and-hold architecture, comparator behavior, SAR conversion, extracted transistor layout, DRC/LVS signoff, or accepted replacement economics
