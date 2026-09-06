# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[0, 1, 1, 0]`
- retained logical bits: `[1, 0, 0, 1]`
- final code: `9`
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
- cycle DAC values V: `[0.44444, 0.8060531, 0.692733, 0.6325718]`
- cycle DAC legal range: `False`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.09284e-08, 7.000836e-08, 6.954386e-08], [1.8, 1.8, 6.365265e-08, 6.494348e-08], [1.8, 6.7822e-08, 1.8, 6.810004e-08], [1.8, 6.824108e-08, 6.827766e-08, 1.8]]`
- comparator differences V: `[-0.8635149, 0.8611261, 0.8629569, 0.8636978, 0.86499, -0.8658764, -0.8634409, 0.863195, 0.8646829, -0.8645352, 0.8648798, -0.8654808, 0.8647738, 0.8660052, -0.8666905, -0.8647611, 0.8644106, 0.8668084, 0.8650624, -0.8681547]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
