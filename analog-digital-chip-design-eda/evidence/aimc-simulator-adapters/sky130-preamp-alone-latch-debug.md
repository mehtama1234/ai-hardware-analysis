# Sky130 Preamp-Alone Latch Debug

- status: `preamp_alone_latch_debug_failed`
- case count: `2`
- measured case count: `0`
- timed-out case count: `2`
- sign pass count: `0`
- output margin pass count: `0`
- settled case count: `0`
- minimum abs preamp output diff V: `0.000000000e+00`
- maximum settling delta 1.6ns to 2.0ns V: `not measured`
- polarity contract: `converter_positive_input_is_negative_raw_preamp_output_diff`
- uses regenerative latch: `False`
- accepted post-layout written: `False`

## First Principle

The failed isolated-latch candidates mixed several possible causes. The preamp might not settle, the latch might not resolve, or the clocks might put the circuit into a bad state.

This run removes the regenerative latch. The only question is whether the preamp itself can turn the target-edge input into a stable signed voltage before the latch would normally be enabled.

## Results

| case | measured | preamp diff 1.2ns V | preamp diff 1.6ns V | preamp diff 2.0ns V | sign pass | margin pass | settled |
|---|---:|---:|---:|---:|---:|---:|---:|
| `negative_target_edge` | `False` | `not measured` | `not measured` | `not measured` | `False` | `False` | `None` |
| `positive_target_edge` | `False` | `not measured` | `not measured` | `not measured` | `False` | `False` | `None` |

## Boundary

does not prove latch resolution, kickback, SAR bit cycling, noise, offset statistics, extracted layout, DRC/LVS, or accepted post-layout converter evidence
