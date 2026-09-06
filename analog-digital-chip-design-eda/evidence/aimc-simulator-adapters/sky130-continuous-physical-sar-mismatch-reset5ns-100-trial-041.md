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
- cycle DAC values V: `[1.343035, 0.7347568, 0.6138002, 0.7973658]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.083762e-08, 6.987718e-08, 6.94861e-08], [6.834097e-08, 1.8, 6.834323e-08, 6.834348e-08], [6.834327e-08, 6.834392e-08, 1.8, 6.834411e-08], [6.833709e-08, 6.834163e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655359, -0.8643311, -0.8650695, -0.8653559, -0.8688451, -0.8646066, 0.8640189, -0.8658958, -0.8686787, 0.8644658, -0.8664254, -0.8651563, -0.8687476, 0.865969, 0.8659136, -0.8664494, -0.8676403, 0.8654225, 0.8668581, 0.865998]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
