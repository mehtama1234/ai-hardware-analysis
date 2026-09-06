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
- cycle DAC values V: `[1.339217, 0.7316102, 0.6221389, 0.8055997]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.091304e-08, 7.00018e-08, 6.953486e-08], [6.834076e-08, 1.8, 6.834319e-08, 6.834347e-08], [6.834298e-08, 6.834382e-08, 1.8, 6.834406e-08], [6.833671e-08, 6.83415e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655385, -0.8643221, -0.8650882, -0.8653575, -0.8688487, -0.86454, 0.8638376, -0.8660103, -0.868667, 0.864492, -0.8664991, -0.8650791, -0.8687403, 0.8659639, 0.865865, -0.8665661, -0.8675863, 0.8654022, 0.866874, 0.8659093]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
