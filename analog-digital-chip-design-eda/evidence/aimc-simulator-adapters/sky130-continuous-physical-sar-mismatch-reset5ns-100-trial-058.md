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
- cycle DAC values V: `[1.337532, 0.7388509, 0.6189789, 0.8031582]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.128395e-08, 7.016893e-08, 6.968447e-08], [6.834176e-08, 1.8, 6.834328e-08, 6.834352e-08], [6.83431e-08, 6.834385e-08, 1.8, 6.834408e-08], [6.833683e-08, 6.834149e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655316, -0.864344, -0.8650782, -0.8653647, -0.8688388, -0.8647062, 0.8639098, -0.8659766, -0.8686743, 0.8644061, -0.8665494, -0.8652889, -0.8687387, 0.86599, 0.8658323, -0.8666658, -0.8675892, 0.8654792, 0.8668701, 0.8658126]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
