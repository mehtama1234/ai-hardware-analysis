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
- cycle DAC values V: `[1.267097, 0.8288679, 0.6139693, 0.8381026]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 8.952023e-08, 7.782103e-08, 7.791027e-08], [6.895183e-08, 1.8, 6.842939e-08, 6.843022e-08], [6.834338e-08, 6.834384e-08, 1.8, 6.834407e-08], [6.833601e-08, 6.834016e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8654872, -0.8647641, -0.8650649, -0.8657085, -0.8687803, -0.8661897, 0.86397, -0.8663936, -0.8686013, -0.8637554, 0.8653509, 0.8637309, -0.868473, 0.8661916, 0.8645187, -0.8683397, -0.8666284, 0.8664313, 0.8667643, -0.8667186]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
