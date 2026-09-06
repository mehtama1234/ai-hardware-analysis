# Sky130 Extracted Frontend Two-Stage Preamp

- status: `two_stage_preamp_offset_corrected_margin_passed_not_layout_or_latch_proof`
- zero-input output offset V: `0.14681100000000002`
- corrected sign pass: `2` of `2`
- corrected margin pass: `2` of `2`

This is a transistor-level two-stage preamp diagnostic. Offset subtraction is a measured diagnostic, not a production calibration proof.

| input diff mV | stage-2 output diff V | corrected output diff V | sign pass | margin pass |
|---:|---:|---:|---|---|
| `-0.15297058540778352` | `0.14628799999999997` | `-0.0005230000000000512` | `True` | `True` |
| `0.0` | `0.14681100000000002` | `` | `` | `` |
| `0.15297058540778352` | `0.14840399999999998` | `0.0015929999999999556` | `True` | `True` |

## Refused Claim

does not prove calibrated offset statistics, noise, mismatch, latch kickback, DRC/LVS, SAR conversion, or accepted post-layout converter evidence
