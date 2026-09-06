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
- cycle DAC values V: `[1.338753, 0.7378043, 0.6190921, 0.8032594]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.132634e-08, 7.020132e-08, 6.970837e-08], [6.834154e-08, 1.8, 6.834326e-08, 6.834351e-08], [6.834309e-08, 6.834385e-08, 1.8, 6.834408e-08], [6.833682e-08, 6.834149e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655383, -0.8643425, -0.865082, -0.865367, -0.8688485, -0.8646879, 0.8639072, -0.8659779, -0.8686675, 0.8644097, -0.8665366, -0.8652671, -0.8687413, 0.8659908, 0.8658344, -0.8666457, -0.8676017, 0.8654718, 0.8668786, 0.8658328]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
