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
- cycle DAC values V: `[1.344239, 0.7391814, 0.6182468, 0.8005969]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.1818e-08, 7.04857e-08, 6.991517e-08], [6.834222e-08, 1.8, 6.834334e-08, 6.834356e-08], [6.834312e-08, 6.834386e-08, 1.8, 6.834409e-08], [6.833698e-08, 6.834157e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655391, -0.8643449, -0.8650796, -0.8653585, -0.8688416, -0.8647184, 0.8639261, -0.8659413, -0.8686741, 0.864383, -0.866537, -0.8652724, -0.8687599, 0.8660002, 0.8658283, -0.8666202, -0.8677085, 0.8655009, 0.86688, 0.865846]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
