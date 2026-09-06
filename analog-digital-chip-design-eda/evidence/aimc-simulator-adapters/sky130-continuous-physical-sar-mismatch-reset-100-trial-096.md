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
- cycle DAC values V: `[0.4446661, 0.8070313, 0.6902108, 0.6340594]`
- cycle DAC legal range: `False`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.101559e-08, 7.003903e-08, 6.959081e-08], [1.8, 1.8, 6.358755e-08, 6.482732e-08], [1.8, 6.786607e-08, 1.8, 6.811951e-08], [1.8, 6.82253e-08, 6.82686e-08, 1.8]]`
- comparator differences V: `[-0.8635084, 0.8611241, 0.8629588, 0.8636992, 0.8649925, -0.8658973, -0.8633472, 0.8631488, 0.8646824, -0.8645646, 0.8648986, -0.8654554, 0.8647697, 0.8660038, -0.8666616, -0.8647609, 0.8644183, 0.866814, 0.8650993, -0.8681524]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
