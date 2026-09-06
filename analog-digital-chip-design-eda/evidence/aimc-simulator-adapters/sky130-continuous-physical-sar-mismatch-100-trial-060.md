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
- cycle DAC values V: `[1.354839, 0.7365847, 0.6191533, 0.8019613]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.177514e-08, 7.046272e-08, 6.992096e-08], [6.834167e-08, 1.8, 6.83433e-08, 6.834353e-08], [6.834307e-08, 6.834385e-08, 1.8, 6.834408e-08], [6.833684e-08, 6.834158e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655439, -0.864339, -0.8650826, -0.8654024, -0.8688546, -0.8646919, 0.8638869, -0.8659343, -0.8686856, 0.8644115, -0.8664442, -0.8651691, -0.8687771, 0.8659802, 0.8659314, -0.8663626, -0.8677685, 0.8654253, 0.8668546, 0.8661244]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
