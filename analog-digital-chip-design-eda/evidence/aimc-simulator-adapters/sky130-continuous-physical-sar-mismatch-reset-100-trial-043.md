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
- cycle DAC values V: `[0.4485549, 0.811494, 0.690282, 0.635731]`
- cycle DAC legal range: `False`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.058071e-08, 6.973563e-08, 6.937226e-08], [1.8, 1.8, 6.408412e-08, 6.51806e-08], [1.8, 6.798338e-08, 1.8, 6.81772e-08], [1.8, 6.824701e-08, 6.828361e-08, 1.8]]`
- comparator differences V: `[-0.8635329, 0.861125, 0.8629613, 0.8637068, 0.8650044, -0.8659596, -0.8633502, 0.8630974, 0.8646973, -0.8646664, 0.8649017, -0.8653968, 0.8647898, 0.865985, -0.8666564, -0.8647666, 0.8644177, 0.8668248, 0.8651159, -0.8681237]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
