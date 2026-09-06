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
- cycle DAC values V: `[1.339783, 0.7387541, 0.618946, 0.8034845]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.160815e-08, 7.036849e-08, 6.983971e-08], [6.834196e-08, 1.8, 6.834331e-08, 6.834354e-08], [6.83431e-08, 6.834385e-08, 1.8, 6.834408e-08], [6.833679e-08, 6.834148e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655331, -0.8643422, -0.8650798, -0.8653698, -0.8688415, -0.8647037, 0.863911, -0.8659809, -0.8686765, 0.8644022, -0.8665431, -0.8653053, -0.8687476, 0.8659722, 0.8658327, -0.8666723, -0.8676394, 0.8654887, 0.8668706, 0.8657994]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
