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
- cycle DAC values V: `[1.336813, 0.7379647, 0.6212889, 0.8035396]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.11525e-08, 7.01112e-08, 6.961178e-08], [6.834141e-08, 1.8, 6.834324e-08, 6.834351e-08], [6.834302e-08, 6.834382e-08, 1.8, 6.834407e-08], [6.833687e-08, 6.834151e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.865538, -0.864344, -0.865086, -0.8653501, -0.8688468, -0.8646918, 0.8638563, -0.8659823, -0.8686656, 0.864411, -0.866572, -0.865217, -0.8687351, 0.8659898, 0.8658098, -0.8666544, -0.8675631, 0.8654674, 0.8668803, 0.8658291]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
