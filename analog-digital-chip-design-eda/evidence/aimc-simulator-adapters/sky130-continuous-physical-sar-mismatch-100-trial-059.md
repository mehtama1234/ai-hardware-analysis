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
- cycle DAC values V: `[1.34357, 0.7404869, 0.6256249, 0.8081749]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.183792e-08, 7.054244e-08, 6.992678e-08], [6.834204e-08, 1.8, 6.83433e-08, 6.834354e-08], [6.834286e-08, 6.834376e-08, 1.8, 6.834404e-08], [6.833663e-08, 6.834143e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655368, -0.8643541, -0.8650933, -0.8653969, -0.8688457, -0.864778, 0.8637258, -0.8660213, -0.8686743, 0.8643625, -0.8665938, -0.8652539, -0.8687523, 0.8659935, 0.8658284, -0.8665956, -0.8676012, 0.8654597, 0.8668688, 0.8659739]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
