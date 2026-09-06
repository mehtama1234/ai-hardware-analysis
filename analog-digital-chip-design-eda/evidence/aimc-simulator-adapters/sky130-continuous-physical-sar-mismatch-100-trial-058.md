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
- cycle DAC values V: `[1.340075, 0.7410734, 0.6228014, 0.8073995]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.141265e-08, 7.024883e-08, 6.974316e-08], [6.834168e-08, 1.8, 6.834326e-08, 6.834351e-08], [6.834296e-08, 6.83438e-08, 1.8, 6.834405e-08], [6.833663e-08, 6.834141e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655356, -0.8643585, -0.8650894, -0.8654077, -0.8688429, -0.8647908, 0.8637982, -0.8660096, -0.8686703, 0.8643637, -0.8665683, -0.8652999, -0.86874, 0.865991, 0.8658539, -0.8665842, -0.8675195, 0.8654482, 0.8668649, 0.8659915]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
