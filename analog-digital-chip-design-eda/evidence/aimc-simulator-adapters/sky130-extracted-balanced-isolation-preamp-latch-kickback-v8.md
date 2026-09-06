# Sky130 Balanced Extracted Frontend Latch Kickback

- status: `balanced_extracted_frontend_latch_kickback_open`
- passing cases: `1` of `2`
- hard kickback limit V: `2.197265625e-04`

This is the first connected extracted-frontend-to-transistor-latch test. It is intentionally bounded and does not constitute converter signoff.

| input diff mV | sense diff after V | sampled kickback V | output diff V | polarity pass |
|---:|---:|---:|---:|---|
| `-0.15297058540778352` | `0.03859239999999997` | `0.0` | `0.996533` | `False` |
| `0.15297058540778352` | `0.03860730000000001` | `0.0` | `0.996587` | `True` |

## Refused Claim

does not prove offset, noise, mismatch, DRC/LVS, SAR bit cycling, full converter behavior, or accepted post-layout economics
