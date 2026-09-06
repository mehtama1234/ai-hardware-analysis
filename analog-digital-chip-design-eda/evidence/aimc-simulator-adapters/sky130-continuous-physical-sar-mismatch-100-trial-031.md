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
- cycle DAC values V: `[1.33967, 0.7386577, 0.6259764, 0.8100021]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.132813e-08, 7.023879e-08, 6.971132e-08], [6.834138e-08, 1.8, 6.834323e-08, 6.834349e-08], [6.834285e-08, 6.834376e-08, 1.8, 6.834403e-08], [6.833653e-08, 6.834139e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655353, -0.8643487, -0.8650948, -0.8654032, -0.8688426, -0.8647372, 0.8637172, -0.8660456, -0.8686698, 0.8643967, -0.8665782, -0.8652284, -0.8687377, 0.865982, 0.8658463, -0.8665896, -0.8675123, 0.865425, 0.8668655, 0.8659879]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
