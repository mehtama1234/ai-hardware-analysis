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
- cycle DAC values V: `[1.43013, 0.7646059, 0.6408755, 0.8410017]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.98, 1.39319e-06, 1.393191e-06, 1.393192e-06], [1.393194e-06, 1.98, 1.393194e-06, 1.393194e-06], [1.393197e-06, 1.393195e-06, 1.98, 1.393194e-06], [1.393193e-06, 1.393193e-06, 1.98, 1.98]]`
- comparator differences V: `[-0.7371607, -0.7363757, -0.7383708, -0.7398353, -0.7449358, -0.7413678, 0.7396739, -0.742311, -0.7444939, 0.7399581, -0.7437698, -0.742936, -0.746392, 0.7405719, 0.743047, -0.7459125, -0.7470153, 0.7385932, 0.7430678, 0.7455331]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
