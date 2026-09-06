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
- cycle DAC values V: `[1.345208, 0.7303167, 0.6196363, 0.8032187]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.108352e-08, 7.009718e-08, 6.962282e-08], [6.834083e-08, 1.8, 6.834321e-08, 6.834348e-08], [6.834306e-08, 6.834385e-08, 1.8, 6.834407e-08], [6.833678e-08, 6.834156e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655395, -0.8643155, -0.8650837, -0.8653614, -0.8688427, -0.8645062, 0.863897, -0.8659775, -0.8686739, 0.864502, -0.8664404, -0.8650588, -0.8687588, 0.8659616, 0.8659028, -0.8664863, -0.8676926, 0.8653993, 0.86687, 0.8659651]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
