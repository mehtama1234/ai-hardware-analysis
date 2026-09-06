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
- cycle DAC values V: `[0.4447884, 0.8089255, 0.6890149, 0.6331166]`
- cycle DAC legal range: `False`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.059011e-08, 6.97518e-08, 6.937899e-08], [1.8, 1.8, 6.399231e-08, 6.512824e-08], [1.8, 6.794115e-08, 1.8, 6.815719e-08], [1.8, 6.824368e-08, 6.828107e-08, 1.8]]`
- comparator differences V: `[-0.8635186, 0.8611219, 0.8631459, 0.8636988, 0.8649909, -0.8659161, -0.8633002, 0.8631775, 0.8646831, -0.8646076, 0.8649133, -0.8653946, 0.8647727, 0.8659926, -0.8666573, -0.8647611, 0.8644096, 0.8668126, 0.865106, -0.8681357]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
