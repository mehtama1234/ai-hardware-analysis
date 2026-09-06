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
- cycle DAC values V: `[1.33915, 0.7359264, 0.6186201, 0.8018571]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.094991e-08, 6.997494e-08, 6.953322e-08], [6.834111e-08, 1.8, 6.834322e-08, 6.834349e-08], [6.834311e-08, 6.834386e-08, 1.8, 6.834408e-08], [6.83369e-08, 6.834154e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655385, -0.864337, -0.865082, -0.8653554, -0.8688487, -0.8646452, 0.8639177, -0.8659588, -0.8686677, 0.8644397, -0.8665111, -0.8651864, -0.8687402, 0.8659805, 0.8658585, -0.8665753, -0.8675848, 0.865442, 0.8668753, 0.8659016]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
