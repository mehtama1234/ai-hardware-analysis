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
- cycle DAC values V: `[1.335721, 0.7428712, 0.6240692, 0.8088634]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.130259e-08, 7.018189e-08, 6.968551e-08], [6.834179e-08, 1.8, 6.834326e-08, 6.834351e-08], [6.834293e-08, 6.834378e-08, 1.8, 6.834404e-08], [6.833659e-08, 6.834137e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.865533, -0.864366, -0.8650916, -0.8654072, -0.8688394, -0.8648289, 0.8637653, -0.8660297, -0.868666, 0.8643414, -0.8666129, -0.8653412, -0.8687268, 0.8659963, 0.8658227, -0.8666528, -0.8674438, 0.8654609, 0.8668685, 0.86594]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
