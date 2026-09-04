# Sky130 Preamp OP Latch Debug

- status: `preamp_op_latch_debug_failed`
- case count: `2`
- OP measured case count: `0`
- timed-out case count: `2`
- sign pass count: `0`
- output margin pass count: `0`
- minimum abs preamp output diff V: `0.000000000e+00`
- uses transient: `False`
- uses regenerative latch: `False`
- accepted post-layout written: `False`

## First Principle

The transient preamp debug timed out. Before changing the latch, the smaller question is whether the same preamp has a valid DC operating point at the target-edge inputs.

If the OP point passes, the bias is basically plausible and the transient problem is startup or initial condition. If the OP point fails, the preamp bias itself is the next repair.

## Results

| case | OP measured | output diff V | gain V/V | sign pass | margin pass |
|---|---:|---:|---:|---:|---:|
| `negative_target_edge` | `False` | `not measured` | `not measured` | `False` | `False` |
| `positive_target_edge` | `False` | `not measured` | `not measured` | `False` | `False` |

## Boundary

does not prove transient settling, latch resolution, kickback, SAR bit cycling, noise, offset statistics, extracted layout, DRC/LVS, or accepted post-layout converter evidence
