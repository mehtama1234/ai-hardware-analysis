# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_nominal_map_passed`
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
- all conversions correct: `True`
- measured: `True`
- cycle DAC values V: `[1.342737, 0.7389829, 0.6233688, 0.8068812]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.132055e-08, 7.020884e-08, 6.970177e-08], [6.834145e-08, 1.8, 6.834324e-08, 6.83435e-08], [6.834294e-08, 6.834379e-08, 1.8, 6.834405e-08], [6.833666e-08, 6.834145e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655366, -0.8643503, -0.8650905, -0.8654003, -0.8688451, -0.8647452, 0.8637848, -0.8660029, -0.8686728, 0.8643917, -0.8665463, -0.8652242, -0.868747, 0.8659834, 0.865869, -0.8665275, -0.8675624, 0.8654283, 0.8668627, 0.8660324]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
