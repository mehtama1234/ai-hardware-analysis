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
- cycle DAC values V: `[1.341803, 0.7377342, 0.6187373, 0.8014013]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.143568e-08, 7.026574e-08, 6.974735e-08], [6.834157e-08, 1.8, 6.834327e-08, 6.834352e-08], [6.83431e-08, 6.834385e-08, 1.8, 6.834408e-08], [6.833694e-08, 6.834155e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655387, -0.8643415, -0.8650812, -0.8653573, -0.8688463, -0.864686, 0.8639153, -0.8659525, -0.8686709, 0.8644081, -0.8665287, -0.8652331, -0.8687498, 0.8659917, 0.8658384, -0.8666056, -0.8676586, 0.8654754, 0.8668784, 0.8658664]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
