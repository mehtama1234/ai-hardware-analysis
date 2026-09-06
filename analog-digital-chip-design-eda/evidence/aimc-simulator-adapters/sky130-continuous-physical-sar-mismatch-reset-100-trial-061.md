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
- cycle DAC values V: `[1.35245, 0.7277463, 0.6159184, 0.7973966]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.085725e-08, 6.993843e-08, 6.951013e-08], [6.834061e-08, 1.8, 6.834322e-08, 6.834349e-08], [6.834319e-08, 6.83439e-08, 1.8, 6.83441e-08], [6.833712e-08, 6.834172e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655442, -0.8643067, -0.8650781, -0.8653484, -0.8688498, -0.8644372, 0.863978, -0.8658967, -0.8686808, 0.8645313, -0.8663476, -0.8649206, -0.8687722, 0.8659225, 0.8659666, -0.8662875, -0.8677789, 0.8653707, 0.8668611, 0.8660937]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
