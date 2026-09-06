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
- cycle DAC values V: `[1.337399, 0.7410425, 0.6244921, 0.8077203]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.115297e-08, 7.01034e-08, 6.96117e-08], [6.834144e-08, 1.8, 6.834323e-08, 6.834349e-08], [6.834291e-08, 6.834378e-08, 1.8, 6.834404e-08], [6.833667e-08, 6.834141e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655342, -0.8643595, -0.8650928, -0.8653948, -0.8688408, -0.8647899, 0.863755, -0.8660145, -0.8686674, 0.8643701, -0.8665948, -0.8652552, -0.8687304, 0.865988, 0.8658384, -0.8665878, -0.8674586, 0.8654373, 0.8668662, 0.8659948]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
