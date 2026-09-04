# Sky130 Bottom Plate Sampling Ngspice

- status: `sky130_bottom_plate_sampling_characterized_not_converter_proof`
- PDK model library: `/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice`
- generated deck: `labs/analog/analog-in-memory-foundation-model-hardware/spice/sky130_bottom_plate_sampling.sp`
- config count: `3`
- case count: `9`
- measured case count: `5`
- timed out case count: `4`
- half LSB 12b V: `2.197265625e-04`
- baseline config: `same_edge_top_and_bottom_off`
- baseline worst hold abs delta V: `7.677000000e-03`
- best config: `same_edge_top_and_bottom_off`
- best worst hold abs delta V: `7.677000000e-03`
- best hold improvement x: `1.000`
- best total error pass count: `0`
- candidate post-layout written: `False`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/sky130-bottom-plate-sampling-ngspice.csv`

## First Principle

A normal sample switch stores a voltage on one node. When the switch clock turns off, the clock edge can push charge straight into that same node. The stored number moves.

Bottom-plate sampling stores the voltage across a capacitor. One side of the capacitor sees the input. The other side is held at a known reference during sampling. The clock order matters because the side that is most sensitive should stop seeing the largest clock disturbance before the final switch edge injects charge.

This fixture measures the stored capacitor voltage, `v(top)-v(bottom)`, after different turn-off orders. It asks a narrow question: does clock ordering reduce held-value movement enough to justify building a stronger converter sample-and-hold around it?

## Config Summary

| config | top off ns | bottom off ns | measured cases | timed out cases | worst hold delta V | total error pass count |
|---|---:|---:|---:|---:|---:|---:|
| `same_edge_top_and_bottom_off` | `7.000` | `7.000` | `2` | `1` | `7.677000000e-03` | `0` |
| `top_opens_before_bottom_200ps` | `6.800` | `7.000` | `0` | `3` | `timeout` | `0` |
| `bottom_opens_before_top_200ps` | `7.000` | `6.800` | `3` | `0` | `1.096000000e-02` | `0` |

## Reading

The best measured clock order is `same_edge_top_and_bottom_off`. If its worst hold movement is still above the half-LSB line, the circuit still needs a stronger sample-and-hold design before it can feed a 12-bit converter claim.

## Refused Claim

does not prove comparator behavior, SAR conversion, extracted transistor layout, DRC/LVS signoff, converter energy, or accepted replacement economics
