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
- cycle DAC values V: `[1.338102, 0.7352398, 0.6211703, 0.8069919]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.140969e-08, 7.028854e-08, 6.977414e-08], [6.83413e-08, 1.8, 6.834324e-08, 6.834349e-08], [6.834302e-08, 6.834382e-08, 1.8, 6.834406e-08], [6.833661e-08, 6.834143e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655319, -0.864329, -0.8650819, -0.8653779, -0.8688396, -0.8646173, 0.8638557, -0.8660286, -0.8686748, 0.8644505, -0.8665268, -0.8652468, -0.8687428, 0.8659776, 0.8658455, -0.8666732, -0.8676038, 0.8654495, 0.8668686, 0.8658015]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
