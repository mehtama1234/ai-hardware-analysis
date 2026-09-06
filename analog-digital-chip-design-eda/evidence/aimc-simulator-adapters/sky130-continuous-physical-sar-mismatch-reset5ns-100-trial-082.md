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
- cycle DAC values V: `[1.344848, 0.7327312, 0.6172065, 0.8023619]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.130443e-08, 7.02025e-08, 6.97296e-08], [6.834115e-08, 1.8, 6.834325e-08, 6.834349e-08], [6.834315e-08, 6.834388e-08, 1.8, 6.834409e-08], [6.833678e-08, 6.834154e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655373, -0.86432, -0.865078, -0.8653736, -0.8688471, -0.8645545, 0.8639506, -0.8659652, -0.8686802, 0.8644806, -0.8664354, -0.8651672, -0.8687578, 0.8659673, 0.8658989, -0.8665214, -0.8676975, 0.8654241, 0.8668607, 0.8659341]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
