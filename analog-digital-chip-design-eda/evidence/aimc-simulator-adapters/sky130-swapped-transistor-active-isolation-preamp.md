# Sky130 Swapped Transistor Active Isolation Preamp

- status: `swapped_transistor_active_isolation_preamp_passed_schematic_not_layout_or_strict`
- setting count: `1`
- case count: `2`
- measured case count: `2`
- timed-out case count: `0`
- passing setting count: `1`
- first passing setting: `medium_iso_pair_8ua`
- best setting: `medium_iso_pair_8ua`
- best minimum abs corrected preamp output diff V: `7.932000000e-04`
- output margin target V: `5.000000000e-04`
- accepted post-layout written: `False`

## First Principle

The previous transistor isolation pair made enough output swing, but the corrected sign was inverted. That means the circuit did not fail like a weak amplifier. It failed like a handoff whose two sides are reversed.

This run keeps the extracted frontend, the isolation pair, and the preamp bias the same. The only circuit change is that the two isolation outputs feed the opposite preamp inputs. If this passes, the next work is to turn the polarity-corrected schematic into a layout candidate and measure the effects that schematic SPICE does not include.

## Setting Summary

| setting | iso width | iso tail uA | zero output mV | measured | corrected sign pass | corrected margin pass | min corrected output mV | min sense ratio |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `medium_iso_pair_8ua` | `2.000` | `8.000` | `13.786300` | `2` | `2` | `2` | `0.793200` | `1.013072` |

## Boundary

does not prove layout, DRC/LVS, offset stability over corners, noise, latch decision, SAR conversion, post-layout converter energy, or accepted converter evidence
