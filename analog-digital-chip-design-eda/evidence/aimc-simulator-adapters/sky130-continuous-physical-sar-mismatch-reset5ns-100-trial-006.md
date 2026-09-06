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
- cycle DAC values V: `[1.342949, 0.7284828, 0.6176022, 0.8039206]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.07561e-08, 6.988503e-08, 6.949172e-08], [6.83406e-08, 1.8, 6.83432e-08, 6.834346e-08], [6.834314e-08, 6.834388e-08, 1.8, 6.834408e-08], [6.833669e-08, 6.834152e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655366, -0.8643068, -0.8650797, -0.8653769, -0.868845, -0.864441, 0.8639426, -0.8659866, -0.8686782, 0.8645351, -0.8663912, -0.8650678, -0.8687509, 0.8659452, 0.8659344, -0.8664609, -0.867644, 0.8653664, 0.8668545, 0.8659876]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
