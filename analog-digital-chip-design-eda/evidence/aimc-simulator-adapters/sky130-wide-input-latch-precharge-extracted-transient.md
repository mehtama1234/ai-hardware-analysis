# Sky130 Wide-Input Latch plus Precharge Extracted Transient

- status: `wide_input_latch_transient_open`
- measured cases: `4` of `4`
- passing cases: `2`

This runs the widened-sense physical variant after Magic extraction, using the exact six-device connectivity and parasitics with bounded structural MOS models.

| input differential mV | final output differential V | polarity | regenerated |
|---:|---:|---|---|
| `-10.0` | `0.906559` | `True` | `True` |
| `-0.5` | `0.864341` | `True` | `True` |
| `0.5` | `0.859558` | `False` | `True` |
| `10.0` | `0.809436` | `False` | `True` |

## Refused Claim

does not prove Sky130-model convergence, noise, mismatch, LVS, PVT yield, SAR conversion, or converter acceptance
