# Sky130 Known-Good-Shape Preamp Transient Latch Debug

- status: `known_good_shape_preamp_transient_passed_ready_for_latch_alone`
- case count: `2`
- measured case count: `2`
- timed-out case count: `0`
- sign pass count: `2`
- output margin pass count: `2`
- settled case count: `2`
- minimum abs preamp output diff V: `1.431600000e-03`
- maximum settling delta 1.6ns to 2.0ns V: `2.070000000e-05`
- uses known-good OP initial point: `True`
- uses regenerative latch: `False`
- accepted post-layout written: `False`

## First Principle

A DC operating point says a circuit has a place to rest. A transient run asks whether the circuit can get there from a stated starting state within the time available before the latch is enabled.

This run uses the OP-passing preamp shape and starts from the measured OP values. It keeps the latch disconnected. If it passes, the preamp is ready for a latch-alone driven-voltage check. If it fails, transient startup is still the blocker.

## Results

| case | measured | diff 1.2ns V | diff 1.6ns V | diff 2.0ns V | sign pass | margin pass | settled |
|---|---:|---:|---:|---:|---:|---:|---:|
| `negative_target_edge` | `True` | `-1.473900000e-03` | `-1.452300000e-03` | `-1.431600000e-03` | `True` | `True` | `True` |
| `positive_target_edge` | `True` | `1.473900000e-03` | `1.452300000e-03` | `1.431600000e-03` | `True` | `True` | `True` |

## Boundary

does not prove latch resolution, kickback, SAR bit cycling, noise, offset statistics, extracted layout, DRC/LVS, or accepted post-layout converter evidence
