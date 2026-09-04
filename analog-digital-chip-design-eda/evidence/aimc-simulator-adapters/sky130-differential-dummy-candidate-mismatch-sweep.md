# Sky130 Differential Dummy Candidate Mismatch Sweep

- status: `sky130_differential_dummy_candidate_mismatch_sweep_characterized_not_converter_proof`
- topology: `fixed_dummy_0p50x_differential_transmission_gate_sample_hold_with_width_mismatch`
- case count: `5`
- measured case count: `5`
- timed out case count: `0`
- half LSB 12b V: `2.197265625e-04`
- worst differential hold abs delta V: `5.090000000e-05`
- differential hold pass count: `5` of `5`
- all measured cases pass differential hold: `True`
- candidate post-layout written: `False`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/sky130-differential-dummy-candidate-mismatch-sweep.csv`

## First Principle

Differential cancellation works only when the two sides make nearly the same error. A width mismatch breaks that equality. One side injects or removes a little more charge than the other, and the comparator sees the leftover difference.

This run keeps the passing 0.50x dummy candidate and scales the positive-side switch and dummy devices by small amounts. It is not a random mismatch model. It is a controlled stress test: how much does simple imbalance move the decision voltage?

## Results

| case | mismatch percent | acquired diff V | held diff V | differential hold delta V | passes half LSB |
|---|---:|---:|---:|---:|---|
| `matched_nominal` | `0.00` | `0.199652400` | `0.199693000` | `4.060000000e-05` | `True` |
| `positive_side_plus_1pct` | `1.00` | `0.199668700` | `0.199704000` | `3.530000000e-05` | `True` |
| `positive_side_minus_1pct` | `1.00` | `0.199637400` | `0.199683200` | `4.580000000e-05` | `True` |
| `positive_side_plus_2pct` | `2.00` | `0.199684100` | `0.199714400` | `3.030000000e-05` | `True` |
| `positive_side_minus_2pct` | `2.00` | `0.199621800` | `0.199672700` | `5.090000000e-05` | `True` |

## Reading

If the small mismatch rows fail, the candidate is fragile and needs layout symmetry, calibration, or a different sample event. If they pass, the next stress is noise and comparator tolerance. Either way, this is still schematic-level evidence, not post-layout converter acceptance.

## Refused Claim

does not prove random mismatch statistics, comparator offset, noise, SAR conversion, extracted layout, DRC/LVS signoff, or accepted replacement economics
