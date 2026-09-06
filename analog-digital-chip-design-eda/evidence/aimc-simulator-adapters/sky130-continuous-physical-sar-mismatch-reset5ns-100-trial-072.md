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
- cycle DAC values V: `[1.338217, 0.7395334, 0.6188495, 0.8047014]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.162105e-08, 7.037015e-08, 6.985432e-08], [6.834216e-08, 1.8, 6.834333e-08, 6.834354e-08], [6.83431e-08, 6.834385e-08, 1.8, 6.834408e-08], [6.833671e-08, 6.834144e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655317, -0.8643449, -0.8650794, -0.8653808, -0.8688397, -0.864721, 0.863913, -0.8659973, -0.8686752, 0.8643906, -0.866552, -0.8653556, -0.8687442, 0.8659954, 0.8658266, -0.8667124, -0.8676159, 0.865498, 0.8668715, 0.8657576]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
