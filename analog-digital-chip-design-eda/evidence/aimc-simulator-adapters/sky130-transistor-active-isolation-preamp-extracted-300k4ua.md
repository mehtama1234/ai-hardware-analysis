# Sky130 Transistor Active Isolation Preamp

- status: `transistor_active_isolation_preamp_failed_schematic`
- setting count: `1`
- case count: `2`
- measured case count: `2`
- timed-out case count: `0`
- passing setting count: `0`
- first passing setting: `None`
- best setting: `extracted_300k_4ua`
- best minimum abs corrected preamp output diff V: `2.015000000e-04`
- output margin target V: `5.000000000e-04`
- accepted post-layout written: `False`

## First Principle

The ideal macro proved the shape of the answer: read the frontend lightly, subtract the zero-input offset, and ask whether both signs still exceed the margin. This run replaces that ideal gain block with a small Sky130 differential pair.

The important test is not whether the transistor pair produces any gain. It must do all three jobs together: keep the frontend sense ratio high, leave a calibratable zero point, and create corrected output margin for both signs.

## Setting Summary

| setting | iso width | iso tail uA | zero output mV | measured | corrected sign pass | corrected margin pass | min corrected output mV | min sense ratio |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `extracted_300k_4ua` | `2.000` | `4.000` | `3.281000` | `2` | `2` | `0` | `0.201500` | `0.124183` |

## Refused Claim

does not prove layout, DRC/LVS, offset stability, noise, latch decision, SAR conversion, post-layout converter energy, or accepted converter evidence
