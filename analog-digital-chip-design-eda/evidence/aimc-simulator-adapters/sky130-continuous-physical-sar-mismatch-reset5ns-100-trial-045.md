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
- cycle DAC values V: `[1.338803, 0.7376816, 0.620047, 0.8049128]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.155822e-08, 7.03553e-08, 6.982426e-08], [6.834173e-08, 1.8, 6.834328e-08, 6.834352e-08], [6.834306e-08, 6.834384e-08, 1.8, 6.834407e-08], [6.833672e-08, 6.834146e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655314, -0.8643382, -0.8650796, -0.8653717, -0.86884, -0.8646789, 0.8638813, -0.8660005, -0.8686755, 0.8644175, -0.8665442, -0.8652856, -0.868745, 0.8659879, 0.8658326, -0.8666799, -0.8676207, 0.8654763, 0.8668704, 0.8657931]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
