# Sky130 Latch-Alone Swapped Preamp Voltage Debug

- status: `latch_alone_swapped_preamp_voltage_passed_ready_for_clock_timing`
- case count: `2`
- measured case count: `2`
- timed-out case count: `0`
- resolved correct polarity count: `2`
- minimum abs latch output diff V: `1.370960000e+00`
- uses swapped preamp voltage mapping: `True`
- accepted post-layout written: `False`

## First Principle

The prior latch-alone run did not look weak. It resolved hard, but with the opposite sign. That is a polarity-map failure, not a gain failure.

This run swaps the two measured preamp voltages before they drive the latch inputs. If both signs now resolve, the next clock-timing work should preserve this mapping explicitly.

## Results

| case | measured | pre_p V | pre_n V | output diff V | resolved |
|---|---:|---:|---:|---:|---:|
| `negative_target_edge` | `True` | `8.215952000e-01` | `8.201636000e-01` | `-1.370960000e+00` | `True` |
| `positive_target_edge` | `True` | `8.201636000e-01` | `8.215952000e-01` | `1.370960000e+00` | `True` |

## Boundary

does not prove sampled-node kickback, coupled preamp/latch loading, SAR bit cycling, noise, offset statistics, extracted layout, DRC/LVS, or accepted post-layout converter evidence
