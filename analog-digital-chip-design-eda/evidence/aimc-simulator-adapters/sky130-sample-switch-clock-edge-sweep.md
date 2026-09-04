# Sky130 Sample Switch Clock Edge Sweep

- status: `sky130_sample_switch_clock_edge_pair_characterized_not_converter_proof`
- generated deck: `labs/analog/analog-in-memory-foundation-model-hardware/spice/sky130_sample_switch_clock_edge_sweep.sp`
- config count: `2`
- case count: `2`
- measured case count: `2`
- timed out case count: `0`
- ngspice timeout s: `180`
- half LSB 12b V: `2.197265625e-04`
- best config: `baseline_20ps_mid_input`
- best worst hold abs delta V: `1.049100000e-03`
- candidate post-layout written: `False`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/sky130-sample-switch-clock-edge-sweep.csv`

## First Principle

Clock feedthrough starts when the control voltage moves. A sharper edge moves charge quickly. A slower edge can spread that movement over time, but it also leaves the switch partly on for longer.

This page records two mid-input edge cases: the original 20 ps edge and a slower 100 ps edge. The earlier nine-case edge sweep was too slow to be a useful bridge step. Keeping a small measured pair is better than keeping a broad sweep that mostly proves timeout behavior.

## Config Summary

| config | edge ps | measured cases | timed out cases | worst hold delta V | hold pass count |
|---|---:|---:|---:|---:|---:|
| `baseline_20ps_mid_input` | `20.0` | `1` | `0` | `1.049100000e-03` | `0` |
| `slower_100ps_mid_input` | `100.0` | `1` | `0` | `1.060400000e-03` | `0` |

## Refused Claim

does not prove a complete sample-and-hold architecture, comparator behavior, SAR conversion, extracted layout, DRC/LVS signoff, or accepted replacement economics
