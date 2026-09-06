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
- cycle DAC values V: `[1.337043, 0.7434855, 0.618755, 0.8004008]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.152038e-08, 7.028257e-08, 6.975025e-08], [6.834247e-08, 1.8, 6.834335e-08, 6.834357e-08], [6.834311e-08, 6.834385e-08, 1.8, 6.834408e-08], [6.833706e-08, 6.834154e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.865538, -0.8643638, -0.8650809, -0.8653512, -0.8688472, -0.8648091, 0.8639132, -0.8659389, -0.8686664, 0.8643301, -0.8666095, -0.8653425, -0.8687385, 0.866012, 0.8657782, -0.8667012, -0.8675803, 0.8655271, 0.8668839, 0.8657783]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
