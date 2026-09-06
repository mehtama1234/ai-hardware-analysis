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
- cycle DAC values V: `[1.339584, 0.7393386, 0.6211254, 0.8043571]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.181259e-08, 7.05122e-08, 6.992034e-08], [6.834218e-08, 1.8, 6.834332e-08, 6.834356e-08], [6.834302e-08, 6.834382e-08, 1.8, 6.834407e-08], [6.833679e-08, 6.834148e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655351, -0.8643438, -0.8650809, -0.8653605, -0.8688413, -0.8647166, 0.863856, -0.8659933, -0.8686765, 0.8643916, -0.8665794, -0.8652922, -0.8687483, 0.8659957, 0.8658041, -0.8667031, -0.8676451, 0.8654994, 0.8668738, 0.865766]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
