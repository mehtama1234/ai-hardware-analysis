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
- cycle DAC values V: `[1.340897, 0.7392333, 0.6199805, 0.8031672]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.174447e-08, 7.045788e-08, 6.988881e-08], [6.83421e-08, 1.8, 6.834332e-08, 6.834355e-08], [6.834306e-08, 6.834384e-08, 1.8, 6.834407e-08], [6.833684e-08, 6.83415e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655388, -0.8643458, -0.8650826, -0.8653631, -0.8688472, -0.8647198, 0.8638872, -0.8659768, -0.8686704, 0.864384, -0.866563, -0.8652908, -0.8687493, 0.8659997, 0.8658096, -0.8666746, -0.867661, 0.865499, 0.8668815, 0.8657961]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
