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
- cycle DAC values V: `[1.341617, 0.7345196, 0.6161411, 0.7999038]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.092966e-08, 6.995219e-08, 6.953208e-08], [6.834105e-08, 1.8, 6.834323e-08, 6.834348e-08], [6.834319e-08, 6.834389e-08, 1.8, 6.83441e-08], [6.833697e-08, 6.834158e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655355, -0.8643293, -0.8650731, -0.8653584, -0.8688434, -0.8646003, 0.8639719, -0.8659315, -0.8686773, 0.864467, -0.8664535, -0.8651592, -0.8687461, 0.8659693, 0.8658988, -0.8665031, -0.8676257, 0.8654244, 0.8668609, 0.8659579]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
