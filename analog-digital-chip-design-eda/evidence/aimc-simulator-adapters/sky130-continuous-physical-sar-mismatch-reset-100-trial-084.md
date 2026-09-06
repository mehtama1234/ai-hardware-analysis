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
- cycle DAC values V: `[1.332014, 0.7365166, 0.6224999, 0.8067685]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.090055e-08, 6.997116e-08, 6.951452e-08], [6.834099e-08, 1.8, 6.834319e-08, 6.834347e-08], [6.834298e-08, 6.83438e-08, 1.8, 6.834405e-08], [6.833669e-08, 6.834143e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655368, -0.8643408, -0.8650888, -0.8653609, -0.8688368, -0.8646595, 0.8638273, -0.8660261, -0.8686625, 0.8644362, -0.8665733, -0.8652196, -0.8687182, 0.8659811, 0.8658129, -0.8666898, -0.8674706, 0.8654425, 0.8668789, 0.8658019]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
