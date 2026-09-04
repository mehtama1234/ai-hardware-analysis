# Sky130 Known-Good-Shape Preamp OP Latch Debug

- status: `known_good_shape_preamp_op_debug_passed_both_signs`
- known-good status: `known_good_reproduction_passed_for_known_and_measured_sense_inputs`
- failed OP status: `preamp_op_latch_debug_failed`
- repair hypothesis: `keep exact known-good OP deck shape; only extend it to both target-edge signs`
- case count: `2`
- OP measured case count: `2`
- timed-out case count: `0`
- sign pass count: `2`
- output margin pass count: `2`
- minimum abs preamp output diff V: `1.407600000e-03`
- uses known-good deck shape: `True`
- uses transient: `False`
- uses regenerative latch: `False`
- accepted post-layout written: `False`

## First Principle

When a smaller debug deck fails but an older similar deck passes, the first repair is not a new topology. The first repair is to remove accidental differences and keep the exact shape that already worked.

This run keeps the known-good OP preamp shape and only changes the sign of the target-edge input. If this passes, the preamp DC point is not the real blocker. The earlier OP failure is a deck-shape problem, and the next step is transient startup using the same known-good shape.

## Results

| case | OP measured | output diff V | gain V/V | sign pass | margin pass |
|---|---:|---:|---:|---:|---:|
| `negative_target_edge` | `True` | `-1.407600000e-03` | `9.201769` | `True` | `True` |
| `positive_target_edge` | `True` | `1.407600000e-03` | `9.201769` | `True` | `True` |

## Boundary

does not prove transient settling, latch resolution, kickback, SAR bit cycling, noise, offset statistics, extracted layout, DRC/LVS, or accepted post-layout converter evidence
