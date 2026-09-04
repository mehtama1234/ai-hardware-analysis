# Sky130 Sample Switch Hold Mitigation Sweep

- status: `sky130_hold_mitigation_sweep_complete_not_converter_proof`
- PDK model library: `/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice`
- generated deck: `labs/analog/analog-in-memory-foundation-model-hardware/spice/sky130_sample_switch_hold_mitigation_sweep.sp`
- config count: `3`
- case count: `9`
- measured case count: `8`
- timed out case count: `1`
- ngspice timeout s: `60`
- half LSB 12b V: `2.197265625e-04`
- baseline worst hold abs delta V: `5.557000000e-03`
- plain hold-mode reference worst hold abs delta V: `5.557000000e-03`
- best config: `larger_cap_smaller_switch_1p0p_1x2`
- best worst hold abs delta V: `1.632500000e-03`
- best hold improvement x: `3.404`
- best improvement vs plain hold-mode x: `3.404`
- best total error pass count: `0`
- candidate post-layout written: `False`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/sky130-sample-switch-hold-mitigation-sweep.csv`

## First Principle

The held-node error is charge divided by capacitance. If the switch injects roughly the same unwanted charge into a larger sample capacitor, the voltage movement gets smaller. But a larger capacitor also costs energy and takes longer to charge. A smaller switch can inject less charge, but it also has more resistance and may settle more slowly.

This sweep tests that tradeoff directly with Sky130 MOS models. It does not solve the converter. It tells us whether the next design should spend capacitance, resize the switch, or move to a better sampling method.

## Config Summary

| config | Wn um | Wp um | Csample pF | measured cases | timed out cases | worst hold delta V | total error pass count |
|---|---:|---:|---:|---:|---:|---:|---:|
| `baseline_0p2p_2x4` | `2.000` | `4.000` | `0.200` | `3` | `0` | `5.557000000e-03` | `0` |
| `larger_cap_1p0p_2x4` | `2.000` | `4.000` | `1.000` | `3` | `0` | `2.107000000e-03` | `0` |
| `larger_cap_smaller_switch_1p0p_1x2` | `1.000` | `2.000` | `1.000` | `2` | `1` | `1.632500000e-03` | `0` |

## Reading

The best setting in this sweep is `larger_cap_smaller_switch_1p0p_1x2`. It changes worst hold movement by `3.404` times compared with the measured in-sweep baseline and by `3.404` times compared with the separate plain hold-mode reference. If it still misses the 12-bit half-LSB line, the next move is not just more capacitance. The circuit needs a sampling method that cancels or avoids switch charge movement.

## Refused Claim

does not prove a complete sample-and-hold architecture, comparator behavior, SAR conversion, extracted transistor layout, DRC/LVS signoff, or accepted replacement economics
