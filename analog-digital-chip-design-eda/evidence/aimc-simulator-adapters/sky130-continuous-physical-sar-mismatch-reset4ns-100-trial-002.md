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
- cycle DAC values V: `[0.4565948, 0.817943, 0.6957961, 0.6415189]`
- cycle DAC legal range: `False`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.113139e-08, 7.006711e-08, 6.961607e-08], [1.8, 1.8, 6.319711e-08, 6.452524e-08], [1.8, 6.792315e-08, 1.8, 6.815074e-08], [1.8, 6.822888e-08, 6.827276e-08, 1.8]]`
- comparator differences V: `[-0.8635766, 0.8611262, 0.8629687, 0.8637125, 0.8650209, -0.8660444, -0.8635612, 0.8629441, 0.8647304, -0.8648513, 0.8648471, -0.8654832, 0.8648487, 0.8659423, -0.8667513, -0.8648269, 0.8644441, 0.866831, 0.8650178, -0.868154]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
