# Sky130 Two-Stage Preamp Latch Handoff

- status: `two_stage_preamp_latch_handoff_open`
- zero-input trim V: `-0.026708799999999977`
- passing cases: `1` of `2`

This test connects the measured-offset-trimmed two-stage transistor preamp to the transistor latch. The sample-side movement is currently reported from the preamp sense measurement and remains a limited kickback proxy.

| input diff mV | latch output diff V | polarity pass |
|---:|---:|---|
| `-0.15297058540778352` | `-1.79647` | `True` |
| `0.15297058540778352` | `-1.79633` | `False` |

## Refused Claim

does not prove statistical offset, noise, mismatch, physical preamp layout, DRC/LVS, SAR bit cycling, or accepted converter evidence
