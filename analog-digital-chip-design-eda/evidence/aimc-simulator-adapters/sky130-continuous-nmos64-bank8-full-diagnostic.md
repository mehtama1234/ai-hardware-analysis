# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[1, 1, 1, 0]`
- retained logical bits: `[0, 0, 0, 1]`
- final code: `1`
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
- cycle DAC values V: `[1.320432, 0.8520809, 0.6220991, 0.5106312]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.747803e-08, 7.239112e-08, 7.025869e-08], [6.893102e-08, 1.8, 6.842598e-08, 6.838231e-08], [6.834616e-08, 6.834523e-08, 1.8, 6.834454e-08], [6.834945e-08, 6.834688e-08, 6.834559e-08, 1.8]]`
- comparator differences V: `[-0.8839739, -0.8767728, -0.8722108, -0.8676213, -0.8708081, -0.8687443, -0.865069, 0.8665852, -0.8681425, -0.8660884, 0.8671232, 0.866225, -0.8659648, 0.8665603, 0.8650783, -0.8651497, -0.8654881, 0.868648, 0.8666979, 0.8654896]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
