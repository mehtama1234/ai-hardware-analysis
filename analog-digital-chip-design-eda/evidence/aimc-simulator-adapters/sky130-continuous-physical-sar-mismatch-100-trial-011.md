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
- cycle DAC values V: `[1.341475, 0.7402774, 0.6236807, 0.8054771]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.122252e-08, 7.014362e-08, 6.963608e-08], [6.834147e-08, 1.8, 6.834324e-08, 6.834351e-08], [6.834293e-08, 6.834379e-08, 1.8, 6.834405e-08], [6.833679e-08, 6.834148e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655358, -0.8643564, -0.8650914, -0.8653833, -0.8688442, -0.8647738, 0.8637761, -0.865984, -0.8686716, 0.864378, -0.8665713, -0.865206, -0.8687425, 0.8659864, 0.8658538, -0.8665234, -0.8675296, 0.8654342, 0.8668644, 0.8660387]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
