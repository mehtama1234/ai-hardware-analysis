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
- cycle DAC values V: `[1.336017, 0.7413436, 0.6168586, 0.8013594]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.126351e-08, 7.012368e-08, 6.966508e-08], [6.834185e-08, 1.8, 6.834329e-08, 6.834352e-08], [6.834318e-08, 6.834387e-08, 1.8, 6.834409e-08], [6.833692e-08, 6.83415e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655377, -0.8643568, -0.8650782, -0.8653681, -0.868846, -0.864767, 0.8639547, -0.8659515, -0.868665, 0.8643637, -0.866558, -0.8653523, -0.8687297, 0.8660021, 0.865822, -0.8666758, -0.8675529, 0.8654994, 0.8668798, 0.8658075]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
