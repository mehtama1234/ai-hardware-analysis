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
- cycle DAC values V: `[1.339267, 0.7392769, 0.6193137, 0.8029433]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.153417e-08, 7.032211e-08, 6.979419e-08], [6.834189e-08, 1.8, 6.83433e-08, 6.834353e-08], [6.834309e-08, 6.834384e-08, 1.8, 6.834408e-08], [6.833685e-08, 6.83415e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.865538, -0.8643471, -0.8650819, -0.865365, -0.8688485, -0.864721, 0.863902, -0.8659737, -0.8686684, 0.8643871, -0.8665576, -0.8652952, -0.8687441, 0.8659979, 0.8658167, -0.8666697, -0.8676272, 0.865492, 0.8668806, 0.8658058]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
