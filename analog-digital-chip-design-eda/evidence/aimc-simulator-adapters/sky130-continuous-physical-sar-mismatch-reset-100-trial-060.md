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
- cycle DAC values V: `[1.352438, 0.7345242, 0.6155034, 0.7979068]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.176896e-08, 7.045891e-08, 6.991812e-08], [6.834166e-08, 1.8, 6.834331e-08, 6.834353e-08], [6.83432e-08, 6.83439e-08, 1.8, 6.83441e-08], [6.833706e-08, 6.834166e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655437, -0.8643267, -0.8650753, -0.8653609, -0.8688501, -0.8646104, 0.8639855, -0.8659035, -0.8686861, 0.8644406, -0.8664318, -0.8651643, -0.8687784, 0.8660192, 0.865902, -0.8664613, -0.8678244, 0.8654612, 0.8668719, 0.8659709]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
