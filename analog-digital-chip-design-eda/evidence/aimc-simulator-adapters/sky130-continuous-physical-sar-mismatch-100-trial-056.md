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
- cycle DAC values V: `[1.338192, 0.7431999, 0.6242792, 0.8091901]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.170444e-08, 7.042869e-08, 6.987183e-08], [6.834221e-08, 1.8, 6.834331e-08, 6.834354e-08], [6.834292e-08, 6.834378e-08, 1.8, 6.834404e-08], [6.833656e-08, 6.834136e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655342, -0.8643656, -0.8650911, -0.8654116, -0.8688414, -0.8648359, 0.8637599, -0.8660343, -0.8686688, 0.8643284, -0.8666159, -0.8653651, -0.868737, 0.8660013, 0.8658149, -0.866671, -0.8675079, 0.8654783, 0.8668702, 0.8659163]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
