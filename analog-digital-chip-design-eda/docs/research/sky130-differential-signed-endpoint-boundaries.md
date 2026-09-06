# Sky130 Differential Signed Endpoint Boundaries

Using the complete 1× calibration artifact and the injective reverse-rank map,
the endpoint source offset was swept with one physical SAR conversion at a
time.

| Expected endpoint | Offset | Result | Final LSB differential |
|---:|---:|---|---:|
| 0 | −100 mV | `0→1` | `+121.7 mV` |
| 7 | +20 mV | `7→6` | `−34.5 mV` |
| 7 | +50 mV | `7→6` | `−5.1 mV` |
| 7 | +60 mV | `7→7` | positive; pass |

The high endpoint has a narrow calibrated window: +60 mV flips only the LSB
boundary while preserving the first three decisions. The low endpoint still
fails after three correct clears because its final physical trial remains
positive even at −100 mV. Direct physical-code probing at the low endpoint
also found positive differential output across codes 0–15, showing that the
current differential transfer is not a single monotonic threshold ladder over
the required input range.

This is diagnostic evidence, not acceptance. It establishes that the next
repair must change the low-end common-mode/LSB transfer or add a signed
boundary calibration mechanism; a single global offset cannot close both
endpoints.

Named evidence:

- `evidence/aimc-simulator-adapters/sky130-differential-endpoint-code0-offset-minus100.json`
- `evidence/aimc-simulator-adapters/sky130-differential-endpoint-code7-offset-plus60.json`
