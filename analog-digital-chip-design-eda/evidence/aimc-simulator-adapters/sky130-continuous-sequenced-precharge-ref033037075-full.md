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
- cycle DAC values V: `[0.6713218, 0.2347579, 0.2336334, 0.3543631]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.264115, 0.0461513, 0.02147389, 0.01035799], [0.08419828, 0.7301994, 0.01780326, 0.008746711], [0.01392537, 0.005326213, 1.703341, 0.0006537031], [0.0001883344, -0.0001405196, 1.80051, 1.799303]]`
- comparator differences V: `[-0.8697857, -0.8648169, 0.8650135, -0.8652077, -0.8688456, -0.8648037, 0.8652108, -0.8650223, -0.8684818, 0.8659141, -0.8667552, -0.865105, -0.8650641, 0.8690893, 0.8653875, -0.8652583, 0.8650525, -0.871552, -0.8704736, -0.8692174]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
