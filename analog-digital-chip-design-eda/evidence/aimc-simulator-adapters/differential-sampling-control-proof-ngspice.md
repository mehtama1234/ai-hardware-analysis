# Differential Sampling Control Proof Ngspice

- status: `differential_sampling_control_proof_passed_topology_only_not_converter_proof`
- topology: `ideal_switch_differential_sampling_with_controlled_charge_injection`
- Sky130 transistor model used: `False`
- generated deck: `labs/analog/analog-in-memory-foundation-model-hardware/spice/differential_sampling_control_proof.sp`
- case count: `3`
- measured case count: `3`
- half LSB 12b V: `2.197265625e-04`
- worst differential hold abs delta V: `3.000000000e-04`
- differential hold pass count: `2` of `3`
- candidate post-layout written: `False`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/differential-sampling-control-proof-ngspice.csv`

## First Principle

A single held node is fragile because every extra bit of charge becomes voltage error. A differential decision is different. If both held nodes receive the same unwanted charge, both voltages move together and the difference stays almost unchanged.

This control proof removes the Sky130 transistor model and uses ideal switches. Then it injects a known amount of charge into both held nodes. When the injected charge is exactly common, the decision voltage barely moves. When one side gets extra charge, only that mismatch remains in the differential voltage.

That is the reason differential sampling is still the right direction even though the full Sky130 transistor fixture is not stable yet. The topology can reject shared disturbance. The transistor proof still has to show that the real devices create disturbance that is matched enough.

## Results

| case | target diff V | common injection mV | mismatch injection mV | acquired diff V | held diff V | p hold delta V | n hold delta V | differential hold delta V | pass |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| common_only_small_signal | `0.020000000` | `5.000` | `0.000` | `0.020000000` | `0.020000000` | `5.000000000e-03` | `5.000000000e-03` | `0.000000000e+00` | `True` |
| common_only_large_signal | `0.800000000` | `5.000` | `0.000` | `0.800000000` | `0.800000000` | `5.000000000e-03` | `5.000000000e-03` | `1.110223025e-16` | `True` |
| mismatched_injection | `0.200000000` | `5.000` | `0.300` | `0.200000000` | `0.199700000` | `5.000000000e-03` | `5.300000000e-03` | `3.000000000e-04` | `False` |

## Refused Claim

does not prove Sky130 transistor behavior, comparator offset, noise, SAR conversion, extracted layout, DRC/LVS signoff, or accepted replacement economics
