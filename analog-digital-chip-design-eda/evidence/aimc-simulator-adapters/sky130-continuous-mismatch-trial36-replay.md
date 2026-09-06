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
- cycle DAC values V: `[0.4176641, 0.7771945, 0.65246, 0.8319882]`
- cycle DAC legal range: `False`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.086881e-08, 6.99228e-08, 6.948271e-08], [1.8, 1.8, 6.350621e-08, 6.483565e-08], [1.8, 6.791091e-08, 1.8, 6.814742e-08], [1.8, 6.765916e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8634697, 0.8611283, 0.8629696, 0.8637208, 0.8648866, -0.8653524, 0.8629966, -0.8663272, 0.8644773, -0.8631768, 0.8652316, -0.8637513, 0.8644531, 0.8661732, -0.8652583, 0.8655996, 0.8642716, 0.8666375, 0.8662534, -0.8672853]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
