# Sky130 Differential Dummy Candidate Input Sweep

- status: `sky130_differential_dummy_candidate_input_sweep_characterized_not_converter_proof`
- topology: `fixed_dummy_0p50x_differential_transmission_gate_sample_hold`
- case count: `3`
- measured case count: `3`
- timed out case count: `0`
- half LSB 12b V: `2.197265625e-04`
- worst differential hold abs delta V: `6.300000000e-05`
- worst differential total abs error V: `3.070000000e-04`
- differential hold pass count: `3` of `3`
- all measured cases pass differential hold: `True`
- candidate post-layout written: `False`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/sky130-differential-dummy-candidate-input-sweep.csv`

## First Principle

A passing middle input can hide a weak circuit. MOS switch charge, overdrive, and body behavior change with voltage. A candidate sample-and-hold front end has to keep the decision voltage still at low, mid, and high input levels, not only where the cancellation happens to line up.

This run fixes the best dummy size from the prior sweep and moves the common-mode input. The only question is whether the same cancellation still keeps the differential hold movement below the 12-bit half-LSB line.

## Results

| case | common mode V | input diff V | acquired diff V | held diff V | differential hold delta V | passes half LSB |
|---|---:|---:|---:|---:|---:|---|
| `low_cm_0p3_diff_0p2` | `0.300` | `0.200000000` | `0.200000000` | `0.199958900` | `4.110000000e-05` | `True` |
| `mid_cm_0p9_diff_0p2` | `0.900` | `0.200000000` | `0.199652400` | `0.199693000` | `4.060000000e-05` | `True` |
| `high_cm_1p5_diff_0p2` | `1.500` | `0.200000000` | `0.200000000` | `0.199937000` | `6.300000000e-05` | `True` |

## Reading

If all three rows pass, the candidate has cleared the first useful breadth gate. The next proof is mismatch and noise. If any row fails, the dummy size is not a general solution; it is only a local cancellation point.

## Refused Claim

does not prove comparator offset, noise, SAR conversion, mismatch, extracted layout, DRC/LVS signoff, or accepted replacement economics
