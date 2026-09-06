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
- cycle DAC values V: `[1.346622, 0.7412225, 0.6218133, 0.8045816]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.182318e-08, 7.048889e-08, 6.991752e-08], [6.834219e-08, 1.8, 6.834332e-08, 6.834355e-08], [6.834299e-08, 6.834381e-08, 1.8, 6.834406e-08], [6.833678e-08, 6.834149e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655391, -0.8643573, -0.8650869, -0.8653993, -0.8688482, -0.8647947, 0.8638223, -0.8659714, -0.8686775, 0.8643518, -0.8665512, -0.8652768, -0.8687592, 0.8659962, 0.8658599, -0.8665313, -0.8676464, 0.8654664, 0.8668651, 0.866021]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
