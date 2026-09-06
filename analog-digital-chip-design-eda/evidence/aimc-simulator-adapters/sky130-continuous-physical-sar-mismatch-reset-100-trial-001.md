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
- cycle DAC values V: `[1.33913, 0.7363388, 0.6199575, 0.8047231]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.134694e-08, 7.023037e-08, 6.973012e-08], [6.834141e-08, 1.8, 6.834325e-08, 6.83435e-08], [6.834306e-08, 6.834384e-08, 1.8, 6.834407e-08], [6.833673e-08, 6.834147e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655379, -0.8643367, -0.8650834, -0.8653715, -0.8688485, -0.8646544, 0.8638881, -0.8659979, -0.8686679, 0.8644279, -0.866527, -0.8652486, -0.8687429, 0.865986, 0.8658401, -0.8666466, -0.8676124, 0.8654604, 0.8668779, 0.8658301]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
