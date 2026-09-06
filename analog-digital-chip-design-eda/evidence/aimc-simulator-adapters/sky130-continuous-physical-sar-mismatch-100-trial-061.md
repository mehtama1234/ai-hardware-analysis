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
- cycle DAC values V: `[1.354892, 0.7298158, 0.6196034, 0.8014072]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.087135e-08, 6.994738e-08, 6.951668e-08], [6.834058e-08, 1.8, 6.834321e-08, 6.834347e-08], [6.834305e-08, 6.834385e-08, 1.8, 6.834408e-08], [6.83369e-08, 6.834164e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655445, -0.8643167, -0.8650856, -0.8653854, -0.8688548, -0.8645269, 0.8638793, -0.8659263, -0.8686843, 0.864506, -0.8663605, -0.8649182, -0.8687724, 0.8659443, 0.8659908, -0.866163, -0.8677158, 0.8653276, 0.8668404, 0.8662349]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
