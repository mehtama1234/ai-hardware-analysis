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
- cycle DAC values V: `[1.336647, 0.7377769, 0.620993, 0.8032141]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.113813e-08, 7.010215e-08, 6.960529e-08], [6.834149e-08, 1.8, 6.834325e-08, 6.834351e-08], [6.834303e-08, 6.834382e-08, 1.8, 6.834407e-08], [6.833689e-08, 6.834151e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655344, -0.8643409, -0.8650822, -0.8653495, -0.8688379, -0.8646815, 0.8638586, -0.865978, -0.8686731, 0.8644243, -0.8665655, -0.8652068, -0.8687365, 0.8659838, 0.8658228, -0.8666453, -0.8675548, 0.8654616, 0.8668707, 0.8658376]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
