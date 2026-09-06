# Sky130 Two-Stage Preamp Latch Handoff

- status: `two_stage_preamp_latch_handoff_open`
- zero-input trim V: `-0.026906099999999933`
- passing cases: `1` of `2`

This test connects the measured-offset-trimmed two-stage transistor preamp to the transistor latch. The sample-side movement is currently reported from the preamp sense measurement and remains a limited kickback proxy.

| input diff mV | latch output diff V | polarity pass |
|---:|---:|---|
| `-1.5297058540778352` | `1.79389` | `False` |
| `1.5297058540778352` | `1.79567` | `True` |

## Refused Claim

does not prove statistical offset, noise, mismatch, physical preamp layout, DRC/LVS, SAR bit cycling, or accepted converter evidence
