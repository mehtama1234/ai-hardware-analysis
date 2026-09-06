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
- cycle DAC values V: `[1.334735, 0.7468316, 0.6202064, 0.8035913]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.111985e-08, 7.001793e-08, 6.95722e-08], [6.83421e-08, 1.8, 6.83433e-08, 6.834353e-08], [6.834306e-08, 6.834382e-08, 1.8, 6.834407e-08], [6.833688e-08, 6.834144e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655327, -0.8643845, -0.8650854, -0.8653943, -0.8688385, -0.8649114, 0.8638577, -0.865957, -0.8686646, 0.8642881, -0.8666194, -0.8653863, -0.8687209, 0.8660073, 0.8658232, -0.8666198, -0.8674071, 0.865487, 0.8668683, 0.865973]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
