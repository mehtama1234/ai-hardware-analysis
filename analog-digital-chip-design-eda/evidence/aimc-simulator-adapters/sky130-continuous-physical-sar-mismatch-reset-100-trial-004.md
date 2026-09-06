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
- cycle DAC values V: `[1.334721, 0.7400022, 0.6220418, 0.8048454]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.135901e-08, 7.023449e-08, 6.970241e-08], [6.834176e-08, 1.8, 6.834327e-08, 6.834353e-08], [6.834299e-08, 6.834381e-08, 1.8, 6.834406e-08], [6.833681e-08, 6.834146e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655373, -0.8643511, -0.8650868, -0.8653549, -0.8688445, -0.8647376, 0.863838, -0.8660002, -0.8686636, 0.864382, -0.8666086, -0.8652842, -0.8687301, 0.8659965, 0.8657797, -0.8667223, -0.8675407, 0.8654912, 0.8668832, 0.8657589]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
