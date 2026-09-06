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
- cycle DAC values V: `[1.339976, 0.7361354, 0.6201322, 0.8015032]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.097578e-08, 7.000124e-08, 6.953167e-08], [6.834119e-08, 1.8, 6.834322e-08, 6.83435e-08], [6.834305e-08, 6.834384e-08, 1.8, 6.834407e-08], [6.833699e-08, 6.834157e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655387, -0.8643375, -0.8652984, -0.8653477, -0.8688489, -0.86465, 0.8638837, -0.8659544, -0.8686684, 0.8644358, -0.8665313, -0.865146, -0.868743, 0.8659822, 0.8658407, -0.8665732, -0.8676113, 0.8654477, 0.8668774, 0.8659025]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
