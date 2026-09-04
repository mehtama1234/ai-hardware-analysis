# Sky130 Fully Differential Sampling Ngspice

- status: `sky130_fully_differential_sampling_characterized_not_converter_proof`
- topology: `matched_transmission_gate_differential_sample_hold_from_baseline`
- PDK model library: `/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice`
- generated deck: `labs/analog/analog-in-memory-foundation-model-hardware/spice/sky130_fully_differential_sampling.sp`
- case count: `1`
- measured case count: `1`
- timed out case count: `0`
- half LSB 12b V: `2.197265625e-04`
- worst single-node hold abs delta V: `1.934200000e-03`
- worst differential hold abs delta V: `2.086600000e-03`
- worst differential total abs error V: `1.721100000e-03`
- differential hold pass count: `0` of `1`
- differential total error pass count: `0` of `1`
- candidate post-layout written: `False`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/sky130-fully-differential-sampling-ngspice.csv`

## First Principle

A comparator does not care about one stored node by itself. It decides from the difference between two nodes. If clock feedthrough moves both nodes in the same direction, the common movement can disappear from the decision voltage.

This fixture samples a positive and negative side with matched Sky130 transmission gates and the same clocks. It then measures both the single-node movement and the differential movement. The important number is the differential hold error, because that is what a later comparator would see.

This is still not a converter. It has no comparator offset, no noise, no SAR loop, no mismatch sweep, and no extracted layout. It is a focused test of whether differential sampling is a better next front-end direction than single-ended holding.

## Results

| case | input diff V | acquired diff V | held diff V | p hold delta V | n hold delta V | differential hold delta V | differential total error V |
|---|---:|---:|---:|---:|---:|---:|---:|
| mid_diff_0p2 | `0.200000000` | `0.199634500` | `0.201721100` | `1.524000000e-04` | `1.934200000e-03` | `2.086600000e-03` | `1.721100000e-03` |

## Reading The Result

If the single nodes move but the difference barely moves, differential sampling is doing useful work. It does not make charge injection vanish. It makes the later decision less sensitive to the part of charge injection that is shared by both sides.

## Refused Claim

does not prove comparator offset, noise, SAR conversion, mismatch across devices, extracted transistor layout, DRC/LVS signoff, or accepted replacement economics
