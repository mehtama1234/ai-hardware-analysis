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
- cycle DAC values V: `[1.338255, 0.7358158, 0.619256, 0.8035087]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.107809e-08, 7.006049e-08, 6.960084e-08], [6.834115e-08, 1.8, 6.834323e-08, 6.834348e-08], [6.834309e-08, 6.834385e-08, 1.8, 6.834408e-08], [6.83368e-08, 6.83415e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655383, -0.8643363, -0.8650829, -0.8653648, -0.8688482, -0.8646426, 0.8639038, -0.8659813, -0.868667, 0.8644398, -0.8665171, -0.8652122, -0.8687383, 0.8659809, 0.8658531, -0.8666084, -0.8675789, 0.8654447, 0.866876, 0.8658711]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
