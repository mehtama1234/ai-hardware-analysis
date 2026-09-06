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
- cycle DAC values V: `[0.4448679, 0.8072275, 0.6920662, 0.6325291]`
- cycle DAC legal range: `False`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.075585e-08, 6.988567e-08, 6.945777e-08], [1.8, 1.8, 6.378059e-08, 6.502929e-08], [1.8, 6.785875e-08, 1.8, 6.811844e-08], [1.8, 6.824598e-08, 6.828129e-08, 1.8]]`
- comparator differences V: `[-0.8635179, 0.8611226, 0.8629574, 0.8636993, 0.8649911, -0.8658927, -0.8634153, 0.8631956, 0.8646843, -0.8645654, 0.8648863, -0.8654532, 0.8647753, 0.8660002, -0.8666878, -0.86476, 0.8644115, 0.8668101, 0.865068, -0.8681474]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
