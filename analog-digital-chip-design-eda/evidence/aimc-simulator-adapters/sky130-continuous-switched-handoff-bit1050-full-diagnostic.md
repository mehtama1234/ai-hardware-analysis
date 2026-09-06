# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[1, 0, 1, 1]`
- retained logical bits: `[0, 1, 0, 0]`
- final code: `4`
- continuous PMOS/NMOS switch width um: `8.0` / `64.0`
- continuous PMOS bank: `8` parallel device(s)
- bottom diode clamp: `False` (area `1.0`)
- dead-time clamp: `False` (width `1.0` um)
- conversion ground precharge: `False` (2.0 ns)
- top dummy capacitor: `0.5p`
- transient step ps: `20.0`
- conversions measured/required: `5`/`5`
- conversion coverage complete: `True`
- all conversions correct: `False`
- measured: `True`
- cycle DAC values V: `[1.434608, 0.6286518, 0.9027866, 0.7686554]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 6.848211e-08, 6.848211e-08, 6.840839e-08], [6.834262e-08, 1.8, 6.834388e-08, 6.834409e-08], [6.833149e-08, 1.8, 1.8, 6.83427e-08], [6.833718e-08, 1.8, 6.834253e-08, 1.8]]`
- comparator differences V: `[-0.8656, -0.8640968, -0.8651353, -0.8649511, -0.8689155, 0.8637901, -0.8670567, -0.8654353, -0.8687463, 0.8650567, -0.8648508, 0.8652494, -0.8688643, 0.8653306, 0.8663962, 0.8659864, -0.8682762, 0.8644454, 0.8665067, 0.8668971]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
