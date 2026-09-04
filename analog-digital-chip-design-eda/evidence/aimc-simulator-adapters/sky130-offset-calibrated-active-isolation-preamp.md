# Sky130 Offset-Calibrated Active Isolation Preamp

- status: `offset_calibrated_active_isolation_macro_passed_not_transistor_layout_or_strict`
- setting count: `4`
- case count: `8`
- measured case count: `8`
- passing setting count: `1`
- first passing setting: `unity_noninverting_low_cin`
- best setting: `unity_noninverting_low_cin`
- best minimum abs corrected preamp output diff V: `6.100000000e-04`
- output margin target V: `5.000000000e-04`
- accepted post-layout written: `False`

## First Principle

A differential readout can be wrong even when it has large voltage swing, because a stable offset can move the zero point. The previous active-isolation macro made large outputs, but the raw zero point was shifted enough that one input sign looked like the other.

This run measures the zero-input output for each setting and subtracts it before judging sign and margin. That does not prove a real calibrated circuit. It tests whether the remaining problem is stable offset rather than missing signal.

## Setting Summary

| setting | gain | polarity | zero output mV | measured | corrected sign pass | corrected margin pass | min corrected output mV |
|---|---:|---:|---:|---:|---:|---:|---:|
| `unity_noninverting_low_cin` | `1.000` | `1` | `2.024300` | `2` | `2` | `2` | `0.610000` |
| `unity_inverting_low_cin` | `1.000` | `-1` | `-2.024300` | `2` | `0` | `2` | `0.610000` |
| `gain4_inverting_low_cin` | `4.000` | `-1` | `-8.092700` | `2` | `0` | `2` | `2.439200` |
| `gain12_inverting_low_cin` | `12.000` | `-1` | `-24.162600` | `2` | `0` | `2` | `7.296000` |

## Refused Claim

does not prove a transistor isolation circuit, drawn layout, offset stability, noise, DRC/LVS, latch decision, SAR conversion, post-layout converter energy, or accepted converter evidence
