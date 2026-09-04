# Sky130 Latch Input-Size Kickback Sweep

- status: `sky130_latch_input_size_sweep_characterized_no_passing_width`
- topology: `coupled_differential_sample_hold_latch_with_swept_input_pair_width`
- target combined offset/noise mV: `0.1530`
- half LSB 12b V: `2.197265625e-04`
- baseline input width um: `10.0`
- baseline kickback V: `1.203400000e-02`
- best width um: `0.5`
- best kickback V: `6.578530000e-04`
- best improvement x: `1.829284050e+01`
- passing width count: `0`
- candidate post-layout written: `False`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/sky130-latch-input-size-kickback-sweep.csv`

## First Principle

The latch failed the coupled gate because it moved the sampled nodes. One direct cause is input capacitance. A wider input transistor has more gate capacitance and stronger coupling paths. Shrinking it should reduce kickback, but it can also weaken the latch input signal.

This sweep changes only the latch input-pair width. The question is whether a smaller input pair can still resolve the target-edge input while pushing less charge back into the sample-and-hold nodes.

## Results

| input width um | kickback V | half LSB V | output diff V | resolved | kickback pass |
|---:|---:|---:|---:|---|---|
| `10.0` | `1.203400000e-02` | `2.197265625e-04` | `1.310520000e+00` | `True` | `False` |
| `5.0` | `6.324480000e-03` | `2.197265625e-04` | `1.349140000e+00` | `True` | `False` |
| `2.0` | `2.598990000e-03` | `2.197265625e-04` | `1.364090000e+00` | `True` | `False` |
| `1.0` | `1.310680000e-03` | `2.197265625e-04` | `1.369650000e+00` | `True` | `False` |
| `0.5` | `6.578530000e-04` | `2.197265625e-04` | `1.371180000e+00` | `True` | `False` |

## Reading

If smaller input width lowers kickback but still misses the half-LSB line, the next circuit needs isolation, preamplification, or a sampled comparator input network. If a smaller width passes both resolution and kickback, it becomes the next candidate to test in both polarities and across input range.

## Refused Claim

does not prove comparator noise, mismatch, SAR bit cycling, extracted layout, DRC/LVS signoff, or accepted replacement economics
