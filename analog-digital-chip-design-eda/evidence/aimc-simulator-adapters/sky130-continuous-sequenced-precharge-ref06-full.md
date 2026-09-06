# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[1, 0, 1, 0]`
- retained logical bits: `[0, 1, 0, 1]`
- final code: `5`
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
- cycle DAC values V: `[0.6714665, 0.2375572, 0.7079883, 0.5830719]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.264056, 0.04615422, 0.02147536, 0.01035872], [0.08422258, 0.7293857, 0.0178069, 0.008748745], [0.003636977, 1.830675, 1.752094, -0.0001493651], [0.000887553, 1.796489, 3.066135e-05, 1.799313]]`
- comparator differences V: `[-0.8665622, 0.8677999, -0.8657418, -0.8650992, -0.8661061, 0.8679054, -0.8655849, 0.8650916, -0.8660867, 0.8679062, -0.865582, 0.8650918, -0.8660835, 0.8679063, -0.865582, 0.8650918, -0.8660893, 0.8679062, -0.865582, 0.8650918]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
