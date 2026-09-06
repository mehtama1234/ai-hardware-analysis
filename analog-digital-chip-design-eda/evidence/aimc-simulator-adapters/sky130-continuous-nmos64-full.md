# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[1, 1, 0, 1]`
- retained logical bits: `[0, 0, 1, 0]`
- final code: `2`
- continuous PMOS/NMOS switch width um: `8.0` / `64.0`
- continuous PMOS bank: `1` parallel device(s)
- dead-time clamp: `False`
- conversion ground precharge: `False` (2.0 ns)
- top dummy capacitor: `0.5p`
- transient step ps: `20.0`
- conversions measured/required: `5`/`5`
- conversion coverage complete: `True`
- all conversions correct: `False`
- measured: `True`
- cycle DAC values V: `[1.044661, 0.6768297, 0.6523328, 0.7813589]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.184867, 0.00568355, 0.002816145, 0.001401736], [0.008585639, 0.9398381, 0.002103259, 0.001048093], [0.001477948, 0.0006972318, 1.702824, 0.000167139], [-2.531859e-05, -1.210529e-05, 1.802183, 1.799261]]`
- comparator differences V: `[-0.8755516, -0.8731908, -0.8707902, -0.8674084, -0.8676288, -0.865799, 0.8650797, -0.8659216, -0.8673749, 0.8651706, -0.8665679, -0.8665555, -0.8658521, 0.867731, 0.8650528, -0.8655343, 0.8655893, -0.8736035, -0.8710089, -0.8691034]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
