# Sky130 Differential Rank-Map Endpoint Diagnostic

The 1× differential dummy calibration cleared the nominal 4-bit spacing
floor, but the affine nearest-threshold mapping still aliased endpoint codes.
This diagnostic replaced that affine map with the injective reverse rank map:
logical code `n` uses the `n`th measured physical threshold from the high end.

At the difficult expected-code-7 endpoint, all four physical comparisons
measured. The sequence was:

| Decision | Logical trial | Physical trial | Sign decision |
|---:|---:|---:|---|
| 1 | 8 | 7 | clear |
| 2 | 4 | 11 | keep |
| 3 | 6 | 9 | keep |
| 4 | 7 | 8 | clear |

The final logical result was `6`, not `7`. The first three decisions are
consistent with the desired endpoint trajectory; the LSB boundary has the
wrong sign at this source/common-mode point. Thus the differential failure is
now narrowed to comparator/input polarity or LSB threshold calibration, not
just a non-injective code map.

This remains a diagnostic, not converter acceptance. The next repair should
measure the LSB decision boundary with a signed input sweep and then retest
the same rank map across all five representative conversions.

Evidence: `evidence/aimc-simulator-adapters/sky130-thermometer-calibrated-physical-sar.json`.
