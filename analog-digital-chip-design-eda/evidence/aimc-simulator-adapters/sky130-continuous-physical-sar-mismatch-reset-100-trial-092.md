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
- cycle DAC values V: `[1.331739, 0.7431995, 0.6221276, 0.8052422]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.148937e-08, 7.029654e-08, 6.975004e-08], [6.834222e-08, 1.8, 6.834331e-08, 6.834355e-08], [6.834299e-08, 6.83438e-08, 1.8, 6.834406e-08], [6.833681e-08, 6.834143e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655365, -0.8643635, -0.8650865, -0.865358, -0.8688364, -0.8648065, 0.8638351, -0.8660055, -0.8686631, 0.8643362, -0.866653, -0.8653669, -0.8687219, 0.8660104, 0.8657425, -0.8667922, -0.8674985, 0.8655222, 0.866886, 0.8656813]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
