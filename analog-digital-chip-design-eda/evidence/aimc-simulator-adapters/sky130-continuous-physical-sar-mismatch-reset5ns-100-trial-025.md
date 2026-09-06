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
- cycle DAC values V: `[1.342444, 0.737777, 0.6203613, 0.8019502]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.168862e-08, 7.043864e-08, 6.985469e-08], [6.834189e-08, 1.8, 6.83433e-08, 6.834354e-08], [6.834304e-08, 6.834383e-08, 1.8, 6.834407e-08], [6.833694e-08, 6.834156e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655355, -0.8643387, -0.8650802, -0.8653511, -0.8688446, -0.8646808, 0.8638741, -0.8659605, -0.868679, 0.8644147, -0.8665487, -0.8652102, -0.8687529, 0.8659891, 0.8658281, -0.8666213, -0.8676784, 0.8654901, 0.8668712, 0.8658479]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
