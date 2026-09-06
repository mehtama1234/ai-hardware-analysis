# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[1, 1, 0, 1]`
- retained logical bits: `[0, 0, 1, 0]`
- final code: `2`
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
- cycle DAC values V: `[0.6683265, 0.2325509, 0.2314209, 0.3521519]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.262517, 0.04623064, 0.0215139, 0.01037799], [0.08419771, 0.7302172, 0.01780318, 0.008746664], [0.01392843, 0.005328256, 1.703313, 0.0006539625], [0.0001883503, -0.0001405285, 1.80051, 1.799303]]`
- comparator differences V: `[-0.8697631, -0.8648073, 0.8650461, -0.8651727, -0.8688218, -0.8648102, 0.8652381, -0.8650009, -0.8684587, 0.8659388, -0.8667356, 0.8651047, -0.8650644, 0.8690068, 0.8652467, -0.8654884, -0.8650624, 0.8691439, 0.8653281, -0.8654332]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
