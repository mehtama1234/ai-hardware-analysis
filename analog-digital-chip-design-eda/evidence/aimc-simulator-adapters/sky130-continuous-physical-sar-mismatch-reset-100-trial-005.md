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
- cycle DAC values V: `[1.349336, 0.7359736, 0.6203863, 0.8004143]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.193156e-08, 7.05998e-08, 6.996379e-08], [6.834193e-08, 1.8, 6.834331e-08, 6.834356e-08], [6.834303e-08, 6.834384e-08, 1.8, 6.834407e-08], [6.833671e-08, 6.834138e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655484, -0.8643319, -0.8650832, -0.8653457, -0.8688468, -0.8646445, 0.8638791, -0.8659394, -0.8686791, 0.8644209, -0.8665178, -0.865142, -0.8687711, 0.8659907, 0.8658381, -0.8665511, -0.8677858, 0.8654784, 0.8668792, 0.8659014]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
