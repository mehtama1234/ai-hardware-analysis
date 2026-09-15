# Sky130 Latch-Alone From Preamp Voltage Debug

- status: `latch_alone_from_preamp_voltage_failed`
- case count: `2`
- target case count: `2`
- calibration case count: `0`
- measured case count: `0`
- timed-out case count: `2`
- resolved correct polarity count: `0`
- minimum abs latch output diff V: `0.000000000e+00`
- uses ideal sources from measured preamp voltages: `True`
- uses sampled nodes: `False`
- accepted post-layout written: `False`

## First Principle

The preamp now settles by itself. The next smaller question is whether the latch can decide when the preamp is replaced by ideal voltage sources at those measured output values.

This removes sampled-node kickback and preamp loading. If this passes, the latch core can read the preamp voltage in principle. The next question becomes clock timing and then coupled kickback.

## Results

| case | measured | pre_p V | pre_n V | output diff V | resolved |
|---|---:|---:|---:|---:|---:|
| `negative_target_edge` | `False` | `not measured` | `not measured` | `not measured` | `False` |
| `positive_target_edge` | `False` | `not measured` | `not measured` | `not measured` | `False` |

## Boundary

does not prove sampled-node kickback, coupled preamp/latch loading, SAR bit cycling, noise, offset statistics, extracted layout, DRC/LVS, or accepted post-layout converter evidence
