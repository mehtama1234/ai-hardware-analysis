# Sky130 Balanced Extracted Frontend Latch Kickback

- status: `balanced_extracted_frontend_latch_kickback_open`
- passing cases: `1` of `3`
- hard kickback limit V: `2.197265625e-04`

This is the first connected extracted-frontend-to-transistor-latch test. It is intentionally bounded and does not constitute converter signoff.

| input diff mV | sense diff after V | sampled kickback V | output diff V | polarity pass |
|---:|---:|---:|---:|---|
| `-0.15297058540778352` | `0.0764977` | `0.0` | `1.79925` | `False` |
| `0.0` | `0.07650539999999995` | `0.0` | `1.79925` | `False` |
| `0.15297058540778352` | `0.0765129` | `0.0` | `1.79925` | `True` |

## Refused Claim

does not prove offset, noise, mismatch, DRC/LVS, SAR bit cycling, full converter behavior, or accepted post-layout economics
