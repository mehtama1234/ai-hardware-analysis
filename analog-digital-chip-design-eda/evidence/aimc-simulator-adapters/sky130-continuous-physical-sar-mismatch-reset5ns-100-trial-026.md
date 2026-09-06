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
- cycle DAC values V: `[1.34355, 0.7363241, 0.6172035, 0.7984922]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.118032e-08, 7.010499e-08, 6.962333e-08], [6.834137e-08, 1.8, 6.834326e-08, 6.834351e-08], [6.834315e-08, 6.834387e-08, 1.8, 6.834409e-08], [6.833713e-08, 6.834164e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655363, -0.8643351, -0.8650781, -0.8653446, -0.8688457, -0.8646439, 0.8639494, -0.8659123, -0.8686795, 0.8644407, -0.8664906, -0.8651501, -0.8687529, 0.8659791, 0.8658738, -0.8665127, -0.8676688, 0.8654505, 0.866865, 0.8659467]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
