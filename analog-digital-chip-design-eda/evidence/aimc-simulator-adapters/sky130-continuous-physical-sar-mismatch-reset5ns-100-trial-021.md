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
- cycle DAC values V: `[0.4484044, 0.8130714, 0.6926789, 0.6335941]`
- cycle DAC legal range: `False`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.101912e-08, 7.001855e-08, 6.95524e-08], [1.8, 1.8, 6.318657e-08, 6.460191e-08], [1.8, 6.7869e-08, 1.8, 6.812801e-08], [1.8, 6.824288e-08, 6.828065e-08, 1.8]]`
- comparator differences V: `[-0.8635373, 0.8611211, 0.8629576, 0.8637031, 0.8649995, -0.8659778, -0.8634378, 0.8631626, 0.8646987, -0.8647279, 0.8648785, -0.8654182, 0.8646205, 0.8659681, -0.8667513, -0.8647695, 0.8644221, 0.8668228, 0.8650086, -0.8681572]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
