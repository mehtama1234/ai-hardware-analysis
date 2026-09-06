# Sky130 Latch-Alone From Preamp Voltage Debug

- status: `latch_alone_from_preamp_voltage_failed`
- case count: `3`
- measured case count: `3`
- timed-out case count: `0`
- resolved correct polarity count: `1`
- minimum abs latch output diff V: `1.373290000e+00`
- uses ideal sources from measured preamp voltages: `True`
- uses sampled nodes: `False`
- accepted post-layout written: `False`

## First Principle

The preamp now settles by itself. The next smaller question is whether the latch can decide when the preamp is replaced by ideal voltage sources at those measured output values.

This removes sampled-node kickback and preamp loading. If this passes, the latch core can read the preamp voltage in principle. The next question becomes clock timing and then coupled kickback.

## Results

| case | measured | pre_p V | pre_n V | output diff V | resolved |
|---|---:|---:|---:|---:|---:|
| `negative_target_edge` | `True` | `2.069412000e-01` | `2.017989000e-01` | `-1.373290000e+00` | `False` |
| `positive_target_edge` | `True` | `2.079585000e-01` | `2.016252000e-01` | `-1.373290000e+00` | `False` |
| `positive_target_edge` | `True` | `2.079852000e-01` | `2.007549000e-01` | `-1.373290000e+00` | `True` |

## Boundary

does not prove sampled-node kickback, coupled preamp/latch loading, SAR bit cycling, noise, offset statistics, extracted layout, DRC/LVS, or accepted post-layout converter evidence
