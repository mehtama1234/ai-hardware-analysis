# Sky130 Transistor Active Isolation Preamp

- status: `transistor_active_isolation_preamp_failed_schematic`
- setting count: `3`
- case count: `6`
- measured case count: `6`
- timed-out case count: `0`
- passing setting count: `0`
- first passing setting: `None`
- best setting: `medium_iso_pair_8ua`
- best minimum abs corrected preamp output diff V: `2.383000000e-04`
- output margin target V: `5.000000000e-04`
- accepted post-layout written: `False`

## First Principle

The ideal macro proved the shape of the answer: read the frontend lightly, subtract the zero-input offset, and ask whether both signs still exceed the margin. This run replaces that ideal gain block with a small Sky130 differential pair.

The important test is not whether the transistor pair produces any gain. It must do all three jobs together: keep the frontend sense ratio high, leave a calibratable zero point, and create corrected output margin for both signs.

## Setting Summary

| setting | iso width | iso tail uA | zero output mV | measured | corrected sign pass | corrected margin pass | min corrected output mV | min sense ratio |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `tiny_iso_pair_2ua` | `0.420` | `2.000` | `2.353500` | `2` | `2` | `0` | `0.081700` | `0.091503` |
| `small_iso_pair_4ua` | `1.000` | `4.000` | `3.221400` | `2` | `2` | `0` | `0.031300` | `0.124183` |
| `medium_iso_pair_8ua` | `2.000` | `8.000` | `4.215400` | `2` | `2` | `0` | `0.238300` | `0.180392` |

## Refused Claim

does not prove layout, DRC/LVS, offset stability, noise, latch decision, SAR conversion, post-layout converter energy, or accepted converter evidence
