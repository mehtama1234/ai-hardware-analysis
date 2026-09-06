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
- cycle DAC values V: `[1.344143, 0.7400224, 0.6239833, 0.8061105]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.155204e-08, 7.035159e-08, 6.979251e-08], [6.834176e-08, 1.8, 6.834327e-08, 6.834353e-08], [6.834292e-08, 6.834378e-08, 1.8, 6.834405e-08], [6.833673e-08, 6.834147e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655378, -0.8643536, -0.8650912, -0.8653891, -0.8688461, -0.8647682, 0.8637687, -0.8659928, -0.8686747, 0.8643737, -0.8665674, -0.8652228, -0.8687517, 0.8659893, 0.8658514, -0.8665367, -0.8675938, 0.8654458, 0.8668655, 0.8660223]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
