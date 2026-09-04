# Sky130 Sample Switch Hold Mode Ngspice

- status: `sky130_sample_switch_hold_mode_characterized_not_converter_proof`
- PDK model library: `/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice`
- generated deck: `labs/analog/analog-in-memory-foundation-model-hardware/spice/sky130_sample_switch_hold_mode.sp`
- device models: `sky130_fd_pr__nfet_01v8, sky130_fd_pr__pfet_01v8`
- case count: `3`
- worst hold abs delta V: `5.557000000e-03`
- worst total abs error V: `5.557000000e-03`
- half LSB 12b V: `2.197265625e-04`
- hold delta pass count: `0` of `3`
- total error pass count: `0` of `3`
- candidate post-layout written: `False`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/sky130-sample-switch-hold-mode-ngspice.csv`

## First Principle

A sampled voltage is stored charge. Once the switch turns off, the sample node should stop following the input. But the switch gate still has capacitance to the sample node, and the channel charge has to go somewhere. That can push the held voltage up or down.

This fixture separates two questions. The earlier sample-switch run measured whether the sample node can follow the input while the switch is on. This run measures what happens after turn-off. If the held value moves too much, the next design work is not more software glue. It is circuit work: clock feedthrough reduction, charge cancellation, bottom-plate sampling, or a stronger sampling topology.

## Results

| case | input V | acquired V | held V | hold delta V | total error V | pass hold delta | pass total error |
|---|---:|---:|---:|---:|---:|---|---|
| low_hold | `0.300000000` | `0.300000000` | `0.295226800` | `-4.773200000e-03` | `4.773200000e-03` | `False` | `False` |
| mid_hold | `0.900000000` | `0.900136900` | `0.899087800` | `-1.049100000e-03` | `9.122000000e-04` | `False` | `False` |
| high_hold | `1.500000000` | `1.500000000` | `1.505557000` | `5.557000000e-03` | `5.557000000e-03` | `False` | `False` |

## Refused Claim

does not prove an ADC decision, comparator behavior, bottom-plate sampling fix, mismatch, noise, extracted transistor layout, DRC/LVS signoff, or accepted replacement economics
