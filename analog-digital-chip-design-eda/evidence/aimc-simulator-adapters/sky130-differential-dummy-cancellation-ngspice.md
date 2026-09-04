# Sky130 Differential Dummy Cancellation Ngspice

- status: `sky130_differential_dummy_cancellation_characterized_not_converter_proof`
- topology: `matched_transmission_gate_differential_sample_hold_with_opposite_clock_dummy_devices`
- PDK model library: `/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice`
- generated deck: `labs/analog/analog-in-memory-foundation-model-hardware/spice/sky130_differential_dummy_cancellation.sp`
- case count: `3`
- measured case count: `3`
- timed out case count: `0`
- half LSB 12b V: `2.197265625e-04`
- baseline differential error V: `2.086600000e-03`
- best config: `dummy_0p50x`
- best differential hold abs delta V: `4.060000000e-05`
- best differential total abs error V: `3.070000000e-04`
- best improvement vs baseline x: `51.394`
- differential hold pass count: `1` of `3`
- candidate post-layout written: `False`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/sky130-differential-dummy-cancellation-ngspice.csv`

## First Principle

A differential comparator sees the distance between two stored voltages. Dummy devices can only help if they make the unwanted clock charge more equal on the two sides or reduce the difference created by switch turn-off.

The dummy device is not a second signal path. It is a controlled error source. It deliberately injects charge on the opposite clock edge so part of the real switch error is cancelled. If the dummy is too small, it does little. If it is too large, it creates a new error.

This run keeps the measured Sky130 differential transmission-gate fixture fixed and changes only the dummy-device scale. That makes the result a direct circuit question: does simple matched dummy cancellation reduce the decision-voltage movement enough to matter?

## Results

| config | dummy scale | acquired diff V | held diff V | differential hold delta V | differential total error V | passes half LSB |
|---|---:|---:|---:|---:|---:|---|
| `no_dummy` | `0.00` | `0.199634500` | `0.201721100` | `2.086600000e-03` | `1.721100000e-03` | `False` |
| `dummy_0p25x` | `0.25` | `0.199654800` | `0.200659700` | `1.004900000e-03` | `6.597000000e-04` | `False` |
| `dummy_0p50x` | `0.50` | `0.199652400` | `0.199693000` | `4.060000000e-05` | `3.070000000e-04` | `True` |

## Reading

If the best dummy row is still above the half-LSB line, then simple dummy sizing is not the converter answer. The next step must change the sampling event itself: timing, bottom-plate order, capacitance, switch topology, or comparator tolerance.

## Refused Claim

does not prove comparator offset, noise, SAR conversion, mismatch, extracted layout, DRC/LVS signoff, or accepted replacement economics
