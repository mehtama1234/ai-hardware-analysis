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
- cycle DAC values V: `[1.350095, 0.7349661, 0.6156564, 0.7974207]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.152037e-08, 7.030703e-08, 6.9793e-08], [6.834166e-08, 1.8, 6.83433e-08, 6.834354e-08], [6.83432e-08, 6.83439e-08, 1.8, 6.83441e-08], [6.833713e-08, 6.834167e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.865542, -0.864328, -0.8650712, -0.8653508, -0.8688519, -0.8646107, 0.8639827, -0.8658969, -0.8686845, 0.8644491, -0.8664414, -0.8651462, -0.8687704, 0.8659788, 0.8659, -0.8664605, -0.8677757, 0.8654544, 0.8668625, 0.865975]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
