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
- cycle DAC values V: `[1.341248, 0.7384474, 0.6226601, 0.8050292]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.192427e-08, 7.060215e-08, 6.996955e-08], [6.834215e-08, 1.8, 6.834332e-08, 6.834356e-08], [6.834297e-08, 6.83438e-08, 1.8, 6.834406e-08], [6.833678e-08, 6.834149e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.865538, -0.864342, -0.8650868, -0.8653586, -0.8688468, -0.8647019, 0.8638243, -0.8660027, -0.8686709, 0.8643914, -0.8665862, -0.865258, -0.8687502, 0.8659986, 0.8657883, -0.8666985, -0.8676746, 0.8654979, 0.8668834, 0.8657682]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
