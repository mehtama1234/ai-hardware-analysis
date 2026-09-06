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
- cycle DAC values V: `[1.341312, 0.7373706, 0.6197798, 0.8028154]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.156185e-08, 7.035695e-08, 6.981117e-08], [6.834179e-08, 1.8, 6.834329e-08, 6.834353e-08], [6.834306e-08, 6.834384e-08, 1.8, 6.834407e-08], [6.833686e-08, 6.834152e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655349, -0.8643372, -0.8650793, -0.8653587, -0.8688434, -0.8646717, 0.8638875, -0.8659721, -0.8686777, 0.8644213, -0.8665359, -0.8652338, -0.8687511, 0.8659868, 0.8658383, -0.8666304, -0.8676586, 0.8654735, 0.8668698, 0.8658407]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
