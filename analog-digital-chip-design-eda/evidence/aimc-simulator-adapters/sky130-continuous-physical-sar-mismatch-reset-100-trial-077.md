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
- cycle DAC values V: `[1.334261, 0.742391, 0.6190059, 0.8028842]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.138049e-08, 7.020695e-08, 6.970975e-08], [6.834209e-08, 1.8, 6.834331e-08, 6.834354e-08], [6.83431e-08, 6.834384e-08, 1.8, 6.834408e-08], [6.833688e-08, 6.834147e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655368, -0.8643605, -0.8650815, -0.8653634, -0.8688439, -0.8647893, 0.8639077, -0.8659728, -0.8686633, 0.864349, -0.8666007, -0.8653643, -0.8687284, 0.8660068, 0.8657874, -0.8667288, -0.8675322, 0.8655118, 0.8668829, 0.8657525]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
