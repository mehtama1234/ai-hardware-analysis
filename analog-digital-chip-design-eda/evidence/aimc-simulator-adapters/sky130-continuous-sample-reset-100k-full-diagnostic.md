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
- cycle DAC values V: `[0.3356201, 0.7998328, 0.5635992, 0.6819991]`
- cycle DAC legal range: `False`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.8, 7.620087e-08, 7.182607e-08, 6.999158e-08], [1.800001, 1.799999, 3.976697e-08, 5.46345e-08], [1.8, 6.841602e-08, 1.8, 6.835959e-08], [1.8, 6.770767e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8625921, 0.8618385, 0.8625398, 0.867049, 0.8655251, -0.8642468, 0.8642836, -0.8650705, 0.8654037, -0.863991, 0.8651978, 0.866364, 0.8665309, 0.8654204, 0.8646585, -0.865357, 0.867423, 0.8665287, 0.8653565, 0.8650505]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
