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
- cycle DAC values V: `[1.346024, 0.7387618, 0.6181428, 0.7990002]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.172754e-08, 7.043234e-08, 6.986218e-08], [6.834217e-08, 1.8, 6.834333e-08, 6.834357e-08], [6.834312e-08, 6.834386e-08, 1.8, 6.834409e-08], [6.833711e-08, 6.834163e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655399, -0.8643476, -0.8650759, -0.8653488, -0.868848, -0.8647028, 0.863919, -0.8659195, -0.8686842, 0.8643892, -0.8665402, -0.865224, -0.8687704, 0.8659913, 0.8658345, -0.8665789, -0.8677297, 0.8654944, 0.8668712, 0.8658825]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
