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
- cycle DAC values V: `[1.337014, 0.7354564, 0.6245393, 0.8107586]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.078939e-08, 6.990541e-08, 6.948565e-08], [6.834073e-08, 1.8, 6.834317e-08, 6.834344e-08], [6.83429e-08, 6.834378e-08, 1.8, 6.834404e-08], [6.833646e-08, 6.834137e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655334, -0.8643388, -0.8650938, -0.865414, -0.8688404, -0.8646634, 0.8637566, -0.8660546, -0.868667, 0.8644484, -0.8665192, -0.8651802, -0.8687264, 0.8659632, 0.8658978, -0.8665267, -0.8674287, 0.8653709, 0.866857, 0.8660446]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
