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
- cycle DAC values V: `[1.339208, 0.7399994, 0.6248114, 0.8074315]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.117554e-08, 7.01257e-08, 6.962218e-08], [6.834138e-08, 1.8, 6.834322e-08, 6.83435e-08], [6.834289e-08, 6.834377e-08, 1.8, 6.834404e-08], [6.833669e-08, 6.834144e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655346, -0.8643554, -0.8650933, -0.8653883, -0.8688423, -0.8647674, 0.8637472, -0.8660108, -0.8686692, 0.864383, -0.8665838, -0.8652174, -0.8687358, 0.8659848, 0.8658455, -0.86656, -0.8674908, 0.8654296, 0.8668653, 0.8660142]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
