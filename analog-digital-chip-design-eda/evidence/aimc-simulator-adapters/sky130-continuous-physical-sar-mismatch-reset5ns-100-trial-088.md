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
- cycle DAC values V: `[1.347468, 0.7302005, 0.6226757, 0.8062902]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.173684e-08, 7.054411e-08, 6.993837e-08], [6.834127e-08, 1.8, 6.834325e-08, 6.834351e-08], [6.834295e-08, 6.834381e-08, 1.8, 6.834405e-08], [6.833663e-08, 6.834151e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655413, -0.8643087, -0.8650841, -0.8653667, -0.8688496, -0.8644868, 0.8638213, -0.8660196, -0.8686821, 0.8645021, -0.8664687, -0.8650779, -0.8687667, 0.8659627, 0.8658774, -0.8665578, -0.8677527, 0.8654176, 0.8668652, 0.8658957]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
