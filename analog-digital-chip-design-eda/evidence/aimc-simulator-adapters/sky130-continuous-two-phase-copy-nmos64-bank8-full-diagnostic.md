# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[0, 1, 0, 1]`
- retained logical bits: `[1, 0, 1, 0]`
- final code: `10`
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
- cycle DAC values V: `[0.3343309, 0.7974051, 0.5601638, 0.6779018]`
- cycle DAC legal range: `False`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.8, 7.619656e-08, 7.182416e-08, 6.999068e-08], [1.800001, 1.799999, 3.932219e-08, 5.442112e-08], [1.8, 6.841611e-08, 1.8, 6.835961e-08], [1.8, 6.769745e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8727632, 0.8726225, 0.8712531, 0.8713695, 0.872435, -0.8715104, 0.8692135, -0.8702765, 0.8728757, -0.8703593, 0.8702822, 0.8691078, 0.8745862, -0.8691271, 0.8716187, 0.8699617, 0.8750834, -0.8691191, 0.8716041, 0.8696398]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
