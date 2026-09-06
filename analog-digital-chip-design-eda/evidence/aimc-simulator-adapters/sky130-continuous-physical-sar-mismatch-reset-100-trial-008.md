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
- cycle DAC values V: `[1.350262, 0.7306125, 0.6221156, 0.805595]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.194352e-08, 7.066546e-08, 7.00355e-08], [6.834137e-08, 1.8, 6.834327e-08, 6.834352e-08], [6.834297e-08, 6.834382e-08, 1.8, 6.834406e-08], [6.833665e-08, 6.834153e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655484, -0.8643121, -0.8650862, -0.8653704, -0.8688478, -0.8645128, 0.8638402, -0.86601, -0.8686798, 0.8644846, -0.8664658, -0.8650987, -0.8687743, 0.865972, 0.8658731, -0.8665507, -0.8678052, 0.8654332, 0.8668752, 0.8658973]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
