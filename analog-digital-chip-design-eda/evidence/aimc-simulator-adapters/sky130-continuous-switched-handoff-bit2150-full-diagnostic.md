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
- cycle DAC values V: `[1.26871, 0.8293498, 0.7221892, 0.5069131]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 9.096582e-08, 8.435401e-08, 7.314012e-08], [6.89971e-08, 1.8, 6.849234e-08, 6.838685e-08], [6.834102e-08, 6.834242e-08, 1.8, 6.834382e-08], [6.834685e-08, 6.834558e-08, 6.834526e-08, 1.8]]`
- comparator differences V: `[-0.8654888, -0.8647769, -0.8652911, -0.8647921, -0.8687859, -0.8661925, -0.8644682, 0.8647825, -0.8686151, -0.8637669, 0.865035, 0.8638271, -0.8684772, 0.8661915, -0.867001, 0.8664508, -0.8666787, 0.8664336, 0.8656042, -0.8666965]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
