# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_nominal_map_passed`
- expected code: `2`
- comparator clear flags: `[1, 1, 0, 1]`
- retained logical bits: `[0, 0, 1, 0]`
- final code: `2`
- continuous PMOS/NMOS switch width um: `8.0` / `64.0`
- continuous PMOS bank: `8` parallel device(s)
- bottom diode clamp: `False` (area `1.0`)
- dead-time clamp: `False` (width `1.0` um)
- conversion ground precharge: `False` (2.0 ns)
- top dummy capacitor: `0.5p`
- transient step ps: `20.0`
- conversions measured/required: `5`/`5`
- conversion coverage complete: `True`
- all conversions correct: `True`
- measured: `True`
- cycle DAC values V: `[1.346275, 0.7331555, 0.622375, 0.8074609]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.104903e-08, 7.006382e-08, 6.961193e-08], [6.834081e-08, 1.8, 6.83432e-08, 6.834346e-08], [6.834297e-08, 6.834381e-08, 1.8, 6.834405e-08], [6.833656e-08, 6.834146e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655393, -0.8643284, -0.8650896, -0.8654112, -0.8688478, -0.8646093, 0.8638121, -0.8660099, -0.8686759, 0.8644674, -0.8664493, -0.8651095, -0.8687536, 0.8659589, 0.865937, -0.8664029, -0.8675983, 0.8653646, 0.8668515, 0.8661141]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
