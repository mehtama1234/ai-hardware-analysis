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
- cycle DAC values V: `[1.329199, 0.7441227, 0.618344, 0.8029208]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.107437e-08, 7.000705e-08, 6.956626e-08], [6.834187e-08, 1.8, 6.834328e-08, 6.834352e-08], [6.834313e-08, 6.834385e-08, 1.8, 6.834408e-08], [6.833689e-08, 6.834144e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655357, -0.8643696, -0.865081, -0.8653645, -0.868832, -0.8648262, 0.8639214, -0.8659732, -0.8686567, 0.8643319, -0.8666216, -0.8654057, -0.8687093, 0.8660092, 0.8657771, -0.8667606, -0.8674293, 0.8655144, 0.8668833, 0.8657279]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
