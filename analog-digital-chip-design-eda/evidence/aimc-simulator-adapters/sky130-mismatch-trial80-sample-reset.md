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
- cycle DAC values V: `[1.335501, 0.738546, 0.6210388, 0.8051359]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.128933e-08, 7.019111e-08, 6.968714e-08], [6.834154e-08, 1.8, 6.834325e-08, 6.834351e-08], [6.834303e-08, 6.834382e-08, 1.8, 6.834406e-08], [6.833675e-08, 6.834145e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655375, -0.8643458, -0.8650853, -0.8653649, -0.8688453, -0.864705, 0.8638622, -0.8660038, -0.8686643, 0.8644016, -0.8665751, -0.86528, -0.8687321, 0.8659928, 0.8658064, -0.8666989, -0.8675502, 0.8654763, 0.866881, 0.8657829]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
