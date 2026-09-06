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
- cycle DAC values V: `[1.341137, 0.7398429, 0.622634, 0.8071815]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.131105e-08, 7.01918e-08, 6.970138e-08], [6.83415e-08, 1.8, 6.834325e-08, 6.83435e-08], [6.834297e-08, 6.83438e-08, 1.8, 6.834405e-08], [6.833663e-08, 6.834142e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655357, -0.8643538, -0.8650893, -0.8654073, -0.8688435, -0.8647642, 0.8638026, -0.8660066, -0.8686712, 0.8643805, -0.8665489, -0.865268, -0.8687424, 0.865986, 0.8658681, -0.8665519, -0.8675323, 0.8654345, 0.8668628, 0.866016]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
