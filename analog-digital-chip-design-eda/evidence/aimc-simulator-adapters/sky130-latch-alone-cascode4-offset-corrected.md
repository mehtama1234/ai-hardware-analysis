# Sky130 Latch-Alone From Preamp Voltage Debug

- status: `latch_alone_from_preamp_voltage_passed_ready_for_clock_timing`
- case count: `3`
- target case count: `2`
- calibration case count: `1`
- measured case count: `3`
- timed-out case count: `0`
- resolved correct polarity count: `2`
- minimum abs latch output diff V: `8.053000000e-03`
- uses ideal sources from measured preamp voltages: `True`
- uses sampled nodes: `False`
- accepted post-layout written: `False`

## First Principle

The preamp now settles by itself. The next smaller question is whether the latch can decide when the preamp is replaced by ideal voltage sources at those measured output values.

This removes sampled-node kickback and preamp loading. If this passes, the latch core can read the preamp voltage in principle. The next question becomes clock timing and then coupled kickback.

## Results

| case | measured | pre_p V | pre_n V | output diff V | resolved |
|---|---:|---:|---:|---:|---:|
| `negative_target_edge` | `True` | `2.037745500e-01` | `2.049655500e-01` | `1.373290000e+00` | `True` |
| `positive_target_edge` | `True` | `2.047918500e-01` | `2.047918500e-01` | `-8.053000000e-03` | `False` |
| `positive_target_edge` | `True` | `2.048185500e-01` | `2.039215500e-01` | `-1.373290000e+00` | `True` |

## Boundary

does not prove sampled-node kickback, coupled preamp/latch loading, SAR bit cycling, noise, offset statistics, extracted layout, DRC/LVS, or accepted post-layout converter evidence
