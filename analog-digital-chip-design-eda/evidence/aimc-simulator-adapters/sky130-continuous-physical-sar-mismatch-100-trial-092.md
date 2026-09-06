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
- cycle DAC values V: `[1.334105, 0.7452193, 0.6255888, 0.8091077]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.143966e-08, 7.026568e-08, 6.972781e-08], [6.834225e-08, 1.8, 6.83433e-08, 6.834355e-08], [6.834288e-08, 6.834376e-08, 1.8, 6.834404e-08], [6.833663e-08, 6.834136e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655313, -0.8643753, -0.8650937, -0.8653983, -0.8688381, -0.8648778, 0.8637243, -0.8660337, -0.8686645, 0.864304, -0.8666652, -0.865369, -0.8687231, 0.8660059, 0.8657795, -0.8667089, -0.8674267, 0.8654882, 0.8668734, 0.865889]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
