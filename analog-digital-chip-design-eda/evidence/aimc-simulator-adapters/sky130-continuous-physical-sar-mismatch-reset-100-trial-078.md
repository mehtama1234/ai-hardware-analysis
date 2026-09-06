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
- cycle DAC values V: `[1.340691, 0.7336911, 0.6208991, 0.8040855]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.113035e-08, 7.01183e-08, 6.9627e-08], [6.834107e-08, 1.8, 6.834322e-08, 6.834349e-08], [6.834302e-08, 6.834383e-08, 1.8, 6.834407e-08], [6.833679e-08, 6.834152e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655387, -0.864328, -0.8650857, -0.865358, -0.8688478, -0.8645917, 0.8638668, -0.8659896, -0.8686692, 0.8644641, -0.866508, -0.8651351, -0.8687457, 0.8659741, 0.865857, -0.866578, -0.8676297, 0.865429, 0.8668756, 0.8658952]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
