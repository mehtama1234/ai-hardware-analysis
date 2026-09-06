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
- cycle DAC values V: `[1.338555, 0.7392619, 0.6210687, 0.803846]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.157581e-08, 7.036442e-08, 6.980624e-08], [6.834191e-08, 1.8, 6.834329e-08, 6.834354e-08], [6.834302e-08, 6.834382e-08, 1.8, 6.834407e-08], [6.833683e-08, 6.834149e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655382, -0.864347, -0.8650848, -0.8653581, -0.8688484, -0.8647207, 0.8638617, -0.8659864, -0.8686675, 0.8643871, -0.8665813, -0.8652748, -0.8687424, 0.8659981, 0.8657976, -0.8666885, -0.8676119, 0.8654928, 0.8668822, 0.8657872]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
