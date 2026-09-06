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
- cycle DAC values V: `[1.338089, 0.7356276, 0.6189594, 0.8031831]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.104386e-08, 7.003899e-08, 6.95851e-08], [6.834118e-08, 1.8, 6.834323e-08, 6.834349e-08], [6.83431e-08, 6.834385e-08, 1.8, 6.834408e-08], [6.833682e-08, 6.83415e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655311, -0.8643328, -0.865079, -0.8653617, -0.8688395, -0.8646273, 0.8639108, -0.865977, -0.8686743, 0.8644524, -0.8665077, -0.865202, -0.8687399, 0.865975, 0.8658639, -0.866599, -0.8675809, 0.8654388, 0.8668658, 0.8658791]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
