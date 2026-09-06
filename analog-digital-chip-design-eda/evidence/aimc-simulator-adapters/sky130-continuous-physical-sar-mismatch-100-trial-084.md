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
- cycle DAC values V: `[1.334405, 0.7385497, 0.6260016, 0.8106018]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.08883e-08, 6.996336e-08, 6.95089e-08], [6.834097e-08, 1.8, 6.834318e-08, 6.834346e-08], [6.834286e-08, 6.834376e-08, 1.8, 6.834403e-08], [6.833652e-08, 6.834136e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655325, -0.8643506, -0.8650959, -0.8654017, -0.8688383, -0.8647345, 0.8637164, -0.8660533, -0.8686631, 0.8644096, -0.8665837, -0.8652172, -0.8687189, 0.8659756, 0.8658503, -0.8665927, -0.8673901, 0.8654023, 0.8668637, 0.8659971]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
