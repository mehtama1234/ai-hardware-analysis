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
- cycle DAC values V: `[1.337775, 0.7363802, 0.6184566, 0.8032973]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.111548e-08, 7.007529e-08, 6.962024e-08], [6.83413e-08, 1.8, 6.834324e-08, 6.834349e-08], [6.834312e-08, 6.834386e-08, 1.8, 6.834408e-08], [6.83368e-08, 6.834149e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655314, -0.8643354, -0.8650801, -0.8653675, -0.868839, -0.8646453, 0.863922, -0.8659783, -0.8686742, 0.8644421, -0.8665104, -0.8652382, -0.8687394, 0.8659784, 0.8658617, -0.866617, -0.8675798, 0.8654478, 0.8668663, 0.8658621]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
