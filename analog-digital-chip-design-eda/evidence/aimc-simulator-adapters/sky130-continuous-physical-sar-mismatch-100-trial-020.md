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
- cycle DAC values V: `[1.343275, 0.7412732, 0.6235279, 0.8071186]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.176937e-08, 7.047336e-08, 6.990012e-08], [6.834208e-08, 1.8, 6.834331e-08, 6.834354e-08], [6.834293e-08, 6.834379e-08, 1.8, 6.834405e-08], [6.833665e-08, 6.834143e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655372, -0.8643575, -0.8650899, -0.865404, -0.8688455, -0.8647952, 0.8637799, -0.8660063, -0.8686741, 0.8643531, -0.8665767, -0.8652947, -0.8687509, 0.8659956, 0.8658424, -0.8665876, -0.8675921, 0.8654642, 0.8668671, 0.8659814]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
