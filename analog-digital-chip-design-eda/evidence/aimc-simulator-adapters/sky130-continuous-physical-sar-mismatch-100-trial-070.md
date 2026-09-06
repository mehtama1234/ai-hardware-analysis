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
- cycle DAC values V: `[1.352071, 0.7335538, 0.6238238, 0.8057206]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.151585e-08, 7.036804e-08, 6.980686e-08], [6.834117e-08, 1.8, 6.834324e-08, 6.83435e-08], [6.834291e-08, 6.83438e-08, 1.8, 6.834405e-08], [6.83367e-08, 6.834154e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655424, -0.864328, -0.8650911, -0.8653931, -0.8688523, -0.8646193, 0.8637758, -0.8659873, -0.8686824, 0.8644533, -0.8664696, -0.8650563, -0.8687704, 0.8659664, 0.8659173, -0.8663798, -0.8677169, 0.8653883, 0.866856, 0.8661189]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
