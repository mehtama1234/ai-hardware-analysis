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
- cycle DAC values V: `[1.340519, 0.733497, 0.620595, 0.8037525]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.112124e-08, 7.011249e-08, 6.96228e-08], [6.834104e-08, 1.8, 6.834322e-08, 6.834349e-08], [6.834304e-08, 6.834383e-08, 1.8, 6.834407e-08], [6.83368e-08, 6.834152e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655347, -0.8643241, -0.8650817, -0.8653549, -0.8688424, -0.8645741, 0.8638693, -0.8659851, -0.8686765, 0.8644761, -0.8664985, -0.8651242, -0.8687469, 0.8659679, 0.8658677, -0.8665682, -0.8676224, 0.8654226, 0.8668654, 0.865903]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
