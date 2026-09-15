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
- cycle DAC values V: `[1.330319, 0.738945, 0.6240206, 0.8386492]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.35353e-08, 7.160132e-08, 7.124151e-08], [6.834241e-08, 1.8, 6.834336e-08, 6.834345e-08], [6.834295e-08, 6.83438e-08, 1.8, 6.8344e-08], [6.833539e-08, 6.834096e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8670859, -0.8665277, -0.8663068, -0.866286, -0.8690019, -0.8651717, 0.8644961, -0.8666799, -0.8688915, 0.8649795, -0.8667241, -0.8661924, -0.8687721, 0.8665872, 0.865977, -0.8673197, -0.8676732, 0.8669944, 0.8671011, 0.8650888]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
