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
- cycle DAC values V: `[0.4554213, 0.8167928, 0.6982951, 0.6386213]`
- cycle DAC legal range: `False`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.142796e-08, 7.02836e-08, 6.973692e-08], [1.8, 1.8, 6.268221e-08, 6.425563e-08], [1.8, 6.781438e-08, 1.8, 6.810319e-08], [1.8, 6.823509e-08, 6.827544e-08, 1.8]]`
- comparator differences V: `[-0.8635628, 0.8611267, 0.8628064, 0.8637123, 0.8650184, -0.8660283, -0.8636594, 0.8630152, 0.8647296, -0.8648312, 0.8648163, -0.8655069, 0.8649932, 0.8659475, -0.8668051, -0.8647911, 0.8644427, 0.8668303, 0.8649748, -0.8681688]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
