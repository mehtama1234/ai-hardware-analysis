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
- cycle DAC values V: `[1.337663, 0.7359609, 0.6189043, 0.8036162]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.103865e-08, 7.003238e-08, 6.958507e-08], [6.834113e-08, 1.8, 6.834322e-08, 6.834348e-08], [6.83431e-08, 6.834385e-08, 1.8, 6.834408e-08], [6.833679e-08, 6.834149e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655378, -0.8643371, -0.8650824, -0.8653681, -0.8688478, -0.864646, 0.8639116, -0.8659827, -0.8686661, 0.8644387, -0.8665149, -0.8652259, -0.8687364, 0.8659811, 0.8658553, -0.8666134, -0.8675685, 0.8654448, 0.8668757, 0.8658675]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
