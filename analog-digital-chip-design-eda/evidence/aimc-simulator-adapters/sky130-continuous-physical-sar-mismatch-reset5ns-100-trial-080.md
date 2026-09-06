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
- cycle DAC values V: `[0.4424173, 0.8085539, 0.6882527, 0.6301998]`
- cycle DAC legal range: `False`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.088432e-08, 6.993758e-08, 6.950297e-08], [1.8, 1.8, 6.357792e-08, 6.485914e-08], [1.8, 6.789394e-08, 1.8, 6.813732e-08], [1.8, 6.824075e-08, 6.827917e-08, 1.8]]`
- comparator differences V: `[-0.8635043, 0.8611222, 0.8629551, 0.8636956, 0.8649848, -0.8659097, -0.8632721, 0.8632703, 0.8646725, -0.8646048, 0.8649183, -0.8653699, 0.8648109, 0.8659923, -0.8666901, -0.8647597, 0.8644039, 0.8668132, 0.8650663, -0.8681485]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
