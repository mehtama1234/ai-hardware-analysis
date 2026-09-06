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
- cycle DAC values V: `[0.4461996, 0.8123622, 0.6866441, 0.63509]`
- cycle DAC legal range: `False`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.068776e-08, 6.977771e-08, 6.942044e-08], [1.8, 1.8, 6.374278e-08, 6.487275e-08], [1.8, 6.798779e-08, 1.8, 6.817941e-08], [1.8, 6.823227e-08, 6.827558e-08, 1.8]]`
- comparator differences V: `[-0.8635262, 0.8611213, 0.8629599, 0.8637019, 0.8649942, -0.8659672, -0.8632158, 0.8631178, 0.8646903, -0.864702, 0.864933, -0.8653551, 0.8645835, 0.8659715, -0.8666555, -0.8647948, 0.8644143, 0.86682, 0.8651096, -0.8681401]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
