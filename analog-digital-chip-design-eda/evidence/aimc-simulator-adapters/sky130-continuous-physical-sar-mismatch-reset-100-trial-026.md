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
- cycle DAC values V: `[1.343721, 0.7365173, 0.6175082, 0.798827]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.118798e-08, 7.010975e-08, 6.962679e-08], [6.834137e-08, 1.8, 6.834326e-08, 6.834351e-08], [6.834314e-08, 6.834387e-08, 1.8, 6.834409e-08], [6.833711e-08, 6.834163e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655393, -0.8643379, -0.8650798, -0.8653475, -0.8688414, -0.8646583, 0.8639418, -0.8659169, -0.8686727, 0.8644277, -0.8665002, -0.8651608, -0.8687518, 0.8659851, 0.8658631, -0.8665228, -0.8676726, 0.8654563, 0.8668753, 0.8659391]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
