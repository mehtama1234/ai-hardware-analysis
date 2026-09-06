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
- cycle DAC values V: `[1.342324, 0.7409851, 0.622789, 0.8077559]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.169092e-08, 7.041983e-08, 6.987764e-08], [6.834196e-08, 1.8, 6.83433e-08, 6.834353e-08], [6.834296e-08, 6.83438e-08, 1.8, 6.834405e-08], [6.833659e-08, 6.834141e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655367, -0.8643571, -0.8650888, -0.8654134, -0.8688447, -0.8647891, 0.8637987, -0.8660145, -0.8686731, 0.8643587, -0.8665631, -0.865318, -0.8687479, 0.8659938, 0.8658534, -0.8665936, -0.8675761, 0.8654588, 0.8668656, 0.865978]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
