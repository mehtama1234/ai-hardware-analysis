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
- cycle DAC values V: `[1.340743, 0.7417581, 0.6226767, 0.8089607]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.175054e-08, 7.045022e-08, 6.991401e-08], [6.83421e-08, 1.8, 6.834331e-08, 6.834353e-08], [6.834297e-08, 6.83438e-08, 1.8, 6.834405e-08], [6.833652e-08, 6.834137e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655352, -0.8643592, -0.8650884, -0.8654232, -0.8688434, -0.8648055, 0.863801, -0.8660306, -0.8686715, 0.864347, -0.8665719, -0.8653681, -0.8687443, 0.8659971, 0.8658463, -0.8666361, -0.8675532, 0.8654682, 0.8668666, 0.8659429]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
