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
- cycle DAC values V: `[1.337838, 0.7414111, 0.621758, 0.8030449]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.171266e-08, 7.044275e-08, 6.984531e-08], [6.834246e-08, 1.8, 6.834334e-08, 6.834358e-08], [6.8343e-08, 6.834381e-08, 1.8, 6.834406e-08], [6.833693e-08, 6.834151e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655315, -0.8643527, -0.8650822, -0.865348, -0.8688392, -0.864763, 0.8638401, -0.8659758, -0.8686749, 0.8643651, -0.8666221, -0.8652897, -0.8687419, 0.8659991, 0.8657756, -0.8667173, -0.8676094, 0.8655138, 0.866876, 0.8657556]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
