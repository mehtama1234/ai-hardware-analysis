# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[1, 0, 1, 1]`
- retained logical bits: `[0, 1, 0, 0]`
- final code: `4`
- continuous PMOS/NMOS switch width um: `8.0` / `8.0`
- continuous PMOS bank: `1` parallel device(s)
- bottom diode clamp: `False` (area `1.0`)
- dead-time clamp: `False` (width `1.0` um)
- conversion ground precharge: `False` (2.0 ns)
- top dummy capacitor: `0.5p`
- transient step ps: `20.0`
- conversions measured/required: `5`/`5`
- conversion coverage complete: `True`
- all conversions correct: `False`
- measured: `True`
- cycle DAC values V: `[0.6714449, 0.2318811, 0.7016873, 0.5767128]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.264437, 0.04613528, 0.0214658, 0.01035395], [0.08419484, 0.7303131, 0.01780275, 0.008746424], [0.003638624, 1.83068, 1.752081, -0.0001493534], [0.0008875435, 1.796489, 3.068084e-05, 1.799313]]`
- comparator differences V: `[-0.8700824, -0.8659675, -0.8649159, 0.8659309, -0.8686619, 0.8648132, -0.8686025, -0.8677841, -0.8686875, 0.8658728, -0.8667836, -0.8650965, -0.8650616, 0.8689918, 0.8652289, -0.8655095, -0.8650687, 0.8691286, 0.865308, -0.8654541]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
