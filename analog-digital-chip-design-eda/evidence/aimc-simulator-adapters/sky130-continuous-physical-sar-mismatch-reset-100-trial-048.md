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
- cycle DAC values V: `[1.337901, 0.7423713, 0.6171124, 0.8002871]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.146887e-08, 7.024345e-08, 6.974463e-08], [6.834224e-08, 1.8, 6.834333e-08, 6.834355e-08], [6.834316e-08, 6.834387e-08, 1.8, 6.834409e-08], [6.8337e-08, 6.834153e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655382, -0.8643597, -0.8650782, -0.8653599, -0.868848, -0.8647888, 0.8639492, -0.8659368, -0.8686672, 0.8643468, -0.8665728, -0.8653517, -0.8687395, 0.8660077, 0.8658081, -0.8666759, -0.8675913, 0.8655154, 0.8668814, 0.8658034]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
