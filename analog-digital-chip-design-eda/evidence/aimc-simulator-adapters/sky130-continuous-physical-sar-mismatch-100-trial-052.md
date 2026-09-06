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
- cycle DAC values V: `[1.345797, 0.7376056, 0.6255982, 0.8059141]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.13916e-08, 7.028122e-08, 6.971484e-08], [6.834139e-08, 1.8, 6.834323e-08, 6.834351e-08], [6.834286e-08, 6.834377e-08, 1.8, 6.834404e-08], [6.833679e-08, 6.834152e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655388, -0.8643447, -0.8650943, -0.8653747, -0.8688475, -0.8647141, 0.8637274, -0.8659907, -0.868676, 0.8644079, -0.8665568, -0.8651105, -0.868754, 0.8659792, 0.8658601, -0.8664776, -0.8676104, 0.8654183, 0.8668638, 0.8660646]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
