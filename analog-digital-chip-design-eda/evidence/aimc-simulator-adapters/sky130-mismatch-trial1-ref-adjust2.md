# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
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
- all conversions correct: `False`
- measured: `True`
- cycle DAC values V: `[1.267094, 0.828865, 0.6139727, 0.8381226]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.8, 8.952014e-08, 7.782099e-08, 7.791023e-08], [6.895108e-08, 1.8, 6.842928e-08, 6.843011e-08], [6.834337e-08, 6.834384e-08, 1.8, 6.834407e-08], [6.833597e-08, 6.834014e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8654871, -0.8647641, -0.8650649, -0.8657085, -0.8688015, -0.8661132, 0.8645888, -0.8662466, -0.8687289, 0.8634034, -0.8674319, -0.8673588, -0.8684271, 0.8666748, 0.86666, -0.8673775, 0.8675952, -0.8678927, -0.86768, -0.8676813]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
