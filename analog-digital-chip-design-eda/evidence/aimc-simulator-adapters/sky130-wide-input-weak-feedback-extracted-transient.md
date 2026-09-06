# Sky130 Wide-Input Weak-Feedback Extracted Transient

- status: `wide_input_weak_feedback_transient_open`
- measured cases: `4` of `4`
- passing cases: `1`

This is the extracted transient of the physical co-tuning candidate. It keeps the widened sense pair and lengthens the feedback gates.

| input differential mV | final output differential V | polarity | regenerated |
|---:|---:|---|---|
| `-10.0` | `0.720301` | `True` | `True` |
| `-0.5` | `0.379213` | `True` | `False` |
| `0.5` | `0.315743` | `False` | `False` |
| `10.0` | `-0.431665` | `True` | `False` |

## Refused Claim

does not prove Sky130-model convergence, noise, mismatch, LVS, PVT yield, SAR conversion, or converter acceptance
