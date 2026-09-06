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
- cycle DAC values V: `[1.337294, 0.739975, 0.6209403, 0.8049195]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.173504e-08, 7.04585e-08, 6.988716e-08], [6.834222e-08, 1.8, 6.834332e-08, 6.834356e-08], [6.834303e-08, 6.834382e-08, 1.8, 6.834407e-08], [6.833676e-08, 6.834145e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655346, -0.8643468, -0.8650808, -0.8653664, -0.8688384, -0.8647294, 0.86386, -0.8660009, -0.8686743, 0.8643853, -0.8665905, -0.8653204, -0.8687419, 0.8659968, 0.8657999, -0.8667262, -0.8676028, 0.865501, 0.866874, 0.8657448]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
