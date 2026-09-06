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
- cycle DAC values V: `[1.337457, 0.7401602, 0.6212316, 0.8052408]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.168475e-08, 7.042714e-08, 6.986427e-08], [6.834217e-08, 1.8, 6.834332e-08, 6.834355e-08], [6.834302e-08, 6.834382e-08, 1.8, 6.834406e-08], [6.833674e-08, 6.834145e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.865538, -0.8643497, -0.8650847, -0.8653688, -0.8688477, -0.8647406, 0.8638578, -0.8660052, -0.8686669, 0.8643722, -0.866594, -0.8653299, -0.8687406, 0.8660026, 0.8657861, -0.8667352, -0.86761, 0.865506, 0.8668834, 0.8657354]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
