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
- cycle DAC values V: `[1.331577, 0.7430157, 0.6218397, 0.8049238]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.146966e-08, 7.02843e-08, 6.974122e-08], [6.83423e-08, 1.8, 6.834332e-08, 6.834356e-08], [6.834301e-08, 6.834381e-08, 1.8, 6.834406e-08], [6.833682e-08, 6.834143e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655307, -0.8643618, -0.8651422, -0.8653556, -0.8688341, -0.8647989, 0.8638372, -0.8660012, -0.8686686, 0.864344, -0.8666503, -0.8653578, -0.8687239, 0.8660017, 0.8657577, -0.8667838, -0.8674887, 0.8655175, 0.8668797, 0.8656912]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
