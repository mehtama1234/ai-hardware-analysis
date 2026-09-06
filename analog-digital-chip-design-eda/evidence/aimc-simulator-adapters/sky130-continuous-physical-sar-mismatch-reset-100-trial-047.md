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
- cycle DAC values V: `[1.339748, 0.7395251, 0.6214174, 0.8046786]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.184184e-08, 7.053049e-08, 6.993364e-08], [6.834221e-08, 1.8, 6.834332e-08, 6.834356e-08], [6.834301e-08, 6.834382e-08, 1.8, 6.834406e-08], [6.833677e-08, 6.834147e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655379, -0.8643466, -0.8649717, -0.8653631, -0.8688485, -0.8647263, 0.8638538, -0.8659976, -0.8686692, 0.8643763, -0.8665858, -0.8653018, -0.868739, 0.8660017, 0.8657906, -0.866712, -0.8676499, 0.8655045, 0.8668832, 0.8657567]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
