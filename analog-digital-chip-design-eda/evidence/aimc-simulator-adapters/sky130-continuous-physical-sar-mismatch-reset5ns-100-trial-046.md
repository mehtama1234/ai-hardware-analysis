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
- cycle DAC values V: `[1.329038, 0.74394, 0.6180583, 0.8026042]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.105867e-08, 6.999748e-08, 6.955923e-08], [6.834195e-08, 1.8, 6.834329e-08, 6.834352e-08], [6.834314e-08, 6.834385e-08, 1.8, 6.834408e-08], [6.83369e-08, 6.834144e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655295, -0.8643667, -0.8650793, -0.8653616, -0.868832, -0.8648197, 0.8639282, -0.8659689, -0.8686654, 0.8643395, -0.8666187, -0.8653969, -0.8687084, 0.8660006, 0.8657912, -0.866752, -0.8674181, 0.8655095, 0.8668739, 0.8657372]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
