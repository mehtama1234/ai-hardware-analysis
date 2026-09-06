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
- cycle DAC values V: `[1.340645, 0.7374745, 0.6250217, 0.811225]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.141574e-08, 7.029238e-08, 6.977696e-08], [6.834134e-08, 1.8, 6.834323e-08, 6.834349e-08], [6.834288e-08, 6.834377e-08, 1.8, 6.834404e-08], [6.833643e-08, 6.834136e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655358, -0.8643431, -0.865093, -0.8654205, -0.8688432, -0.8647105, 0.8637434, -0.8660613, -0.8686709, 0.8644098, -0.8665462, -0.8652583, -0.8687347, 0.865979, 0.8658673, -0.8665908, -0.8675353, 0.8654182, 0.8668629, 0.865984]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
