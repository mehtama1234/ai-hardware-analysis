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
- cycle DAC values V: `[1.339302, 0.7397421, 0.619707, 0.804318]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.08336e-08, 6.98767e-08, 6.947785e-08], [6.834107e-08, 1.8, 6.834321e-08, 6.834346e-08], [6.834307e-08, 6.834384e-08, 1.8, 6.834407e-08], [6.833677e-08, 6.834146e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655348, -0.8643565, -0.8650854, -0.8654027, -0.8688423, -0.8647623, 0.8638725, -0.8659664, -0.8686687, 0.8643944, -0.8665134, -0.8652441, -0.8687324, 0.8659794, 0.8659009, -0.8664763, -0.867464, 0.8654108, 0.8668567, 0.866078]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
