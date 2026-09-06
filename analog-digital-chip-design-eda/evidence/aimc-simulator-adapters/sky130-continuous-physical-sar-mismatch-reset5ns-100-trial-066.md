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
- cycle DAC values V: `[0.4376939, 0.8074136, 0.683735, 0.6267917]`
- cycle DAC legal range: `False`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.09528e-08, 6.996283e-08, 6.952895e-08], [1.8, 1.8, 6.325772e-08, 6.460108e-08], [1.8, 6.789146e-08, 1.8, 6.81371e-08], [1.8, 6.82325e-08, 6.827474e-08, 1.8]]`
- comparator differences V: `[-0.8634701, 0.8611258, 0.8629508, 0.8636869, 0.8649723, -0.8658956, -0.8631244, 0.86338, 0.8646535, -0.8645783, 0.8649561, -0.8652958, 0.8647298, 0.8659958, -0.8666782, -0.8647608, 0.8644025, 0.8668117, 0.865077, -0.8681548]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
